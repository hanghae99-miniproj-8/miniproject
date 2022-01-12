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
    tag = request.args.get("tag")
    print(tag)
    if(tag == None):
        post = list(db.review.find({}, {"_id": False}))
    else:
        post = list(db.review.find({"tag": {"$regex": tag}}, {"_id": False}))
    like = list(db.like.find({'id': id}, {"_id": False}))

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
        'tag' : tag_receive.split(" ")

    }
    db.review.insert_one(doc)

    return jsonify({'result': 'success', 'msg': '입력 완료'})

@app.route('/main/like', methods=['POST'])
def like_post():
    id_receive = request.form["id_give"]
    title_receive = request.form["title_give"]
    doc = {
        'id' : id_receive,
        'title' : title_receive
    }
    db.like.insert_one(doc)

    return jsonify({'result': 'success', 'msg': 'Like it!'})


@app.route('/main/unlike', methods=['POST'])
def unlike_post():
    id_receive = request.form["id_give"]
    title_receive = request.form["title_give"]

    db.like.delete_one(({'id': id_receive, 'title' : title_receive}))

    return jsonify({'result': 'success', 'msg': 'Cancle Like...'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)