import logging

from travisshark.parsers.build_log_file_parser import BuildLogFileParser

logger = logging.getLogger("parser")


class JavaBuildLogFileParser(BuildLogFileParser):
    def __init__(self, log, debug_level):
        super().__init__(log, debug_level)

    def check_if_list_is_in_job_config(self, job_config, keywords):
        KEYS_TO_CHECK = ['env', 'install', 'script', 'after_success']

        for key_to_check in KEYS_TO_CHECK:
            if key_to_check in job_config:
                for keyword_to_check in keywords:
                    if keyword_to_check in ' '.join(job_config[key_to_check]):
                        return True

        return False
