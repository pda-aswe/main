import sounddevice as sd
from vosk import Model, KaldiRecognizer
import queue
import json
import threading

class STT:
    def __init__(self,debug=False):
        #setup vars
        self.STTRecognizer = None
        self.audioQueue = queue.Queue()
        self.debug = debug

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

    def getText(self):
        while not self.audioQueue.empty():
            data = self.audioQueue.get()   
            self.STTRecognizer.AcceptWaveform(data)
        resultDict = json.loads(self.STTRecognizer.FinalResult())
        if not resultDict.get("text", "") == "":
            if self.debug:
                print(resultDict["text"])
            return resultDict["text"]
        else:
            return ""