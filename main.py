from flask import Flask, redirect, render_template, request, url_for

from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from models import db, User, Item
from blueprints.api.api import api
from blueprints.auth.auth import auth
from blueprints.items.items_manager import items_manager

# ========== Init ==========
app = Flask(__name__)
csrf = CSRFProtect()
login_manager = LoginManager()
photos = UploadSet('photos', IMAGES)

# ========== Config ==========
app.config.from_pyfile('config.py')
app.register_blueprint(api)
db.init_app(app)
csrf.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "login"
configure_uploads(app, (photos))


@app.route("/")
@app.route("/home")
@app.route("/index")
def index():
    # load the users list and their password, for debug mode only.
    users = None
    if app.debug:
        users = User.query.all()

    # load the items to show them.
    items = Item.query.all()

    return render_template('index.html', data=users,
                           items=items)



@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404


# ====== Automatically update static files ======
#       http://flask.pocoo.org/snippets/40/
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
# ====== END ======


if __name__ == '__main__':
    app.run(host='0.0.0.0')
