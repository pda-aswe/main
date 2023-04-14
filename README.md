# main

## WICHTIG
Im Google-Drive des PDA-Google-Accounts liegt ein credentials-Ordner. Dieser muss vor dem Start des Main-Repos in den src-Ordner gelegt werden.

Die Main.py muss aufgerufen werden, wenn man sich in dem Order src befindet, sonst gibt es Probleme beim auslesen der preferences.json-Datei.

Vor dem ersten aufrufen der Main muss der Befehl `python -m spacy download de_core_news_lg` ausgeführt werden.

## Allgemein
Weitere Dienste und Use-Cases-Container können in der docker-compose.yaml Datei hinzugefügt werden. Zusätzlich muss in der main.py die Liste mit allen Containernamen angepasst werden.

Mit `docker compose pull` werden die aktuellen Dockerimages der hinterlegten Repos in der docker-compose.yaml Datei heruntergeladen.

Mit `docker compose up` werden die neuen Container gestartet.

Mit `pip3 install -r requirements.txt` werden alle benötigen Python Pakete nachinstalliert.

## Datenstruktur des Topics stt
```json
{
   "base":"<USRPÜNGLICHER STT-TEXT>",
   "tokens":[
      {
         "type":"VERB",
         "token":"informieren",
         "stopWord":false
      },
      {
         "type":"NOM",
         "token":"apple",
         "stopWord":false
      },
   ],
   "verbs":[
      "LISTE","ALLER","VERBEN"
   ],
   "nouns":[
      "LISTE","ALLER","NOMEN"
   ],
   "numbers":[
      "LISTE","ALLER","ZAHLEN"
   ],
   "adp":[
      "LISTE","ALLER","ADPOSITIONEN"
   ],
   "adj":[
      "LISTE","ALLER","ADJEKTIVE"
   ],
   "adv": [
      "LISTE","ALLER","ADVERBEN"
   ],
   "cleaned":"<STT OHNE STOPWÖRTER UND NUR GRUNDFORMEN>"
}
```