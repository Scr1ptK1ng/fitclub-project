# FitClub ЛЗ9 — екі спринттегі ағын метрикасы

## Орындау форматы

Методикадағы екі апталық кезең уақыт шектеуіне байланысты 29.10.2026 күні екі **жеделдетілген оқу прогоны** ретінде орындалды. GitHub оқиғалары мен timestamp-тары өзгертілмеді. Сондықтан төмендегі сандар құралдан алынған нақты осы прогон метрикасы, бірақ өндірістік команданың апталық өнімділігі деп түсіндірілмейді.

## Workflow

Бағандар: Backlog → Ready → In Progress → Review → Test → Waiting for customer → Done. Толық WIP, transition policy, DoR және DoD: [workflow-policy.md](workflow-policy.md).

## Метрика салыстыруы

| Метрика | Sprint 1 | Sprint 2 | Түсіндіру |
|---|---:|---:|---|
| Scope / throughput | 5 / 5 | 3 / 3 | екі sprint-та таңдалған жұмыстың 100%-ы жабылды; абсолют throughput scope әртүрлі болғандықтан тікелей өнімділік салыстыруы емес |
| Орташа cycle time | 0,033 сағ | 0,017 сағ | 48,5% төмен |
| p85 cycle time | 0,072 сағ | 0,018 сағ | 75,0% төмен |
| Developer WIP max | бірнеше карточка кеш белгіленді | 1 | Sprint 2-де эксперимент шарты орындалды |

Бастапқы дерек:

- `artifacts/sprint-1/work-items.csv`, `event-cfd.csv`, `raw-issues-events.json`;
- `artifacts/sprint-2/work-items.csv`, `event-cfd.csv`, `raw-issues-events.json`;
- [CFD салыстыруы](cfd-comparison.svg).

## Bottleneck және өзгеріс

Sprint 1-дегі bottleneck кодта емес, ағынды белгілеу тәртібінде болды: карточкалар нақты жұмыс басталған сәтте емес, кейінірек `In Progress` күйіне өтті. Нәтижесінде тақта шешім қабылдауға кеш ақпарат берді және cycle time инженерлік уақыттың барлығын қамтымады.

Ретроспективада **дәл бір әрекет** таңдалды: Айдос developer WIP лимитін 3-тен 1-ге азайтады және келесі карточканы алдыңғысы `Done` болғаннан кейін ғана бастайды. Sprint 2 event тарихы осы шарттың орындалғанын көрсетеді.

## Қорытынды

WIP=1 кезінде орташа және p85 cycle time төмендеді, ал бір мезетте ашық әзірлеу жұмысы болмады. Бірақ үш маңызды шектеу бар: прогон өте қысқа, карточкалар саны аз және екі sprint scope-ы әртүрлі. Сондықтан «WIP=1 әрқашан 75% жақсартады» деген себептік қорытынды жасалмайды. Нақты апталық cadence-те экспериментті қайталау — нәтижені растаудың дұрыс жолы.

## ЛЗ9 талабының орындалуы

| Талап | Дәлел |
|---|---|
| баған, WIP, transition policy, DoR/DoD | `workflow-policy.md` |
| Sprint Goal және Sprint 1 review/retro | `sprint-1-plan.md`, `sprint-1-review-retro.md` |
| throughput, average/p85 cycle time, CFD | екі `artifacts/sprint-*` бумасы және `cfd-comparison.svg` |
| bottleneck | осы есептің «Bottleneck және өзгеріс» бөлімі |
| дәл бір ретро әрекет және owner | WIP 3→1, owner Айдос |
| Sprint 2 және салыстыру | `sprint-2-plan.md`, `sprint-2-review.md`, осы кесте |
