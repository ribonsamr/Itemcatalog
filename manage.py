from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

# import from main.py the flask app, and the models.py's db (SQLAlchemy)
from main import app, db

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
