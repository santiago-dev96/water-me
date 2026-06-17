from flask import (
    Blueprint, g, render_template, request, abort
)

from flaskr.db import get_db
from flaskr.auth import login_required

bp = Blueprint('cultivation_plots', __name__)


@bp.route("/")
@login_required
def index():
    """Shows the system status."""

    db = get_db()
    user_id = g.user['id']
    cursor = db.execute("SELECT * FROM cultivation_plots WHERE user_id = ?", (user_id,))
    cultivation_plots = cursor.fetchall()
    cursor.close()
    return render_template("cultivation_plots/index.html", cultivation_plots=cultivation_plots)


@bp.route("/new_cultivation_plot", methods=["GET", "POST"])
@login_required
def new_cultivation_plot():
    """New cultivation plot."""

    if request.method == "GET":
        return render_template("cultivation_plots/new_cultivation_plot.html")

    abort(500)
