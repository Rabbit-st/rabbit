#-*-coding:utf-8-*-

class ResponseCode(object):
    Success = 1  # 成功
    layui_Success = 0 # layui table成功状态码
    Fail = -1  # 失败
    Created = 201
    Deleted = 202 # 删除成功
    Forbidden = 403
    NoResourceFound = 40001  # 未找到资源
    InvalidParameter = 40002  # 参数无效
    AccountOrPassWordErr = 40003  # 账户或密码错误
    VerificationCodeError = 40004  # 验证码错误
    PleaseSignIn = 40005  # 请登陆
    WeChatAuthorizationFailure = 40006  # 微信授权失败
    InvalidOrExpired = 40007  # 验证码过期
    MobileNumberError = 40008  # 手机号错误
    FrequentOperation = 40009  # 操作频繁,请稍后再试

class ResponseMessage(object):
    Success = "成功"
    layui_Success = "成功"
    Fail = "失败"
    Forbidden = '没有权限'
    NoResourceFound = "未找到资源"
    InvalidParameter = "参数无效"
    AccountOrPassWordErr = "账户或密码错误"
    VerificationCodeError = "验证码错误"
    PleaseSignIn = "请登陆"
    # 编码对应的msg
    Msg = {
        'zh_CN': {
            0: "成功"
            ,1: "成功"
            ,-1: "失败"
            ,403: '没有权限'
            ,201: "数据添加成功"
            ,202: "删除成功"
            ,40001: "资源不存在"
            ,40002: "参数无效"
            ,40003: "账户或密码错误"
            ,40004: "验证码错误"
            ,40005: "请登陆"
            ,40006: "微信授权失败"
            ,40007: "验证码过期"
            ,40008: "手机号错误"
            ,40009: "操作频繁,请稍后再试:"
        }
        ,'en': {
            0: "success"
            ,-1: "fail"
            ,201: "created"
            ,40001: "No resources found"
            ,40002: "Invalid argument"
            ,40003: "Incorrect account or password"
            ,40004: "Verification code error"
            ,40005: "Please sign in"
            ,40006: "WeChat Authorization Failure"
            ,40007: "Verification code expired"
            ,40008: "Mobile number error"
            ,40009: "Frequent operation, please try again late"
        }
    }


