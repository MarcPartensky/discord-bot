#!/bin/sh

# rm -rf .venv
# uv cache prune
# uv sync -v
uv run --directory discord_bot python .
