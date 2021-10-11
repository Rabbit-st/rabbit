from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app.models.models import AdminUser
from app.api.errors import error_response
from flask import make_response, jsonify, redirect, url_for

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

# token 添加
@basic_auth.verify_password
def verify_password(username, password):
    user = AdminUser.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user

@basic_auth.error_handler
def basic_auth_error(status):
    return error_response(status)

@basic_auth.error_handler
def unauthorized():
    """401密码验证失败会出现一个弹窗，太丑了，这里改成用403"""
    return make_response(jsonify({'error': 'Unauthorized access'}),403)

# token访问限制
@token_auth.verify_token
def verify_token(token):
    return AdminUser.verify_auth_token(token) if token else None

@token_auth.error_handler
def token_auth_error(status):
    return error_response(status)
