import os
import sys
import django_pg_commands

from setuptools import setup, find_packages


if sys.argv[-1] == 'publish':
    # if os.system("pip freeze | grep wheel"):
    #     print("wheel not installed.\nUse `pip install wheel`.\nExiting.")
    #     sys.exit()
    if os.system("pip freeze | grep twine"):
        print("twine not installed.\nUse `pip install twine`.\nExiting.")
        sys.exit()
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (django_pg_commands.__version__, django_pg_commands.__version__))
    print("  git push --tags")
    sys.exit()

setup(
    name='django_pg_commands',
    version=django_pg_commands.__version__,
    description="Collections of command for postgreSQL with django",
    long_description=open('readme.md').read(),
    keywords=['postgreSQL', 'django'],
    author='Franz Emil Eulate Chacolla',
    author_email='franzemil35@gmail.com',
    url='http://github.com/franzemil/django_pg_commands',
    license='MIT',
    packages=find_packages(exclude=['docs']),
    install_requires=[
        'inquirer',
        'psycopg2'
    ],
    include_package_data=True,
    zip_safe=False,
)
