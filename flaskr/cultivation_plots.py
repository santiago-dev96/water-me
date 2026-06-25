from flask import (
    Blueprint, g, render_template, request, flash, redirect, url_for, current_app, abort
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
    return render_template("cultivation_plots/index.html.jinja", cultivation_plots=cultivation_plots)


@bp.route("/new_cultivation_plot", methods=["GET", "POST"])
@login_required
def new_cultivation_plot():
    """New cultivation plot."""

    if request.method == "GET":
        return render_template("cultivation_plots/new_cultivation_plot.html.jinja")

    name = request.form.get('name')
    if not name:
        flash('The name of the plot is required', 'danger')
        return render_template("cultivation_plots/new_cultivation_plot.html.jinja", form=request.form), 400

    crop = request.form.get('crop')
    if not crop:
        flash('The crop is required', 'danger')
        return render_template("cultivation_plots/new_cultivation_plot.html.jinja", form=request.form), 400

    number_of_plants = request.form.get('number-of-plants')
    if not number_of_plants:
        number_of_plants = 0
    else:
        bad_value_msg = f'Received a bad value for the number of plants: {number_of_plants}'
        try:
            number_of_plants = int(number_of_plants)
            if number_of_plants < 0:
                current_app.logger.info(bad_value_msg)
                number_of_plants = 0
        except ValueError:
            current_app.logger.info(bad_value_msg)
            number_of_plants = 0

    db = get_db()
    user_id = g.user['id']
    cursor = db.execute('INSERT INTO cultivation_plots (name, crop, number_of_plants, user_id) VALUES (?, ?, ?, ?)', (name, crop, number_of_plants, user_id))
    cursor.close()
    db.commit()

    return redirect(url_for('cultivation_plots.index'))


@bp.route('/cultivation_plots/<int:id>', methods=["GET"])
@login_required
def cultivation_plot(id):
    db = get_db()
    cursor = db.execute('SELECT * FROM cultivation_plots WHERE id = ?', (id,))
    cultivation_plot = cursor.fetchone()
    cursor.close()
    if not cultivation_plot:
        return abort(404)
    else:
        return render_template('cultivation_plots/cultivation_plot.html.jinja', cultivation_plot=cultivation_plot)


@bp.route('/cultivation_plots/<int:id>/log_operation', methods=["GET", "POST"])
@login_required
def log_cultivation_plot_operation(id):
    db = get_db()
    cursor = db.execute('SELECT * FROM cultivation_plots WHERE id = ?', (id,))
    cultivation_plot = cursor.fetchone()
    cursor.close()
    if not cultivation_plot:
        return abort(404)
    elif request.method == 'GET':
        return render_template('cultivation_plots/log_cultivation_plot_operation.html.jinja', cultivation_plot=cultivation_plot)
    else:
        number_of_plants = request.form.get('number_of_plants', 0)
        try:
            number_of_plants = int(number_of_plants)
        except ValueError:
            flash('The number of plants must be a whole number', 'danger')
            return render_template('cultivation_plots/log_cultivation_plot_operation.html.jinja', cultivation_plot=cultivation_plot), 400
        water_spent = request.form.get('water_spent', 0.0)
        try:
            water_spent = float(water_spent)
        except ValueError:
            flash('The amount of water must be a number greater than zero', 'danger')
            return render_template('cultivation_plots/log_cultivation_plot_operation.html.jinja', cultivation_plot=cultivation_plot), 400
        harvest = request.form.get('harvest', 0.0)
        try:
            harvest = float(harvest)
        except ValueError:
            flash('The harvest must be a number greater than zero', 'danger')
            return render_template('cultivation_plots/log_cultivation_plot_operation.html.jinja', cultivation_plot=cultivation_plot), 400
        cursor = db.execute('INSERT INTO operations (number_of_plants, water_spent, harvest, cultivation_plot_id) VALUES (?, ?, ?, ?)', (number_of_plants, water_spent, harvest, id))
        cursor.close()
        cursor = db.execute('UPDATE cultivation_plots SET number_of_plants = ?, water_spent = ?, harvest = ? WHERE id = ?', (cultivation_plot['number_of_plants'] + number_of_plants, cultivation_plot['water_spent'] + water_spent, cultivation_plot['harvest'] + harvest, id))
        cursor.close()
        db.commit()
        flash('Operation successfully logged', 'success')
        return redirect(url_for('cultivation_plots.cultivation_plot', id=id))
