import os
from db import init_db, close_db
from flask import Flask, request, render_template, flash, redirect, url_for, session
from security import check_credentials, sign_in_required, sign_up

app = Flask(__name__)

if os.getenv('INIT_DB') == 'True':
    init_db(app)

@app.route('/')
@sign_in_required
def index():
    return render_template('index.html')

@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    """Signs in or prompts for credentials"""

    # Render the sign-in form.

    if request.method == 'GET':
        return render_template('sign_in.html')
    
    # Signs in the user if the credentials are correct.

    session.clear()
    id = check_credentials(request.form.get('usename'), request.form.get('password'))
    if not id:
        flash('Invalid credentials', 'error')
        return render_template('sign_in.html'), 401
    session['user_id'] = id
    flash('You are signed in!', 'success')
    if 'redirect_to' in request.args:
        return redirect(request.args['redirect_to'])
    return redirect(url_for('index'))


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    """Signs up a user or prompts for new credentials"""

    # Render the sign-up form.

    if request.method == 'GET':
        return render_template('sign_up.html')
    
    # Register the new user in the database.

    username = request.form.get('username')
    password = request.form.get('password')
    password_confirmation = request.form.get('password_confirmation')
    try:
        session['user_id'] = sign_up(username, password, password_confirmation)
    except ValueError as e:
        app.logger.error(e)
        flash('Could not sign you up', 'error')
        return render_template('sign_up.html'), 400
    return redirect(url_for('index'))

@app.teardown_appcontext
def close_connection(exception):
    close_db()