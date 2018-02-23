# Taekwondo scoring

Django channels web-app

## Prequirements:

- python3.6
- redis ([config url](https://github.com/van4oza/taekwondo/blob/e6de2490c741d6549d76272d6e083aeeff56a8da/taekwondo/settings.py#L79))

## Installation:

```
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
python manage.py runserver
```

As superuser, **create group** `Judges` in admin panel:

`/admin/auth/group/add/`

**Create users** and **specify** that they're in `Judges` group:

`/admin/auth/user/add/`