# coding=utf-8
import difflib

import inquirer

from django.core.management import BaseCommand, CommandError
from django.db import connections
from django_pg_commands.utils import get_connections, execute_command, execute_query


class Command(BaseCommand):
    """
    Sync the functions beetween two databases
    """

    help = 'It\'s responsive to sync the function beeten to databases'
    schema = 'public'
    to_conn = None
    from_conn = None

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            dest='schema',
            nargs=1,
            required=True,
            help='Schema\'s name'
        )

    def handle(self, *args, **options):
        schema = options.get('schema', None)

        if schema:
            self.schema = schema[0]

        [self.from_conn, self.to_conn] = get_connections()

        self.stdout.write("connection created ...")

        [to_funcs, from_funcs] = [self.get_functions(self.to_conn), self.get_functions(self.from_conn)]
        function_to_migrate = []

        for _ in from_funcs:
            n_fun = self.compare_functions(_, to_funcs)
            if n_fun is not None:
                if n_fun['definition'] != _['definition']:
                    sm = self.inline_diff(n_fun['definition'], _['definition'])
                    _['type'] = '[MODIFICADO] ' + _['name'] + self.print_args(_['arg_names']) + ')'
                    function_to_migrate.append(_)
            else:
                _['type'] = '[NUEVO] ' + _['name'] + '(' + self.print_args(_['arg_names']) + ')'
                function_to_migrate.append(_)

        if len(function_to_migrate) == 0:
            self.stdout.write("No se presentan Cambios")
            return

        questions = [
            inquirer.Checkbox(
                'functions',
                message="Que funcion desea motificar",
                choices=[x['type'] for x in function_to_migrate],
            ),
        ]

        answers = inquirer.prompt(questions)['functions']

        functions_to_migrate = list(filter(lambda x: x['type'] in answers, function_to_migrate))

        for item in functions_to_migrate:
            self.update_function(item, self.to_conn)


    def get_functions(self, conn):
        """
        Returns all function from a connection and scheme
        """
        query = """
          SELECT n.nspname AS schema, proname AS name, proargnames AS arg_names,
          t.typname AS return_type, d.description, pg_get_functiondef(p.oid) as definition
          FROM pg_proc p
          INNER JOIN pg_type t on p.prorettype = t.oid
          LEFT JOIN pg_description d on p.oid = d.objoid
          INNER JOIN pg_namespace n on n.oid = p.pronamespace
          WHERE n.nspname = '%s'
        """ % self.schema
        return execute_query(conn, query)

    def compare_functions(self, function, list_functions):
        """
        Verify if a function was changed
        """
        args = function['arg_names'] if function['arg_names'] else []

        existe = list(filter(lambda x: function['name'] == x['name'] and len(
            x['arg_names'] if x['arg_names'] is not None else []) == len(args), list_functions))

        if len(existe) == 0:
            return None
        return existe[0]

    def print_args(self, args):
        """
        Print the function's arguments
        """
        if args is None:
            return ''
        str_args = ','.join(args)
        if len(str_args) > 60:
            return str_args[:60] + '...'
        return str_args

    def inline_diff(self, a, b):
        """
        Return de diferences between two text
        """
        matcher = difflib.SequenceMatcher(None, a, b)

        def process_tag(tag, i1, i2, j1, j2):
            if tag == 'replace':
                return '{' + matcher.a[i1:i2] + ' -> ' + matcher.b[j1:j2] + '}'
            if tag == 'delete':
                return '{- ' + matcher.a[i1:i2] + '}'
            if tag == 'equal':
                return matcher.a[i1:i2]
            if tag == 'insert':
                return '{+ ' + matcher.b[j1:j2] + '}'

        return ''.join(process_tag(*t) for t in matcher.get_opcodes())

    def update_function(self, function, conn):
        """
        Update a function 
        """
        self.stdout.write('*' * 50)
        self.stdout.write('Syncying functions: %s' % function['name'])
        if execute_command(conn, function['definition']):
            self.stdout.write('The function: %s, was synced' % function['name'])
        else:
            self.stdout.write('There\'s a problem with function: %s' % function['name'])
        self.stdout.write('*' * 50)