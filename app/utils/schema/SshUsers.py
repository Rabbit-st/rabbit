#-*- coding:utf-8 -*-
from datetime import datetime
from app import ma
from marshmallow import fields,INCLUDE, ValidationError, validates_schema,validates
#from app.models.models import AdminUser
from marshmallow import fields,INCLUDE
from app.utils import validate_empty
from app.utils import check_password

# 用户models的序列化类
class SshUsersSchema(ma.Schema):
    id = fields.Integer()
    name = fields.Str(required=True, validate=validate_empty(error='名称不能为空'))
    ssh_user = fields.Str(required=True, validate=validate_empty(error='用户名不能为空'))
    ssh_password = fields.Str(load_only=True)
    private_key = fields.Str(load_only=True)
    remark = fields.Str()
    state = fields.Integer(missing=1)
    update_time = fields.DateTime(missing=datetime.now)

    class Meta:
        # 忽略未知的字段
        unknown = INCLUDE