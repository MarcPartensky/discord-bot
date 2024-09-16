#!/bin/sh

apk update

curl -LsSf https://astral.sh/uv/install.sh | sh
apk add --no-cache --virtual .build build-base libffi-dev

apk add ffmpeg postgresql p7zip &
# pip install -r requirements.txt 
uv sync -v &
wait

# apk del .build &
# rm -rf /var/cache/apk/* /tmp/* &
# wait
