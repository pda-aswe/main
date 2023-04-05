import paho.mqtt.client as mqtt

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
        self.mqttConnection.message_callback_add("tts", self.__sttMQTTCallback)

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

    def __sttMQTTCallback(self,client, userdata, msg):
        if self.displayTextCallback is not None:
            self.displayTextCallback(str(msg.payload.decode("utf-8")))
        self.tts.speak(str(msg.payload.decode("utf-8")))

    #received default mqtt messages
    def __onMessageMQTT(self,client, userdata, msg):
        pass
