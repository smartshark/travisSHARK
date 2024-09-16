import logging
import datetime
import timeit

import pprint

import sys
from mongoengine import connect, DoesNotExist

from pycoshark.mongomodels import TravisBuild, TravisJob, Project, CiTravisSystem
from pycoshark.utils import create_mongodb_uri_string
from travisshark.client.travis_client import TravisClient, RequestException
from travisshark.parsers.build_log_file_parser import BuildLogFileParser, JobConfigError, NoFittingParserFoundError
from deepdiff import DeepDiff

logger = logging.getLogger("main")


class TravisSHARK(object):
    def __init__(self, cfg):
        logger.setLevel(cfg.get_debug_level())

        self.build_id = None
        self.parsed_travis = {'builds': {}, 'jobs': {}}
        self.old_travis = {'builds': {}}
        self.travis_diff = {}
        # Connect to mongodb
        uri = create_mongodb_uri_string(cfg.user, cfg.password, cfg.host, cfg.port, cfg.authentication_db,
                                        cfg.ssl_enabled)

        connect(cfg.database, host=uri)

        try:
            self.project = Project.objects.get(name=cfg.project_name)
        except Project.DoesNotExist:
            logger.error('Project %s not found!', cfg.project_name)
            sys.exit(1)

        last_system = CiTravisSystem.objects.filter(project_id=self.project.id).order_by('-collection_date').first()
        self.last_system_id = last_system.id if last_system else None

        self.ci_system = CiTravisSystem(project_id=self.project.id, url=cfg.repository_url,
                                           collection_date=datetime.datetime.now())
        self.ci_system.save()

        self.client = TravisClient(cfg.token, cfg.get_proxy_dictionary(), cfg.get_debug_level())
        self.cfg = cfg

    def run(self):
        start_time = timeit.default_timer()
        logger.info("Starting extraction process for repository with slug %s..." % self.cfg.get_slug())

        # Get the first few builds
        self.parse_travis()
        self.save_travis()

        elapsed = timeit.default_timer() - start_time
        logger.info("Execution time: %0.5f s" % elapsed)

    def save_travis(self):
        """
         Save parsed Travis CI builds and jobs to MongoDB.

         :return: None

         Example:
             save_travis()
         """
        for build_id, build in self.parsed_travis['builds'].items():
            if build_id in self.travis_diff and self.travis_diff[build_id]:
                build.save()
                if build_id not in self.parsed_travis['jobs']:
                    continue
                for job_id, job in self.parsed_travis['jobs'][build_id].items():
                    job.build_id = build.id
                    job.save()
            else:
                self.old_travis['builds'][build_id]['ci_system_ids'].append(self.ci_system.id)
                self.old_travis['builds'][build_id].save()

    def parse_travis(self):
        """
         Parse and collect data for Travis CI builds and jobs.

         :return: None

         Example:
             parse_travis()
         """
        resp = self.client.get_initial_builds_for_project_sorted_by_number(self.cfg.get_slug())
        while True:
            # Parse all builds
            for build in resp['builds']:

                new_build, mongo_build = self.parse_builds(build)

                logger.info(
                    "Build with number %d and id %s got %d job(s). Parsing..." % (new_build.number, new_build.tr_id,
                                                                                  len(build['jobs'])))
                self.pares_job(build, mongo_build)
            # If we do not have builds left, we go out of this loop
            if resp['@pagination']['next'] is None:
                break
            # Get new builds using the pagination style
            resp = self.client.get_next_builds(resp['@pagination']['next']['@href'])

    def pares_job(self, build, mongo_build):
        """
            Parse and compare Travis CI jobs within a build.

            :param build: dict
                A dictionary containing information about a Travis CI build that includes job data.

            :param mongo_build: TravisBuild or None
                The MongoDB document representing the Travis CI build, or None if no corresponding document is found.

            :return: None

            Example:
                parse_job(build_data, mongo_build)
            """
        for job in build['jobs']:
            mongo_job = None
            if mongo_build:
                try:
                    mongo_job = TravisJob.objects.get(build_id=mongo_build.id, tr_id=job['id'])
                except TravisJob.DoesNotExist:
                    mongo_job = None

            new_job = TravisJob(tr_id=job['id'])
            new_job.allow_failure = bool(job['allow_failure'])
            new_job.number = job['number']
            new_job.state = job['state']

            if job['started_at'] is not None:
                new_job.started_at = datetime.datetime.strptime(job['started_at'], '%Y-%m-%dT%H:%M:%SZ')

            if job['finished_at'] is not None:
                new_job.finished_at = datetime.datetime.strptime(job['finished_at'], '%Y-%m-%dT%H:%M:%SZ')

            if job['stage'] is not None:
                new_job.stages.append(str(job['stage']))

            new_job.config = self._make_dict_keys_compatible(job['config'])

            # If we only want to mine failed jobs, we can use the only_failed switch
            if self.cfg.only_failed and job.state != 'failed':
                logger.info("Travis job %s did not fail, but %s. Skipping..." % (repr(job), job.state))
                continue

            # Here we start to collect metrics from the log, where we first get all parser that fit the log
            # and execute them
            try:
                logger.info("Collecting data for Job with id %s..." % new_job.tr_id)

                log = self.client.get_log_for_job_id(new_job.tr_id)
                new_job.job_log = log

                try:
                    parsers = BuildLogFileParser(log, self.cfg.get_debug_level(), self.cfg.ignore_errors,
                                                 new_job).get_correct_parsers()
                except:
                    logger.warning("Could not detect log parser for job id %s", new_job.tr_id)
                    parsers = []

                for parser in parsers:
                    logger.info("Using %s." % parser.__class__.__name__)

                    try:
                        parser.parse()
                    except:
                        logger.warning("Could not parse log for job id %s", new_job.tr_id)

                    # Debug stuff
                    logger.debug("Parsed the following job: %s" % repr(job))
            except RequestException:
                logger.warning("Could not get log file for job with id %s. Travis error..." % new_job.tr_id)

            if self.build_id not in self.parsed_travis['jobs']:
                self.parsed_travis['jobs'][self.build_id] = {}

            self.parsed_travis['jobs'][self.build_id][job['id']] = new_job
            self.check_diff_job(mongo_job, new_job)

    def parse_builds(self, build):
        """
        Parse and compare Travis CI builds.

        :param build: dict
            A dictionary containing information about a Travis CI build.

        :return: tuple
            A tuple containing the new TravisBuild instance and the old TravisBuild instance, or None if no
            corresponding document is found in the database.

        Example:
            new_build, mongo_build = parse_builds(build_data)
        """

        self.build_id = build['id']
        # If we already have this build, we continue
        try:
            mongo_build = TravisBuild.objects.get(ci_system_ids=self.last_system_id, tr_id=self.build_id)
            self.old_travis['builds'][self.build_id] = mongo_build
        except TravisBuild.DoesNotExist:
            mongo_build = None
        new_build = TravisBuild(ci_system_ids=[self.ci_system.id], tr_id=build['id'])
        new_build.tr_id = build['id']
        new_build.project = self.project.id
        new_build.number = int(build['number'])
        new_build.state = build['state']
        new_build.event_type = build['event_type']
        if build['duration'] is not None:
            new_build.duration = int(build['duration'])
        if build['started_at'] is not None:
            new_build.started_at = datetime.datetime.strptime(build['started_at'], '%Y-%m-%dT%H:%M:%SZ')
        if build['finished_at'] is not None:
            new_build.finished_at = datetime.datetime.strptime(build['finished_at'], '%Y-%m-%dT%H:%M:%SZ')
        if build['pull_request_number'] is not None:
            new_build.pr_number = int(build['pull_request_number'])
        if build['stages'] is not None:
            for stage in build['stages']:
                new_build.stages.append(stage['name'])
        # It can happen that we do not find the corresponding commit. This happens, e.g., if someone did a
        # git rebase to change the history after a build -> travis build was done, but the commit is no longer
        # existent
        new_build.commit_id = build['commit']['sha']
        self.parsed_travis['builds'][self.build_id] = new_build
        self.check_diff_build(mongo_build, new_build)
        return new_build, mongo_build

    def _make_dict_keys_compatible(self, d):
        new = {}
        for k, v in d.items():
            if isinstance(v, dict):
                v = self._make_dict_keys_compatible(v)
            new[k.replace('.', '').replace('$', '')] = v
        return new

    def check_diff_build(self, old, new):
        """
        Compare two objects and perform checks.

        :param old: Object
            The old object to be compared.

        :param new: Object
            The new object to be compared.

        :return: None

        Example:
            check_diff_build(old_build, new_build)
        """
        self.check_diff(old, new, 'ci_system_ids')

    def check_diff_job(self, old, new):
        """
        Compare two objects  and perform checks.

        :param old: Object
            The old object to be compared.

        :param new: Object
            The new object to be compared.

        :return: None

        Example:
            check_diff_job(old_job, new_job)
        """
        self.check_diff(old, new, 'build_id')

    def check_diff(self, old, new, ex_path):
        """
        Compare and identify differences between old and new objects.

        This function compares two objects, `old` and `new`, typically representing data from different
        states, to identify differences between them. The comparison is performed by utilizing the
        DeepDiff library. Differences are stored in the `pr_diff` dictionary for the pull request
        identified by `self.pr_id`. If differences are found, the corresponding key in `pr_diff`
        is set to `True`.

        :param old: The old object to be compared.
        :param new: The new object to be compared.
        :param ex_path: List of paths to be excluded from the comparison.

        """
        self.travis_diff[self.build_id] = False
        if old:
            diff = DeepDiff(t1=old.__dict__, t2=new.__dict__, exclude_paths=ex_path)
            if diff:
                self.travis_diff[self.build_id] = True
        else:
            self.travis_diff[self.build_id] = True