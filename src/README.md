# FitClub MVP

FitClub web MVP: әкімші dashboard-ы, клиент базасы, абонемент/төлем тарихы және клиенттің жеке кабинеті.

## Негізгі мүмкіндік

- әкімші dashboard-ы және негізгі KPI;
- клиентті тіркеу, іздеу және толық профиль;
- лимитті/лимитсіз абонемент, ұзарту және төлем;
- клиенттің өздігінен тіркелуі және жеке кабинеті;
- идемпотентті ұзарту/төлем және рөлдік қолжетімділік;
- презентацияға арналған `flask --app fitclub seed-demo` деректері.
- `/health` арқылы қолданба мен дерекқор дайындығын тексеру.

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

## ЛЗ11 Docker стенді

```text
set FITCLUB_SECRET_KEY=<кездейсоқ-құпия-мән>
set FITCLUB_ADMIN_PASSWORD=<демо-әкімші-құпиясөзі>
docker compose up --build -d
```

FitClub: `http://localhost:5000`, Uptime Kuma 2: `http://localhost:3001`. Kuma monitor URL: `http://fitclub:5000/health`.

Құпия мәндерді репозиторийге қоспау үшін `.env.example` файлын `.env` ретінде көшіріп, мәндерін ауыстыруға болады.

Алғашқы әкімші `FITCLUB_ADMIN_LOGIN` және `FITCLUB_ADMIN_PASSWORD` орталық айнымалыларымен жасалады. Құпиясөз репозиторийде сақталмайды.
