from __future__ import annotations

import os

import click
from flask import Flask
from werkzeug.security import generate_password_hash

from .models import User, db
from .routes import web


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("FITCLUB_SECRET_KEY", "development-only-change-me"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("FITCLUB_DATABASE_URL", "sqlite:///fitclub.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    app.register_blueprint(web)

    @app.cli.command("init-db")
    def init_db_command() -> None:
        """Create the schema and the first administrator from environment variables."""
        db.create_all()
        login = os.environ.get("FITCLUB_ADMIN_LOGIN")
        password = os.environ.get("FITCLUB_ADMIN_PASSWORD")
        if login and password and not User.query.filter_by(login=login).first():
            db.session.add(User(login=login, password_hash=generate_password_hash(password), role="admin"))
            db.session.commit()
            click.echo("Administrator created.")
        click.echo("Database initialized.")

    return app
