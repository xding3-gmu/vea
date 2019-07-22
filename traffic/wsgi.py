"""
WSGI config for traffic project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

python_home = '/Volumes/MiniRaid/htdocs/apis/env/bin/python'

# activate_this = python_home + '/bin/activate_this.py'
# execfile(activate_this, dict(__file__=activate_this))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traffic.settings')

application = get_wsgi_application()
