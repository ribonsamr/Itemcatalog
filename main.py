import os

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_uploads import configure_uploads
from flask_login import current_user

from models import db, User, Item

from blueprints.api.api import api
from blueprints.auth.auth import auth, csrf, login_manager
from blueprints.items.items_manager import items_manager, photos

app = Flask(__name__)

app.config.from_pyfile  ('config.py')
db.init_app             (app)
csrf.init_app           (app)
login_manager.init_app  (app)
configure_uploads       (app, (photos))

app.register_blueprint  (api)
app.register_blueprint  (auth)
app.register_blueprint  (items_manager)


@app.route('/')
@app.route('/index')
@app.route('/home')
def main():
    return render_template('index.html')


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


@app.context_processor
def current_user_authed():
    return dict(current_user_authed=str(current_user.is_authenticated).lower())


if __name__ == '__main__':
    # app.run(ssl_context=('cert.pem', 'key.pem'))
    app.run('0.0.0.0', port=5000)
