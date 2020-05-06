#!/bin/bash

apt-get update -y
apt-get upgrade -y
apt-get install -y python3-pip

pip3 install --upgrade flask
pip3 install --upgrade flask-login
pip3 install --upgrade werkzeug
pip3 install --upgrade requests
pip3 install --upgrade flask_httpauth

mkdir /home/sstein17/authentication_server
cd /home/sstein17/authentication_server

while [ ! -f /auth_server.py ]
do
	sleep 5
done
sleep 5
python3 auth_server.py
