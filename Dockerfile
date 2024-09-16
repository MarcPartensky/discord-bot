FROM python:3.8.13-alpine AS uv-export
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev
RUN uv pip freeze > requirements.txt

FROM python:3.8.13-alpine AS alpine
LABEL maintainer="marc.partensky@proton.me"
LABEL image="https://hub.docker.com/r/marcpartensky/discord-bot"
LABEL source="https://github.com/marcpartensky/discord-bot"

WORKDIR /app
COPY README.md LICENSE build.sh ./
COPY --from=uv-export /app/requirements.txt /app/requirements.txt
RUN ./build.sh
COPY ./discord_bot discord_bot
WORKDIR /app/discord_bot
# RUN uv venv

ENV DISCORD_BOT_HOST=0.0.0.0
ENV DISCORD_BOT_PORT=8000
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl -f http://localhost:8000/live || exit 1
# ENTRYPOINT ["uv", "run", "--directory", "discord_bot", "python", "."]
ENTRYPOINT ["python", "."]
