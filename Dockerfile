FROM python:3.8.12 as builder

RUN pip install pipenv
COPY Pipfile Pipfile
RUN pipenv lock --pre --clear
RUN pipenv lock -r > requirements.txt

FROM python:3.8.12-slim
LABEL maintainer="marc.partensky@gmail.com"
LABEL image="https://hub.docker.com/r/marcpartensky/discord-bot"
LABEL source="https://github.com/marcpartensky/discord-bot"
RUN apt-get update && apt-get upgrade -y && apt autoremove -y
# RUN add-apt-repository ppa:mc3man/trusty-media
RUN apt-get install -y ffmpeg git

WORKDIR /app
COPY ./tts tts
COPY ./libs libs
COPY ./assets assets
COPY ./utils utils
COPY ./config config
COPY ./models models
COPY ./cogs cogs
COPY  __main__.py LICENSE ./
# COPY --from=builder requirements.txt ./
COPY requirements.txt ./

RUN pip install -U pip
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "__main__.py"]
