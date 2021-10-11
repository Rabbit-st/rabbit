#-*-coding:utf-8-*-

from flask import current_app

class REDIS(object):
    @staticmethod
    def _cli():
        if not current_app.redis:
            return False
        else:
            return current_app.redis

    @classmethod
    def set(cls, key, value, expire=None):
        """
        写入键值对
        """
        rs = cls._cli()
        if not expire:
            expire = current_app.config.get('REDIX_EXPIRE', 500)

        try:
            rs.set(key, value, ex=expire)
        except Exception as e:
            raise e
        
        return True

    @classmethod
    def get(cls, key):
        """
        读取键值
        """
        rs = cls._cli()
        value = rs.get(key)
        return value

    @classmethod
    def delete(cls, key):
        """
        删除键值
        """
        rs = cls._cli()
        try:
            rs.delete(key)
        except Exception as e:
            return False
        return True
