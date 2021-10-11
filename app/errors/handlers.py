from flask import render_template, request
from app import db
from app.errors import bp
from app.api.errors import error_response as api_error_response

def wants_json_response():
    return request.accept_mimetypes['application/json'] >= \
        request.accept_mimetypes['text/html']

@bp.errorhandler(404)
def not_fount_error(error):
    if wants_json_response():
        return api_error_response(404)
    return render_template('errors/404.html'), 404 # 第二个值表示错误代码号

@bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if wants_json_response(500):
        return api_error_response(500)
    return render_template('errors/500.html'), 500 # 第二个值表示错误代码号
