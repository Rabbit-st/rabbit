# -*- coding: UTF-8 -*-

from flask import render_template
from app.main import bp

@bp.route('/role/roles')
def roles():
    return render_template('role/roles.html')

@bp.route('/role/role')
def role():
    return render_template('role/role.html')

@bp.route('/role/add_role')
def add_role():
    return render_template('role/add_role.html')

@bp.route('/role/edit_role')
def edit_role():
    return render_template('role/edit_role.html')

@bp.route('/role/permission')
def role_permission():
    return render_template('role/permission.html')