import sys

import django
from unipath import Path
from django.conf import settings
from django.core.management import execute_from_command_line

BASE_DIR = Path(__file__).ancestor(2)

print(BASE_DIR)

sys.path.append(BASE_DIR.absolute())


settings.configure(
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR.child('db.sqlite3')
        }
    },
    INSTALLED_APPS=[
        'django_pg_commands',
    ],
    PG_COMMAND_TOOLS=BASE_DIR.child('configuration.json')
)

django.setup()

execute_from_command_line(sys.argv)
