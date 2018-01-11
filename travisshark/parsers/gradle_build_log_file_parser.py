from travisshark.parsers.build_log_file_parser import BuildLogFileParser


class GradleBuildLogFileParser(BuildLogFileParser):
    def __init__(self, log, debug_level, ignore_errors, job):
        super().__init__(log, debug_level, ignore_errors, job)

    def parse(self):
        pass

    def detect(self):
        if any(identifier in self.log for identifier in ['gralde', 'gradlew']):
            self.logger.debug("Found Gradle build file...")
            return True
        return False

    def _extract_tests(self):
        pass