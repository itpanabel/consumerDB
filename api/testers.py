from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from api.auth import login_required
from api.db import get_db
import csv
import os

bp = Blueprint("testers", __name__, url_prefix="/testers")


@bp.route("/")
def index():
    """Return all testers created"""
    db = get_db()
    testers = db.execute(
        "SELECT T0.testercode, T0.tester_name, T0.tester_brand, T0.tester_axe, T1.entityname "
        "FROM TESTERS T0 INNER JOIN SUBSIDIARIES T1 ON T0.subsidiaryid = T1.id"
    ).fetchall()
    return render_template("testers/index.html", testers=testers)


def get_tester(id):
    """Get the tester by id.
    :param id: tester id
    """
    tester = get_db().execute(
        "SELECT testercode, tester_name, tester_brand, tester_axe, subsidiaryid "
        "FROM TESTERS "
        "WHERE testercode = ?",
        (id,),
    ).fetchone()

    if tester is None:
        abort(404, f"El tester {id} no existe.")

    return tester


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new tester"""
    if request.method == "POST":
        tester_code = request.form["testercode"]
        tester_name = request.form["testername"]
        tester_brand = request.form["testerbrand"]
        tester_axe = request.form["testeraxe"]
        entity = request.form["entity"]
        db = get_db()
        error = None

        if not tester_name:
            error = "Se requiere nombre del tester."
        elif not entity:
            error = "Se require país."
        elif not tester_code:
            error = "Se requiere código de Artículo."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO TESTERS (testercode, tester_name, tester_brand, tester_axe, subsidiaryid) VALUES (?, ?, ?, ?, ?)",
                    (tester_code, tester_name, tester_brand, tester_axe, entity)
                )
                db.commit()
            except db.IntegrityError:
                # if tester already exist
                # show error.
                error = f"{tester_name.capitalize()} ya existe en la base de datos."
            else:
                return redirect(url_for("testers.index"))

        flash(error, "alert-danger")

    # Get Entities for Select tag
    db = get_db()
    entities = db.execute(
        "SELECT id, entityname "
        "FROM SUBSIDIARIES "
        "ORDER BY id"
    ).fetchall()
    brands = db.execute("SELECT DISTINCT tester_brand FROM TESTERS").fetchall()
    axes = db.execute("SELECT DISTINCT tester_axe FROM TESTERS").fetchall()

    return render_template("testers/create.html", entities=entities, brands=brands, axes=axes)


@bp.route("/import_testers", methods=("GET", "POST"))
@login_required
def import_testers():
    """Import CSV file into the TESTERS table"""
    ALLOWED_EXTENSIONS = {'csv'}
    UPLOAD_FOLDER = os.path.join('api/static', 'uploads')
    db = get_db()
    if request.method == "POST":
        csv_file = request.files["fileToImport"]
        csv_filename = secure_filename(csv_file.filename)
        csv_delimeter = request.form["csvDelimeter"]

        uploaded_data_file_path = os.path.join(UPLOAD_FOLDER, csv_filename)
        csv_file.save(uploaded_data_file_path)

        # limpia la tabla de testers viejos
        db.execute("DELETE FROM TESTERS")
        db.commit()

        if csv_delimeter == "":
            flash("Se requiere delimitador del archivo", "alert-danger")
            return redirect("testers/import_testers")
        with open(uploaded_data_file_path, "r", encoding="utf-8-sig") as file:
            reader = csv.reader(file, delimiter=csv_delimeter)
            next(reader)
            for row in reader:
                itemcode = row[0]
                itemname = row[3]
                itembrand = row[1]
                itemaxe = row[2]
                try:
                    db.execute(
                        "INSERT INTO TESTERS (testercode, tester_name, tester_brand, tester_axe, subsidiaryid) VALUES (?, ?, ?, ?, ?)",
                        (itemcode, itemname, itembrand, itemaxe, 1)
                    )
                    db.commit()
                except db.IntegrityError:
                    flash("El producto ya existe en la base de datos", "alert-warning")
            flash("Se importo el archivo correctamente!", "alert-success")
            return redirect("/testers")
    return render_template("testers/import_testers.html")


@bp.route("<string:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update data for a tester"""
    tester = get_tester(id)

    if request.method == "POST":
        tester_code = request.form["testercode"]
        tester_name = request.form["testername"]
        tester_brand = request.form["testerbrand"]
        tester_axe = request.form["testeraxe"]
        entity = request.form["entity"]
        error = None

        if not tester_code or not entity:
            error = "Por favor llenar los campos"

        if error is not None:
            flash(error, "alert-danger")
        else:
            db = get_db()
            db.execute(
                "UPDATE TESTERS SET testercode = ?, tester_name = ?, tester_brand = ?, tester_axe = ?, subsidiaryid = ? "
                "WHERE testercode = ?", (tester_code, tester_name, tester_brand, tester_axe, entity, id)
            )
            db.commit()
            return redirect(url_for("testers.index"))

    # Get Entities for Select tag
    db = get_db()
    entities = db.execute(
        "SELECT id, entityname "
        "FROM SUBSIDIARIES "
        "ORDER BY id"
    ).fetchall()
    brands = db.execute("SELECT DISTINCT tester_brand FROM TESTERS").fetchall()
    axes = db.execute("SELECT DISTINCT tester_axe FROM TESTERS").fetchall()

    return render_template("testers/update.html", tester=tester, entities=entities, brands=brands, axes=axes)



@bp.route("<id>/detele", methods=("GET", "POST"))
@login_required
def delete(id):
    """Delete tester from Database."""
    get_tester(id)
    db = get_db()
    db.execute("DELETE FROM TESTERS WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("testers.index"))


@bp.route("/export_resquest", methods=("GET", "POST"))
def export_resquest():
    """This will render the tester requested
    for the current month."""
    db = get_db()
    data = db.execute(
        "SELECT T1.pos_name, T0.requester, T0.itemcode, T2.tester_name, 1 AS 'Qty', Date(T0.orderdate) AS'orderdate' "
        "FROM ORDEREDTESTERS "
        "T0 INNER JOIN POS T1 ON T0.orderpos = T1.id "
        "INNER JOIN TESTERS T2 ON T0.itemcode = T2.testercode "
        "WHERE strftime('%m', T0.orderdate) = strftime('%m', 'now')"
    )
    return render_template("testers/export_testers.html", data=data)
