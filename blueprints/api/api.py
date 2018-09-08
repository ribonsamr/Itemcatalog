from flask import Blueprint, jsonify
from models import User, Item

api = Blueprint('api', __name__)


@api.route("/api/catagory/<name>")
def api_catag_view(name):
    query = Item.query.filter(Item.catagory.ilike(name)).all()
    return jsonify([i.serialize for i in query])


@api.route("/api/item/<name>")
def api_item_view(name):
    query = Item.query.filter(Item.name.ilike(name)).all()
    return jsonify([i.serialize for i in query])


@api.route("/api/item/<int:id>")
def api_item_by_id(id):
    query = Item.query.get(id)
    return jsonify(query.serialize)


@api.route("/api/items")
def api_view_items_all():
    query = Item.query.all()
    return jsonify(Items=[i.serialize for i in query])


@api.route("/api/users")
def api_view_users_all():
    query = User.query.all()
    return jsonify(Users=[i.serialize for i in query])