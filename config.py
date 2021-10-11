import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class MysqlConfig(object):
    DB_HOST = os.environ.get('DB_HOST') or '127.0.0.1'
    DB_PORT = os.environ.get('DB_PORT') or 3306
    DB_USER = os.environ.get('DB_USER') or 'us_flask'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or '111222333'
    DB_DATABASE = os.environ.get('DB_DATABASE') or 'rabbit'
    DB_CHARSET = os.environ.get('DB_CHARSET') or 'utf8'

class Config(object):
    SYSTEM_NAME = os.environ.get('SYSTEM_NAME') or 'rabbit'
    JSON_AS_ASCII = False  # 显示中文
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'das123GFDa21314cxgrsaDA'
    AUTH_SALT = os.environ.get('AUTH_SALT') or '123GF3241GHd21'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://{}:{}@{}:{}/{}?charset={}'.format(
                MysqlConfig.DB_USER, MysqlConfig.DB_PASSWORD, MysqlConfig.DB_HOST, 
                MysqlConfig.DB_PORT, MysqlConfig.DB_DATABASE, MysqlConfig.DB_CHARSET)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 10  # 每页显示多少项
    TOKEN_EXPIRE = 28800 # token过期时间
    # 支持的语言
    LANGUAGES = ['zh','en']
    # redis
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://127.0.0.1:6379/0'
    REDIS_EXPIRE = 300
    # celery redis
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://127.0.0.1:6379/1'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://127.0.0.1:6379/1'  # 存储任务状态和任务执行结果
    # 上传文件路径
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or '/tmp'
    # 脚本生成临时目录
    SCRIPT_FOLDER = os.environ.get('SCRIPT_FOLDER') or '/tmp'
    # tornado
    TORNADO_PORT= 8000
