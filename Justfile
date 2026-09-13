set dotenv-load := true

image := "marcpartensky/discord-bot"

default:
    @just --list

# lance le bot en local
run:
    uv run --directory discord_bot python .

# installe les deps
sync:
    uv sync

# build l'image
build:
    podman build -t {{image}}:local .

# lance l'image
docker-run:
    podman run --rm -it --env-file .env {{image}}:local

# logs du service
logs:
    journalctl -fu podman-discord-bot

# relance le service
restart:
    sudo systemctl reset-failed podman-discord-bot
    sudo systemctl restart podman-discord-bot
