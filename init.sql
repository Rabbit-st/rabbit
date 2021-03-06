use rabbit;
INSERT INTO `admin_user`(`id`, `username`, `nickname`, `email`,`password`, `avatar`, `state`, `remark`, `create_time`, `last_seen`)
VALUES (1,'admin','','aaaa@qq.com','pbkdf2:sha256:150000$6758JkHn$2c83a005e71ad9805823337ce06ae0df2380f87e3a67199dfd41976c36bc8eb2','',1,'超级管理员',now(),now());

INSERT INTO `admin_permission`(`id`,`name`,`url` ,`type`,`description` ,`create_time` ,`icon`,`open_type`,`parent_id`,`sort`,`state`,`update_time` ,`code`)
VALUES (2,'系统管理','','0','','2021-08-11 10:23:23','layui-icon layui-icon-set-fill','','0',99,1,'2021-08-11 10:23:23',''),
(3,'权限管理','/permission','1','','2021-08-11 10:20:49','layui-icon layui-icon-set-fill','_iframe','2',3,1,'2021-08-11 10:20:49','permission:main'),
(4,'添加权限','','2','','2021-09-01 08:56:01','layui-icon None','','3',1,1,'2021-09-01 08:56:01','api:permission:add'),
(5,'删除权限','','2','','2021-09-01 08:58:18','layui-icon None','','3',1,1,'2021-09-01 08:58:18','api:permission:delete'),
(6,'修改权限','','2','','2021-09-01 09:01:57','layui-icon None','','3',2,1,'2021-09-01 09:01:57','api:permission:edit'),
(15,'服务器管理','','0','','2021-09-03 05:49:29','layui-icon layui-icon-align-left','','0',1,1,'2021-09-03 05:49:29',''),
(16,'服务器管理','/hosts/hosts','1','','2021-09-03 05:50:47','layui-icon layui-icon-align-center','','15',1,1,'2021-09-03 05:50:47','hosts:main'),
(17,'项目管理','/projects/projects','1','','2021-09-03 05:52:23','layui-icon layui-icon-tabs','','15',2,1,'2021-09-03 05:52:23','projects:main'),
(18,'SSH用户管理','/ssh_users/ssh_users','1','','2021-09-03 05:54:07','layui-icon layui-icon-password','','15',3,1,'2021-09-03 05:54:07','ssh_users:main'),
(19,'任务管理','','0','','2021-09-03 05:55:52','layui-icon layui-icon-date','','0',2,1,'2021-09-03 05:55:52',''),
(20,'环境部署','/deployenv','1','','2021-09-03 05:59:02','layui-icon layui-icon-rate-half','_iframe','19',1,1,'2021-09-03 05:59:02','env:main'),
(21,'报警配置','','0','','2021-09-03 06:00:15','layui-icon layui-icon-chart','','0',3,1,'2021-09-03 06:00:15',''),
(22,'报警管理','/alarm/config','1','','2021-09-03 06:01:45','layui-icon layui-icon-cellphone','_iframe','21',1,1,'2021-09-03 06:01:45','alarm:config'),
(23,'报警邮件记录','/alarm/history','1','','2021-09-03 06:02:26','layui-icon ','_iframe','21',2,1,'2021-09-03 06:02:26','alarm:history'),
(24,'收件人配置','/alarm/mail','1','','2021-09-03 06:02:59','layui-icon ','_iframe','21',1,1,'2021-09-03 06:02:59','alarm:mail'),
(25,'用户管理','/users/users','1','','2021-09-03 06:04:58','layui-icon None','','2',1,1,'2021-09-03 06:04:58','user:main'),
(26,'角色管理','/role/roles','1','','2021-09-03 06:05:35','layui-icon None','_iframe','2',2,1,'2021-09-03 06:05:35','role:main'),
(27,'刷新权限','/permission/refresh','1','','2021-09-03 06:33:33','layui-icon ','_iframe','2',4,1,'2021-09-03 06:33:33','permission:refresh'),
(28,'查看权限','','2','','2021-09-03 07:14:03','layui-icon None','','3',1,1,'2021-09-03 07:14:03','api:permission:main'),
(29,'刷新权限','','2','','2021-09-03 07:24:26','layui-icon ','','27',0,1,'2021-09-03 07:24:26','api:permission:refresh'),
(30,'添加角色','','2','','2021-09-06 06:17:19','layui-icon None','','26',0,1,'2021-09-06 06:17:19','api:role:add'),
(31,'修改角色','','2','','2021-09-06 06:17:50','layui-icon None','','26',0,1,'2021-09-06 06:17:50','api:role:edit'),
(32,'删除角色','','2','','2021-09-06 06:18:16','layui-icon ','','26',0,1,'2021-09-06 06:18:16','api:role:delete'),
(33,'查看角色','','2','','2021-09-06 06:23:32','layui-icon ','','26',0,1,'2021-09-06 06:23:32','api:role:main'),
(34,'修改权限状态','','2','','2021-09-06 06:59:30','layui-icon ','','3',0,1,'2021-09-06 06:59:30','api:permission:state'),
(35,'修改角色状态','','2','','2021-09-06 08:07:15','layui-icon ','','26',0,1,'2021-09-06 08:07:15','api:role:state'),
(36,'查看角色权限','','2','','2021-09-07 02:54:13','layui-icon None','','26',0,1,'2021-09-07 02:54:13','api:role:permissions:main'),
(37,'修改角色权限','','2','','2021-09-07 06:18:07','layui-icon ','','26',0,1,'2021-09-07 06:18:07','api:role:permissions:edit'),
(39,'添加用户','','2','','2021-09-08 03:23:22','layui-icon ','','25',1,1,'2021-09-08 03:23:22','api:user:add'),
(40,'修改用户','','2','','2021-09-08 03:28:26','layui-icon None','','25',1,1,'2021-09-08 03:28:26','api:user:edit'),
(43,'删除用户','','2','','2021-09-08 07:21:17','layui-icon ','','25',1,1,'2021-09-08 07:21:17','api:user:delete'),
(44,'查看用户','','2','','2021-09-08 07:21:39','layui-icon ','','25',2,1,'2021-09-08 07:21:39','api:user:main'),
(45,'修改用户状态','','2','','2021-09-08 14:23:08','layui-icon ','','25',1,1,'2021-09-08 14:23:08','api:user:state'),
(46,'查看权限','','2','','2021-09-17 07:18:41','layui-icon ','','16',0,1,'2021-09-17 07:18:41','api:hosts:main'),
(47,'修改主机','','2','','2021-09-17 07:19:16','layui-icon ','','16',1,1,'2021-09-17 07:19:16','api:hosts:edit'),
(48,'新增主机','','2','','2021-09-17 07:19:31','layui-icon ','','16',1,1,'2021-09-17 07:19:31','api:hosts:add'),
(49,'禁用主机','','2','','2021-09-17 07:19:53','layui-icon ','','16',1,1,'2021-09-17 07:19:53','api:hosts:dis'),
(50,'删除主机','','2','','2021-09-17 07:20:10','layui-icon ','','16',1,1,'2021-09-17 07:20:10','api:hosts:remove'),
(51,'恢复主机','','2','','2021-09-17 07:20:35','layui-icon ','','16',1,1,'2021-09-17 07:20:35','api:hosts:recycle'),
(52,'批量添加主机','','2','','2021-09-17 07:25:47','layui-icon ','','16',1,1,'2021-09-17 07:25:47','api:hosts:upload'),
(53,'查看项目','','2','','2021-09-17 08:06:27','layui-icon ','','17',1,1,'2021-09-17 08:06:27','api:projects:main'),
(54,'修改项目','','2','','2021-09-17 08:06:47','layui-icon ','','17',1,1,'2021-09-17 08:06:47','api:projects:edit'),
(55,'删除项目','','2','','2021-09-17 08:07:14','layui-icon ','','17',1,1,'2021-09-17 08:07:14','api:projects:remove'),
(56,'禁用项目','','2','','2021-09-17 08:07:31','layui-icon ','','17',1,1,'2021-09-17 08:07:31','api:projects:dis'),
(57,'添加项目','','2','','2021-09-17 08:52:36','layui-icon ','','17',1,1,'2021-09-17 08:52:36','api:projects:add'),
(58,'查看SSH用户','','2','','2021-09-22 02:43:44','layui-icon ','','18',1,1,'2021-09-22 02:43:44','api:ssh_users:main'),
(59,'添加SSH账号','','2','','2021-09-22 02:44:04','layui-icon ','','18',1,1,'2021-09-22 02:44:04','api:ssh_users:add'),
(60,'删除ssh用户','','2','','2021-09-22 02:44:21','layui-icon None','','18',1,1,'2021-09-22 02:44:21','api:ssh_users:delete'),
(61,'修改SSH用户','','2','','2021-09-22 02:45:09','layui-icon ','','18',1,1,'2021-09-22 02:45:09','api:ssh_users:edit'),
(62,'禁用SSH用户','','2','','2021-09-22 02:45:32','layui-icon ','','18',1,1,'2021-09-22 02:45:32','api:ssh_users:disable'),
(63,'webssh','/webssh/web','1','','2021-09-24 09:47:02','layui-icon None','_iframe','15',4,1,'2021-09-24 09:47:02','webssh:main');


INSERT INTO `admin_role` (`id`,`level`,`type`,`state`,`create_time`,`name`,`remark`,`update_time`)
VALUES (1,1,'系统默认',1,'2021-09-06 14:23:16','超级管理员','t','2021-09-06 16:26:51'),
(2,2,'系统默认',1,'2021-09-06 14:23:16','管理员','','2021-09-06 14:23:16'),
(3,3,'系统默认',1,'2021-09-06 14:23:16','ops','','2021-09-06 14:23:16'),
(4,1,'系统默认',1,'2021-09-06 14:23:16','临时账号','s','2021-09-06 17:54:44');