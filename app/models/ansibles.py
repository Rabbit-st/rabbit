# -*- coding: UTF-8 -*-
# 数据库模型
# 依赖库：flask-sqlalchemy、flask-migrate、pymysql

import os
import json
import base64
from time import time
from hashlib import md5
from time import time
from datetime import datetime, timedelta
from app import db
from app.utils import REDIS
from flask_sqlalchemy import Pagination
from sqlalchemy.dialects.mysql import TINYINT
from flask import g

class APIMixin(object):
    @staticmethod
    def to_collection_dict(resource, **kwargs):
        """
        查询结果转换成字典格式。
        参数：
            resource：分页后的数据
        """
        data = [item.to_dict() for item in resource.items]
        return data

class AnsPlaybook(APIMixin, db.Model):
    """ansible playbook列表"""
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    comment = db.Column(db.Text, comment='playbook')
    vars = db.Column(db.String(200), nullable=False, comment='脚本需要的变量')
    description = db.Column(db.String(256), nullable=False, default='', comment='备注')
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow,comment='添加时间')
    update_time = db.Column(db.DateTime, default=datetime.utcnow)
    add_user = db.Column(db.Integer, nullable=False, comment='添加用户')
    last_user = db.Column(db.Integer, nullable=False, comment='最后更改用户')
    
    def to_dict(self):
        """生成字典格式"""
        data = {
            'id': self.id,
            'comment': self.comment,
            'description': self.description,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'add_user': self.add_user,
        }
        return data

    def from_dict(self, data, is_new=None):
        for field in data:
            if field != 'password' and field != 'role':
                setattr(self, field, data[field])
        if is_new:
            self.last_user = self.add_user

class Task(APIMixin, db.Model):
    """
        任务列表
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, comment='task id')
    type = db.Column(db.String(100), nullable=False, comment='任务类型。可选值：ansible、shell、ansible-playbook')
    description = db.Column(db.String(256), nullable=False, default='', comment='备注')
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow,comment='添加时间')
    add_user = db.Column(db.Integer, nullable=False, comment='添加用户')
    playbook_id = db.Column(db.Integer, nullable=False, comment='对应的ansible playbook id')
    last_execution = db.Column(db.DateTime, nullable=False, default=datetime.utcnow,comment='最后执行时间')
    total_run_amount = db.Column(db.Integer, nullable=False, comment='执行总次数')
    success_run_amount = db.Column(db.Integer, nullable=False, comment='执行成功次数')    

    def to_dict(self):
        """生成字典格式"""
        data = {
            'id': self.id,
            'type': self.type,
            'vars': self.vars,
            'createtime': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'add_user': self.add_user,
            'description': self.description
        }
        return data

    def from_dict(self, data, is_new=False):
        for field in data:
            setattr(self, field, data[field])
        if isnew:
            self.total_run_amount = 0
            self.success_run_amount = 0

class TaskQueue(APIMixin, db.Model):
    """
        执行中的任务
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, comment='id')
    job_id = db.Column(db.String(200), nullable=False, comment='任务id')
    add_user = db.Column(db.Integer, nullable=False, comment='创建任务的用户id')
    #task_id = db.Column(db.Integer, nullable=False, comment='关联的task id')
    status = db.Column(db.String(20), nullable=False, default='', comment='任务状态，PENDING, STARTED, SUCCESS, FAILUER, RETRY, REVOKED')
    callback = db.Column(db.Text, comment='执行返回的信息')
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow,comment='开始时间')

    def to_dict(self):
        """生成字典格式"""
        data = {
            'job_id': self.job_id,
            'add_user': self.add_user,
            'callback': self.callback,
            'start_time': self.start_time,
        }
        return data

class TaskHistory(APIMixin, db.Model):
    """
        执行任务历史记录
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False,comment="id")
    job_id = db.Column(db.String(200), nullable=False, comment='任务id')
    add_user = db.Column(db.Integer, nullable=False, comment='创建任务的用户')
    #task_id = db.Column(db.Integer, nullable=False, comment='关联的task id')
    callback = db.Column(db.Text, comment='执行返回的信息')
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow,comment='开始时间')
    end_time = db.Column(db.DateTime, default=datetime.utcnow,comment='结束时间')
    state = db.Column(TINYINT, nullable=False, comment='执行结果，0：失败，1：成功，2：未知')
    
    def to_dict(self):
        """生成字典格式"""
        data = {
            'job_id': self.job_id,
            'add_user': self.add_user,
            'callback': self.callback,
            'duration': (self.end_time - self.start_time).seconds,  # 执行花费秒数
            'state': self.state,
        }
        return data

    def from_dict(self, data):
        for field in data:
            setattr(self, field, data[field])

class Scripts(APIMixin, db.Model):
    """脚本列表"""
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False, comment='脚本名称')
    classifying = db.Column(db.String(50), nullable=False, default='',comment='类别')
    lang = db.Column(db.String(30), nullable=False, comment='脚本语言')
    description = db.Column(db.String(256), nullable=False, default='', comment='描述')
    version = db.Column(db.String(50), nullable=False, comment='上线版本')
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow,comment='添加时间')
    update_time = db.Column(db.DateTime, default=datetime.utcnow, comment='最后一次更新时间')
    last_user = db.Column(db.Integer, nullable=False, comment='最后更改用户id')
    
    def to_dict(self):
        """生成字典格式"""
        data = {
            'id': self.id,
            'name': self.name,
            'classifying': self.classifying,
            'description': self.description,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'user': self.last_user,
            'lang': self.lang,
        }
        return data

    def from_dict(self, data, is_new=None):
        for field in data:
            if hasattr(self, field) and field != 'version':
                setattr(self, field, data[field])
        if is_new:
            self.version = '--'
            self.create_time = datetime.utcnow()
            self.update_time = datetime.utcnow()
        self.last_user = g.uid

class ScriptsVersion(APIMixin, db.Model):
    """脚本版本列表"""
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    script_id = db.Column(db.Integer, nullable=False, comment='脚本id')
    version = db.Column(db.String(50), nullable=False, comment='版本')
    comment = db.Column(db.Text, comment='脚本内容')
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow,comment='添加时间')
    add_user = db.Column(db.Integer, nullable=False, comment='添加用户id')
    vars = db.Column(db.Text, nullable=False, default='', comment='脚本需要的变量')
    parameter_mode = db.Column(db.String(20), nullable=False, default='line', comment='变量传递方式，1.命令行，2.json')
    vars_tpl = db.Column(db.Text, comment="脚本变量前端模板数据")
    state = db.Column(db.Integer, nullable=False, default=0, comment='状态,0：未上线，1：在线，2：下线')
    
    def to_dict(self, include_comment=False):
        """生成字典格式"""
        data = {
            'id': self.id,
            #'comment': self.comment,
            'version': self.version,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'add_user': self.add_user,
        }
        if include_comment:
            data['comment'] = self.comment
        return data

    def from_dict(self, data, is_new=None):
        for field in data:
            if hasattr(self, field):
                setattr(self, field, data[field])
        self.create_time = datetime.utcnow()
        self.add_user = g.uid
        self.state = 0
