from src import GUI
from unittest.mock import patch, ANY, MagicMock

class DummyEvent:
    def __init__(self):
        self.type = 1

    def set_type(self,data):
        self.type = data

@patch("STT.STT")
@patch("messenger.Messenger")
def test_display(mock_stt,mock_messenger):
    obj = GUI.GUI()

    with patch.object(obj, 'window') as mock_window:
        obj.display()
        mock_window.mainloop.assert_called()

@patch("STT.STT")
@patch("messenger.Messenger")
def test_buttonSpeakPress(mock_stt,mock_messenger):
    obj = GUI.GUI()
    eventObj = DummyEvent()
    eventObj.set_type(5)

    with patch.object(obj, 'mqttConnection') as mock_connection, patch.object(obj, "speakThread"), patch.object(obj, "stt") as mock_stt_obj:
        obj._GUI__buttonSpeakPress(eventObj)
        mock_connection.publish.assert_called_with('stt', ANY)