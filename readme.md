# Item Catalog Project

## Installation
You can quickly install the website by running `./install.sh`, this install file will do all the work needed to run this website. Then you can run the website: `python3 main.py`

***Note**: Python 3.6 is recommended, also the latest versions of the required packages is recommended.*

***Note**: the installation file uses `pip3` to install the packages, absence of `pip3` will cause errors.*

Manual install steps are included in the end of this file.

## Project specifications

### API endpoints:
Can be found at `/blueprints/api/api.py`.

List of available api endpoints:
- `/api/catagory/<name>` - Get items by name.
- `/search/<name>` or `/api/item/<name>` - Search for items using a keyword.
- `/api/item/<id>` - Get item by id.
- `/api/items` - Get all the items.
- `/api/catagories` - Get all the catagories.
- `/api/users` - Get all the users. Login required. Results are shown in the browser's console.

### CRUD:
The website database is called: `itemcatag_db`. Automatically, the installation file will create the database and do the migrations to it.

@`manage.py` - [Flask-migrate](https://flask-migrate.readthedocs.io/en/latest/) is used to manage database changes.

@`models.py` - [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/2.3/) is used to manage CRUD operations.
There are two tables, `Users` and `Items`. Each one of them has a property to return a JSON-format of its content.