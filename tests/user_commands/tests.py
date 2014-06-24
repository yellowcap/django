import os
import sys

from django.core import management
from django.core.management import CommandError
from django.core.management.utils import find_command, popen_wrapper
from django.test import SimpleTestCase
from django.utils import translation
from django.utils.six import StringIO


class CommandTests(SimpleTestCase):
    def test_command(self):
        out = StringIO()
        management.call_command('dance', stdout=out)
        self.assertEqual(out.getvalue(),
            "I don't feel like dancing Rock'n'Roll.\n")

    def test_command_style(self):
        out = StringIO()
        management.call_command('dance', style='Jive', stdout=out)
        self.assertEqual(out.getvalue(),
            "I don't feel like dancing Jive.\n")

    def test_language_preserved(self):
        out = StringIO()
        with translation.override('fr'):
            management.call_command('dance', stdout=out)
            self.assertEqual(translation.get_language(), 'fr')

    def test_explode(self):
        """ Test that an unknown command raises CommandError """
        self.assertRaises(CommandError, management.call_command, ('explode',))

    def test_system_exit(self):
        """ Exception raised in a command should raise CommandError with
            call_command, but SystemExit when run from command line
        """
        with self.assertRaises(CommandError):
            management.call_command('dance', example="raise")
        old_stderr = sys.stderr
        sys.stderr = err = StringIO()
        try:
            with self.assertRaises(SystemExit):
                management.ManagementUtility(['manage.py', 'dance', '--example=raise']).execute()
        finally:
            sys.stderr = old_stderr
        self.assertIn("CommandError", err.getvalue())

    def test_find_command_without_PATH(self):
        """
        find_command should still work when the PATH environment variable
        doesn't exist (#22256).
        """
        current_path = os.environ.pop('PATH', None)

        try:
            self.assertIsNone(find_command('_missing_'))
        finally:
            if current_path is not None:
                os.environ['PATH'] = current_path

    def test_optparse_compatibility(self):
        """
        optparse should be supported during Django 1.8/1.9 releases.
        """
        out = StringIO()
        management.call_command('optparse_cmd', stdout=out)
        self.assertEqual(out.getvalue(), "All right, let's dance Rock'n'Roll.\n")

        # Simulate command line execution
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = StringIO(), StringIO()
        try:
            management.execute_from_command_line(['django-admin', 'optparse_cmd'])
        finally:
            output = sys.stdout.getvalue()
            sys.stdout, sys.stderr = old_stdout, old_stderr
        self.assertEqual(output, "All right, let's dance Rock'n'Roll.\n")


class UtilsTests(SimpleTestCase):

    def test_no_existent_external_program(self):
        self.assertRaises(CommandError, popen_wrapper, ['a_42_command_that_doesnt_exist_42'])
