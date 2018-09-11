import os
import json

from flask import Blueprint, request
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_login import login_required

from models import Item, db

items_manager = Blueprint('/items', __name__)

photos = UploadSet('photos', IMAGES)


@items_manager.route('/<catagory>/<name>')
def view_by_data(catagory, name):
    query = Item.query.filter(Item.name.ilike(name),
                              Item.catagory.ilike(catagory)).first()
    return render_template('view.html', query=query)


@items_manager.route("/add", methods=['POST'])
@login_required
def add():
    item_name = request.form.get('name')
    item_catagory = request.form.get('catagory')
    item_file = ''

    if 'file' in request.files:
        print(request.files['file'])
        item_file = request.files['file']

    if not item_name or not item_catagory:
        return "Missing fields.", 405

    query = Item.query.filter(Item.name.ilike(item_name),
                              Item.catagory.ilike(item_catagory)).first()

    if query:
        return "Already exists", 405

    if item_file:
        filename = photos.save(item_file)
        # return (filename, redirect(url_for('image_get', path=filename)))
        db.session.add(Item(item_name, item_catagory, filename))
        db.session.commit()
        return "OK", 200

    db.session.add(Item(item_name, item_catagory, ''))
    db.session.commit()

    return "OK", 200


@items_manager.route('/image', methods=['POST'])
def get_image():
    file_url = photos.url(request.values['filename'])
    return file_url


@items_manager.route('/delete', methods=['POST'])
@login_required
def delete():
    j_data = request.get_json()

    item_id = j_data['id']

    query = Item.query.filter(Item.id == item_id)

    if not query:
        return "Not found", 404

    item = query.first()

    if item.image_filename:
        file_path = photos.path(item.image_filename)
        os.remove(file_path)

    query.delete(synchronize_session=False)
    db.session.commit()

    return "OK", 200


@items_manager.route('/edit', methods=['POST'])
@login_required
def edit():
    j_data = request.get_json()

    item_id = j_data['id']
    item_name = j_data['name']
    item_catagory = j_data['catagory']

    query = Item.query.filter(Item.id == item_id)

    if not query:
        return "Not found", 404

    query = query.first()
    query.name = item_name
    query.catagory = item_catagory
    db.session.commit()

    return "OK", 200
