from flask import Blueprint, jsonify
from models import User, Item, db
from flask_login import login_required

api = Blueprint('api', __name__)


# Item from a specific catagory
@api.route("/api/catagory/<name>")
def api_catag_view(name):
    query = Item.query.filter(Item.catagory.ilike(name)).all()
    return jsonify([i.serialize for i in query])


# Items hold the name: <name>
@api.route("/api/item/<name>")
def api_item_view(name):
    query = Item.query.filter(Item.name.ilike(name)).all()
    return jsonify([i.serialize for i in query])


# Item with id: <id>
@api.route("/api/item/<int:id>")
def api_item_by_id(id):
    query = Item.query.get(id)
    return jsonify(query.serialize)


# All the items in the database
@api.route("/api/items")
def api_view_items_all():
    query = Item.query.all()
    return jsonify([i.serialize for i in query])


# All the catagories in the database
@api.route("/api/catagories")
def api_view_catagories_all():
    query = db.session.query(Item.catagory)
    results = query.group_by(Item.catagory).all()

    catagories = [i[0] for i in results]

    return jsonify(catagories)


# All the users in the database
@api.route("/api/users")
@login_required
def api_view_users_all():
    query = User.query.all()
    return jsonify([i.serialize for i in query])
