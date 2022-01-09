FROM python:3.8.12-slim
LABEL maintainer="marc.partensky@gmail.com"
LABEL image="https://hub.docker.com/r/marcpartensky/discord-bot"
LABEL source="https://github.com/marcpartensky/discord-bot"
RUN apt-get update && apt-get upgrade -y && apt-get autoremove -y
# RUN add-apt-repository ppa:mc3man/trusty-media
RUN apt-get install -y ffmpeg git curl
COPY Pipfile.lock ./

RUN pip install -U pip pipenv
RUN pipenv install --system

WORKDIR /app
COPY ./tts tts
COPY ./libs libs
COPY ./assets assets
COPY ./utils utils
COPY ./config config
COPY ./models models
COPY ./cogs cogs
COPY  __main__.py LICENSE ./

ENV DISCORD_BOT_HOST 0.0.0.0
ENV DISCORD_BOT_PORT 8000
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl -f http://localhost:8000/live || exit 1

ENTRYPOINT ["python", "__main__.py"]
