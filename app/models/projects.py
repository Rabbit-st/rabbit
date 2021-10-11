# -*- coding: UTF-8 -*-
from app.utils.model import APIMixin
from app import db
from datetime import datetime
from sqlalchemy.dialects.mysql import TINYINT

class Projects(APIMixin, db.Model):
    """服务器项目表"""
    id = db.Column(db.Integer, primary_key=True, comment='项目id')
    name = db.Column(db.String(128), nullable=False, comment='项目名称')
    remark = db.Column(db.String(256), nullable=False, default='', comment='备注')
    state = db.Column(TINYINT, nullable=False, default=1, comment='状态，1启用，0禁用')
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now,comment='添加时间')
    update_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='修改时间')

    def __repr__(self):
        return '<Project {}>'.format(self.name)

    def to_dict(self):
        """生成字典格式"""
        data = {
            'id': self.id,
            'name': self.name,
            'remark': self.remark,
            'state': self.state,
        }
        return data