import unittest
import os

from travisshark.parsers.python_parser.python_build_log_file_parser import PythonBuildLogFileParser


class PythonBuildLogFileParserTest(unittest.TestCase):
    def _get_log(self, filename):
        with open(os.path.join(os.path.dirname(__file__), 'data', filename), 'r', encoding="utf-8") as file:
            log = file.readlines()

            # We need to make some adaptions so that the file matches the return value from the api
            new_lines = []
            for line in log:
                new_lines.append(line.strip("\n") + "\r")
        return '\n'.join(new_lines)

    def test_errored_test_pytest_2(self):
        parser = PythonBuildLogFileParser(self._get_log('python_errored_tests_unittest_2.txt'), 'DEBUG')
        parser.parse()
        self.assertSetEqual(parser.failed_tests, set([]))
        self.assertSetEqual(parser.errored_tests, {'test_unix.Test_UV_Unix.test_transport_unclosed_warning',
                                                   'test_unix.Test_UV_Unix.test_transport_fromsock_get_extra_info',
                                                   'test_unix.Test_UV_Unix.test_create_unix_connection_5',
                                                   'test_unix.Test_UV_Unix.test_create_unix_connection_4',
                                                   'test_unix.Test_UV_Unix.test_create_unix_connection_1',
                                                   })
        self.assertTrue(parser.tests_run_completely)
        self.assertEqual(parser.test_framework, "unittest")

    def test_failed_tests_1(self):
        parser = PythonBuildLogFileParser(self._get_log('python_failed_tests_unittest.txt'), 'DEBUG')
        parser.parse()
        self.assertSetEqual(parser.errored_tests, set([]))
        self.assertSetEqual(parser.failed_tests,
                            {'test_legacy_api.TestLegacyBulkNoResults.test_no_results_unordered_failure'})
        self.assertTrue(parser.tests_run_completely)
        self.assertEqual(parser.test_framework, "unittest")

    def test_errored_tests_1(self):
        parser = PythonBuildLogFileParser(self._get_log('python_errored_tests_unittest.txt'), 'DEBUG')
        parser.parse()
        self.assertEqual(len(parser.errored_tests), 358)
        self.assertSetEqual(parser.failed_tests, set([]))
        self.assertTrue(parser.tests_run_completely)
        self.assertEqual(parser.test_framework, "unittest")

    def test_errored_test_pytest_1(self):
        parser = PythonBuildLogFileParser(self._get_log('python_errored_tests_pytest.txt'), 'DEBUG')
        parser.parse()
        self.assertSetEqual(parser.failed_tests, set([]))
        self.assertSetEqual(parser.errored_tests, {'tests/test_formatutils.py', 'tests/test_formatutils.py'})
        self.assertTrue(parser.tests_run_completely)
        self.assertEqual(parser.test_framework, "pytest")

    def test_failed_and_errored_test_pytest_1(self):
        parser = PythonBuildLogFileParser(self._get_log('python_failed_and_errored_tests_pyttest.txt'), 'DEBUG')
        parser.parse()
        self.assertSetEqual(parser.failed_tests, {'boltons.gcutils.get_all', 'boltons.statsutils.rel_std_dev',
                                                  'boltons.timeutils.decimal_relative_time'})
        self.assertSetEqual(parser.errored_tests, {'boltons/namedutils.py'})
        self.assertTrue(parser.tests_run_completely)
        self.assertEqual(parser.test_framework, "pytest")

    def test_failed_test_pytest_2(self):
        parser = PythonBuildLogFileParser(self._get_log('python_failed_tests_pytest_new_output.txt'), 'DEBUG')
        parser.parse()
        self.assertSetEqual(parser.failed_tests, {'tests.tbutils_test.test_eval_tb', 'tests.tbutils_test.test_normal_tb'})
        self.assertSetEqual(parser.errored_tests, set([]))
        self.assertTrue(parser.tests_run_completely)
        self.assertEqual(parser.test_framework, "pytest")

    
    def test_failed_test_pytest(self):
        parser = PythonBuildLogFileParser(self._get_log('python_failed_tests_pytest.txt'), 'DEBUG')
        parser.parse()
        self.assertSetEqual(parser.failed_tests, {'tests.test_strutils.test_is_uuid'})
        self.assertSetEqual(parser.errored_tests, set([]))
        self.assertTrue(parser.tests_run_completely)
        self.assertEqual(parser.test_framework, "pytest")


if __name__ == '__main__':
    unittest.main()
