# -*- coding: UTF-8 -*-

import os
import random
import string
import time
import pandas as pd
from .pscrypt import pscrypt

ALLOWED_EXTENSIONS = {'csv', 'txt'}
CSV_FORMAT = {
                'host_ip': 'ip',
                'host_name': '主机名',
                'city': '地区', 
                'ssh_port': 'ssh_port',
                'ssh_id': 'ssh_id', 
                'project_id': '项目id',
                'site_name': '站点域名',
                'remark': '备注'
            }

def random_filename():
    nums = 5
    re = ''.join(random.choice(string.ascii_lowercase) for _ in range(nums))
    return 'opsdev_{}_{}.csv'.format(int(time.time()),re)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_format(line):
    if len(line) != len(CSV_FORMAT):
        return False
    for index, item in enumerate(line):
        if CSV_FORMAT[index] != item:
            return False
    return True

def remove_duplicate(data, key):
    """
    列表去重
    :param data: list, [{'host_ip':'102.168.3.1'},{'host_ip':'102.168.3.1'}]
    :param key: str/list, host_ip
    :return: list, [{'host_ip':'102.168.3.1'}]
    """
    new_data =[]  # 新的列表
    values = []   # 当前已有的键值
    if isinstance(key, list):
        for k in key:
            data = remove_duplicate(data, k)
        return data
    else:
        for d in data:
            if key in d.keys():
                if d[key] not in values:
                    new_data.append(d)
                    values.append(d[key])
            else:
                new_data.append(d) # 不存在的key，返回原列表
    return new_data

def csv_to_list(path, filename, exist_data):
    """
    读取csv文件，将数据转换为列表
    path：csv文件目录
    filename：csv文件名
    exist_data：已有的ip数据
    """
    result = {'success':[], 'existing': []}
    ips = []
    hosts_name = []
    for ip in exist_data:
        ips.append(ip.host_ip)
        hosts_name.append(ip.host_name)
    print(ips)
    print(hosts_name)
    data = pd.read_csv(os.path.join(path, filename), encoding='gbk')
    if 0 in data.shape:
        return False, '没有数据'
    data_dict = data.fillna('').to_dict()  # 缺失值替换成空值

    # 先判断列数对不对
    if data.shape[1] != len(CSV_FORMAT):
        return False, '数据格式不对'

    # 判断列对不对
    if data.shape[1] == len(CSV_FORMAT):
        for value in CSV_FORMAT.values():
            if data_dict.get(value, 0) == 0:
                return False, '数据格式不对'

    # 生成list
    for num in range(data.shape[0]):
        is_add = 1
        d = {}
        for key in CSV_FORMAT.keys():
            if key == 'host_ip' and data_dict[CSV_FORMAT[key]][num] in ips:
                is_add = 0
            if key == 'host_name' and data_dict[CSV_FORMAT[key]][num] in hosts_name:
                is_add = 0
            # 密码字段加密存储
            #if key == 'ssh_password':
            #    d[key] = pscrypt.encrypt(data_dict[CSV_FORMAT[key]][num])
            #else:
            d[key] = data_dict[CSV_FORMAT[key]][num]
        if is_add:
            result['success'].append(d)
        else:
            result['existing'].append(d)
    print(result)
    if not result['success']:
        return False,'所有IP都已存在'
    result['success'] = remove_duplicate(result['success'], ['host_ip','host_name'])
    return True, result
