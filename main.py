import os

from flask import Flask, flash, redirect, render_template, \
                  request, session, url_for

from flask_sqlalchemy import SQLAlchemy

# Import the models's SQLAlchemy db
from models import db

# Import the User model.
from models import User, Item

"""
Setup
"""
# Init a Flask application
app = Flask(__name__)

app.config['CSRF_ENABLED'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///main_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Load the app into the SQLAlchemy db
db.init_app(app)

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
    users = None
    if app.debug:
        users = User.query.all()

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
                # Check if the username already exists
                query = User.query.filter(User.username.ilike(user))

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
        query = User.query.filter(User.username.ilike(username),
                                  User.password.ilike(password))
        result = query.first()

        # If data exists, log the user in.
        if result:
            session['session_login_status'] = True
        else:
            flash('Wrong username or password: %s' % (username))

        return redirect(url_for('login'))

    else:
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
            query = Item.query.filter(Item.name.ilike(f"%{request.form['text']}%"))
            if query.first():
                return render_template('view.html', query=query)
            else:
                flash("Not found.")
                return redirect(url_for("search"))
        else:
            flash("Empty keyword.")
            return redirect(request.referrer or url_for("index"))

@app.route('/<catag>/<name>/delete', methods=['POST', 'GET'])
def delete_row(catag, name):
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
    app.secret_key = sKey = os.urandom(12)
    app.run(host='0.0.0.0', debug=True)
