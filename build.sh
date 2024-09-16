#!/bin/sh

apk update

apk add --no-cache --virtual .build build-base libffi-dev &

apk add ffmpeg postgresql p7zip &
pip install -r requirements.txt &
wait

# apk del .build &
# rm -rf /var/cache/apk/* /tmp/* &
# wait
