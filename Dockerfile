FROM python:3.8.13-alpine AS alpine
LABEL maintainer="marc.partensky@proton.me"
LABEL image="https://hub.docker.com/r/marcpartensky/discord-bot"
LABEL source="https://github.com/marcpartensky/discord-bot"

WORKDIR /app
COPY README.md LICENSE pyproject.toml uv.lock build.sh ./
COPY ./discord_bot discord_bot
RUN ./build.sh

ENV DISCORD_BOT_HOST=0.0.0.0
ENV DISCORD_BOT_PORT=8000
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl -f http://localhost:8000/live || exit 1
ENTRYPOINT ["uv", "run", "--directory", "discord_bot", "python", "."]
