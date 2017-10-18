import os
import unittest

from tests.base_test import BaseTest, JobMock
from travisshark.parsers.python_build_log_file_parser import PythonBuildLogFileParser


class PythonBuildLogFileParserTest(BaseTest):
    def setUp(self):
        self.job = JobMock()

    def test_errored_test_pytest_1(self):
        parser = PythonBuildLogFileParser(self.get_log('python_errored_tests_pytest.txt'), 'DEBUG', False)
        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, set([]))
        self.assertSetEqual(self.job.errored_tests, {'tests/test_formatutils.py', 'tests/test_formatutils.py'})
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "pytest")

    def test_trial_errored_tests_4(self):
        parser = PythonBuildLogFileParser(self.get_log('python_errored_tests_trial_4.txt'), 'DEBUG', False)

        parser.parse(self.job)
        self.assertEqual(len(self.job.failed_tests), 10)
        self.assertEqual(len(self.job.errored_tests), 21)
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "unittest")

    def test_trial_errored_tests_3(self):
        parser = PythonBuildLogFileParser(self.get_log('python_errored_tests_trial_3.txt'), 'DEBUG', False)

        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, set([]))
        self.assertSetEqual(self.job.errored_tests, {'scrapy.tests.test_selector_libxml2',
                                                 'scrapy.tests.test_contrib_linkextractors'})
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "unittest")

    def test_trial_errored_tests_2(self):
        parser = PythonBuildLogFileParser(self.get_log('python_errored_tests_trial_2.txt'), 'DEBUG', False)

        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, set([]))
        self.assertSetEqual(self.job.errored_tests, {'scrapy.tests.test_selector_libxml2',
                                                 'scrapy.tests.test_contrib_linkextractors'})
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "unittest")

    def test_trial_errored_tests(self):
        parser = PythonBuildLogFileParser(self.get_log('python_errored_tests_trial.txt'), 'DEBUG', False)

        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, set([]))
        self.assertSetEqual(self.job.errored_tests, {'scrapy.tests.test_selector_libxml2'})
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "unittest")

    def test_trial_failed_tests(self):
        parser = PythonBuildLogFileParser(self.get_log('python_failed_tests_trial.txt'), 'DEBUG', False)

        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, {'scrapy.tests.test_contrib_exporter.JsonLinesItemExporterTest.test_nested_item'})
        self.assertSetEqual(self.job.errored_tests, set([]))
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "unittest")

    def test_special_case_4(self):
        parser = PythonBuildLogFileParser(self.get_log('python_special_case_4.txt'), 'DEBUG', False)

        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, {'tests.test_client_session.test_borrow_connector_loop',
                                                'tests.test_client_session.test_create_session_outside_of_coroutine',
                                                'tests.test_connector.TestHttpClientConnector.test_tcp_connector_uses_provided_local_addr'})
        self.assertSetEqual(self.job.errored_tests, set([]))
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "pytest-sugar")

    def test_special_case_3(self):
        parser = PythonBuildLogFileParser(self.get_log('python_special_case_3.txt'), 'DEBUG', False)

        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, set([]))
        self.assertSetEqual(self.job.errored_tests, set([]))
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "pytest-sugar")

    def test_special_case_2(self):
        parser = PythonBuildLogFileParser(self.get_log('python_special_case_2.txt'), 'DEBUG', False)

        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, {'tests.test_client_session.test_lazy_init_create_session'})
        self.assertSetEqual(self.job.errored_tests, set([]))
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "pytest-sugar")

    def test_special_case_1(self):
        parser = PythonBuildLogFileParser(self.get_log('python_special_case_1.txt'), 'DEBUG', False)

        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, {'tests.test_connector.TestHttpClientConnector.test_resolver_not_called_with_address_is_ip'})
        self.assertSetEqual(self.job.errored_tests, set([]))
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "pytest-sugar")

    def test_errored_test_unittest_7(self):
        parser = PythonBuildLogFileParser(self.get_log('python_errored_tests_unittest_7.txt'), 'DEBUG', False)

        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, set([]))
        self.assertEqual(len(self.job.errored_tests), 54)
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "unittest")

    def test_errored_test_unittest_8(self):
        parser = PythonBuildLogFileParser(self.get_log('python_errored_tests_unittest_8.txt'), 'DEBUG', False)

        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, set([]))
        self.assertSetEqual(self.job.errored_tests, {'test_requests.RequestsTestSuite.test_file_post_data'})
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "unittest")

    def test_failed_test_unittest_6(self):
        parser = PythonBuildLogFileParser(self.get_log('python_failed_tests_unittest_6.txt'), 'DEBUG', False)

        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, {"test_clique.TestCliques.test_find_cliques1"})
        self.assertSetEqual(self.job.errored_tests, set([]))
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "unittest")

    def test_errored_test_unittest_6(self):
        parser = PythonBuildLogFileParser(self.get_log('python_errored_tests_unittest_6.txt'), 'DEBUG', False)

        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, set([]))
        self.assertSetEqual(self.job.errored_tests, {"test_cuts.test_node_cutset_random_graphs"})
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "unittest")

    def test_failed_test_unittest_5(self):
        parser = PythonBuildLogFileParser(self.get_log('python_failed_tests_unittest_5.txt'), 'DEBUG', False)

        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, {"networkx.algorithms.connectivity.cuts.minimum_st_edge_cut"})
        self.assertSetEqual(self.job.errored_tests, set([]))
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "unittest")

    def test_errored_test_pytest_4(self):
        parser = PythonBuildLogFileParser(self.get_log('python_errored_tests_pytest_4.txt'), 'DEBUG', False)
        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, set([]))
        self.assertSetEqual(self.job.errored_tests, {'tests/integration/py2/nupic/opf/opf_description_template_test/opf_description_template_test.py'})
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "pytest")

    def test_failed_and_errored_test_unittest_special_2(self):
        parser = PythonBuildLogFileParser(self.get_log('python_unittest_special_case_2.txt'), 'DEBUG', True)

        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, set([]))
        self.assertSetEqual(self.job.errored_tests, set([]))
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "pytest")

    def test_failed_and_errored_test_unittest_special(self):
        parser = PythonBuildLogFileParser(self.get_log('python_unittest_special_case.txt'), 'DEBUG', True)

        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, {"nupic-linux64.nta.eng.lib.python2.7.site-packages.nupic.support.unittesthelpers.testcasebase.TPLikelihoodTest.testLikelihood1Long",
                                                "tests.integration.py2.nupic.algorithms.tp_likelihood_test.TPLikelihoodTest.testLikelihood1Short",
                                                "nupic-linux64.nta.eng.lib.python2.7.site-packages.nupic.support.unittesthelpers.testcasebase.TPLikelihoodTest.testLikelihood2Long",
                                                "tests.integration.py2.nupic.algorithms.tp_likelihood_test.TPLikelihoodTest.testLikelihood2Short",
                                                "tests.integration.py2.nupic.opf.opf_region_test.OPFRegionTest.testCLAAndSP",
                                                "tests.integration.py2.nupic.opf.opf_region_test.OPFRegionTest.testCLAAndSPFlow",
                                                "tests.integration.py2.nupic.opf.opf_region_test.OPFRegionTest.testCLAAndSPTP",
                                                "tests.integration.py2.nupic.opf.opf_region_test.OPFRegionTest.testCLAAndSPTPFlow",
                                                "tests.integration.py2.nupic.opf.opf_region_test.OPFRegionTest.testMaxEnabledPhase",
                                                "tests.integration.py2.nupic.opf.opf_region_test.OPFRegionTest.testSaveAndReload",
                                                "tests.unit.py2.nupic.math.sparse_matrix_test.SparseMatrixTest.test_LogSumApprox",
                                                "tests.unit.py2.nupic.math.sparse_tensor_test.TestSparseTensor.test_Pickling"})
        self.assertSetEqual(self.job.errored_tests, {"tests/integration/py2/nupic/opf/run_opf_benchmarks_test.py"})
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "pytest")

    def test_failed_and_errored_test_unittest(self):
        parser = PythonBuildLogFileParser(self.get_log('python_failed_and_errored_tests_unittest.txt'), 'DEBUG', True)

        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, {"tests.test_official.check_object(Sticker)"})
        self.assertSetEqual(self.job.errored_tests, {"tests.test_official.check_object(StickerSet)",
                                                 "tests.test_official.check_object(MaskPosition)",
                                                 "tests.test_official.check_method(getStickerSet)",
                                                 "tests.test_official.check_method(uploadStickerFile)",
                                                 "tests.test_official.check_method(createNewStickerSet)",
                                                 "tests.test_official.check_method(addStickerToSet)",
                                                 "tests.test_official.check_method(setStickerPositionInSet)",
                                                 "tests.test_official.check_method(deleteStickerFromSet)",
                                                 })
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "unittest")

    def test_failed_test_unittest_4(self):
        parser = PythonBuildLogFileParser(self.get_log('python_failed_tests_unittest_4.txt'), 'DEBUG', False)

        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, {"tests.test_audio.AudioTest.test_send_audio_mp3_url_file_with_caption",
                                                "tests.test_audio.AudioTest.test_send_audio_mp3_url_file"})
        self.assertSetEqual(self.job.errored_tests, set([]))
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "unittest")

    def test_errored_test_unittest_5(self):
        parser = PythonBuildLogFileParser(self.get_log('python_errored_tests_unittest_5.txt'), 'DEBUG', False)

        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, set([]))
        self.assertSetEqual(self.job.errored_tests, {"tests.test_bot.BotTest.test_set_webhook_get_webhook_info"})
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "unittest")

    def test_errored_test_unittest_4(self):
        parser = PythonBuildLogFileParser(self.get_log('python_errored_tests_unittest_4.txt'), 'DEBUG', False)

        # Here an exeception is thrown as we can not identify the correct number of errored tests in any way
        with self.assertRaises(Exception):
            parser.parse(self.job)

    def test_errored_test_pytest_3(self):
        parser = PythonBuildLogFileParser(self.get_log('python_errored_tests_pytest_3.txt'), 'DEBUG', False)
        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, set([]))
        self.assertSetEqual(self.job.errored_tests, {'tests/integration/py2/nupic/swarming/swarming_test.py',
                                                   'tests/unit/py2/nupic/frameworks/opf/clamodel_classifier_helper_test.py',
                                                   'tests/unit/py2/nupic/frameworks/opf/clamodel_test.py'})
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "pytest")

    def test_errored_test_pytest_2(self):
        parser = PythonBuildLogFileParser(self.get_log('python_errored_tests_pytest_2.txt'), 'DEBUG', False)
        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, set([]))
        self.assertSetEqual(self.job.errored_tests, {'tests/unit/py2/nupic/data/aggregator_test.py'})
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "pytest")

    def test_failed_tests_unittest_2(self):
        parser = PythonBuildLogFileParser(self.get_log('python_failed_tests_unittest_2.txt'), 'DEBUG', False)
        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, {'tests.test_process.Test_UV_Process.test_process_lated_stdio_init',
                                                  'tests.test_process.Test_UV_Process.test_process_lated_stdio_init',
                                                  'tests.test_process.Test_UV_Process.test_process_lated_stdio_init'})
        self.assertSetEqual(self.job.errored_tests, set([]))
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "unittest")

    def test_errored_test_unittest_3(self):
        parser = PythonBuildLogFileParser(self.get_log('python_errored_tests_unittest_3.txt'), 'DEBUG', False)
        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, set([]))
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "unittest")

    def test_failed_tests_unittest_3(self):
        parser = PythonBuildLogFileParser(self.get_log('python_failed_tests_unittest_3.txt'), 'DEBUG', False)
        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, set([]))
        self.assertSetEqual(self.job.errored_tests, set([]))
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "unittest")

    def test_errored_test_unittest_2(self):
        parser = PythonBuildLogFileParser(self.get_log('python_errored_tests_unittest_2.txt'), 'DEBUG', False)
        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, set([]))
        self.assertSetEqual(self.job.errored_tests, {'test_unix.Test_UV_Unix.test_transport_unclosed_warning',
                                                   'test_unix.Test_UV_Unix.test_transport_fromsock_get_extra_info',
                                                   'test_unix.Test_UV_Unix.test_create_unix_connection_5',
                                                   'test_unix.Test_UV_Unix.test_create_unix_connection_4',
                                                   'test_unix.Test_UV_Unix.test_create_unix_connection_1',
                                                   })
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "unittest")

    def test_failed_tests_1(self):
        parser = PythonBuildLogFileParser(self.get_log('python_failed_tests_unittest.txt'), 'DEBUG', False)
        parser.parse(self.job)
        self.assertSetEqual(self.job.errored_tests, set([]))
        self.assertSetEqual(self.job.failed_tests,
                            {'test_legacy_api.TestLegacyBulkNoResults.test_no_results_unordered_failure'})
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "unittest")

    def test_errored_tests_1(self):
        parser = PythonBuildLogFileParser(self.get_log('python_errored_tests_unittest.txt'), 'DEBUG', False)
        parser.parse(self.job)
        self.assertEqual(len(self.job.errored_tests), 358)
        self.assertSetEqual(self.job.failed_tests, set([]))
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "unittest")

    

    def test_failed_and_errored_test_pytest_1(self):
        parser = PythonBuildLogFileParser(self.get_log('python_failed_and_errored_tests_pyttest.txt'), 'DEBUG', False)
        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, {'boltons.gcutils.get_all', 'boltons.statsutils.rel_std_dev',
                                                  'boltons.timeutils.decimal_relative_time'})
        self.assertSetEqual(self.job.errored_tests, {'boltons/namedutils.py'})
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "pytest")

    def test_failed_test_pytest_new_output(self):
        parser = PythonBuildLogFileParser(self.get_log('python_failed_tests_pytest_new_output.txt'), 'DEBUG', False)
        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, {'tests.tbutils_test.test_eval_tb', 'tests.tbutils_test.test_normal_tb'})
        self.assertSetEqual(self.job.errored_tests, set([]))
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "pytest")

    def test_failed_test_pytest(self):
        parser = PythonBuildLogFileParser(self.get_log('python_failed_tests_pytest.txt'), 'DEBUG', False)
        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, {'tests.test_strutils.test_is_uuid'})
        self.assertSetEqual(self.job.errored_tests, set([]))
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "pytest")

    def test_failed_test_pytest_2(self):
        parser = PythonBuildLogFileParser(self.get_log('python_failed_tests_pytest_2.txt'), 'DEBUG', False)
        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, {'test_bashcomplete.test_single_command',
                                                  'test_bashcomplete.test_boolean_flag',
                                                  'test_bashcomplete.test_multi_value_option',
                                                  'test_bashcomplete.test_multi_option',
                                                  'test_bashcomplete.test_small_chain',
                                                  'test_bashcomplete.test_long_chain',
                                                  'test_bashcomplete.test_chaining',
                                                  'test_bashcomplete.test_argument_choice',
                                                  'test_bashcomplete.test_option_choice',
                                                  'test_bashcomplete.test_option_and_arg_choice',
                                                  'test_bashcomplete.test_boolean_flag_choice',
                                                  'test_bashcomplete.test_multi_value_option_choice',
                                                  'test_bashcomplete.test_multi_option_choice',
                                                  'test_bashcomplete.test_variadic_argument_choice',
                                                  'test_bashcomplete.test_long_chain_choice'})
        self.assertSetEqual(self.job.errored_tests, set([]))
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "pytest")

    def test_failed_test_pytest_3(self):
        parser = PythonBuildLogFileParser(self.get_log('python_failed_tests_pytest_3.txt'), 'DEBUG', False)
        parser.parse(self.job)
        self.assertEqual(len(self.job.failed_tests), 75)
        self.assertSetEqual(self.job.errored_tests, set([]))
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "pytest")

    def test_failed_test_pytest_4(self):
        parser = PythonBuildLogFileParser(self.get_log('python_failed_tests_pytest_4.txt'), 'DEBUG', True)
        parser.parse(self.job)
        self.assertSetEqual(self.job.failed_tests, {
            'tests.test_requests.TestPreparingURLs.test_preparing_url[6url6-http://xn--knigsgchen-b4a3dun.de/stra%C3%9Fe]',
            'tests.test_requests.TestPreparingURLs.test_preparing_url[4url4-http://xn--strae-oqa.de/stra%C3%9Fe]',
            'tests.test_requests.TestPreparingURLs.test_preparing_url[5http://stra\\xc3\\x9fe.de/stra\\xc3\\x9fe-http://xn--strae-oqa.de/stra%C3%9Fe]',
            'tests.test_requests.TestPreparingURLs.test_preparing_url[3http://\\xe3\\x82\\xb8\\xe3\\x82\\xa7\\xe3\\x83\\xbc\\xe3\\x83\\x94\\xe3\\x83\\xbc\\xe3\\x83\\x8b\\xe3\\x83\\x83\\xe3\\x82\\xaf.jp-http://xn--hckqz9bzb1cyrb.jp/]',
            'tests.test_requests.TestPreparingURLs.test_preparing_url[7http://K\\xc3\\xb6nigsg\\xc3\\xa4\\xc3\\x9fchen.de/stra\\xc3\\x9fe-http://xn--knigsgchen-b4a3dun.de/stra%C3%9Fe]',
            'tests.test_requests.TestPreparingURLs.test_preparing_bad_url[4url4]',
        })
        self.assertSetEqual(self.job.errored_tests, set([]))
        self.assertTrue(self.job.tests_run)
        self.assertEqual(self.job.test_framework, "pytest")


if __name__ == '__main__':
    unittest.main()
