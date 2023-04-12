import sounddevice as sd
from vosk import Model, KaldiRecognizer
import queue
import json
import threading
import spacy
import zahlwort2num as w2n
import os
import paho.mqtt.publish as publish

#own libraries
import singelton

class STT(metaclass=singelton.SingletonMeta):
    def __init__(self,debug=False):
        #setup vars
        self.STTRecognizer = None
        self.audioQueue = queue.Queue()
        self.debug = debug

        self.nlp = spacy.load('de_core_news_lg')

        #setup microphone
        # get the samplerate - this is needed by the Kaldi recognizer
        device_info = sd.query_devices(sd.default.device[0], 'input')
        samplerate = int(device_info['default_samplerate'])

        #setup stt
        model = Model(lang="de")
        self.STTRecognizer = KaldiRecognizer(model, samplerate)
        self.STTRecognizer.SetWords(True)
    
    def speakRecordingThread(self):
        t = threading.current_thread()
        with sd.RawInputStream(dtype='int16',channels=1,callback=self.recordCallback):
            while getattr(t, "run", True):
                pass
        return
    
    def recordCallback(self,indata, frames, time, status):
        self.audioQueue.put(bytes(indata))

    def sendSTTText(self):
        while not self.audioQueue.empty():
            data = self.audioQueue.get()   
            self.STTRecognizer.AcceptWaveform(data)
        resultDict = json.loads(self.STTRecognizer.FinalResult())
        if not resultDict.get("text", "") == "":
            if self.debug:
                print(resultDict["text"])

            nlpThread = threading.Thread(target=self.nlpString, args=(resultDict["text"],))
            nlpThread.start()

    def nlpString(self,stringData):
        doc = self.nlp(stringData)

        sttData = {}
        sttData["base"] = stringData
        sttData["tokens"] = []
        sttData["verbs"] = []
        sttData["nouns"] = []
        sttData["numbers"] = []
        sttData["adp"] = []
        sttData["adj"] = []
        sttData["cleaned"] = ""
        for token in doc:
            if token.lemma_ != "--":

                try:
                    string2Num = w2n.convert(token.text)
                except:
                    string2Num = None
                
                if string2Num:
                    tokenData = {}
                    tokenData['type'] = "NUM"
                    tokenData['token'] = string2Num
                    tokenData['stopWord'] = False
                    sttData["tokens"].append(tokenData)
                    sttData["numbers"].append(string2Num)
                    if sttData["cleaned"] != "":
                        sttData["cleaned"] += " "
                    sttData["cleaned"] += str(string2Num)
                    continue

                if not token.is_stop:
                    if sttData["cleaned"] != "":
                        sttData["cleaned"] += " "
                    sttData["cleaned"] += token.lemma_.lower()
                    tokenData = {}
                    tokenData['type'] = token.pos_
                    tokenData['token'] = token.lemma_.lower()
                    tokenData['stopWord'] = token.is_stop
                    sttData["tokens"].append(tokenData)
                
                if token.pos_ == "VERB":
                    sttData["verbs"].append(token.lemma_.lower())
                elif token.pos_ == "NOUN":
                    sttData["nouns"].append(token.lemma_.lower())
                elif token.pos_ == "NUM":
                    sttData["numbers"].append(token.lemma_.lower())
                elif token.pos_ == "ADP":
                    sttData["adp"].append(token.lemma_.lower())
                elif token.pos_ == "ADJ":
                    sttData["adj"].append(token.lemma_.lower())
                elif token.pos_ == "PROPN":
                    sttData["nouns"].append(token.lemma_.lower())

        docker_container = os.environ.get('DOCKER_CONTAINER', False)
        if docker_container:
            mqtt_address = "broker"
        else:
            mqtt_address = "localhost"

        publish.single("stt",payload=json.dumps(sttData),hostname=mqtt_address,port=1883)