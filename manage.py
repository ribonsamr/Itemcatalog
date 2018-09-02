import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from main import app, db

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///main_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
