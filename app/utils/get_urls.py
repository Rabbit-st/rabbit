#-*- coding:utf-8 -*-
# 获取所有的url

data = []
for rule in current_app.url_map.iter_rules():
    permissions = Permission.methods_to_code(rule.methods)
    if '/api/' in str(rule) and '<' not in str(rule) and '>' not in str(rule):
        for permission in permissions:
            d = {}
            d['url'] = str(rule)
            d['permission'] = permission
            d['type'] = 1
            data.append(d)
    elif '/api/hosts/<int:id>' == str(rule):
        for host in Hosts.query.all():
            for permission in permissions:
                d = {}
                d['url'] = '/api/hosts/' + str(host.hostid)
                d['permission'] = permission
                d['type'] = 0
                data.append(d)
    elif '/api/user/<int:id>' == str(rule):
        for user in User.query.all():
            for permission in permissions:
                d = {}
                d['url'] = '/api/user/' + str(user.id)
                d['permission'] = permission
                d['type'] = 2
                data.append(d)
    elif '/api/role/<int:id>' == str(rule):
        for role in Role.query.all():
            for permission in permissions:
                d = {}
                d['url'] = '/api/role/' + str(role.id)
                d['permission'] = permission
                d['type'] = 3
                data.append(d)
    elif '/api/ssh_user/<int:id>' == str(rule):
        for suser in SshUsers.query.all():
            for permission in permissions:
                d = {}
                d['url'] = '/api/ssh_user/' + str(suser.ssh_id)
                d['permission'] = permission
                d['type'] = 4
                data.append(d)
    elif '/api/projects/<int:id>' == str(rule):
        for project in Projects.query.all():
            for permission in permissions:
                d = {}
                d['url'] = '/api/projects/' + str(project.projectid)
                d['permission'] = permission
                d['type'] = 5
                data.append(d)
