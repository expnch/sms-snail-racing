FROM python:3.7-slim-buster

COPY requirements.txt .

RUN mkdir /app &&\
    pip install -r requirements.txt

WORKDIR /app

COPY *.py ./

ENTRYPOINT python controller.py
