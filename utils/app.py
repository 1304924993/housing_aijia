from flask import Flask

from app.hous_views import hous
from app.models import db
from app.order_views import order
from app.user_views import user
from utils.config import Conf
from utils.setting import STATIC_PATH, TEMPLATE_PATH


def create_app():
    app = Flask(__name__,
                static_folder=STATIC_PATH,
                template_folder=TEMPLATE_PATH)

    app.config.from_object(Conf)

    app.register_blueprint(blueprint=user, url_prefix='/user')
    app.register_blueprint(blueprint=hous, url_prefix='/hous')
    app.register_blueprint(blueprint=order, url_prefix='/order')


    db.init_app(app)

    return app