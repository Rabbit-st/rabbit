# -*- coding: UTF-8 -*-

from flask import render_template
from app.main import bp

@bp.route('/hosts/hosts')
def hosts():
    return render_template('hosts/hosts.html')

@bp.route('/hosts/host')
def host():
    return render_template('hosts/host.html')

@bp.route('/hosts/add_host')
def add_host():
    return render_template('hosts/add_host.html')

@bp.route('/hosts/batch_add_host')
def batch_add_host():
    '''批量添加host'''
    return render_template('hosts/batch_add_host.html')

@bp.route('/hosts/edit_host')
def edit_host():
    return render_template('hosts/edit_host.html')

@bp.route('/hosts/recycle')
def recycle_host():
    return render_template('hosts/recycle.html')
