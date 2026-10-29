# FitClub MVP

Sprint 1 тік срезі: әкімші жүйеге кіреді, клиентті тіркейді және аты не байланысы бойынша іздейді.

## Жергілікті іске қосу

```text
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
set FLASK_APP=fitclub
set FITCLUB_DATABASE_URL=sqlite:///fitclub.db
.venv\Scripts\flask --app fitclub init-db
.venv\Scripts\flask --app fitclub run
```

PostgreSQL үшін `FITCLUB_DATABASE_URL=postgresql+psycopg://user:password@host/database` беріледі.

Алғашқы әкімші `FITCLUB_ADMIN_LOGIN` және `FITCLUB_ADMIN_PASSWORD` орталық айнымалыларымен жасалады. Құпиясөз репозиторийде сақталмайды.
