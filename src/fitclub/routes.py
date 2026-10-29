from __future__ import annotations

from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash

from .models import Client, User, db


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
    return redirect(url_for("web.clients") if session.get("user_id") else url_for("web.login"))


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
            return redirect(url_for("web.clients"))
        flash("Кіру деректері қате.", "error")
    return render_template("login.html")


@web.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("web.login"))


@web.route("/clients")
@admin_required
def clients():
    query = request.args.get("q", "").strip()
    items = []
    if query:
        pattern = f"%{query}%"
        items = Client.query.filter(or_(Client.full_name.ilike(pattern), Client.contact.ilike(pattern))).order_by(Client.full_name).all()
    return render_template("clients.html", clients=items, query=query)


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
