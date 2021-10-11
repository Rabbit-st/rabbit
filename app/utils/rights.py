#-*- coding=utf-8 -*-

from app.api.errors import bad_request
from app.models.models import AdminUser, Permission
from flask import g, request
from functools import wraps
from app.utils import ResMsg, ResponseCode
from flask import session,jsonify
from app.api.auth import token_auth

def permission_required(permission):
    def decorator(func):
        @token_auth.login_required
        @wraps(func)
        def decorated_function(*args, **kwargs):
            res = ResMsg()
            if permission not in session.get('permissions'):
                res.update(code=ResponseCode.Forbidden, msg="权限不足")
                return res.data
            return func(*args, **kwargs)
        return decorated_function
    return decorator
