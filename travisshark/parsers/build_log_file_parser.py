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
    def __init__(self, log, debug_level, ignore_errors, job):
        self.log = log
        self.debug_level = debug_level
        self.ignore_errors = ignore_errors
        self.job = job

        self.logger = logging.getLogger("parser")
        self.logger.setLevel(debug_level)

    def get_correct_parsers(self):
        BuildLogFileParser._import_parser()

        list_of_parsers = all_subclasses(BuildLogFileParser)
        fitting_parsers = []
        for sc in list_of_parsers:
            parser = sc(self.log, self.debug_level, self.ignore_errors, self.job)
            try:
                if parser.detect():
                    fitting_parsers.append(parser)
            except AttributeError:
                pass
            except NotImplementedError:
                pass

        return fitting_parsers

    def detect(self):
        raise NotImplementedError()

    def parse(self):
        raise NotImplementedError()

    @staticmethod
    def _import_parser():
        backend_files = [x[:-3] for x in os.listdir(os.path.dirname(os.path.realpath(__file__)))
                         if x.endswith(".py")]
        sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
        for backend in backend_files:
            __import__(backend)