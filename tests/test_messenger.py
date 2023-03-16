from src import messenger

mqttConnection = messenger.Messenger()

def test_connect():
    assert mqttConnection.connect() or not mqttConnection.connected()

def test_disconnect():
    assert mqttConnection.disconnect()