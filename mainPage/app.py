from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests
import jwt
import datetime
import hashlib
from datetime import datetime, timedelta

from werkzeug.utils import secure_filename

app = Flask(__name__)

#jinja2에서 break 사용하기 위한 라이브러리
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

#기본 프로필 사진 업로드
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

#로그인 secret key
SECRET_KEY = 'SPARTA'


client = MongoClient('3.34.190.40', 27017, username="test", password="test")
db = client.miniproj


@app.route('/')
def home():
    return render_template("login.html")

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


# 로그인
@app.route('/sign_in', methods=['POST'])
def sign_in():

    #로그인 정보 receive
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    #받은 pw hash 암호화와
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()

    #유저 ID정보 확인
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    #ID정보가 DB에 존재
    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 0.5)  # 로그인 30분 유지
        }

        #토큰 암호화
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 조회 실패할 경우
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


#회원 가입
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    #유저의 ID, PW, nick receive
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    nick_receive = request.form['nick_give']
    #받은 PW hash 암호화
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()

    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "profile_name": username_receive,  # 프로필 이름 기본값은 아이디
        "nick": nick_receive,
        "profile_pic": "",  # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png",  # 프로필 사진 기본 이미지
        "profile_info": ""  # 프로필 한 마디

    }
    #db에 저장 후 결과 전달
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

#ID 중복 체크
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    #ID를 받아 DB에서 존재하는지 여부를 전달
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

#메인 화면
@app.route('/main')
def main():
    #토큰 receive
    token_receive = request.cookies.get('mytoken')
    try:
        #payload 선언
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        #db에서 알맞는 회원 정보를 user_info에 초기화
        user_info = db.users.find_one({"username": payload["id"]})

        #전달 정보 초기화
        all_user_info = list(db.users.find({},{'_id':0}))
        id = (user_info['username'])
        tag = request.args.get("tag")

        #search 정보
        if (tag == None):   #search 정보가 없을 경우
            post = list(db.review.find({}, {"_id": False}))
        else:               #search 정보가 있을 경우
            post = list(db.review.find({"tag": {"$regex": tag}}, {"_id": False}))

        return render_template("main.html", id=id, post=post, user_info=user_info,all_user_info = all_user_info)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

#게시물 포스트 페이지
@app.route('/create')
def create():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        id = (user_info['username'])

        return render_template("create.html", id=id)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

#게시물 포스팅
@app.route('/create/save', methods=['POST'])
def save():
    #포스팅 정보 receive
    user_receive = request.form["user_give"]
    title_receive = request.form["title_give"]
    add_receive = request.form["add_give"]
    desc_receive = request.form["desc_give"]
    tag_receive = request.form["tag_give"]

    #포스팅 정보 초기화
    doc={
        'id' : user_receive,
        'title' : title_receive,
        'add' : add_receive,
        'desc':desc_receive,
        'tag' : tag_receive.split(" "),
        'like' : []

    }

    if 'file_give' in request.files:
        file = request.files["file_give"]
        filename = secure_filename(file.filename)
        extension = filename.split(".")[-1]
        file_path = f"post_img/{title_receive}.{extension}"
        file.save("./static/" + file_path)
        doc["img"] = file_path

    #DB insert
    db.review.insert_one(doc)

    return jsonify({'result': 'success', 'msg': '입력 완료'})

#좋아요
@app.route('/main/like', methods=['POST'])
def like_post():
    #좋아요 누른 계정과 제목 receive
    id_receive = request.form["id_give"]
    title_receive = request.form["title_give"]

    #포스트의 like에 누른 계정 추가 후 업데이트
    post = db.review.find_one({'title' : title_receive}, {"_id": False})
    post['like'].append(id_receive)
    db.review.update_one({'title': title_receive},{'$set': {'like' : post['like']}})

    return jsonify({'result': 'success', 'msg': 'Like it!'})

#좋아요 취소
@app.route('/main/unlike', methods=['POST'])
def unlike_post():
    # 좋아요 누른 계정과 제목 receive
    id_receive = request.form["id_give"]
    title_receive = request.form["title_give"]

    # 포스트의 like에 누른 계정 제거 후 업데이트
    post = db.review.find_one({'title' : title_receive}, {"_id": False})
    post['like'].remove(id_receive)
    db.review.update_one({'title': title_receive},{'$set': {'like' : post['like']}})

    return jsonify({'result': 'success', 'msg': 'Cancle Like...'})

#포스트 상세 페이지
@app.route('/detail')
def detail():
    #포스트의 제목 receive
    title = request.args.get("title")
    #토큰 receive
    token_receive = request.cookies.get('mytoken')
    try:

        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})

        id = (user_info['username'])
        post = list(db.review.find({"title": title}, {"_id": False}))

        return render_template("detail.html", id=id, post = post)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
    return render_template("detail.html")

#유저 정보 수정 페이지
@app.route('/user')
def user():

    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})

        return render_template("user.html", id=id, user_info = user_info )

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
    return render_template("detail.html")

#계정 프로필 사진 변경
@app.route('/user/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        #변경점 receive
        username = payload["id"]
        name_receive = request.form["name_give"]
        nick_receive = request.form["nick_give"]
        about_receive = request.form["about_give"]

        new_doc = {
            "profile_name": name_receive,
            "nick": nick_receive,
            "profile_info": about_receive
        }
        #이미지 파일 경로 설정 후 저장
        if 'file_give' in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/{username}.{extension}"
            file.save("./static/"+file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path

        db.users.update_one({'username': payload['id']}, {'$set':new_doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)