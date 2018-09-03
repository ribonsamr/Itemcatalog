import os
from flask import Flask, flash, redirect, render_template, \
                  request, session, url_for, jsonify, send_from_directory, \
                  safe_join
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Item
from flask_wtf.csrf import CSRFProtect
from flask_login import current_user, login_user, logout_user, LoginManager, \
                        login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_uploads import *

upload_folder = 'uploads'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# Init a Flask application
app = Flask(__name__)

# Flask config
app.config.update(
    SECRET_KEY=os.urandom(16),
    HOST='0.0.0.0',
    DEBUG=True,
    JSONIFY_PRETTYPRINT_REGULAR=True,
    ENV="development",
    CSRF_ENABLED=True,
    SQLALCHEMY_DATABASE_URI='postgresql:///itemcatag_db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    UPLOADED_PHOTOS_DEST=upload_folder
)

# Load SQLAlchemy Db and CSRFProtect.
db.init_app(app)
csrf = CSRFProtect(app)

# flask-login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

photos = UploadSet('photos', IMAGES)
configure_uploads(app, (photos))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

    if file and allowed_file(file.filename):
        filename = photos.save(file)
        return filename, redirect(url_for('image_get', path=filename))


@app.route('/iview/<path>')
def image_get(path):
    photo = photos.url(path)
    if photo is None:
        abort(404)

    return redirect(photo)


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

            if not user or not password:
                flash('Missing fields.')
                return redirect(url_for("signup"))

            else:
                # check if the username already exists
                query = User.query.filter(User.username.ilike(user))

                if query.first():
                    flash("Username is taken.")
                    return redirect(url_for('signup'))

                else:
                    # register this new user
                    new_user = User(user, password)
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
        if current_user.is_authenticated:
            flash("You are already logged in.")
            return redirect(url_for('index'))
        else:
            return render_template('login.html')


@app.route("/add", methods=['POST', 'GET'])
@login_required
def add():
    if request.method == 'GET':
        return render_template('add.html')

    else:
        name, catag = request.form['name'], request.form['catag']

        if name and catag:
            query = Item.query.filter(Item.name.ilike(name),
                                      Item.catag.ilike(catag))
            if query.first():
                flash("Item: %s already exists." % (name))
                return redirect(url_for("add"))

            else:
                results = upload(request)
                if not results:
                    # No image file:
                    db.session.add(Item(name, catag, ''))

                else:
                    filename, redirection = results
                    db.session.add(Item(name, catag, filename))

                db.session.commit()

                flash("%s added in %s successfully." % (name, catag))

                return redirection or redirect(url_for("index"))

        else:
            flash("Missing input.")
            return redirect(url_for("add"))


@app.route('/<catag>/<name>')
def view(catag, name):
    query = Item.query.filter(Item.name.ilike(name),
                              Item.catag.ilike(catag)).first()
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


@app.route('/<catag>/<name>/delete', methods=['POST', 'GET'])
@login_required
def delete(catag, name):
    query = Item.query.filter(Item.name.ilike(name),
                              Item.catag.ilike(catag))

    if request.method == 'POST':
        exist_st = check_for_existance(query)
        if exist_st:
            return exist_st

        # remove the picture first
        file_path = photos.path(query.first().imgpath)
        os.remove(file_path)

        # then delete the item from the database, which delets the path of
        # the picture too.
        query.delete(synchronize_session=False)
        db.session.commit()

        flash("%s deleted successfully." % (f"{catag}/{name}"))
        return redirect(url_for("index"))

    else:
        return render_template("delete.html", query=query)


@app.route('/<catag>/<name>/edit', methods=['POST', 'GET'])
@login_required
def edit(catag, name):
    query = Item.query.filter(Item.name.ilike(name),
                              Item.catag.ilike(catag))

    if request.method == 'GET':
        return render_template('edit.html', query=query.first())

    else:
        exist_st = check_for_existance(query)
        if exist_st:
            return exist_st

        query = query.first()
        query.name = request.form['name']
        query.catag = request.form['catag']
        db.session.commit()

        flash(f"Updated successfully to: {query.name} - {query.catag}")
        return redirect(url_for("index"))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404


@app.route("/api/catagory/<name>")
def api_catag_view(name):
    query = Item.query.filter(Item.catag.ilike(name)).all()
    return jsonify([i.serialize for i in query])


@app.route("/api/item/<name>")
def api_item_view(name):
    query = Item.query.filter(Item.name.ilike(name)).all()
    return jsonify([i.serialize for i in query])


@app.route("/api/item/<int:id>")
def api_item_by_id(id):
    query = Item.query.get(id)
    return jsonify(query.serialize)


@app.route("/api/items")
def api_view_items_all():
    query = Item.query.all()
    return jsonify(Items=[i.serialize for i in query])


@app.route("/api/users")
def api_view_users_all():
    query = User.query.all()
    return jsonify(Users=[i.serialize for i in query])


if __name__ == '__main__':
    app.run(host='0.0.0.0')
