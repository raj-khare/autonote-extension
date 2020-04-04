FROM python:3

WORKDIR /app

COPY app.py /app
COPY requirements.txt /app

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "app:app"]