# -*- coding:utf-8 -*-
#

from io import StringIO
import paramiko

def ssh_key_string_to_obj(text, password=None):
    """key字符转换"""
    key = None
    try:
        key = paramiko.RSAKey.from_private_key(StringIO(text), password=password)
    except paramiko.SSHException:
        pass

    try:
        key = paramiko.DSSKey.from_private_key(StringIO(text), password=password)
    except paramiko.SSHException:
        pass
    return key

def validate_ssh_private_key(text, password=None):
    """
    private key字符格式校验
    """
    if isinstance(text, bytes):
        try:
            text = text.decode("utf-8")
        except UnicodeDecodeError:
            return False

    key = ssh_key_string_to_obj(text, password=password)
    if key is None:
        return False
    else:
        return True
