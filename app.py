import redis
import re
from summarizer import Summarizer
from bs4 import BeautifulSoup
import requests
import rq
import os
from flask import Flask, request, jsonify, current_app

app = Flask(__name__)
model = Summarizer(model='distilbert-base-uncased')  # BERT Model
app.redis = redis.Redis.from_url(os.environ.get('REDIS_URL') or 'redis://')
app.task_queue = rq.Queue('tasks', connection=app.redis)


def make_notes(url):
    job = rq.get_current_job()
    try:
        article = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
        article_parsed = BeautifulSoup(article, 'html.parser')
        paragraphs = article_parsed.find_all('p')  # Getting all <p>CONTENT</p>
        article_content = []
        for p in paragraphs:
            article_content.append(p.text)
        notes = model("".join(article_content))
        job.meta['notes'] = notes
        job.save_meta()
    except:
        job.meta['failed'] = True
        job.save_meta()


@app.route('/notes', methods=['POST'])
def notes():
    data = request.json
    if not data or not data.get('url', None):
        return jsonify({'error': 'No url is given'}), 400
    url = data['url']
    if not re.match(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)", url):
        return jsonify({'error': 'Bad url format'}), 400
    job = current_app.task_queue.enqueue('app.make_notes', url)
    return jsonify({'status': 'Started', 'id': job.id})


@app.route("/notes/<job_id>", methods=['GET'])
def get_results(job_id):
    try:
        job = rq.job.Job.fetch(job_id, connection=current_app.redis)
        if job.is_finished:
            if not job.meta.get('failed'):
                return jsonify({'status': 'Done', 'notes': job.meta['notes']})
            else:
                return jsonify({'status': 'Failed', 'notes': None}), 400
        else:
            return jsonify({'status': 'Pending', 'notes': None}), 202
    except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
        return jsonify({'error': 'No such job'}), 400


if __name__ == "__main__":
    app.run()
