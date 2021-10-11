#!/usr/bin/env python3
#-*- coding:utf-8 -*-
# author: zzh
# time: 2020-07-20
# ansible==2.8.0
# 参考1：https://docs.ansible.com/ansible/latest/dev_guide/developing_api.html#python-api-2-0
# 参考2：https://blog.51cto.com/jackor/2340880
# 参考3：https://www.cnblogs.com/stones/p/8252731.html

import os
import tempfile
import shutil
from pprint import pprint
from collections import defaultdict
from ansible import context
from ansible.cli import CLI
from ansible.module_utils.common.collections import ImmutableDict
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.vars.manager import VariableManager
from ansible.plugins.callback import CallbackBase
from ansible.plugins.callback.default import CallbackModule
from ansible.plugins.callback.minimal import CallbackModule as CMDCallBackModule
from ansible.playbook.play import Play
import ansible.constants as C

C.HOST_KEY_CHECKING = False # 首次连接不检测key

def get_default_options():
    options = dict(
            syntax=False, 
            connection='ssh',
            module_path=None, 
            forks=30, 
            remote_user='root', 
            timeout=30, 
            remote_tmp='/tmp/.ansible',
            ssh_common_args=None, 
            ssh_extra_args=None, 
            sftp_extra_args=None, 
            scp_extra_args=None,
            verbosity=True, 
            check=False, 
            start_at_task=None,
            host_key_checking=False,
            system_warnings = True
        )
    return options

class CallbackMixin:
    def __init__(self, display=None):
        # result_raw example: {
        #   "ok": {"hostname": {"task_name": {}，...},..},
        #   "failed": {"hostname": {"task_name": {}..}, ..},
        #   "unreachable: {"hostname": {"task_name": {}, ..}},
        #   "skipped": {"hostname": {"task_name": {}, ..}, ..},
        # }
        # results_summary example: {
        #   "contacted": {"hostname": {"task_name": {}}, "hostname": {}},
        #   "dark": {"hostname": {"task_name": {}, "task_name": {}},...,},
        #   "success": True
        # }
        self.results_raw = dict(
            ok=defaultdict(dict),
            failed=defaultdict(dict),
            unreachable=defaultdict(dict),
            skippe=defaultdict(dict),
        )
        self.results_summary = dict(
            contacted=defaultdict(dict),
            dark=defaultdict(dict),
            success=True
        )
        self.results = {
            'raw': self.results_raw,
            'summary': self.results_summary,
        }
        super().__init__()
        if display:
            self._display = display

        cols = os.environ.get("TERM_COLS", None)
        self._display.columns = 79
        if cols and cols.isdigit():
            self._display.columns = int(cols) - 1

    def display(self, msg):
        self._display.display(msg)

    def gather_result(self, t, result):
        self._clean_results(result._result, result._task.action)
        host = result._host.get_name()
        task_name = result.task_name
        task_result = result._result

        self.results_raw[t][host][task_name] = task_result
        self.clean_result(t, host, task_name, task_result)


class AdHocResultCallback(CallbackMixin, CallbackModule, CMDCallBackModule):
    """
    Task result Callback
    """
    context = None

    def clean_result(self, t, host, task_name, task_result):
        contacted = self.results_summary["contacted"]
        dark = self.results_summary["dark"]

        if task_result.get('rc') is not None:
            cmd = task_result.get('cmd')
            if isinstance(cmd, list):
                cmd = " ".join(cmd)
            else:
                cmd = str(cmd)
            detail = {
                'cmd': cmd,
                'stderr': task_result.get('stderr'),
                'stdout': task_result.get('stdout'),
                'rc': task_result.get('rc'),
                'delta': task_result.get('delta'),
                'msg': task_result.get('msg', '')
            }
        else:
            detail = {
                "changed": task_result.get('changed', False),
                "msg": task_result.get('msg', '')
            }

        if t in ("ok", "skipped"):
            contacted[host][task_name] = detail
        else:
            dark[host][task_name] = detail

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.results_summary['success'] = False
        self.gather_result("failed", result)

        if result._task.action in C.MODULE_NO_JSON:
            CMDCallBackModule.v2_runner_on_failed(self,
                result, ignore_errors=ignore_errors
            )
        else:
            super().v2_runner_on_failed(
                result, ignore_errors=ignore_errors
            )

    def v2_runner_on_ok(self, result):
        self.gather_result("ok", result)
        if result._task.action in C.MODULE_NO_JSON:
            CMDCallBackModule.v2_runner_on_ok(self, result)
        else:
            super().v2_runner_on_ok(result)

    def v2_runner_on_skipped(self, result):
        self.gather_result("skipped", result)
        super().v2_runner_on_skipped(result)

    def v2_runner_on_unreachable(self, result):
        self.results_summary['success'] = False
        self.gather_result("unreachable", result)
        super().v2_runner_on_unreachable(result)

    def display_skipped_hosts(self):
        pass

    def display_ok_hosts(self):
        pass

    def display_failed_stderr(self):
        pass

    def set_play_context(self, context):
        # for k, v in context._attributes.items():
        #     print("{} ==> {}".format(k, v))
        if self.context and isinstance(self.context, dict):
            for k, v in self.context.items():
                setattr(context, k, v)

class AnsibleResultCallback(CallbackBase):
    """
        执行ansible playbook 回调类
    """

    def __init__(self, display=None, options=None):
        super().__init__(display, options)
        self.playbook_results = []  # 所有的输出结果
        self.error_num = 0  # 执行状态码
        self.print_len_size = 80
        self.isdisplay = True # 是否输出执行信息

    def v2_playbook_on_play_start(self, play):
        """
            playbook 信息
        """
        msg = 'PLAY [{0}]'.format(play.get_name())
        msg = '{0}{1}'.format(msg, '*' * (self.print_len_size-len(msg)))
        msg += '\n'
        self.print_msg(msg)

    def v2_playbook_on_task_start(self, task, is_conditional):
        """
            task 信息
        """
        msg = 'TASK [{0}]'.format(task.get_name())
        msg = '{0}{1}'.format(msg, '*' * (self.print_len_size-len(msg)))
        self.print_msg(msg)

    def v2_runner_on_skipped(self, result):
        if C.DISPLAY_SKIPPED_HOSTS:
            host = result._host.get_name()
            self.runner_on_skipped(host, self._get_item_label(getattr(result._result, 'results', {})))
            if result._result.get('rc') == None:
                msg = 'skipping: [{0}]'.format(host)
            elif result._result.get('rc') == 0:
                msg = 'skipping_0: [{0}]'.format(host)
            else:
                msg = 'skipping_f: [{0}]'.format(host)
            self.print_msg(msg)

    def v2_runner_on_ok(self, result):
        host = result._host.get_name()
        if result._result.get('rc') == None:
            msg = 'OK: [{0}]'.format(host)
        elif result._result.get('rc') == 0:
            msg = 'changed: [{0}]'.format(host)
        else:
            msg = 'ok unknown : code {0}, [{1}]'.format(result._result.get('rc'), host)
        self.print_msg(msg)

    def v2_runner_on_unreachable(self, result):
        host = result._host.get_name()
        if result._result.get('rc') == None:
            msg = 'fatal: [{0}] unreachable! => {{'.format(host)
            for key in sorted(result._result.keys()):
                if str(key).startswith('_'):
                    continue
                msg += '"{0}": "{1}" '.format(key, result._result[key])
            msg += '}}'
        elif result._result.get('rc') == 0:
            msg = 'unreachable_0: [{0}]'.format(host)
        else:
            msg = 'unreachable unknown : code {0}, [{1}]'.format(result._result.get('rc'), host)
        self.print_msg(msg)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        host = result._host.get_name()
        if result._result.get('rc') in [1, 2, 3]:
            msg = 'fatal: [{0}] FAILED! => {{"changed": {1}, "stderr": "{2}"}}'.format(host, result._result.get('changed'), result._result.get('stderr'))
        else:
            msg = 'recode: {0} msg: {1}, {2}'.format(result._result.get('rc'), result._result.get('stderr', ''), result._result.get('msg', ''))
        if ignore_errors:
            msg += '\n...ignoring'
        self.print_msg(msg)

    def v2_playbook_on_stats(self, stats):
        """
            统计信息
        """
        hosts = stats.processed.keys()
        msg = 'PLAY RECAP '
        msg = '{0}{1}'.format(msg, '*' * (self.print_len_size - len(msg)))
        for h in hosts:
            msg += '\n{} {}'.format(h, stats.summarize(h))
            if stats.summarize(h)['failures'] or stats.summarize(h)['unreachable']:
                self.error_num = 1
        self.print_msg(msg)

    def print_msg(self, msg):
        if self.isdisplay:
            print(msg)
        self.playbook_results.append(msg)

class BaseInventory(InventoryManager):
    """
        动态生成Inventory类
    """
    loader_class = DataLoader

    def __init__(self, resource=None):
        """
            resource的数据格式是一个列表字典，比如：
                {
                    'group1':{
                        "hosts": [{"ip": "10.0.0.0", "port": "22", "username": "root", "password": "pass"}, ...]
                        "group_vars": {"var1", "var2", "var3", ...}
                    }
                }
            如果只传入一个列表，默认改列表内的所有主机属于default组，比如：
                [{"ip": "10.0.0.0", "port": "22", "username": "root", "password": "pass"}, ...]
            sources：自带的参数，inventory文件路径，可以指定一个，也可以以列表形式指定多个
        """
        self.loader = self.loader_class()
        super().__init__(loader=self.loader)
        self.resource = resource  #  列表字典
        self.dynamic_inventory()

    def dynamic_inventory(self):
        """
            生成动态inventory。如果传入的是列表，默认为default组
        """
        if isinstance(self.resource, list):
            self.parse_resource(self.resource, 'default')
        elif isinstance(self.resource, dict):
            for groupname, hosts_and_vars in self.resource.items():
                self.parse_resource(hosts_and_vars.get("hosts"), groupname, hosts_and_vars.get("group_vars"))

    def parse_resource(self, hosts, group_name, group_vars=None):
        """
            resoure解析成ansible可以读取的内容
        """
        # 添加主机组
        self.add_group(group_name)
    
        # 添加主机组变量
        if group_vars:
            for key, value in group_vars.items():
                self.groups[group_name].set_variable(key, value)

        for host in hosts:
            ip = host.get('ip')
            port = host.get('port')
            # 添加到主机组
            self.add_host(ip, group_name, port)
    
            username = host.get('username')
            password = host.get('password')
            ssh_key = host.get('ssh_key')
            
            # 生成ansible主机变量
            self.get_host(ip).set_variable('ansible_ssh_host', ip)
            self.get_host(ip).set_variable('ansible_ssh_port', port)
            self.get_host(ip).set_variable('ansible_ssh_user', username)
            if ssh_key:
                self.get_host(ip).set_variable('ansible_ssh_private_key_file', ssh_key) # key 文件路径
            else:
                self.get_host(ip).set_variable('ansible_ssh_pass', password)

            # 设置其他变量
            for key, value in host.items():
                if key not in ["ip", "port", "username", "password", "ssh_key"]:
                    self.get_host(ip).set_variable(key, value)

class AnsibleRunner(object):
    """执行ansible"""
    loader_class = DataLoader
    def __init__(self, inventory=None, options=None):
        """
            resource: dict / list 
                {
                    'group1':{
                        "hosts": [{"ip": "10.0.0.0", "port": "22", "username": "root", "password": "pass"}, ...]
                        "group_vars": {"var1", "var2", "var3", ...}
                    }
                }
            如果只传入一个列表，默认改列表内的所有主机属于default组，比如：
                [{"ip": "10.0.0.0", "port": "22", "username": "root", "password": "pass"}, ...]
            sources：自带的参数，inventory(hosts)文件路径，可以指定一个，也可以列表形式指定多个。
            options：ansible参数
        """
        self.exit_code = 0
        self.options = options
        self.inventory = inventory
        self.loader = self.loader_class()
        if not self.options:
            self.options = get_default_options()

        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory, version_info=CLI.version_info(gitinfo=False))
        self.results_callback = None   # 信息回调
        self._validate

    @property
    def _validate(self):
        """验证playbook是否存在，default是否存在"""
        pass

    def adhoc_runner(self, tasks, hosts, play_name='Ansible Ad-hoc', gather_facts='no',display=True):
        """
            执行单独的模块
            参数：
                tasks: [{'action': {'module': 'shell', 'args': 'ls'}, ...}, ]
                hosts: all, ip1,ip2,ip3, or others
        """

        play_source = {
            'name': play_name
            ,'hosts': hosts
            ,'gather_facts': gather_facts
            ,'tasks': tasks
        }
        self.results_callback = AdHocResultCallback()
        self.results_callback.display = display  # 是否打印执行信息
        context.CLIARGS = ImmutableDict(self.options)
        
        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)
        tqm = None
        try:
            tqm = TaskQueueManager(
                    inventory=self.inventory,
                    variable_manager=self.variable_manager,
                    loader=self.loader,
                    passwords={},
                    stdout_callback=self.results_callback,
                )
            tqm.run(play)
        finally:
            if tqm is not None:
                tqm.cleanup()

        return self.results_callback
        #shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)
        
    def exec_playbook(self, playbook_path, display=True, extra_vars=None):
        """
            执行ansible playbook。
            参数：
                playbook_path: playbook文件路径
                display： 是否打印执行结果到stdout
                exitra_vars：playbook变量
        """
        self.results_callback = AnsibleResultCallback()
        self.results_callback.isdisplay = display
        context.CLIARGS = ImmutableDict(self.options)

        if extra_vars:
            self.variable_manager._extra_vars = extra_vars

        pbex = PlaybookExecutor(playbooks=playbook_path, inventory=self.inventory, variable_manager=self.variable_manager, loader=self.loader, passwords={})
        pbex._tqm._stdout_callback = self.results_callback 
        pbex.run()
        
        if self.results_callback.error_num:
            self.exit_code = 1

    @staticmethod
    def get_inventory(hosts_file):
        """获取inventory主机信息"""

        loader = DataLoader()
        inventorys = MyInventory(loader = loader, sources=hosts_file)
        
        return inventorys

if __name__=='__main__':
    resource = [{
        'ip': '192.168.3.53'
        ,'port': 22
        ,'username': 'root'
        ,'password': 'fzfyhd!@#2306'
    }]
    inventory = BaseInventory(resource=resource)
    ans = AnsibleRunner(inventory)
    tasks = [{'action': {'module': 'shell', 'args': 'ls'}}]
    ans.adhoc_runner(tasks, '192.168.3.53')
