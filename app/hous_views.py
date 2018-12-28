import os

from flask import Blueprint, render_template, session, jsonify, request

from app.models import User, House, Area, Facility, HouseImage
from utils.functions import is_login
from utils.setting import upload_folder, MEDIA_PATH

hous = Blueprint('hous', __name__)



@hous.route('/myhous/', methods=['GET'])
def myhous():
    return render_template('myhous.html')


@hous.route('/house_info/', methods=['GET'])
@is_login
def house_info():
    user = User.query.get(session['user_id'])
    if user.id_card:
        # 实名认证成功
        houses = House.query.filter(House.user_id==session['user_id']).all()
        houses_list = [house.to_dict() for house in houses]
        return jsonify({'code': 200, 'houses_list': houses_list})
    else:
        return jsonify({'code': 1001, 'msg': '还未实名认证，请去认证!'})


@hous.route('/newhous/', methods=['GET'])
def newhous():

    return render_template('newhous.html')


@hous.route('/area_facility/', methods=['GET'])
def area_facility():
    # 获取城区信息
    areas = Area.query.all()
    # 获取设施信息
    facilitys = Facility.query.all()
    # 遍历出城区所对应的 区域编号id 和 区域名字name
    areas_json = [area.to_dict() for area in areas]
    # 遍历出设施信息所对应的 设施编号id 和 设施名字name 设施展示的图标css
    facilitys_json = [facility.to_dict() for facility in facilitys ]

    return jsonify({'code': 200, 'areas': areas_json, 'facilitys': facilitys_json})


@hous.route('/newhous/', methods=['POST'])
@is_login
def my_newhous():
    # 保存房屋信息，设施信息
    house = House()
    house.user_id = session['user_id']
    house.price = request.form.get('price')
    house.title = request.form.get('title')
    house.area_id = request.form.get('area_id')
    house.address = request.form.get('address')
    house.room_count = request.form.get('room_count')
    house.acreage = request.form.get('acreage')
    house.unit = request.form.get('unit')
    house.capacity = request.form.get('capacity')
    house.beds = request.form.get('beds')
    house.deposit = request.form.get('deposit')
    house.min_days = request.form.get('min_days')
    house.max_days = request.form.get('max_days')

    facilitys = request.form.getlist('facility')
    for facility_id in facilitys:
        facility = Facility.query.get(facility_id)
        # 多对多关联
        house.facilities.append(facility)
    house.add_update()
    return jsonify({'code': 200, 'msg': '成功', 'house_id': house.id})


@hous.route('/hous_images/', methods=['POST'])
def hous_images():
    # 创建房屋图片
    house_id = request.form.get('house_id')
    image = request.files.get('house_image')

    # 保存图片
    save_url = os.path.join(MEDIA_PATH, image.filename)
    image.save(save_url)
    # 保存房屋和图片信息
    house_image = HouseImage()
    house_image.house_id = house_id
    image_url = os.path.join(image.filename)
    house_image.url = image_url
    house_image.add_update()
    # 创建房屋首图
    house = House.query.get(house_id)
    if not house.index_image_url:
        house.index_image_url = image_url
        house.add_update()
    return jsonify({'code': 200, 'image_url': image_url})


@hous.route('/detail/', methods=['GET'])
def detail():
    return render_template('detail.html')


@hous.route('/house_detail/<int:id>/', methods=['GET'])
def house_detail(id):
    house = House.query.get(id)
    houses = house.to_full_dict()
    user_hous = House.query.filter(House.user_id==session['user_id']).all()
    if user_hous:
        return jsonify({'code': 7000, 'msg': 'GG', 'house': houses})
    return jsonify({'code': 200, 'house': houses})


@hous.route('/hindex/', methods=['GET'])
def my_index():
    user_id = session.get('user_id')
    # 验证用户的登录情况
    if user_id:
        user = User.query.get(user_id)
        username = user.name
    else:
        username = ''
    houses =House.query.filter(House.index_image_url != '')
    houses_image = [house.to_dict() for house in houses]

    return jsonify({'code':200, 'username':username, 'houses_image':houses_image})


@hous.route('/index/', methods=['GET'])
def index():
    return render_template('index.html')





























# @house_blueprint.route('/search/', methods=['GET'])
# def search():
#     return render_template('search.html')
#
#
# @house_blueprint.route('/my_search/', methods=['GET'])
# def search_house():
#
#     aid = request.args.get('aid')
#     sd = request.args.get('sd')
#     ed = request.args.get('ed')
#     sk = request.args.get('sk')
#     # 过滤区域信息
#     house = House.query.filter(House.area_id==aid)
#     # 过滤登录用户发布房屋信息
#     if 'user_id' in session:
#         hlist = house.filter(House.user_id != session['user_id'])
#     # 查询不满足条件的房屋id
#     order1 = Order.query.filter(Order.begin_date <= sd, Order.end_date >= ed)
#     order2 = Order.query.filter(Order.begin_date <= sd, Order.end_date >= sd)
#     order3 = Order.query.filter(Order.begin_date >= sd, Order.begin_date <= ed)
#     order4 = Order.query.filter(Order.begin_date >= sd, Order.end_date <= ed)
#     house_ids1 = [order.house_id for order in order1]
#     house_ids2 = [order.house_id for order in order2]
#     house_ids3 = [order.house_id for order in order3]
#     house_ids4 = [order.house_id for order in order4]
#
#     house_ids = list(set(house_ids1 + house_ids2 + house_ids3 + house_ids4))
#     # 最终展示的房屋信息
#     houses = hlist.filter(House.id.notin_(house_ids))
#
#     if sk == 'booking':
#         houses = houses.order_by('order_count')
#     elif sk == 'price-inc':
#         houses = houses.order_by('price')
#     elif sk == 'price-des':
#         houses = houses.order_by('-price')
#     else:
#         houses = houses.order_by('-id')
#
#     houses_dict = [house.to_dict() for house in houses]
#
#     return jsonify(code=status_code.OK, house_dict=houses_dict)