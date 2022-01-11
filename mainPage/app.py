from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests



app = Flask(__name__)

app.jinja_env.add_extension('jinja2.ext.loopcontrols')

client = MongoClient('3.34.190.40', 27017, username="test", password="test")
db = client.miniproj


@app.route('/')
def login():
    # DB에서 저장된 단어 찾아서 HTML에 나타내기
    return render_template("main.html")


@app.route('/main')
def main():
    id = request.args.get("id")

    # doc = {
    #    'id': id,
    #    'title': "제목 7",
    # }
    # db.like.insert_one(doc)

    like = list(db.like.find({}, {"_id": False}))
    post = list(db.review.find({'id': id}, {"_id": False}))
    return render_template("main.html",id=id, post = post, like = like)

@app.route('/create')
def create():
    id = request.args.get("id")

    return render_template("create.html",id=id)

@app.route('/create/save', methods=['POST'])
def save():
    user_receive = request.form["user_give"]
    title_receive = request.form["title_give"]
    add_receive = request.form["add_give"]
    img_receive = request.form["img_give"]
    desc_receive = request.form["desc_give"]
    tag_receive = request.form["tag_give"]


    doc={
        'id' : user_receive,
        'title' : title_receive,
        'add' : add_receive,
        'img' :img_receive,
        'desc':desc_receive,
        'tag' : tag_receive

    }
    db.review.insert_one(doc)

    return jsonify({'result': 'success', 'msg': '입력 완료'})


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