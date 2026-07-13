"""
Flask Application Factory.

create_app() builds and returns a fully configured Flask app:
  - loads config from environment (.env)
  - initializes extensions (db, scheduler)
  - registers blueprints
  - (Phase 6+) starts the APScheduler background sync job

Kept deliberately simple per project rules: no auth, no cloud config,
single SQLite file, single Windows PC deployment target.
"""

import os

from flask import Flask
from dotenv import load_dotenv

from app.config import config_by_name
from app.extensions import db, scheduler

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

    _init_extensions(app)
    _register_blueprints(app)

    # APScheduler is wired up starting Phase 6, once email_service.sync_emails()
    # exists. Left as a placeholder comment here so the factory's final shape
    # is visible now:
    #
    # if not scheduler.running:
    #     scheduler.add_job(
    #         func=sync_emails_job,
    #         trigger="interval",
    #         minutes=app.config["SYNC_INTERVAL_MINUTES"],
    #         id="email_sync_job",
    #         replace_existing=True,
    #     )
    #     scheduler.start()

    return app


def _init_extensions(app):
    db.init_app(app)


def _register_blueprints(app):
    from app.blueprints.dashboard import dashboard_bp
    from app.blueprints.tickets import tickets_bp
    from app.blueprints.email_sync import email_sync_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(email_sync_bp)
