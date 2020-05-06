#!/bin/bash

apt-get update -y
apt-get upgrade -y
apt-get install -y python3-pip

pip3 install --upgrade flask
pip3 install --upgrade flask-login
pip3 install --upgrade werkzeug
pip3 install --upgrade requests
pip3 install --upgrade flask_httpauth


cd /home/sstein17
while [ ! -f /server.py ]
do
	sleep 5
done
python3 server.py
