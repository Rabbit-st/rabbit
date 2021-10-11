from flask import current_app

class ES(object):
    """
    elasticsearch操作
    """
    @staticmethod
    def _es():
        if not current_app.elasticsearch:
            return False
        else:
            return current_app.elasticsearch

    @classmethod
    def chinese_put_mapping(cls, ndex, field):
        """
        设置字段分词器为ik_max_word(中文)，指定搜索分词器为ik_max_word（中文）。
        参数：
            index：索引名
            field：字段名
        """
        es = cls._es()
        if not es:
            return 
        if es.indices.exists(index):
            mapping = {
                'properties': {
                    field: {
                        'type': 'text',
                        'analyzer': 'ik_max_word',
                        'search_analyzer': 'ik_max_word'
                    }
                }
            }
            result = es.put_mapping(index=index, body=mapping)
            if result.get('acknowledged', False):
                return False
            return True

    @classmethod
    def create_index(cls, index, mapping=False):
        """
        创建index。
        参数：
            index：index
            mapping：description字段添加中文分词器
        """
        es = cls._es()
        if not es:
            return 
        if not es.indices.exists(index):
            es.indices.create(index=index, ignore=400)
            if mapping:
                cls.chinese_put_mapping(index, 'description')

    @classmethod
    def add_to_index(cls, index, model):
        # 添加/修改。添加一个已有ID的数据，会直接更新数据
        es = cls._es()
        if not es:
            return 
        payload = {}
        for field in model.__searchable__:
            # 可被搜索的列都添加到es中
            payload[field] = getattr(model, field)
        es.index(index=index, id=model.hostid, body=payload) 

    @classmethod
    def remove_from_index(cls, index, model):
        # 删除索引
        es = cls._es()
        if not es:
            return 
        es.delete(index=index, id=model.id)

    @classmethod
    def query_index(cls, index, query, page, per_page):
        # 查询索引
        es = cls._es()
        if not es:
            return 
        search = es.search(
            index=index,
            body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
                'from': ( page - 1)* per_page, 'size': per_page})  # multi_match：跨多个字段查询。
        ids = [int(hit['_id']) for hit in search['hits']['hits']]
        return ids, search['hits']['total']['value']
