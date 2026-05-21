import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, abort, current_app
)
from werkzeug.utils import secure_filename
from uuid import uuid4

from flaskr.db import get_db
from flaskr.auth import sign_in_required

bp = Blueprint('plants', __name__)


@bp.route("/")
@sign_in_required
def index():
    """Shows the plant status, but if you have none then a CTA."""

    # The the user plant. One per user, for now.

    db = get_db()
    user_id = g.user['id']
    cursor = db.execute("SELECT * FROM plants WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    if len(rows) not in range(2):
        bp.logger.error(
            f"Zero or one plants were expected but instead got {len(rows)}"
        )
        abort(500)
    if len(rows) == 0:
        plant = None
    else:
        plant = rows[0]
    return render_template("plants/index.html", plant=plant)


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/add_plant", methods=["GET", "POST"])
@sign_in_required
def add_plant():
    """Shows a form to create a new plant and also saves the plant data."""

    if request.method == "GET":
        return render_template("plants/add_plant.html")

    if "file" not in request.files:
        flash("No plant picture file given", "danger")
        return render_template("plants/add_plant.html"), 400
    file = request.files["file"]
    if file.filename == "":
        flash("No plant picture file given", "danger")
        return render_template("plants/add_plant.html"), 400
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit(".", 1)[1].lower()
        file.save(
            os.path.join(
                current_app.config["IMAGES"], f"{uuid4()}.{file_extension}"
            )
        )
        return redirect(url_for("plants.index"))
    abort(500)
