"""
WSGI config for TV_LEARNING project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys
from threading import Thread

from django.core.wsgi import get_wsgi_application

from preprocessor.models import PreprocessingMovie

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TV_LEARNING.settings')

application = get_wsgi_application()

if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
    Thread(target=PreprocessingMovie.thread_dispatcher).start()
