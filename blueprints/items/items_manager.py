from flask import Blueprint
from flask_uploads import *

items_manager = Blueprint('/items', __name__)

@app.route('/<catagory>/<name>')
def view(catagory, name):
    query = Item.query.filter(Item.name.ilike(name),
                              Item.catagory.ilike(catagory)).first()
    return render_template('view.html', query=query)


@app.route("/add", methods=['POST', 'GET'])
@login_required
def add():
    if request.method == 'GET':
        return render_template('add.html')

    else:
        name, catagory = request.form['name'], request.form['catagory']

        if name and catagory:
            query = Item.query.filter(Item.name.ilike(name),
                                      Item.catagory.ilike(catagory))
            if query.first():
                flash("Item: %s already exists." % (name))
                return redirect(url_for("add"))

            else:
                results = upload(request)
                if not results:
                    # No image file:
                    db.session.add(Item(name, catagory, ''))
                    db.session.commit()
                    flash("%s added in %s successfully." % (name, catagory))
                    return redirect(url_for("index"))

                else:
                    # Image exists
                    filename, redirection = results
                    db.session.add(Item(name, catagory, filename))
                    db.session.commit()
                    flash("%s added in %s successfully." % (name, catagory))
                    return redirection

        else:
            flash("Missing input.")
            return redirect(url_for("add"))

@app.route('/<catagory>/<name>/delete', methods=['POST', 'GET'])
@login_required
def delete(catagory, name):
    query = Item.query.filter(Item.name.ilike(name),
                              Item.catagory.ilike(catagory))

    if request.method == 'POST':
        exist_st = check_for_existance(query)
        if exist_st:
            return exist_st

        # remove the picture first
        if query.first().image_filename:
            file_path = photos.path(query.first().image_filename)
            os.remove(file_path)

        # then delete the item from the database, which delets the path of
        # the picture too.
        query.delete(synchronize_session=False)
        db.session.commit()

        flash("%s deleted successfully." % (f"{catagory}/{name}"))
        return redirect(url_for("index"))

    else:
        return render_template("delete.html", query=query)
@app.route('/<catagory>/<name>/edit', methods=['POST', 'GET'])
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
