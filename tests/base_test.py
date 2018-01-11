import unittest

import os


class JobMock(object):
    def __init__(self):
        self.metrics = {}


class BaseTest(unittest.TestCase):
    path_to_data_folder = os.path.join(os.path.dirname(__file__), 'data')

    def get_log(self, filename):
        with open(os.path.join(self.path_to_data_folder, filename), 'r', encoding='utf8') as file:
            log = file.readlines()

            # We need to make some adaptions so that the file matches the return value from the api
            new_lines = []
            for line in log:
                new_lines.append(line.strip("\n")+"\r")
        return '\n'.join(new_lines)

    def get_all_log_names(self):
        return [f for f in os.listdir(self.path_to_data_folder)
                if os.path.isfile(os.path.join(self.path_to_data_folder, f))]

