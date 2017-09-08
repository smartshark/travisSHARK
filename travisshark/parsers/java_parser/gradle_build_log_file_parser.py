from travisshark.parsers.java_parser.java_build_log_file_parser import JavaBuildLogFileParser


class GradleBuildLogFileParser(JavaBuildLogFileParser):
    def __init__(self, log, debug_level, ignore_errors):
        super().__init__(log, debug_level, ignore_errors)

    def parse(self):
        pass

    def detect(self, job_config):
        if self.check_if_list_is_in_job_config(job_config, ['gradle', 'gradlew']):
            self.logger.debug("Found Gradle build file...")
            return True
        return False

    def _extract_tests(self):
        pass