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


args = [sys.argv[0], 'test']
# Current module (``tests``) and its submodules.
test_cases = '.'


# # Allow accessing test options from the command line.
offset = 1
try:
    sys.argv[1]
except IndexError:
    pass
else:
    option = sys.argv[1].startswith('-')
    if not option:
        test_cases = sys.argv[1]
        offset = 2


args.append('django_pg_commands.tests')
# # ``verbosity`` can be overwritten from command line.
# args.append('--verbosity=2')
# args.extend(sys.argv[offset:])

execute_from_command_line(args)