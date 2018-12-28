import os
import re

from flask import Blueprint, render_template, request, jsonify, session,url_for

from app import form
from app.models import User
from utils.functions import generateImageCode, is_login
from utils.setting import MEDIA_PATH

user = Blueprint('user', __name__)



@user.route('/verify/', methods=['GET','POST'])
def verify():
    if request.method == 'POST':
        code = generateImageCode()
        session['code'] = code
        return jsonify({'code': 200, 'msg': '验证成功', 'verify': code})


@user.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        mobile = request.form.get('phone')
        imagecode = request.form.get('imagecode')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        # 验证参数是否完整
        if not all([mobile, imagecode, password, password2]):
            return jsonify({'code': 7001, 'msg': '请把字段填写完整'})
        # 验证验证码是否一致
        if session['code'] != imagecode:
            return jsonify({'code': 7002, 'msg': '验证码不一致请重新填写'})
        # 验证手机号是否正确
        if not re.match(r'^1[3456789]\d{9}$', mobile):
            return jsonify({'code': 7003, 'msg': '该手机号无效'})
        # 验证密码是否一致
        if password != password2:
            return jsonify({'code': 7004, 'msg': '密码不一致'})
        # 验证手机号是否已经被注册
        if User.query.filter(User.phone==mobile).count():
            return jsonify({'code': 7005, 'msg': '该手机号已被注册'})
        # 验证邮箱格式是否正确
        if not re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email):
            return jsonify({'code': 7006, 'msg': '邮箱格式不正确'})
        # 该手机号如果不存在就添加到数据库
        user = User()
        user.phone = mobile
        user.password = password
        user.name = mobile
        user.email = email
        user.save()

        return jsonify({'code': 200, 'msg': '请求成功'})


@user.route('/login/', methods=['GET'])
def login():
        return render_template('login.html')


@user.route('/login/', methods=['POST'])
def my_login():
    mobile = request.form.get('mobile')
    password = request.form.get('password')
    if not all([mobile, password]):
        return jsonify({'code': 7001, 'msg': '请把字段填写完整'})
    # 判断登录手机号格式
    if not re.match(r'^1[3456789]\d{9}$', mobile):
        return jsonify({'code': 7002, 'msg': '该手机号格式不正确'})
    # 获取登录手机号与数据库是否一致
    user = User.query.filter(User.phone == mobile).first()
    if not user:
        return jsonify({'code': 7003, 'msg': '该手机号没有注册，请去注册'})
    if not user.check_pwd(password):
        return jsonify({'code': 7004, 'msg': '密码错误，请想好了在输入'})
    session['user_id'] = user.id
    return jsonify({'code': 200, 'msg': '请求成功'})


@user.route('/logout/', methods=['GET'])
def logout():
    session.clear()
    return jsonify({'code': 200, 'msg': '请求成功'})


@user.route('/my/', methods=['GET'])
@is_login
def my():
    return render_template('my.html')


@user.route('/user_info/', methods=['GET'])
@is_login
def user_info():
    user_id = session['user_id']
    user = User.query.get(user_id)
    user_info = user.to_basic_dict()
    return jsonify(user_info=user_info, code=200)


@user.route('/profile/', methods=['GET'])
@is_login
def profile():
    return render_template('profile.html')


@user.route('/profile/', methods=['PATCH'])
@is_login
def wmy_profile():
    avatar = request.files.get('avatar')
    if avatar:
        # 判断图片格式是否正确
        if not re.match(r'image/*', avatar.mimetype):
            return jsonify({'code': 7001, 'msg': '请上传正确图片格式'})
        # 保存图片
        avatars = os.path.join(MEDIA_PATH, avatar.filename)
        avatar.save(avatars)
        # 修改图片字段
        user = User.query.get(session['user_id'])
        user.avatar = avatar.filename
        user.save()
        try:
            user.add_update()
            return jsonify(code=200, avatar=avatar)
        except:
            return jsonify({'code': 500, 'msg': '罩不住了'})


@user.route('/profile/', methods=['POST'])
@is_login
def my_profile():
    name = request.form.get('name')
    if name:
        if User.query.filter(User.name==name).count():
            return jsonify({'code': 7002, 'msg': '名字重复无需更改'})
        user = User.query.get(session['user_id'])
        user.name = name
        try:
            user.add_update()
            return jsonify(code=200)
        except:
            return jsonify({'code': 7003, 'msg': '啊啊啊啊啊'})


@user.route('/auth/', methods=['GET', 'PATCH'])
@is_login
def auth():
    if request.method == 'GET':
        return render_template('auth.html')

    if request.method == 'PATCH':
        real_name = request.form.get('real_name')
        id_card = str(request.form.get('id_card'))
        # 判断姓名格式是否合格
        if not re.match(r'^[\u4E00-\u9FA5A-Za-z]+$', real_name):
            return jsonify({'code': 7001, 'msg': '输入的姓名格式不对'})
        # 判断身份证是否合格
        if not re.match(r'^[1-9]\d{5}[1-9]\d{3}((0\d)|(1[0-2]))(([0|1|2]\d)|3[0-1])\d{3}([0-9]|X)$', id_card):
            return jsonify({'code': 7002, 'msg': '您输入的身份证格式错误!'})
        user = User.query.get(session['user_id'])
        user.id_card = id_card
        user.id_name = real_name
        try:
            user.add_update()
            return jsonify(code=200)
        except:
            return jsonify({'code': 7003, 'msg': '失败'})


@user.route('/info_auth/', methods=['GET'])
def info_auth():
    user = User.query.filter(User.id==session['user_id']).first()
    info = user.to_auth_dict()
    return jsonify({'code': 100, 'msg': '请求成功', 'info': info})









