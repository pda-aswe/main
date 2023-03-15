#!/usr/bin/python3
import docker
import time
import subprocess
import json
import os
import threading
from datetime import datetime, timedelta
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import paho.mqtt.client as mqtt
from tkinter import *
import customtkinter
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import queue
import pyttsx3
import platform

containerNames = ["bard-broker","bard-casepreis", "bard-casesport", "bard-casenews", "bard-casewelcome", "bard-servicewetter", "bard-serviceverkehrsinfos", "bard-servicekalender", "bard-servicenews", "bard-servicelocation", "bard-servicesport", "bard-servicepreis", "bard-servicemail"]

preferences = {}

preferencePath = os.path.join(os.getcwd(), 'preferences.json')

speakThread = None
STTRecognizer = None
TTSEngine = None

#queue for audio chunks
audioQueue = queue.Queue()

def readPreferences(path):
    try:
        with open(path) as preferncesFile:
            return json.load(preferncesFile)
    except FileNotFoundError:
        return {}

def sendPreference(client,path,value):
    if type(value) is list:
        client.publish(path, json.dumps(value))
    else:
        client.publish(path, value)

def sendPreferenceStructure(client,rootPath,prefStructure):
    for key in prefStructure:
        if type(prefStructure[key]) is dict:
            sendPreferenceStructure(client,os.path.join(rootPath,key),prefStructure[key])
        else:
            sendPreference(client,os.path.join(rootPath,key),prefStructure[key])

class  PreferencesFileHandler(FileSystemEventHandler):
    def __init__(self,mqttClient):
        self.last_modified = datetime.now()
        self.mqttClient = mqttClient
    def  on_modified(self,  event):
        global preferences
        if datetime.now() - self.last_modified < timedelta(seconds=1):
            return
        else:
            self.last_modified = datetime.now()
        #send difference between old and new preferences
        newPreferences = readPreferences(event.src_path)
        preferenceDifference = jsonDifference(preferences,newPreferences)
        if preferenceDifference is not None:
            sendPreferenceStructure(self.mqttClient,"pref",preferenceDifference)
        preferences = newPreferences
    def  on_created(self,  event):
        global preferences
        preferences = readPreferences(event.src_path)
        sendPreferenceStructure(self.mqttClient,"pref",preferences)
    def  on_deleted(self,  event):
        global preferences
        preferences = {}

def jsonDifference(oldData,newData):
    difference = {}
    for key in newData:
        if key in oldData:
            if type(newData[key]) is dict:
                retData = jsonDifference(oldData[key],newData[key])
                if retData:
                    difference[key] = retData
            else:
                if oldData[key] != newData[key]:
                    difference[key] = newData[key]
        else:
            difference[key] = newData[key]
    return difference if difference else None
                    

def onConnectMQTT(client,userdata,flags, rc):
    client.subscribe([("req/pref/#",0),("tts",0)])

def preferenceMQTTCallback(client, userdata, msg):
    if msg.topic == "req/pref/all":
        sendPreferenceStructure(client,"pref",preferences)
    else:
        returnData = preferences
        keys = msg.topic.split("/")
        if len(keys) != 0:
            for key in keys[2:]:
                if key == "":
                    continue
                if key in returnData:
                    returnData = returnData[key]
                else:
                    returnData = None
                    break
        else:
            returnData = None
        
        if returnData is not None:
            sendPreferenceStructure(client,"/".join(keys[1:]),returnData)

def sendSTTMessage(message):
    client.publish("stt",str(message))

def sttMQTTCallback(client, userdata, msg):
    TTSEngine.say(str(msg.payload.decode("utf-8")))
    TTSEngine.runAndWait()

#Diese Funktion wird aufgerufen, wenn es für ein Topic kein spezielles Callback gibt
def onMessageMQTT(client, userdata, msg):
    pass

def speakRecognition():
    t = threading.current_thread()
    with sd.RawInputStream(dtype='int16',channels=1,callback=recordCallback):
        while getattr(t, "run", True):
           pass
    return

def speakPress(event=None):
    global speakThread
    global STTRecognizer
    if event and int(event.type) == 4:
        speakThread = threading.Thread(target=speakRecognition)
        speakThread.start()
    elif event and int(event.type) == 5:
        speakThread.run = False
        speakThread.join()
        while not audioQueue.empty():
            data = audioQueue.get()   
            STTRecognizer.AcceptWaveform(data)
        resultDict = json.loads(STTRecognizer.FinalResult())
        if not resultDict.get("text", "") == "":
            print(resultDict["text"])
            sendSTTMessage(resultDict["text"])

def recordCallback(indata, frames, time, status):
    audioQueue.put(bytes(indata))

if __name__ ==  "__main__":
    #connect to docker
    #more information: https://docker-py.readthedocs.io/en/stable/client.html
    client = docker.from_env()

    #start all container
    subprocess.run(["docker", "compose", "up", "-d"])

    #setup mqtt client
    #aufbau der MQTT-Verbindung
    client = mqtt.Client()
    client.on_connect = onConnectMQTT
    client.on_message = onMessageMQTT
    client.message_callback_add("req/pref/#", preferenceMQTTCallback)
    client.message_callback_add("tts", sttMQTTCallback)
    try:
        client.connect("localhost",1883,60)
    except:
        print("No MQTT broker running")
        quit()
    client.loop_start()

    #setup file watchdog
    event_handler = PreferencesFileHandler(client)
    observer = Observer()
    observer.schedule(event_handler,  path=preferencePath,  recursive=False)
    observer.start()

    #setup microphone
    # get the samplerate - this is needed by the Kaldi recognizer
    device_info = sd.query_devices(sd.default.device[0], 'input')
    samplerate = int(device_info['default_samplerate'])
    # display the default input device
    print("Microphone: {}".format(device_info['name']))

    #setup STT
    model = Model(lang="de")
    STTRecognizer = KaldiRecognizer(model, samplerate)
    STTRecognizer.SetWords(True)

    #setup TTS
    TTSEngine = pyttsx3.init()
    if platform.system() == "Windows":
        TTSEngine.setProperty('voice', "LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_DE-DE_HEDDA_11.0")
        TTSEngine.setProperty('rate', TTSEngine.getProperty('rate')-50)

    #send preferences from preferences.json
    preferences = readPreferences(preferencePath)
    sendPreferenceStructure(client,"pref",preferences)

    #create main window
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("green")
    mainWindow = customtkinter.CTk()
    mainWindow.geometry("400x240")
    mainWindow.title('BARD')
    button = customtkinter.CTkButton(master=mainWindow, text='Speak')
    button.bind('<ButtonPress-1>',speakPress)
    button.bind('<ButtonRelease-1>',speakPress)
    button.place(relx=0.5,rely=0.4,anchor=CENTER)
    mainWindow.mainloop()

    #stop all container
    subprocess.run(["docker", "compose", "stop"])

    #stop file watchdog
    observer.stop()

    #stop mqtt
    client.loop_stop()
    client.disconnect()