#!/bin/sh

apk update
apk add curl

curl -LsSf https://astral.sh/uv/install.sh | sh &
apk add --no-cache --virtual .build build-base libffi-dev &
wait

uv sync -v &
apk add ffmpeg postgresql p7zip &
fg

# pip install -r requirements.txt 
# apk del .build &
# rm -rf /var/cache/apk/* /tmp/* &
# wait
