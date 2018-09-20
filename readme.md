# Item Catalog Project
The project uses [KnockoutJS](https://knockoutjs.com) library to handle the front-end at `static/base.js`. Ajax is used to handle requests with the Flask back-end.

## Config
Config file can be found at `/config/config.py`.

## Installation
You can quickly install the website by running `./install.sh`, this will do all the work needed to run the website. Then you can run the website: `python3 main.py`

You can pass an argument to the installation file to silent warnings and errors: `./install.sh -s`.

***Note**: Python 3.6 is recommended, also the latest versions of the required packages are recommended.*

***Note**: the installation file uses `pip3` to install the packages, absence of `pip3` will cause errors.*

A dumped copy of the sample database exists as `itemcatag_db`, If it wasn't loaded during the installation process, it can be restored using this command: `psql itemcatag_db < itemcatag_db` ([psql_dump](https://www.postgresql.org/docs/9.1/static/backup-dump.html)).

Manual install steps are included at the end of this file.

## Project specifications

### API endpoints:
Can be found at `/blueprints/api/v1/api.py`.

List of available api endpoints:
- `/api/v1/catagory/<name>` - Get items by name.
- `/search/<name>` or `/api/v1/item/<name>` - Search for items using a keyword.
- `/api/v1/item/<id>` - Get item by id.
- `/api/v1/items` - Get all the items.
- `/api/v1/catagories` - Get all the catagories.
- `/api/v1/users` - Get all the users. Login required. Results are shown in the browser's console.

### CRUD:
The website database is called: `itemcatag_db`. Automatically, the installation file will create the database and do the migrations to it.

- `manage.py` - [Flask-migrate](https://flask-migrate.readthedocs.io/en/latest/) is used to manage database changes.
- `models.py` - [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/2.3/) is used to manage CRUD operations.
There are two tables, `Users` and `Items`. Each one of them has a property to return a JSON-format of its content.
- `/blueprints/items/items_manager.py` - This file handles the CRUD operations (Add, Edit, View, Delete), also [Flask-Uploads](https://pythonhosted.org/Flask-Uploads/) is used to handle image uploading and fetching tasks.
- `main.py` - [CSRFProtect](https://flask-wtf.readthedocs.io/en/stable/csrf.html) is used to protect the website from CSRF attacks. At `/templates/base.html`, Ajax is using CSRF natively with any request.

### Authentication & Authorization:
- `/blueprints/auth/auth.py` - [Flask-Login](https://flask-login.readthedocs.io/en/latest/) is used to handle users login and logout operations.
- `main.py` - Line 86, the user login state always passed to KnockoutJS to determine when to allow certain views to load and when not. And the login state is used to set an observable value inside the KO ViewModel `mainViewModel`.
- `/blueprints/auth/auth.py` @ `/gconnect` route & at `/templates/base.html`, `/templates/login.html` - [Google Sign-in button](https://developers.google.com/identity/sign-in/web/server-side-flow) is used to login and register users. Login and Logout buttons are provided to the user using KnockoutJS.

### HTTPS:
I tried to achieve HTTPS, at `/config/`, the certification and the key can be found. At the end of `main.py`, you can uncomment a line that will launch the website using HTTPS instead of HTTP. And accessing it via `https://localhost:5000`.

## Manual Installation
### Install required packages:
`pip3 install --upgrade flask flask-migrate flask-script flask-sqlalchemy flask-wtf psycopg2-binary flask-login flask-uploads google-auth requests oauth2client google-api-python-client`

### Create the database:
`psql -c 'create database itemcatag_db'`

### Run migrations:
- `python3 manage.py db init`
- `python3 manage.py db migrate`
- `python3 manage.py db upgrade`

### (Optional) Load the sample database:
`psql itemcatag_db < itemcatag_db`
