#!/usr/bin/env python3
#-*-coding: utf-8 -*-
# author: zzh
# time: 2020-10-23
# 模块：pycryptodome==3.8.0
# 用途：密码加密解密

import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from config import Config

key = 'gOQXANLPbxwUy7s9'.encode('utf-8')
mode = AES.MODE_CBC
iv = 'PLs0gG3wEhs*tfZr'.encode('utf-8')

class DecodeAES(object):
    """密钥生成器"""

    @staticmethod
    def encode(data):
        """加密"""
        cipher = AES.new(key, mode, iv)
        pad_pkcs7 = pad(str(data).encode('utf-8'), AES.block_size, style='pkcs7')
        result = base64.encodebytes(cipher.encrypt(pad_pkcs7))
        encrypted_text = str(result, encoding='utf-8').replace('\n', '')
        return encrypted_text

    @staticmethod
    def decode(data):
        """解密"""
        cipher = AES.new(key, mode, iv)
        base64_decrypted = base64.decodebytes(data.encode('utf-8'))
        una_pkcs7 = unpad(cipher.decrypt(base64_decrypted), AES.block_size, style='pkcs7')
        decrypted_text = str(una_pkcs7, encoding='utf-8')
        return decrypted_text

    def test(self):
        data1 = 'sdasdaswqm12321msdaDSF@#@#!##'
        data2 = 'fViIadHJfic2MS7u/qWA6XHF1s7sNGBq4cRxcPdqPps='
        print('加密结果：', self.encode(data1))
        print('解密结果：', self.decode(data2))

def process_key(key):
    """
    返回32 bytes 的key
    """
    if not isinstance(key, bytes):
        key = bytes(key, encoding="utf-8")

    if len(key) >= 32:
        return key[:32]
    
    return pad(key, 32)

def process_text(text):
    if isinstance(text, str):
        text = bytes(text, encoding='utf-8')
    if isinstance(text, bytes):
        text = text.decode().encode('utf-8')

    return text

class PrivateKeyAES(object):
    """
    密钥加密、解密
    """
    def __init__(self, key):
        self.key = process_key(key)
        
    def encrypt(self, text):
        """
        加密text，并将 header, nonce, tag (3*16 bytes, base64后变为 3*24 bytes)
        附在密文前。解密时要用到。
        """
        header = get_random_bytes(16)
        cipher = AES.new(self.key, AES.MODE_GCM)
        cipher.update(header)
        ciphertext, tag = cipher.encrypt_and_digest(process_text(text))
        
        result = []
        for byte_data in (header, cipher.nonce, tag, ciphertext):
            result.append(base64.b64encode(byte_data).decode('utf-8'))
        
        return ''.join(result)
    
    def decrypt(self, text):
        """
        提取header, nonce, tag并解密text。
        """
        metadata = text[:72]
        header = base64.b64decode(metadata[:24])
        nonce = base64.b64decode(metadata[24:48])
        tag = base64.b64decode(metadata[48:])
        ciphertext = base64.b64decode(text[72:])

        cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)

        cipher.update(header)
        plain_text_bytes = cipher.decrypt_and_verify(ciphertext, tag)
        return plain_text_bytes.decode('utf-8')

pscrypt = PrivateKeyAES(Config.SECRET_KEY)
