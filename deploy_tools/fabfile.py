import random
from fabric.contrib.files import append, exists
from fabric.api import cd, env, local, run

REPO_URL = 'https://github.com/illyakaynov/python-tdd-book'

def _create_or_update():
    append('.env', 'DJANGO_DEBUG_FALSE=y')
    append('.env', f'SITENAME={env.host}')
    current_contents = run('cat .env')
    if 'DJANGO_SECRET_KEY':
        new_secret = ''.join(random.SystemRandom().choices(
            'abcdefghijklmnopqrstuvwxyz0123456789', k=50
        ))
    append('.env', f'DJANGO_SECRET_KEY={new_secret}')

def _udpate_static_files():
    run('./virtualenv/bin/python manage.py collectstatic --noinput')

def _update_datavase():
    run('./virtualenv/bin/python manage.py migrate --noinput')

