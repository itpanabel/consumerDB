import logging
import os
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from pathlib import Path

#
# LOAD SECRETS
#
load_dotenv(Path(".env"))
APP_SECRET_KEY = os.getenv("SECRET_KEY")

limiter = Limiter(key_func=get_remote_address, default_limits=[])

def create_app(test_config=None):
    # Create and configure the App
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=APP_SECRET_KEY,
        DATABASE=os.path.join(app.instance_path, "App.sqlite"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Logging
    log_format = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler = RotatingFileHandler("app.log", maxBytes=1_000_000, backupCount=3)
    file_handler.setFormatter(log_format)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_format)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    if not root_logger.handlers:
        root_logger.addHandler(file_handler)
        root_logger.addHandler(stream_handler)

    # CSRF Protection
    CSRFProtect(app)

    # Rate Limiting
    limiter.init_app(app)

    # Security Headers
    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

    # DB
    from . import db
    db.init_app(app)

    # Register All Blueprint
    from . import auth, entity, stores, beautyadvisors, forms, pos, testers, brands
    app.register_blueprint(auth.bp)
    app.register_blueprint(entity.bp)
    app.register_blueprint(stores.bp)
    app.register_blueprint(beautyadvisors.bp)
    app.register_blueprint(pos.bp)
    app.register_blueprint(testers.bp)
    app.register_blueprint(forms.bp)
    app.register_blueprint(brands.bp)
    app.add_url_rule("/", endpoint="index")

    return app
