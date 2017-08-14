import unittest
import os

from travisshark.parsers.java_parser.maven_build_log_file_parser import MavenBuildLogFileParser


class MavenBuildLogFileParserTest(unittest.TestCase):


    def _get_log(self, filename):
        with open(os.path.join(os.path.dirname(__file__), 'data', filename), 'r') as file:
            log = file.readlines()

            # We need to make some adaptions so that the file matches the return value from the api
            new_lines = []
            for line in log:
                new_lines.append(line.strip("\n")+"\r")
        return '\n'.join(new_lines)

    def test_failed_tests(self):
        parser = MavenBuildLogFileParser(self._get_log('maven_failed_tests_junit.txt'), 'DEBUG')
        parser.parse()
        self.assertEqual(parser.tests_failed, {'com.google.inject.JitBindingsTest.testChildInjectorInheritsOption'})



    def test_failed_tests_2(self):
        parser = MavenBuildLogFileParser(self._get_log('maven_failed_tests_junit_2.txt'), 'DEBUG')
        parser.parse()
        self.assertEqual(parser.tests_failed, {'org.apache.commons.math4.random.RandomUtilsDataGeneratorJDKSecureRandomTest.testNextUniformUniformNegativeToPositiveBounds'})


    def test_test_framework_junit(self):
        parser = MavenBuildLogFileParser(self._get_log('maven_failed_tests_junit.txt'), 'DEBUG')
        parser.parse()
        self.assertEqual(parser.test_framework, 'junit')
        self.assertEqual(parser.tests_run_completely, True)
        
    def test_errored_tests_2(self):
        parser = MavenBuildLogFileParser(self._get_log('maven_errored_tests_junit_2.txt'), 'DEBUG')
        parser.parse()
        self.assertSetEqual(parser.tests_errored, {'com.google.inject.testing.persist.PersistJUnit4ClassRunnerTest.testSimpleNonTransaction',
                                                   'com.google.inject.testing.persist.PersistJUnit4ClassRunnerTest.testSimpleTransaction'})

    def test_errored_tests(self):
        parser = MavenBuildLogFileParser(self._get_log('maven_errored_tests_junit.txt'), 'DEBUG')
        parser.parse()
        self.assertSetEqual(parser.tests_errored, {'org.apache.commons.math4.fraction.FractionTest.testAdd',
                                                   'org.apache.commons.math4.fraction.FractionTest.testSubtract',
                                                   'org.apache.commons.math4.fraction.FractionTest.testReciprocal',
                                                   'org.apache.commons.math4.fraction.FractionTest.testGetReducedFraction',
                                                   'org.apache.commons.math4.fraction.FractionTest.testDivide',
                                                   'org.apache.commons.math4.fraction.FractionTest.testNegate',
                                                   'org.apache.commons.math4.fraction.FractionTest.testConstructor',
                                                   'org.apache.commons.math4.util.CombinatoricsUtilsTest.testStirlingS2Overflow',
                                                   'org.apache.commons.math4.util.CombinatoricsUtilsTest.testFactorialFail'})






if __name__ == '__main__':
    unittest.main()
