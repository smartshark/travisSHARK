import unittest

from tests.base_test import JobMock, BaseTest
from travisshark.parsers.maven_build_log_file_parser import MavenBuildLogFileParser


class MavenBuildLogFileParserTest(BaseTest):
    def setUp(self):
        self.job = JobMock()

    def test_detect(self):
        for log_name in self.get_all_log_names():
            parser = MavenBuildLogFileParser(self.get_log(log_name), 'DEBUG', False, self.job)

            if log_name.startswith('maven'):
                self.assertTrue(parser.detect(), 'Log %s should not be an maven log file!' % log_name)
            else:
                self.assertFalse(parser.detect(), 'Log %s should be an maven log file!' % log_name)

    def test_failed_tests_4(self):
        parser = MavenBuildLogFileParser(self.get_log('maven_failed_tests_junit_4.txt'), 'DEBUG', False, self.job)
        parser.parse()
        self.assertSetEqual(self.job.metrics['errored_tests'], set([]))
        self.assertSetEqual(self.job.metrics['failed_tests'], {'com.zaxxer.hikari.pool.HouseKeeperCleanupTest.testHouseKeeperCleanupWithCustomExecutor'})

    def test_failed_tests_2(self):
        parser = MavenBuildLogFileParser(self.get_log('maven_failed_tests_junit_2.txt'), 'DEBUG', False, self.job)
        parser.parse()
        self.assertSetEqual(self.job.metrics['errored_tests'], set([]))
        self.assertSetEqual(self.job.metrics['failed_tests'],
                         {'org.apache.commons.math4.random.RandomUtilsDataGeneratorJDKSecureRandomTest.testNextUniformUniformNegativeToPositiveBounds'})


    def test_failed_tests_3(self):
        parser = MavenBuildLogFileParser(self.get_log('maven_failed_tests_junit_3.txt'), 'DEBUG', False, self.job)
        parser.parse()
        self.assertSetEqual(self.job.metrics['errored_tests'], set([]))
        self.assertSetEqual(self.job.metrics['failed_tests'], {'org.apache.commons.io.filefilter.FileFilterTestCase.testAgeFilter'})

    
    def test_failed_tests(self):
        parser = MavenBuildLogFileParser(self.get_log('maven_failed_tests_junit.txt'), 'DEBUG', False, self.job)
        parser.parse()
        self.assertSetEqual(self.job.metrics['errored_tests'], set([]))
        self.assertSetEqual(self.job.metrics['failed_tests'], {'com.google.inject.JitBindingsTest.testChildInjectorInheritsOption'})


    def test_test_framework_junit(self):
        parser = MavenBuildLogFileParser(self.get_log('maven_failed_tests_junit.txt'), 'DEBUG', False, self.job)
        parser.parse()
        self.assertEqual(self.job.metrics['test_framework'], 'junit')
        self.assertEqual(self.job.metrics['tests_run'], True)
        
    def test_errored_tests_2(self):
        parser = MavenBuildLogFileParser(self.get_log('maven_errored_tests_junit_2.txt'), 'DEBUG', False, self.job)
        parser.parse()
        self.assertSetEqual(self.job.metrics['failed_tests'], set([]))
        self.assertSetEqual(self.job.metrics['errored_tests'], {'com.google.inject.testing.persist.PersistJUnit4ClassRunnerTest.testSimpleNonTransaction',
                                                   'com.google.inject.testing.persist.PersistJUnit4ClassRunnerTest.testSimpleTransaction'})

    def test_errored_tests(self):
        parser = MavenBuildLogFileParser(self.get_log('maven_errored_tests_junit.txt'), 'DEBUG', False, self.job)
        parser.parse()
        self.assertSetEqual(self.job.metrics['failed_tests'], set([]))
        self.assertSetEqual(self.job.metrics['errored_tests'], {'org.apache.commons.math4.fraction.FractionTest.testAdd',
                                                   'org.apache.commons.math4.fraction.FractionTest.testSubtract',
                                                   'org.apache.commons.math4.fraction.FractionTest.testReciprocal',
                                                   'org.apache.commons.math4.fraction.FractionTest.testGetReducedFraction',
                                                   'org.apache.commons.math4.fraction.FractionTest.testDivide',
                                                   'org.apache.commons.math4.fraction.FractionTest.testNegate',
                                                   'org.apache.commons.math4.fraction.FractionTest.testConstructor',
                                                   'org.apache.commons.math4.util.CombinatoricsUtilsTest.testStirlingS2Overflow',
                                                   'org.apache.commons.math4.util.CombinatoricsUtilsTest.testFactorialFail'})

    def test_errored_tests_3(self):
        parser = MavenBuildLogFileParser(self.get_log('maven_errored_tests_junit_3.txt'), 'DEBUG', False, self.job)
        parser.parse()
        self.assertSetEqual(self.job.metrics['failed_tests'], set([]))
        self.assertSetEqual(self.job.metrics['errored_tests'], {'okio.BufferedSourceTest.longDecimalStringTooShortThrows[RealBufferedSource]',
                                                   'okio.BufferedSourceTest.longDecimalStringAcrossSegment[Buffer]',
                                                   'okio.BufferedSourceTest.longDecimalString[Buffer]',
                                                   'okio.BufferedSourceTest.longDecimalStringTooLongThrows[Buffer]',
                                                   'okio.BufferedSourceTest.longDecimalStringTooHighThrows[Buffer]',
                                                   'okio.BufferedSourceTest.longDecimalStringTooShortThrows[Buffer]',
                                                   'okio.BufferedSourceTest.longDecimalStringAcrossSegment[RealBufferedSource]',
                                                   'okio.BufferedSourceTest.longDecimalString[RealBufferedSource]',
                                                   'okio.BufferedSourceTest.longDecimalStringTooLongThrows[RealBufferedSource]',
                                                   'okio.BufferedSourceTest.longDecimalStringTooHighThrows[RealBufferedSource]'})

    def test_errored_tests_4(self):
        parser = MavenBuildLogFileParser(self.get_log('maven_errored_tests_junit_4.txt'), 'DEBUG', False, self.job)
        parser.parse()
        self.assertSetEqual(self.job.metrics['failed_tests'], set([]))
        self.assertSetEqual(self.job.metrics['errored_tests'], {
            'org.apache.ibatis.submitted.multiple_resultsets.MultipleResultTest.shouldGetAGraphOutOfMultipleRsWithNoFKs',
            'org.apache.ibatis.submitted.multiple_resultsets.MultipleResultTest.shouldGetAGraphOutOfMultipleRsWithFKs',
             })

    def test_errored_tests_5_and_ignore_errors_because_of_setup_method(self):
        parser = MavenBuildLogFileParser(self.get_log('maven_errored_tests_junit_5.txt'), 'DEBUG', False, self.job)
        parser.parse()
        self.assertSetEqual(self.job.metrics['failed_tests'], set([]))
        self.assertSetEqual(self.job.metrics['errored_tests'],
                            {'org.apache.ibatis.submitted.manyanno.ManyAnnoTest.testGetMessageForEmptyDatabase',
                             'org.apache.ibatis.submitted.duplicate_resource_loaded.DuplicateResourceTest.shouldDemonstrateDuplicateResourceIssue',
                             'org.apache.ibatis.submitted.sptests.SPTest.testAdderAsSelectDoubleCall1',
                             'org.apache.ibatis.submitted.sptests.SPTest.testAdderAsSelectDoubleCall2',
                             'org.apache.ibatis.submitted.sptests.SPTest.testGetNamesAndItemsLinkedWithNoMatchingInfo',
                             'org.apache.ibatis.submitted.sptests.SPTest.testCallWithResultSet1Annotated',
                             'org.apache.ibatis.submitted.sptests.SPTest.testAdderAsSelectAnnotated',
                             'org.apache.ibatis.submitted.sptests.SPTest.testGetNamesAndItemsLinked',
                             'org.apache.ibatis.submitted.sptests.SPTest.testGetNamesAndItems_a2',
                             'org.apache.ibatis.submitted.sptests.SPTest.testGetNamesAndItems_a3',
                             'org.apache.ibatis.submitted.sptests.SPTest.testGetNamesWithArray_a1',
                             'org.apache.ibatis.submitted.sptests.SPTest.testGetNamesWithArray_a2',
                             'org.apache.ibatis.submitted.sptests.SPTest.testCallLowHighWithResultSet',
                             'org.apache.ibatis.submitted.sptests.SPTest.testGetNamesAndItems',
                             'org.apache.ibatis.submitted.sptests.SPTest.testAdderAsSelect',
                             'org.apache.ibatis.submitted.sptests.SPTest.testAdderAsUpdate',
                             'org.apache.ibatis.submitted.sptests.SPTest.testCallWithResultSet1',
                             'org.apache.ibatis.submitted.sptests.SPTest.testCallWithResultSet2',
                             'org.apache.ibatis.submitted.sptests.SPTest.testCallWithResultSet3',
                             'org.apache.ibatis.submitted.sptests.SPTest.testCallWithResultSet4',
                             'org.apache.ibatis.submitted.sptests.SPTest.testCallWithResultSet1_a2',
                             'org.apache.ibatis.submitted.sptests.SPTest.testCallWithResultSet2_a1',
                             'org.apache.ibatis.submitted.sptests.SPTest.testCallWithResultSet2_a2',
                             'org.apache.ibatis.submitted.sptests.SPTest.testCallWithResultSet3_a1',
                             'org.apache.ibatis.submitted.sptests.SPTest.testCallWithResultSet3_a2',
                             'org.apache.ibatis.submitted.sptests.SPTest.testCallWithResultSet4_a1',
                             'org.apache.ibatis.submitted.sptests.SPTest.testCallWithResultSet4_a2',
                             'org.apache.ibatis.submitted.sptests.SPTest.testAdderAsUpdateAnnotated',
                             'org.apache.ibatis.submitted.sptests.SPTest.testAdderAsUpdateWithParameterMap',
                             'org.apache.ibatis.submitted.sptests.SPTest.testGetNamesWithArray',
                             'org.apache.ibatis.submitted.sptests.SPTest.testEchoDate',
                             'org.apache.ibatis.submitted.sptests.SPTest.testAdderAsSelectDoubleCallAnnotated1',
                             'org.apache.ibatis.submitted.sptests.SPTest.testAdderAsSelectDoubleCallAnnotated2',
                             'org.apache.ibatis.jdbc.SqlRunnerTest.shouldInsert',
                             'org.apache.ibatis.builder.xml.dynamic.DynamicSqlSourceTest.shouldTrimSETInsteadOfCOMMAForBothConditions',
                             'org.apache.ibatis.builder.xml.dynamic.DynamicSqlSourceTest.shouldConditionallyDefault',
                             'org.apache.ibatis.builder.xml.dynamic.DynamicSqlSourceTest.shouldConditionallyIncludeWhere',
                             'org.apache.ibatis.builder.xml.dynamic.DynamicSqlSourceTest.shouldDemonstrateSimpleExpectedTextWithNoLoopsOrConditionals',
                             'org.apache.ibatis.builder.xml.dynamic.DynamicSqlSourceTest.shouldTrimNoWhereClause',
                             'org.apache.ibatis.builder.xml.dynamic.DynamicSqlSourceTest.shouldTrimWHEREANDWithCRLFForFirstCondition',
                             'org.apache.ibatis.builder.xml.dynamic.DynamicSqlSourceTest.shouldTrimWHEREORWithCRLFForFirstCondition',
                             'org.apache.ibatis.builder.xml.dynamic.DynamicSqlSourceTest.shouldTrimWHEREInsteadOfANDForFirstCondition',
                             'org.apache.ibatis.builder.xml.dynamic.DynamicSqlSourceTest.shouldTrimWHEREInsteadOfANDForBothConditions',
                             'org.apache.ibatis.builder.xml.dynamic.DynamicSqlSourceTest.shouldTrimNoSetClause',
                             'org.apache.ibatis.builder.xml.dynamic.DynamicSqlSourceTest.shouldTrimWHEREANDWithLFForFirstCondition',
                             'org.apache.ibatis.builder.xml.dynamic.DynamicSqlSourceTest.shouldTrimWHEREORWithLFForFirstCondition',
                             'org.apache.ibatis.builder.xml.dynamic.DynamicSqlSourceTest.shouldTrimWHEREANDWithTABForFirstCondition',
                             'org.apache.ibatis.builder.xml.dynamic.DynamicSqlSourceTest.shouldIterateOnceForEachItemInCollection',
                             'org.apache.ibatis.builder.xml.dynamic.DynamicSqlSourceTest.shouldPerformStrictMatchOnForEachVariableSubstitution',
                             'org.apache.ibatis.builder.xml.dynamic.DynamicSqlSourceTest.shouldTrimWHEREORWithTABForFirstCondition',
                             'org.apache.ibatis.builder.xml.dynamic.DynamicSqlSourceTest.shouldDemonstrateMultipartExpectedTextWithNoLoopsOrConditionals',
                             'org.apache.ibatis.builder.xml.dynamic.DynamicSqlSourceTest.shouldConditionallyChooseFirst',
                             'org.apache.ibatis.builder.xml.dynamic.DynamicSqlSourceTest.shouldConditionallyExcludeWhere',
                             'org.apache.ibatis.builder.xml.dynamic.DynamicSqlSourceTest.shouldTrimWHEREInsteadOfORForSecondCondition',
                             'org.apache.ibatis.builder.xml.dynamic.DynamicSqlSourceTest.shouldConditionallyChooseSecond',
                             })

    def test_errored_tests_6(self):
        parser = MavenBuildLogFileParser(self.get_log('maven_errored_tests_junit_6.txt'), 'DEBUG', False, self.job)
        parser.parse()
        self.assertSetEqual(self.job.metrics['errored_tests'],
                            {
                                'org.apache.ibatis.executor.loader.JavassistProxyTest.shouldSerizalizeADeserlizaliedProxy',
                                'org.apache.ibatis.executor.loader.JavassistProxyTest.shouldLetCallALoadedProperty',
                                'org.apache.ibatis.executor.loader.JavassistProxyTest.shouldFailCallingAnUnloadedProperty',
                                'org.apache.ibatis.executor.loader.JavassistProxyTest.shouldCreateAProxyForAPartiallyLoadedBean',
                                'org.apache.ibatis.executor.loader.JavassistProxyTest.shouldSerizaliceAFullLoadedObjectToOriginalClass',
                                'org.apache.ibatis.executor.loader.JavassistProxyTest.shouldSerializeAProxyForABeanWithoutDefaultConstructorAndUnloadedProperties',
                                'org.apache.ibatis.executor.loader.JavassistProxyTest.shouldNotLetReadUnloadedPropertyAfterSerialization',
                                'org.apache.ibatis.executor.loader.JavassistProxyTest.shouldLetReadALoadedPropertyAfterSerialization',
                                'org.apache.ibatis.executor.loader.JavassistProxyTest.shouldGenerateWriteReplace',
                                'org.apache.ibatis.executor.loader.JavassistProxyTest.shouldSerializeAProxyForABeanWithoutDefaultConstructor',
                                'org.apache.ibatis.executor.loader.JavassistProxyTest.shouldSerializeAProxyForABeanWithDefaultConstructor',
                                'org.apache.ibatis.executor.loader.JavassistProxyTest.shouldNotLetReadUnloadedPropertyAfterTwoSerializations',
                                'org.apache.ibatis.executor.loader.JavassistProxyTest.shouldKeepGenericTypes',
                                'org.apache.ibatis.executor.loader.JavassistProxyTest.shouldNotCreateAProxyForAFullyLoadedBean',
                                'org.apache.ibatis.executor.loader.JavassistProxyTest.shouldNotGenerateWriteReplaceItThereIsAlreadyOne',
                                'org.apache.ibatis.submitted.javassist.JavassistTest.shouldGetAUserAndGroups',
                            })
        self.assertSetEqual(self.job.metrics['failed_tests'], set([]))

    def test_errored_tests_7(self):
        parser = MavenBuildLogFileParser(self.get_log('maven_errored_tests_junit_7.txt'), 'DEBUG', False, self.job)
        parser.parse()
        self.assertSetEqual(self.job.metrics['failed_tests'],
                            {
                                'org.apache.ibatis.submitted.associationtest.AssociationTest.shouldGetAllCars',
                                'org.apache.ibatis.submitted.column_prefix.ColumnPrefixNestedQueryTest.testComplexPerson',
                                'org.apache.ibatis.submitted.column_prefix.ColumnPrefixTest.testComplexPerson',
                                'org.apache.ibatis.submitted.column_prefix.ColumnPrefixTest.testSelectPetAndRoom',
                                'org.apache.ibatis.submitted.column_prefix.ColumnPrefixAutoMappingTest.testComplexPerson',
                                'org.apache.ibatis.submitted.column_prefix.ColumnPrefixAutoMappingTest.testSelectPetAndRoom',
                                'org.apache.ibatis.submitted.not_null_column.NotNullColumnTest.testNotNullColumnWithoutChildrenFidWorkaround',
                                'org.apache.ibatis.submitted.null_associations.FooMapperTest.testNullAssociation',
                                'org.apache.ibatis.submitted.parent_childs.ParentChildTest.shouldGetAUser',
                                'org.apache.ibatis.submitted.parent_reference_3level.BlogTest.testSelectBlogWithoutPostsColumnPrefix',
                                'org.apache.ibatis.submitted.parent_reference_3level.BlogTest.testSelectBlogWithoutPosts',
                                'org.apache.ibatis.type.ClobTypeHandlerTest.shouldGetResultNullFromResultSetByName',
                                'org.apache.ibatis.type.ClobTypeHandlerTest.shouldGetResultNullFromCallableStatement',
                                'org.apache.ibatis.type.ClobTypeHandlerTest.shouldGetResultNullFromResultSetByPosition',
                                'org.apache.ibatis.type.NClobTypeHandlerTest.shouldGetResultNullFromResultSetByName',
                                'org.apache.ibatis.type.NClobTypeHandlerTest.shouldGetResultNullFromCallableStatement',
                                'org.apache.ibatis.type.NClobTypeHandlerTest.shouldGetResultNullFromResultSetByPosition',
                                'org.apache.ibatis.submitted.emptycollection.DaoTest.testWithEmptyList',
                            })
        self.assertSetEqual(self.job.metrics['errored_tests'], set([]))

if __name__ == '__main__':
    unittest.main()
