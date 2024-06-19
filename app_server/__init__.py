import logging
from http import HTTPStatus

from flask import Flask, request
from flask_migrate import Migrate
from flask_cors import CORS

from app_server.db import db
from config import Config

from app_server.routes.assistant import assistant_bp

app = Flask(__name__)
CORS(app, supports_credentials=True)
# 数据库的变量
app.config['SQLALCHEMY_DATABASE_URI'] = Config.MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True  # 设置sqlalchemy自动更新跟踪数据库

# 日志
app.logger.setLevel(logging.INFO)  # 或者 logging.DEBUG 用于获取更详细的日志


@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data().decode('utf-8'))


@app.after_request
def log_response_info(response):
    app.logger.debug('Status Code: %s', response.status_code)
    app.logger.debug('Response: %s', response.get_data().decode('utf-8'))
    return response


# # JWT部分
# app.config['JWT_SECRET_KEY'] = Config.JWT_KEY
# # 配置JWT过期时间
# app.config['JWT_ACCESS_TOKEN_EXPIRES'] = Config.JWT_EXPIRE
#
# # 注册JWT
# jwt = JWTManager(app)

# 注册路由
app.register_blueprint(assistant_bp)

# 连接数据库
with app.app_context():
    # 初始化数据库
    db.init_app(app)
    # db.drop_all() #删除所有的表
    # db.create_all()  # 创建所有的表

migrate = Migrate(app, db)


@app.route('/')
def index():
    return {
        "code": HTTPStatus.OK,
        "msg": "success",
        "datas": {
        }
    }
