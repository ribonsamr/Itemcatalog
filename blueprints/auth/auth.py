import json

from flask import Blueprint, request, url_for, redirect, render_template, flash
from flask_wtf.csrf import CSRFProtect
from flask_login import current_user, login_user, logout_user, LoginManager, \
                        login_required
from werkzeug.security import generate_password_hash, check_password_hash
from oauth2client import client

from models import db, User

auth = Blueprint('auth', __name__)

# Load CSRFProtect and LoginManager
csrf = CSRFProtect()
login_manager = LoginManager()

# Set the default route for login form to auth.login
login_manager.login_view = "auth.login"


# https://flask-login.readthedocs.io/en/latest/#flask_login.LoginManager.user_loader
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


# A GET request will return the page to login.
# A POST request will accept JSON data to login a user.
@auth.route("/login", methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        if request.method == 'GET':
            # if the user tries to access the login page, redirect him back to
            # home.
            return redirect(url_for('main'))

        # if the user tries to do a login again block the request.
        return "Already logged in", 403

    # not logged in
    if request.method == 'GET':
        return render_template('login.html')

    # load the username and password data from JSON
    j_data = json.loads(request.get_json())
    username = j_data['username']
    password = j_data['password']

    # check if there's any match in the db's usernames/emails with the
    # provided username. The user can log in using his username/email.
    query = User.query.filter(User.username.ilike(username)).first()
    if not query:
        query = User.query.filter(User.email.ilike(username)).first()

    if not query:
        return "Username/Password is wrong.", 405

    # if the user does exists, check his password.
    if check_password_hash(query.password, password):
        login_user(query, remember=True)
        return "OK", 200

    # otherwise, the password is wrong.
    return "Username/Password is wrong.", 405


# A GET request will return a page to sign up.
# A POST request will accept JSON data to sign up a user.
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
            # load JSON data
            j_data = json.loads(request.get_json())
            username = j_data['username']
            email = j_data['email']
            password = j_data['password']

            # if any field is missing, though the form inputs have
            # 'required' tags on them.
            if not username or not email or not password:
                return 'Missing fields.', 405

            else:
                # All good, check the database
                db_email = User.query.filter(User.email.ilike(email)).first()
                db_username = User.query.filter(
                              User.username.ilike(username)).first()

                # check if the data exists
                if db_email:
                    return 'Email already exists.', 405

                if db_username:
                    return 'Username already exists.', 405

                # register the user
                new_user = User(username, password, email, False)
                db.session.add(new_user)
                db.session.commit()

                # login the user
                login_user(new_user, remember=True)

                return "OK", 200

# Google Sign-in
# A POST request will accept a auth_code to use it.
@auth.route("/gconnect", methods=['POST'])
def gconnect():
    if current_user.is_authenticated:
        return "Already logged in.", 405

    auth_code = request.data

    CLIENT_SECRET_FILE = 'config/csec.json'

    credentials = client.credentials_from_clientsecrets_and_code(
                CLIENT_SECRET_FILE,
                ['https://www.googleapis.com/auth/drive.appdata',
                    'profile',
                    'email'],
                auth_code)

    # Get profile info from ID token
    email = credentials.id_token['email']

    if email:
        query = User.query.filter(User.email.ilike(email)).first()

        # if the user exists
        if query:
            # if he was registered via Google.
            if query.google:
                # log him in.
                login_user(query, remember=True)
                return "OK", 200

            # email exists, link google to it and sign him
            query.google = True
            db.session.commit()
            login_user(query)

            return "OK.", 200

        # New one, register the user
        new_user = User(email, '', email, True)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user, remember=True)

        return "OK", 200

    return "Missing email.", 405

    # except ValueError:
    #     return "Invalid token", 405


@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return "OK", 200
