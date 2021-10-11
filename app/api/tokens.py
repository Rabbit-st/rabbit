from io import BytesIO
from flask import jsonify, request, session, make_response
from app import db
from app.api import bp
from app.api.auth import basic_auth, token_auth
from app.utils import REDIS, ResMsg, ResponseCode, common, api_result
from app.api.errors import bad_request
from app.models.models import AdminUser
import sys

@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    """
    获取token
    """
    res = ResMsg()
    data = request.get_json() or {}
    code = data.get('captcha')
    s_code = session.get('code', None)
    
    if not all([code, s_code]):
        res.update(code=ResponseCode.Fail, msg='没有输入验证码')
        return res.data
    
    if code != s_code:
        res.update(code=ResponseCode.Fail, msg='验证码错误')
        return res.data
    
    if basic_auth.current_user().state == 0:
        res.update(code=ResponseCode.Fail, msg='账号已禁用')
        return res.data
    try:
        token = basic_auth.current_user().generate_auth_token()
        username = basic_auth.current_user().username
    except Exception as e:
        res.update(code=ResponseCode.Fail, msg='用户或密码不正确')
        return res.data
    try:
        if basic_auth.current_user().id == 1:
            # 超级管理员直接用1
            level = 1
        else:
            level = basic_auth.current_user().role.first().level
    except Exception as e:
        res.update(code=ResponseCode.Fail, msg="用户没有绑定用户组")
        return res.data
    db.session.commit()
    common.add_auth_session()
    session['level'] = level
    res.update(code=ResponseCode.Success, data={'token': token, 'username': username,'l': level})
    return res.data

@bp.route('/captcha', methods=['GET'])
def get_captcha():
    code, image = common.gen_captcha()
    session["code"] = code
    out = BytesIO()
    image.save(out, 'png')
    out.seek(0)
    resp = make_response(out.read())
    resp.content_type = 'image/png'
    return resp

@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    """
    删除token
    """
    res = ResMsg()
    if 'Authorization' in request.headers:
        auth_type, token = request.headers['Authorization'].split(
            None, 1)
        try:
            AdminUser.revoke_token(token)
        except Exception as e:
            return api_result(code=-1, msg='token 移除失败')
        return res.data
