#!/bin/sh

apk update

pip install -U uv &
add --no-cache --virtual .build build-base libffi-dev &
wait

apk add ffmpeg postgresql p7zip &
uv sync -v &
wait

apk del .build &
rm -rf /var/cache/apk/* /tmp/* &
wait
