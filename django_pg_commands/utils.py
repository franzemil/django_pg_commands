import psycopg2
import json

from django.conf import settings
from django.core.management import CommandError


CONFIGURATION_FILE = getattr(settings, 'PG_COMMAND_TOOLS', None)

def read_file():
    """
    this method reads the file than describe the server credencials
    """
    if CONFIGURATION_FILE is None:
        raise CommandError('You need specified PG_COMMAND_TOOLS constant in your settings file.')
    try:
        data = json.load(open(CONFIGURATION_FILE))
    except FileNotFoundError:
        raise CommandError('The file %s doesn\'t exists' % CONFIGURATION_FILE)
    except ValueError:
        raise CommandError('The file isn\'t a valid format')
    return data

def get_connection_from_dict(info):
    """
    this method make the connection
    """
    try:
        conn = psycopg2.connect(
            host=info['host'],
            user=info['user'],
            password=info['password'],
            database=info['dbname']
        )
    except psycopg2.Error:
        raise CommandError('The database credencials are not valid')
    return conn

def get_connections():
    """
    Returns the connections for both databases
    """
    data = read_file()
    to_file = data['to']
    from_file = data['from']

    to_conn = get_connection_from_dict(to_file)
    from_conn = get_connection_from_dict(from_file)
    return [from_conn, to_conn]


def execute_command(conn, command):
    """
    Execute a query and write and the database
    """
    cursor = conn.cursor()
    try:
        cursor.execute(command)
        conn.commit()
        return True
    except psycopg2.DatabaseError:
        conn.rollback()
        return False

def execute_query(conn, query):
    """
    Execute a query and return the data
    """
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    return results
