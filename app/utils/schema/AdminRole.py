#-*- coding:utf-8 -*-
from datetime import datetime
from app import ma
from marshmallow import fields,INCLUDE
from app.utils import validate_empty

# 用户models的序列化类
class AdminRoleSchema(ma.Schema):
    id = fields.Integer()
    name = fields.Str(required=True,data_key='roleName'
                      ,error_messages={'required':'名称不能为空'}
                      ,validate=validate_empty(error='名称不能为空值'))
    remark = fields.Str()
    type = fields.Str(required=True,data_key='roleType'
                      ,error_messages={'required':'类型不能为空'}
                      ,validate=validate_empty(error='类型不能为空值'))
    level = fields.Integer(missing=1)
    state = fields.Integer(missing=1)
    create_at = fields.DateTime(missing=datetime.now)
    update_time = fields.DateTime(missing=datetime.now)

    class Meta:
        # 忽略未知的字段
        unknown = INCLUDE
