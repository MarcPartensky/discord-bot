#!/bin/sh

rm -rf .venv
uv sync -v
uv run --directory discord_bot python .
