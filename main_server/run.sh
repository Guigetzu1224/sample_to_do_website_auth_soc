#!/bin/bash
echo 'Launching the server'
IPS=$(cat ./api_ip.txt)
python3 main.py $IPS

