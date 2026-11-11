# Автоматтандырылған тексеру нәтижелері

**Күні:** 2026-11-11  
**Commit:** тексеру сәтіндегі жұмыс көшірмесі

| Тексеру | Нәтиже | Дәлел |
|---|---|---|
| pytest | PASS, 9/9 | `python -m pytest -q` |
| Playwright UI smoke | PASS | health, admin login, dashboard, clients |
| k6 | PASS | 495 сұрау, 0 қате, p95 3,08 ms |
| Docker Compose синтаксисі | PASS | `docker compose config` |
| Docker Compose runtime | PASS | FitClub `healthy`, Uptime Kuma 2.5.9 `healthy` |
| Uptime Kuma monitor | PENDING | жергілікті admin setup растауын күтеді |
| Controlled incident | PASS | 503 анықталды, init-db кейін 200, UI retest PASS |

`PENDING` сәтті нәтиже ретінде есептелмейді. Kuma ішінде `http://fitclub:5000/health` HTTP monitor-ы жасалып, 503 → DOWN → recovery → UP тізбегі дәлелденуі керек.
