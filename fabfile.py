# -*- coding: utf-8 -*-
from fabric.api import task, local, prefix


# ==============================================================================
# Docker
# ==============================================================================

@task
def build():
    local('docker-compose build')


@task
def start(port='8000'):
    with prefix('export APP_PORT=%s' % port):
        local('docker-compose up -d')


@task
def stop():
    local('docker-compose down')


@task
def status():
    local('docker-compose ps')


@task
def migrate(app='', fake=False):
    local('docker-compose exec django python manage.py migrate %s %s' % (
        app, '--fake-initial' if fake else ''
    ))


@task
def makemigrations(app=''):
    local('docker-compose exec django python manage.py makemigrations %s' % app)


@task
def runserver():
    local('docker-compose exec django python manage.py runserver 0.0.0.0:8000')


@task
def celeryw():
    local('docker-compose exec django celery -A comments worker -l info -B')


@task
def celeryb():
    local('docker-compose exec django celery -A comments beat')


@task
def shell():
    local('docker-compose exec django python manage.py shell')


@task
def manage(command):
    local('docker-compose exec django python manage.py %s' % command)


@task
def runtests(app=''):
    local('docker-compose exec django python manage.py test %s --keepdb' % app)
