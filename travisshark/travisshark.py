import logging
import datetime
import timeit

from mongoengine import connect, DoesNotExist

from pycoshark.mongomodels import TravisBuild, Commit, VCSSystem, TravisJob
from pycoshark.utils import create_mongodb_uri_string
from travisshark.client.travis_client import TravisClient, RequestException
from travisshark.parsers.build_log_file_parser import BuildLogFileParser

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
        failed_jobs = {}

        start_time = timeit.default_timer()
        logger.info("Starting extraction process for repository with slug %s..." % self.cfg.get_slug())
        repo = self.client.get_repository(self.cfg.get_slug())

        for build_number in range(1, int(repo['last_build_number'])):
            # If we already have this build, we continue
            if TravisBuild.objects(vcs_system_id=self.vcs_system_id, number=build_number).first() is not None:
                logger.info("Travis build with number %d and vcs_system_id %s already in database. Skipping..." % (
                    build_number, self.vcs_system_id
                ))
                continue

            tr_build = self.client.get_build_for_repository(repo['id'], build_number)
            build = self._create_mongo_build(tr_build)

            # We are only interested in failed builds at the moment
            logger.info("Build with number %d and id %s got %d jobs. Parsing..." % (build_number, build.tr_id,
                                                                                    len(build.job_ids)))

            for job_id in build.job_ids:
                tr_job = self.client.get_job_for_id(job_id)
                job = self._create_mongo_job(tr_job)
                build.jobs.append(job)

                # If we only want to mine failed jobs, we can use the only_failed switch
                if self.cfg.only_failed and job.state != 'failed':
                    logger.info("Travis job with number %s and id %s did not fail, but %s. Skipping..." % (
                        job.number, job_id, job.state
                    ))
                    continue

                # Debug stuff
                failed_jobs['https://api.travis-ci.org/jobs/%s/log.txt?deansi=true' % job_id] = {}

                try:
                    logger.info("Collecting data for Job with id %s..." % job.tr_id)
                    log = self.client.get_log_for_job_id(job.tr_id)

                    try:
                        logger.debug("Looking at job config %s..." % job.config)
                        parser = BuildLogFileParser(log, self.cfg.get_debug_level()).get_correct_parser(job.config)
                    except NotImplementedError as e:
                        logger.error("Got following error: %s" % e)
                        continue

                    logger.info("Using %s." % parser.__class__.__name__)

                    job.failed_tests, job.errored_tests, job.test_framework, job.tests_run = parser.parse()

                    # Debug stuff
                    failed_jobs['https://api.travis-ci.org/jobs/%s/log.txt?deansi=true' % job_id]['failed_tests'] = job.failed_tests
                    failed_jobs['https://api.travis-ci.org/jobs/%s/log.txt?deansi=true' % job_id]['errored_tests'] = job.errored_tests
                    logger.debug("The following tests failed: %s" % job.failed_tests)
                    logger.debug("The following tests errored: %s" % job.errored_tests)
                except RequestException:
                    logger.warning("Could not get log file for job with id %s. Travis error..." % job.tr_id)

            build.save()

        for failed_job, results in failed_jobs.items():
            print(failed_job)
            print(results)

        elapsed = timeit.default_timer() - start_time
        logger.info("Execution time: %0.5f s" % elapsed)

    def _create_mongo_job(self, job):
        m_job = TravisJob()
        m_job.tr_id = job['id']
        m_job.state = job['state']
        m_job.allow_failure = bool(job['allow_failure'])
        m_job.tags = job['tags']

        if job['started_at'] is not None:
            m_job.started_at = datetime.datetime.strptime(job['started_at'], '%Y-%m-%dT%H:%M:%SZ')

        if job['finished_at'] is not None:
            m_job.finished_at = datetime.datetime.strptime(job['finished_at'], '%Y-%m-%dT%H:%M:%SZ')

        m_job.number = job['number']

        if len(job['annotation_ids']) > 0:
            m_job.annotation_desc = [annotation['description'] for annotation in
                                     self.client.get_annotations_for_job_id(job['id'])]

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
        if len(build['builds']) > 1:
            logger.warning("Build %s has more than one build!" % build)
            #raise Exception("More than one build!")

        if len(build['commits']) > 1:
            logger.warning("Build %s has more than one commit!" % build)
            #raise Exception("More than one commit!")

        m_build.vcs_system_id = self.vcs_system_id
        m_build.state = build['builds'][0]['state']
        m_build.number = int(build['builds'][0]['number'])
        m_build.event_type = build['builds'][0]['event_type']
        m_build.duration = int(build['builds'][0]['duration'])

        if build['builds'][0]['started_at'] is not None:
            m_build.started_at = datetime.datetime.strptime(build['builds'][0]['started_at'], '%Y-%m-%dT%H:%M:%SZ')

        if build['builds'][0]['finished_at'] is not None:
            m_build.finished_at = datetime.datetime.strptime(build['builds'][0]['finished_at'], '%Y-%m-%dT%H:%M:%SZ')
        m_build.pull_request = bool(build['builds'][0]['pull_request'])
        m_build.tr_id = build['builds'][0]['id']
        m_build.job_ids = build['builds'][0]['job_ids']

        if not m_build.pull_request:
            # It can happen that we do not find the corresponding commit. This happens, e.g., if someone did a
            # git rebase to change the history after a build -> travis build was done, but the commit is no longer
            # existent
            try:
                m_build.commit_id = Commit.objects(vcs_system_id=self.vcs_system_id,
                                                   revision_hash=build['commits'][0]['sha']).only('id').get().id
            except DoesNotExist:
                logger.warning("Could not find commit with hash %s." % build['commits'][0]['sha'])
        else:
            m_build.pr_number = int(build['commits'][0]['pull_request_number'])

        return m_build
