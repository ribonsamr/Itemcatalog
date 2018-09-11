import os

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_uploads import configure_uploads
from flask_login import current_user

from blueprints.api.api import api
from blueprints.auth.auth import auth, csrf, login_manager
from blueprints.items.items_manager import items_manager, photos

from models import db, User, Item


app = Flask(__name__)

# load flask config file
app.config.from_pyfile  ('config/config.py')

# init SQLAlchemy
db.init_app             (app)

# init CSRFProtect
csrf.init_app           (app)

# init login_manager
login_manager.init_app  (app)

# init flask_uploads
configure_uploads       (app, (photos))

# register the blueprints [api, auth, items_manager]
app.register_blueprint  (api)
app.register_blueprint  (auth)
app.register_blueprint  (items_manager)


@app.route('/')
@app.route('/index')
@app.route('/home')
def main():
    return render_template('index.html')


@app.route('/items')
def items():
    return render_template('items.html')


# for testing purposes
# @app.route('/test', methods=['POST'])
# def test():
#     form = request.form
#     if 'file' in request.files:
#         print(request.files['file'])
#     return "OK"


# @app.errorhandler(404)
# def not_found(error):
#     return render_template('error.html'), 404


# Automatically update static files
# http://flask.pocoo.org/snippets/40/
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)
# ========================================================

# pass the current_user authentication state always to
# the front-end (Knockout.JS)
@app.context_processor
def current_user_authed():
    return dict(current_user_authed=str(current_user.is_authenticated).lower())


if __name__ == '__main__':
    # uncomment next line to enable HTTPS
    # app.run('0.0.0.0', ssl_context=('config/cert.pem', 'config/key.pem'))
    app.run('0.0.0.0', port=5000)
