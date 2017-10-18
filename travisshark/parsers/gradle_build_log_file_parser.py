from travisshark.parsers.build_log_file_parser import BuildLogFileParser


class GradleBuildLogFileParser(BuildLogFileParser):
    def __init__(self, log, debug_level, ignore_errors):
        super().__init__(log, debug_level, ignore_errors)

    def parse(self, job):
        pass

    def detect(self, job_config):
        if 'language' in job_config and job_config['language'].lower() != "java":
            return False

        if self.check_if_list_is_in_job_config(job_config, ['gradle', 'gradlew']):
            self.logger.debug("Found Gradle build file...")
            return True
        return False

    def _extract_tests(self):
        pass