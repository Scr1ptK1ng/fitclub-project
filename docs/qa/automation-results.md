# Автоматтандырылған тексеру нәтижелері

**Күні:** 2026-11-11  
**Commit:** тексеру сәтіндегі жұмыс көшірмесі

| Тексеру | Нәтиже | Дәлел |
|---|---|---|
| pytest | PASS, 9/9 | `python -m pytest -q` |
| Playwright UI smoke | PASS | health, admin login, dashboard, clients |
| k6 | PASS | 495 сұрау, 0 қате, p95 3,08 ms |
| Docker Compose синтаксисі | PASS | `docker compose config` |
| Uptime Kuma runtime | NOT RUN | Docker Desktop engine компьютерде қолжетімсіз |
| Controlled incident | PASS | 503 анықталды, init-db кейін 200, UI retest PASS |

`NOT RUN` сәтті нәтиже ретінде есептелмейді. Docker engine қолжетімді машинада `docker compose up --build -d` орындалып, Kuma ішінде `http://fitclub:5000/health` HTTP monitor-ы жасалуы керек.
