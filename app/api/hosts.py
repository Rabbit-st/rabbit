# -*- coding: UTF-8 -*-

from datetime import datetime
from app.api import bp
from flask import request, current_app, g, jsonify
from app.models.models import AdminUser,\
        Permission, AdminPermission
from app.models import Hosts, Projects
from app import db
from app.utils import allowed_file, \
        random_filename, csv_to_list, api_result
from app.utils.schema import HostsSchema
from app.utils.rights import permission_required
from marshmallow import ValidationError
import os

@bp.route('/hosts', methods=['GET'])
@permission_required('api:hosts:main')
def get_hosts():
    """获取所有的Hosts"""
    state = request.args.get('state', 1, type=int)
    tree = request.args.get('tree', 0, type=int)
    data = db.session.query(Hosts, Projects.name).outerjoin(
        Projects, Hosts.project_id==Projects.id
    ).filter(Hosts.state==state).layui_paginate()
    count = data.total
    data = Hosts.to_collection_dict(data)
    if tree:
        d = {}
        for h in data:
            pid = '000{0}'.format(h.get('project_id'))
            d.setdefault(h.get('project_name'), {}).setdefault('data', []).append({
                'id': str(h.get('id'))
                ,'title': '{0}({1})'.format(h.get('host_ip'),h.get('host_name'))
                ,'last': True
                ,'parentId': pid
            })
            d[h.get('project_name')].setdefault('id', pid)
        data = []
        for p in d:
            data.append({
                'id': d[p]['id']
                ,'title': p
                ,'last': False
                ,'parentId': 1231321
                ,'children': d[p]['data']
            })
        return jsonify({
            'status': {'code': 200, 'message':'操作成功'}
            ,'data': data
        })
    return api_result(code=0, data=data, count=count)

'''
@bp.route('/states/<int:id>/hosts', methods=['GET'])
@token_auth.login_required
#@permission_required(Permission.READ)
def get_states_hosts(id):
    """
        获取指定状态的所有Hosts
        role.level <= 2
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('limit', current_app.config['POSTS_PER_PAGE'], type=int), 100)

    host = db.session.query(Hosts, Projects).outerjoin(
                Projects, Hosts.project_id==Projects.id).filter(Hosts.state==id)
    data = Hosts.to_collection_dict(host.paginate(page, per_page, False))
    count = host.count()
    return api_result(code=0, data=data, count=count)
    res = ResMsg()
    res.update(data=data)
    res.add_field(name='count', value=count)
    return res.data
'''

'''
@bp.route('/limitation/states/<int:id>/hosts', methods=['GET'])
@token_auth.login_required
#@permission_required(Permission.READ)
def get_limit_states_hosts(id):
    """
        获取指定状态的所有hosts，受限的
        role.level > 2
    """
    #TODO: 管理员或者超级管理员由于auth_url没有授权，请求这个接口会返回空值。
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('limit', current_app.config['POSTS_PER_PAGE'], type=int), 100)
    hosts_id = []
    u = AdminUser.query.get(g.uid)
    res = ResMsg()
    try:
        for r in u.roles.all():
            for h in r.urls.filter(AdminPermission.url.like('/api/hosts/%'))\
                .with_entities(db.func.substring_index(AdminPermission.url, '/', '-1').label('hid'), 
                    AdminPermission.permission):
                if h.permission & Permission.READ == Permission.READ:
                    hosts_id.append(h.hid)
    except AttributeError as e:
        res.update(code=ResponseCode.NoResourceFound, msg="没有数据")
        return res.data
    host = db.session.query(Hosts, Projects).outerjoin(
                Projects, Hosts.project_id==Projects.id).filter(Hosts.state==id, Hosts.id.in_(hosts_id))
    data = Hosts.to_collection_dict(host.paginate(page, per_page, False))
    count = host.count()
    res.update(data=data)
    res.add_field(name='count', value=count)
    return res.data
'''

@bp.route('/hosts/<int:id>', methods=['GET'])
@permission_required('api:hosts:main')
def get_host(id):
    """获取单个主机信息"""
    host = Hosts.query.get(id)
    hosts_schema = HostsSchema()
    data = hosts_schema.dump(host)
    return api_result(code=1, data=data)

@bp.route('/hosts', methods=['POST'])
@permission_required('api:hosts:add')
def create_hosts():
    """添加新主机"""
    data = request.get_json() or {}
    if not data:
        return api_result(code=-1, msg='未接收到任何数据')
    hosts_schema = HostsSchema()
    try:
        hosts_schema.load(data)
    except ValidationError as err:
        return api_result(code=-1, msg=err.messages)

    if Hosts.query.filter_by(host_ip=data['host_ip']).first():
        return api_result(code=-1, msg='IP已存在')
    if Hosts.query.filter_by(host_name=data['host_name']).first():
        return api_result(code=-1, msg='主机名已存在')

    host = Hosts()
    host.from_dict(data)
    db.session.add(host)
    db.session.commit()
    return api_result(code=1, msg='添加成功')

@bp.route('/hosts/<int:id>', methods=['PUT'])
@permission_required('api:hosts:edit')
def put_hosts(id):
    """更改指定主机信息"""
    data = request.get_json() or {}
    hosts_schema = HostsSchema()
    try:
        data = hosts_schema.load(data)
    except ValidationError as err:
        return api_result(code=-1, msg=err.messages)

    host = Hosts.query.get(id)
    if 'host_ip' in data and data.get('host_ip') != host.host_ip \
         and Hosts.query.filter_by(host_ip=data['host_ip']).first():
        return api_result(code=-1, msg='IP已存在')
    # 防止前端传过来的数据格式不对，导致数据库更新多余的字段。
    data['ssh_port'] = int(data['ssh_port'])
    data['project_id'] = int(data['project_id'])

    host.from_dict(data)
    db.session.add(host)
    db.session.commit()
    return api_result(code=1, data=data)

@bp.route('/hosts/<int:id>', methods=['POST'])
@permission_required('api:hosts:dis')
def disable_hosts(id):
    """禁用主机"""
    host = Hosts.query.get(id)
    host.state = 0
    host.delete_time = datetime.now()
    db.session.commit()
    return api_result(code=1, msg='删除成功')

@bp.route('/hosts/batch', methods=['POST'])
@permission_required('api:hosts:dis')
def batch_disable_hosts():
    """批量禁用主机"""

    data = request.get_json() or {}
    ids = data.get('ids',[])
    Hosts.query.filter(Hosts.id.in_(ids)).update(dict(state=0, delete_time=datetime.now()), synchronize_session='fetch')
    db.session.commit()

    return api_result(msg='删除成功')

@bp.route('/hosts/remove', methods=['delete'])
@permission_required('api:hosts:remove')
def remove_hosts():
    """批量删除主机"""

    data = request.get_json() or {}
    ids = data.get('ids',[])
    Hosts.query.filter(Hosts.id.in_(ids)).delete(synchronize_session=False)
    db.session.commit()

    return api_result(msg='删除成功')

@bp.route('/hosts/recycle', methods=['post'])
@permission_required('api:hosts:recycle')
def recycle_hosts():
    """批量恢复主机"""

    data = request.get_json() or {}
    ids = data.get('ids',[])
    Hosts.query.filter(Hosts.id.in_(ids)).update(dict(state=1), synchronize_session='fetch')
    db.session.commit()

    return api_result(msg='恢复成功')

@bp.route('/hosts/search', methods=['GET'])
@permission_required('api:hosts:main')
def search():
    """
    查询字符串为空的时候，返回所有数据。
    """
    q = request.args.get('host_ip', None)
    project_id = request.args.get('project_id', None)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('limit', current_app.config['POSTS_PER_PAGE'], type=int), 100)  # 最多只能搜索100页的内容
    if not q and not project_id:
        host = db.session.query(Hosts, Projects.name).outerjoin(
                Projects, Hosts.project_id==Projects.id).filter(Hosts.state==1).paginate(page, per_page, False)
        data = Hosts.to_collection_dict(host)
    elif not q and project_id:
        project_ids = project_id.split(',')
        host = db.session.query(Hosts, Projects.name).outerjoin(
            Projects, Hosts.project_id==Projects.id).filter(Hosts.project_id.in_(project_ids), Hosts.state==1).paginate(page, per_page, False)
        data = Hosts.to_collection_dict(host)
    else:
        project_ids = project_id.split(',')
        host = db.session.query(Hosts, Projects.name).outerjoin(
            Projects, Hosts.project_id==Projects.id).filter(Hosts.project_id.in_(project_ids),
                                                                  Hosts.state==1,
                                                                  Hosts.host_ip.like('%{0}%'.format(q))).paginate(
            page, per_page, False)
        data = Hosts.to_collection_dict(host)
        #host, count = Hosts.search(q, page, per_page, project_ids)
    count = host.total
    return api_result(code=0, data=data, count=count)

@bp.route('/hosts/upload', methods=['POST'])
@permission_required('api:hosts:upload')
def upload():
    """
    上传文件接口
    """
    if 'file' not in request.files:
        return api_result(code=-1, msg='请选择文件')
    file = request.files['file']
    if file.filename == '':
        return api_result(code=-1, msg='没有选择文件')
    if file and allowed_file(file.filename):
        filename = random_filename()
        file_path = current_app.config['UPLOAD_FOLDER']
        file.save(os.path.join(file_path, filename))
        hosts = Hosts.query.with_entities(Hosts.host_ip,Hosts.host_name)
        state, data = csv_to_list(file_path, filename, hosts)
        if not state:
            return api_result(code=-1, msg=data)
        db.session.bulk_insert_mappings(Hosts, data['success'])
        db.session.commit()
        #Hosts.reindex()
        if data['existing']:
            return api_result(code=1, msg='添加成功，部分主机已存在')
        return api_result(code=1, msg='添加成功')
    return api_result(code=-1, msg='添加失败')
