FROM python:3.7.7-slim-buster

WORKDIR /app

COPY app.py /app
COPY requirements.txt /app

RUN pip install -r requirements.txt

CMD gunicorn app:app