#!/bin/sh

apk update
apk add curl

curl -LsSf https://astral.sh/uv/install.sh | sh &
apk add --no-cache --virtual .build build-base libffi-dev &
wait
export PATH="$PATH:$HOME/.cargo/bin"

# uv sync -v &
uv pip compile pyproject.toml -o requirements.txt
# uv export > requirements.txt
# sed -i '1,2d' requirements.txt
pip install -r requirements.txt  &
apk add ffmpeg postgresql p7zip &
wait
# apk del .build &
# rm -rf /var/cache/apk/* /tmp/* &
# wait
