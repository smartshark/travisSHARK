import logging
import re

from travisshark.parsers.build_log_file_parser import BuildLogFileParser

logger = logging.getLogger("parser")


class PythonBuildLogFileParser(BuildLogFileParser):
    def __init__(self, log, debug_level):
        super().__init__(log, debug_level)
        self.errored_tests = set([])
        self.failed_tests = set([])
        self.test_framework = None
        self.tests_run_completely = False

        self._error_regex = re.compile("errors=(\d*)")
        self._failures_regex = re.compile("failures=(\d*)")

        self._error_pytest_regex = re.compile("(\d*) error")
        self._failures_pytest_regex = re.compile("(\d*) failed")
        self._test_method_name_pytest_regex = re.compile("_*\s(\S*)\s_*")
        self._test_name_pytest_regex = re.compile("(\S*):\d*:\s*")

    def check_if_list_is_in_job_config(self, job_config, keywords):
        KEYS_TO_CHECK = ['env', 'install', 'script', 'after_success', 'before_install']

        for key_to_check in KEYS_TO_CHECK:
            if key_to_check in job_config and job_config[key_to_check] is not None:
                for keyword_to_check in keywords:
                    value_to_check = job_config[key_to_check]

                    if isinstance(value_to_check, list):
                        value_to_check = ' '.join(job_config[key_to_check])

                    if keyword_to_check in value_to_check:
                        return True

        return False

    def detect(self, job_config):
        if self.check_if_list_is_in_job_config(job_config, ['python', 'pytest', 'nose', 'nosetests', 'py.test']) or \
                job_config['language'] == "python":
            self.logger.debug("Found Python build...")
            return True
        return False

    def _get_fqn_of_test(self, line):
        line_parts = line.split("(")
        return line_parts[1].strip(")")+"."+line_parts[0]

    def _get_num_tests_based_on_regex(self, line, regex):
        matches = re.search(regex, line)
        if matches is not None:
            return int(matches.group(1))
        return 0

    def parse(self):
        summary_started = False
        next_line_must_be_parsed = False
        _parsed_num_errored_tests = 0
        _parsed_num_failed_tests = 0

        # We need this and cannot use the len of self.failed_tests etc, as it can happen that the same error is thrown
        # two times, which counts as two distinct errors in the summary of pytest
        found_num_errored_tests = 0
        found_num_failed_tests = 0

        pytest_section = None
        method_name_of_test = None

        log_lines = self.log.split("\n")
        for index, line in enumerate(log_lines):
            if "======================================================================" in line:
                next_line_must_be_parsed = True
            elif next_line_must_be_parsed:
                if line.startswith("ERROR:"):
                    found_num_errored_tests += 1
                    self.errored_tests.add(self._get_fqn_of_test(''.join(line.strip().split(" ")[1:3])))
                elif line.startswith("FAIL:"):
                    found_num_failed_tests += 1
                    self.failed_tests.add(self._get_fqn_of_test(''.join(line.strip().split(" ")[1:3])))
                next_line_must_be_parsed = False
            elif "----------------------------------------------------------------------" in line:
                summary_started = True
            elif summary_started and "FAILED (" in line:
                _parsed_num_errored_tests += self._get_num_tests_based_on_regex(line, self._error_regex)
                _parsed_num_failed_tests += self._get_num_tests_based_on_regex(line, self._failures_regex)
            elif summary_started and "Ran" in line and "tests in" in line:
                # Unittest summary
                self.test_framework = "unittest"
                self.tests_run_completely = True

            # From here on, everything is connected to pytest
            elif "=================" in line and "seconds" in line:
                self.test_framework = "pytest"
                self.tests_run_completely = True

                _parsed_num_errored_tests += self._get_num_tests_based_on_regex(line, self._error_pytest_regex)
                _parsed_num_failed_tests += self._get_num_tests_based_on_regex(line, self._failures_pytest_regex)
            elif line == "==================================== ERRORS ====================================\r":
                pytest_section = "error"
            elif line == "=================================== FAILURES ===================================\r":
                pytest_section = "failure"
            elif (line.startswith("_") or line.startswith("\x1b[1m\x1b[31m_") or line.startswith("\x1b[31m\x1b[1m_"))\
                    and ("ERROR" in line or "[doctest]" in line):
                failed_or_errored_test = line.split(" ")[-2]
                if pytest_section == "error":
                    found_num_errored_tests += 1
                    self.errored_tests.add(failed_or_errored_test)
                elif pytest_section == "failure":
                    found_num_failed_tests += 1
                    self.failed_tests.add(failed_or_errored_test)
                else:
                    raise Exception("No pytest section found!")
            # Sometimes the build logs have some grunch before "___" stuff, so we need to check for that too
            elif (line.startswith("_") or line.startswith("\x1b[1m\x1b[31m_") or line.startswith("\x1b[31m\x1b[1m_")) and \
                    (line.endswith("_\r") or line.endswith("_\x1b[0m\r")) and method_name_of_test is None:
                matches = re.search(self._test_method_name_pytest_regex, line)
                if matches is not None and matches.group(1) is not '_':
                    method_name_of_test = matches.group(1)
            elif method_name_of_test is not None:
                matches = re.search(self._test_name_pytest_regex, line)
                if matches is not None:
                    test_name = matches.group(1).replace('/', '.').replace('.py', '')+"."+method_name_of_test
                    if pytest_section == "error":
                        found_num_errored_tests += 1
                        self.errored_tests.add(test_name)
                    elif pytest_section == "failure":
                        found_num_failed_tests += 1
                        self.failed_tests.add(test_name)
                    else:
                        raise Exception("No pytest section found!")
                    method_name_of_test = None

        # Sanity Checks
        if found_num_errored_tests != _parsed_num_errored_tests:
            raise Exception("Not all errored tests were found!")

        if found_num_failed_tests != _parsed_num_failed_tests:
            raise Exception("Not all failed tests were found!")

        return list(self.failed_tests), list(self.errored_tests), self.test_framework, self.tests_run_completely
