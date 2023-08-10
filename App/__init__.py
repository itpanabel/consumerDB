import os
from flask import Flask, render_template

from . import forms


def create_app(test_config=None):
    # Create and configure the App
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="UGFuYWJlbElUMjAyMyE=",
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

    #temp index
    @app.route("/test")
    def index():
        return render_template("base.html")

    # DB
    from . import db
    db.init_app(app)

    # Register All Blueprint
    from . import auth, entity, stores, beautyadvisors
    app.register_blueprint(auth.bp)
    app.register_blueprint(entity.bp)
    app.register_blueprint(stores.bp)
    app.register_blueprint(beautyadvisors.bp)
    app.register_blueprint(forms.bp)
    app.add_url_rule("/", endpoint="index")

    return app
