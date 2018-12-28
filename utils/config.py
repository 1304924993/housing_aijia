import os

from utils.functions import get_sqlalchemy_uri
from utils.setting import DATABASE


class Conf():
    SQLALCHEMY_DATABASE_URI = get_sqlalchemy_uri(DATABASE)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SECRET_KEY = '1221'


