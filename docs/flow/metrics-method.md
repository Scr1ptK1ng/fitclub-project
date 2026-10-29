# Ағын метрикасын GitHub-тан алу әдісі

## Бастапқы дерек

Метриканың жалғыз бастапқы дерегі — GitHub Issues API және issue event тарихы. Қолмен енгізілген «жабылды» күні cycle time есебіне қолданылмайды.

## Күй оқиғалары

- басталу уақыты — issue-ге `status:in-progress` label қосылған уақыт;
- аяқталу уақыты — GitHub issue `closed` оқиғасының уақыты;
- аралық күй — тиісті `status:*` label қосылған уақыт;
- reopen болса, жаңа жұмыс интервалы бөлек белгіленеді және есепте түсіндіріледі.

## Формулалар

- `throughput` — спринт ішінде жабылған жұмыс саны;
- `cycle time` — `closed_at − first_in_progress_at`;
- `average cycle time` — жабылған жұмыстар cycle time арифметикалық ортасы;
- `p85 cycle time` — жабылған cycle time мәндерінің nearest-rank 85-перцентилі;
- `WIP` — сол күнде In Progress, Review, Test немесе Waiting күйіндегі карточка саны;
- `work item age` — ашық карточка үшін `snapshot_at − first_in_progress_at`;
- CFD — әр күн соңындағы Backlog/Ready/In Progress/Review/Test/Waiting/Done санының кумулятивті көрінісі.

## Неліктен 29.10.2026 күні қорытынды метрика жоқ

Репозиторийде бұрыннан issue-лер бар, бірақ workflow status label тарихы мен екі спринттің жабылған карточкалары жоқ. Сондықтан екі спринтті салыстыратын санды қазір жазу — методикадағы «метрика құралдан алынуы тиіс» талабын бұзады.

## Экспорт

`python scripts/export_flow_metrics.py --repo Scr1ptK1ng/fitclub-project --sprint "Sprint 1" --start 2026-10-29 --end 2026-11-04 --out artifacts/sprint-1`

Скрипт GitHub API-ден issue, milestone және event оқиғаларын алады. `work-items.csv` cycle time-ды, `daily-cfd.csv` күндік кесіндіні, `event-cfd.csv` әр status/close оқиғасынан кейінгі CFD күйін сақтайды. `raw-issues-events.json` — қайта тексеруге арналған бастапқы экспорт.

