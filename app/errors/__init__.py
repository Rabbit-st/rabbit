from flask import Blueprint

bp = Blueprint('errors', __name__) # blueprint 名称

from app.errors import handlers
