# -*- coding: UTF-8 -*-
from app.utils.model import APIMixin
from app import db
from flask_sqlalchemy import Pagination
from datetime import datetime
from app.utils import pscrypt
from app import ma
from marshmallow import fields,INCLUDE

# 用户models的序列化类
class HostsSchema(ma.Schema):
    id = fields.Integer()
    host_ip = fields.Str()
    host_name = fields.Str()
    city = fields.Str()
    site_name = fields.Str()
    remark = fields.Str()
    state = fields.Integer()
    project_id = fields.Integer()
    ssh_id = fields.Integer()
    ssh_port = fields.Integer()

    class Meta:
        # 忽略未知的字段
        unknown = INCLUDE

class hostsAPIMixin(object):
    @staticmethod
    def to_collection_dict(resource, include_project=True, **kwargs):
        """
        查询结果转换成字典格式。
        参数：
            resource：查询结果
            include_project：是否包含项目名称
        """
        data = []
        h_schema = HostsSchema()
        if include_project:
            if isinstance(resource, Pagination):
                # 分页
                for item in resource.items:
                    data.append({**h_schema.dump(item.Hosts), **{'project_name': item.name}})
                    #data.append({**item.Hosts.to_dict(), **item.Projects.to_dict()})
            else:
                for item in resource:
                    data.append({**h_schema.dump(item.Hosts), **{'project_name': item.name}})
                    #data.append({**h_schema.dump(item.Hosts), **p_schema.dump(item.Projects)})
                    #data.append({**item.Hosts.to_dict(), **item.Projects.to_dict()})
        else:
            if isinstance(resource, Pagination):
                data = [item.to_dict() for item in resource.items]
            else:
                data = [item.to_dict() for item in resource]

        return data

class Hosts(hostsAPIMixin, APIMixin, db.Model):
    """服务器信息表"""
    id = db.Column(db.Integer, primary_key=True, comment="id")
    host_ip = db.Column(db.CHAR(15), nullable=False, comment="服务器ip")
    host_name = db.Column(db.String(128), nullable=False, default='',comment='主机名')
    city = db.Column(db.String(128), nullable=False, default='', comment='机器所在地区')
    site_name = db.Column(db.String(256), nullable=False, default='', comment='站点域名')
    remark = db.Column(db.String(256), nullable=False, default='', comment='机器备注')
    state = db.Column(db.Integer, nullable=False, default=1, comment='机器状态')
    project_id = db.Column(db.Integer, index=True, nullable=False, default=0, comment='项目id')
    ssh_id = db.Column(db.Integer, nullable=False, comment="ssh id")
    ssh_port = db.Column(db.Integer, nullable=False, default=22, comment="ssh端口")
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now,comment='添加时间')
    update_time = db.Column(db.DateTime,  default=datetime.now, comment='更新时间')
    delete_time = db.Column(db.DateTime, comment='禁用时间')
    __searchable__ = ['host_ip', 'name', 'site_name', 'remark']   # 可搜索的列

    def __repr__(self):
        return '<Host {}>'.format(self.host_ip)

    def set_password(self, password):
        self.ssh_password = pscrypt.encrypt(password)

    def to_dict(self, include_projectid=False):
        """生成字典格式"""
        data = {
            'id': self.id,
            'host_ip': self.host_ip,
            'name': self.host_name,
            'city': self.city,
            'site_name': self.site_name,
            'remark': self.remark,
            'state': self.state,
            'ssh_id': self.ssh_id,
            'ssh_port': self.ssh_port
        }
        if include_projectid:
            data['project_id'] = self.project_id
        return data

    def csv_from_dict(self, filename):
        """
        csv文件转换
        """
        pass