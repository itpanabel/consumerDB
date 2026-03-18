import sqlite3
import click
from flask import current_app
from flask import g
from werkzeug.security import generate_password_hash


def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    """Clear existing data and create new tables."""
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def migrate_db():
    """Apply additive schema migrations (safe for production)."""
    db = get_db()
    with current_app.open_resource("migrate.sql") as f:
        db.executescript(f.read().decode("utf8"))


def seed_admin(username: str, password: str):
    db = get_db()
    existing = db.execute(
        "SELECT id FROM USERS WHERE username = ?", (username,)
    ).fetchone()
    if existing:
        click.echo(f"User '{username}' already exists — skipping seed.")
        return
    db.execute(
        "INSERT INTO USERS (username, password, subsidiary_id, role) VALUES (?, ?, NULL, 'admin')",
        (username, generate_password_hash(password)),
    )
    db.commit()
    click.echo(f"Admin user '{username}' created.")


@click.command("migrate-db")
def migrate_db_command():
    """Apply schema migrations and seed admin user."""
    migrate_db()
    click.echo("Applied schema migrations.")
    username = click.prompt("Admin username", default="admin")
    password = click.prompt("Admin password", hide_input=True, confirmation_prompt=True)
    seed_admin(username, password)


@click.command("add-role-column")
def add_role_column_command():
    """Add role column to USERS table and promote existing admins."""
    db = get_db()
    try:
        db.execute("ALTER TABLE USERS ADD COLUMN role TEXT NOT NULL DEFAULT 'user'")
        click.echo("Added 'role' column.")
    except Exception:
        click.echo("'role' column already exists — skipping.")
    db.execute("UPDATE USERS SET role = 'admin' WHERE subsidiary_id IS NULL")
    db.commit()
    click.echo("Promoted all NULL-subsidiary users to role='admin'.")


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(migrate_db_command)
    app.cli.add_command(add_role_column_command)
