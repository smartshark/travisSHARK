import logging
import os
import sys


class JobConfigError(Exception):
    pass

class NoFittingParserFoundError(Exception):
    pass

def all_subclasses(cls):
    return cls.__subclasses__() + [g for s in cls.__subclasses__() for g in all_subclasses(s)]


class BuildLogFileParser(object):
    def __init__(self, log, debug_level, ignore_errors):
        self.log = log
        self.logger = logging.getLogger("parser")
        self.debug_level = debug_level
        self.logger.setLevel(debug_level)
        self.ignore_errors = ignore_errors

    def get_correct_parsers(self, job_config):
        BuildLogFileParser._import_parser()

        list_of_parsers = all_subclasses(BuildLogFileParser)
        fitting_parsers = []
        for sc in list_of_parsers:
            parser = sc(self.log, self.debug_level, self.ignore_errors)
            try:
                if parser.detect(job_config):
                    fitting_parsers.append(parser)
            except AttributeError:
                pass
            except NotImplementedError:
                pass

        return fitting_parsers

    def detect(self, job_config):
        raise NotImplementedError()

    def parse(self, job):
        raise NotImplementedError()

    def check_if_list_is_in_job_config(self, job_config, keywords):
        KEYS_TO_CHECK = ['env', 'install', 'script', 'after_success', 'before_install', 'cache', 'global_env']

        for key_to_check in KEYS_TO_CHECK:
            if key_to_check in job_config and job_config[key_to_check] is not None:
                for keyword_to_check in keywords:
                    value_to_check = job_config[key_to_check]

                    if isinstance(value_to_check, list):
                        value_to_check = ' '.join(job_config[key_to_check])

                    if keyword_to_check.lower() in value_to_check.lower():
                        return True

        return False

    @staticmethod
    def _import_parser():
        backend_files = [x[:-3] for x in os.listdir(os.path.dirname(os.path.realpath(__file__)))
                         if x.endswith(".py")]
        sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
        for backend in backend_files:
            __import__(backend)