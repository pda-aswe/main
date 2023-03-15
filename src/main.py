#!/usr/bin/python3
import subprocess
import os
import paho.mqtt.client as mqtt
import pyttsx3
import platform

#own libraries
import GUI
import STT
import preferences

TTSEngine = None   
preferencesObj = None                 

def onConnectMQTT(client,userdata,flags, rc):
    client.subscribe([("req/pref/#",0),("tts",0)])

def preferenceMQTTCallback(client, userdata, msg):
    global preferencesObj
    if msg.topic == "req/pref/all":
        preferencesObj.send("all")
    else:
        preferencesObj.send(msg.topic.split("/",1)[1])

def sendSTTMessage(message):
    client.publish("stt",str(message))

def sttMQTTCallback(client, userdata, msg):
    TTSEngine.say(str(msg.payload.decode("utf-8")))
    TTSEngine.runAndWait()

#Diese Funktion wird aufgerufen, wenn es für ein Topic kein spezielles Callback gibt
def onMessageMQTT(client, userdata, msg):
    pass

if __name__ ==  "__main__":
    #start all container
    #subprocess.run(["docker", "compose", "up", "-d"])

    #setup mqtt client
    #aufbau der MQTT-Verbindung
    mqttConnection = mqtt.Client()
    mqttConnection.on_connect = onConnectMQTT
    mqttConnection.on_message = onMessageMQTT
    mqttConnection.message_callback_add("req/pref/#", preferenceMQTTCallback)
    mqttConnection.message_callback_add("tts", sttMQTTCallback)
    try:
        mqttConnection.connect("localhost",1883,60)
    except:
        print("No MQTT broker running")
        quit()
    mqttConnection.loop_start()

    #setup preferences
    preferencesObj = preferences.Preferences(os.path.join(os.getcwd(), 'preferences.json'),mqttConnection)

    #setup STT
    stt = STT.STT()

    #setup TTS
    TTSEngine = pyttsx3.init()
    if platform.system() == "Windows":
        TTSEngine.setProperty('voice', "LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_DE-DE_HEDDA_11.0")
        TTSEngine.setProperty('rate', TTSEngine.getProperty('rate')-50)

    #setup gui
    mainWindow = GUI.GUI(stt)
    mainWindow.display()

    #stop all container
    #subprocess.run(["docker", "compose", "stop"])

    #stop preferences watchdog
    preferencesObj.stop()

    #stop mqtt
    mqttConnection.loop_stop()
    mqttConnection.disconnect()