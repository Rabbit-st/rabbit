#-*- coding:utf-8 -*-
from app import ma
from marshmallow import fields,INCLUDE
from datetime import datetime
from app.utils import validate_empty

# menu中用到
class AdminPermissionSchema(ma.Schema):
    id = fields.Integer()
    title = fields.Str(attribute="name")
    type = fields.Str()
    code = fields.Str()
    href = fields.Str(attribute="url")
    openType = fields.Str(attribute="open_type")
    parent_id = fields.Integer()
    icon = fields.Str()
    sort = fields.Integer()
    create_time = fields.DateTime()
    update_time = fields.DateTime()
    state = fields.Integer()

# 角色权限管理页面
class AdminPermissionSchema3(ma.Schema):
    id = fields.Integer()
    name = fields.Str()
    type = fields.Method("get_type")
    code = fields.Str()
    url = fields.Str()
    open_type = fields.Str()
    parent_id = fields.Integer()
    icon = fields.Str()
    sort = fields.Integer()
    create_time = fields.DateTime()
    update_time = fields.DateTime()
    state = fields.Integer()

    def get_type(self, obj):
        if obj.type == '0':
            return '目录'
        elif obj.type == '1':
            return '菜单'
        elif obj.type == '2':
            return 'api'
        else:
            return 'obj.type'

# 角色数据验证
class AdminPermissionSchema4(ma.Schema):
    id = fields.Str()
    name = fields.Str(required=True, validate=validate_empty(error='名称不能为空值')
                      ,error_messages={'required':'名称必须填写'})
    type = fields.Str(required=True, validate=validate_empty(error='类型必须选择')
                      ,error_messages={'required':'类型不存在'})
    code = fields.Str(required=True,error_messages={'required':'标识不存在'})
    url = fields.Str(required=True,error_messages={'required':'路径不能为空'})
    open_type = fields.Str(required=True,error_messages={'required':'必须选择打开方式'})
    parent_id = fields.Str(required=True,validate=validate_empty(error='父级必须选择')
                           ,error_messages={'required':'必须选择父级'})
    icon = fields.Str()
    sort = fields.Integer(error_messages={'invalid':'排序不能为空'})
    create_at = fields.DateTime(missing=datetime.now)
    updateTime = fields.DateTime(missing=datetime.now)
    state = fields.Integer(missing=1)

    class Meta:
        # 忽略未知的字段
        unknown = INCLUDE