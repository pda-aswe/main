import json
from copy import deepcopy
from datetime import datetime, timedelta
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

#own libraries
import singelton
import messenger

class Preferences(metaclass=singelton.SingletonMeta):
    def __init__(self,filepath):
        self.preferences = {}
        self.filepath = filepath
        self.mqttClient = messenger.Messenger()
        self.mqttClient.setPreferenceCallback(self.send)
        self.loadPreferencesFromFile()

        #setup file watchdog
        event_handler = PreferencesFileHandler(self)
        #only polling observer working --> os nativ broken in windows
        self.observer = PollingObserver()
        self.observer.schedule(event_handler,  path=filepath,  recursive=False)
        self.observer.start()

    def loadPreferencesFromFile(self):
        try:
            with open(self.filepath) as preferncesFile:
                newPreferences = json.load(preferncesFile)
        except FileNotFoundError:
            newPreferences = {}

        #send new preferences
        preferenceDifference = self.__jsonDifference(self.preferences,newPreferences)
        if preferenceDifference is not None:
            self.__sendPreferenceStructure("pref",preferenceDifference)
        self.preferences = deepcopy(newPreferences)
    
    def clear(self):
        self.preferences = {}

    def send(self,path):
        if path == "all":
            self.__sendPreferenceStructure("pref",self.preferences)
        else:
            returnData = self.preferences
            keys = path.split("/")
            if len(keys) != 0:
                for key in keys[1:]:
                    if key == "":
                        continue
                    if key in returnData:
                        returnData = returnData[key]
                    else:
                        returnData = None
                        break
            else:
                returnData = None
            if returnData is not None:
                self.__sendPreferenceStructure(path,returnData)

    def __sendPreference(self,path,value):
        if type(value) is list:
            self.mqttClient.publish(path, json.dumps(value))
        else:
            self.mqttClient.publish(path, value)

    def __sendPreferenceStructure(self,path,prefStructure):
        if type(prefStructure) is str:
            self.__sendPreference(path,prefStructure)
        else:
            for key in prefStructure:
                if type(prefStructure[key]) is dict:
                    self.__sendPreferenceStructure(path+"/"+key,prefStructure[key])
                else:
                    self.__sendPreference(path+"/"+key,prefStructure[key])

    def stop(self):
        #stop file watchdog
        self.observer.stop()

    def __jsonDifference(self,oldData,newData):
        difference = {}
        for key in newData:
            if key in oldData:
                if type(newData[key]) is dict:
                    retData = self.__jsonDifference(oldData[key],newData[key])
                    if retData:
                        difference[key] = retData
                else:
                    if oldData[key] != newData[key]:
                        difference[key] = newData[key]
            else:
                difference[key] = newData[key]
        return difference if difference else None

class  PreferencesFileHandler(FileSystemEventHandler):
    def __init__(self,preferencesObj):
        self.last_modified = datetime.now()
        self.preferences = preferencesObj

    #UPDATE
    def  on_modified(self,  event):
        if datetime.now() - self.last_modified < timedelta(seconds=1):
            return
        else:
            self.last_modified = datetime.now()
        #find new preferences and sent them
        self.preferences.loadPreferencesFromFile()
        

    #UPDATE
    def  on_created(self,  event):
        self.preferences.loadPreferencesFromFile()

    def  on_deleted(self,  event):
        self.preferences.clear()