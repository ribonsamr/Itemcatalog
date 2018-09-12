from flask import Blueprint, jsonify
from models import User, Item, Catagory, db
from flask_login import login_required

api = Blueprint('api', __name__)


# Item from a specific catagory
@api.route("/api/v1/catagory/<name>")
def api_catag_view(name):
    query = Item.query.filter(Item.catagory.ilike(name)).all()
    return jsonify([i.serialize for i in query])


# Items hold the name: <name>
@api.route('/search/<name>')
@api.route("/api/v1/item/<name>")
def api_item_view(name):
    query = Item.query.filter(Item.name.ilike(name)).all()
    if not query:
        return "Not found", 404

    return jsonify([i.serialize for i in query])


# Item with id: <id>
@api.route("/api/v1/item/<int:id>")
def api_item_by_id(id):
    query = Item.query.get(id)
    return jsonify(query.serialize)


# All the items in the database
@api.route("/api/v1/items")
def api_view_items_all():
    query = Item.query.all()
    return jsonify([i.serialize for i in query])


# All the catagories in the database
@api.route("/api/v1/catagories")
def api_view_catagories_all():
    query = Catagory.query.all()
    return jsonify([i.serialize for i in query])


# All the users in the database
@api.route("/api/v1/users")
@login_required
def api_view_users_all():
    query = User.query.all()
    return jsonify([i.serialize for i in query])
