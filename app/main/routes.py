from datetime import datetime
import re
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, send_file, send_from_directory
from flask_login import current_user, login_required
#from guess_language import guess_language
from app import db
from app.main import bp

@bp.route('/welcome')
def welcome():
    return render_template('index/welcome.html')

@bp.route('/')
@bp.route('/login')
def login():
    return render_template('login.html')

@bp.route('/index')
def index():
    return render_template('index.html')

@bp.route('/index_pear')
def index_pear():
    return render_template('index_pear.html')

@bp.route('/member-list')
def member_list():
    return render_template('member-list.html')

@bp.route('/mail_history')
def mail_history():
    return send_file('templates/alarm/mail_history.html')

@bp.route('/alarm_mail')
def alarm_mail():
    return send_file('templates/alarm/alarm_mail.html')

@bp.route('/edit_alarm_mail')
def edit_alarm_config():
    return send_file('templates/alarm/edit_alarm_mail.html')

@bp.route('/mail_config')
def mail_config():
    return send_file('templates/alarm/mail_config.html')

@bp.route('/add_mail_config')
def add_mail_config():
    return send_file('templates/alarm/add_mail_config.html')

@bp.route('/edit_mail_config')
def edit_mail_config():
    return send_file('templates/alarm/edit_mail_config.html')

@bp.route('/deployenv')
def deployenv():
    return send_file('templates/tasks/deployenv.html')

@bp.route('/add_deployenv')
def add_deployenv():
    return send_file('templates/tasks/add_deployenv.html')

@bp.route('/exec_deployenv')
def exec_deployenv():
    return send_file('templates/tasks/exec_deployenv.html')

@bp.route('/version_manage')
def version_manage():
    return send_file('templates/tasks/version_manage.html')

@bp.route('/script')
def get_script():
    return send_file('templates/tasks/script.html')

@bp.route('/add_script_version')
def add_script_version():
    return send_file('templates/tasks/add_script_version.html')

@bp.route('/edit_script_version')
def edit_script_version():
    return send_file('templates/tasks/edit_script_version.html')

@bp.route('/script_version')
def get_script_version():
    return send_file('templates/tasks/script_version.html')
