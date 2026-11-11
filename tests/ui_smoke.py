"""Browser smoke test for the running FitClub demo stand."""

from __future__ import annotations

import os

from playwright.sync_api import sync_playwright


BASE_URL = os.environ.get("FITCLUB_BASE_URL", "http://127.0.0.1:5000")
ADMIN_LOGIN = os.environ.get("FITCLUB_ADMIN_LOGIN", "admin")
ADMIN_PASSWORD = os.environ.get("FITCLUB_ADMIN_PASSWORD")


def main() -> None:
    if not ADMIN_PASSWORD:
        raise RuntimeError("FITCLUB_ADMIN_PASSWORD must be set for UI smoke")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"{BASE_URL}/health")
        assert page.locator("body").inner_text().find('"status":"ok"') >= 0
        page.goto(f"{BASE_URL}/login")
        page.get_by_label("Логин").fill(ADMIN_LOGIN)
        page.get_by_label("Құпиясөз").fill(ADMIN_PASSWORD)
        page.get_by_role("button", name="Кіру").click()
        page.wait_for_url("**/dashboard")
        assert page.get_by_role("heading", name="Клуб жұмысы. Бір экранда.").is_visible()
        page.goto(f"{BASE_URL}/clients")
        assert page.get_by_text("Клиенттер").first.is_visible()
        browser.close()
    print("UI smoke: PASS (health, admin login, dashboard, clients)")


if __name__ == "__main__":
    main()
