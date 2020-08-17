import logging
import datetime
import timeit

import pprint

import sys
from mongoengine import connect, DoesNotExist

from pycoshark.mongomodels import TravisBuild, Commit, VCSSystem, TravisJob
from pycoshark.utils import create_mongodb_uri_string
from travisshark.client.travis_client import TravisClient, RequestException
from travisshark.parsers.build_log_file_parser import BuildLogFileParser, JobConfigError, NoFittingParserFoundError

logger = logging.getLogger("main")


class TravisSHARK(object):
    def __init__(self, cfg):
        logger.setLevel(cfg.get_debug_level())

        # Connect to mongodb
        uri = create_mongodb_uri_string(cfg.user, cfg.password, cfg.host, cfg.port, cfg.authentication_db,
                                        cfg.ssl_enabled)
        connect(cfg.database, host=uri)

        self.client = TravisClient(cfg.token, cfg.get_proxy_dictionary(), cfg.get_debug_level())
        self.vcs_system_id = VCSSystem.objects(url=cfg.vcs_system_url).get().id
        self.cfg = cfg

    def run(self):
        start_time = timeit.default_timer()
        logger.info("Starting extraction process for repository with slug %s..." % self.cfg.get_slug())

        # Get the first few builds
        resp = self.client.get_initial_builds_for_project_sorted_by_number(self.cfg.get_slug())
        while True:

            # Parse all builds
            for build in resp['builds']:

                # If we already have this build, we continue
                m_build = TravisBuild.objects(vcs_system_id=self.vcs_system_id, number=build['number']).first()
                if m_build is None:
                    m_build = self._create_mongo_build(build)
                else:
                    if not self.cfg.rerun:
                        logger.info("Travis build %s already exists in database. Skipping..." % repr(m_build))
                        continue

                logger.info("Build with number %d and id %s got %d job(s). Parsing..." % (m_build.number, m_build.tr_id,
                                                                                          len(m_build.jobs)))
                for job in m_build.jobs:
                    # If we only want to mine failed jobs, we can use the only_failed switch
                    if self.cfg.only_failed and job.state != 'failed':
                        logger.info("Travis job %s did not fail, but %s. Skipping..." % (repr(job), job.state))
                        continue

                    # Here we start to collect metrics from the log, where we first get all parser that fit the log
                    # and execute them
                    try:
                        logger.info("Collecting data for Job with id %s..." % job.tr_id)

                        log = self.client.get_log_for_job_id(job.tr_id)
                        job.job_log = log

                        for parser in BuildLogFileParser(log, self.cfg.get_debug_level(), self.cfg.ignore_errors, job) \
                                .get_correct_parsers():
                            logger.info("Using %s." % parser.__class__.__name__)
                            parser.parse()

                            # Debug stuff
                            logger.debug("Parsed the following job: %s" % repr(job))
                    except RequestException:
                        logger.warning("Could not get log file for job with id %s. Travis error..." % job.tr_id)

                m_build.save()

            # If we do not have builds left, we go out of this loop
            if resp['@pagination']['next'] is None:
                break

            # Get new builds using the pagination style
            resp = self.client.get_next_builds(resp['@pagination']['next']['@href'])

        elapsed = timeit.default_timer() - start_time
        logger.info("Execution time: %0.5f s" % elapsed)

    def _create_mongo_job(self, job):
        m_job = TravisJob()
        m_job.tr_id = job['id']
        m_job.allow_failure = bool(job['allow_failure'])
        m_job.number = job['number']
        m_job.state = job['state']

        if job['started_at'] is not None:
            m_job.started_at = datetime.datetime.strptime(job['started_at'], '%Y-%m-%dT%H:%M:%SZ')

        if job['finished_at'] is not None:
            m_job.finished_at = datetime.datetime.strptime(job['finished_at'], '%Y-%m-%dT%H:%M:%SZ')

        if job['stage'] is not None:
            for stage in job['stage']:
                job.stages.append(stage['name'])

        m_job.config = self._make_dict_keys_compatible(job['config'])
        return m_job

    def _make_dict_keys_compatible(self, d):
        new = {}
        for k, v in d.items():
            if isinstance(v, dict):
                v = self._make_dict_keys_compatible(v)
            new[k.replace('.', '').replace('$', '')] = v
        return new

    def _create_mongo_build(self, build):
        m_build = TravisBuild()
        m_build.tr_id = build['id']
        m_build.vcs_system_id = self.vcs_system_id
        m_build.number = int(build['number'])
        m_build.state = build['state']
        m_build.event_type = build['event_type']

        if build['duration'] is not None:
            m_build.duration = int(build['duration'])

        if build['started_at'] is not None:
            m_build.started_at = datetime.datetime.strptime(build['started_at'], '%Y-%m-%dT%H:%M:%SZ')

        if build['finished_at'] is not None:
            m_build.finished_at = datetime.datetime.strptime(build['finished_at'], '%Y-%m-%dT%H:%M:%SZ')

        if build['pull_request_number'] is not None:
            m_build.pr_number = int(build['pull_request_number'])

        if build['stages'] is not None:
            for stage in build['stages']:
                build.stages.append(stage['name'])

        # It can happen that we do not find the corresponding commit. This happens, e.g., if someone did a
        # git rebase to change the history after a build -> travis build was done, but the commit is no longer
        # existent
        try:
            m_build.commit_id = Commit.objects(vcs_system_id=self.vcs_system_id,
                                               revision_hash=build['commit']['sha']).only('id').get().id
        except DoesNotExist:
            logger.warning("Could not find commit with hash %s." % build['commit']['sha'])

        for job in build['jobs']:
            m_job = self._create_mongo_job(job)
            m_build.jobs.append(m_job)

        return m_build
