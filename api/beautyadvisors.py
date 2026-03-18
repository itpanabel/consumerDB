from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from api.auth import login_required
from api.db import get_db

bp = Blueprint("beautyadvisors", __name__, url_prefix="/beautyadvisors")


@bp.route("/")
@login_required
def index():
    """Return all the Beauty Advisors"""
    db = get_db()
    if g.user["role"] != "admin":
        beautyadvisors = db.execute(
            "SELECT T0.id, T0.fullname, T1.entityname "
            "FROM CONSEJERAS T0 INNER JOIN SUBSIDIARIES T1 ON T0.subsidiaryid = T1.id "
            "WHERE T0.subsidiaryid = ?",
            (g.user["subsidiary_id"],)
        ).fetchall()
    else:
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
    db = get_db()
    if request.method == "POST":
        advisor_name = request.form["fullname"]
        advisor_country = request.form["entity"] if g.user["role"] == "admin" else str(g.user["subsidiary_id"])
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

    if g.user["role"] == "admin":
        entities = db.execute("SELECT id, entityname FROM SUBSIDIARIES ORDER BY id").fetchall()
    else:
        entities = db.execute(
            "SELECT id, entityname FROM SUBSIDIARIES WHERE id = ?", (g.user["subsidiary_id"],)
        ).fetchall()

    return render_template("beautyadvisors/create.html", entities=entities)


@bp.route("<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update name and country for Beauty Advisors"""
    beauty_advisor = get_beautyadvisor(id)
    db = get_db()

    if g.user["role"] != "admin" and beauty_advisor["subsidiaryid"] != g.user["subsidiary_id"]:
        abort(403)

    if request.method == "POST":
        advisor_name = request.form["fullname"]
        advisor_country = request.form["entity"] if g.user["role"] == "admin" else str(g.user["subsidiary_id"])
        error = None

        if not advisor_name or not advisor_country:
            error = "Por favor llenar campos."

        if error is not None:
            flash(error, "alert-danger")
        else:
            db.execute(
                "UPDATE CONSEJERAS SET fullname = ?, subsidiaryid = ? "
                "WHERE id = ?", (advisor_name, advisor_country, id)
            )
            db.commit()
            return redirect(url_for("beautyadvisors.index"))

    if g.user["role"] == "admin":
        entities = db.execute("SELECT id, entityname FROM SUBSIDIARIES ORDER BY id").fetchall()
    else:
        entities = db.execute(
            "SELECT id, entityname FROM SUBSIDIARIES WHERE id = ?", (g.user["subsidiary_id"],)
        ).fetchall()

    return render_template("beautyadvisors/update.html", beauty_advisor=beauty_advisor, entities=entities)


@bp.route("<int:id>/delete", methods=("GET", "POST"))
@login_required
def delete(id):
    """Delete beauty advisors from Database."""
    beauty_advisor = get_beautyadvisor(id)
    if g.user["role"] != "admin" and beauty_advisor["subsidiaryid"] != g.user["subsidiary_id"]:
        abort(403)
    db = get_db()
    db.execute("DELETE FROM CONSEJERAS WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("beautyadvisors.index"))
