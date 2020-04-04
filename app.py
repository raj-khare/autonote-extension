import re
from summarizer import Summarizer
from bs4 import BeautifulSoup
import requests
from flask import Flask, request, jsonify
app = Flask(__name__)


@app.route('/notes', methods=['POST'])
def notes():
    data = request.json
    if not data or not data.get('url', None):
        return jsonify({'error': 'No url is given'}), 400
    url = data['url']
    if not re.match(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)", url):
        return jsonify({'error': 'Bad url format'}), 400
    article = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
    article_parsed = BeautifulSoup(article, 'html.parser')
    paragraphs = article_parsed.find_all('p')  # Getting all <p>CONTENT</p>
    article_content = []
    for p in paragraphs:
        article_content.append(p.text)
    model = Summarizer(model='distilbert-base-uncased')
    return jsonify({'notes': model("".join(article_content))})


if __name__ == "__main__":
    app.run()
