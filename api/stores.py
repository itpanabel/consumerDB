from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from api.auth import login_required
from api.db import get_db

bp = Blueprint("stores", __name__, url_prefix="/stores")


@bp.route("/")
@login_required
def index():
    """Return all stores created"""
    db = get_db()
    if g.user["role"] != "admin":
        stores = db.execute(
            "SELECT T0.id, T0.storename, T1.entityname "
            "FROM TIENDAS T0 INNER JOIN SUBSIDIARIES T1 ON T0.subsidiaryid = T1.id "
            "WHERE T0.subsidiaryid = ?",
            (g.user["subsidiary_id"],)
        ).fetchall()
    else:
        stores = db.execute(
            "SELECT T0.id, T0.storename, T1.entityname "
            "FROM TIENDAS T0 INNER JOIN SUBSIDIARIES T1 ON T0.subsidiaryid = T1.id"
        ).fetchall()
    return render_template("stores/index.html", stores=stores)


def get_store(id):
    """Get the Store by id.
    :param id: store id
    """
    store = get_db().execute(
        "SELECT id, storename, subsidiaryid "
        "FROM TIENDAS "
        "WHERE id = ?",
        (id,),
    ).fetchone()

    if store is None:
        abort(404, f"La tienda {id} no existe.")

    return store


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new Store"""
    db = get_db()
    if request.method == "POST":
        store = request.form["store"]
        entity = request.form["entity"] if g.user["role"] == "admin" else str(g.user["subsidiary_id"])
        error = None

        if not store:
            error = "Se requiere nombre de la tienda."
        elif not entity:
            error = "Se require país."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO TIENDAS (storename, subsidiaryid) VALUES (?, ?)",
                    (store, entity)
                )
                db.commit()
            except db.IntegrityError:
                error = f"{store.capitalize()} ya existe en la base de datos."
            else:
                return redirect(url_for("stores.index"))

        flash(error, "alert-danger")

    # Admin sees all subsidiaries; regular user sees only their own
    if g.user["role"] == "admin":
        entities = db.execute("SELECT id, entityname FROM SUBSIDIARIES ORDER BY id").fetchall()
    else:
        entities = db.execute(
            "SELECT id, entityname FROM SUBSIDIARIES WHERE id = ?", (g.user["subsidiary_id"],)
        ).fetchall()

    return render_template("stores/create.html", entities=entities)


@bp.route("<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update data for a Store"""
    store = get_store(id)
    db = get_db()

    if g.user["role"] != "admin" and store["subsidiaryid"] != g.user["subsidiary_id"]:
        abort(403)

    if request.method == "POST":
        store_name = request.form["store"]
        entity = request.form["entity"] if g.user["role"] == "admin" else str(g.user["subsidiary_id"])
        error = None

        if not store_name or not entity:
            error = "Por favor llenar los campos"

        if error is not None:
            flash(error, "alert-danger")
        else:
            db.execute(
                "UPDATE TIENDAS SET storename = ?, subsidiaryid = ? "
                "WHERE id = ?", (store_name, entity, id)
            )
            db.commit()
            return redirect(url_for("stores.index"))

    if g.user["role"] == "admin":
        entities = db.execute("SELECT id, entityname FROM SUBSIDIARIES ORDER BY id").fetchall()
    else:
        entities = db.execute(
            "SELECT id, entityname FROM SUBSIDIARIES WHERE id = ?", (g.user["subsidiary_id"],)
        ).fetchall()
    return render_template("stores/update.html", store=store, entities=entities)


@bp.route("<int:id>/delete", methods=("GET", "POST"))
@login_required
def delete(id):
    """Delete Store from Database."""
    store = get_store(id)
    if g.user["role"] != "admin" and store["subsidiaryid"] != g.user["subsidiary_id"]:
        abort(403)
    db = get_db()
    db.execute("DELETE FROM TIENDAS WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("stores.index"))
