# -*- coding: UTF-8 -*-

from datetime import datetime
import json
from app.api import bp
from flask import request, current_app, g
from app.models.models import AdminUser, \
        Permission
from app.models.ansibles import Scripts, ScriptsVersion, \
    TaskQueue
from app import db, celery
from app.api.errors import bad_request
#from app.api.permission import permission_required
from app.utils.rights import permission_required
from app.api.tasks_celery import exec_ansible_playbook, ansible_exec_script
from app.utils import ResMsg, ResponseCode
from app.api.auth import token_auth

@bp.route('/tasks/ansible/playbook', methods=['POST'])
@token_auth.login_required
@permission_required(Permission.READ)
def exec_playbook():
    """
        执行ansible playbook，返回任务id
    """
    res = ResMsg()
    data = request.get_json() or {}
    tq = TaskQueue(job_id=data.get('job'), add_user=g.uid, start_time=datetime.utcnow(), status="PENDING")
    db.session.add(tq)
    db.session.commit()
    task = ansible_exec_script.delay(data.get('job'), g.uid, data.get('hosts'), data.get('ssh_id'), data.get('vid'))
    res.update(code=ResponseCode.Created, msg="任务创建成功")
    return res.data

@bp.route('/tasks/status/<string:task_id>', methods=['GET'])
@token_auth.login_required
@permission_required(Permission.READ)
def get_tasks_status(task_id):
    """
        根据task_id获取任务执行状态
    """
    task = exec_ansible_playbook.AsyncResult(task_id)
    if task.state == 'PENDING':
        # 还没开始
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    res = ResMsg()
    res.update(data=response)
    return res.data

@bp.route('/tasks/ansible/playbook/<int:id>/state', methods=['GET'])
@token_auth.login_required
@permission_required(Permission.READ)
def get_playbook_state(id):
    pass

@bp.route('/tasks/scripts', methods=['GET'])
@token_auth.login_required
@permission_required(Permission.READ)
def get_scripts():
    """
        获取所有脚本信息
    """
    res = ResMsg()
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('limit', current_app.config['POSTS_PER_PAGE'], type=int), 100)  # 最大值为100
    scripts = Scripts.query.outerjoin(AdminUser, Scripts.last_user == AdminUser.id).with_entities(
                Scripts.id, Scripts.name, Scripts.classifying, Scripts.description, 
                Scripts.version,Scripts.update_time, Scripts.lang, AdminUser.username)
    data = []
    for s in scripts.paginate(page, per_page, False).items:
        data.append({
            'id': s.id
            ,'name': s.name
            ,'classifying': s.classifying
            ,'description': s.description
            ,'version': s.version
            ,'update_time': s.update_time.strftime('%Y-%m-%d %H:%M:%S')
            ,'username': s.username
            ,'lang': s.lang
        })
    count = scripts.count()
    res = ResMsg()
    res.update(data=data)
    res.add_field(name='count', value=count)
    return res.data

@bp.route('/tasks/script/<int:script_id>', methods=['GET'])
@token_auth.login_required
@permission_required(Permission.READ)
def get_script(script_id):
    """
        获取单个脚本信息
    """
    res = ResMsg()
    script = Scripts.query.filter_by(id=script_id).outerjoin(AdminUser, Scripts.last_user == AdminUser.id).with_entities(
                Scripts.id, Scripts.name, Scripts.classifying, Scripts.description,
                    Scripts.version, Scripts.update_time, Scripts.create_time, Scripts.lang, AdminUser.username).first()
    if not script:
        res.update(msg='没有数据')
        return res.data
    data = {
        'id': script.id
        ,'name': script.name
        ,'classifying': script.classifying
        ,'description': script.description
        ,'version': script.version
        ,'update_time': script.update_time.strftime('%Y-%m-%d %H:%M:%S')
        ,'create_time': script.create_time.strftime('%Y-%m-%d %H:%M:%S')
        ,'lang': script.lang
        ,'username': script.username
    }
    res.update(data=data)
    return res.data

@bp.route('/tasks/script/<int:script_id>', methods=['DELETE'])
@token_auth.login_required
@permission_required(Permission.DELETE)
def delete_script(script_id):
    """
        删除指定脚本
    """
    res = ResMsg()
    script = Scripts.query.get(script_id)
    db.session.delete(script)
    sv = ScriptsVersion.query.filter_by(script_id=script_id).delete()
    db.session.commit()
    res.update(code=ResponseCode.Deleted,data=script.to_dict())
    return res.data

@bp.route('/tasks/script/<int:script_id>/version/<int:vid>', methods=['DELETE'])
@token_auth.login_required
@permission_required(Permission.DELETE)
def delete_script_version(script_id, vid):
    """
        删除脚本的指定版本。
        安全起见，删除版本也要验证脚本id
    """
    res = ResMsg()
    sv = ScriptsVersion.query.filter_by(id=vid, script_id=script_id).first()
    if not sv:
        return bad_request('版本不存在')
    db.session.delete(sv)
    db.session.commit()
    res.update(code=ResponseCode.Deleted)
    return res.data

@bp.route('/tasks/script/<int:script_id>/version/<int:vid>', methods=['PUT'])
@token_auth.login_required
@permission_required(Permission.DELETE)
def update_script_version(script_id, vid):
    """
        更改脚本版本信息。
        请求参数：
            /vid?action=disabled：下线指定版本
            /vid?action=enabled: 启用指定版本
            /vid: 修改版本信息。注意：只有未上线的版本才能更改
    """
    res = ResMsg()
    data = request.get_json() or {}
    action = data.get('action', 'put')
    if action == 'disabled':
        script = Scripts.query.get(script_id)
        if not script:
            db.session.rollback()
            return bad_request('脚本不存在')
        sv = ScriptsVersion.query.get(vid)
        if not sv:
            db.session.rollback()
            return bad_request('版本不存在')
        script.version = '--'
        sv.state = 2
        code=ResponseCode.Deleted
    elif action == 'enabled':
        old_sv = ScriptsVersion.query.filter_by(script_id=script_id, state=1)
        if old_sv:
            old_sv.update(dict(state=2))
        sv = ScriptsVersion.query.get(vid)
        if not sv:
            db.session.rollback()
            return bad_request('版本不存在')
        sv.state = 1
        script = Scripts.query.get(script_id)
        if not script:
            db.session.rollback()
            return bad_request('脚本不存在')
        script.version = data['data'].get('version')
        script.update_time = datetime.utcnow()
        code=ResponseCode.Created
    elif action == 'put':
        # 版本信息修改只能更改脚本内容
        sv = ScriptsVersion.query.filter_by(id=vid, script_id=script_id)
        if not sv:
            return bad_request('版本不存在')
        sv.update(dict(
            comment = data.get('comment')
            ,create_time = datetime.utcnow()
            ,add_user = g.uid
        ))
        code=ResponseCode.Created
    db.session.commit()
    res.update(code=code)
    return res.data

@bp.route('/tasks/script/<int:script_id>/version', methods=['GET'])
@token_auth.login_required
@permission_required(Permission.READ)
def get_script_versions(script_id):
    """
        获取单个脚本所有版本信息或者上线版本信息
    """
    res = ResMsg()
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('limit', current_app.config['POSTS_PER_PAGE'], type=int), 100)  # 最大值为100
    online = request.args.get('online', 0, type=int)
    if online:
        scripts = Scripts.query.filter_by(id=script_id).outerjoin(
                        ScriptsVersion, Scripts.id == ScriptsVersion.script_id).filter_by(
                            state=1).with_entities(
                                Scripts.id, Scripts.name, ScriptsVersion.version, ScriptsVersion.create_time,
                                    ScriptsVersion.id.label('vid'), ScriptsVersion.comment, ScriptsVersion.vars,
                                        Scripts.lang, ScriptsVersion.vars_tpl).first()
        data = {
                "id": scripts.id
                ,"vid": scripts.vid
                ,"name": scripts.name
                ,"version": scripts.version
                ,'comment': scripts.comment
                ,'vars': scripts.vars
                ,'update_time': scripts.create_time
                ,'lang': scripts.lang
                ,'vars_template': ''
        }
        if scripts.vars_tpl:
            data['vars_template'] = json.loads(scripts.vars_tpl, strict=False)
        count =1
    else:
        data = []
        scripts = Scripts.query.filter_by(id=script_id).outerjoin(
                        ScriptsVersion, Scripts.id == ScriptsVersion.script_id).outerjoin(
                            AdminUser, ScriptsVersion.add_user == AdminUser.id).with_entities(
                                Scripts.id, Scripts.name, ScriptsVersion.version, AdminUser.username, 
                                    ScriptsVersion.create_time,ScriptsVersion.state, ScriptsVersion.id.label('vid'))
        for s in scripts.paginate(page, per_page, False).items:
            data.append({
                'id': s.id
                ,'vid': s.vid
                ,'name': s.name
                ,'version': s.version
                ,'update_user': s.username
                ,'update_time': s.create_time.strftime('%Y-%m-%d %H:%M:%S')
                ,'state': s.state
            })
        count = scripts.count()
    res = ResMsg()
    res.update(data=data)
    res.add_field(name='count', value=count)
    return res.data

@bp.route('/tasks/script/<int:script_id>/version/<int:vid>', methods=['GET'])
@token_auth.login_required
@permission_required(Permission.READ)
def get_script_version(script_id, vid):
    """
        获取指定脚本指定版本信息。
        vid虽然是唯一的，但是必须要有script id才能查询版本信息。
    """
    res = ResMsg()
    script = ScriptsVersion.query.filter_by(id=vid, script_id=script_id).outerjoin(
                Scripts, Scripts.id==ScriptsVersion.script_id).with_entities(
                    ScriptsVersion.id, ScriptsVersion.add_user, ScriptsVersion.comment,
                    ScriptsVersion.create_time, ScriptsVersion.version, Scripts.lang, 
                    Scripts.name, ScriptsVersion.script_id, ScriptsVersion.parameter_mode,
                    ScriptsVersion.vars_tpl).first()
    if not script:
        return bad_request('版本不存在')
    data = {
        'id': script.id
        ,'add_user': script.add_user
        ,'create_time': script.create_time
        ,'comment': script.comment
        ,'version': script.version
        ,'name': script.name
        ,'lang': script.lang
        ,'script_id': script.script_id
        ,'parameter_mode': script.parameter_mode
        ,'vars_template': ''
    }
    if script.vars_tpl:
        data['vars_template'] = json.loads(script.vars_tpl, strict=False)
    res.update(data=data)
    return res.data

@bp.route('/tasks/scripts', methods=['POST'])
@token_auth.login_required
@permission_required(Permission.WRITE)
def add_scripts():
    """
    添加脚本
    """
    data = request.get_json() or {}
    if 'name' not in data:
        return bad_request('脚本名称不能为空')
    if 'version' not in data:
        return bad_request('版本号为空')
    if 'cmd_comment' not in data:
        return bad_request('脚本内容为空')
    if Scripts.query.filter_by(name=data['name']).first():
        return bad_request('脚本名称已存在')
            
    s = Scripts()
    s.from_dict(data, is_new=True)
    db.session.add(s)
    db.session.commit()
    version = ScriptsVersion()
    vdata = {}
    keys = list(data.keys())
    keys.sort()
    vs = {}  # 变量
    vtpl = []   # 前端变量模板数据
    for v in keys:
        if v.find('ocparname') != -1 or v.find('osparname') != -1:
            vs[v] = ''
            if v.find('oc') != -1:
                # 字符参数
                vtpl.append({
                    'name': data.get(v)
                    ,'id': v.split('_')[1]
                    ,'value': data.get('ocpardefault_{0}'.format(v.split('_')[1]))
                    ,'desc': data.get('ocpardesc_{0}'.format(v.split('_')[1]))
                    ,'type': 1
                })
            if v.find('os') != -1:
                # 选项参数
                vtpl.append({
                    'name': data.get(v)
                    ,'id': v.split('_')[1]
                    ,'value': data.get('osparselect_{0}'.format(v.split('_')[1]))
                    ,'desc': data.get('ospardesc_{0}'.format(v.split('_')[1]))
                    ,'type': 2
                })
    vdata['vars'] = json.dumps(vs, ensure_ascii=False)
    vdata['vars_tpl'] = json.dumps(vtpl, ensure_ascii=False)
    vdata['script_id'] = s.id
    vdata['version'] = data['version']
    vdata['comment'] = data['cmd_comment']
    vdata['parameter_mode'] = data['parameter_mode']
    version.from_dict(vdata, is_new=True)
    db.session.add(version)
    db.session.commit()
    res = ResMsg()
    res.update(code=ResponseCode.Created, data=s.to_dict())
    return res.data

@bp.route('/tasks/script/version', methods=['POST'])
@token_auth.login_required
@permission_required(Permission.WRITE)
def add_script_version():
    """
        脚本添加版本
    """
    data = request.get_json() or {}
    if 'name' not in data:
        return bad_request('脚本名称不能为空')
    if 'version' not in data:
        return bad_request('版本号为空')
    if 'comment' not in data:
        return bad_request('脚本内容为空')
    if not Scripts.query.get(int(data.get('script_id'))):
        return bad_request('脚本不存在')

    sv = ScriptsVersion()
    sv.from_dict(data, is_new=True)
    db.session.add(sv)
    db.session.commit()
    res = ResMsg()
    res.update(code=ResponseCode.Created, data=sv.to_dict())
    return res.data

