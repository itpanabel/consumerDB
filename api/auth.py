import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from api.db import get_db

# Create Blueprint auth to
# manage user login session
# status.
bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    """View decorator that redirects
    anonymous users to the login page.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)
    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session,
    load the user object from database into
    ``g.user``.
    """
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute(
                "SELECT * FROM USERS WHERE id = ?", (user_id,)
            ).fetchone()
        )


@bp.route("/register", methods=("GET", "POST"))
def register():
    """Register new user in database.
    Validate if the username is not
    taken. Hashes the password for
    security.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        if not username:
            error = "Nombre de usuario es requerido"
        elif not password:
            error = "Contraseña es requerida"

        if error is None:
            try:
                db.execute(
                    "INSERT INTO USERS (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                # The username was already taken, which caused the
                # commit to fail. Show a validation error.
                error = f"El usuario {username} ya existe."
            else:
                # Sucess, go the login page.
                return redirect(url_for("auth.login"))

        flash(error, "alert-danger")

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in registered user by adding the
    user id to the session.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM USERS WHERE username = ?",
            (username,)
        ).fetchone()

        if user is None:
            error = "Nombre de usuario no puede estar vacio."
        elif not check_password_hash(user["password"], password):
            error = "Usuario o contraseña incorrectos."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error, "alert-danger")


    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Clear the current session,
    including the stored user id.
    """
    session.clear()
    return redirect(url_for("index"))
