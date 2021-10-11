# -*- coding: UTF-8 -*-

from flask import render_template
from app.main import bp

@bp.route('/webssh')
def web_ssh():
    return render_template('webssh/webssh.html')

@bp.route('/webssh/web')
def get_web_ssh():
    return render_template('webssh/web.html')