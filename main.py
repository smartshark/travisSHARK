import sys
import logging

from pycoshark.utils import get_base_argparser, delete_last_system_data_on_failure
from travisshark.config import Config, ConfigValidationException
from travisshark.travisshark import TravisSHARK


log = logging.getLogger('travisshark')
log.setLevel(logging.INFO)
i = logging.StreamHandler(sys.stdout)
e = logging.StreamHandler(sys.stderr)

i.setLevel(logging.DEBUG)
e.setLevel(logging.ERROR)

log.addHandler(i)
log.addHandler(e)

def start():
    parser = get_base_argparser('Collects information from the Travis CI.', '1.0.0')
    parser.add_argument('-u', '--repository-url', help='URL of the project (e.g., GIT Url).', required=True)
    parser.add_argument('-pn', '--project-name', help='Name of the project.', required=True)
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
    try:
        travisshark.run()
    except (KeyboardInterrupt, Exception) as e:
        log.error(f"Program did not run successfully. Reason:{e}")
        log.info(f"Deleting uncompleted data .....")
        delete_last_system_data_on_failure('ci_travis_system', cfg.repository_url, db_user=cfg.user,
                                           db_password=cfg.password,
                                           db_hostname=cfg.host, db_port=cfg.port,
                                           db_authentication_db=cfg.authentication_db,
                                           db_ssl=cfg.ssl_enabled, db_name=cfg.database)


if __name__ == "__main__":
    start()
