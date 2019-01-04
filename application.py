import os

from flask import Flask, session, render_template, redirect, request, url_for, g
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route('/', methods= ['GET', 'POST'])
def index():
    if request.method =='POST' :
        session.pop('user', None) 

        submitted_username = request.form['username']
        submitted_password = request.form['password']
        user = db.execute("SELECT id, login, password FROM users WHERE login = :login", {"login": submitted_username}).fetchone()
    
        if db.execute("SELECT id, login, password FROM users WHERE login = :login", {"login": submitted_username}).rowcount == 0:
            error=("User not found in database")
            return render_template("failed.html", error=error)
        elif submitted_password != user.password:
            error=("Wrong password")
            return render_template("failed.html", error=error)
        elif submitted_password == user.password:
             session['user'] = user.login
             return redirect(url_for('protected'))

    
    else:
        return render_template("index.html")

@app.route('/register', methods= ['POST', 'GET'])
def register():
    if request.method == 'POST' :
        session.pop('user', None)
        session['user'] = request.form['username']
        return redirect(url_for('protected'))
    else:
        return render_template("register.html")


@app.route('/protected')
def protected():
        return render_template('protected.html', username=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return render_template('logout.html')




@app.route('/getsession')
def getsession():
    if 'user' in session:
        return session ['user']
    
    return 'not logged in!'
 



    


""" @app.route('/protected')
def protected():
        if g.user:
            return render_template('protected.html')
        return redirect(url_for('index'))

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
            return session['user'] """

""" @app.route('/')
def index():
    session['user'] = 'test'
    return 'index' """