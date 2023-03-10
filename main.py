#!/usr/bin/python3
import docker
import time
import subprocess
import json
import os
from datetime import datetime, timedelta
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import paho.mqtt.client as mqtt

containerNames = ["bard-broker","bard-casepreis", "bard-casesport", "bard-casenews", "bard-casewelcome", "bard-servicewetter", "bard-serviceverkehrsinfos", "bard-servicekalender", "bard-servicenews", "bard-servicelocation", "bard-servicesport", "bard-servicepreis", "bard-servicemail"]

preferences = {}

preferencePath = os.path.join(os.getcwd(), 'preferences.json')

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
    def __init__(self):
        self.last_modified = datetime.now()
    def  on_modified(self,  event):
        if datetime.now() - self.last_modified < timedelta(seconds=1):
            return
        else:
            self.last_modified = datetime.now()
        preferences = readPreferences(event.src_path)
    def  on_created(self,  event):
        preferences = readPreferences(event.src_path)
    def  on_deleted(self,  event):
        preferences = {}

def onConnectMQTT(client,userdata,flags, rc):
    pass

#Diese Funktion wird aufgerufen, wenn es für ein Topic kein spezielles Callback gibt
def onMessageMQTT(client, userdata, msg):
    pass

if __name__ ==  "__main__":
    #connect to docker
    #more information: https://docker-py.readthedocs.io/en/stable/client.html
    client = docker.from_env()

    #start all container
    subprocess.run(["docker", "compose", "up", "-d"])

    #setup file watchdog
    event_handler = PreferencesFileHandler()
    observer = Observer()
    observer.schedule(event_handler,  path=preferencePath,  recursive=False)
    observer.start()

    #setup mqtt client
    #aufbau der MQTT-Verbindung
    client = mqtt.Client()
    client.on_connect = onConnectMQTT
    client.on_message = onMessageMQTT
    try:
        client.connect("localhost",1883,60)
    except:
        print("No MQTT broker running")
        observer.stop()
        observer.join()
        quit()
    client.loop_start()

    #send preferences from preferences.json
    preferences = readPreferences(preferencePath)
    sendPreferenceStructure(client,"pref",preferences)

    #stop all container
    subprocess.run(["docker", "compose", "stop"])

    #stop file watchdog
    observer.stop()
    observer.join()

    #stop mqtt
    client.loop_stop()
    client.disconnect()