FROM python:3.7-slim-buster

ENV WEB_PORT=5000

COPY requirements.txt .

RUN mkdir /app &&\
    pip install -r requirements.txt

WORKDIR /app

COPY *.py ./

ENTRYPOINT gunicorn --bind 0.0.0.0:"$WEB_PORT" wsgi:app
