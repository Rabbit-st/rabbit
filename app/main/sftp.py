# -*- coding: UTF-8 -*-

from flask import render_template
from app.main import bp

@bp.route('/sftp/sftp')
def get_ssh_users():
    return render_template('sftp/sftp.html')