from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse
from app import db
from app.auth import bp

@bp.route('/login')
def login():
    if current_user.is_authenticated:  # 是否已经登录
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data): # 用户是否存在，密码是否正确
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)  # 用户登录状态注册为已登录，其他页面可以通过current_user变量访问用户实例
        # 如果是从其他页面跳转过来的，登录成功后，回转到原先要访问的页面，否则跳转到index页面
        next_page = request.args.get('next')   
        if not next_page or url_parse(next_page).netloc != '':  # url_parse用于判断源页面域名是不是完整的，如果是完整的域名直接跳转到本站的主页。
            next_page = url_for('main.index')
        return redirect(next_page)

    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    pass

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    pass

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    pass
