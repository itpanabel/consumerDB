from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from App.auth import login_required
from App.db import get_db

bp = Blueprint("stores", __name__, url_prefix="/stores")


@bp.route("/")
def index():
    """Return all stores created"""
    db = get_db()
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
    if request.method == "POST":
        store = request.form["store"]
        entity = request.form["entity"]
        db = get_db()
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
                # if store already exist
                # show error.
                error = f"{store.capitalize()} ya existe en la base de datos."
            else:
                return redirect(url_for("stores.index"))

        flash(error)

    # Get Entities for Select tag
    db = get_db()
    entities = db.execute(
        "SELECT id, entityname "
        "FROM SUBSIDIARIES "
        "ORDER BY id"
    ).fetchall()

    return render_template("stores/create.html", entities=entities)


@bp.route("<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update data for a Store"""
    store = get_store(id)

    if request.method == "POST":
        store = request.form["store"]
        entity = request.form["entity"]
        error = None

        if not store or not entity:
            error = "Por favor llenar los campos"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE TIENDAS SET storename = ?, subsidiaryid = ? "
                "WHERE id = ?", (store, entity, id)
            )
            db.commit()
            return redirect(url_for("stores.index"))

    # Get Entities for Select tag
    db = get_db()
    entities = db.execute(
        "SELECT id, entityname "
        "FROM SUBSIDIARIES "
        "ORDER BY id"
    ).fetchall()
    return render_template("stores/update.html", store=store, entities=entities)



@bp.route("<int:id>/detele", methods=("GET", "POST"))
@login_required
def delete(id):
    """Delete Store from Database."""
    get_store(id)
    db = get_db()
    db.execute("DELETE FROM TIENDAS WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("stores.index"))
