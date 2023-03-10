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
import tkinter

containerNames = ["bard-broker","bard-casepreis", "bard-casesport", "bard-casenews", "bard-casewelcome", "bard-servicewetter", "bard-serviceverkehrsinfos", "bard-servicekalender", "bard-servicenews", "bard-servicelocation", "bard-servicesport", "bard-servicepreis", "bard-servicemail"]

preferences = {}

preferencePath = os.path.join(os.getcwd(), 'preferences.json')

speakThread = None

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
    client.subscribe([("req/pref/#",0),])

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


#Diese Funktion wird aufgerufen, wenn es für ein Topic kein spezielles Callback gibt
def onMessageMQTT(client, userdata, msg):
    pass

def speakRecognition():
    t = threading.current_thread()
    while getattr(t, "run", True):
        print ("Recording")
        time.sleep(0.5)
    return

def speakPress(event=None):
    global speakThread
    if event and int(event.type) == 4:
        speakThread = threading.Thread(target=speakRecognition)
        speakThread.start()
    elif event and int(event.type) == 5:
        speakThread.run = False
        speakThread.join()

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

    #send preferences from preferences.json
    preferences = readPreferences(preferencePath)
    sendPreferenceStructure(client,"pref",preferences)

    #create main window
    mainWindow = tkinter.Tk()
    mainWindow.title('BARD')
    button = tkinter.Button(mainWindow, text='Speak', width=25)
    button.bind('<ButtonPress-1>',speakPress)
    button.bind('<ButtonRelease-1>',speakPress)
    button.pack()
    mainWindow.mainloop()

    #stop all container
    subprocess.run(["docker", "compose", "stop"])

    #stop file watchdog
    observer.stop()
    observer.join()

    #stop mqtt
    client.loop_stop()
    client.disconnect()