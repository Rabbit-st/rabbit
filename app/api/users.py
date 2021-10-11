# -*- coding: UTF-8 -*-
import re
from app.api import bp
from flask import request, current_app
from app.models.models import AdminUser, Permission, AdminRole
from app import db
from app.api.errors import bad_request
#from app.api.permission import permission_required
from app.utils.rights import permission_required
from app.utils import ResMsg, ResponseCode, check_password,api_result
from app.api.auth import token_auth
from app.utils.schema import AdminUserSchema,AdminRoleSchema,AdminUserSchema2
from marshmallow import ValidationError

@bp.route('/users', methods=['GET'])
@permission_required('api:user:main')
def get_users():
    """
    获取所有账号
    """
    #page = request.args.get('page', 1, type=int)
    #per_page = min(request.args.get('limit', current_app.config['POSTS_PER_PAGE'], type=int), 100)  # 最大值为100
    data = AdminUser.query.layui_paginate()
    count = data.total
    user_schema = AdminUserSchema(many=True)
    data = user_schema.dump(data.items)
    return api_result(code=0, data=data, count=count)

@bp.route('/user', methods=['POST'])
@token_auth.login_required
@permission_required('api:user:add')
def create_user():
    """
        创建用户
    """
    request_data = request.get_json() or {}
    user_schema = AdminUserSchema()
    try:
        data = user_schema.load(request_data)
    except ValidationError as err:
        return api_result(code=-1, msg=err.messages)

    if AdminUser.query.filter_by(username=data['username']).first():
        return api_result(code=-1, msg='用户名已存在，请使用其他用户名')
    if AdminUser.query.filter_by(email=data['email']).first():
        return api_result(code=-1, msg='邮箱已存在，请使用其他邮箱')

    if request_data.get('role', None) is not None:
        data['role'] = AdminRole.query.filter(AdminRole.id.in_(request_data['role'].split(',')))
    user = AdminUser()
    user.from_dict(data)
    db.session.add(user)
    db.session.commit()
    return api_result(code=1, msg='用户添加成功')

@bp.route('/user/<int:id>', methods=['GET'])
@permission_required('api:user:main')
def get_user(id):
    """
        获取账号信息
    """
    user = AdminUser.query.get(id)
    role_list = []
    user_schema = AdminUserSchema()
    data = user_schema.dump(user)

    # 获取用户的role id列表
    if id == 1:
        # 超级管理员默认就是超级管理员组，不用再查库
        role_list.append(1)
    else:
        roles = user.role
        for role in roles:
            role_list.append(role.id)
    data['role'] = role_list
    return api_result(code=1, data=data)

@bp.route('/user/<int:id>', methods=['PUT'])
@permission_required('api:user:edit')
def edit_user(id):
    """修改用户资料"""
    request_data = request.get_json() or {}
    if not request_data:
        # 防骚扰
        return api_result(code=-1, msg='空数据')
    user = AdminUser.query.get(id)
    user_schema = AdminUserSchema2()
    try:
        if request_data.get('password', None) is None:
            request_data.pop('password')
            request_data.pop('password2')
            data = user_schema.load(request_data, partial=('username','nickname','email'))
        else:
            data = user_schema.load(request_data)
    except ValidationError as err:
        return api_result(code=-1, msg=err.messages)

    if 'username' in data and data['username'] != user.username and \
            AdminUser.query.filter_by(username=data['username']).first():
        return api_result(code=-1,msg='账号已存在')
    if 'email' in data and data['email'] != user.email and \
            AdminUser.query.filter_by(email=data['email']).first():
        return api_result(code=-1,msg='邮箱已存在')

    if id == 1 and '1' not in data.get('role').split(','):
        return api_result(code=-1, msg='超级管理员用户组不能做更改')

    if request_data.get('role', None) is not None:
        data['role'] = AdminRole.query.filter(AdminRole.id.in_(request_data['role'].split(',')))
    user.from_dict(data)
    db.session.commit()
    return api_result(code=1, msg='修改成功')

@bp.route('/user/<int:id>', methods=['DELETE'])
@permission_required('api:user:delete')
def delete_user(id):
    """
        删除用户
    """
    if id == 1:
        return api_result(code=-1,msg='默认用户不能删除!')
    user = AdminUser.query.get(id)
    # 删除角色关联的用户和权限
    user.role = []
    u = AdminUser.query.filter_by(id=id).delete()
    db.session.commit()
    if u:
        return api_result(msg='用户删除成功')
    else:
        return api_result(code=-1, msg='用户删除失败')

@bp.route('/users/batch', methods=['DELETE'])
@permission_required('api:user:delete')
def batch_delete_users():
    """批量删除用户"""
    data = request.get_json() or {}
    for id in data.get('ids',[]):
        if id == 1:
            return api_result(code=-1,msg='默认用户不能删除')
        user = AdminUser.query.get(id)
        # 删除角色关联的用户和权限
        user.role = []
        AdminUser.query.filter_by(id=id).delete()
        db.session.commit()

    return api_result(msg='删除成功')

@bp.route('/user/state/<int:id>', methods=['PUT'])
@permission_required('api:user:state')
def edit_user_state(id):
    """禁用/启用用户"""
    data = request.get_json() or {}
    if data.get('state', None) is None:
        return api_result(code=-1, msg='请选择状态值')
    u = AdminUser.query.get(id)
    u.state = data.get('state')
    db.session.commit()
    return api_result(msg='状态修改成功')
