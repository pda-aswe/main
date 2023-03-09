#!/usr/bin/python3

import docker
import time
import subprocess

containerNames = ["bard-broker","bard-casepreis", "bard-casesport", "bard-casenews", "bard-casewelcome", "bard-servicewetter", "bard-serviceverkehrsinfos", "bard-servicekalender", "bard-servicenews", "bard-servicelocation", "bard-servicesport", "bard-servicepreis", "bard-servicemail"]

#connect to docker
#more information: https://docker-py.readthedocs.io/en/stable/client.html
client = docker.from_env()

#start all container
subprocess.run(["docker", "compose", "up", "-d"])

#main code
time.sleep(60)

#stop all container
subprocess.run(["docker", "compose", "stop"])