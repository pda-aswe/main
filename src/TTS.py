import pyttsx3
import platform

#own libraries
import singelton

class TTS(metaclass=singelton.SingletonMeta):
    def __init__(self):
        self.TTSEngine = pyttsx3.init()
        if platform.system() == "Windows":
            self.TTSEngine.setProperty('voice', "LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_DE-DE_HEDDA_11.0")
            self.TTSEngine.setProperty('rate', self.TTSEngine.getProperty('rate')-50)

    def speak(self,message):
        if type(message) == str:
            self.TTSEngine.say(message)
        else:
            self.TTSEngine.say(str(message.decode("utf-8")))
        self.TTSEngine.runAndWait()