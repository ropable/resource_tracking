"""
WSGI config for resource_tracking project.
It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# These lines are required for interoperability between local and container environments.
d = Path(__file__).resolve().parent.parent
dot_env = os.path.join(str(d), ".env")
if os.path.exists(dot_env):
    from dotenv import load_dotenv

    load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "resource_tracking.settings")
application = get_wsgi_application()
