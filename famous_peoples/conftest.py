import os
import django


def pytest_configure():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "famous_peoples.settings")
    django.setup()