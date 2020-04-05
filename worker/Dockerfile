FROM python:3.7.7-slim-buster

WORKDIR /worker

COPY requirements.txt /worker

RUN pip install -r requirements.txt

CMD rq worker -u $REDIS_URL tasks