import sys

from pycoshark.utils import get_base_argparser
from travisshark.config import Config, ConfigValidationException
from travisshark.travisshark import TravisSHARK

def start():
    parser = get_base_argparser('Collects information from the Travis CI.', '1.0.0')
    parser.add_argument('-u', '--url', help='URL of the project (e.g., GIT Url).', required=True)
    parser.add_argument('-PH', '--proxy-host', help='Proxy hostname or IP address.', default=None)
    parser.add_argument('-PP', '--proxy-port', help='Port of the proxy to use.', default=None)
    parser.add_argument('-Pp', '--proxy-password', help='Password to use the proxy (HTTP Basic Auth)', default=None)
    parser.add_argument('-PU', '--proxy-user', help='Username to use the proxy (HTTP Basic Auth)', default=None)
    parser.add_argument('--debug', help='Sets the debug level.', default='DEBUG',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    parser.add_argument('-t', '--token', help='Token for accessing travis.', required=True)
    parser.add_argument('--ignore-errors', help='Switch on, if errors should be ignored.', default=False,
                        action='store_true')
    parser.add_argument('--only-failed', help='Switch on, if you only want to mine failed jobs', default=False,
                        action='store_true')
    parser.add_argument('--rerun', help='Switch on, if you want to rerun on all builds', default=False,
                        action='store_true')

    try:
        args = parser.parse_args()
        cfg = Config(args)
    except ConfigValidationException as e:
        sys.stderr.write("Could not validate config!")
        sys.exit(1)

    travisshark = TravisSHARK(cfg)
    travisshark.run()


if __name__ == "__main__":
    start()