import os

SECRET_KEY = os.urandom(16)

HOST = '0.0.0.0'

ENV = "development"

SQLALCHEMY_DATABASE_URI = 'postgresql:///itemcatag_db'

UPLOADED_PHOTOS_DEST = 'uploads'

CSRF_ENABLED = True

DEBUG = True

SQLALCHEMY_TRACK_MODIFICATIONS = False

JSONIFY_PRETTYPRINT_REGULAR = True

TEMPLATES_AUTO_RELOAD = True
