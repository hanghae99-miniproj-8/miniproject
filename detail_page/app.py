from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests

app = Flask(__name__)

client = MongoClient('3.37.130.181', 27017, username="test", password="test")
db = client.miniproj

@app.route('/')
def main():
    # DB에서 저장된 단어 찾아서 HTML에 나타내기
    return "this is main page"


@app.route('/detail')
def detail():
    return render_template("detail.html")

@app.route('/save', methods=['POST'])
def write_review():
    user_receive = request.form['user_give']
    title_receive = request.form['title_give']
    add_receive = request.form['add_give']
    img_receive = request.form['img_give']
    desc_receive = request.form['desc_give']
    tag_receive = request.form['tag_give']

    doc = {
        "title": title_receive,
        "add": add_receive,
        "img": img_receive,
        "desc": desc_receive,
        "tag": tag_receive
    }

    db.posting.insert_one(doc)

    return jsonify({"msg": "posting completed"})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

