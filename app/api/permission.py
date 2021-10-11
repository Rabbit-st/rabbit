#-*- coding=utf-8 -*-

from app.api.errors import bad_request
from app.models.models import AdminUser, AdminPermission,Permission,AdminRole
from flask import g, request,jsonify,session
from functools import wraps
from app.utils import api_result
from app.utils.rights import permission_required
from app.utils import curd,common
from app.utils.schema import AdminPermissionSchema4,AdminPermissionSchema3
from app.api import bp
from app import db
from marshmallow import ValidationError

@bp.route('/permissions', methods=['GET'])
@permission_required('api:permission:main')
def permissions():
    """
        获取所有的权限
    """
    permission = AdminPermission.query.all()
    data = curd.model_to_dicts(schema=AdminPermissionSchema3, data=permission)
    data.append({"id": 0, "name": "顶级权限", "parent_id": -1})

    return jsonify({
        'status': {'code': 200,"message": '默认'},
        'data': data
    })

@bp.route('/permissions', methods=['POST'])
@permission_required('api:permission:add')
def add_permissions():
    """
        添加权限
    """
    data = request.get_json() or {}
    per_schema = AdminPermissionSchema4()
    try:
        data = per_schema.load(data)
    except ValidationError as err:
        return api_result(code=-1, msg=err.messages)

    if AdminPermission.query.filter_by(name=data['name'], type=data['type'], parent_id=data['parent_id']).first():
        return api_result(code=-1, msg='权限名称已存在')
    p = AdminPermission()
    p.from_dict(data)
    db.session.add(p)
    db.session.commit()
    return api_result(msg='添加成功')

@bp.route('/permission/<int:id>', methods=['GET'])
@permission_required('api:permission:main')
def get_permission(id):
    """获取单个权限信息"""
    data = AdminPermission.query.get(id)
    per_schema = AdminPermissionSchema4()
    data = per_schema.dump(data)
    icon = str(data.get('icon')).split()
    if len(icon) == 2:
        data['icon'] = icon[1]
    else:
        data['icon'] = 'None'
    return api_result(data=data)

@bp.route('/permission/<int:id>', methods=['PUT'])
@permission_required('api:permission:edit')
def edit_permission(id):
    """更改权限信息"""
    data = request.get_json() or {}

    per_schema = AdminPermissionSchema4()
    try:
        if data.get('type') == 2:
            data = per_schema.load(data, partial=('type', 'parent_id',
                                                  'name','code'))
        elif data.get('type') == 0:
            data = per_schema.load(data, partial=('type','parent_id','name'))
        else:
            data = per_schema.load(data)
    except ValidationError as err:
        return api_result(code=-1, msg=err.messages)

    p = AdminPermission.query.get(id)

    if data.get('name') != p.name \
         and AdminPermission.query.filter_by(name=data.get('name'), type=data.get('type')).first():
        return bad_request('名称已存在')
    if data.get('type') in [1, 2] and data.get('code') != p.code \
        and AdminPermission.query.filter_by(code=data.get('code')).first():
        return bad_request('权限标识不能重复')

    p.from_dict(data)
    db.session.add(p)
    db.session.commit()
    return api_result(msg='修改成功',data=data)

@bp.route('/permission/<int:id>', methods=['DELETE'])
@permission_required('api:permission:delete')
def remove_permission(id):
    """删除权限信息"""
    permission = AdminPermission.query.get(id)
    permission.role = []
    r = AdminPermission.query.filter_by(id=id).delete()
    db.session.commit()
    if r:
        return api_result(msg='删除成功')
    else:
        return api_result(code=-1, msg='删除失败')

@bp.route('/permission/batch', methods=['DELETE'])
@permission_required('api:permission:remove:batch')
def batch_remove_permission():
    """批量删除权限信息"""
    data = request.get_json() or {}
    for id in data.get('ids',[]):
        pers = AdminPermission.query.filter_by(id=id).first()
        pers.role = []
        AdminPermission.query.filter_by(id=id).delete()
        db.session.commit()

    return api_result(msg='删除成功')

@bp.route('/permissions/refresh', methods=['GET'])
@permission_required('api:permission:refresh')
def refresh_permission():
    """刷新权限信息"""
    common.add_auth_session(refresh=True)
    p = session.get('permissions')
    return api_result(code=1, data=p,msg='刷新权限成功')

@bp.route('/permission/state/<int:id>', methods=['PUT'])
@permission_required('api:permission:state')
def edit_state(id):
    """
    修改权限状态
    """
    data = request.get_json() or {}
    if data.get('state', None) is None:
        return api_result(code=-1, msg='请选择状态值')
    p = AdminPermission.query.get(id)
    p.state = data.get('state')
    db.session.add(p)
    db.session.commit()
    return api_result(msg='状态修改成功')