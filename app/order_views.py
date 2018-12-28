from datetime import datetime

from flask import Blueprint, render_template, request, session, jsonify

from app.models import House, Order
from utils.functions import is_login

order = Blueprint('order', __name__)


@order.route('/orders/', methods=['GET'])
def orders():
    order = None
    if request.method == 'GET':
        return render_template('orders.html', order=order)


@order.route('/orders/', methods=['POST'])
def my_orders():
    house_id = request.form.get('house_id')
    begin_date = datetime.strptime(request.form.get('begin_date'), '%Y-%m-%d')
    end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')

    house = House.query.get(house_id)

    order = Order()
    order.user_id = session['user_id']
    order.house_id = house_id
    order.begin_date = begin_date
    order.end_date = end_date
    order.days = (end_date - begin_date).days + 1
    order.house_price = house.price
    order.amount = order.days * order.house_price

    order.add_update()

    return jsonify({'code': 200, 'msg': '成功'})


@order.route('/booking/', methods=['GET'])
def booking():
    return render_template('booking.html')


@order.route('/user_orders/', methods=['GET'])
@is_login
def user_orders():
    orders = Order.query.filter(Order.user_id==session['user_id']).all()
    order = [order.to_dict() for order in orders]
    return jsonify({'code': 200, 'msg': '成功', 'orders': order})


@order.route('/lorders/', methods=['GET'])
@is_login
def lorders():
    return render_template('lorders.html')


@order.route('/my_lorders/', methods=['GET'])
def my_lorders():
    # 获取登录的session[user_id]
    user_id = session['user_id']
    houses = House.query.filter(House.user_id==user_id)
    houses_ids = [house.id for house in houses]

    orders = Order.query.filter(Order.house_id.in_(houses_ids))
    orders_list = [order.to_dict() for order in orders]
    return jsonify(code=200, order=orders_list)
