from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests



app = Flask(__name__)

app.jinja_env.add_extension('jinja2.ext.loopcontrols')

client = MongoClient('3.37.130.181', 27017, username="test", password="test")
db = client.miniproj

@app.route('/')
def main():
    # DB에서 저장된 단어 찾아서 HTML에 나타내기
    return "this is main page"


@app.route('/detail')
def detail():
    return render_template("detail.html", user="id")

@app.route('/spec/<keyword>')
def spec(keyword):
    id = request.args.get("user")
    post = db.posting.find_one({"title": keyword}, {"_id": False})
    return render_template("specific.html", id=id, post=post)

@app.route('/save', methods=['POST'])
def write_review():
    user_receive = request.form['user_give']
    title_receive = request.form['title_give']
    add_receive = request.form['add_give']
    img_receive = request.form['img_give']
    desc_receive = request.form['desc_give']
    tag_receive = request.form['tag_give'].split(' ')

    doc = {
        "user": user_receive,
        "title": title_receive,
        "add": add_receive,
        "img": img_receive,
        "desc": desc_receive,
        "tag": tag_receive
    }

    db.posting.insert_one(doc)

    return jsonify({
        "msg": "posting completed",
        "tag": tag_receive
    })


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)