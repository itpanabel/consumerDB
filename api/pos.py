from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from api.auth import login_required
from api.db import get_db

bp = Blueprint("pos", __name__, url_prefix="/pos")


@bp.route("/")
@login_required
def index():
    """Return all pos created"""
    db = get_db()
    if g.user["role"] != "admin":
        pos = db.execute(
            "SELECT T0.id, T0.pos_name, T1.entityname "
            "FROM POS T0 INNER JOIN SUBSIDIARIES T1 ON T0.subsidiaryid = T1.id "
            "WHERE T0.subsidiaryid = ? "
            "ORDER BY T0.pos_name",
            (g.user["subsidiary_id"],)
        ).fetchall()
    else:
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
    db = get_db()
    if request.method == "POST":
        pos = request.form["pos"]
        entity = request.form["entity"] if g.user["role"] == "admin" else str(g.user["subsidiary_id"])
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
                error = f"{pos.capitalize()} ya existe en la base de datos."
            else:
                return redirect(url_for("pos.index"))

        flash(error, "alert-danger")

    if g.user["role"] == "admin":
        entities = db.execute("SELECT id, entityname FROM SUBSIDIARIES ORDER BY id").fetchall()
    else:
        entities = db.execute(
            "SELECT id, entityname FROM SUBSIDIARIES WHERE id = ?", (g.user["subsidiary_id"],)
        ).fetchall()

    return render_template("pos/create.html", entities=entities)


@bp.route("<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update data for a pos"""
    pos = get_pos(id)
    db = get_db()

    if g.user["role"] != "admin" and pos["subsidiaryid"] != g.user["subsidiary_id"]:
        abort(403)

    if request.method == "POST":
        pos_name = request.form["pos"]
        entity = request.form["entity"] if g.user["role"] == "admin" else str(g.user["subsidiary_id"])
        error = None

        if not pos_name or not entity:
            error = "Por favor llenar los campos"

        if error is not None:
            flash(error, "alert-danger")
        else:
            db.execute(
                "UPDATE POS SET pos_name = ?, subsidiaryid = ? "
                "WHERE id = ?", (pos_name, entity, id)
            )
            db.commit()
            return redirect(url_for("pos.index"))

    if g.user["role"] == "admin":
        entities = db.execute("SELECT id, entityname FROM SUBSIDIARIES ORDER BY id").fetchall()
    else:
        entities = db.execute(
            "SELECT id, entityname FROM SUBSIDIARIES WHERE id = ?", (g.user["subsidiary_id"],)
        ).fetchall()
    return render_template("pos/update.html", pos=pos, entities=entities)


@bp.route("<int:id>/delete", methods=("GET", "POST"))
@login_required
def delete(id):
    """Delete pos from Database."""
    pos = get_pos(id)
    if g.user["role"] != "admin" and pos["subsidiaryid"] != g.user["subsidiary_id"]:
        abort(403)
    db = get_db()
    db.execute("DELETE FROM POS WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("pos.index"))
