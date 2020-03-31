import datetime
import re
import time

from robot.api import ExecutionResult


class ReportParser:
    _tests = []
    _suites = []

    def __init__(self, input_xml):
        self.result = ExecutionResult(input_xml)
        self.all_tests, self.all_suites = self._flatten_test_case(self.result)
        self.failed_tests = [tc for tc in self.all_tests if tc.status in set(['FAIL'])]
        self.passed_tests = [tc for tc in self.all_tests if tc.status in set(['PASS'])]

        self.failed_suites = [s for s in self.all_suites if s.status in set(['FAIL'])]
        self.passed_suites = [s for s in self.all_suites if s.status in set(['PASS'])]

    def _flatten_test_case(self, result):
        if not (getattr(result, 'suites', None) is None):
            for suite in result.suites:
                self._suites.append(suite)
                self._flatten_test_case(suite)

        if not (getattr(result, 'suite', None) is None):
            self._flatten_test_case(getattr(result, 'suite'))

        for test in getattr(result, 'tests', []):
            self._tests.append(test)

        return self._tests, self._suites


class TestEntity:
    def __init__(self, test):
        self.test = test
        self.failed_keywords = []

    def __str__(self):
        return f'test case: {self.test.name}, [{self.test.status}]'


class SuiteEntity:
    def __init__(self, suite):
        self.suite = suite
        self.tests = []
        self.failed_tests = []
        self.failed_keywords = []


class ParserTool:
    DEFAULT_REASON_ID = 0

    @staticmethod
    def get_failed_test_keyword(test_keyword, results):
        if not test_keyword.passed:
            for kw in test_keyword.keywords.all:
                ParserTool.get_failed_test_keyword(kw, results)
            if len(test_keyword.keywords.all) == 0:
                results.append(test_keyword)
                return
        return

    @staticmethod
    def analyze_tests(test_cases):
        test_entities = []

        for tc in test_cases:
            test_entity = TestEntity(tc)

            for kw in tc.keywords:
                failed_results = []
                if not kw.passed:
                    ParserTool.get_failed_test_keyword(kw, failed_results)
                    test_entity.failed_keywords = failed_results

            test_entities.append(test_entity)

        return test_entities

    @staticmethod
    def analyze_suites(suites):
        suite_entities = []

        for suite in suites:
            suite_entity = SuiteEntity(suite)

            for kw in suite.keywords:
                if not kw.passed:
                    suite_entity.failed_keywords.append(kw)

            for tc in suite.tests:
                if not tc.status:
                    suite_entity.failed_tests.append(tc)

            suite_entities.append(suite)

        return suite_entities

    # @staticmethod
    # def show_testcase(testcase):
    #     print ('TC: {}, status: {}'.format(testcase.name, testcase.status))
    #     print ('start: {}, end: {}'.format(testcase.starttime, testcase.endtime))
    #     print testcase.message
    #     print testcase.passed, testcase.id
    #
    # @staticmethod
    # def show_keyword(keyword):
    #     print ('keyword: {}, status: {}'.format(keyword.name, keyword.status))
    #     print ('start: {}, end: {}'.format(keyword.starttime, keyword.endtime))
    #     print keyword.passed, keyword.id, keyword.type
    #
    # @staticmethod
    # def find_failed_keyword(testcase):
    #     for keyword in getattr(testcase, 'keywords', []):
    #         if keyword.passed is False:
    #             return keyword
    #
    # @staticmethod
    # def filter_by_method0(testcases, attribute, method=None):
    #     result_dict = {}
    #     if method is None:
    #         method = ParserTool.same_attribute_method
    #     for tc in testcases:
    #         if method(tc, result_dict, attribute):
    #             result_dict[getattr(tc, attribute)].append(tc)
    #         else:
    #             result_dict[getattr(tc, attribute)] = [tc]
    #
    #     return result_dict
    #
    # @staticmethod
    # def filter_by_method(testcases, attribute, method=None):
    #     result_dict = {}
    #     if method is None:
    #         method = ParserTool.same_attribute_method
    #     for tc in testcases:
    #         if method(tc, result_dict, attribute):
    #             result_dict[tc].append(getattr(tc, attribute))
    #         else:
    #             result_dict[tc] = [getattr(tc, attribute)]
    #
    #     return result_dict
    #
    # @staticmethod
    # def same_attribute_method(tc, result_dict, attribute):
    #     if getattr(tc, attribute) in result_dict:
    #         return True
    #     else:
    #         return False
    #
    # @staticmethod
    # def filter_by_same_suite(testcases):
    #     return ParserTool.filter_by_method(testcases, 'parent', ParserTool.same_attribute_method)
    #
    # @staticmethod
    # def filter_by_same_message(testcases):
    #     return ParserTool.filter_by_method(testcases, 'message', ParserTool.same_attribute_method)
    #
    # @staticmethod
    # def filter_by_same_source(testcases):
    #     result_dict = {}
    #     for tc in testcases:
    #         if not (getattr(tc, 'parent', False) is False):
    #             source = getattr(tc.parent, 'source')
    #             if source in result_dict:
    #                 result_dict[source].append(tc)
    #             else:
    #                 result_dict[source] = [tc]
    #
    #     return result_dict

    @staticmethod
    def extract_test_keyword_message(test_entities):
        lines = []

        for t in test_entities:
            test = t.test
            keywords = [k.name for k in t.failed_keywords]
            keyword_messages = [k.messages for k in t.failed_keywords]

            failed_messages = []
            for items in keyword_messages:
                message = ''
                for i in items:
                    message += '\n' + i.message
                failed_messages.append(message)

            lines.append({'test': test.name, 'test_message': test.message,
                          'keywords': keywords, 'keyword_messages': failed_messages,
                          'reason_id': ParserTool.DEFAULT_REASON_ID})

        return lines

    @staticmethod
    def find_parent_attribute(testcase, parent_key, attribute):
        pass

    @staticmethod
    def report_time_to_timestamp(report_time):
        report_time = re.sub(r'\..*$', '', report_time)
        report_timestamp = time.mktime(time.strptime(report_time, '%Y%m%d %H:%M:%S'))
        return report_timestamp

    @staticmethod
    def text_report(test_entities, options=[]):
        passed_number = 0
        failed_number = 0
        testcase_lines = []
        start_timestamp = float("inf")
        end_timestamp = - float("inf")

        for entity in test_entities:
            if entity.test.passed:
                passed_number += 1
            else:
                failed_number += 1

            if 'with_testcase' in options:
                testcase_lines.append('{:60.60s}\t[{}]'.format(entity.test.name, entity.test.status))

                if 'with_time' in options:
                    testcase_lines[-1] = testcase_lines[-1] + '\t{}\t{}'.format(entity.test.starttime,
                                                                                entity.test.endtime)

                if 'with_error_message' in options:
                    if not entity.test.passed:
                        testcase_lines[-1] = testcase_lines[-1] + '\n{}\n'.format(entity.test.message)

                if 'with_failed_keyword' in options:
                    for kw in entity.failed_keywords:
                        message = '\n'.join(m.message for m in kw.messages)
                        testcase_lines[-1] = testcase_lines[-1] + '\n{}\n{}\n'.format(kw.name, message)

            if 'with_time' in options:
                start_timestamp = min(start_timestamp, ParserTool.report_time_to_timestamp(entity.test.starttime))
                end_timestamp = max(end_timestamp, ParserTool.report_time_to_timestamp(entity.test.endtime))

        try:
            total_number = passed_number + failed_number
            passed_rate = round(passed_number * 100. / total_number, 1)
        except ZeroDivisionError:
            passed_rate = 0
        except Exception as e:
            print(e)

        report_content = ''
        if 'with_pass_rate' in options:
            report_content = 'total TCs: {:d}, passed TCs: {:d}, passed rate: {:.1f} %'.format(total_number,
                                                                                               passed_number,
                                                                                               passed_rate)
        if testcase_lines:
            report_content = '\n'.join(testcase_lines) + '\n' + report_content

        return report_content

    @staticmethod
    def suite_report(suite_entities):
        pass


if __name__ == '__main__':
    input_xml = '/tmp/output.xml'
    report_parser = ReportParser(input_xml)
    # print(report_parser.failed_test_cases)
    # print(report_parser.passed_test_cases)

    test_entities = ParserTool.analyze_tests(report_parser.all_tests)

    # opts = ['with_testcase', 'with_error_message']
    # opts = ['with_testcase', 'with_failed_keyword', 'with_error_message', 'with_time', 'with_pass_rate']
    opts = ['with_testcase', 'with_failed_keyword', 'with_error_message', 'with_pass_rate']
    text = ParserTool.text_report(test_entities, opts)
    print(text)

    # suite_entities = ParserTool.analyze_suites(report_parser.all_suites)
