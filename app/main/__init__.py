from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes, permission, users, roles \
    ,hosts, projects, ssh_users, web_ssh
