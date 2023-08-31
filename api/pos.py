from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from api.auth import login_required
from api.db import get_db

bp = Blueprint("pos", __name__, url_prefix="/pos")


@bp.route("/")
def index():
    """Return all pos created"""
    db = get_db()
    pos = db.execute(
        "SELECT T0.id, T0.pos_name, T1.entityname "
        "FROM POS T0 INNER JOIN SUBSIDIARIES T1 ON T0.subsidiaryid = T1.id "
        "ORDER BY T0.pos_name"
    ).fetchall()
    return render_template("pos/index.html", pos=pos)


def get_pos(id):
    """Get the POS by id.
    :param id: pos id
    """
    pos = get_db().execute(
        "SELECT id, pos_name, subsidiaryid "
        "FROM POS "
        "WHERE id = ?",
        (id,),
    ).fetchone()

    if pos is None:
        abort(404, f"La tienda {id} no existe.")

    return pos


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new pos"""
    if request.method == "POST":
        pos = request.form["pos"]
        entity = request.form["entity"]
        db = get_db()
        error = None

        if not pos:
            error = "Se requiere nombre de la tienda."
        elif not entity:
            error = "Se require país."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO POS (pos_name, subsidiaryid) VALUES (?, ?)",
                    (pos, entity)
                )
                db.commit()
            except db.IntegrityError:
                # if pos already exist
                # show error.
                error = f"{pos.capitalize()} ya existe en la base de datos."
            else:
                return redirect(url_for("pos.index"))

        flash(error, "alert-danger")

    # Get Entities for Select tag
    db = get_db()
    entities = db.execute(
        "SELECT id, entityname "
        "FROM SUBSIDIARIES "
        "ORDER BY id"
    ).fetchall()

    return render_template("pos/create.html", entities=entities)


@bp.route("<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update data for a pos"""
    pos = get_pos(id)

    if request.method == "POST":
        pos = request.form["pos"]
        entity = request.form["entity"]
        error = None

        if not pos or not entity:
            error = "Por favor llenar los campos"

        if error is not None:
            flash(error, "alert-danger")
        else:
            db = get_db()
            db.execute(
                "UPDATE POS SET pos_name = ?, subsidiaryid = ? "
                "WHERE id = ?", (pos, entity, id)
            )
            db.commit()
            return redirect(url_for("pos.index"))

    # Get Entities for Select tag
    db = get_db()
    entities = db.execute(
        "SELECT id, entityname "
        "FROM SUBSIDIARIES "
        "ORDER BY id"
    ).fetchall()
    return render_template("pos/update.html", pos=pos, entities=entities)



@bp.route("<int:id>/detele", methods=("GET", "POST"))
@login_required
def delete(id):
    """Delete pos from Database."""
    get_pos(id)
    db = get_db()
    db.execute("DELETE FROM POS WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("pos.index"))
