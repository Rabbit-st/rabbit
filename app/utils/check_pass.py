#-*- coding:utf-8 -*-
#

import re

class CheckPass(object):
    """
        密码复杂度检查
    """
    @staticmethod
    def check_length(password):
        """长度"""
        if len(password) < 9:
            return False
        return True

    @staticmethod
    def check_number_exists(password):
        """数字"""
        pattern = '\d'
        if not re.search(pattern, password):
            return False
        return True

    @staticmethod
    def check_letter_exists(password):
        """大小写字母"""
        pattern = '\w'
        if not re.search(pattern, password):
            return False
        return True

    @staticmethod
    def check_special_exists(password):
        """特殊字符"""
        pattern = '\W'
        if not re.search(pattern, password):
            return False
        return True

def check_password(password):
    if not CheckPass.check_length(password):
        return '密码长度小于9位'
    if not CheckPass.check_number_exists(password):
        return '密码必须包含数字'
    if not CheckPass.check_letter_exists(password):
        return '密码必须包含大小写字母'    
    if not CheckPass.check_special_exists(password):
        return '密码必须包含特殊字符'
    return 1
