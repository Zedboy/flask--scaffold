Ngnix，一个高性能的web服务器，毫无疑问它是当下的宠儿。卓越的性能，灵活可扩展，在服务器领域里攻城拔寨，征战天下。

静态文件对于大多数website是不可或缺的一部分。使用Nginx来处理静态文件也是常见的方式。然而，一些静态文件，我们并不像任何情况下都公开给任何用户。例如一些提供给用户下载的文件，一些用户上传的涉及用户隐私的图片等。我们我希望用户登录的情况下可以访问，未登录的用户则不可见。

粗略的处理，在后端程序可以做过滤，渲染页面的时候，在视图逻辑里面验证用户登录，然后返回对应的页面。例如下面的flask代码（伪代码）

    @app.router('/user/idcard'):
    def user_idcard_page():
        if user is login:
            return '<img src="/upload/user/xxx.png'>"
        else:
            reutrn '<p>Pemission Denied<p>', 403

可是这样的处理，还有一个问题，静态文件是交给 nginx 处理的，如果hacker找到了文件的绝对地址，直接访问 `http://www.example.com/upload/user/xxx.png`也是可以的。恰巧这些文件又涉及用户隐私，比如用户上传的身份证照片。那么码农可不希望第二天媒体报道，知名网站XXX存在漏洞，Hacker获取了用户身份证等信息。 

为了做这样的限制，可以借助 Nginx 的一个小功能----[XSendfile](http://wiki.nginx.org/XSendfile)。 其原理也比较简单，大概就是使用了请求重定向。

我们知道，如果用Nginx做服务器前端的反向代理，一个请求进来，nginx先补捉到，然后再根据规则转发给后端的程序处理，或者直接处理返回。前者处理一些动态逻辑，后者多是处理静态文件。因此上面那个例子中，直接访问静态文件的绝对地址，Nginx就直接返回了，并没有调用后端的 `user_idcard_page`做逻辑限制。

为了解决这个问题，nginx提供的 XSendfile功能，简而言之就是用 internal 指令。该指令表示只接受内部的请求，即后端转发过来的请求。后端的视图逻辑中，需要明确的写入` X-Accel-Redirect`这个headers信息。

伪代码如下：

    location /upload/(.*) {
            alias /vagrant/;
            internal;
    }

    @app.router('upload/<filename>')
    @login_required
    def upload_file(filename):
        response = make_response()
        response['Content-Type'] = 'application/png'
        response['X-Accel-Redirect'] = '/vagrant/upload/%s' % filename
        return response
                
经过这样的处理，就能将静态资源进行重定向。这样的用法还是比较常见的，很多下载服务器可以通过这样的手段针对用户的权限做下载处理。

Flask是我喜欢的web框架，Flask甚至实现了一个 sendfile的方法，比上面的做法还简单。我用vagrant作了一个虚拟机，用Flask实现了上面的需求，具体代码如下：

项目结构
project struct

    project
      app.py
      templates
      static
        0.jpeg
      upload
        0.jpeg
        

nginx的配置 nginx conf
 
web.conf

    server {
            listen 80 default_server;
            
            # server_name localhost;
            server_name 192.168.33.10;
            location / {
                    proxy_pass http://127.0.0.1:8888;
                    proxy_redirect off;
                    proxy_set_header Host $host:8888;
                    proxy_set_header X-Real-IP $remote_addr;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            }
            # 正常的静态文件
            location /static/(.*) {
                    root /vagrant/;
    
            }
            # 用户上传的文件，需要做权限限制
            location /upload/(.*) {
                    alias /vagrant/;
                    internal;             # 只接受内部请求的指令
            }
    }
    
Flask 代码

app.py

    
    from functools import wraps
    from flask import Flask,  render_template, redirect, url_for, session, send_file
    
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'you never guess'
    
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('login'):
                return redirect(url_for('login', next=request.url))
            return f(*args, **kwargs)
        return decorated_function
    
    @app.route('/')
    def index():
        return 'index'
    
    
    @app.route('/user')
    @login_required
    def user():

        return render_template('upload.html')
    
    # 用户上传的文件视图处理，在此处返回请求给nginx
    @app.route('/upload/<filename>')
    @login_required
    def upload(filename):
    
        return send_file('upload/{}'.format(filename))
    
    
    @app.route('/login')
    def login():
        session['login'] = True
        return 'log in'
    
    @app.route('/logout')
    def logout():
        session['login'] = False
        return 'log out'
    
    
    if __name__ == '__main__':
        app.run(debug=True)



简单部署

    gunicorn -w4 -b0.0.0.0:8888 app:app  --access-logfile access.log --error-logfile error.log



