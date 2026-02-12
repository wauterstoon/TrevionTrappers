# Trappers Manager (Django 5)

Production-ready webapp om een bedrijfs-wielerploeg te beheren: ritten, inschrijvingen, km-punten en klassement.

## Features (MVP)
- Registratie/login/logout/password reset
- Profielen met seizoens-km, all-time km, # uitgereden ritten, historiek
- Ritten aanmaken/bewerken/verwijderen (door maker of staff)
- In/uitschrijven + na-rit verwerking (status en km)
- Anti-cheat basis: na `FINISHED` kan km-aanpassing enkel door ritmaker/admin
- Klassement met seizoensfilter en laatste 30 dagen
- Django admin met filters/list displays
- Sportieve Bootstrap UI + dark mode toggle

## Tech stack
- Django 5.x
- PostgreSQL default-ready (via env) + SQLite fallback voor development
- Django templates + Bootstrap 5 + HTMX script include

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Database & migraties
SQLite (default):
```bash
python manage.py migrate
```

PostgreSQL:
1. Zet env vars (`DB_ENGINE=postgres`, `POSTGRES_*`) of `DATABASE_URL`
2. Run:
```bash
python manage.py migrate
```

## Superuser
```bash
python manage.py createsuperuser
```

## Runserver
```bash
python manage.py runserver
```

## Tests
```bash
python manage.py test
```

## Kernpagina's
- `/` dashboard
- `/rides/` rittenlijst
- `/rides/<id>/` ritdetail + inschrijven/uitschrijven/finish
- `/rides/<id>/process/` na-rit verwerking
- `/leaderboard/` klassement
- `/accounts/profile/<username>/` profiel
- `/admin/` beheer

## Screenshots (beschrijving)
- Dashboard: card-grid met komende ritten + topklassement
- Ritten detail: ritkaart + CTA's + deelnemers met status badges
- Klassement: ranking tabel met highlight van je eigen positie
