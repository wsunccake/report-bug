#!/usr/bin/env python3
import json

from fire import Fire
from parser import ReportParser
from parser import ParserTool


def run(input_xml):
    report_parser = ReportParser(input_xml)
    test_entities = ParserTool.analyze_tests(report_parser.failed_tests)
    lines = ParserTool.extract_test_keyword_message(test_entities)
    json_data = json.dumps(lines, indent=4, separators=(',', ': '))
    print(json_data)


if __name__ == '__main__':
    Fire(run)
