from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from App.auth import login_required
from App.db import get_db

bp = Blueprint("entity", __name__, url_prefix="/entity")

@bp.route("/")
def index():
    """Return all entities created"""
    db = get_db()
    entities = db.execute(
        "SELECT *"
        " FROM SUBSIDIARIES"
    ).fetchall()
    return render_template("entity/index.html", entities=entities)


def get_entity(id):
    """Get the Subsidiary by id.
    :param id: id of the subsidiary
    """
    subsidiary = (
        get_db().execute(
            "SELECT id, entityname, mailchimpentityid"
            " FROM SUBSIDIARIES"
            " WHERE id = ?",
            (id,),
        ).fetchone()
    )

    if subsidiary is None:
        abort(404, f"La entidad {id} no existe.")

    return subsidiary


@bp.route("/create", methods=("GET", "POST"))
def create():
    """Create a new Entity"""
    if request.method == "POST":
        entity = request.form["entidad"]
        mailchimp_id = request.form["mailchimpid"]
        db = get_db()
        error = None

        if not entity:
            error = "Es requerido el país"
        elif not mailchimp_id:
            error = "Se requiere ID de Mailchimp."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO SUBSIDIARIES (entityname, mailchimpentityid) VALUES (?, ?)",
                    (entity, mailchimp_id)
                )
                db.commit()
            except db.IntegrityError:
                # If entity already exist
                # show and error
                error = f"{entity.capitalize()} ya existe en la base de datos."
            else:
                return redirect(url_for("entity.index"))

        flash(error)

    return render_template("entity/create.html")


@bp.route("<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update data for an entity"""
    subsidiary = get_entity(id)

    if request.method == "POST":
        entityname = request.form["entidad"]
        mailchimp_id = request.form["mailchimpid"]
        error = None

        if not entityname or not mailchimp_id:
            error = "Por favor completar los campos"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE SUBSIDIARIES SET entityname = ?, mailchimpentityid = ?"
                " WHERE id = ?", (entityname, mailchimp_id, id)
            )
            db.commit()
            return redirect(url_for("entity.index"))

    return render_template("entity/update.html", subsidiary=subsidiary)



@bp.route("<int:id>/delete", methods=("POST",))
def delete(id):
    """Delete a subsidiary
    Ensure that the entity exist and the
    user is logged.
    """
    get_entity(id)
    db = get_db()
    db.execute("DELETE FROM SUBSIDIARIES WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("entity.index"))
