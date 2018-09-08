from flask import Blueprint, request, url_for, redirect, render_template, flash
from flask_wtf.csrf import CSRFProtect
from flask_login import current_user, login_user, logout_user, LoginManager, \
                        login_required
from werkzeug.security import generate_password_hash, check_password_hash
from google.oauth2 import id_token
from google.auth.transport import requests as rqs

from models import db, User

import json

auth = Blueprint('auth', __name__)

csrf = CSRFProtect()
login_manager = LoginManager()

login_manager.login_view = "login"

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@auth.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            username = request.form['username']
            password = request.form['password']

            # get the data from the database
            query = User.query.filter(User.username.ilike(username))
            user = query.first()

            if user.google:
                flash("Please login with Google.")
                return redirect(url_for("gconnect"))

            # if data exists, log the user in.
            if user and check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for("index"))

            else:
                flash('Wrong username or password: %s' % (username))
                return redirect(url_for('login'))

        else:
            flash("You are already logged in.")
            return redirect(url_for('index'))

    else:
        # redirect the user to index or login based on his log in status.
        # if current_user.is_authenticated:
        #     flash("You are already logged in.")
        #     return redirect(url_for('index'))
        # else:
        return render_template('login.html')

@auth.route("/signup", methods=['POST', 'GET'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    else:
        # Not logged in
        # Get request:
        if request.method == 'GET':
            return render_template('signup.html')

        # Post request:
        else:
            j_data = json.loads(request.get_json())
            username = j_data['username']
            email = j_data['email']
            password = j_data['password']

            if not username or not email or not password:
                return 'Missing fields.', 405

            else:
                # All good, check the database
                db_email = User.query.filter(User.email.ilike(email)).first()
                db_username = User.query.filter(User.username.ilike(username)).first()

                if db_email:
                    return 'Email already exists.', 405

                if db_username:
                    return 'Username already exists.', 405

                new_user = User(username, password, email, False)
                db.session.add(new_user)
                db.session.commit()

                login_user(new_user, remember=True)

                return "Done", 200



    # if not current_user.is_authenticated:
    #     if request.method == 'GET':
    #             return render_template("signup.html")
    #
    #     else:
    #         user, password = request.form['username'], request.form['password']
    #
    #         # TODO: validate email
    #         email = request.form['email']
    #
    #         if not user or not password or not email:
    #             flash('Missing fields.')
    #             return redirect(url_for("signup"))
    #
    #         else:
    #             # check if the username & email already exist
    #             q_email = User.query.filter(User.email.ilike(email)).first()
    #             q_username = User.query.filter(User.username.ilike(user)).first()
    #
    #             if q_email or q_username:
    #                 existance = []
    #
    #                 if q_email:
    #                     existance.append(email)
    #                 if q_username:
    #                     existance.append(user)
    #                 existance = ', '.join(i for i in existance)
    #
    #                 flash(f"{existance} already exist.")
    #                 return redirect(url_for('signup'))
    #
    #             else:
    #                 # register this new user
    #                 new_user = User(user, password, email, False)
    #                 db.session.add(new_user)
    #                 db.session.commit()
    #
    #                 login_user(new_user, remember=True)
    #
    #                 return redirect(url_for("index"))
    # else:
    #     flash("You are already logged in.")
    #     return redirect(url_for("index"))

@auth.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    if request.method == 'POST':
        logout_user()
        return url_for("index")
    if current_user.google:
        return redirect(url_for('login'))
    logout_user()
    return redirect(url_for('index'))

@auth.route("/gconnect", methods=['POST', 'GET'])
def gconnect():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            token = request.data
            try:
                # Specify the CLIENT_ID of the app that accesses the backend:
                idinfo = id_token.verify_oauth2_token(token, rqs.Request(),
                '957567508066-ju7cas7bvc93aqbpmr717gcpljojj070.apps.googleusercontent.com')

                if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                    raise ValueError('Wrong issuer.')

                # ID token is valid. Get the user's Google Account ID from the decoded token.
                email = idinfo['email']
                if email:
                    query = User.query.filter(User.email.ilike(email)).first()
                    if query and query.google:
                        login_user(query, remember=True)
                        current_user.google_signed = True
                        return url_for("index")

                    else:
                        new_user = User(email, '', email, True)

                        db.session.add(new_user)
                        db.session.commit()

                        login_user(new_user, remember=True)
                        current_user.google_signed = True

                        return url_for("index")

            except ValueError:
                return "Invalid token"
        else:
            return render_template("login.html")

                # return jsonify(idinfo)
    else:
        return redirect(url_for("login"))
