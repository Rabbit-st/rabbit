#-*- coding:utf-8 -*-
from datetime import datetime
from app import ma
from marshmallow import fields,INCLUDE, ValidationError, validates
from marshmallow import fields,INCLUDE
from app.utils import validate_empty
from app.models import Projects,SshUsers

# 用户models的序列化类
class HostsSchema(ma.Schema):
    id = fields.Integer()
    host_ip = fields.Str(required=True, validate=validate_empty(error='ip不能为空'))
    host_name = fields.Str(required=True, validate=validate_empty(error='主机名不能为空'))
    city = fields.Str(missing='')
    site_name = fields.Str(missing='')
    remark = fields.Str(missing='')
    state = fields.Integer(missing=1)
    project_id = fields.Integer(required=True, validate=validate_empty(error='请选择项目'),error_messages={'invalid':'请选择项目id'})
    ssh_id = fields.Integer(required=True, validate=validate_empty(error='请选择ssh'),error_messages={'invalid':'请选择ssh用户'})
    ssh_port = fields.Integer(required=True, validate=validate_empty(error='ssh端口不能为空'))
    update_time = fields.DateTime(missing=datetime.now)
    delete_time = fields.DateTime(missing=None)
    project_name = fields.Method("get_project")

    class Meta:
        # 忽略未知的字段
        unknown = INCLUDE

    @validates('project_id')
    def validate_password(self, data, **kwargs):
        if not Projects.query.filter_by(id=data).first():
            raise ValidationError('项目不存在')

    @validates('ssh_id')
    def validate_password(self, data, **kwargs):
        if not SshUsers.query.filter_by(id=data).first():
            raise ValidationError('ssh用户不存在')

    def get_project(self, obj):
        if obj.project_id != None:
            p = Projects.query.filter_by(id=obj.project_id).first()
            return p.name if p else None
        return None
