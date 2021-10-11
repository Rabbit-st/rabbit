#-*- coding:utf-8 -*-

from captcha.image import ImageCaptcha
from PIL import Image
from random import choices
from string import ascii_lowercase, digits
from flask import session, g
from app.api.auth import basic_auth
from app.models.models import AdminPermission,AdminUser

def gen_captcha(content=digits + ascii_lowercase):
    """生成验证码"""
    image = ImageCaptcha()
    # 获取字符串
    captcha_text = "".join(choices(content, k=4))
    # 生成图像
    captcha_image = Image.open(image.generate(captcha_text))
    return captcha_text, captcha_image

def add_auth_session(refresh=False):
    """
    用户权限添加到session中
    """
    if refresh:
        user = AdminUser.query.get(g.uid)
        role = user.role
        user_id = user.id
    else:
        role = basic_auth.current_user().role
        user_id = basic_auth.current_user().id
    user_permission = []
    if user_id == 1:
        # 超级管理员直接获取全部
        p = AdminPermission.query.all()
        for i in p:
            if i.state == 0 or i.code is None or i.code == '':
                continue
            user_permission.append(i.code)
    else:
        for i in role:
            if i.state == 0:
                continue
            for p in i.permission:
                if p.state == 0:
                    continue
                user_permission.append(p.code)
    session['permissions'] = user_permission

def permission_to_tree(data, pid=0, field1='id', field2='parent_id', field3='children'):
    result =[]
    for k in data:
        if data[k][field2] == pid:
            data[k][field3] = permission_to_tree(data, data[k][field1])
            result.append(data[k])
    return result