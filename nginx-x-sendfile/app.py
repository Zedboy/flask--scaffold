

from flask import Flask,  render_template,  redirect, url_for, session, send_file

from functools import wraps




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



