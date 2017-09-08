from travisshark.parsers.java_parser.java_build_log_file_parser import JavaBuildLogFileParser

class AntBuildLogFileParser(JavaBuildLogFileParser):
    def __init__(self, log, debug_level, ignore_errors):
        super().__init__(log, debug_level, ignore_errors)
        self.reactor_lines = []
        self._test_lines = []
        self._errored_tests_lines = []
        self._failed_tests_lines = []
        self.tests_failed = set([])
        self.tests_errored = set([])
        self.test_framework = None
        self.tests_run_completely = False

    def parse(self):
        self._extract_tests()
        self._analyze_tests()
        return list(self.tests_failed), list(self.tests_errored), self.test_framework, self.tests_run_completely

    def _get_fqn_from_line(self, line):
        line_parts = line.strip().split('(')
        method_name = line_parts[0]
        fqn = line_parts[1].split(')')[0] + "." + method_name
        return fqn

    def _analyze_tests(self):
        # If not, we need to parse through the file, till we get to the "Failed tests" / "Tests in error" part
        failed_tests_started = False

        for line in self._test_lines:
            # Example line:     [junit] 1) testEviction(com.google.inject.internal.WeakKeySetTest)junit.framework.AssertionFailedError
            if failed_tests_started:
                new_line = line.replace('[junit]', '')
                new_line = new_line.strip()

                if new_line and new_line[0].isdigit():
                    test_part = new_line.split(')')[1].strip()+")"
                    self.tests_failed.add(self._get_fqn_from_line(test_part))

            if 'Tests run:' in line and 'Failures:' in line and 'Errors:' in line:
                self.test_framework = 'junit'
                self.tests_run_completely = True
            elif 'Total tests run:' in line and 'Failures:' in line and 'Skips:' in line:
                self.test_framework = 'testng'
                self.tests_run_completely = True
            elif ('There was' in line or 'There were' in line) and 'failure' in line:
                failed_tests_started = True

    def _extract_tests(self):
        for line in self.log.split("\n"):
            if '[junit]' in line or '[testng]' in line or '[test' in line:
                self._test_lines.append(line)

    def detect(self, job_config):
        if self.check_if_list_is_in_job_config(job_config, ['ant']):
            self.logger.debug("Found Ant build file...")
            return True
        return False