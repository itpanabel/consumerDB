import functools
from flask import (
    Blueprint, abort, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from api.db import get_db
from api import limiter

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
@login_required
def register():
    """Register new user in database.
    Validate if the username is not
    taken. Hashes the password for
    security.
    """
    if g.user["role"] != "admin":
        abort(403)

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form.get("role", "user")
        if role not in ("admin", "user"):
            abort(400)
        db = get_db()
        error = None

        if not username:
            error = "Nombre de usuario es requerido"
        elif not password:
            error = "Contraseña es requerida"

        if error is None:
            try:
                db.execute(
                    "INSERT INTO USERS (username, password, role) VALUES (?, ?, ?)",
                    (username, generate_password_hash(password), role),
                )
                db.commit()
            except db.IntegrityError:
                # The username was already taken, which caused the
                # commit to fail. Show a validation error.
                error = f"El usuario {username} ya existe."
            else:
                flash(f"Usuario '{username}' creado.", "alert-success")
                return redirect(url_for("auth.users"))

        flash(error, "alert-danger")

    return render_template("auth/register.html")


@bp.route("/users")
@login_required
def users():
    """List all users. Admin only."""
    if g.user["role"] != "admin":
        abort(403)
    db = get_db()
    all_users = db.execute(
        "SELECT u.id, u.username, u.role, s.entityname "
        "FROM USERS u LEFT JOIN SUBSIDIARIES s ON u.subsidiary_id = s.id "
        "ORDER BY u.username"
    ).fetchall()
    return render_template("auth/users.html", users=all_users)


@bp.route("/users/<int:id>/update", methods=("GET", "POST"))
@login_required
def update_user(id):
    """Update a user's username, role, and subsidiary. Admin only."""
    if g.user["role"] != "admin":
        abort(403)
    db = get_db()
    user = db.execute("SELECT * FROM USERS WHERE id = ?", (id,)).fetchone()
    if user is None:
        abort(404)

    if request.method == "POST":
        username = request.form["username"]
        role = request.form.get("role", "user")
        subsidiary_id = request.form.get("subsidiary_id") or None
        new_password = request.form.get("password", "").strip()
        error = None

        if not username:
            error = "Nombre de usuario es requerido."
        elif role not in ("admin", "user"):
            error = "Rol inválido."

        if error is None:
            try:
                if new_password:
                    db.execute(
                        "UPDATE USERS SET username = ?, role = ?, subsidiary_id = ?, password = ? WHERE id = ?",
                        (username, role, subsidiary_id, generate_password_hash(new_password), id),
                    )
                else:
                    db.execute(
                        "UPDATE USERS SET username = ?, role = ?, subsidiary_id = ? WHERE id = ?",
                        (username, role, subsidiary_id, id),
                    )
                db.commit()
            except db.IntegrityError:
                error = f"El usuario '{username}' ya existe."
            else:
                flash(f"Usuario '{username}' actualizado.", "alert-success")
                return redirect(url_for("auth.users"))

        flash(error, "alert-danger")

    subsidiaries = db.execute("SELECT id, entityname FROM SUBSIDIARIES ORDER BY id").fetchall()
    return render_template("auth/update_user.html", user=user, subsidiaries=subsidiaries)


@bp.route("/users/<int:id>/delete", methods=("POST",))
@login_required
def delete_user(id):
    """Delete a user. Admin only. Cannot delete yourself."""
    if g.user["role"] != "admin":
        abort(403)
    if g.user["id"] == id:
        flash("No puedes eliminar tu propia cuenta.", "alert-danger")
        return redirect(url_for("auth.users"))
    db = get_db()
    user = db.execute("SELECT username FROM USERS WHERE id = ?", (id,)).fetchone()
    if user is None:
        abort(404)
    db.execute("DELETE FROM USERS WHERE id = ?", (id,))
    db.commit()
    flash(f"Usuario '{user['username']}' eliminado.", "alert-success")
    return redirect(url_for("auth.users"))


@bp.route("/login", methods=("GET", "POST"))
@limiter.limit("5 per minute")
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
