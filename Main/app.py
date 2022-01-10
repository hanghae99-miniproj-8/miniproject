from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests


app = Flask(__name__)

client = MongoClient('3.34.190.40', 27017, username="test", password="test")
db = client.dbsparta_plus_week2


@app.route('/')
def main():
    # DB에서 저장된 단어 찾아서 HTML에 나타내기
    msg = request.args.get("msg")
    words = list(db.words.find({},{"_id" : False}))
    return render_template("index.html",words = words,msg = msg)


@app.route('/detail/<keyword>')
def detail(keyword):
    # API에서 단어 뜻 찾아서 결과 보내기
    status_receive = request.args.get("status_give")
    r = requests.get(f"https://owlbot.info/api/v4/dictionary/{keyword}", headers={"Authorization": "Token 54c8a25ffc9d2460bc54412c0b7261225875abd1"})
    #제대로 받을 경우는 무조건 200
    if r.status_code != 200:
        return redirect(url_for("main", msg = "단어가 이상행.."))
    result = r.json()
    print(result)
    return render_template("detail.html", word=keyword, result = result, status = status_receive)


@app.route('/api/save_word', methods=['POST'])
def save_word():
    # 단어 저장하기
    word_receive = request.form["word_give"]
    def_receive = request.form["def_give"]
    doc = {
        "word" : word_receive,
        "def" : def_receive
    }
    db.words.insert_one(doc)
    return jsonify({'result': 'success', 'msg': f'단어 {word_receive} 저장'})


@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    # 단어 삭제하기
    word_receive = request.form["word_give"]
    db.words.delete_one({"word" : word_receive})
    return jsonify({'result': 'success', 'msg': f'단어 {word_receive} 삭제'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)