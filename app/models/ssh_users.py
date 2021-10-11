# -*- coding: UTF-8 -*-
from app.utils.model import APIMixin
from app import db
from datetime import datetime
from sqlalchemy.dialects.mysql import TINYINT
from app.utils import pscrypt

class SshUsers(APIMixin, db.Model):
    """
    ssh user表
    """
    id = db.Column(db.Integer, primary_key=True, comment="id")
    name = db.Column(db.String(128), nullable=False, comment='名称')
    ssh_user = db.Column(db.CHAR(30), nullable=False, comment="ssh用户")
    ssh_password = db.Column(db.CHAR(255), comment="ssh密码")
    private_key = db.Column(db.Text, comment='密钥')
    remark = db.Column(db.String(256), nullable=False, default='', comment='备注')
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='添加时间')
    state = db.Column(TINYINT, nullable=False, default=1, comment='用户状态, 0: 禁用，1：启用')

    def __repr__(self):
        return '<SshUser {}>'.format(self.name)

    def set_password(self, password):
        self.ssh_password = pscrypt.encrypt(password)

    def set_private_key(self, private_key):
        self.private_key = pscrypt.encrypt(private_key)

    def get_password(self, password):
        return pscrypt.decrypt(password)

    def to_dict(self):
        """
        生成字典格式，默认不返回密码跟密钥，也不提供查询密码的接口。
        """
        data = {
            'ssh_id': self.id
            , 'ssh_name': self.name
            , 'ssh_user': self.ssh_user
            , 'remark': self.remark
        }
        return data

    def from_dict(self, data):
        """
            修改信息
        """
        for field in data:
            if hasattr(self, field):
                if field == 'ssh_password':
                    if data.get(field):
                        self.set_password(data[field])
                    continue
                if field == 'private_key':
                    if data.get(field):
                        self.set_private_key(data[field])
                    continue
                setattr(self, field, data[field])
