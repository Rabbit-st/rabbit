# -*- coding: UTF-8 -*-
from app.api import bp
from flask import jsonify, url_for, current_app
from app.api.auth import token_auth

@bp.route('/frontcheck', methods=['POST'])
@token_auth.login_required
def frontcheck():
    """前端检测token"""
    return jsonify({'status': 200})
