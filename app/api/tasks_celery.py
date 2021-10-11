# -*- coding: UTF-8 -*-
import re
from datetime import datetime
import time
from flask import request, current_app, g
from app.models.ansibles import Scripts, ScriptsVersion, \
    TaskQueue, TaskHistory
from app.models import Hosts, SshUsers
from app.utils import BaseInventory, AnsibleRunner
from app import db, celery
import os

@celery.task(bind=True)
def exec_ansible_playbook(self, hosts:list, playbook:str, extra_vars:str = None):
    """
        执行ansible playbook
        参数：
            job_id：任务id
            hosts：主机id列表
            playbook：ansible playbook文件路径
            extra_vars：变量
    """
    # print(self.request.id)  # self.request.id == task.id
    with open(os.path.join('/tmp/celery', self.request.id), 'w+') as f:
        for i in range(1, 100):
            f.write(str(i))
            self.update_state(
                state='PROGRESS',
                meta={'current': i 
                      ,'total': 100
                      ,'status': str(i)})
            time.sleep(1)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}

@celery.task
def ansible_exec_script(job_id:str, username:str, hosts:list, ssh_id:int, script_id:int, extra_vars:str = None):
    """
        执行脚本
        参数：
            jobid：任务id
            username: 用户名
            hosts：host id列表
            ssh_id: ssh用户id
            script_id：脚本id
            extra_vars：脚本变量
    """
    status = 'SUCCESS'
    state = 1
    callback = ''
    # 添加到task_history
    th = TaskHistory(job_id=job_id, add_user=username, start_time=datetime.utcnow(), state=2)
    # 更新task_queue状态
    tq = TaskQueue.query.filter_by(job_id=job_id)
    tq.update(dict(status="STARTED"))
    db.session.add(th)
    db.session.commit()
    script = ScriptsVersion.query.filter_by(id=script_id).outerjoin(
                Scripts, Scripts.id == ScriptsVersion.script_id
                ).with_entities(ScriptsVersion.comment, Scripts.lang).first()
    if not script or not script.comment:
        tq.update(dict(status="FAILURE",callback="脚本不存在"))
        db.session.commit()
        return False
    host = Hosts.query.filter(Hosts.id.in_(hosts)).with_entities(
            Hosts.host_ip, Hosts.ssh_port)
    ssh = SshUsers.query.filter_by(id=ssh_id).first()
    ssh_password = ssh.get_password(ssh.ssh_password)
    resource = []
    for h in host:
        resource.append({
            'ip': h.hostip
            ,'port': h.ssh_port
            ,'username': ssh.ssh_user
            ,'password': ssh_password
        })
    # 添加ansible hosts信息
    inventory = BaseInventory(resource=resource)
    ans = AnsibleRunner(inventory)
    if script.lang == 'shell' or script.lang == 'python':
        # 脚本写入到临时文件
        script_tmp = os.path.join(current_app.config['SCRIPT_FOLDER'], job_id)
        with open(script_tmp, 'w+') as f:
            f.write(script.comment)
        # 脚本copy到目标机器
        tasks = [{'action': {'module': 'copy', 'args': 'src={0} dest={0} mode=u+x'.format(script_tmp)}}]
        res = ans.adhoc_runner(tasks, 'all')
        if res.results_raw.get('failed'):
            status = 'FAILURE'
            callback = '脚本不存在'
            state = 0
        # 执行脚本
        if state == 1:
            tasks = [{'action': {'module': 'shell', 'args': './{0}'.format(script_tmp)}}]
            res = ans.adhoc_runner(tasks, 'all')
            if res.results_raw.get('failed'):
                status = 'FAILURE'
                state = 0
        th.state = state
        th.callback = res.results_raw
        db.session.delete(tq)
        db.session.commit()
    #else:
