from flask import Blueprint, jsonify
from models import User, Item
from flask_login import login_required

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
    return jsonify([i.serialize for i in query])


@api.route("/api/users")
@login_required
def api_view_users_all():
    query = User.query.all()
    return jsonify([i.serialize for i in query])
