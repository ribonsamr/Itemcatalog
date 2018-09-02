from flask_sqlalchemy import SQLAlchemy

# Init empty SQLAlchemy instance, will init the app later.
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username


class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    catag = db.Column(db.String, nullable=False)

    def __init__(self, name, catag):
        self.name = name
        self.catag = catag

    def __repr__(self):
        return '<Name %r>' % self.name
