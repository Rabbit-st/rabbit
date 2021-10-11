# -*- coding: UTF-8 -*-
from app.api import bp
from flask import request, current_app
from app.models.models import AdminUser, Permission, AdminRole, AdminPermission
from app.models import Hosts
from app import db
from app.api.errors import bad_request
from app.utils.rights import permission_required
from app.utils import api_result
from app.utils.schema import AdminRoleSchema, AdminPermissionSchema3
from app.api.auth import token_auth
from marshmallow import ValidationError

@bp.route('/roles', methods=['GET'])
@permission_required('api:role:main')
def get_roles():
    """
        获取所有角色
    """
    search = request.args.get('s',None)
    role_schema = AdminRoleSchema(many=True)
    if search:
        r = AdminRole.query.filter(AdminRole.name.like('%{0}%'.format(search))).layui_paginate()
    else:
        r = AdminRole.query.layui_paginate()
    count = r.total
    data = role_schema.dump(r.items)

    return api_result(code=0,data=data,count=count)


@bp.route('/role', methods=['POST'])
@permission_required('api:role:add')
def add_role():
    """
    添加角色
    """
    data = request.get_json() or {}
    if not data:
        return api_result(code=-1,msg='空数据')
    role_schema = AdminRoleSchema()
    try:
        data = role_schema.load(data)
    except ValidationError as err:
        return api_result(code=-1, msg=err.messages)

    if AdminRole.query.filter_by(name=data['name']).first():
        return api_result(code=-1, msg='角色名称已存在')
    #if data.get('users'):
    #   users = AdminUser.query.filter(AdminUser.id.in_(data['users'].split(',')))  # 用户和角色是多对多关系
    role = AdminRole()
    role.from_dict(data)
    #role.from_dict(data, isnew=True, users=users)
    db.session.add(role)
    db.session.commit()
    return api_result(data=data)

@bp.route('/role/state/<int:id>', methods=['PUT'])
@permission_required('api:role:state')
def edit_role_state(id):
    """
    修改权限状态
    """
    data = request.get_json() or {}
    if data.get('state', None) is None:
        return api_result(code=-1, msg='请选择状态值')
    r = AdminRole.query.get(id)
    r.state = data.get('state')
    db.session.add(r)
    db.session.commit()
    return api_result(msg='状态修改成功')

@bp.route('/role/<int:id>', methods=['GET'])
@permission_required('api:role:main')
def get_role(id):
    """
        获取指定角色信息
    """
    r = AdminRole.query.get(id)
    role_schema = AdminRoleSchema()
    data = role_schema.dump(r)
    return api_result(data=data)


@bp.route('/role/<int:id>', methods=['PUT'])
@permission_required('api:role:edit')
def update_role(id):
    """修改角色资料"""
    data = request.get_json() or {}
    role_schema = AdminRoleSchema()
    try:
        data = role_schema.load(data, partial=('name','type'))
    except ValidationError as err:
        return api_result(code=-1, msg=err.messages)

    role = AdminRole.query.get(id)
    if 'role' in data and data.get('role') != role.role \
            and AdminRole.query.filter_by(id=data['id']).first():
        return api_result(code=-1, msg='角色名已存在')

    #users = AdminUser.query.filter(AdminUser.id.in_(data['users'].split(',')))  # 用户和角色是多对多关系
    role.from_dict(data)
    db.session.commit()
    return api_result(data=data)

@bp.route('/role/<int:id>', methods=['DELETE'])
@permission_required('api:role:delete')
def delete_role(id):
    """
        删除角色
    """
    if id <= 4:
        return api_result(code=-1,msg='默认组不能删除!')
    role = AdminRole.query.get(id)
    # 删除角色关联的用户和权限
    role.users = []
    role.permission = []
    r = AdminRole.query.filter_by(id=id).delete()
    db.session.commit()
    if r:
        return api_result(msg='删除成功')
    else:
        return api_result(code=-1, msg='删除失败')

@bp.route('/roles/batch', methods=['DELETE'])
@permission_required('api:role:delete')
def batch_delete_roles():
    """批量删除角色"""
    data = request.get_json() or {}
    for id in data.get('ids',[]):
        if id <= 4:
            return api_result(code=-1,msg='默认角色不能删除')
        roles = AdminRole.query.get(id)
        # 删除角色关联的用户和权限
        roles.users = []
        roles.permission = []
        AdminRole.query.filter_by(id=id).delete()
        db.session.commit()

    return api_result(msg='删除成功')

@bp.route('/role/permissions/<int:id>', methods=['GET'])
@permission_required('api:role:permissions:main')
def get_role_permissions(id):
    """
        获取指定角色所有权限
    """
    role = AdminRole.query.get(id)
    permissions = []
    check_data = []
    data = {}
    per_schema = AdminPermissionSchema3(only=("id", "name","type"))

    # 所有权限
    p = AdminPermission.query.all()
    for i in p:
        tmp_data = per_schema.dump(i)
        if i.state == 0:
            tmp_data['disabled'] = True
        permissions.append(tmp_data)
        check_data.append(i.id)
    if id != 1:
        check_data = []
        for p in role.permission:
            # 被禁用的直接跳过
            if p.state == 0:
                continue
            check_data.append(p.id)
    data['permissions'] = permissions
    data['checked'] = check_data
    return api_result(data=data)

@bp.route('/role/permissions/<int:id>', methods=['PUT'])
@permission_required('api:role:permissions:edit')
def add_role_permissions(id):
    """
        指定角色添加权限
    """
    if id == 1:
        return api_result(code=-1, msg='超级管理员无法修改权限')
    data = request.get_json() or {}
    ids = data.get('ids')
    role = AdminRole.query.get(id)

    permissions = AdminPermission.query.filter(AdminPermission.id.in_(ids))
    role.permission = permissions

    db.session.commit()
    return api_result(msg='修改成功')

@bp.route('/roles/users', methods=['GET'])
@token_auth.login_required
@permission_required(Permission.READ)
def get_full_roles():
    """
        获取所有角色以及关联的用户
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('limit', current_app.config['POSTS_PER_PAGE'], type=int), 100)  # 最大值为100
    roles = AdminRole.query.paginate(page, per_page, False)
    data = []
    for role in roles.items:
        d = role.to_dict()
        d['users'] = []
        d['users_id'] = {}
        for u in role.users.all():
            d['users'].append(u.username)
            d['users_id'][u.id] = u.username
        data.append(d)
    count = roles.total
    return api_result(data=data, code=0, count=count)

@bp.route('/role/<int:id>/hosts', methods=['GET'])
@token_auth.login_required
@permission_required(Permission.READ)
def get_role_hosts(id):
    """
        获取指定角色所有主机权限
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('limit', current_app.config['POSTS_PER_PAGE'], type=int), 100)  # 最大值为100
    data = []
    role = AdminRole.query.get(id)
    hosts = role.permission.filter(AdminPermission.type== 0).outerjoin(
                    Hosts, Hosts.id == db.func.substring_index(AdminPermission.url, '/', -1)
                ).filter(Hosts.state == 1).with_entities(AdminPermission.id, AdminPermission.permission, Hosts.host_ip)
    for h in hosts:
        data.append({
            'id': h[0]
            ,'permission': Permission.code_to_str(h[1])
            ,'ip': h[2]
        })
    count = hosts.count()
    return api_result(data=data, count=count)


@bp.route('/role/<int:id>/users', methods=['POST'])
@token_auth.login_required
@permission_required(Permission.WRITE)
def ass_role_users(id):
    """
        指定角色关联用户
    """
    data = request.get_json() or {}
    role = AdminRole.query.get(id)
    users = AdminUser.query.filter(AdminUser.id.in_(data))
    role.add_user(users)
    db.session.commit()
    return api_result(data=role.to_dict())

@bp.route('/role/<int:id>/users', methods=['GET'])
@token_auth.login_required
@permission_required(Permission.READ)
def get_role_users(id):
    """
        获取指定角色所有的用户
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('limit', current_app.config['POSTS_PER_PAGE'], type=int), 100)  # 最大值为100
    u = AdminRole.query.get(id).users.paginate(
            page, per_page, False)
    count = u.total
    data = AdminUser.to_collection_dict(u)
    return api_result(data=data, count=count)

'''
@bp.route('/role/<int:id>/host/<int:urlid>', methods=['DELETE'])
@token_auth.login_required
@permission_required(Permission.DELETE)
def delete_role_host(id, urlid):
    """
    删除指定角色关联的主机。
    主机跟url权限控制是同一张表，对应的ID是一样的
    """
    role = AdminRole.query.get(id)
    h = AdminPermission.query.get(urlid)
    role.urls.remove(h)
    db.session.commit()
    return api_result(data=role.to_dict())
'''

'''
@bp.route('/role/<int:id>/url/<int:urlid>', methods=['DELETE'])
@token_auth.login_required
@permission_required(Permission.DELETE)
def delete_role_url(id, urlid):
    """
    删除指定角色的url权限
    """
    role = AdminRole.query.get(id)
    h = AdminPermission.query.get(urlid)
    role.urls.remove(h)
    db.session.commit()
    res = ResMsg()
    res.update(code=ResponseCode.Deleted, data=role.to_dict())
    return res.data
'''
    
@bp.route('/role/<int:id>/user/<int:userid>', methods=['DELETE'])
@token_auth.login_required
@permission_required(Permission.DELETE)
def delete_role_user(id, userid):
    """
    删除指定关联的用户
    """
    if int(id) == 1 and int(userid) == 1:
        return bad_request('默认系统用户不能删除')
    role = AdminRole.query.get(id)
    u = AdminUser.query.get(userid)
    role.users.remove(u)
    db.session.commit()
    return api_result(data=role.to_dict())

@bp.route('/permission/urls', methods=['GET'])
@token_auth.login_required
@permission_required(Permission.READ)
def get_permission_urls():
    """
        获取所有的url
    """
    page = request.args.get('page', 1, type=int)
    per_page = 1000
    data = AdminPermission.to_collection_dict(AdminPermission.query.filter(AdminPermission.type > 0).paginate(
            page, per_page, False))
    return api_result(data=data)

@bp.route('/permission/hosts', methods=['GET'])
@token_auth.login_required
@permission_required(Permission.READ)
def get_permission_hosts():
    """
        获取所有的主机权限列表
    """
    page = request.args.get('page', 1, type=int)
    per_page = 1000
    data = []
    hosts = AdminPermission.query.filter(AdminPermission.type == 0).outerjoin(
                    Hosts, Hosts.id == db.func.substring_index(AdminPermission.url, '/', -1)
                ).filter(Hosts.state == 1).with_entities(AdminPermission.id, AdminPermission.permission, Hosts.host_ip)
    for h in hosts:
        data.append({
            'id': h[0]
            ,'permission': Permission.code_to_str(h[1])
            ,'ip': h[2]
        })
    count = hosts.count()
    return api_result(data=data, count=count)
