#-*- coding:utf-8 -*-
from datetime import datetime
from app import ma
from marshmallow import fields,INCLUDE, ValidationError, validates_schema,validates
#from app.models.models import AdminUser
from marshmallow import fields,INCLUDE
from app.utils import validate_empty
from app.utils import check_password

# 用户models的序列化类
class AdminUserSchema(ma.Schema):
    id = fields.Integer()
    username = fields.Str(required=True, validate=validate_empty(error='账号不能为空'))
    email = fields.Email(error_messages={'invalid':'邮箱格式错误'})
    last_seen = fields.DateTime(missing=datetime.now)
    state = fields.Integer(missing=1)
    create_at = fields.DateTime(missing=datetime.now)
    nickname = fields.Str(required=True, validate=validate_empty(error='姓名不能为空'))
    avatar = fields.Str()
    remark = fields.Str()
    password = fields.Str(required=True, load_only=True)
    password2 = fields.Str(required=True, allow_none=True)

    class Meta:
        # 忽略未知的字段
        unknown = INCLUDE

    @validates_schema
    def validate(self,data,**kwargs):
        if data['password'] != data['password2']:
            raise ValidationError('输入的两次密码不一致!')
        data.pop('password2')
        return data

    @validates('password')
    def validate_password(self, data, **kwargs):
        r = check_password(data)
        if  r != 1:
            raise ValidationError(r)

# 编辑反序列化
class AdminUserSchema2(ma.Schema):
    id = fields.Integer()
    username = fields.Str(required=True, validate=validate_empty(error='账号不能为空'))
    email = fields.Email(error_messages={'invalid':'邮箱格式错误'})
    last_seen = fields.DateTime(missing=datetime.now)
    state = fields.Integer(missing=1)
    create_at = fields.DateTime(missing=datetime.now)
    nickname = fields.Str(required=True, validate=validate_empty(error='姓名不能为空'))
    avatar = fields.Str()
    remark = fields.Str()
    password = fields.Str(load_only=True)
    password2 = fields.Str(allow_none=True)

    class Meta:
        # 忽略未知的字段
        unknown = INCLUDE

    @validates_schema
    def validate(self,data,**kwargs):
        if data.get('password', None) is not None:
            if data['password'] != data['password2']:
                raise ValidationError('输入的两次密码不一致!')

            data.pop('password2')
            return data

    @validates('password')
    def validate_password(self, data, **kwargs):
        if data:
            r = check_password(data)
            if  r != 1:
                raise ValidationError(r)