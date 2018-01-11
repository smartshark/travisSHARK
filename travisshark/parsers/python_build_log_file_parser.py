import logging
import re

from travisshark.parsers.build_log_file_parser import BuildLogFileParser

logger = logging.getLogger("parser")


class PythonBuildLogFileParser(BuildLogFileParser):
    def __init__(self, log, debug_level, ignore_errors, job):
        super().__init__(log, debug_level, ignore_errors, job)
        self.errored_tests = set([])
        self.failed_tests = set([])
        self.test_framework = None
        self.tests_run_completely = False

        self._error_regex = re.compile("errors=(\d*)")
        self._failures_regex = re.compile("failures=(\d*)")

        self._error_pytest_regex = re.compile("(\d*) error")
        self._failures_pytest_regex = re.compile("(\d*) failed")
        self._test_method_name_pytest_regex = re.compile("_*\s(\S*)\s_*")
        self._test_method_name_pytest_special_regex = re.compile("_*\s(\S*)\s*_*")
        self._test_name_pytest_regex = re.compile("(\S*):\d*:\s*")
        self._test_name_pytest_args_regex = re.compile("<(\S*)\stestMethod=(\S*)>")

        self._test_name_errored_test_unittest_regex = re.compile("(\w*)\s\((\S*)\)\s\.{3}\sERROR")
        self._test_name_failed_test_unittest_regex = re.compile("(\w*)\s\((\S*)\)\s\.{3}\sFAILED")

        self._parse_failures_coverage_regex = re.compile("(\d*)\sFAILED.*")
        self._parse_errors_coverage_regex = re.compile("(\d*)\serror[^=]*")

        self._test_name_failed_test_unittest = re.compile("\S*\s*FAIL:\s(\S*)\s\((\S*)\)")
        self._test_name_failed_test2_unittest = re.compile("\S*\s*FAIL:\s(\S*)")
        self._test_name_failed_doctest_unittest = re.compile("\S*\s*FAIL: Doctest:\s(\S*)")

        self._test_name_errored_test_unittest = re.compile("\S*\s*ERROR:\s(\S*)\s\((\S*)\)")
        self._test_name_errored_test2_unittest = re.compile("\S*\s*ERROR:\s(\S*)")

        self._pytest_sugar_failed_tests = re.compile("\s*(\d*) failed")
        self._pytest_sugar_errored_tests = re.compile("\s*(\d*) error\S*")
        self._pytest_sugar_test_name = re.compile("\s*- (\S*):\d*\s(\S*)")

    def detect(self):
        if any(identifier in self.log for identifier in ['python', 'pytest', 'nose', 'nosetests', 'py.test',
                                                         'pip install']):
            self.logger.debug("Found Python build file...")
            return True
        return False

    def _get_num_tests_based_on_regex(self, line, regex):
        matches = re.search(regex, line)
        if matches is not None:
            if matches.group(1).strip():
                return int(matches.group(1))
        return 0

    def parse(self):
        summary_started = False
        next_lines_must_be_parsed = False
        _parsed_num_errored_tests = 0
        _parsed_num_failed_tests = 0

        # We need this and cannot use the len of self.failed_tests etc, as it can happen that the same error is thrown
        # two times, which counts as two distinct errors in the summary of pytest
        found_num_errored_tests = 0
        found_num_failed_tests = 0

        pytest_section = None
        method_name_of_test = None

        sugar_summary_started = False
        started_pytest_sugar_failed_section = False
        started_pytest_sugar_errored_section = False

        find_failed_trial_test = False
        find_errored_trial_test = False

        log_lines = self.log.split("\n")
        #log_lines = [line for line in log_lines if line.strip()]
        for index, line in enumerate(log_lines):
            line = line.replace("\x1b[1m", "").replace("\x1b[31m", "").replace("\x1b[0m", "").replace("\x1b[32m", "")\
                .replace("\x1b[33m", "").replace("\x1b[36m", "")
            if "======================================================================" in line:
                next_lines_must_be_parsed = True
            elif next_lines_must_be_parsed and not line.startswith("[FAIL]") and not line.startswith("[ERROR]") and line.strip("\r"):
                next_lines_must_be_parsed = False
                print(line)
                failed_matches = re.search(self._test_name_failed_test_unittest, line)
                failed_matches_2 = re.search(self._test_name_failed_test2_unittest, line)
                failed_doctest_matches = re.search(self._test_name_failed_doctest_unittest, line)
                errored_matches = re.search(self._test_name_errored_test_unittest, line)
                errored_matches_2 = re.search(self._test_name_errored_test2_unittest, line)

                if failed_matches is not None and len(failed_matches.groups()) == 2:
                    found_num_failed_tests += 1
                    self.failed_tests.add(failed_matches.group(2)+"."+failed_matches.group(1))
                elif failed_matches_2 is not None and "Doctest:" not in line:
                    found_num_failed_tests += 1
                    if not line.startswith("FAIL: Tests") and not line.startswith("FAIL: Verify"):
                        self.failed_tests.add(failed_matches_2.group(1))
                elif failed_doctest_matches is not None:
                    found_num_failed_tests += 1
                    self.failed_tests.add(failed_doctest_matches.group(1))
                elif errored_matches is not None:
                    found_num_errored_tests += 1
                    self.errored_tests.add(errored_matches.group(2)+"."+errored_matches.group(1))
                # It can happen that a line looks like this ERROR: test_cuts.test_node_cutset_random_graphs
                elif errored_matches_2 is not None:
                    # But also like this ERROR: Failure: AttributeError ('dict' object has no attribute 'iteritems')
                    found_num_errored_tests += 1
                    if ":" not in errored_matches_2.group(1) and "." in errored_matches_2.group(1):
                        self.errored_tests.add(errored_matches_2.group(1))
            elif "----------------------------------------------------------------------" in line:
                summary_started = True
            elif summary_started and ("FAILED (" in line or "tests passed)" in line):
                _parsed_num_errored_tests += self._get_num_tests_based_on_regex(line, self._error_regex)
                _parsed_num_failed_tests += self._get_num_tests_based_on_regex(line, self._failures_regex)

                _parsed_num_failed_tests += self._get_num_tests_based_on_regex(line, self._parse_failures_coverage_regex)
                _parsed_num_errored_tests += self._get_num_tests_based_on_regex(line, self._parse_errors_coverage_regex)
            elif summary_started and (("Ran" in line and "tests in" in line) or
                                          ("tests run in" in line and "seconds" in line)):
                # Unittest summary
                self.test_framework = "unittest"
                self.tests_run_completely = True

            elif line == "[FAIL]\r":
                find_failed_trial_test = True
            elif line == "[ERROR]\r":
                find_errored_trial_test = True
            elif line.startswith("[ERROR]: ") and \
                            log_lines[index-1] == "===============================================================================\r":
                found_num_errored_tests += 1
                self.errored_tests.add(line.split(" ")[-1].strip("\r"))
            elif line.startswith("[FAIL]: ") and \
                            log_lines[index-1] == "===============================================================================\r":
                found_num_failed_tests += 1
                self.failed_tests.add(line.split(" ")[-1].strip("\r"))
            elif find_errored_trial_test and \
                    (log_lines[index+1] == "===============================================================================\r" or
                    log_lines[index+1] == '-------------------------------------------------------------------------------\r'):
                find_errored_trial_test = False

                i = index
                while log_lines[i].strip("\r"):
                    found_num_errored_tests += 1
                    self.errored_tests.add(line.strip("\r"))
                    i -=1
            elif find_failed_trial_test and \
                    (log_lines[index+1] == "===============================================================================\r" or
                    log_lines[index+1] == '-------------------------------------------------------------------------------\r'):
                find_failed_trial_test = False

                i = index
                while log_lines[i].strip("\r"):
                    found_num_failed_tests += 1
                    self.failed_tests.add(line.strip("\r"))
                    i -= 1

            # From here on, everything is connected to pytest
            elif "=" in line and "seconds" in line:
                self.test_framework = "pytest"
                self.tests_run_completely = True

                _parsed_num_errored_tests += self._get_num_tests_based_on_regex(line, self._error_pytest_regex)
                _parsed_num_failed_tests += self._get_num_tests_based_on_regex(line, self._failures_pytest_regex)
            elif line == "==================================== ERRORS ====================================\r" or \
                    (line.startswith("=") and "ERRORS" in line and line.endswith("=\r")):
                pytest_section = "error"
                summary_started = True
            elif line == "=================================== FAILURES ===================================\r" or \
                    (line.startswith("=") and "FAILURES" in line and line.endswith("=\r")):
                pytest_section = "failure"
                summary_started = True
            # Here we execlude errors at setups, as this is not of intereset for us
            elif "ERROR at setup" in line:
                found_num_errored_tests += 1
            elif (line.startswith("_") or "ERROR collecting " in line) and ("ERROR" in line or "[doctest]" in line) \
                    and summary_started:
                # If the line does not contain "_", we need to split differently
                # E.g.:  ERROR collecting tests/unit/py2/nupic/frameworks/opf/clamodel_classifier_helper_test.py
                # versus: ____ ERROR collecting tests/integration/py2/nupic/swarming/swarming_test.py ____
                if line.endswith("_\r"):
                    failed_or_errored_test = line.split(" ")[-2]
                else:
                    failed_or_errored_test = line.strip().split(" ")[-1].strip("\r")

                if pytest_section == "error":
                    found_num_errored_tests += 1
                    self.errored_tests.add(failed_or_errored_test)
                elif pytest_section == "failure":
                    found_num_failed_tests += 1
                    self.failed_tests.add(failed_or_errored_test)
                else:
                    raise Exception("No pytest section found!")
            # Sometimes the build logs have some grunch before "___" stuff, so we need to check for that too
            elif (line.startswith("_") or (line.startswith(" ") and "test" in line.lower() and not line.startswith("  File"))) \
                    and (line.endswith("_\r") or line.endswith(" \r")) and method_name_of_test is None and summary_started \
                    and " summary " not in line:
                matches = re.search(self._test_method_name_pytest_regex, line)
                if matches is not None and matches.group(1) is not '_':
                    method_name_of_test = matches.group(1)
            # sometimes lines with the pattern like: __________________________ test_args[args3-one two can happen
            elif line.startswith("_") and "[" in line and summary_started and " summary " not in line:
                first_part = line.split("[")[0]
                matches = re.search(self._test_method_name_pytest_special_regex, first_part)
                if matches is not None and matches.group(1) is not '_':
                    method_name_of_test = matches.group(1)
            elif method_name_of_test is not None and ".py" in line:
                matches = re.search(self._test_name_pytest_regex, line)

                if matches is not None:
                    test_name = matches.group(1).replace('/', '.')[0:-3].lstrip('.')+"."+method_name_of_test
                    if pytest_section == "error":
                        found_num_errored_tests += 1
                        self.errored_tests.add(test_name)
                    elif pytest_section == "failure":
                        found_num_failed_tests += 1
                        self.failed_tests.add(test_name)
                    else:
                        raise Exception("No pytest section found!")
                    method_name_of_test = None
            elif re.search(self._test_name_errored_test_unittest_regex, line):
                parts = line.split(" ")
                self.errored_tests.add(parts[1].split(")")[0].strip("(") + "." + parts[0])
            elif re.search(self._test_name_failed_test_unittest_regex, line):
                parts = line.split(" ")
                self.failed_tests.add(parts[1].split(")")[0].strip("(")+"."+parts[0])
            # It can happen that people are using pytest sugar. But, we have the problem then that
            # it completely changes the whole look and feel and therefore the parsing of the log.
            # E.g., we can not tell if a test was erroneous or a failure, therefore we just store it as failure
            elif "Results (" in line:
                sugar_summary_started = True
                self.test_framework = "pytest-sugar"
            elif "Test session starts" in line:
                summary_started = False
                sugar_summary_started = False
                started_pytest_sugar_failed_section = False
                started_pytest_sugar_errored_section = False
            elif sugar_summary_started and started_pytest_sugar_failed_section and line.strip().startswith("-")\
                    and not line.strip().startswith("---"):
                matches = re.search(self._pytest_sugar_test_name, line)
                module = matches.group(1)[0:-3].replace("/", ".")
                found_num_failed_tests += 1
                print(line)
                # If it starts with a dot, we have a full path instead of a correct test
                if not module.startswith("."):
                    self.failed_tests.add(module+"."+matches.group(2))
            elif sugar_summary_started and started_pytest_sugar_errored_section and line.strip().startswith("-")\
                    and not line.strip().startswith("---"):
                matches = re.search(self._pytest_sugar_test_name, line)
                module = matches.group(1)[0:-3].replace("/", ".")
                found_num_errored_tests += 1
                self.errored_tests.add(module+"."+matches.group(2))
            elif sugar_summary_started:
                self.tests_run_completely = True
                matches = re.search(self._pytest_sugar_failed_tests, line)
                if matches is not None and matches.group(1):
                    started_pytest_sugar_failed_section = True
                    _parsed_num_failed_tests += int(matches.group(1))

                matches = re.search(self._pytest_sugar_errored_tests, line)
                if matches is not None and matches.group(1):
                    started_pytest_sugar_errored_section = True
                    _parsed_num_errored_tests += int(matches.group(1))


        # Sanity Checks. Sometimes, a build is so buggy that we could not parse and errored test
        # and also the number of errors is no longer correctly countable
        if self.tests_run_completely and found_num_errored_tests != _parsed_num_errored_tests and \
                        len(self.errored_tests) != 0:
            msg = "Not all errored tests were found! Parsed: %s; Found: %s" % (_parsed_num_errored_tests,
                                                                               found_num_errored_tests)
            if not self.ignore_errors:
                raise Exception(msg)
            else:
                self.logger.error(msg)

        print("FAILED tests: %d, ERRORED tests: %d" % (_parsed_num_failed_tests, _parsed_num_errored_tests))
        if self.tests_run_completely and found_num_failed_tests != _parsed_num_failed_tests:
            msg = "Not all failed tests were found! Parsed: %s; Found: %s" % (_parsed_num_failed_tests,
                                                                              found_num_failed_tests)
            if not self.ignore_errors:
                raise Exception(msg)
            else:
                self.logger.error(msg)

        self.job.metrics['failed_tests'] = self.failed_tests
        self.job.metrics['errored_tests'] = self.errored_tests
        self.job.metrics['test_framework'] = self.test_framework
        self.job.metrics['tests_run'] = self.tests_run_completely
