from os import urandom

from flask import Flask, flash, redirect, render_template, \
request, session, abort, url_for

from sqlalchemy.orm import sessionmaker
from db import *

engine = create_engine('sqlite:///main.db', echo=True)

app = Flask(__name__)

@app.route("/")
def index():
    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(User).all()

    if not session.get('loggedin'):
        return render_template('index.html', logged=False, data=query)
    else:
        return render_template('index.html', logged=True, data=query)

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        if not session.get("loggedin"):
            return render_template("signup.html")
        else:
            return redirect(url_for("index"))
    else:
        if not session.get("loggedin"):
            user, password = request.form['username'], request.form['password']
            if not user or not password:
                flash('Invalid input')
                return redirect(url_for("signup"))
            else:
                Session = sessionmaker(bind=engine)
                s = Session()
                user = User(user, password)
                s.add(user)
                s.commit()
                session['loggedin'] = True

                return redirect(url_for("index"))

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        Session = sessionmaker(bind=engine)
        s = Session()

        query = s.query(User).filter(User.username.in_([username]),
                                     User.password.in_([password]))
        result = query.first()

        if result:
            session['loggedin'] = True
        else:
            flash('wrong username or password: %s' %(username))

        return redirect(url_for('login'))
    else:
        if not session.get('loggedin'):
            return render_template('login.html')
        else:
            return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session['loggedin'] = False
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404


app.secret_key = sKey = urandom(12)
app.run(host='0.0.0.0', debug=True)
