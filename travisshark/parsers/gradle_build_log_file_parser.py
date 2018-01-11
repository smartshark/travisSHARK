from travisshark.parsers.build_log_file_parser import BuildLogFileParser


class GradleBuildLogFileParser(BuildLogFileParser):
    def __init__(self, log, debug_level, ignore_errors, job):
        super().__init__(log, debug_level, ignore_errors, job)

    def parse(self):
        pass

    def detect(self):
        if 'language' in self.job.config and \
                (self.job.config['language'].lower() != "java" and self.job.config['language'].lower() != "android"):
            return False

        if self.check_if_list_is_in_job_config(self.job.config, ['gradle', 'gradlew']) or \
                ('language' in self.job.config and self.job.config['language'].lower() == "android"):
            self.logger.debug("Found Gradle build file...")
            return True
        return False

    def _extract_tests(self):
        pass