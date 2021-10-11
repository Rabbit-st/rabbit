# -*- coding: UTF-8 -*-

from flask import send_file,render_template
from app.main import bp

@bp.route('/permission')
def permission():
    return render_template('permission/permission.html')

@bp.route('/permission/add')
def add_permission():
    return render_template('permission/add_permission.html')

@bp.route('/permission/edit')
def edit_permission():
    return render_template('permission/edit_permission.html')

@bp.route('/permission/refresh')
def refresh_permission():
    return render_template('permission/refresh_permission.html')