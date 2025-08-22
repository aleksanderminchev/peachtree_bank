import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate
from config import config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name="development"):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    from commands import commands
    from models.contractors import Contractor
    from models.transactions import Transaction
    from models.balance import Balance
    from models.user import User

    app.register_blueprint(commands)
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    print("TEST")

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    return app
