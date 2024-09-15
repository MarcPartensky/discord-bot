#!/bin/sh

apk update

pip install -U uv &
apk add --no-cache build-base libffi-dev ffmpeg postgresql p7zip &
wait

uv sync -v
# rm -rf .venv
# uv sync -v

# apk del .build
# rm -rf /tmp/* /var/apk/cache/*
