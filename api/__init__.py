import os
from flask import Flask, render_template
from dotenv import load_dotenv
from pathlib import Path

#
# LOAD SECRETS
#
load_dotenv(Path(".env"))
APP_SECRET_KEY = os.getenv("SECRET_KEY")

def create_app(test_config=None):
    # Create and configure the App
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=APP_SECRET_KEY,
        DATABASE=os.path.join(app.instance_path, "App.sqlite")
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
