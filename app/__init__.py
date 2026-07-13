"""
Flask Application Factory.

create_app() builds and returns a fully configured Flask app:
  - loads config from environment (.env)
  - initializes the SQLAlchemy extension
  - creates all tables via db.create_all() (no Flask-Migrate / Alembic --
    this is a local single-PC SQLite app, migrations are unnecessary
    complexity for the scope of this project)
  - registers the single routes blueprint

Kept deliberately simple per project rules: no auth, no cloud config,
single SQLite file, single Windows PC deployment target.
"""

import os

from flask import Flask
from dotenv import load_dotenv

from app.config import config_by_name
from app.extensions import db

load_dotenv()  # populate os.environ from .env before Config reads it


def create_app(config_name=None):
    app = Flask(__name__, instance_relative_config=True)

    # Make sure instance/ exists (this is where cdoe.db will live)
    os.makedirs(app.instance_path, exist_ok=True)

    config_name = config_name or os.environ.get("FLASK_ENV", "development")
    app.config.from_object(config_by_name[config_name])

    # SQLite file lives in instance/, regardless of what's in .env, unless
    # an absolute DATABASE_URL was explicitly provided.
    if app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///cdoe.db":
        db_path = os.path.join(app.instance_path, "cdoe.db")
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    db.init_app(app)

    with app.app_context():
        from app import models  # noqa: F401  (import so db.create_all sees them)
        db.create_all()

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app