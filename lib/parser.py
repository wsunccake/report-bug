import datetime
import re
import time

from robot.api import ExecutionResult


class ReportParser:
    _tests = []

    def __init__(self, input_xml):
        self.result = ExecutionResult(input_xml)
        self.all_test_cases = self._flatten_test_case(self.result)
        self.failed_test_cases = [tc for tc in self.all_test_cases if tc.status in set(['FAIL'])]
        self.passed_test_cases = [tc for tc in self.all_test_cases if tc.status in set(['PASS'])]

    def _flatten_test_case(self, result):
        if not (getattr(result, 'suites', None) is None):
            for suite in result.suites:
                self._flatten_test_case(suite)

        if not (getattr(result, 'suite', None) is None):
            self._flatten_test_case(getattr(result, 'suite'))

        for test in getattr(result, 'tests', []):
            self._tests.append(test)

        return self._tests


class ParserTool:
    @staticmethod
    def get_failed_test_keyword(test_keyword, results):
        if not test_keyword.passed:
            for kw in test_keyword.keywords.all:
                ParserTool.get_failed_test_keyword(kw, results)
            if len(test_keyword.keywords.all) == 0:
                results.append((test_keyword.name, test_keyword.messages))
                return
        return

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
    def find_parent_attribute(testcase, parent_key, attribute):
        pass

    @staticmethod
    def report_time_to_timestamp(report_time):
        report_time = re.sub(r'\..*$', '', report_time)
        report_timestamp = time.mktime(time.strptime(report_time, '%Y%m%d %H:%M:%S'))
        return report_timestamp

    @staticmethod
    def simple_report(test_cases, options=[]):
        passed_number = 0
        failed_number = 0
        testcase_lines = []
        start_timestamp = float("inf")
        end_timestamp = - float("inf")

        for tc in test_cases:
            if tc.passed:
                passed_number += 1
            else:
                failed_number += 1

            if 'with_testcase' in options:
                testcase_lines.append('{:60.60s}\t[{}]'.format(tc.name, tc.status))

                if 'with_time' in options:
                    testcase_lines[-1] = testcase_lines[-1] + '\t{}\t{}'.format(tc.starttime, tc.endtime)

                if 'with_error_message' in options:
                    if not tc.passed:
                        testcase_lines[-1] = testcase_lines[-1] + '\n{}\n'.format(tc.message)

                if 'with_failed_keyword' in options:
                    for kw in tc.keywords:
                        failed_results = []
                        if not kw.passed:
                            ParserTool.get_failed_test_keyword(kw, failed_results)
                            failed_kw = failed_results[0][0]
                            failed_message = '\n'.join(m.message for m in failed_results[0][1])
                            testcase_lines[-1] = testcase_lines[-1] + '\n{}\n{}\n'.format(failed_kw, failed_message)

            if 'with_time' in options:
                start_timestamp = min(start_timestamp, ParserTool.report_time_to_timestamp(tc.starttime))
                end_timestamp = max(end_timestamp, ParserTool.report_time_to_timestamp(tc.endtime))

        try:
            total_number = passed_number + failed_number
            passed_rate = round(passed_number * 100. / total_number, 1)
        except ZeroDivisionError:
            passed_rate = 0
        except Exception as e:
            print(e)

        report_content = 'total TCs: {:d}, passed TCs: {:d}, passed rate: {:.1f} %'.format(total_number, passed_number,
                                                                                           passed_rate)

        if 'with_time' in options:
            s = datetime.datetime.fromtimestamp(start_timestamp).strftime('%Y%m%d %H:%M:%S')
            e = datetime.datetime.fromtimestamp(end_timestamp).strftime('%Y%m%d %H:%M:%S')
            report_content = report_content + '\t{}\t{}'.format(s, e)

        if testcase_lines:
            report_content = '\n'.join(testcase_lines) + '\n' + report_content

        return report_content


if __name__ == '__main__':
    input_xml = '/tmp/output.xml'
    report_parser = ReportParser(input_xml)
    # print(report_parser.failed_test_cases)
    # print(report_parser.passed_test_cases)

    # opts = ['with_testcase', 'with_error_message']
    opts = ['with_testcase', 'with_failed_keyword']
    simple_report = ParserTool.simple_report(report_parser.failed_test_cases, opts)
    print(simple_report)
