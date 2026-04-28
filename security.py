from flask import session, redirect, flash, request
from werkzeug.security import check_password_hash, generate_password_hash
from db import query_db
from functools import wraps

def check_credentials(username, password):
    user = query_db('SELECT * FROM users WHERE username = ?', [username], True)
    if not user:
        return None
    if not check_password_hash(user['password_hash'], password):
        return None
    return user['id']

def sign_in_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not 'user_id' in session:
            return redirect(f'/sign_in?redirect_to={request.path}')
        return f(*args, **kwargs)
    return decorated

def sign_up(username, password, password_confirmation):
    if password != password_confirmation:
        raise ValueError('password and password confirmation are not the same')
    user = query_db('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                    [username, generate_password_hash(password)],
                    True)
    return user['id']
