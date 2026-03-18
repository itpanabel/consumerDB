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
@login_required
def index():
    """Return all testers created"""
    db = get_db()
    if (g.user['role'] != "admin"):
      username = g.user['username']
      userCountry = db.execute("SELECT subsidiary_id FROM USERS WHERE username = ?", (username,)).fetchone()[0]
      testers = db.execute(
          "SELECT T0.testercode, T0.tester_name, T2.brandname, T0.tester_axe, T1.entityname "
          "FROM TESTERS T0 INNER JOIN SUBSIDIARIES T1 ON T0.subsidiaryid = T1.id INNER JOIN MARCAS T2 ON T0.tester_id = T2.id "
          "WHERE T0.subsidiaryid = ?"
          "ORDER BY T2.brandname ASC, T0.tester_axe ASC, T0.tester_name", (userCountry,)
      ).fetchall()
    else:
      testers = db.execute(
          "SELECT T0.testercode, T0.tester_name, T2.brandname, T0.tester_axe, T1.entityname "
          "FROM TESTERS T0 INNER JOIN SUBSIDIARIES T1 ON T0.subsidiaryid = T1.id INNER JOIN MARCAS T2 ON T0.tester_id = T2.id "
          "ORDER BY T2.brandname ASC, T0.tester_axe ASC, T0.tester_name"
      ).fetchall()
    return render_template("testers/index.html", testers=testers)


def get_tester(id):
    """Get the tester by id.
    :param id: tester id
    """
    tester = get_db().execute(
        "SELECT testercode, tester_name, tester_id, tester_axe, subsidiaryid "
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
        tester_id = request.form["testerbrand"]
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
                    "INSERT INTO TESTERS (testercode, tester_name, tester_id, tester_axe, subsidiaryid) VALUES (?, ?, ?, ?, ?)",
                    (tester_code, tester_name, tester_id, tester_axe, entity)
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
    if (g.user['role'] != "admin"):
      username = g.user['username']
      userCountry = db.execute("SELECT subsidiary_id FROM USERS WHERE username = ?", (username,)).fetchone()[0]
      brands = db.execute("SELECT id, brandname FROM MARCAS WHERE subsidiaryid = ? ORDER BY brandname", (userCountry,)).fetchall()
    else:
      brands = db.execute("SELECT id, brandname FROM MARCAS ORDER BY brandname").fetchall()
    entities = db.execute(
        "SELECT id, entityname "
        "FROM SUBSIDIARIES "
        "ORDER BY id"
    ).fetchall()
    axes = db.execute("SELECT DISTINCT tester_axe FROM TESTERS").fetchall()

    return render_template("testers/create.html", entities=entities, brands=brands, axes=axes)


@bp.route("/import_testers", methods=("GET", "POST"))
@login_required
def import_testers():
    """Import CSV file into the TESTERS table"""
    ALLOWED_EXTENSIONS = {'csv'}
    UPLOAD_FOLDER = os.path.join('api/static', 'uploads')
    db = get_db()

    # Determine the user's subsidiary for scoping
    if g.user['role'] != 'admin':
        subsidiaryid = db.execute(
            "SELECT subsidiary_id FROM USERS WHERE id = ?", (g.user['id'],)
        ).fetchone()[0]
    else:
        subsidiaryid = None  # admin must select via form

    if request.method == "POST":
        csv_file = request.files["fileToImport"]
        if not csv_file or not csv_file.filename:
            flash("Se requiere archivo", "alert-danger")
            return redirect("/testers/import_testers")
        csv_filename = secure_filename(csv_file.filename)
        csv_delimeter = request.form["csvDelimeter"]

        if g.user['role'] == 'admin':
            subsidiaryid = request.form.get("entity", type=int)
            if not subsidiaryid:
                flash("Se requiere seleccionar un país.", "alert-danger")
                return redirect("/testers/import_testers")

        if not csv_file:
            flash("Se requiere archivo", "alert-danger")
            return redirect("/testers/import_testers")

        if not ('.' in csv_filename and csv_filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
            flash("Solo se permiten archivos CSV", "alert-danger")
            return redirect("/testers/import_testers")

        allowed_delimiters = [',', ';', '\t', '|']
        if csv_delimeter not in allowed_delimiters:
            flash("Delimitador no permitido. Use: coma, punto y coma, tabulador o pipe.", "alert-danger")
            return redirect("/testers/import_testers")

        uploaded_data_file_path = os.path.join(UPLOAD_FOLDER, csv_filename)
        csv_file.save(uploaded_data_file_path)

        # Delete only this subsidiary's testers
        db.execute("DELETE FROM TESTERS WHERE subsidiaryid = ?", (subsidiaryid,))
        db.commit()

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
                        "INSERT INTO TESTERS (testercode, tester_name, tester_id, tester_axe, subsidiaryid) VALUES (?, ?, ?, ?, ?)",
                        (itemcode, itemname, itembrand, itemaxe, subsidiaryid)
                    )
                    db.commit()
                except db.IntegrityError:
                    flash("El producto ya existe en la base de datos", "alert-warning")
            flash("Se importo el archivo correctamente!", "alert-success")
            return redirect("/testers")

    entities = db.execute("SELECT id, entityname FROM SUBSIDIARIES ORDER BY id").fetchall()
    return render_template("testers/import_testers.html", entities=entities, user_subsidiary=subsidiaryid, is_admin=g.user['role'] == 'admin')


@bp.route("<string:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update data for a tester"""
    username = g.user['username']
    tester = get_tester(id)

    if g.user['role'] != 'admin':
        db = get_db()
        userCountry = db.execute("SELECT subsidiary_id FROM USERS WHERE username = ?", (username,)).fetchone()[0]
        if tester['subsidiaryid'] != userCountry:
            abort(403)

    if request.method == "POST":
        tester_code = request.form["testercode"]
        tester_name = request.form["testername"]
        tester_id = request.form["testerbrand"]
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
                "UPDATE TESTERS SET testercode = ?, tester_name = ?, tester_id = ?, tester_axe = ?, subsidiaryid = ? "
                "WHERE testercode = ?", (tester_code, tester_name, tester_id, tester_axe, entity, id)
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
    if g.user['role'] != 'admin':
        userCountry = db.execute("SELECT subsidiary_id FROM USERS WHERE username = ?", (username,)).fetchone()[0]
        brands = db.execute("SELECT id, brandname FROM MARCAS WHERE subsidiaryid = ? ORDER BY brandname", (userCountry,)).fetchall()
    else:
        brands = db.execute("SELECT id, brandname FROM MARCAS ORDER BY brandname").fetchall()
    axes = db.execute("SELECT DISTINCT tester_axe FROM TESTERS").fetchall()

    return render_template("testers/update.html", tester=tester, entities=entities, brands=brands, axes=axes)



@bp.route("<id>/delete", methods=("GET", "POST"))
@login_required
def delete(id):
    """Delete tester from Database."""
    get_tester(id)
    db = get_db()
    db.execute("DELETE FROM TESTERS WHERE testercode = ?", (id,))
    db.commit()
    return redirect(url_for("testers.index"))


@bp.route("/export_resquest", methods=("GET", "POST"))
@login_required
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
