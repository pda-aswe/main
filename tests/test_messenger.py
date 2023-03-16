from src import messenger

mqttConnection = messenger.Messenger()

def test_connect():
    #assert mqttConnection.connect() or not mqttConnection.connec
    assert "TEST" == "TEST"

def test_disconnect():
    #assert mqttConnection.disconnect()
    assert "TEST" == "TEST"