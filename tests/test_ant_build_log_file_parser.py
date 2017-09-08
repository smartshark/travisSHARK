import unittest
import os

from travisshark.parsers.java_parser.ant_build_log_file_parser import AntBuildLogFileParser


class MavenBuildLogFileParserTest(unittest.TestCase):
    def _get_log(self, filename):
        with open(os.path.join(os.path.dirname(__file__), 'data', filename), 'r', encoding='utf8') as file:
            log = file.readlines()

            # We need to make some adaptions so that the file matches the return value from the api
            new_lines = []
            for line in log:
                new_lines.append(line.strip("\n")+"\r")
        return '\n'.join(new_lines)

    def test_failed_tests_more_than_one(self):
        parser = AntBuildLogFileParser(self._get_log('ant_failed_tests_junit_2.txt'), 'DEBUG', False)
        parser.parse()
        self.assertEqual(parser.tests_failed, {'com.google.inject.internal.WeakKeySetTest.testEviction_keyOverlap_2x',
                                               'com.google.inject.internal.WeakKeySetTest.testWeakKeySet_integration',
                                               'com.google.inject.internal.WeakKeySetTest.testWeakKeySet_integration_multipleChildren'})

    def test_test_framework_junit(self):
        parser = AntBuildLogFileParser(self._get_log('ant_failed_tests_junit.txt'), 'DEBUG', False)
        parser.parse()
        self.assertEqual(parser.test_framework, 'junit')
        self.assertEqual(parser.tests_run_completely, True)
        
    
    def test_failed_tests(self):
        parser = AntBuildLogFileParser(self._get_log('ant_failed_tests_junit.txt'), 'DEBUG', False)
        parser.parse()
        self.assertEqual(parser.tests_failed, {'com.google.inject.internal.WeakKeySetTest.testEviction'})

if __name__ == '__main__':
    unittest.main()
