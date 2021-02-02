FROM python:3.8.3

COPY . .
WORKDIR .

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "."]
