from logging.handlers import RotatingFileHandler
import logging
import os
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from config import Config  
from flask_redis import FlaskRedis
from elasticsearch import Elasticsearch
from flask_marshmallow import Marshmallow
from app.utils.custom_query import Query
from celery import Celery
#from app.view import init_view
#from flask_socketio import SocketIO

db = SQLAlchemy(query_class=Query) # query_class默认使用的是BaseQuery，这里为了方便layui使用，加了个分页的方法
migrate = Migrate()   # 数据库插件
#login = LoginManager()  # 登录插件
#login.login_view = 'auth.login'   # 定义哪个页面是登录页面，当用户未登录时，访问需要登录的页面，会强制跳转到此页面。
mail = Mail()  # 邮件
ma = Marshmallow() # 数据转换器的对象创建
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)  # celery

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class) # 载入配置文件
    
    db.init_app(app)
    migrate.init_app(app, db)

    # 数据转换器的初始化
    ma.init_app(app)

    # 注册路由
    #init_view(app)

    from app.errors import bp as errors_bp # 注册errors blueprint
    app.register_blueprint(errors_bp)

    # api
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # websocket
    #from app.ws import bp as ws_bp
    #app.register_blueprint(ws_bp, url_prefix='/ws')

    # redis
    app.redis = FlaskRedis(app)
    
    # celery
    celery.conf.update(app.config)

    # socketio
    #socketio.init_app(app=app)

    if not app.debug and not app.testing:
        # 没有开启debu模式，日志写入到日志文件
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/opsdev.log', maxBytes=102400,
                                        backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')

    return app

from app.models import models, ansibles
