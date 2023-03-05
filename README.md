# main
Weitere Dienste und Use-Cases-Container können in der docker-compose.yaml Datei hinzugefügt werden. Der Aufbau sieht wie folgt aus:

```
  <Container-name>:
    image: "ghcr.io/pda-aswe/<Repo-Name>"
    restart: on-failure
```

Mit `docker compose pull` werden die aktuellen Dockerimages der hinterlegten Repos in der docker-compose.yaml Datei heruntergeladen.

Mit  `docker compose up` werden die neuen Container gestartet.