# -*- coding: UTF-8 -*-

class APIMixin(object):
    @staticmethod
    def to_collection_dict(resource, **kwargs):
        """
        查询结果转换成字典格式。
        参数：
            resource：分页后的数据
        """
        data = [item.to_dict() for item in resource.items]
        return data

    def from_dict(self, data):
        """
            修改信息
        """
        for field in data:
            if hasattr(self, field):
                if data[field] == '':
                    #print(field)
                    # 空值的列，设置为None
                    setattr(self, field, '')
                else:
                    setattr(self, field, data[field])