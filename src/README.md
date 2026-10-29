# FitClub MVP

FitClub web MVP: әкімші dashboard-ы, клиент базасы, абонемент/төлем тарихы және клиенттің жеке кабинеті.

## Негізгі мүмкіндік

- әкімші dashboard-ы және негізгі KPI;
- клиентті тіркеу, іздеу және толық профиль;
- лимитті/лимитсіз абонемент, ұзарту және төлем;
- клиенттің өздігінен тіркелуі және жеке кабинеті;
- идемпотентті ұзарту/төлем және рөлдік қолжетімділік;
- презентацияға арналған `flask --app fitclub seed-demo` деректері.

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
