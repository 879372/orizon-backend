# Orizon Backend

Django + PostgreSQL REST API backend for the multitenant construction management system.

## Tech Stack
- Python 3.12+
- Django 5.x
- Django REST Framework (DRF)
- djangorestframework-simplejwt (JWT auth)
- drf-spectacular (OpenAPI/Swagger docs)
- PostgreSQL

## Setup & Running
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure environment variables in `.env`.
3. Run migrations and start server:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```
