from models import db, User, Item
from api.api import api

from flask import Flask, flash, redirect, render_template, \
                  request, session, url_for, jsonify, send_from_directory, \
                  safe_join
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import current_user, login_user, logout_user, LoginManager, \
                        login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_uploads import *
from google.oauth2 import id_token
from google.auth.transport import requests as rqs



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




@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


def upload(request):
    if 'file' not in request.files:
        flash('No files attached.')
        return False

    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return False

    if file:
        filename = photos.save(file)
        return (filename, redirect(url_for('image_get', path=filename)))


@app.route('/iview/<path>')
def image_get(path):
    photo = photos.url(path)
    if photo is None:
        abort(404)

    return redirect(photo)


@app.route("/gconnect", methods=['POST', 'GET'])
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


@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if not current_user.is_authenticated:
        if request.method == 'GET':
                return render_template("signup.html")

        else:
            user, password = request.form['username'], request.form['password']

            # TODO: validate email
            email = request.form['email']

            if not user or not password or not email:
                flash('Missing fields.')
                return redirect(url_for("signup"))

            else:
                # check if the username & email already exist
                q_email = User.query.filter(User.email.ilike(email)).first()
                q_username = User.query.filter(User.username.ilike(user)).first()

                if q_email or q_username:
                    existance = []

                    if q_email:
                        existance.append(email)
                    if q_username:
                        existance.append(user)
                    existance = ', '.join(i for i in existance)

                    flash(f"{existance} already exist.")
                    return redirect(url_for('signup'))

                else:
                    # register this new user
                    new_user = User(user, password, email, False)
                    db.session.add(new_user)
                    db.session.commit()

                    login_user(new_user, remember=True)

                    return redirect(url_for("index"))
    else:
        flash("You are already logged in.")
        return redirect(url_for("index"))


@app.route("/login", methods=['POST', 'GET'])
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


@app.route("/add", methods=['POST', 'GET'])
@login_required
def add():
    if request.method == 'GET':
        return render_template('add.html')

    else:
        name, catagory = request.form['name'], request.form['catagory']

        if name and catagory:
            query = Item.query.filter(Item.name.ilike(name),
                                      Item.catagory.ilike(catagory))
            if query.first():
                flash("Item: %s already exists." % (name))
                return redirect(url_for("add"))

            else:
                results = upload(request)
                if not results:
                    # No image file:
                    db.session.add(Item(name, catagory, ''))
                    db.session.commit()
                    flash("%s added in %s successfully." % (name, catagory))
                    return redirect(url_for("index"))

                else:
                    # Image exists
                    filename, redirection = results
                    db.session.add(Item(name, catagory, filename))
                    db.session.commit()
                    flash("%s added in %s successfully." % (name, catagory))
                    return redirection

        else:
            flash("Missing input.")
            return redirect(url_for("add"))


@app.route('/<catagory>/<name>')
def view(catagory, name):
    query = Item.query.filter(Item.name.ilike(name),
                              Item.catagory.ilike(catagory)).first()
    return render_template('view.html', query=query)


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'GET':
        return render_template('view.html')

    else:

        if request.form['text']:
            query = Item.query.filter(Item.name.ilike(
                                      f"%{request.form['text']}%"))
            if query.first():
                return render_template('view.html', query=query)

            else:
                flash("Not found.")
                return redirect(url_for("search"))

        else:
            flash("Empty keyword.")
            return redirect(request.referrer or url_for("index"))


def check_for_existance(query):
    if not query.first():
        flash("Query not found.")
        return redirect(url_for("index"))

    else:
        None


@app.route('/<catagory>/<name>/delete', methods=['POST', 'GET'])
@login_required
def delete(catagory, name):
    query = Item.query.filter(Item.name.ilike(name),
                              Item.catagory.ilike(catagory))

    if request.method == 'POST':
        exist_st = check_for_existance(query)
        if exist_st:
            return exist_st

        # remove the picture first
        if query.first().image_filename:
            file_path = photos.path(query.first().image_filename)
            os.remove(file_path)

        # then delete the item from the database, which delets the path of
        # the picture too.
        query.delete(synchronize_session=False)
        db.session.commit()

        flash("%s deleted successfully." % (f"{catagory}/{name}"))
        return redirect(url_for("index"))

    else:
        return render_template("delete.html", query=query)


@app.route('/<catagory>/<name>/edit', methods=['POST', 'GET'])
@login_required
def edit(catagory, name):
    query = Item.query.filter(Item.name.ilike(name),
                              Item.catagory.ilike(catagory))

    if request.method == 'GET':
        return render_template('edit.html', query=query.first())

    else:
        exist_st = check_for_existance(query)
        if exist_st:
            return exist_st

        query = query.first()
        query.name = request.form['name']
        query.catagory = request.form['catagory']
        db.session.commit()

        flash(f"Updated successfully to: {query.name} - {query.catagory}")
        return redirect(url_for("index"))


@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    if request.method == 'POST':
        logout_user()
        return url_for("index")
    if current_user.google:
        return redirect(url_for('login'))
    logout_user()
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404



"""
    Automatically update static files
    http://flask.pocoo.org/snippets/40/
"""
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


if __name__ == '__main__':
    app.run(host='0.0.0.0')
