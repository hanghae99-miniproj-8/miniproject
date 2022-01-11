from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests


app = Flask(__name__)

client = MongoClient('3.34.190.40', 27017, username="test", password="test")
db = client.miniproj


@app.route('/')
def main():
    # DB에서 저장된 단어 찾아서 HTML에 나타내기
    return render_template("main.html")


@app.route('/main')
def detail():
    id = request.args.get("id")

    #doc = {
    #    'id': id,
    #    'title': "제목 5",
    #    'content': "컨텐츠 5"
    #}
    #db.review.insert_one(doc)

    post = list(db.review.find({'id': id}, {"_id": False}))
    return render_template("main.html",id=id, post = post)


@app.route('/api/save_word', methods=['POST'])
def save_word():
    # 단어 저장하기
    return jsonify({'result': 'success', 'msg': '단어 저장'})


@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    # 단어 삭제하기
    return jsonify({'result': 'success', 'msg': '단어 삭제'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)