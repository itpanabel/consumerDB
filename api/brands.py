from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from api.auth import login_required
from api.db import get_db
import csv
import os

bp = Blueprint("brands", __name__, url_prefix="/brands")

@bp.route("/")
def index():
    """Return all brands created"""
    db = get_db()
    username = g.user['username']
    if (g.user['username'] != "admin"):
      userCountry = db.execute("SELECT subsidiary_id FROM USERS WHERE username = ?", (username,)).fetchone()[0]
      brands = db.execute(
          "SELECT m.id, m.brandname, m.brandcode, s.entityname "
          "FROM MARCAS m INNER JOIN SUBSIDIARIES s ON m.subsidiaryid = s.id "
          "WHERE s.id = ? "
          "ORDER BY m.brandname", (userCountry,)
      ).fetchall()
    else:
      brands = db.execute(
          "SELECT m.id, m.brandname, m.brandcode, s.entityname "
          "FROM MARCAS m INNER JOIN SUBSIDIARIES s ON m.subsidiaryid = s.id "
          "ORDER BY m.brandname"
      ).fetchall()
    return render_template("brands/index.html", brands=brands)


def get_brand(id):
    """Get the brand by id.
    :param id: brand id
    """
    brand = get_db().execute(
        "SELECT id, brandname, brandcode, subsidiaryid "
        "FROM MARCAS "
        "WHERE id = ?",
        (id,),
    ).fetchone()

    if brand is None:
        abort(404, f"La marca {id} no existe.")

    return brand


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new Brand"""
    username = g.user['username']
    if request.method == "POST":
        brandname = request.form["brandname"]
        brandcode = request.form["brandcode"]
        subsidiaryid = request.form["entity"]
        db = get_db()
        error = None

        if not brandname:
            error = "Se requiere nombre de la marca."
        elif not subsidiaryid:
            error = "Se require país."
        elif not brandcode:
            error = "Se requiere código corto de marca."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO MARCAS (brandname, brandcode, subsidiaryid) VALUES (?, ?, ?)",
                    (brandname, brandcode, subsidiaryid)
                )
                db.commit()
            except db.IntegrityError:
                # if brand already exist
                # show error.
                error = f"{brandname.capitalize()} ya existe en la base de datos."
            else:
                return redirect(url_for("brands.index"))

        flash(error, "alert-danger")

    # Get Entities for Select tag
    db = get_db()
    entities = db.execute(
        "SELECT id, entityname "
        "FROM SUBSIDIARIES "
        "ORDER BY id"
    ).fetchall()

    return render_template("brands/create.html", entities=entities)


@bp.route("<string:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update data for a brand"""
    #username = g.user['username']
    brand = get_brand(id)

    if request.method == "POST":
        brandname = request.form["brandname"]
        brandcode = request.form["brandcode"]
        entity = request.form["entity"]
        error = None

        if not brandname or not entity or not brandcode:
            error = "Por favor llenar los campos"

        if error is not None:
            flash(error, "alert-danger")
        else:
            db = get_db()
            db.execute(
                "UPDATE MARCAS SET brandname = ?, brandcode = ?, subsidiaryid = ? "
                "WHERE id = ?", (brandname, brandcode, entity, id)
            )
            db.commit()
            return redirect(url_for("brands.index"))

    # Get Entities for Select tag
    db = get_db()
    entities = db.execute(
        "SELECT id, entityname "
        "FROM SUBSIDIARIES "
        "ORDER BY id"
    ).fetchall()

    return render_template("brands/update.html", brand=brand, entities=entities)


@bp.route("<id>/detele", methods=("GET", "POST"))
@login_required
def delete(id):
    """Delete tester from Database."""
    get_brand(id)
    db = get_db()
    db.execute("DELETE FROM MARCAS WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("brands.index"))
