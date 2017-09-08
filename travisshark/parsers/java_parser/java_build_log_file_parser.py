import logging

from travisshark.parsers.build_log_file_parser import BuildLogFileParser

logger = logging.getLogger("parser")


class JavaBuildLogFileParser(BuildLogFileParser):
    def __init__(self, log, debug_level, ignore_errors):
        super().__init__(log, debug_level, ignore_errors)

    def check_if_list_is_in_job_config(self, job_config, keywords):
        KEYS_TO_CHECK = ['env', 'install', 'script', 'after_success', 'before_install']

        for key_to_check in KEYS_TO_CHECK:
            # It can happen that the value of "install" is just True, which would break our check here
            if key_to_check in job_config and job_config[key_to_check] is not None \
                    and not isinstance(job_config[key_to_check], bool):

                for keyword_to_check in keywords:
                    value_to_check = job_config[key_to_check]

                    if isinstance(value_to_check, list):
                        value_to_check = ' '.join(job_config[key_to_check])

                    if keyword_to_check.lower() in value_to_check.lower():
                        return True
        return False
