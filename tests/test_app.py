from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from werkzeug.security import generate_password_hash

from fitclub import create_app
from fitclub.models import Client, Membership, User, db


class FitClubTestCase(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        database = Path(self.tempdir.name) / "test.db"
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-key",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database.as_posix()}",
        })
        with self.app.app_context():
            db.create_all()
            db.session.add(User(login="admin", password_hash=generate_password_hash("correct-password"), role="admin"))
            db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()
        self.tempdir.cleanup()

    def login(self, password="correct-password"):
        return self.client.post("/login", data={"login": "admin", "password": password}, follow_redirects=True)

    def test_login_success_and_wrong_password_is_generic(self):
        response = self.login("wrong")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Кіру деректері қате".encode(), response.data)
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Клиенттер".encode(), response.data)

    def test_clients_require_authentication(self):
        response = self.client.get("/clients")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/login"))

    def test_register_validate_duplicate_and_search(self):
        self.login()
        missing = self.client.post("/clients/new", data={"full_name": "", "contact": "+77010000000"})
        self.assertEqual(missing.status_code, 400)
        created = self.client.post("/clients/new", data={"full_name": "Аян Серік", "contact": "+77010000000"}, follow_redirects=True)
        self.assertEqual(created.status_code, 200)
        self.assertIn("Аян Серік".encode(), created.data)
        duplicate = self.client.post("/clients/new", data={"full_name": "Басқа адам", "contact": "+77010000000"})
        self.assertEqual(duplicate.status_code, 409)
        by_name = self.client.get("/clients?q=Аян")
        self.assertIn("Аян Серік".encode(), by_name.data)
        empty = self.client.get("/clients?q=жоқ")
        self.assertIn("Сәйкес клиент табылмады".encode(), empty.data)
        with self.app.app_context():
            self.assertEqual(Client.query.count(), 1)

    def test_open_limited_and_unlimited_membership(self):
        self.login()
        self.client.post("/clients/new", data={"full_name": "Аян Серік", "contact": "+77010000000"})
        with self.app.app_context():
            client_id = Client.query.one().id
        invalid = self.client.post(f"/clients/{client_id}/memberships/new", data={
            "starts_on": "2026-11-01", "ends_on": "2026-10-31", "kind": "limited", "remaining_visits": "0"
        })
        self.assertEqual(invalid.status_code, 400)
        limited = self.client.post(f"/clients/{client_id}/memberships/new", data={
            "starts_on": "2026-11-01", "ends_on": "2026-12-01", "kind": "limited", "remaining_visits": "8"
        }, follow_redirects=True)
        self.assertIn("8 келу қалды".encode(), limited.data)
        unlimited = self.client.post(f"/clients/{client_id}/memberships/new", data={
            "starts_on": "2026-12-02", "ends_on": "2027-01-02", "kind": "unlimited", "remaining_visits": ""
        }, follow_redirects=True)
        self.assertIn("лимитсіз".encode(), unlimited.data)
        with self.app.app_context():
            self.assertEqual(Membership.query.count(), 2)
            self.assertIsNone(Membership.query.order_by(Membership.id.desc()).first().remaining_visits)


if __name__ == "__main__":
    unittest.main()
