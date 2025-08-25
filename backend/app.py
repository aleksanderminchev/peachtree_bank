import os

from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

from flask_migrate import Migrate
from config import config

cors = CORS()

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()


def create_app(config_name="development"):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    cors.init_app(
        app,
        supports_credentials=True,
        origins=["http://localhost:5173/", "http://localhost:5173",'http://127.0.0.1:5173/'],
    )
    from commands import commands
    from blueprints.user import users
    from blueprints.transactions import transactions
    from blueprints.contractors import contractors

    # import here to allow for migration tracking to trigger
    from models.contractors import Contractor
    from models.transactions import Transaction
    from models.token import Token
    from models.user import User

    # register api routes
    app.register_blueprint(commands, url_prefix="/api")
    app.register_blueprint(users, url_prefix="/api")
    app.register_blueprint(transactions, url_prefix="/api")
    app.register_blueprint(contractors, url_prefix="/api")
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    print("TEST")

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    # Middleware to add new tokens to response headers/cookies

    return app
