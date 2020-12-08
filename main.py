# -*- coding: utf-8 -*-
# Import all needed libs
import glob

from flask import (
    Flask,
    render_template
)
from bs4 import BeautifulSoup, Comment
import requests
import json
import spacy
from spacy_ner import NerExtraction


# Load English tokenizer, tagger, parser, NER and word vectors
nlp = spacy.load("en_core_web_sm")
# Create the application instance
app = Flask(__name__, template_folder="templates")


# Create a URL route in our application for "/"
@app.route('/')
def home():
    """
    This function just responds to the browser ULR
    localhost:7000/

    :return:        the rendered template 'index.html'
    """
    return render_template('index.html')


# Api which parse text from list of urls in file
@app.route('/api/get_from_file', methods=["GET"])
def getParsePages():
    result = {}
    parsed_json = (json.loads(open("assets/InputData/input.json").read()))
    for url in parsed_json['urls']:
        html_text = requests.get(url).text
        key = url.rsplit('/', 1)[-1]
        text = getTextFromHtml(html_text)

        saveFile('assets/OutputData', key, json.dumps({key: text}))
        result.update({key: text})
    return str(json.dumps(result))


# Api which returns text from wiki by parameter
@app.route('/api/get_from_wiki/<param>', methods=["GET"])
def getParsePageWiki(param):
    url = "https://en.wikipedia.org/wiki/" + param
    html_text = requests.get(url).text
    text = getTextFromHtml(html_text)
    saveFile('assets/OutputData', param, json.dumps({param: text}))
    return text


# Ner extraction
@app.route('/api/ner_extract')
def getText():
    result = {}
    for filepath in glob.glob("assets/OutputData/*.json"):
        res = NerExtraction.extract_ner(open(filepath).read(), nlp)
        filename = filepath.split('/')[-1].split('\\')[-1].replace('.json', '')

        saveFile("assets/NerOutputData", filename, json.dumps(res))
        result.update({filename: res})
    return str(json.dumps(result))


# Function to save json to file
def saveFile(location, filename, json):
    location += '/' + filename + ".json"
    file = open(location, 'w+')
    file.write(json)


# Function to parse all text from html
def getTextFromHtml(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(host="localhost", port=7000, debug=True)
