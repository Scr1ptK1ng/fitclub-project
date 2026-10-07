# Gitleaks және Trivy сканы

## Тексеру паспорты

| Өріс | Мән |
|---|---|
| Репозиторий | `Scr1ptK1ng/fitclub-project` |
| Branch | `main` |
| Commit | `27ea53fc22549cb5c7dba69f32a80b1c15b4d7ab` |
| Тексеру күні | 07.10.2026 |
| Gitleaks | 8.30.1 |
| Trivy | 0.75.0 |

## Нәтиже

- **Gitleaks:** 1 commit және 334.52 KB тексерілді; құпия кілт табылған жоқ.
- **Trivy:** filesystem режимінде `secret,misconfig` сканерлері іске қосылды; finding табылған жоқ.
- Нәтижелер: `scans/gitleaks.json` және `scans/trivy.json`.

## Шектеу және RAID шешімі

Ағымдағы репозиторий негізінен құжаттардан тұрады; тәуелділік lock-файлдары, контейнер манифестері және өндірістік конфигурация жоқ. Сондықтан нөлдік finding «болашақ код толық қауіпсіз» дегенді білдірмейді. Бұл факт R08 және R09 тәуекелдерін жаппайды; SEC-03 тапсырмасы сканды код пен конфигурация қосылған сайын қайталауды талап етеді.

Қолданылған ресми нұсқаулықтар:

- Trivy filesystem: https://trivy.dev/docs/latest/target/filesystem/
- Gitleaks: https://github.com/gitleaks/gitleaks
