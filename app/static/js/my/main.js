function savelStorage(key, value){
    if (window.localStorage) {
        var storage=window.localStorage;
        storage.setItem(key, value);
        return true;
    }else{
        return false;
    }
}
function savelStorageJson(data){
    if (window.localStorage) {
        var storage=window.localStorage;
        var d=JSON.stringify(data);
        storage.setItem("data", d);
        return true;
    }else{
        return false;
    }
}
function getToken(){
    if (window.localStorage) {
        var storage=window.localStorage;
        var token=storage.getItem("token");
        if(typeof token == "undefined" || token == null || token == ""){
            return false;
        }else{
            return token;
        }
    }
}
function getlStorage(key){
  if (window.localStorage) {
    var name=window.localStorage.getItem(key);
    if(typeof name == "undefined" || name == null || name == ""){
      return false;
    }else{
      return name;
    }
  }
}
function checkIP(value){
    var reg=/^(\d+)\.(\d+)\.(\d+)\.(\d+)$/;  // IP正则表达式
    if (reg.test(value)){
        if ( RegExp.$1<256 && RegExp.$2<256 && RegExp.$3<256 && RegExp.$4 < 256){
            return true;
        }else {
            return false;
        }
    }
}
function checkPhone(phone){
    if(!(/^1\d{10}$/.test(phone))){ 
        return false; 
    }else {
        return true;
    }
}
function logout(){
  $.ajax({
    url:'/api/tokens',
    type: 'delete',
    headers: {
        "Authorization": 'Bearer ' + getToken()
    },
    success:function(data){
        window.location.href="/login";
    }
  });
}
// ssh_users 表格数据加载
function ssh_users_render(tbobj, url){
  tbobj.render({
    elem: '#ssh_users-table'
    ,url: url
    ,headers: {"Authorization": 'Bearer ' + getToken()}
    ,method: 'get'
    ,title: '项目列表'
    ,cols: [[
      {field:'ssh_id', title:'ID'}
      ,{field:'ssh_name', title:'名称'}
      ,{field:'ssh_user', title:'ssh user'}
      ,{field:'description', title:'备注'}
      ,{field: 'oper',fixed: 'right', title:'操作', toolbar: '#toolbaroper'}
    ]]
    ,page: true
  });
}
// users 表格数据加载
function users_render(tbobj, url){
  tbobj.render({
    elem: '#users-table'
    ,url: url
    ,headers: {"Authorization": 'Bearer ' + getToken()}
    ,method: 'get'
    ,title: '所有用户列表'
    ,cols: [[
      {field:'id', hide:true}
      ,{field:'username', title:'用户名', templet:tpluser}
      ,{field:'email', title:'邮箱'}
      ,{field:'role', title:'角色'}
      ,{field:'phone', title:'手机号'}
      ,{field:'description', title:'备注'}
      ,{field:'last_seen', title:'最后登录时间'}
      ,{field: 'state', title:'状态', toolbar: '#toolbarswitchtp'}
      ,{field: 'oper',fixed: 'right', title:'操作', toolbar: '#toolbaroper'}
    ]]
    ,page: true
  });
}
// scripts表格数据加载
function scripts_render(tbobj, url){
  tbobj.render({
    elem: '#scripts'
    ,url: url
    ,headers: {"Authorization": 'Bearer ' + getToken()}
    ,method: 'get'
    ,title: '所有脚本列表'
    ,cols: [[
      {field:'id', hide:true}
      ,{field:'vid', hide:true}
      ,{field:'name', title:'名称', templet:tplscript}
      ,{field:'lang', title:'脚本语言'}
      ,{field:'classifying', title:'场景标签'}
      ,{field:'version', title:'线上版本'}
      ,{field:'username', title:'更新人'}
      ,{field:'update_time', title:'更新时间'}
      ,{field: 'oper',fixed: 'right', title:'操作', toolbar: '#toolbaroper'}
    ]]
    ,page: true
  });
}
// 脚本版本管理
function script_version_render(tbobj, url, elem){
  tbobj.render({
    elem: elem
    ,url: url
    ,headers: {"Authorization": 'Bearer ' + getToken()}
    ,method: 'get'
    ,title: '脚本版本'
    ,cols: [[
      {field:'id', hide:true}
      ,{field:'version', title:'版本号', templet: tplscript}
      ,{field:'update_user', title:'更新人'}
      ,{field:'update_time', title:'更新时间'}
      ,{field: 'state', title:'状态' ,toolbar: '#toolbarswitchtp'}
      ,{field: 'oper',fixed: 'right', title:'操作', toolbar: '#toolbaroper'}
    ]]
    ,page: true
  });
}
// user 表格数据加载
function user_render(tbobj, url){
  tbobj.render({
    elem: '#users-table'
    ,url: url
    ,headers: {"Authorization": 'Bearer ' + getToken()}
    ,method: 'get'
    ,title: '用户列表'
    ,skin: 'nob'
    ,cols: [[
      {field:'id', hide:true}
      ,{field:'role_id', hide:true}
      ,{field:'username', templet:tpluser}
      ,{field:'email'}
      ,{field:'last_seen'}
      ,{field:'description'}
      ,{field: 'state', toolbar: '#toolbarswitchtp'}
      ,{field: 'oper',fixed: 'right', toolbar: '#toolbaroper'}
    ]]
    ,page: true
  });
}
/* 收件人表格加载 */
function mail_config_render(tbobj, url){
  tbobj.render({
    elem: '#alarm-mail-config'
    ,url: url
    ,headers: {"Authorization": 'Bearer ' + getToken()}
    ,method: 'get'
    ,title: '收件人列表'
    ,cols: [[
      {field:'id', hide:true}
      ,{field:'groupname', title:'组名'}
      ,{field:'email',title: '邮箱'}
      ,{field:'expire', title: '失效时间'}
      ,{field: 'issend', title:'状态' ,toolbar: '#toolbarswitchtp'}
      ,{field: 'oper',fixed: 'right', toolbar: '#toolbaroper'}
    ]]
    ,page: true
  });
}
// roles 表格数据加载
function roles_render(tbobj, url){
  tbobj.render({
    elem: '#roles-table'
    ,url: url
    ,headers: {"Authorization": 'Bearer ' + getToken()}
    ,method: 'get'
    ,title: '角色列表'
    ,cols: [[
      {field:'id', hide:true}
      ,{field:'role', title:'角色名', templet:tplrole}
      ,{field:'type', title: '类型'}
      ,{field:'createtime', title: '创建时间'}
      ,{field:'description', title: '备注'}
      ,{field:'users', title: '关联的用户'}
      ,{field: 'oper',fixed: 'right', toolbar: '#toolbaroper', title: '操作'}
    ]]
    ,page: true
  });
}
// role_hosts 表格加载
function rh_render(tbobj, url){
  tbobj.render({
    elem: '#role-hosts'
    ,url: url
    ,headers: {"Authorization": 'Bearer ' + getToken()}
    ,method: 'get'
    ,title: '角色主机权限列表'
    ,cols: [[
      {field:'id', hide:true}
      ,{field:'ip', title:'主机'}
      ,{field:'permission', title:'权限'}
      ,{field: 'oper',fixed: 'right', toolbar: '#toolbaroper', title: '操作'}
    ]]
    ,page: true
  });
}
// role_urls 表格加载
function rurl_render(tbobj, url){
  tbobj.render({
    elem: '#role-urls'
    ,url: url
    ,headers: {"Authorization": 'Bearer ' + getToken()}
    ,method: 'get'
    ,title: '角色url权限列表'
    ,cols: [[
      {field:'id', hide:true}
      ,{field:'url', title:'url'}
      ,{field:'permission', title:'权限'}
      ,{field: 'oper', fixed: 'right', toolbar: '#toolbaroper', title: '操作'}
    ]]
    ,page: true
  });
}
// role_users 表格加载
function ruser_render(tbobj, url){
  tbobj.render({
    elem: '#role-users'
    ,url: url
    ,headers: {"Authorization": 'Bearer ' + getToken()}
    ,method: 'get'
    ,title: '角色用户列表'
    ,cols: [[
      {field:'id', hide:true}
      ,{field:'username', title:'用户'}
      ,{field:'description', title:'备注'}
      ,{field: 'oper', fixed: 'right', toolbar: '#toolbaroper', title: '操作'}
    ]]
    ,page: true
  });
}
// 项目表格数据加载
function projects_render(tbobj, url){
  tbobj.render({
    elem: '#projects-table'
    ,url: url
    ,headers: {"Authorization": 'Bearer ' + getToken()}
    ,method: 'get'
    ,title: '项目列表'
    ,cols: [[
      {field:'projectid', title:'ID'}
      ,{field:'projectname', title:'项目名称'}
      ,{field:'description', title:'备注'}
      ,{field: 'oper',fixed: 'right', title:'操作', toolbar: '#toolbaroper'}
    ]]
    ,page: true
  });
}
// 报警邮件历史表数据加载
function mail_history_render(tbobj, url){
  tbobj.render({
    elem: '#alarm-mail-his'
    ,url: url
    ,headers: {"Authorization": 'Bearer ' + getToken()}
    ,method: 'get'
    ,title: '报警邮件历史数据'
    ,id: 'alarm-mail-his'
    ,cols: [[
      {field:'MessageType', title:'报警类型',width: '5%'}
      ,{field: 'Group', title: '分组', width: '5%'}
      ,{field: 'ReportName', title: '邮件模板', width: '10%'}
      ,{field: 'Subject', title: '标题', width: '25%'}
      ,{field: 'CreateTime', title: '报警时间', width: '10%', autoSort: false, sort: true}
      ,{field: 'Message', title: '报警信息', width: '25%'}
      ,{field:'Email', title:'收件人', width: '10%'}
      ,{field:'mlevel', title:'报警等级', width: '5%'}
      ,{field:'issend', fixed: 'right',title:'发送状态'}
    ]]
    ,page: true
  });
}
// 报警邮件配置
function alarm_mail_render(tbobj, url){
  tbobj.render({
    elem: '#alarm-mail'
    ,url: url
    ,headers: {"Authorization": 'Bearer ' + getToken()}
    ,method: 'get'
    ,title: '邮件配置'
    ,cols: [[
      {type: 'checkbox', width: '5%'}
      ,{field:'monitorid', hide: true}
      ,{field: 'mtype', title: '类型',width:'5%'}
      ,{field: 'groupname', title: '组名', width: '5%'}
      ,{field: 'mhost', title: '备注',width: '8%'}
      ,{field: 'host', title: '主机名',width:'8%'}
      ,{field: 'ip', title: 'IP',width:'8%'}
      ,{field:'key_', title:'键值', width: '7%'}
      ,{field:'lasterrortime', title: '最后报警时间',width: '10%'}
      ,{field:'lastOKtime', title:'上次恢复时间', width: '10%'}
      ,{field:'ismonitor', title:'状态', width: '4%'}
      ,{field:'comparetype', title: '阈值类型', width: '5%'}
      ,{field:'comparevalue', title: '阈值', width: '5%'}
      ,{field:'comparexpire', title: '阈值过期时间',width:'5%'}
      ,{field:'sendcount', title: '发送次数',width: '5%'}
      ,{field: 'oper',title:'操作', toolbar: '#toolbaroper'}
    ]]
    ,page: true
  });
}
// 服务器列表表格数据加载
function servers_render(tbobj, url){
  tbobj.render({
    elem: '#servers-table'
    ,url: url
    ,headers: {"Authorization": 'Bearer ' + getToken()}
    ,method: 'get'
    ,title: '服务列表'
    // ,id: 'serverlist'
    ,cols: [[
      {type: 'checkbox', width: '5%'}
      ,{field:'city', title:'地区', width: '10%'}
      ,{field:'hostip', title:'服务器IP', width: '10%'}
      ,{field:'hostname', title:'主机名', width: '10%'}
      ,{field:'projectname', title:'项目', width: '15%'}
      ,{field:'sitename', title:'站点域名', width: '15%'}
      ,{field:'description', title:'备注', width: '15%'}
      ,{field: 'ssh', title: '连接', toolbar: '#toolbarterm', width: '5%'}
      ,{field: 'oper',fixed: 'right', title:'操作', toolbar: '#toolbaroper'}
      ,{field: 'hostid', hide: true}
      ,{field: 'ssh_id', hide: true}
      ,{field: 'ssh_port', hide: true}
    ]]
    ,page: true
  });
}
// servers 下拉框表格数据加载
function tb_servers_reload(tbobj, id){
    var data_url;
    if(id == '0'){
        data_url = '/api/hosts_states/1';
    } else {
        data_url = '/api/projects/' + id +'/server?state=1'
    }
    servers_render(tbobj, data_url);
}
/*用户-停用*/
function member_stop(obj,id){
    layer.confirm('确认要停用吗？',function(index){
        if($(obj).attr('title')=='启用'){
            // 发异步把用户状态进行更改
            $(obj).attr('title','停用');
            $(obj).find('i').html('&#xe62f;');
            
            $(obj).parents("tr").find("span.layui-btn-mini").addClass('layui-btn-disabled').html('已停用');
            layer.msg('已停用!',{icon: 5,time:1000});
        }else{
            $(obj).attr('title','启用');
            $(obj).find('i').html('&#xe601;');

            $(obj).parents("tr").find("span.layui-btn-mini").removeClass('layui-btn-disabled').html('已启用');
            layer.msg('已启用!',{icon: 5,time:1000});
        }     
    });
}
/*用户-删除*/
function member_del(obj,id){
    layer.confirm('确认要禁用吗？',function(index){
        //发异步删除数据
        $.ajax({
            url:'/api/hosts/' + id,
            type: 'delete',
            headers: {
              "Authorization": 'Bearer ' + getToken()
            },
            success:function(data){
              obj.del();
              layer.close(index);
              // $(obj).parents("tr").remove();
              layer.msg('已删除!',{icon:1,time:1000});
            },
            error: function(data){
              layer.msg("删除异常");
            }
        });
    });
}
/* 删除角色*/
function delete_role(obj,data){
    layer.confirm('确认要删除['+ data.role+']角色吗？',function(index){
        //发异步删除数据
        $.ajax({
            url:'/api/role/' + data.id,
            type: 'delete',
            headers: {
              "Authorization": 'Bearer ' + getToken()
            },
            success:function(data){
              obj.del();
              layer.close(index);
              // $(obj).parents("tr").remove();
              layer.msg('已删除!',{icon:1,time:1000});
            },
            error: function(res){
                if(typeof res.responseJSON.msg == "undefined" || res.responseJSON.msg == null || res.responseJSON.msg == ""){
                    layer.msg(res.responseJSON.status);
                } else {
                    layer.msg(res.responseJSON.msg);
                }
              //layer.msg("删除异常");
            }
        });
    });
}
function delete_script(obj,data){
    layer.confirm('确认要删除['+ data.name +']脚本吗？',function(index){
        //发异步删除数据
        $.ajax({
            url:'/api/tasks/script/' + data.id,
            type: 'delete',
            headers: {
              "Authorization": 'Bearer ' + getToken()
            },
            success:function(data){
              obj.del();
              layer.close(index);
              layer.msg('已删除!',{icon:1,time:1000});
            },
            error: function(res){
                error_message(res)
            }
        });
    });
}
// 删除脚本版本
function delete_script_version(obj, jqy, url, data){
    layer.confirm('确认要删除['+ data.version +']版本吗？',function(index){
        //发异步删除数据
        jqy.ajax({
            url: url,
            type: 'delete',
            headers: {
              "Authorization": 'Bearer ' + getToken()
            },
            success:function(data){
              obj.del();
              layer.close(index);
              layer.msg('已删除!',{icon:1,time:1000});
            },
            error: function(res){
                error_message(res)
            }
        });
    });
}
/* 删除收件人邮箱 */
function delete_mail_config(obj,data, jq){
    layer.confirm('确认要删除['+ data.email+']吗？',function(index){
        //发异步删除数据
        jq.ajax({
            url:'/api/alarm/mail/config/' + data.id,
            type: 'delete',
            headers: {
              "Authorization": 'Bearer ' + getToken()
            },
            success:function(data){
              obj.del();
              layer.close(index);
              // $(obj).parents("tr").remove();
              layer.msg('已删除!',{icon:1,time:1000});
            },
            error: function(res){
                error_message(res);
            }
        });
    });
}
// 删除角色绑定的主机
function delete_role_host(obj,data, role_id){
    layer.confirm('确认要删除['+ data.ip +']关联主机吗？',function(index){
        //发异步删除数据
        $.ajax({
            url:'/api/role/' + role_id + '/host/' + data.id,
            type: 'delete',
            headers: {
              "Authorization": 'Bearer ' + getToken()
            },
            success:function(data){
              obj.del();
              layer.close(index);
              // $(obj).parents("tr").remove();
              layer.msg('已删除!',{icon:1,time:1000});
            },
            error: function(res){
                if(typeof res.responseJSON.msg == "undefined" || res.responseJSON.msg == null || res.responseJSON.msg == ""){
                    layer.msg(res.responseJSON.status);
                } else {
                    layer.msg(res.responseJSON.msg);
                }
              //layer.msg("删除异常");
            }
        });
    });
}
// 删除角色绑定视图
function delete_role_url(obj,data, role_id){
    layer.confirm('确认要删除['+ data.url+ ']视图吗？',function(index){
        //发异步删除数据
        $.ajax({
            url:'/api/role/' + role_id + '/url/' + data.id,
            type: 'delete',
            headers: {
              "Authorization": 'Bearer ' + getToken()
            },
            success:function(data){
              obj.del();
              layer.close(index);
              // $(obj).parents("tr").remove();
              layer.msg('已删除!',{icon:1,time:1000});
            },
            error: function(res){
                if(typeof res.responseJSON.msg == "undefined" || res.responseJSON.msg == null || res.responseJSON.msg == ""){
                    layer.msg(res.responseJSON.status);
                } else {
                    layer.msg(res.responseJSON.msg);
                }
              //layer.msg("删除异常");
            }
        });
    });
}
/* alarm mail dis*/
function dis_alarm_mail(obj, data){
    layer.confirm('确认要禁用['+ data.ip + ']吗？',function(index){
        //发异步删除数据
        console.log(data);
        $.ajax({
            url:'/api/alarm/mail/' + data.monitorid,
            type: 'delete',
            headers: {
              "Authorization": 'Bearer ' + getToken()
            },
            success:function(data){
              //obj.del();
              layer.close(index);
              obj.update({
                'ismonitor': 0
              });
              layer.msg('已禁用!',{icon:1,time:1000});
            },
            error: function(res){
                error_message(res);
            }
        });
    });
}
// 删除角色关联的用户
function delete_role_user(obj,data, role_id){
    layer.confirm('确认要删除['+ data.username+']关联用户吗？',function(index){
        //发异步删除数据
        $.ajax({
            url:'/api/role/' + role_id + '/user/' + data.id,
            type: 'delete',
            headers: {
              "Authorization": 'Bearer ' + getToken()
            },
            success:function(data){
              obj.del();
              layer.close(index);
              // $(obj).parents("tr").remove();
              layer.msg('已删除!',{icon:1,time:1000});
            },
            error: function(res){
                if(typeof res.responseJSON.msg == "undefined" || res.responseJSON.msg == null || res.responseJSON.msg == ""){
                    layer.msg(res.responseJSON.status);
                } else {
                    layer.msg(res.responseJSON.msg);
                }
              //layer.msg("删除异常");
            }
        });
    });
}
/* 删除ssh 用户*/
function ssh_user_del(obj,id){
    layer.confirm('确认要删除吗？',function(index){
        //发异步删除数据
        $.ajax({
            url:'/api/ssh_user/' + id,
            type: 'delete',
            headers: {
              "Authorization": 'Bearer ' + getToken()
            },
            success:function(data){
              obj.del();
              layer.close(index);
              // $(obj).parents("tr").remove();
              layer.msg('已删除!',{icon:1,time:1000});
            },
            error: function(data){
              layer.msg("删除异常");
            }
        });
    });
}

/* 删除用户*/
function user_del(obj,id){
    layer.confirm('确认要删除吗？',function(index){
        //发异步删除数据
        $.ajax({
            url:'/api/user/' + id,
            type: 'delete',
            headers: {
              "Authorization": 'Bearer ' + getToken()
            },
            success:function(data){
              obj.del();
              layer.close(index);
              // $(obj).parents("tr").remove();
              layer.msg('已删除!',{icon:1,time:1000});
            },
            error: function(data){
              layer.msg("删除异常");
            }
        });
    });
}
/* projectid下拉框赋值 */
function projects_load(obj){
    $.ajax({
        url:'/api/projects',
        type: 'get',
        headers: {
          "Authorization": 'Bearer ' + getToken()
        },
        success:function(data){
            $.each(data.data, function(index, item){
                $('select[name=projectid]').append('<option value="'+item.projectid +'">' + item.projectname + '</option>');
            });
            obj.render("select");
        }
    });
}
/* 邮件报警配置下拉框数据赋值*/
function m_select_reload(obj, url, sid){
    $.ajax({
        url: url,
        type: 'get',
        headers: {
          "Authorization": 'Bearer ' + getToken()
        },
        success:function(data){
            $.each(data.data, function(index, item){
                $('select[name='+ sid +']').append('<option value="'+item.id +'">' + item.name + '</option>');
            });
            obj.render("select");
        }
    })
}
/* 报警邮件历史下拉框数据赋值 */
function mh_select_reload(jq, obj, url, sid){
    jq.ajax({
        url: url,
        type: 'get',
        headers: {
          "Authorization": 'Bearer ' + getToken()
        },
        success:function(data){
            jq.each(data.data, function(index, item){
                jq('select[name='+ sid +']').append('<option value="'+item.id +'">' + item.name + '</option>');
            });
            obj.render("select");
        }
    })
}

/* role下拉框赋值 */
function roles_load(obj){
    $.ajax({
        url:'/api/roles',
        type: 'get',
        headers: {
          "Authorization": 'Bearer ' + getToken()
        },
        success:function(data){
            $.each(data.data, function(index, item){
                $('select[name=role]').append('<option value="'+item.id +'">' + item.role + '</option>');
            });
            obj.render("select");
        }
    });
}
/* sshuser 下拉框赋值*/
function ssh_users_load(obj, jqy){
    jqy.ajax({
        url:'/api/ssh_users',
        type: 'get',
        headers: {
          "Authorization": 'Bearer ' + getToken()
        },
        success:function(data){
            jqy.each(data.data, function(index, item){
                jqy('select[name=ssh_id]').append('<option value="'+item.ssh_id +'">' + item.ssh_name +'(' + item.ssh_user + ')' + '</option>');
            });
            obj.render("select");
        }
    });
}
/* 获取url参数 */
function searchToObject() {
    var pairs = window.location.search.substring(1).split("&"),
      obj = {},
      pair,
      i;

    for ( i in pairs ) {
      if ( pairs[i] === "" ) continue;

      pair = pairs[i].split("=");
      obj[ decodeURIComponent( pair[0] ) ] = decodeURIComponent( pair[1] );
    }
    return obj;
}
/* ajax错误提示 */
function error_message(res){
    if(typeof res.responseJSON == "undefined" || typeof res.responseJSON.msg == 'undefined' ||res.responseJSON.msg == null || res.responseJSON.msg == ""){
        layer.msg(res.statusText);
    } else {
        layer.msg(res.responseJSON.msg);
    }
}
/* 拼接url */
function paramsJoin(url, params){
    let paramsArray = [];
    Object.keys(params).forEach(key => paramsArray.push(key + '=' + params[key]));
    if (url.search(/\?/) === -1) {
        url += '?' + paramsArray.join('&');
    } else {
        url += '&' + paramsArray.join('&');
    }
    return url;
}
function show_back(obj){
    obj.style.backgroundColor='#ECECEC';
}
function dis_back(obj){
    obj.style.backgroundColor='#FFF';
};
// 上线脚本
function enable_script(jq, url, data, action){
  layer.confirm('确认要上线' + data.version + '版本吗？',function(index){
    var d={};
    d['action'] = action;
    d['data'] = data;
    jq.ajax({
        url: url,
        type: 'put',
        headers: {
            "Authorization": 'Bearer ' + getToken()
        },
        data: JSON.stringify(d),
        dataType: 'json',
        contentType: "application/json; charset=utf-8",
        success:function(data){
            layer.msg('上线成功', {icon:1,time:1000})
            location.reload();
        },
        error: function(res){
            error_message(res);
        }
    });
  })
}
function get_authorization(){
    return {"Authorization": 'Bearer ' + window.localStorage.getItem('token')};
}
// 下线脚本
function disable_script(jq, url, data, action){
  layer.confirm('确认要下线' + data.version + '版本吗？',function(index){
    var d={};
    d['action'] = action;
    d['data'] = data;
    jq.ajax({
        url: url,
        type: 'put',
        headers: {
            "Authorization": 'Bearer ' + getToken()
        },
        data: JSON.stringify(d),
        dataType: 'json',
        contentType: "application/json; charset=utf-8",
        success:function(data){
            layer.msg('下线成功', {icon:1,time:1000});
            location.reload();
        },
        error: function(res){
            error_message(res);
        }
    });
  })
}
function show_job_list(jqy, url){
    jqy.ajax({
        url: url
        ,type: 'get'
        ,headers: {
            "Authorization": 'Bearer ' + getToken()
        }
        ,success: function(data){
            if(data.data.num > 99){
                jqy('#msgnum').show();
                jqy('#msgnum').text('...');
            }else if(data.data.num > 0){
                jqy('#msgnum').show();
                jqy('#msgnum').text(data.data.num);
            }else{
                jqy('#msgnum').hide();
            }
        }
        ,error: function(res){
            error_message(res);
        }
    })
}
function removeself(obj){
    obj.parentNode.parentNode.remove();
    //console.log(obj.parentNode);
    /*
    var idObject = document.getElementById(obj.id);
    if (idObject != null){
            idObject.parentNode.parentNode.remove(idObject);
    }*/
}
function add_parameter(jqy, obj, add_num, add_exit=true, name='', value='', desc=''){
    var ops_text;
    if(obj === 1){
        ops_text='<div style="width:50%;padding-left:100px">' +
                                    '<fieldset class="layui-elem-field">' +
                                      '<legend>字符参数'
        if(add_exit){
            ops_text += '<button type="button" class="layui-btn layui-btn-radius layui-btn-primary layui-btn-sm" style="float:right;border:none;color:red"' +
                                               'onclick="removeself(this);" onmouseover="show_back(this)" onmouseout="dis_back(this)">' +
                                              '<i class="layui-icon">&#x1006;</i>'+
                                          '</button>'
        }
            ops_text += '</legend>'+
                                      '<div class="layui-field-box">'+
                                        '<div>'+
                                          '<div style="display:inline-block;padding:9px 15px;width:60px;text-align:right;vertical-align:top;">'+
                                            '<label><span class="x-red">*</span>参数名</label>'+
                                          '</div>'+
                                          '<div style="display:inline-block;width:50%;">'+
                                            '<input type="text" id="OC_parname_' +add_num + '" name="ocparname_' + add_num +'" required="" lay-verify="required"'+
                                              'autocomplete="off" class="layui-input" value="'+ name + '">'+
                                          '</div>'+
                                        '</div>'+
                                        '<div>'+
                                          '<div style="display:inline-block;padding:9px 15px;width:60px;text-align:right;vertical-align:top;">'+
                                            '<label><span class="x-red"></span>默认值</label>'+
                                          '</div>'+
                                          '<div style="display:inline-block;width:50%;">'+
                                            '<input type="text" id="OC_pardefault_' + add_num + '" name="ocpardefault_'+ add_num +'" required="" lay-verify=""'+
                                              'autocomplete="off" class="layui-input" value="' + value + '">'+
                                          '</div>'+
                                        '</div>'+
                                        '<div>'+
                                          '<div style="display:inline-block;padding:9px 15px;width:60px;text-align:right;vertical-align:top;">'+
                                            '<label><span class="x-red"></span>描述</label>'+
                                          '</div>'+
                                          '<div style="display:inline-block;width:50%;">'+
                                            '<textarea id="OC_pardesc_'+add_num+'" name="ocpardesc_'+ add_num + '" autocomplete="off" class="layui-textarea">'+ desc +'</textarea>'+
                                          '</div>'+
                                        '</div>'+
                                      '</div>'+
                                    '</fieldset>'+
                               '</div>';
    }else if (obj === 2){
        ops_text='<div style="width:50%;padding-left:100px">'+
                                    '<fieldset class="layui-elem-field">'+
                                      '<legend>选项参数'
        if(add_exit){
            ops_text += '<button type="button" class="layui-btn layui-btn-radius layui-btn-primary layui-btn-sm" style="float:right;border:none;color:red"' +
                                               'onclick="removeself(this);" onmouseover="show_back(this)" onmouseout="dis_back(this)">' +
                                              '<i class="layui-icon">&#x1006;</i>'+
                                          '</button>'
        }
            ops_text += '</legend>'+
                                      '<div class="layui-field-box">'+
                                        '<div>'+
                                          '<div style="display:inline-block;padding:9px 15px;width:60px;text-align:right;vertical-align:top;">'+
                                            '<label><span class="x-red">*</span>参数名</label>'+
                                          '</div>'+
                                          '<div style="display:inline-block;width:50%;">'+
                                            '<input type="text" id="OS_parname_'+ add_num +'" name="osparname_'+ add_num +'" required="" lay-verify="required"'+
                                              'autocomplete="off" class="layui-input" value="' + name +'">'+
                                          '</div>'+
                                        '</div>'+
                                        '<div>'+
                                          '<div style="display:inline-block;padding:9px 15px;width:60px;text-align:right;vertical-align:top;">'+
                                            '<label><span class="x-red">*</span>选项</label>'+
                                          '</div>'+
                                          '<div style="display:inline-block;width:50%;">'+
                                            '<textarea id="OS_parselect_' + add_num + '" name="osparselect_'+ add_num +'" autocomplete="off" class="layui-textarea" lay-verify="required">' + value +'</textarea>'+
                                          '</div>'+
                                        '</div>'+
                                        '<div>'+
                                          '<div style="display:inline-block;padding:9px 15px;width:60px;text-align:right;vertical-align:top;">'+
                                            '<label><span class="x-red"></span>描述</label>'+
                                          '</div>'+
                                          '<div style="display:inline-block;width:50%;">'+
                                            '<textarea id="OS_pardesc_'+ add_num +'" name="ospardesc_'+ add_num + '" autocomplete="off" class="layui-textarea">'+ desc +'</textarea>'+
                                          '</div>'+
                                        '</div>'+
                                      '</div>'+
                                    '</fieldset>'+
                               '</div>';
    }
    jqy('#options').append(ops_text);
}
