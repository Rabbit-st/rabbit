#-*- coding:utf-8 -*-
from datetime import datetime
from app import ma
from marshmallow import fields,INCLUDE
from marshmallow import fields,INCLUDE
from app.utils import validate_empty

class ProjectsSchema(ma.Schema):
    id = fields.Integer()
    name = fields.Str(required=True, validate=validate_empty(error='项目名不能为空'))
    remark = fields.Str(missing='')
    state = fields.Integer(missing=1)
    #create_time = fields.DateTime(missing=datetime.now, load_only=True)
    update_time = fields.DateTime(missing=datetime.now)

    class Meta:
        # 忽略未知的字段
        unknown = INCLUDE