from flask_sqlalchemy import SQLAlchemy
from flask import url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# init a SQLAlchemy instance, will init the app later in the main.py file.
db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id        = db.Column(db.Integer, primary_key=True, nullable=False)
    username  = db.Column(db.String, unique=True, nullable=False)
    password  = db.Column(db.String)
    email     = db.Column(db.String, unique=True, nullable=False)
    google    = db.Column(db.Boolean, nullable=False)


    def __init__(self, username, password, email, google):
        self.username = username
        self.password = generate_password_hash(password)
        self.email = email
        self.google = google


    def __repr__(self):
        return '<User %r>' % self.username


    # return a JSON format of the user.
    @property
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'google account': self.google
        }



class Item(db.Model):
    __tablename__ = "items"

    id              = db.Column(db.Integer, primary_key=True, nullable=False)
    name            = db.Column(db.String, nullable=False)
    catagory        = db.Column(db.String, nullable=False)
    image_filename  = db.Column(db.String


    def __init__(self, name, catagory, image_filename):
        self.name = name
        self.catagory = catagory
        self.image_filename = image_filename


    def __repr__(self):
        return '<Name %r>' % self.name


    # return a JSON format of the item.
    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'catagory': self.catagory,
            'image_filename': self.image_filename
        }
