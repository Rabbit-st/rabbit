from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import routes, projects, ssh_users, \
                errors, tokens, users, hosts, roles,\
                tasks, tasks_celery, menu, permission