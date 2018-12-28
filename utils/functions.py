import random
from functools import wraps

from flask import session, url_for
from werkzeug.utils import redirect

from utils.setting import DATABASE


def get_sqlalchemy_uri(DATABASE):
    user = DATABASE['USER']
    password = DATABASE['PASSWORD']
    host = DATABASE['HOST']
    port = DATABASE['PORT']
    name = DATABASE['NAME']
    engine = DATABASE['ENGINE']
    driver = DATABASE['DRIVER']
    return '%s+%s://%s:%s@%s:%s/%s' % (engine, driver,
                                       user, password,
                                       host, port, name)


def generateImageCode():
    str = '1234567890qwertyuiop'
    code = ''
    for _ in range(4):
        code += random.choice(str)
    return code


def is_login(func):

    @wraps(func)
    def check_login(*args, **kwargs):
        if 'user_id' in session:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('user.login'))

    return check_login
