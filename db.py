from flask import Flask
from flask import flash, redirect, render_template, request, session, abort, url_for

import os

app = Flask(__name__)

@app.route("/")
def index():
    if not session.get('loggedin'):
        return "<a href='login'>login</a>"
    else:
        return "<a href='logout'>logout</a>"

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if request.form['password'] == '123' and request.form['username'] == 'amr':
            session['loggedin'] = True
        else:
            flash('wrong password')
        return redirect(url_for('index'))
    else:
        if not session.get('loggedin'):
            return render_template('login.html')
        else:
            return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session['loggedin'] = False
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404


app.secret_key = sKey = os.urandom(12)
app.run(host='0.0.0.0', debug=True)
