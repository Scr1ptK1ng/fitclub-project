# FitClub хостинг нұсқалары — 3 жыл

Салыстыруға қолданбаны әзірлеу мен ортақ қолдау кірмейді: олар барлық нұсқаға ортақ. Валюта 22.10.2026 ресми бағамымен аударылды: 1 USD = 448,61 ₸; 1 GBP = 600,82 ₸.

| Нұсқа | Жарияланған конфигурация | 3 жылдық құн | Қамтылмағаны |
|---|---|---:|---|
| Public cloud | AWS Lightsail $24 VM + $30 managed PostgreSQL | 872 098 ₸ | салық, traffic overage, қосымша snapshot |
| Өз инфрақұрылымы | Raspberry Pi 5 Starter Kit 8GB, £224.50 | 134 884 ₸ — **төменгі шек** | жеткізу, кеден, UPS, электр, ISP/static IP, ауыстыру |
| Open stack / rented VPS | DigitalOcean $24 Droplet + weekly backup 20% | 465 119 ₸ | салық, traffic overage, DB әкімшілігі |

## Шешім

MVP үшін DigitalOcean VPS-та Ubuntu + PostgreSQL ашық стек ұсынылады:

- ЛЗ3-те таңдалған архитектурамен сәйкес;
- сервер мен weekly backup үшін жарияланған recurring тариф бар;
- код, локализация және интеграция команда бақылауында;
- AWS managed DB нұсқасынан жарияланған инфрақұрылым құны төмен.

Own infrastructure ең төмен санды көрсетеді, бірақ ол толық TCO емес. Расталған электр, интернет/static IP, UPS, жеткізу, кеден және ауыстыру бағасы болмайынша оны толық бағаланған жеңімпаз деп жариялауға болмайды.

## Дереккөздер

- ҚР Ұлттық Банкі: https://nationalbank.kz/kz/exchangerates/ezhednevnye-oficialnye-rynochnye-kursy-valyut
- AWS Lightsail: https://aws.amazon.com/lightsail/pricing/
- DigitalOcean Droplet: https://www.digitalocean.com/pricing/droplets
- DigitalOcean Backups: https://docs.digitalocean.com/products/backups/details/pricing/
- The Pi Hut: https://thepihut.com/products/raspberry-pi-5-starter-kit?variant=42614953214147

