import unittest

from tests.base_test import BaseTest, JobMock
from travisshark.parsers.ant_build_log_file_parser import AntBuildLogFileParser


class MavenBuildLogFileParserTest(BaseTest):
    def setUp(self):
        self.job = JobMock()

    def test_detect(self):
        for log_name in self.get_all_log_names():
            parser = AntBuildLogFileParser(self.get_log(log_name), 'DEBUG', False, self.job)

            if log_name.startswith('ant'):
                self.assertTrue(parser.detect(), 'Log %s should not be an ant log file!' % log_name)
            else:
                self.assertFalse(parser.detect(), 'Log %s should be an ant log file!' % log_name)

    def test_failed_tests_more_than_one(self):
        parser = AntBuildLogFileParser(self.get_log('ant_failed_tests_junit_2.txt'), 'DEBUG', False, self.job)
        parser.parse()
        self.assertEqual(self.job.metrics['failed_tests'],
                         {
                             'com.google.inject.internal.WeakKeySetTest.testEviction_keyOverlap_2x',
                             'com.google.inject.internal.WeakKeySetTest.testWeakKeySet_integration',
                             'com.google.inject.internal.WeakKeySetTest.testWeakKeySet_integration_multipleChildren'
                         })

    def test_test_framework_junit(self):
        parser = AntBuildLogFileParser(self.get_log('ant_failed_tests_junit.txt'), 'DEBUG', False, self.job)
        parser.parse()
        self.assertEqual(self.job.metrics['test_framework'], 'junit')
        self.assertEqual(self.job.metrics['tests_run'], True)

    def test_failed_tests(self):
        parser = AntBuildLogFileParser(self.get_log('ant_failed_tests_junit.txt'), 'DEBUG', False, self.job)
        parser.parse()
        self.assertEqual(self.job.metrics['failed_tests'], {'com.google.inject.internal.WeakKeySetTest.testEviction'})

if __name__ == '__main__':
    unittest.main()
