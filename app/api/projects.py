#-*- coding: UTF-8 -*-
from app.api import bp
from flask import request, current_app
from app.models import Projects
from app import db
from app.utils.rights import permission_required
from app.utils import api_result
from app.utils.schema import ProjectsSchema
from marshmallow import ValidationError

@bp.route('/projects', methods=['GET'])
@permission_required('api:projects:main')
def get_projects():
    """获取所有project"""
    all = request.args.get('all', 0, type=int)
    p_schema = ProjectsSchema(many=True)
    if not all:
        data = Projects.query.layui_paginate()
        count = data.total
        data = p_schema.dump(data.items)
        return api_result(code=0, data=data, count=count)
    data = Projects.query.all()
    data = p_schema.dump(data)
    return api_result(code=0, data=data)

@bp.route('/projects/<int:id>', methods=['GET'])
@permission_required('api:projects:main')
def get_project(id):
    '''获取单个项目信息'''
    p = Projects.query.get(id)
    p_schema = ProjectsSchema()
    data = p_schema.dump(p)
    return api_result(code=1,data=data)

@bp.route('/projects', methods=['POST'])
@permission_required('api:projects:add')
def create_project():
    """添加新项目"""
    data = request.get_json() or {}
    if not data:
        return api_result(code=-1, msg='未接收到任何数据')
    p_schema = ProjectsSchema()
    try:
        data=p_schema.load(data)
    except ValidationError as err:
        return api_result(code=-1, msg=err.messages)

    if Projects.query.filter_by(name=data['name'].strip(' ')).first():
        return api_result(code=-1, msg='项目已存在')

    project = Projects()
    project.from_dict(data)
    db.session.add(project)
    db.session.commit()
    return api_result(msg='添加成功')

@bp.route('/projects/<int:id>', methods=['PUT'])
@permission_required('api:projects:edit')
def put_project(id):
    """更改指定项目信息"""
    data = request.get_json() or {}
    if not data:
        return api_result(code=-1, msg='未接收到任何数据')
    p_schema = ProjectsSchema()
    try:
        data = p_schema.load(data)
    except ValidationError as err:
        return api_result(code=-1, msg=err.messages)

    project = Projects.query.get(id)
    if project.name != data.get('name').strip(' ') and Projects.query.filter_by(name=data.get('name')).first():
        return api_result(code=-1, msg='项目已存在')
    # 防止前端传过来的数据格式不对，导致数据库更新多余的字段。

    project.from_dict(data)
    #db.session.add(project)
    db.session.commit()
    return api_result(msg='修改成功')

@bp.route('/projects/state/<int:id>', methods=['PUT'])
@permission_required('api:projects:dis')
def disable_project(id):
    """修改项目状态"""
    data = request.get_json() or {}
    if data.get('state', None) is None:
        return api_result(code=-1, msg='状态不正确')
    p = Projects.query.get(id)
    p.state = data.get('state')
    db.session.commit()
    return api_result(msg='状态修改成功')

@bp.route('/projects/<int:id>', methods=['DELETE'])
@permission_required('api:projects:remove')
def remove_project(id):
    """删除项目"""
    p = Projects.query.filter_by(id=id).delete()
    db.session.commit()
    if p:
        return api_result(code=1, msg='删除成功')
    return api_result(code=-1, msg='删除失败')


'''
@bp.route('/projects/<int:id>/hosts', methods=['GET'])
@permission_required('api:projects:main')
def get_projects_hosts(id):
    """获取指定项目的hosts"""
    #res_data = request.get_json() or {}
    #page = res_data['page'] \
    #    if 'page' in res_data else 1
    #per_page = res_data['limit'] \
    #    if 'limit' in res_data else 100
    res = ResMsg()
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('limit', current_app.config['POSTS_PER_PAGE'], type=int), 100)
    host = db.session.query(Hosts, Projects).outerjoin(
            Projects, Hosts.project_id==Projects.id).filter_by(projectid=id)
    data = Hosts.to_collection_dict(host.paginate(page, per_page, False))
    count = host.count()
    res.update(data=data)
    res.add_field(name='count', value=count)
    return res.data
'''
'''
@bp.route('/projects/<int:id>/server', methods=['GET'])
@permission_required(Permission.READ)
def get_projects_states(id):
    """
    获取指定状态指定项目的所有主机
    例：
        /api/projects/1/server?state=1
    """
    state = request.args.get('state', 1, type=int)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('limit', current_app.config['POSTS_PER_PAGE'], type=int), 100)
    host = db.session.query(Hosts, Projects).outerjoin(
                Projects, Hosts.project_id==Projects.id).filter(Hosts.project_id==id, Hosts.state==state)
    data = Hosts.to_collection_dict(host.paginate(page, per_page, False))
    count = host.count()
    res = ResMsg()
    res.update(data=data)
    res.add_field(name='count', value=count)
    return res.data
'''