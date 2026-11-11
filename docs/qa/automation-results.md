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
| Uptime Kuma monitor | PASS | `FitClub Health`: 20 секундтық HTTP тексеру; `UP → DOWN → UP` нақты тіркелді |
| Controlled incident | PASS | 503 анықталды, init-db кейін 200, UI retest PASS |

## Uptime Kuma recovery retest

- Monitor: `FitClub Health`, URL: `http://fitclub:5000/health`, интервал: 20 секунд.
- Қалыпты күй: `UP`, HTTP 200.
- FitClub контейнері әдейі тоқтатылғанда Kuma `DOWN` күйін және timeout қатесін тіркеді.
- Контейнер қайта іске қосылғаннан кейін 2026-11-11 21:39:32 +05 кезінде monitor `UP`, `200 - OK`, ағымдағы жауап уақыты 3 ms көрсетті.
- Тест кезінде 7 heartbeat жиналды: 4 `UP`, 3 `DOWN`. Бұл пайыз production SLA емес, қысқа басқарылатын эксперименттің нәтижесі.

