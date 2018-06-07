import os

from django.core.management import call_command
from django.test import TestCase


class DataImporterTestCase(TestCase):
    def test_command_launch(self):
        test_file = os.path.join(os.path.dirname(__file__), 'test.csv')
        call_command('import_csv_features',
                     '--csv-type=insee',
                     f'--source={test_file}')