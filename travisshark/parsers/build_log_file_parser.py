import logging
import os
import sys


class JobConfigError(Exception):
    pass


class NoFittingParserFoundError(Exception):
    pass


def all_subclasses(cls):
    return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                   for g in all_subclasses(s)]


class BuildLogFileParser(object):
    def __init__(self, log, debug_level):
        self.log = log
        self.logger = logging.getLogger("parser")
        self.debug_level = debug_level
        self.logger.setLevel(debug_level)

    def get_correct_parser(self, job_config):
        BuildLogFileParser._import_parser()
        # Sometimes, people work with two build systems besides each other (e.g., google guice in the beginning)
        # --> we only use the parser for the first reported build system (e.g., if it uses maven and ant,
        # we only use the maven parser)
        if 'language' not in job_config:
            raise JobConfigError("No language specified")

        if job_config['language'] not in ['java', 'python']:
            raise NotImplementedError("Only java and python are implemented at the moment!")

        list_of_parsers = all_subclasses(BuildLogFileParser)
        list_of_parsers.reverse()
        for sc in list_of_parsers:
            parser = sc(self.log, self.debug_level)
            print(parser.__class__.__name__)
            try:
                if parser.detect(job_config):
                    return parser
            except AttributeError:
                pass

        raise NoFittingParserFoundError()

    @staticmethod
    def _import_parser():
        backend_files = [x[:-3] for x in os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                 'java_parser')) if x.endswith(".py")]
        backend_files.extend([x[:-3] for x in os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                      'python_parser')) if x.endswith(".py")])
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), 'java_parser'))
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), 'python_parser'))
        for backend in backend_files:
            __import__(backend)