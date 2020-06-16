from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from werkzeug.wrappers import Request
from werkzeug.exceptions import Forbidden
import casbin


app = Flask(__name__)

# 这个必须写，不然没有session
app.secret_key = 'bj-nego'

login_manager = LoginManager()
login_manager.init_app(app)
# 设置登录视图的名称，如果一个未登录用户请求一个只有登录用户才能访问的视图，
# 则闪现一条错误消息，并重定向到这里设置的登录视图。
# 如果未设置登录视图，则直接返回401错误。
login_manager.login_view = 'login'
# 设置当未登录用户请求一个只有登录用户才能访问的视图时，闪现的错误消息的内容，
# 默认的错误消息是：Please log in to access this page.。
login_manager.login_message = 'Unauthorized User'
# 设置闪现的错误消息的类别
login_manager.login_message_category = "info"

# 用户记录表
users = [
    {'username': 'tom', 'password': '111'},
    {'username': 'jerry', 'password': '222'}
]


logged_user = {'username': None}


class CasbinMiddleware:
    def __init__(self, app, enforcer):
        self.app = app
        self.enforcer = enforcer

    def __call__(self, environ, start_response):
        # not Flask request - from werkzeug.wrappers import Request
        request = Request(environ)

        # Check the permission for each request.
        if not self.check_permission(request):
            # Not authorized, return HTTP 403 error.
            return Forbidden()(environ, start_response)

        # Permission passed, go to next module.
        return self.app(environ, start_response)

    def check_permission(self, request):
        # Customize it based on your authentication method.
        if logged_user['username'] is None:
            user = 'anonymous'
        else:
            user = logged_user['username']
        path = request.path
        method = request.method

        return self.enforcer.enforce(user, path, method)


# Initialize the Casbin enforcer, load the casbin model and policy from files.
# Change the 2nd arg to use a database.
enforcer = casbin.Enforcer("authz_model.conf", "authz_policy.csv")

app.wsgi_app = CasbinMiddleware(app.wsgi_app, enforcer)


class User(UserMixin):
    pass


# 通过用户名，获取用户记录，如果不存在，则返回None
def query_user(username):
    for user in users:
        if user['username'] == username:
            return user


# 如果用户名存在则构建一个新的用户类对象，并使用用户名作为ID
# 如果不存在，必须返回None
@login_manager.user_loader
def user_loader(username):
    if query_user(username) is None:
        return

    user = User()
    user.id = username

    return user


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    if query_user(username) is None:
        return

    user = User()
    user.id = username

    return user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = query_user(username)
        # 验证表单中提交的用户名和密码
        if user is not None and request.form['password'] == user['password']:
            user = User()
            user.id = username
            login_user(user)
            # 重要步骤
            logged_user['username'] = username

            return redirect(url_for('index'))

        flash('Wrong username or password!')

    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    # 重要步骤
    logged_user['username'] = None
    return redirect(url_for('index'))


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/home')
@login_required
def home():
    return render_template('home.html')


# 自定义未授权访问的处理方法
# 这个@login_manager.unauthorized_handler装饰器所修饰的方法就会代替@login_required装饰器的默认处理方法。
# @login_manager.unauthorized_handler
# def unauthorized_handler():
#     return 'Unauthorized'


if __name__ == '__main__':
    app.run(port=5001, debug=True)

