# Taekwondo scoring

Django channels web-app

## Prequirements:

- [python 3.6](https://www.python.org/downloads/)
- [redis](https://redis.io/download) ([config url](https://github.com/van4oza/taekwondo/blob/e6de2490c741d6549d76272d6e083aeeff56a8da/taekwondo/settings.py#L79))

## Installation:

```
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

As superuser, **create group** `Judges` in admin panel:

`/admin/auth/group/add/`

**Create users** and **specify** that they're in `Judges` group:

`/admin/auth/user/add/`

## Deploy:

- change and hide [SECRET KEY](https://github.com/van4oza/taekwondo/blob/33fc64a2354980045655222574c6cd9cf7ae39f8/taekwondo/settings.py#L23)
- [DEBUG](https://github.com/van4oza/taekwondo/blob/80093d221fb94e67df697751f0ce439f5fa807e0/taekwondo/settings.py#L26) = False
- set [ALLOWED_HOSTS](https://github.com/van4oza/taekwondo/blob/80093d221fb94e67df697751f0ce439f5fa807e0/taekwondo/settings.py#L28)
- config [SSL](https://github.com/van4oza/taekwondo/blob/80093d221fb94e67df697751f0ce439f5fa807e0/taekwondo/settings.py#L84) (as on your nginx or whatever)
- `python manage.py collectstatic`