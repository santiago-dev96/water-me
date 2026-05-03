from flask import (
    Flask,
    request,
    render_template,
    flash,
    redirect,
    url_for,
    session,
    g,
    abort,
)
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.local import LocalProxy
import re
from functools import wraps

# We initalize the app.

app = Flask(__name__)

# We update the app configuration from the environment variables.

app.config.from_prefixed_env()

# Configure the database connection, SQLite by the way.


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DB_PATH"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


db = LocalProxy(get_db)

# If the INIT_DB configuration is passed, we run the script
# with the database schema. When the environment variable
# is "True" then the app configuration value will become
# 1.

if app.config.get("INIT_DB") == 1:
    with app.app_context():
        with app.open_resource("schema.sql", mode="r") as f:
            db.cursor().executescript(f.read())
        db.commit()


def sign_in_required(f):
    """Decorator for routes that require a valid session."""

    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return redirect(
                url_for("sign_in", values={"redirect_to": request.full_path})
            )
        else:
            cursor = db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            rows = cursor.fetchall()
            cursor.close()
            if len(rows) != 1:
                session.clear()
                return redirect(
                    url_for("sign_in", values={"redirect_to": request.full_path})
                )
        return f(*args, **kwargs)

    return decorated


@app.route("/")
@sign_in_required
def index():
    """Shows the plant status, but if you have none then a CTA."""

    # The the user plant. One per user, for now.

    cursor = db.execute("SELECT * FROM plants WHERE user_id = ?", (session["user_id"],))
    rows = cursor.fetchall()
    cursor.close()
    if len(rows) not in range(1):
        app.logger.error(
            f"Zero or one plants were expected but instead got {len(rows)}"
        )
        abort(500)
    if len(rows) == 0:
        plant = None
    else:
        plant = rows[0]
    return render_template("index.html", plant=plant)


@app.route("/add_plant", methods=["GET", "POST"])
@sign_in_required
def add_plant():
    """Shows a form to create a new plant and also saves the plant data."""

    if request.method == "GET":
        return render_template("add_plant.html")


@app.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    """Signs in or prompts for credentials"""

    # Render the sign-in form.

    if request.method == "GET":
        return render_template("sign_in.html")

    # Signs in the user if the credentials are correct.

    # We clear the session first.

    session.clear()

    # And now we validate the credentials.

    username = request.form.get("username")
    if not username:
        flash("Missing username", "danger")
        return render_template("sign_in.html"), 400
    password = request.form.get("password")
    if not password:
        flash("Missing password", "danger")
        return render_template("sign_in.html"), 400

    # Now try to get the user and update the session.

    cursor = db.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,),
    )
    rows = cursor.fetchall()
    cursor.close()
    if len(rows) > 1:
        flash("Internal server error", "danger")
        return render_template("sign_in.html")
    elif len(rows) == 0:
        flash("Invalid credentials", "danger")
        return render_template("sign_in.html"), 401
    user = rows[0]
    if not check_password_hash(user["password_hash"], password):
        flash("Invalid credentials", "danger")
        return render_template("sign_in.html"), 401
    session["user_id"] = user["id"]
    flash("You are signed in!", "success")
    if "redirect_to" in request.args:
        return redirect(request.args["redirect_to"])
    return redirect(url_for("index"))


# Thanks Copilot. This is a regular expression to validate email addresses.

email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"


@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    """Signs up a user or prompts for new credentials"""

    # Render the sign-up form.

    if request.method == "GET":
        return render_template("sign_up.html")

    # Get the username, strip the whitespace and validate it.

    username = request.form.get("username")
    if not username:
        flash("The username is required", "danger")
        return render_template("sign_up.html"), 400
    username = username.strip()
    if not re.fullmatch(email_regex, username):
        flash("Only email addresses can be used as usernames", "danger")
        return render_template("sign_up.html"), 400

    # Get the password, it should contain at least 1 digit, 1 letter,
    # a special character and that the password confirmation is equal
    # to the given password.

    password = request.form.get("password")
    if not password:
        flash("The password is required", "danger")
        return render_template("sign_up.html"), 400
    if len(password) < 12:
        flash("The lenght of the password must be at least 12 characters", "danger")
        return render_template("sign_up.html"), 400
    if len(password > 32):
        flash("The length of the password must be at most 32 characters", "danger")
        return render_template("sign_up.html"), 400
    if not re.search(r"\d", password):
        flash("The password must have at least one number", "danger")
        return render_template("sign_up.html"), 400
    if not re.search(r"[a-z]", password):
        flash("The password must have at least one lowercase letter", "danger")
        return render_template("sign_up.html"), 400
    if not re.search(r"[A-Z]", password):
        flash("The password must have at least one uppercase letter", "danger")
        return render_template("sign_up.html"), 400
    if not re.search(r"[^a-zA-Z0-9\s]", password):
        flash("The password must have at least one special character", "danger")
        return render_template("sign_up.html"), 400
    password_confirmation = request.form.get("password_confirmation")
    if not password_confirmation:
        flash("The password confirmation is required", "danger")
        return render_template("sign_up.html"), 400
    if password != password_confirmation:
        flash("The password and the password confirmation must be equal", " danger")
        return render_template("sign_up.html"), 400

    # Now save the user in the database.

    cursor = db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, generate_password_hash(password)),
    )
    db.commit()
    user_id = cursor.lastrowid
    cursor.close()

    # And start a session for the user.
    session["user_id"] = user_id

    return redirect(url_for("index"))


@app.route("/sign_out", methods=["POST"])
def sign_out():
    """Signs out the user."""

    session.clear()
    return redirect(url_for("sign_in"))


@app.errorhandler(500)
def internal_server_error(error):
    return render_template("internal_server_error.html"), 500


@app.teardown_appcontext
def close_connection(exception):
    if db:
        db.close()
