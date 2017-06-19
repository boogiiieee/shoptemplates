#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys

# По умолчанию используется версия Django 1.3,
# если вы хотите использовать другие версии, закомментируйте строку ниже и раскомментируйте нужную вам версию.
sys.path.insert(0, '/opt/django-1.3/lib/python2.6/site-packages/')

# Раскомментировать для версии Django 1.2.3
# sys.path.insert(0, '/opt/django-1.2.3/lib/python2.5/site-packages')

# Раскомментировать для версии Django 1.1.1
# sys.path.insert(0, '/opt/django-1.1.1/lib/python2.5/site-packages')

# Если закомментировать все версии, будет использоваться версия, установленная на сервере.

# Добавьте нужные вам пути поиска.
# Если вы получаете ошибку 500 Internal Server Error,
# скорее всего проблема именно в путях поиска.

sys.path.insert(0, '/home/hosting_gladkiyva/projects/shop/www')
#sys.path.insert(0, '/home/hosting_gladkiyva/projects/shop')


os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

# ------ Ниже этой линии изменения скорее всего не нужны --------

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
