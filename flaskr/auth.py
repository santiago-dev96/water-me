import functools
import re

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"


@bp.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    """Signs up a user or prompts for new credentials"""

    # Render the sign-up form.

    if request.method == "GET":
        return render_template("auth/sign_up.html")

    # Get the username, strip the whitespace and validate it.

    username = request.form.get("username")
    if not username:
        flash("The username is required", "danger")
        return render_template("auth/sign_up.html", form=request.form), 400
    username = username.strip()
    if not re.fullmatch(email_regex, username):
        flash("Only email addresses can be used as usernames", "danger")
        return render_template("auth/sign_up.html", form=request.form), 400

    # Get the password, it should contain at least 1 digit, 1 letter,
    # a special character and that the password confirmation is equal
    # to the given password. The length of the password should be
    # at least 12 and at most 32.

    password = request.form.get("password")
    if not password:
        flash("The password is required", "danger")
        return render_template("auth/sign_up.html", form=request.form), 400
    if len(password) < 12:
        flash("The length of the password must be at least 12 characters", "danger")
        return render_template("auth/sign_up.html", form=request.form), 400
    if len(password) > 32:
        flash("The length of the password must be at most 32 characters", "danger")
        return render_template("auth/sign_up.html", form=request.form), 400
    if not re.search(r"\d", password):
        flash("The password must have at least one number", "danger")
        return render_template("auth/sign_up.html", form=request.form), 400
    if not re.search(r"[a-z]", password):
        flash("The password must have at least one lowercase letter", "danger")
        return render_template("auth/sign_up.html", form=request.form), 400
    if not re.search(r"[A-Z]", password):
        flash("The password must have at least one uppercase letter", "danger")
        return render_template("auth/sign_up.html", form=request.form), 400
    if not re.search(r"[^a-zA-Z0-9\s]", password):
        flash("The password must have at least one special character", "danger")
        return render_template("auth/sign_up.html", form=request.form), 400
    password_confirmation = request.form.get("password_confirmation")
    if not password_confirmation:
        flash("The password confirmation is required", "danger")
        return render_template("auth/sign_up.html", form=request.form), 400
    if password != password_confirmation:
        flash("The password and the password confirmation must be equal", "danger")
        return render_template("auth/sign_up.html", form=request.form), 400

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

    return redirect(url_for("plants.index"))


@bp.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    """Signs in or prompts for credentials"""

    # Render the sign-in form.

    if request.method == "GET":
        return render_template("auth/sign_in.html")

    # Signs in the user if the credentials are correct.

    # We clear the session first.

    session.clear()

    # And now we validate the credentials.

    username = request.form.get("username")
    if not username:
        flash("Missing username", "danger")
        return render_template("auth/sign_in.html"), 400
    password = request.form.get("password")
    if not password:
        flash("Missing password", "danger")
        return render_template("auth/sign_in.html"), 400

    # Now try to get the user and update the session.

    db = get_db()
    cursor = db.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,),
    )
    rows = cursor.fetchall()
    cursor.close()
    if len(rows) > 1:
        flash("Internal server error", "danger")
        return render_template("auth/sign_in.html")
    elif len(rows) == 0:
        flash("Invalid credentials", "danger")
        return render_template("auth/sign_in.html"), 401
    user = rows[0]
    if not check_password_hash(user["password_hash"], password):
        flash("Invalid credentials", "danger")
        return render_template("auth/sign_in.html"), 401
    session["user_id"] = user["id"]
    flash("You are signed in!", "success")
    if "redirect_to" in request.args:
        return redirect(request.args["redirect_to"])
    return redirect(url_for("plants.index"))


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
                'SELECT * FROM users WHERE id = ?', (user_id,)
                ).fetchone()


@bp.route('/sign_out', methods=['POST'])
def sign_out():
    """Signs out the user."""

    session.clear()
    flash("You are signed out", "info")
    return redirect(url_for("auth.sign_in"))


def sign_in_required(view):
    """Decorator for routes that require a session."""

    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(
                    url_for("auth.sign_in",
                            redirect_to=request.full_path)
                    )
        return view(*args, **kwargs)

    return wrapped_view

