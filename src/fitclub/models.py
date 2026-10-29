from __future__ import annotations

from datetime import UTC, date, datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="admin")
    active = db.Column(db.Boolean, nullable=False, default=True)


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(160), nullable=False, index=True)
    contact = db.Column(db.String(120), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))
    memberships = db.relationship("Membership", back_populates="client", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("contact", name="uq_client_contact"),)


class Membership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False, index=True)
    starts_on = db.Column(db.Date, nullable=False)
    ends_on = db.Column(db.Date, nullable=False)
    unlimited = db.Column(db.Boolean, nullable=False, default=False)
    remaining_visits = db.Column(db.Integer)
    request_id = db.Column(db.String(80), unique=True, index=True)
    client = db.relationship("Client", back_populates="memberships")
    payments = db.relationship("Payment", back_populates="membership", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("ends_on >= starts_on", name="ck_membership_date_order"),
        CheckConstraint("remaining_visits IS NULL OR remaining_visits >= 0", name="ck_membership_visits_nonnegative"),
    )

    @property
    def status(self) -> str:
        return "active" if self.ends_on >= date.today() else "expired"


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    membership_id = db.Column(db.Integer, db.ForeignKey("membership.id"), nullable=False, index=True)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="paid")
    external_reference = db.Column(db.String(120), nullable=False)
    request_id = db.Column(db.String(80), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))
    membership = db.relationship("Membership", back_populates="payments")

    __table_args__ = (CheckConstraint("amount > 0", name="ck_payment_positive"),)
