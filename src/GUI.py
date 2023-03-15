from tkinter import *
import customtkinter
import threading

class GUI:
    def __init__(self,stt,debug=False):
        #setup vars
        self.speakThread = None
        self.debug = debug
        self.stt = stt

        #setup window
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("green")
        self.window = customtkinter.CTk()
        self.window.geometry("400x240")
        self.window.title('BARD')
        button = customtkinter.CTkButton(master=self.window, text='Speak')
        button.bind('<ButtonPress-1>',self.__buttonSpeakPress)
        button.bind('<ButtonRelease-1>',self.__buttonSpeakPress)
        button.place(relx=0.5,rely=0.4,anchor=CENTER)
     
    def display(self):
        self.window.mainloop()
     
    def __buttonSpeakPress(self,event=None):
        global STTRecognizer
        if event and int(event.type) == 4:
            self.speakThread = threading.Thread(target=self.stt.speakRecordingThread)
            self.speakThread.start()
        elif event and int(event.type) == 5:
            self.speakThread.run = False
            self.speakThread.join()
            print(self.stt.getText())
            #sendSTTMessage()