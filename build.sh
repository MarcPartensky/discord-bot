#!/bin/sh

apk update
apk add curl

curl -LsSf https://astral.sh/uv/install.sh | sh &
apk add --no-cache --virtual .build build-base libffi-dev &
wait

apk add ffmpeg postgresql p7zip &
# pip install -r requirements.txt 
uv sync -v &
wait

# apk del .build &
# rm -rf /var/cache/apk/* /tmp/* &
# wait
