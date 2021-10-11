# -*- coding: utf-8 -*-

from flask_sqlalchemy import BaseQuery
from flask import request

class Query(BaseQuery):
    """
        query添加layui表格分页方法
    """
    def layui_paginate(self):
        """
            layui表格分页
            page 页数
            limit  每页数量
        """
        return self.paginate(page=request.args.get('page',1, type=int),
                             per_page=request.args.get('limit',10,type=int),
                             error_out=False)
