import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish
from multiprocessing import Process, Queue
import datetime
import json
import os

#own libraries
import TTS
import singelton

class Messenger(metaclass=singelton.SingletonMeta):
    def __init__(self):
        #setup TTS
        self.tts = TTS.TTS()
        self.preferenceCallback = None
        self.connected = False
        self.displayTextCallback = None

        #aufbau der MQTT-Verbindung
        self.mqttConnection = mqtt.Client()
        self.mqttConnection.on_connect = self.__onConnectMQTT
        self.mqttConnection.on_message = self.__onMessageMQTT
        self.mqttConnection.message_callback_add("req/pref/#", self.__preferenceMQTTCallback)
        self.mqttConnection.message_callback_add("tts", self.__ttsMQTTCallback)

    def connect(self):
        if not self.connected:
            try:
                self.mqttConnection.connect("localhost",1883,60)
            except:
                return False
            self.mqttConnection.loop_start()
        self.connected = True
        return True
    
    def disconnect(self):
        if self.connected:
            self.connected = False
            self.mqttConnection.loop_stop()
            self.mqttConnection.disconnect()
        return True
    
    def __onConnectMQTT(self,client,userdata,flags, rc):
        client.subscribe([("req/pref/#",0),("tts",0)])

    def __preferenceMQTTCallback(self,client, userdata, msg):
        if self.preferenceCallback is not None:
            if msg.topic == "req/pref/all":
                self.preferenceCallback("all")
            else:
                self.preferenceCallback(msg.topic.split("/",1)[1])

    def setPreferenceCallback(self,func):
        self.preferenceCallback = func

    def setTextoutputCallback(self,func):
        self.displayTextCallback = func

    def publish(self,path,message):
        self.mqttConnection.publish(path,str(message))

    def __ttsMQTTCallback(self,client, userdata, msg):
       
        calendarEvent = self.__currentCalendarEvent("req/appointment/next","appointment/next")
        doNotDisturb = False
        ttsData = str(msg.payload.decode("utf-8"))

        if self.displayTextCallback is not None and (calendarEvent or doNotDisturb):
            self.displayTextCallback(ttsData)
        else:
            self.displayTextCallback("")
            self.tts.speak(ttsData)

    #received default mqtt messages
    def __onMessageMQTT(self,client, userdata, msg):
        pass

    def __currentCalendarEvent(self,requestTopic,responseTopic):
        q = Queue()
        process = Process(target=mqttRequestResponseProzess, args=(q,requestTopic,responseTopic))
        process.start()
        process.join(timeout=3)
        process.terminate()
        if process.exitcode == 0:
            try:
                mqttData = q.get(timeout=1)
            except:
                return(False)

            try:
                mqttData = json.loads(str(mqttData.decode("utf-8")))
            except:
                print("Can't decode message")
                return(False)

            start = mqttData.get("start",None)
            if start is not None:
                try:
                    start = datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M:%S%z')
                except:
                    return(False)
                    

                if start <= datetime.datetime.now().replace(tzinfo=start.tzinfo):
                    return(True)
                else:
                    return(False)
                    
            else:
                return(False)

def mqttRequestResponseProzess(q,requestTopic,responseTopic):
    docker_container = os.environ.get('DOCKER_CONTAINER', False)
    if docker_container:
        mqtt_address = "broker"
    else:
        mqtt_address = "localhost"

    publish.single(requestTopic,hostname=mqtt_address,port=1883)
    mqttResponse = subscribe.simple(responseTopic,hostname=mqtt_address,port=1883).payload

    q.put(mqttResponse)
