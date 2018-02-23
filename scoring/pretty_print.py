def pretty_search_or_print(dict_or_list, key_to_search=None, search_for_first_only=False, print_spaces=0):
    if key_to_search:
        search_result = set()
        if isinstance(dict_or_list, dict):
            for key in dict_or_list:
                key_value = dict_or_list[key]
                if key == key_to_search and key_value != 399650832 and len(str(key_value)) == 9 or len(
                        str(key_value)) > 12:
                    try:
                        search_result.add(key_value)
                    except:
                        print(pretty_search_or_print(key_value))
                if isinstance(key_value, dict) or isinstance(key_value, list) or isinstance(key_value, set):
                    _search_result = pretty_search_or_print(key_value, key_to_search)
                    if _search_result:
                        for result in _search_result:
                            if result != 399650832 and len(str(result)) == 9 or len(str(result)) > 12:
                                try:
                                    search_result.add(result)
                                except:
                                    print(pretty_search_or_print(result))
        elif isinstance(dict_or_list, list) or isinstance(dict_or_list, set):
            for element in dict_or_list:
                if isinstance(element, list) or isinstance(element, set) or isinstance(element, dict):
                    _search_result = pretty_search_or_print(element, key_to_search)
                    if _search_result:
                        for result in _search_result:
                            if result != 399650832 and len(str(result)) == 9 or len(str(result)) > 12:
                                try:
                                    search_result.add(result)
                                except:
                                    print(pretty_search_or_print(result))
        return search_result if not search_for_first_only else list(search_result)[0]
    else:
        pretty_text = ""
        if isinstance(dict_or_list, dict):
            for key in dict_or_list:
                key_value = dict_or_list[key]
                if isinstance(key_value, dict):
                    key_value = pretty_search_or_print(key_value, print_spaces=print_spaces + 1)
                    pretty_text += "-\t" * print_spaces + "{}:\n{}\n".format(key, key_value)
                elif isinstance(key_value, list) or isinstance(key_value, set):
                    pretty_text += "-\t" * print_spaces + "{}:\n".format(key)
                    for element in key_value:
                        if isinstance(element, dict) or isinstance(element, list) or isinstance(element, set):
                            pretty_text += pretty_search_or_print(element, print_spaces=print_spaces + 1)
                        elif element:
                            pretty_text += "-\t" * (print_spaces + 1) + "{}\n".format(element)
                else:
                    pretty_text += "-\t" * print_spaces + "{}: {}\n".format(key, key_value)
        elif isinstance(dict_or_list, list) or isinstance(dict_or_list, set):
            for element in dict_or_list:
                if isinstance(element, dict) or isinstance(element, list) or isinstance(element, set):
                    pretty_text += pretty_search_or_print(element, print_spaces=print_spaces + 1)
                elif element:
                    pretty_text += "-\t" * print_spaces + "{}\n".format(element)
        elif dict_or_list:
            if print_spaces:
                pretty_text += "-\t" * print_spaces + "{}\n".format(dict_or_list)
            else:
                pretty_text += "{}".format(dict_or_list)
        return pretty_text


'''
git config credential.helper 'cache --timeout=2592000'
git config --global credential.helper store

ssh ivan@93.174.131.29

find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

cd legal_consult/
workon django_env
git pull
python3 manage.py makemigrations
python3 manage.py migrate
echo ivan17ivan | sudo -S reboot

cd legal_consult/
git pull
echo ivan17ivan | sudo -S reboot

python3 manage.py collectstatic

cd legal_consult/
workon django_env
python manage.py runworker &
daphne -b 127.0.0.1 -p 8001 legal_consult.asgi:channel_layer &
celery -A legal_consult worker &
celery -A legal_consult beat --scheduler django_celery_beat.schedulers:DatabaseScheduler &

print(len(s), s[0], s[-1])

celery -A legal_consult worker -l info &
python manage.py runworker &
gunicorn -b 127.0.0.1:8001 legal_consult.wsgi &

@reboot workon ur_env && cd /home/ivan/legal_consult/ && python manage.py runworker & && python manage.py runworker & && daphne -b 127.0.0.1 -p 8001 legal_consult.asgi:channel_layer & && celery -A legal_consult worker -l info & && celery -A legal_consult worker -l info & && celery -A legal_consult beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler &


workon ur_env && cd /home/ivan/legal_consult/ && python manage.py runworker && python manage.py runworker && daphne -b 127.0.0.1 -p 8001 legal_consult.asgi:channel_layer && celery -A legal_consult worker -l info && celery -A legal_consult worker -l info && celery -A legal_consult beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler


daphne -e ssl:443:privateKey=/etc/ssl/private/legal-consult.online.2017.private.np.key:certKey=/etc/ssl/private/legal-consult.online.2017.crt legal_consult.asgi:channel_layer


rm -rf audio_items.pkl

find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
cd legal_consult/
workon ur_env
git pull
gunicorn -b 127.0.0.1:8001 legal_consult.wsgi &
celery -A legal_consult worker -l info &
celery -A legal_consult beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler &
python manage.py runworker &
daphne legal_consult.asgi:channel_layer &
celery -A legal_consult worker -l info &
python manage.py runworker &
daphne legal_consult.asgi:channel_layer &
celery -A legal_consult beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler &
deactivate
exit

sudo docker run \
  -d \
  -p 127.0.0.1:3000:3000 \
  --name=grafana \
  -e "GF_SERVER_DOMAIN=185.26.99.145" \
  -e "GF_SERVER_ROOT_URL=http://185.26.99.145/grafana" \
  -e "GF_SECURITY_ADMIN_PASSWORD=C9sGrVgX5jHtl1NB6kbR" \
  grafana/grafana

'''