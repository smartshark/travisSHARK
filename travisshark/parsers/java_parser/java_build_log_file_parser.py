import logging

from travisshark.parsers.build_log_file_parser import BuildLogFileParser

logger = logging.getLogger("parser")


class JavaBuildLogFileParser(BuildLogFileParser):
    def __init__(self, log, debug_level):
        super().__init__(log, debug_level)
