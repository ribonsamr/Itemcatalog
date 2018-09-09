from flask import Blueprint, request, url_for, redirect, render_template, flash
from flask_wtf.csrf import CSRFProtect
from flask_login import current_user, login_user, logout_user, LoginManager, \
                        login_required
from werkzeug.security import generate_password_hash, check_password_hash
from apiclient import discovery
import httplib2
from oauth2client import client

from models import db, User

import json

auth = Blueprint('auth', __name__)

csrf = CSRFProtect()
login_manager = LoginManager()

login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@auth.route("/login", methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        if request.method == 'GET':
            return redirect(url_for('main'))

        return "Already logged in", 403

    # not logged in
    if request.method == 'GET':
        return render_template('login.html')

    j_data = json.loads(request.get_json())
    username = j_data['username']
    password = j_data['password']

    query = User.query.filter(User.username.ilike(username)).first()
    if not query:
        query = User.query.filter(User.email.ilike(username)).first()

    if not query:
        return "Username/Password is wrong.", 405

    if query.google:
        pass

    if check_password_hash(query.password, password):
        login_user(query, remember=True)
        return "OK", 200

    return "Username/Password is wrong.", 405


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

                return "OK", 200


@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return "OK", 200


@auth.route("/gconnect", methods=['POST'])
def gconnect():
    if current_user.is_authenticated:
        return "Already logged in.", 405

    auth_code = request.data

    CLIENT_SECRET_FILE = 'config/csec.json'

    credentials = client.credentials_from_clientsecrets_and_code(
    CLIENT_SECRET_FILE,
    ['https://www.googleapis.com/auth/drive.appdata', 'profile', 'email'],
    auth_code)

    # Get profile info from ID token
    email = credentials.id_token['email']

    if email:
        query = User.query.filter(User.email.ilike(email)).first()
        if query:
            if query.google:
                login_user(query, remember=True)
                return "OK", 200

            return "Email exists.", 405

        # New one, register the user
        new_user = User(email, '', email, True)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user, remember=True)

        return "OK", 200

    return "Missing email.", 405

    # except ValueError:
    #     return "Invalid token", 405
