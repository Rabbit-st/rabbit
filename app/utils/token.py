#-*-coding:utf-8-*-

from app.utils import REDIS
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                        BadSignature, SignatureExpired)
from config import Config
            
class Token(object):
    @staticmethod
    def verify_auth_token(token):
        """验证token是否有效"""
        rs_status = 1
        username = None

        # 在黑名单的
        try:
            u = REDIS.get('black:{}'.format(token))
            if u:
                return False
        except Exception as e:
            rs_status = 0
            pass

        # 缓存有的
        if rs_status:
            try:
                username = REDIS.get(token)
                if username:
                    return True
            except Exception as e:
                rs_status = 0
                pass # 很大可能redis挂了, 记录日志

        s = Serializer(
                secret_key = Config.SECRET_KEY,
                salt = Config.AUTH_SALT,
            )
        try:
            data = s.loads(token)
        except SignatureExpired:
            #raise make_response(jsonify({'msg': 'token is expired'}),1003)
            return False
        except BadSignature as e:
            encoded_payload = e.payload
            if encoded_payload is not None:
                try:
                    s.load_payload(encoded_payload)
                except BadData:
                    return False
                    #raise make_response(jsonify({'msg': 'token is tampered'}), 1002)
            #raise make_response(jsonify({'msg':'badSignature of token'}), 1002)
            return False
        except:
            return False
            #raise make_response(jsonify({'msg':'wrong token with unknown reason'}), 1004)
        if 'id' not in data or 'username' not in data:
            return False
            #raise make_response(jsonify({'msg':'illegal payload inside'}), 1005)
        # 缓存没找到，但是解析成功，格式正确的，加入到缓存中
        if rs_status:
            REDIS.set(token, data['username'], Config.TOKEN_EXPIRE)
        return True
