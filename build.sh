#!/bin/sh

apk update

pip install -U uv &
apk add --no-cache --virtual .build build-base libffi-dev &
wait

apk add ffmpeg postgresql p7zip
uv sync -v
uv cache clean
uv sync -v

# apk del .build &
# rm -rf /tmp/* /var/apk/cache/*
