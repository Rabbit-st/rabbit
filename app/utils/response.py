from flask import jsonify, request, current_app
from werkzeug.http import HTTP_STATUS_CODES
from app.utils.code import ResponseCode, ResponseMessage as resmsg
from time import time

def api_result(code=1, data='', msg='', **kwargs):
    """
        code: 响应编码
        data: 数据
        msg： 消息
        **kwargs：其他数据
    """
    lang = request.headers.get("lang",current_app.config.get('LANG', 'zh_CN'))
    payload = {
        'code': code
        ,'data': data
        ,'msg': msg if msg else resmsg.Msg[lang].get(code, None)
        ,'lang': lang
        ,'ts': time()
    }
    for key in kwargs:
        if key in ['code', 'msg', 'data']:
            continue
        payload[key] = kwargs[key]
    return jsonify(payload)

class ResMsg(object):
    def __init__(self, data=None, code=ResponseCode.Success, rq=request):
        """
        根据语言返回对应的消息，默认为中文
        """
        self.lang = rq.headers.get("lang",
                                  current_app.config.get('LANG', 'zh_CN'))
        self._data = data
        self._msg = resmsg.Msg[self.lang].get(code, None)
        self._code = code

    def update(self, code=None, data=None, msg=None):
        """
        更新默认响应文本
        参数：
            code：响应编码
            data：响应数据
            msg：响应消息
        """
        if code is not None:
            self._code = code
            self._msg = resmsg.Msg[self.lang].get(code, None)
        if data is not None:
            self._data = data
        if msg is not None:
            self._msg = msg

    def add_field(self, name=None, value=None):
        """
        在响应文本中加入新的字段
        参数：
            name：字段名
            value：值
        """
        if name is not None and value is not None:
            self.__dict__[name] = value  # self.__dict__为类自带的属性，self.xxx都存储在这个属性里

    @property
    def data(self):
        """
        响应数据
        """
        payload = self.__dict__
        payload["data"] = payload.pop("_data")
        payload["msg"] = payload.pop("_msg")
        payload["code"] = payload.pop("_code")
        response = jsonify(payload)  # jsonify返回一个flask Response对象, 默认状态码为200
        return response

