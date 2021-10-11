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
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from itsdangerous import BadData
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, url_for, make_response, jsonify, g
from flask_login import UserMixin
from app import db
from app.utils import pscrypt, REDIS
from app.search import ES
from sqlalchemy.dialects.mysql import TINYINT
#from app.search.ES import add_to_index, remove_from_index, query_index

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

    def from_dict(self, data, map={}):
        """
            修改信息
        """
        if not isinstance(map, dict):
            return False
        for field in data:
            mfield = map.get(field, field)
            if hasattr(self, mfield):
                if data[field] == '':
                    #print(field)
                    # 空值的列，设置为None
                    setattr(self, mfield, '')
                else:
                    setattr(self, mfield, data[field])



class SearchableMixin(object):
    """
    搜索类
    """
    @classmethod
    def search(cls, expression, page, per_page, projectid=None):
        """搜索"""
        ids, total = ES.query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            # 没有搜索结果
            return 0, 0
        if projectid:
            return db.session.query(cls, Projects).outerjoin(
                Projects, cls.projectid==Projects.projectid).filter(
                    cls.hostid.in_(ids), cls.projectid==projectid), total
        else:
            return db.session.query(cls, Projects).outerjoin(
                Projects, cls.projectid==Projects.projectid).filter(
                    cls.hostid.in_(ids)), total

    '''
    @classmethod
    def before_commit(cls, session):
        # 提交前将要更改数据保存到_changes对象中。
        # session.new、session.dirty、session.deleted这些对象在提交前才有数据。
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        # 提交成功后，将更改的数据保存到es中
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                ES.add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                ES.add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                ES.remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        # 更新所有的数据
        for obj in cls.query:
            ES.add_to_index(cls.__tablename__, obj)
    '''

'''
# 数据库事件监听
db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)
'''

# 用户与角色映射表
user_role = db.Table('admin_user_role',
    db.Column('user_id', db.Integer, db.ForeignKey('admin_user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('admin_role.id'))
)
# 角色与permission映射表
role_permission = db.Table('admin_role_permission',
    db.Column('role_id', db.Integer, db.ForeignKey('admin_role.id')),
    db.Column('url_id', db.Integer, db.ForeignKey('admin_permission.id'))
)

class AdminUser(APIMixin, UserMixin, db.Model):
    """User表结构"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True,comment='登录名')
    nickname = db.Column(db.String(64),comment='真名')
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    avatar = db.Column(db.String(256), comment="头像链接")
    state = db.Column(db.Integer, nullable=False, default=1, comment='用户状态,1: 正常，0：禁用')
    remark = db.Column(db.String(256), nullable=False, default='', comment='备注')
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow,comment='添加时间')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.relationship(
                'AdminRole',                    # 关联的表类
                secondary=user_role,       # 中间表
                backref=db.backref('users', lazy='dynamic'),   # 反向引用
                lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def get_reset_password_token(self, expires_in=600):
        # 重置密码，生成令牌字符串。exp是jwt的标准字段，如果它存在，则表示令牌的到期时间
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        # 重置密码，解密令牌得到user
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return AdminUser.query.get(id)

    def to_dict(self, include_email=True):
        """生成字典格式"""
        data = {
            'id': self.id,
            'username': self.username,
            'last_seen': self.last_seen.strftime('%Y-%m-%d %H:%M:%S'),
            'state': self.state,
            'phone': self.phone,
            'description': self.description,
        }
        if include_email:
            data['email'] = self.email
        return data

    def from_dict(self, data):
        """
            修改信息
        """
        for field in data:
            if hasattr(self, field):
                if field == 'password' and data.get(field):
                    self.set_password(data[field])
                if field != 'password':
                    setattr(self, field, data[field])
    '''
    def from_dict(self, data, role=None, new_user=False):
        for field in data:
            if field != 'password' and field != 'role':
                setattr(self, field, data[field])
        if new_user:
            self.state = 1
            self.createtime = datetime.utcnow()
        if new_user or data.get('password', 0):
            self.set_password(data['password'])
        if role:
            self.roles = role
    '''

    def add_role(self, role):
        """
            添加角色。
            默认为临时账号
        """
        self.roles.append(role)

    def generate_auth_token(self, expiration=None):
        """生成token,默认过期时间为10分钟"""
        expire = expiration \
                if expiration else current_app.config.get('TOKEN_EXPIRE')
        s = Serializer(
                secret_key = current_app.config['SECRET_KEY'],
                salt = current_app.config['AUTH_SALT'],
                expires_in = expire)
        token = s.dumps({
                    'id': self.id,
                    'username': self.username,
                    'iat': time()
                }).decode('utf-8')
        #TODO: 后期放到verify_auth_token
        #TODO: redis设置失败的时候要将token存到其他地方，不然退出登录没法实现
        self.last_seen = datetime.utcnow() 
        try:
            REDIS.set(token, '{0}:{1}'.format(self.id, self.username), expire)
        except Exception as e:
            pass  # 后面要记录日志
        return token

    @staticmethod
    def verify_auth_token(token):
        """验证token是否有效"""
        rs_status = 1
        username = None

        # 在黑名单的
        try:
            u = REDIS.get('black:{}'.format(token))
            if u:
                return False
        except Exception as e:
            rs_status = 0
            pass

        # 缓存有的
        if rs_status:
            try:
                user = REDIS.get(token)
                if user:
                    g.uid = user.split(':')[0]
                    g.username = user.split(':')[1]
                    return True
            except Exception as e:
                rs_status = 0
                pass # 很大可能redis挂了, 记录日志

        s = Serializer(
                secret_key = current_app.config['SECRET_KEY'],
                salt = current_app.config['AUTH_SALT'],
            )
        try:
            data = s.loads(token)
        except SignatureExpired:
            return False
        except BadSignature as e:
            encoded_payload = e.payload
            if encoded_payload is not None:
                try:
                    s.load_payload(encoded_payload)
                except BadData:
                    return False
            return False
        except:
            return False
        if 'id' not in data or 'username' not in data:
            return False
            #raise make_response(jsonify({'msg':'illegal payload inside'}), 1005)
        # 缓存没找到，但是解析成功，格式正确的，加入到缓存中
        if rs_status:
            REDIS.set(token, '{0}:{1}'.format(data['id'], data['username']), current_app.config.get('TOKEN_EXPIRE'))
        g.uid = data['id']
        g.username = data['username']
        return True

    @staticmethod
    def revoke_token(token):
        """
        登出的token加到黑名单
        """
        key = 'black:{}'.format(token)
        REDIS.set(key, 'b', current_app.config.get('TOKEN_EXPIRE'))
    
        return True

class AdminRole(APIMixin, db.Model):
    """
        角色表。
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, comment='role id')
    name = db.Column(db.String(100), nullable=False, comment='角色名称')
    remark = db.Column(db.String(256), nullable=False, default='', comment='备注')
    type = db.Column(db.String(50), nullable=False,comment='类型,超级管理员、管理员、临时账号等')
    level = db.Column(db.Integer, nullable=False, comment='账号权限等级，1:超级管理员,2:管理员,3:开发,4:临时')
    state = db.Column(db.Integer, nullable=False, default=1, comment='角色状态, 1启用，0禁用')
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='添加时间')
    update_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='更新时间')
    permission = db.relationship(
                'AdminPermission',                    # 关联的表类
                secondary=role_permission,       # 中间表
                backref=db.backref('role', lazy='dynamic'),   # 反向引用
                lazy='dynamic')
    
    def to_dict(self):
        """生成字典格式"""
        data = {
            'id': self.id,
            'role': self.role,
            'type': self.type,
            'description': self.description,
            'createtime': self.createtime.strftime('%Y-%m-%d %H:%M:%S'),
        }
        return data

    '''
    def from_dict(self, data, isnew=False, users=None):
        """修改角色"""
        for field in data:
            if field != 'users':
                setattr(self, field, data[field])
        if isnew:
            self.createtime = datetime.utcnow()
            self.level = 5   # 新建的组都用5
            self.type = '自定义'
            self.state = 1
        if users:
            self.users = users
    '''

    def add_url(self, urls):
        """
            添加url.
            urls: list
        """
        self.permission = urls

    def add_user(self, users):
        """
            关联用户
            users: list
        """
        self.users = users

class AdminPermission(APIMixin, db.Model):
    """
        admin_permission权限表
        admin_role表和admin_permission表为多对多关系
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, comment='url id')
    name = db.Column(db.String(128), nullable=False, default='', comment='权限名称')
    url = db.Column(db.String(300), nullable=True, comment='url链接')
    #permission = db.Column(db.Integer, nullable=False, comment='权限. 1读,2写，4更改，8删除，15所有')
    type = db.Column(db.String(50), nullable=False,comment='类型, 0: 一级菜单, 1:二级菜单，2：按钮，3:hosts')
    description = db.Column(db.String(256), nullable=False, default='', comment='备注')
    open_type = db.Column(db.String(10), comment='打开方式，_iframe或者空值')
    parent_id = db.Column(db.String(19), comment='父类编号')
    icon = db.Column(db.String(128), comment='图标,对应的layui-icon类')
    sort = db.Column(db.Integer, comment='排序顺序')
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow,comment='添加时间')
    update_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow,comment='添加时间')
    state = db.Column(db.Integer, nullable=False, default=1, comment='权限状态 0: 禁用，1：正常')
    code = db.Column(db.String(30), comment='权限标识')

    def to_dict(self):
        """生成字典格式"""
        data = {
            'powerId': self.id,
            'powerName': self.name,
            'createTime': self.create_time,
            'openType': self.open_type,
            'parentId': self.parent_id,
            'powerType': self.type,
            'powerUrl': self.url,
            'sort': self.sort,
            'state': self.state,
            'icon': self.icon,
            'powerCode': self.code,
            'updateTime': self.update_time,
            #'permission': Permission.code_to_str(self.permission),
            'description': self.description,
        }
        return data

class Permission(object):
    READ = 0x01
    WRITE = 0x02
    UPDATE = 0x04
    DELETE = 0x08
    ALL = 0x0F

    @classmethod
    def code_to_str(cls, code):
        permission = []
        if code & cls.ALL == cls.ALL:
            permission.append('所有')
            return permission

        if code & cls.READ == cls.READ:
            permission.append('读')
        if code & cls.WRITE == cls.WRITE:
            permission.append('写')
        if code & cls.UPDATE == cls.UPDATE:
            permission.append('更改')
        if code & cls.DELETE == cls.DELETE:
            permission.append('删除')
        return permission

    @classmethod
    def methods_to_code(cls, methods):
        """
            method: list
        """
        c = []
        if isinstance(methods, list):
            return False
        for method in methods:
            if str(method).lower() == 'get':
                c.append(cls.READ)
            elif str(method).lower() == 'post':
                c.append(cls.WRITE)
            elif str(method).lower() == 'delete':
                c.append(cls.DELETE)
            elif str(method).lower() == 'put':
                c.append(cls.UPDATE)
            else:
                continue
        return c