from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES

def bad_request(message, status_code=400):
    return error_response(status_code, message)

def error_response(status_code, message=None):
    payload = {'code': status_code,
               'status': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['msg'] = message
    response = jsonify(payload)  # jsonify返回一个flask Response对象, 默认状态码为200
    response.status_code = status_code
    return response
