from travisshark.parsers.java_parser.java_build_log_file_parser import JavaBuildLogFileParser


class GradleBuildLogFileParser(JavaBuildLogFileParser):
    def __init__(self, log, debug_level):
        super().__init__(log, debug_level)

    def parse(self):
        pass

    def detect(self, job_config):
        if ('env' in job_config and 'gradle' in job_config['env']) \
                or ('install' in job_config and 'gradle' in ' '.join(job_config['install'])) \
                or ('script' in job_config and 'gradle' in ' '.join(job_config['script'])):
            self.logger.debug("Found Gradle build file...")
            return True
        return False

    def _extract_tests(self):
        pass