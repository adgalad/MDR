#!/bin/bash

echo Starting Mega Dash Raffle

sudo kill -9 `ps -alef | grep python3 | awk '{print($4)}'`

python3 manage.py makemigrations app
python3 manage.py migrate

sudo DASH_CLI=/home/ubuntu/dashcore-0.12.3/bin/dash-cli RPC_SERVER=54.224.101.39 RPC_USER=carlos RPC_PASSWORD=carlos python3 manage.py runserver 0.0.0.0:80 > log.txt &
sudo DASH_CLI=/home/ubuntu/dashcore-0.12.3/bin/dash-cli RPC_SERVER=54.224.101.39 RPC_USER=carlos RPC_PASSWORD=carlos python3 manage.py update_raffle > cron.txt &
