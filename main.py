import os

from flask import Flask, flash, redirect, render_template, \
request, session, url_for

from flask_sqlalchemy import SQLAlchemy


"""
Setup
"""
# Init a Flask application
app = Flask(__name__)

# Some SQLAlchemy configs
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import the models' SQLAlchemy
from models import db

# Load the app into the SQLAlchemy db
db.init_app(app)

# Finally, import the User model.
from models import User


"""
Routes
"""
def logged(session):
    return bool(session.get("session_login_status"))

# Index
@app.route("/")
@app.route("/home")
@app.route("/index")
def index():
    query = User.query.all()

    if not logged(session):
        return render_template('index.html', logged=False, data=query)
    else:
        return render_template('index.html', logged=True, data=query)


@app.route("/signup", methods=['POST', 'GET'])
def signup():
    logged_status = logged(session)

    if request.method == 'GET':
        if not logged_status:
            return render_template("signup.html")
        else:
            return redirect(url_for("index"))
    else:
        if not logged_status:
            user, password = request.form['username'], request.form['password']

            if not user or not password:
                flash('Missing fields.')
                return redirect(url_for("signup"))

            else:
                # Check if the username already exists
                query = User.query.filter(User.username.in_([user]))

                if query.first():
                    # Username is already taken.
                    flash("Username is taken.")
                    return redirect(url_for('signup'))

                else:
                    new_user = User(user, password)
                    db.session.add(new_user)
                    db.session.commit()
                    session['session_login_status'] = True

                    return redirect(url_for("index"))


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']

        # Get the data from the database
        query = User.query.filter(User.username.in_([username]),
                                  User.password.in_([password]))
        result = query.first()

        # If data exists, log the user in.
        if result:
            session['session_login_status'] = True
        else:
            flash('Wrong username or password: %s' %(username))

        return redirect(url_for('login'))

    else:
        if logged(session):
            return redirect(url_for('index'))
        else:
            return render_template('login.html')


@app.route('/logout')
def logout():
    session['session_login_status'] = False
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404


app.secret_key = sKey = os.urandom(12)
app.run(host='0.0.0.0', debug=True)
