from src import TTS
from unittest.mock import patch, ANY, MagicMock

def test_speak():
    obj = TTS.TTS()

    with patch.object(obj, 'TTSEngine') as mock_tts:
        obj.speak("Hallo Unit-Test")
        mock_tts.say.assert_called_with("Hallo Unit-Test")