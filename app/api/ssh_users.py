#-*- coding:utf-8 -*-

from app.api import bp
from flask import jsonify, request, url_for, current_app
from app.models import SshUsers
from app import db
from app.utils.rights import permission_required
from app.utils import (validate_ssh_private_key, api_result)
from app.utils.schema import SshUsersSchema
from marshmallow import ValidationError

@bp.route('/ssh_users', methods=['GET'])
@permission_required('api:ssh_users:main')
def get_ssh_users():
    """
    获取ssh账号，返回状态为1的用户
    """
    all = request.args.get('all', 0, type=int)
    u_schema = SshUsersSchema(many=True)
    if not all:
        u = SshUsers.query.layui_paginate()
        count = u.total
        data = u_schema.dump(u.items)
        return api_result(code=0, data=data, count=count)
    u = SshUsers.query.all()
    data = u_schema.dump(u)
    return api_result(code=0, data=data)

@bp.route('/ssh_users/<int:id>', methods=['GET'])
@permission_required('api:ssh_users:main')
def get_ssh_user(id):
    '''获取单个项目信息'''
    u = SshUsers.query.get(id)
    u_schema = SshUsersSchema()
    data = u_schema.dump(u)
    return api_result(code=1,data=data)

@bp.route('/ssh_users/search', methods=['GET'])
@permission_required('api:hosts:main')
def ssh_users_search():
    """
    查询字符串为空的时候，返回所有数据。
    """
    q = request.args.get('name', None)
    if q:
        data = SshUsers.query.filter(SshUsers.name.like('{0}%'.format(q))).layui_paginate()
    else:
        data = SshUsers.query.layui_paginate()
    count = data.total
    u_schema = SshUsersSchema(many=True)
    data = u_schema.dump(data.items)

    return api_result(code=0, data=data, count=count)

@bp.route('/ssh_users', methods=['POST'])
@permission_required('api:ssh_users:add')
def add_ssh_user():
    """
    添加ssh账号
    """
    data = request.form.to_dict()
    u_schema = SshUsersSchema()
    try:
        data = u_schema.load(data)
    except ValidationError as err:
        return api_result(code=-1, msg=err.messages)

    if int(data.get('pass_type')) not in [1, 2]:
        return api_result(code=-1, msg='密码类型错误')
    if SshUsers.query.filter_by(name=data.get('name')).first():
        return api_result(code=-1, msg='名称已存在!')
    if int(data.get('pass_type')) == 2:
        if 'file' in request.files:
            file = request.files['file']
            if file:
                private_key = file.read()
                valid = validate_ssh_private_key(private_key, None)
                if not valid:
                    return api_result(code=-1, msg="密钥不合法")
                data['private_key'] = private_key
            else:
                return api_result(code=-1, msg="密钥为空")
        else:
            return api_result(code=-1, msg="密钥为空")
    elif not data.get('ssh_password'):
        return api_result(code=-1, msg="密码不能为空")

    user = SshUsers()
    user.from_dict(data)
    db.session.add(user)
    db.session.commit()
    return api_result(code=1, data=data, msg='添加成功')

@bp.route('/ssh_users/<int:id>', methods=['PUT'])
@permission_required('api:ssh_users:edit')
def edit_ssh_user(id):
    """
    修改ssh账户
    """
    data = request.form.to_dict()
    if not data:
        return api_result(code=-1, msg='没有数据')
    try:
        u_schema = SshUsersSchema()
        data = u_schema.load(data)
    except ValidationError as err:
        return api_result(code=-1, msg=err.messages)

    user = SshUsers.query.get(id)
    if user.name != data.get('name') and SshUsers.querys.filter_by(name=data.get('name')).first():
        return api_result(code=-1, msg='名称已存在')
    # 密钥文件处理
    if 'file' in request.files:
        file = request.files['file']
        if file:
            private_key = file.read()
            valid = validate_ssh_private_key(private_key, data.get('ssh_password'))
            if not valid:
                return api_result(code=-1, msg="密钥不合法")
            data['private_key'] = private_key

    user.from_dict(data)
    db.session.add(user)
    db.session.commit()
    return api_result(code=1, msg='修改成功')

@bp.route('/ssh_users/state/<int:id>', methods=['PUT'])
@permission_required('api:ssh_users:disable')
def disable_ssh_user(id):
    """禁用/启用ssh用户"""
    data = request.get_json() or {}
    u = SshUsers.query.get(id)
    u.state = data.get('state')
    db.session.commit()
    return api_result(msg='状态修改成功')

@bp.route('/ssh_users/<int:id>', methods=['DELETE'])
@permission_required('api:ssh_users:delete')
def delete_ssh_user(id):
    """
        删除ssh用户
    """
    u = SshUsers.query.filter_by(id=id).delete()
    db.session.commit()
    if u:
        return api_result(msg='ssh用户删除成功')
    return api_result(code=-1, msg='ssh用户删除失败')