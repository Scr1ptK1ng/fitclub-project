from __future__ import annotations

import os
from datetime import date, timedelta
from decimal import Decimal

import click
from flask import Flask
from werkzeug.security import generate_password_hash

from .models import Client, Membership, Payment, User, db
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

    @app.cli.command("seed-demo")
    def seed_demo_command() -> None:
        """Add presentation-ready demo records without replacing user data."""
        today = date.today()
        samples = [
            ("Аружан Нұрлан", "member@fitclub.kz", True, None, "paid", Decimal("24000")),
            ("Данияр Қасым", "+77015550102", False, 8, "pending", Decimal("18000")),
            ("Мадина Әли", "+77015550103", False, 2, "paid", Decimal("20000")),
        ]
        for index, (name, contact, unlimited, visits, payment_status, amount) in enumerate(samples, start=1):
            client = Client.query.filter_by(contact=contact).first()
            if not client:
                client = Client(full_name=name, contact=contact)
                db.session.add(client)
                db.session.flush()
            membership = Membership.query.filter_by(client_id=client.id, request_id=f"demo-membership-{index}").first()
            if not membership:
                membership = Membership(
                    client=client,
                    starts_on=today - timedelta(days=12),
                    ends_on=today + timedelta(days=18 + index * 4),
                    unlimited=unlimited,
                    remaining_visits=visits,
                    request_id=f"demo-membership-{index}",
                )
                db.session.add(membership)
                db.session.flush()
            if not Payment.query.filter_by(request_id=f"demo-payment-{index}").first():
                db.session.add(Payment(
                    membership=membership,
                    amount=amount,
                    status=payment_status,
                    external_reference=f"DEMO-{202600 + index}",
                    request_id=f"demo-payment-{index}",
                ))
        if not User.query.filter_by(login="member@fitclub.kz").first():
            db.session.add(User(login="member@fitclub.kz", password_hash=generate_password_hash("MemberDemo2026"), role="client"))
        db.session.commit()
        click.echo("Demo data added.")

    return app
