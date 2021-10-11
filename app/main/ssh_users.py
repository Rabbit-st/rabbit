# -*- coding: UTF-8 -*-

from flask import render_template
from app.main import bp

@bp.route('/ssh_users/ssh_users')
def get_ssh_users():
    return render_template('sshusers/ssh_users.html')

@bp.route('/ssh_users/add_ssh_user')
def add_ssh_user_n():
    return render_template('sshusers/add_ssh_user.html')

@bp.route('/ssh_users/edit_ssh_user')
def edit_ssh_user_n():
    return render_template('sshusers/edit_ssh_user.html')
