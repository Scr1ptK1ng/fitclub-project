from __future__ import annotations

from functools import wraps
from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from .models import Client, Membership, Payment, User, db


web = Blueprint("web", __name__)


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("web.login"))
        if session.get("role") != "admin":
            return "Forbidden", 403
        return view(*args, **kwargs)

    return wrapped


@web.route("/")
def index():
    if not session.get("user_id"):
        return redirect(url_for("web.login"))
    return redirect(url_for("web.dashboard") if session.get("role") == "admin" else url_for("web.portal"))


@web.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_value = request.form.get("login", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(login=login_value, active=True).first()
        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session["user_id"] = user.id
            session["role"] = user.role
            return redirect(url_for("web.dashboard") if user.role == "admin" else url_for("web.portal"))
        flash("Кіру деректері қате.", "error")
    return render_template("login.html")


@web.route("/register", methods=["GET", "POST"])
def register():
    values = {
        "full_name": request.form.get("full_name", "").strip(),
        "contact": request.form.get("contact", "").strip(),
    }
    if request.method == "POST":
        password = request.form.get("password", "")
        confirmation = request.form.get("confirmation", "")
        if not values["full_name"] or not values["contact"]:
            flash("Аты-жөні мен байланыс міндетті.", "error")
            return render_template("register.html", values=values), 400
        if len(password) < 8 or password != confirmation:
            flash("Құпиясөз кемінде 8 таңба болуы және қайталануы тиіс.", "error")
            return render_template("register.html", values=values), 400
        if User.query.filter_by(login=values["contact"]).first() or Client.query.filter_by(contact=values["contact"]).first():
            flash("Бұл байланыс бұрын тіркелген.", "error")
            return render_template("register.html", values=values), 409
        db.session.add_all([
            Client(full_name=values["full_name"], contact=values["contact"]),
            User(login=values["contact"], password_hash=generate_password_hash(password), role="client"),
        ])
        db.session.commit()
        flash("Тіркелу сәтті аяқталды. Енді жүйеге кіріңіз.", "success")
        return redirect(url_for("web.login"))
    return render_template("register.html", values=values)


@web.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("web.login"))


@web.route("/dashboard")
@admin_required
def dashboard():
    today = date.today()
    client_count = db.session.scalar(db.select(func.count(Client.id))) or 0
    active_memberships = db.session.scalar(db.select(func.count(Membership.id)).where(Membership.ends_on >= today)) or 0
    paid_total = db.session.scalar(db.select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.status == "paid")) or 0
    recent_clients = Client.query.order_by(Client.created_at.desc()).limit(5).all()
    return render_template(
        "dashboard.html",
        client_count=client_count,
        active_memberships=active_memberships,
        paid_total=paid_total,
        pending_payments=Payment.query.filter_by(status="pending").count(),
        recent_clients=recent_clients,
    )


@web.route("/portal")
def portal():
    if not session.get("user_id"):
        return redirect(url_for("web.login"))
    if session.get("role") != "client":
        return redirect(url_for("web.dashboard"))
    user = db.session.get(User, session["user_id"])
    client = Client.query.filter_by(contact=user.login).first_or_404()
    memberships = Membership.query.filter_by(client_id=client.id).order_by(Membership.ends_on.desc()).all()
    return render_template("portal.html", client=client, memberships=memberships)


@web.route("/clients")
@admin_required
def clients():
    query = request.args.get("q", "").strip()
    items = Client.query.order_by(Client.created_at.desc()).all()
    if query:
        pattern = f"%{query}%"
        items = Client.query.filter(or_(Client.full_name.ilike(pattern), Client.contact.ilike(pattern))).order_by(Client.full_name).all()
    return render_template("clients.html", clients=items, query=query)


@web.route("/clients/<int:client_id>")
@admin_required
def client_detail(client_id: int):
    client = db.get_or_404(Client, client_id)
    memberships = Membership.query.filter_by(client_id=client.id).order_by(Membership.ends_on.desc()).all()
    payments = Payment.query.join(Membership).filter(Membership.client_id == client.id).order_by(Payment.created_at.desc()).all()
    return render_template("client-detail.html", client=client, memberships=memberships, payments=payments)


@web.route("/clients/new", methods=["GET", "POST"])
@admin_required
def new_client():
    values = {"full_name": request.form.get("full_name", "").strip(), "contact": request.form.get("contact", "").strip()}
    if request.method == "POST":
        if not values["full_name"] or not values["contact"]:
            flash("Аты-жөні мен байланыс міндетті.", "error")
            return render_template("client-form.html", values=values), 400
        if Client.query.filter_by(contact=values["contact"]).first():
            flash("Бұл байланыспен клиент бар. Ықтимал дубль.", "error")
            return render_template("client-form.html", values=values), 409
        db.session.add(Client(**values))
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Бұл байланыспен клиент бар. Ықтимал дубль.", "error")
            return render_template("client-form.html", values=values), 409
        flash("Клиент тіркелді.", "success")
        return redirect(url_for("web.clients", q=values["contact"]))
    return render_template("client-form.html", values=values)


@web.route("/clients/<int:client_id>/memberships/new", methods=["GET", "POST"])
@admin_required
def new_membership(client_id: int):
    client = db.get_or_404(Client, client_id)
    values = {
        "starts_on": request.form.get("starts_on", ""),
        "ends_on": request.form.get("ends_on", ""),
        "kind": request.form.get("kind", "limited"),
        "remaining_visits": request.form.get("remaining_visits", ""),
    }
    if request.method == "POST":
        try:
            starts_on = date.fromisoformat(values["starts_on"])
            ends_on = date.fromisoformat(values["ends_on"])
            unlimited = values["kind"] == "unlimited"
            remaining = None if unlimited else int(values["remaining_visits"])
            if ends_on < starts_on:
                raise ValueError("date-order")
            if not unlimited and remaining <= 0:
                raise ValueError("visit-count")
        except (TypeError, ValueError):
            flash("Күндерді және лимитті абонемент үшін оң келу санын тексеріңіз.", "error")
            return render_template("membership-form.html", client=client, values=values), 400
        db.session.add(Membership(client=client, starts_on=starts_on, ends_on=ends_on, unlimited=unlimited, remaining_visits=remaining))
        db.session.commit()
        flash("Абонемент ашылды.", "success")
        return redirect(url_for("web.clients", q=client.contact))
    return render_template("membership-form.html", client=client, values=values)


@web.route("/memberships/<int:membership_id>/extend", methods=["GET", "POST"])
@admin_required
def extend_membership(membership_id: int):
    previous = db.get_or_404(Membership, membership_id)
    values = {
        "starts_on": request.form.get("starts_on", ""),
        "ends_on": request.form.get("ends_on", ""),
        "request_id": request.form.get("request_id", "").strip(),
    }
    if request.method == "POST":
        existing = Membership.query.filter_by(request_id=values["request_id"]).first() if values["request_id"] else None
        if existing:
            flash("Бұл сұрау бұрын өңделген; екінші кезең жасалмады.", "success")
            return redirect(url_for("web.clients", q=previous.client.contact))
        try:
            starts_on = date.fromisoformat(values["starts_on"])
            ends_on = date.fromisoformat(values["ends_on"])
            if not values["request_id"] or ends_on < starts_on or starts_on <= previous.ends_on:
                raise ValueError("invalid-extension")
        except (TypeError, ValueError):
            flash("Request ID және алдыңғы кезеңнен кейінгі дұрыс күндер қажет.", "error")
            return render_template("membership-extend.html", previous=previous, values=values), 400
        db.session.add(Membership(
            client=previous.client,
            starts_on=starts_on,
            ends_on=ends_on,
            unlimited=previous.unlimited,
            remaining_visits=previous.remaining_visits,
            request_id=values["request_id"],
        ))
        db.session.commit()
        flash("Абонемент ұзартылды; бұрынғы кезең тарихта сақталды.", "success")
        return redirect(url_for("web.clients", q=previous.client.contact))
    return render_template("membership-extend.html", previous=previous, values=values)


@web.route("/memberships/<int:membership_id>/payments/new", methods=["GET", "POST"])
@admin_required
def new_payment(membership_id: int):
    membership = db.get_or_404(Membership, membership_id)
    values = {
        "amount": request.form.get("amount", ""),
        "status": request.form.get("status", "paid"),
        "external_reference": request.form.get("external_reference", "").strip(),
        "request_id": request.form.get("request_id", "").strip(),
    }
    if request.method == "POST":
        existing = Payment.query.filter_by(request_id=values["request_id"]).first() if values["request_id"] else None
        if existing:
            flash("Бұл төлем сұрауы бұрын өңделген; қайталама төлем жасалмады.", "success")
            return redirect(url_for("web.clients", q=membership.client.contact))
        try:
            amount = Decimal(values["amount"])
            if amount <= 0 or not values["external_reference"] or not values["request_id"]:
                raise ValueError("invalid-payment")
            if values["status"] not in {"paid", "pending", "cancelled"}:
                raise ValueError("invalid-status")
        except (InvalidOperation, ValueError):
            flash("Оң сома, сыртқы сілтеме, request ID және дұрыс күй қажет.", "error")
            return render_template("payment-form.html", membership=membership, values=values), 400
        db.session.add(Payment(
            membership=membership,
            amount=amount,
            status=values["status"],
            external_reference=values["external_reference"],
            request_id=values["request_id"],
        ))
        db.session.commit()
        flash("Төлем күйі тіркелді.", "success")
        return redirect(url_for("web.clients", q=membership.client.contact))
    return render_template("payment-form.html", membership=membership, values=values)
