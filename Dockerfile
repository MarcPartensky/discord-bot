FROM python:3.8.12 as builder

RUN pip install pipenv
COPY Pipfile Pipfile
RUN pipenv lock --pre --clear
RUN pipenv lock -r > requirements.txt

FROM python:3.8.12-slim
LABEL maintainer="marc.partensky@gmail.com"
RUN apt-get update && apt-get upgrade -y && apt autoremove -y
# RUN add-apt-repository ppa:mc3man/trusty-media
RUN apt-get install -y ffmpeg

WORKDIR /app
COPY assets cogs config libs models tts utils __main__.py LICENSE ./
COPY --from=builder requirements.txt ./

RUN pip install -U pip
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "."]
