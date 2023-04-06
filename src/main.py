#!/usr/bin/python3
import subprocess
import os
import os.path

#own libraries
import GUI
import preferences
import messenger
import googleLogin

if __name__ ==  "__main__":
    #connect with google
    googleLogin.connect()
    if not os.path.isfile("credentials/token.json"):
        print("Google login error")
        quit()

    #start all container
    subprocess.run(["docker", "compose", "up", "-d"])

    #setup mqtt client
    mqttConnection = messenger.Messenger()
    if not mqttConnection.connect():
        print("No MQTT broker running")
        quit()

    #setup preferences
    preferencesObj = preferences.Preferences(os.path.join(os.getcwd(), 'preferences.json'))

    #setup gui
    mainWindow = GUI.GUI()
    mainWindow.display()

    #stop all container
    subprocess.run(["docker", "compose", "stop"])

    #stop preferences watchdog
    preferencesObj.stop()

    #stop mqtt
    mqttConnection.disconnect()