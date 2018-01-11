import requests
import logging
import datetime as dt
import time

logger = logging.getLogger("main")

class RequestException(Exception):
    pass

class TravisClient(object):
    def __init__(self, travis_token, proxy, debug_level):
        self.travis_token = travis_token
        self.base_url = "https://api.travis-ci.org"
        self.proxy = proxy
        self.last_request = dt.datetime.now()
        logger.setLevel(debug_level)

    def get_initial_builds_for_project_sorted_by_number(self, slug):
        req_url = "%s/repo/%s/builds?sort_by=started_at&limit=100&include=build.jobs" % (self.base_url, slug)
        return self._send_request(req_url)

    def get_next_builds(self, next):
        req_url = "%s%s" % (self.base_url, next)
        return self._send_request(req_url)

    def get_log_for_job_id(self, job_id):
        # Currently, travis is using the s3 service to store their job logs, we can directly retrieve it without
        # using the api. Especially, as sometimes the api is failing.
        req_url = "https://s3.amazonaws.com/archive.travis-ci.org/jobs/%s/log.txt" % job_id

        # Sometimes, the direct connection to the s3 service fails, thats why we are using the api afterwards
        try:
            return self._send_request(req_url, accept_header='', json_format=False, authorization=False)
        except RequestException:
            req_url = "%s/jobs/%s/log.txt" % (self.base_url, job_id)
            return self._send_request(req_url, accept_header='', json_format=False)

    def _send_request(self, url, accept_header='application/vnd.travis-ci.2+json', json_format=True, authorization=True):
        tries = 1
        while tries <= 2:
            logger.debug("Sending request to url: %s" % url)

            # If tokens are used, set the header, if not use basic authentication
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0',
                'Accept': accept_header,
                'Travis-API-Version': '3',
            }
            if authorization:
                headers['Authorization'] = 'token %s' % self.travis_token

            while (dt.datetime.now()-self.last_request).total_seconds() <= 3:
                time.sleep(2)

            # Make the request
            resp = requests.get(url, headers=headers, proxies=self.proxy)
            self.last_request = dt.datetime.now()

            if resp.status_code != 200:
                logger.error("Problem with getting data via url %s. Error: %s" % (url, resp.text))
                tries = tries + 1
            else:
                if json_format:
                    logger.debug('Got response: %s' % resp.json())
                    return resp.json()
                else:
                    return resp.text

        raise RequestException("Problem with getting data via url %s. Error: %s" % (url, resp.text))

