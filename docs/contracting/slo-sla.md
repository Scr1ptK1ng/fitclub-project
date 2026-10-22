# FitClub SLO, SLA және error budget

Күйі: оқу жобасының draft-ы; production келісімі емес.

## Қызмет көрсету шекарасы

- service window: 08:00–20:00, аптасына 7 күн;
- өлшеу терезесі: күнтізбелік ай;
- availability мақсаты: 99%; жоспарлы тоқтау да есепке кіреді;
- RPO: 24 сағат; RTO: 4 сағат.

## Үш негізгі сценарий

| Сценарий | SLI | SLO | Error budget | Нөлдік төзім | Дәлел |
|---|---|---|---|---|---|
| Клиентті іздеу және абонемент мәртебесін ашу | дұрыс рөлмен ≤1 с жауап берген valid request / барлық valid request | айына ≥99%; p95 ≤1 с | valid request-тің ≤1%-ы | unauthorized data disclosure — 0 | request log, RBAC test |
| Жаттығуға жазылу немесе бас тарту | ≤1 с ішінде бір ғана нәтиже жасаған valid operation / барлық valid operation | айына ≥99%; p95 ≤1 с | valid operation-ның ≤1%-ы | double booking — 0 | integration test, audit log |
| Қатысу немесе төлем мәртебесін тіркеу | ≤1 с ішінде сақталған және audit бар valid operation / барлық valid operation | айына ≥99%; p95 ≤1 с | valid operation-ның ≤1%-ы | duplicate және unauthorized change — 0 | idempotency test, audit log |

## SLA міндеттемесі

- service window ішінде айлық availability кемінде 99%;
- үш сценарийдің p95 уақыты 1 секундтан аспайды және күтпеген server error 1%-дан төмен;
- backup және қалпына келтіру RPO ≤24 сағат, RTO ≤4 сағат шегінде;
- рұқсатсыз қол жеткізу, double booking және duplicate write қалыпты қате budget-іне кірмейді.

## Error budget есебі

30 күндік мысал:

`30 күн × 12 сағат = 360 жоспарланған сағат`  
`360 × (1 − 0,99) = 3,6 сағат = 3 сағат 36 минут`

ЛЗ3-тегі 600 операция болжамымен request budget: `600 × 1% = 6` баяу не күтпеген қатесі бар операция. Нақты айда 600 саны production log-пен ауыстырылады.

## Budget біткендегі әрекет

Жаңа функция шығару тоқтайды; incident issue ашылады; Айдос root-cause пен recovery plan дайындайды; Әділбек қайта тест жүргізеді; Ануар оқытушыға статус пен шешімді жеткізеді. Оқу жобасында қаржылық service credit жоқ.

