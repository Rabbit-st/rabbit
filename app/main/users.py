# -*- coding: UTF-8 -*-

from flask import render_template
from app.main import bp

@bp.route('/users/users')
def users():
    return render_template('users/users.html')

@bp.route('/users/add_user')
def add_user():
    return render_template('users/add_user.html')

@bp.route('/users/edit_user')
def edit_user():
    return render_template('users/edit_user.html')