from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from api.auth import login_required
from api.db import get_db

bp = Blueprint("beautyadvisors", __name__, url_prefix="/beautyadvisors")


@bp.route("/")
def index():
    """Return all the Beauty Advisors"""
    db = get_db()
    beautyadvisors = db.execute(
        "SELECT T0.id, T0.fullname, T1.entityname "
        "FROM CONSEJERAS T0 INNER JOIN SUBSIDIARIES T1 ON T0.subsidiaryid = T1.id"
    ).fetchall()
    return render_template("beautyadvisors/index.html", beautyadvisors=beautyadvisors)


def get_beautyadvisor(id):
    """Get Beauty Advisor by id
    :param id: advisor id"""
    beauty_advisor = get_db().execute(
        "SELECT id, fullname, subsidiaryid "
        "FROM CONSEJERAS "
        "WHERE id = ?",
        (id,),
    ).fetchone()

    if beauty_advisor is None:
        abort(404, f"La consejera {id} no existe.")

    return beauty_advisor


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create Beauty Advisors"""
    if request.method == "POST":
        advisor_name = request.form["fullname"]
        advisor_country = request.form["entity"]
        db = get_db()
        error = None

        if not advisor_name:
            error = "Se requiere nombre de la consejera."
        elif not advisor_country:
            error = "Se requiere asignar un país."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO CONSEJERAS (fullname, subsidiaryid) VALUES (?, ?)",
                    (advisor_name, advisor_country)
                )
                db.commit()
            except db.IntegrityError:
                error = f"{advisor_name.capitalize()} existe en la base de datos."
            else:
                return redirect(url_for("beautyadvisors.index"))

        flash(error, "alert-danger")

    # data for Select Tag
    db = get_db()
    entities = db.execute(
        "SELECT id, entityname "
        "FROM SUBSIDIARIES "
        "ORDER BY id"
    ).fetchall()

    return render_template("beautyadvisors/create.html", entities=entities)


@bp.route("<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update name and country for
    Beauty Advisors"""

    beauty_advisor = get_beautyadvisor(id)

    if request.method == "POST":
        beauty_advisor = request.form["fullname"]
        advisor_country = request.form["entity"]
        error = None

        if not beauty_advisor or not advisor_country:
            error = "Por favor llenar campos."

        if error is not None:
            flash(error, "alert-danger")
        else:
            db = get_db()
            db.execute(
                "UPDATE CONSEJERAS SET fullname = ?, subsidiaryid = ? "
                "WHERE id = ?", (beauty_advisor, advisor_country, id)
            )
            db.commit()
            return redirect(url_for("beautyadvisors.index"))

    # get data for select Tag
    db = get_db()
    entities = db.execute(
        "SELECT id, entityname "
        "FROM SUBSIDIARIES "
        "ORDER BY id"
    ).fetchall()

    return render_template("beautyadvisors/update.html", beauty_advisor=beauty_advisor, entities=entities)


@bp.route("<int:id>/delete", methods=("GET", "POST"))
@login_required
def delete(id):
    """Delete beauty advisors from Database.
    :params
    id:int database id of record"""
    get_beautyadvisor(id)
    db = get_db()
    db.execute("DELETE FROM CONSEJERAS WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("beautyadvisors.index"))
