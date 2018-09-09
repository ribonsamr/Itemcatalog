from flask import Blueprint, request
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_login import login_required

from models import Item, db

import json

items_manager = Blueprint('/items', __name__)

photos = UploadSet('photos', IMAGES)

@items_manager.route('/<catagory>/<name>')
def view_by_data(catagory, name):
    query = Item.query.filter(Item.name.ilike(name),
                              Item.catagory.ilike(catagory)).first()
    return render_template('view.html', query=query)


@items_manager.route('/<filename>')
def view_by_file(filename):
    query = Item.query.filter(Item.name.ilike(name),
                              Item.catagory.ilike(catagory)).first()
    return render_template('view.html', query=query)


@items_manager.route("/add", methods=['POST'])
@login_required
def add():
    j_data = json.loads(request.get_json())
    item_name = j_data['itemName']
    item_catagory = j_data['itemCatagory']

    if not item_name or not item_catagory:
        return "Missing fields.", 405

    query = Item.query.filter(Item.name.ilike(item_name),
                              Item.catagory.ilike(item_catagory)).first()

    if query:
        return "Already exists", 405

    db.session.add(Item(item_name, item_catagory, ''))
    db.session.commit()

    return "OK", 200


@items_manager.route('/delete', methods=['POST'])
@login_required
def delete():
    j_data = json.loads(request.get_json())
    item_name = j_data['itemName']
    item_catagory = j_data['itemCatagory']

    query = Item.query.filter(Item.name.ilike(item_name),
                              Item.catagory.ilike(item_catagory))

    if not query.first():
        return "Not found", 404

    query.delete(synchronize_session=False)
    db.session.commit()

    return "OK", 200
        # # remove the picture first
        # if query.first().image_filename:
        #     file_path = photos.path(query.first().image_filename)
        #     os.remove(file_path)

        # then delete the item from the database, which delets the path of
        # the picture too.

@items_manager.route('/<catagory>/<name>/edit', methods=['POST', 'GET'])
@login_required
def edit(catagory, name):
    query = Item.query.filter(Item.name.ilike(name),
                              Item.catagory.ilike(catagory))

    if request.method == 'GET':
        return render_template('edit.html', query=query.first())

    else:
        exist_st = check_for_existance(query)
        if exist_st:
            return exist_st

        query = query.first()
        query.name = request.form['name']
        query.catagory = request.form['catagory']
        db.session.commit()

        flash(f"Updated successfully to: {query.name} - {query.catagory}")
        return redirect(url_for("index"))
def upload(request):
    if 'file' not in request.files:
        flash('No files attached.')
        return False

    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return False

    if file:
        filename = photos.save(file)
        return (filename, redirect(url_for('image_get', path=filename)))
