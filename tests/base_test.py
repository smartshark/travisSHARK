import unittest

import os


class JobMock(object):
    def __init__(self):
        self.failed_tests = set([])
        self.errored_tests = set([])
        self.test_framework = None
        self.tests_run = False

    @property
    def failed_tests(self):
        return self._failed_tests

    @failed_tests.setter
    def failed_tests(self, value):
        self._failed_tests = set(value)

    @property
    def errored_tests(self):
        return self._errored_tests

    @errored_tests.setter
    def errored_tests(self, value):
        self._errored_tests = set(value)

class BaseTest(unittest.TestCase):

    def get_log(self, filename):
        with open(os.path.join(os.path.dirname(__file__), 'data', filename), 'r', encoding='utf8') as file:
            log = file.readlines()

            # We need to make some adaptions so that the file matches the return value from the api
            new_lines = []
            for line in log:
                new_lines.append(line.strip("\n")+"\r")
        return '\n'.join(new_lines)

