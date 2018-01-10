import json

from django.test import TestCase

from .utils import read_file


class UtilsTest(TestCase):
    def setUp(self):
        self.data = json.loads(open('configuration.json').read())

    def test_read_file(self):
        self.assertDictEqual(self.data, read_file())
