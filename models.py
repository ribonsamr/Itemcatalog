from flask_sqlalchemy import SQLAlchemy
from flask import url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Init empty SQLAlchemy instance, will init the app later.
db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password
        }


class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    catag = db.Column(db.String, nullable=False)
    img_filename = db.Column(db.String())

    def __init__(self, name, catag, img_filename):
        self.name = name
        self.catag = catag
        self.img_filename = img_filename

    def __repr__(self):
        return '<Name %r>' % self.name

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'catagory': self.catag,
            'image_filename': self.img_filename
        }
