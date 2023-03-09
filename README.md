# main
Weitere Dienste und Use-Cases-Container können in der docker-compose.yaml Datei hinzugefügt werden. Zusätzlich muss in der main.py die Liste mit allen Containernamen angepasst werden.

Mit `docker compose pull` werden die aktuellen Dockerimages der hinterlegten Repos in der docker-compose.yaml Datei heruntergeladen.

Mit `docker compose up` werden die neuen Container gestartet.

Mit `pip3 install -r requirements.txt` werden alle benötigen Python Pakete nachinstalliert.