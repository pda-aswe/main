from src import messenger
from unittest.mock import patch, ANY, MagicMock
import json

class DummyMSG:
    def __init__(self):
        self.payload = "Test"
        self.topic = "test"

    def set_payload(self,data):
        self.payload = str.encode(data)

    def set_topic(self,topic):
        self.topic = topic

@patch("TTS.TTS")
def test_connect(mock_tts):
    obj = messenger.Messenger()

    with patch.object(obj, 'mqttConnection') as mock_connect:
        obj.connect()
        mock_connect.connect.assert_called_with("localhost",1883,60)
        mock_connect.loop_start.assert_called()

@patch("TTS.TTS")
def test_disconnect(mock_tts):
    obj = messenger.Messenger()

    with patch.object(obj, 'connected', True), patch.object(obj, 'mqttConnection') as mock_connect:
        obj.disconnect()
        mock_connect.disconnect.assert_called()
        mock_connect.loop_stop.assert_called()

@patch("TTS.TTS")
def test_onConnectMQTT(mock_tts):
    obj = messenger.Messenger()

    mock_client = MagicMock()

    obj._Messenger__onConnectMQTT(mock_client,None,None,None)

    mock_client.subscribe.assert_called_with([("req/pref/#",0),("tts",0)])


@patch("TTS.TTS")
def test_onMessageMQTT(mock_tts):
    obj = messenger.Messenger()

    obj._Messenger__onMessageMQTT(MagicMock(),None,None)

@patch("TTS.TTS")
def test_preferenceMQTTCallback(mock_tts):
    obj = messenger.Messenger()

    with patch.object(obj, 'preferenceCallback') as mock_callback:
        responseData = DummyMSG()
        responseData.set_payload("")
        responseData.set_topic("req/pref/all")

        obj._Messenger__preferenceMQTTCallback(None,None,responseData)

        mock_callback.assert_called_with("all")

@patch("TTS.TTS")
def test_publish(mock_tts):
    obj = messenger.Messenger()

    with patch.object(obj, 'mqttConnection') as mock_connect:
        obj.publish("testPath","testMessage")
        mock_connect.publish.assert_called_with("testPath","testMessage")

#@patch("TTS.TTS")
#def test_ttsMQTTCallback(mock_tts):
#    obj = messenger.Messenger()
#    responseData = DummyMSG()
#    responseData.set_payload("Testnachricht")

#    with patch.object(obj, 'tts') as mock_tts_object:
#        obj._Messenger__ttsMQTTCallback(None,None,responseData)
#        mock_tts_object.speak.assert_called_with(str(responseData.payload.decode("utf-8")))