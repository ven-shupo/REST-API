"""
WSGI config for Yandex project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os, sys
sys.path.append('/home/entrance/REST-API')
sys.path.append('/home/entrance/REST-API/env/Lib/site-packages')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Yandex.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
