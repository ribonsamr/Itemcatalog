import os
from flask import Flask, flash, redirect, render_template, \
                  request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from models import db
from models import User, Item
from flask_wtf.csrf import CSRFProtect

# Init a Flask application
app = Flask(__name__)

# Flask config
app.config.update(
    SECRET_KEY=os.urandom(16)
    HOST='0.0.0.0',
    DEBUG=True,
    ENV="development",
    CSRF_ENABLED=True,
    SQLALCHEMY_DATABASE_URI='postgresql:///main_db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

# Load SQLAlchemy Db and CSRFProtect.
db.init_app(app)
csrf = CSRFProtect(app)


# Check if the user is logged in or not.
def logged(session):
    return bool(session.get("session_login_status"))


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

    if not logged(session):
        return render_template('index.html', logged=False, data=users,
                               items=items)
    else:
        return render_template('index.html', logged=True, data=users,
                               items=items)


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

                    session['session_login_status'] = True

                    return redirect(url_for("index"))


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']

        # get the data from the database
        query = User.query.filter(User.username.ilike(username),
                                  User.password.ilike(password))
        result = query.first()

        # if data exists, log the user in.
        if result:
            session['session_login_status'] = True
        else:
            flash('Wrong username or password: %s' % (username))

        return redirect(url_for('login'))

    else:
        # redirect the user to index or login based on his log in status.
        if logged(session):
            return redirect(url_for('index'))
        else:
            return render_template('login.html')


@app.route("/add", methods=['POST', 'GET'])
def add():
    if logged(session):
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
                    db.session.add(Item(name, catag))
                    db.session.commit()

                    flash("%s added in %s successfully." % (name, catag))

                    return redirect(url_for("index"))
            else:
                flash("Missing input.")
                return redirect(url_for("add"))
    else:
        flash("We're sorry, this page is only for member."
              + "If you have an account please log in")

        return redirect(url_for("index"))


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


@app.route('/<catag>/<name>/delete', methods=['POST', 'GET'])
def delete(catag, name):
    query = Item.query.filter(Item.name.ilike(name),
                              Item.catag.ilike(catag))
    if request.method == 'POST':
        query.delete(synchronize_session=False)
        db.session.commit()

        flash("%s deleted successfully." % (f"{catag}/{name}"))
        return redirect(url_for("index"))
    else:
        return render_template("delete.html", query=query)


@app.route('/<catag>/<name>/edit', methods=['POST', 'GET'])
def edit(catag, name):
    if logged(session):
        query = Item.query.filter(Item.name.ilike(name),
                                  Item.catag.ilike(catag)).first()
        if request.method == 'GET':
            return render_template('edit.html', query=query)
        else:
            query.name = request.form['name']
            query.catag = request.form['catag']
            db.session.commit()
            flash(f"Updated successfully to: {query.name} - {query.catag}")

            return redirect(url_for("index"))
    else:
        flash("You need to log in first.")
        return redirect(url_for("login"))


@app.route('/logout')
def logout():
    session['session_login_status'] = False
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0')
