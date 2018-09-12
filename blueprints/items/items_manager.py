import os
import json

from flask import Blueprint, request
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_login import login_required, current_user

from models import Item, Catagory, db

items_manager = Blueprint('/items', __name__)

# init Flask-uploads
photos = UploadSet('photos', IMAGES)


# check if there is a catagory by this name, otherwise, create a new one.
def check_catagory(name):
    query = Catagory.query.filter(Catagory.name.ilike(name))
    if not query.first():
        db.session.add(Catagory(name))
        db.session.commit()


# A POST request will parse form data to add a new item.
# An image is not required, and a record can be added without it.
@items_manager.route("/add", methods=['POST'])
@login_required
def add():
    item_name = request.form.get('name')
    item_catagory = request.form.get('catagory')
    item_file = ''

    # check if a file was included
    if 'file' in request.files:
        # print(request.files['file'])
        item_file = request.files['file']

    # block the request if fields are missing
    if not item_name or not item_catagory:
        return "Missing fields.", 405

    check_catagory(item_catagory)
    query = Item.query.filter(Item.name.ilike(item_name),
                              Item.catagory.ilike(item_catagory)).first()

    # if a query of the same data exists
    if query:
        return "Already exists", 405

    # if a file was included, save it and link it to the item in the db.
    if item_file:
        filename = photos.save(item_file)
        db.session.add(Item(item_name, item_catagory, filename, current_user.id))
        db.session.commit()
        return "OK", 200

    # add the item to the db
    db.session.add(Item(item_name, item_catagory, '', current_user.id))
    db.session.commit()

    return "OK", 200


# A POST will receive a filename of a record, and will return a full path
# to the image.
@items_manager.route('/image', methods=['POST'])
def get_image():
    file_url = photos.url(request.values['filename'])
    return file_url


# A POST request will get JSON data about a record to delete.
@items_manager.route('/delete', methods=['POST'])
@login_required
def delete():
    j_data = request.get_json()

    item_id = j_data['id']

    query = Item.query.filter(Item.id == item_id)

    if not query:
        return "Not found", 404

    item = query.first()

    user_id = item.user_id
    if user_id != int(current_user.get_id()):
        return "Not allowed for you.", 405

    # check if the item has an image linked to it, then delete it.
    if item.image_filename:
        file_path = photos.path(item.image_filename)
        os.remove(file_path)

    # then delete the item
    query.delete(synchronize_session=False)
    db.session.commit()

    return "OK", 200


# A POST request will receive a JSON data with the modified record to commit.
@items_manager.route('/edit', methods=['POST'])
@login_required
def edit():
    j_data = request.get_json()

    item_id = j_data['id']
    item_name = j_data['name']
    item_catagory = j_data['catagory']

    # use the id to find the item in the db
    query = Item.query.filter(Item.id == item_id)

    check_catagory(item_catagory)

    # if the item doesn't exists, block the request
    if not query:
        return "Not found", 404

    # modify the record and commit it.
    query = query.first()

    user_id = query.user_id
    if user_id != int(current_user.get_id()):
        return "Not allowed for you.", 405

    query.name = item_name
    query.catagory = item_catagory
    db.session.commit()

    return "OK", 200
