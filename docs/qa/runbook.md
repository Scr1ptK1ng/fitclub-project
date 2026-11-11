# Runbook: FitClub немесе дерекқор қолжетімсіз

## Триггер және жауаптылар

Триггер: Uptime Kuma `/health` үшін екі рет қатарынан 200-ден өзге жауап алды немесе пайдаланушы кіре алмайды. Incident commander — Ануар; техникалық орындаушы — Айдос; тексеруші — Әділбек.

## 1. Растау және хабарлау

1. `http://localhost:5000/health` ашып, HTTP коды мен уақытын жазу.
2. `docker compose ps` арқылы `fitclub` және `uptime-kuma` күйін тексеру.
3. Ануарға басталу уақытын, әсерді және келесі жаңарту уақытын хабарлау.
4. Контейнерді немесе volume-ды бірден жоймау.

## 2. Диагностика

```text
docker compose logs --since 10m fitclub
docker compose exec fitclub flask --app fitclub init-db
docker compose ps
```

`no such table` қатесі схема инициализациясын көрсетеді. Құпиясөзді, cookie-ді немесе дерекқор файлын логқа көшірмеу керек.

## 3. Қалпына келтіру

1. `docker compose exec fitclub flask --app fitclub init-db` орындау.
2. `docker compose restart fitclub` орындау.
3. 30 секунд ішінде `/health` қайта тексеру.
4. Әділбек UI smoke орындайды: әкімші кіруі, dashboard және клиент іздеуі.
5. Uptime Kuma күйі `UP` болғанын растау.

## 4. Откат шарты

Егер init және бір restart-тен кейін `/health` 503 болып қалса немесе дерек бүліну белгісі болса, өзгерісті тоқтату, volume көшірмесін сақтау және соңғы белгілі жұмыс істейтін image/commit-ке оралу. Дерекқор volume-ын жоюға Incident commander рұқсат бермейді.

## 5. Жабу

Қалпына келу уақыты, әсер, лог үзіндісі және тексеру нәтижесі incident issue-ға жазылады. 2 жұмыс күні ішінде postmortem өткізіліп, әрекеттер backlog-қа енгізіледі.
