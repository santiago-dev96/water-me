import functools
import re

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registers a user account."""

    # Render the sign-up form.

    if request.method == "GET":
        return render_template("auth/register.html")
    
    # Validate the username
    
    username = request.form.get('username')
    if not username:
        flash('The username is required', 'danger')
        return render_template('auth/register.html', form=request.form), 400
    if username.strip() == '':
        flash('The username is just whitespace', 'danger')
        return render_template('auth/register.html', form=request.form), 400
    if len(username) < 3:
        flash('The length of the username must be greater than 3', 'danger')
        return render_template('auth/register.html', form=request.form), 400
    if len(username) > 50:
        flash('The length of the username must be less than 50', 'danger')
        return render_template('auth/register.html', form=request.form), 400

    # Get the password, it should contain at least 1 digit, 1 letter,
    # a special character and that the password confirmation is equal
    # to the given password. The length of the password should be
    # at least 12 and at most 32.

    password = request.form.get("password")
    if not password:
        flash("The password is required", "danger")
        return render_template("auth/register.html", form=request.form), 400
    if len(password) < 12:
        flash("The length of the password must be at least 12 characters", "danger")
        return render_template("auth/register.html", form=request.form), 400
    if len(password) > 32:
        flash("The length of the password must be at most 32 characters", "danger")
        return render_template("auth/register.html", form=request.form), 400
    if not re.search(r"\d", password):
        flash("The password must have at least one number", "danger")
        return render_template("auth/register.html", form=request.form), 400
    if not re.search(r"[a-z]", password):
        flash("The password must have at least one lowercase letter", "danger")
        return render_template("auth/register.html", form=request.form), 400
    if not re.search(r"[A-Z]", password):
        flash("The password must have at least one uppercase letter", "danger")
        return render_template("auth/register.html", form=request.form), 400
    if not re.search(r"[^a-zA-Z0-9\s]", password):
        flash("The password must have at least one special character", "danger")
        return render_template("auth/register.html", form=request.form), 400
    password_confirmation = request.form.get("password_confirmation")
    if not password_confirmation:
        flash("The password confirmation is required", "danger")
        return render_template("auth/register.html", form=request.form), 400
    if password != password_confirmation:
        flash("The password and the password confirmation must be equal", "danger")
        return render_template("auth/register.html", form=request.form), 400

    # Now save the user in the database.

    db = get_db()
    cursor = db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, generate_password_hash(password)),
    )
    db.commit()
    user_id = cursor.lastrowid
    cursor.close()

    # And start a session for the user.
    session["user_id"] = user_id

    return redirect(url_for("cultivation_plots.index"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Logs in the user account."""

    # Render the login form.

    if request.method == "GET":
        return render_template("auth/login.html")

    # Logs in the user if the credentials are correct.

    # We clear the session first.

    session.clear()

    # And now we validate the credentials.

    username = request.form.get("username")
    if not username:
        flash("Missing username", "danger")
        return render_template("auth/login.html"), 400

    password = request.form.get("password")
    if not password:
        flash("Missing password", "danger")
        return render_template("auth/login.html"), 400

    # Now try to get the user and update the session.

    db = get_db()
    cursor = db.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    some_user = cursor.fetchone()
    cursor.close()
    if not some_user:
        flash("There is no user account in the database with the given username", "danger")
        return render_template("auth/register.html"), 500
    if not check_password_hash(some_user["password_hash"], password):
        flash("Invalid password", "danger")
        return render_template("auth/login.html"), 401
    session["user_id"] = some_user["id"]
    flash("You're logged in.", "success")
    if "redirect_to" in request.args:
        return redirect(request.args["redirect_to"])
    return redirect(url_for("cultivation_plots.index"))


@bp.before_app_request
def load_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
                'SELECT * FROM users WHERE id = ?', (user_id,)
                ).fetchone()


@bp.route('/logout', methods=['POST'])
def logout():
    """Logs out the user."""

    session.clear()
    flash("You're logged out", "info")
    return redirect(url_for("auth.logout"))


def login_required(view):
    """Decorator for routes that require a session."""

    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(
                    url_for("auth.login",
                            redirect_to=request.full_path)
                    )
        return view(*args, **kwargs)

    return wrapped_view

