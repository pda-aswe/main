from src import GUI
from unittest.mock import patch, ANY, MagicMock

class DummyEvent:
    def __init__(self):
        self.type = 1

    def set_type(self,data):
        self.type = data

@patch("STT.STT")
@patch("spacy.load")
@patch("messenger.Messenger")
@patch("customtkinter.CTk")
@patch("customtkinter.CTkButton")
def test_display(mockt_ctk_button,mock_ctk,mock_stt,mock_spacy,mock_messenger):
    obj = GUI.GUI()

    with patch.object(obj, 'window') as mock_window:
        obj.display()
        mock_window.mainloop.assert_called()

@patch("STT.STT")
@patch("spacy.load")
@patch("messenger.Messenger")
@patch("customtkinter.CTk")
@patch("customtkinter.CTkButton")
def test_buttonSpeakPress(mockt_ctk_button,mock_ctk,mock_stt,mock_spacy,mock_messenger):
    obj = GUI.GUI()
    eventObj = DummyEvent()
    eventObj.set_type(5)

    with patch.object(obj, "speakThread"), patch.object(obj, "stt") as mock_stt_obj:
        obj._GUI__buttonSpeakPress(eventObj)
        mock_stt_obj.sendSTTText.assert_called()