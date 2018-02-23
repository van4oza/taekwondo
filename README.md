# Taekwondo scoring

Django channels web-app

## Prequirements:

- python3.6
- redis

## Installation:

```
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
python manage.py runserver
```

As superuser, create group `Judges` in admin panel:

`/admin/auth/group/add/`

Create users for Judges:

`/admin/auth/user/add/`

Then add them to `Judges` group.