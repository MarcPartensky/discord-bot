FROM python:3.8.3

RUN apt-get update
# RUN add-apt-repository ppa:mc3man/trusty-media
# RUN apt-get update && apt-get install -y ffmpeg
RUN apt-get install -y ffmpeg

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install -U pip

ENTRYPOINT ["python", "."]
