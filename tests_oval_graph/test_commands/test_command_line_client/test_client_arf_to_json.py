import json
import os
import re
import tempfile
import time
import uuid

import pytest

from oval_graph.command_line_client.arf_to_json import ArfToJson

from ...test_tools import TestTools

PATCH_TO_REPORT = '../../global_test_data/ssg-fedora-ds-arf.xml'

EXPECTED_RULES_ID = [
    'xccdf_org.ssgproject.content_rule_package_abrt_removed',
    'xccdf_org.ssgproject.content_rule_package_sendmail_removed'
]


def get_client_arf_to_json(rule, optional_args=None):
    top_patch = os.path.dirname(os.path.realpath(__file__))
    patch = os.path.join(top_patch, PATCH_TO_REPORT)
    args = [patch, rule]
    if optional_args is not None:
        args.extend(optional_args)
    client = ArfToJson(args)
    client.load_file()
    return client


def get_date_regex():
    # Days 31, 30, 29
    date_regex_part_one = (
        r'(?:(?:31(\_)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\_)'
        r'(?:0?[1,3-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})'
    )
    # Feb 29
    date_regex_part_two = (
        r'(?:29(\_)(?:0?2)\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|'
        r'[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))'
    )
    # Others days
    date_regex_part_three = (
        r'(?:0?[1-9]|1\d|2[0-8])(\_)(?:(?:0?[1-9])|'
        r'(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})'
    )
    time_regex = (
        r'(?:[0-1]\d|2[0-3])'
        r'(?:\_([0-5]?\d))?'
        r'(?:\_([0-5]?\d))?'
    )
    regex_date = '(?:-{}-|-{}-|-{}-){}'.format(
        date_regex_part_one,
        date_regex_part_two,
        date_regex_part_three,
        time_regex
    )
    return regex_date


def test_expection_prepare_data():
    rule = 'non-existent_rule'
    client = get_client_arf_to_json(rule)
    rules = {'rules': [rule]}
    with pytest.raises(Exception, match='404'):
        assert client.prepare_data(rules)


@pytest.mark.parametrize("rule, error_pattern", [
    ('non-existent_rule', '404'),
    ('xccdf_org.ssgproject.content_rule_package_nis_removed', 'notselected'),
])
def test_expection_search_rules_id(rule, error_pattern):
    client = get_client_arf_to_json(rule)
    with pytest.raises(Exception, match=error_pattern):
        assert client.search_rules_id()


def test_prepare_json(capsys):
    rule = 'xccdf_org.ssgproject.content_rule_package_abrt_removed'
    client = get_client_arf_to_json(rule)
    rules = {'rules': [rule]}

    results_src = client.prepare_data(rules)
    assert not results_src

    captured = capsys.readouterr()
    regex_date = get_date_regex()
    out = re.sub(regex_date, "-REPLACE_DATE", captured.out)
    assert out == (
        '{\n'
        '    "xccdf_org.ssgproject.content_rule_package_abrt_removed-REPLACE_DATE": {\n'
        '        "node_id": "xccdf_org.ssgproject.content_rule_package_abrt_removed",\n'
        '        "type": "operator",\n'
        '        "value": "and",\n'
        '        "negation": false,\n'
        '        "comment": "Package abrt Removed",\n'
        '        "tag": "Rule",\n'
        '        "test_result_details": null,\n'
        '        "child": [\n'
        '            {\n'
        '                "node_id": "oval:ssg-package_abrt_removed:def:1",\n'
        '                "type": "operator",\n'
        '                "value": "and",\n'
        '                "negation": false,\n'
        '                "comment": "The RPM package abrt should be removed.",\n'
        '                "tag": "Definition",\n'
        '                "test_result_details": null,\n'
        '                "child": [\n'
        '                    {\n'
        '                        "node_id": "oval:ssg-test_package_abrt_removed:tst:1",\n'
        '                        "type": "value",\n'
        '                        "value": "false",\n'
        '                        "negation": false,\n'
        '                        "comment": "package abrt is removed",\n'
        '                        "tag": "Test",\n'
        '                        "test_result_details": {\n'
        '                            "id": "oval:ssg-test_package_abrt_removed:tst:1",\n'
        '                            "comment": "package abrt is removed",\n'
        '                            "objects": [\n'
        '                                {\n'
        '                                    "oval:ssg-obj_package_abrt_removed:obj:1":'
        ' "complete",\n'
        '                                    "rpminfo_object": {\n'
        '                                        "name": "abrt",\n'
        '                                        "arch": "x86_64",\n'
        '                                        "epoch": "(none)",\n'
        '                                        "release": "2.fc30",\n'
        '                                        "version": "2.12.0",\n'
        '                                        "evr": "0:2.12.0-2.fc30",\n'
        '                                        "signature_keyid": "ef3c111fcfc659b9",\n'
        '                                        "extended_name":'
        ' "abrt-0:2.12.0-2.fc30.x86_64"\n'
        '                                    }\n'
        '                                }\n'
        '                            ]\n'
        '                        },\n'
        '                        "child": null\n'
        '                    }\n'
        '                ]\n'
        '            }\n'
        '        ]\n'
        '    }\n'
        '}\n')


def test_prepare_json_and_save_in_defined_destination():
    rule = 'xccdf_org.ssgproject.content_rule_package_abrt_removed'
    file_name = str(uuid.uuid4()) + ".json"
    args = ["--output",
            os.path.join(tempfile.gettempdir(), file_name)]
    client = get_client_arf_to_json(rule, args)
    rules = {'rules': [rule]}
    results_src = client.prepare_data(rules)
    TestTools.compare_results_json(results_src[0])


def test_prepare_graph_with_not_selected_rule(capsys):
    rule = 'xccdf_org.ssgproject.content_rule_package_nis_removed'
    client = get_client_arf_to_json(rule)
    rules = {'rules': [rule]}
    client.prepare_data(rules)
    captured = capsys.readouterr()
    assert 'notselected' in captured.out


@pytest.mark.parametrize("file_src, result", [
    ('../test_data/empty_file.json', True),
    ('../test_data/referenc_result_data_json.json', False),
])
def test_file_is_empty(file_src, result):
    rule = 'xccdf_org.ssgproject.content_rule_package_abrt_removed'
    file_name = str(uuid.uuid4()) + ".json"
    args = ["--output",
            os.path.join(tempfile.gettempdir(), file_name)]
    client = get_client_arf_to_json(rule, args)

    top_patch = os.path.dirname(os.path.realpath(__file__))
    patch = os.path.join(top_patch, file_src)

    assert client.file_is_empty(patch) == result


def test_creation_json_with_two_more_rule():
    rule = 'xccdf_org.ssgproject.content_rule_package_abrt_removed'
    file_name = str(uuid.uuid4()) + ".json"
    args = ["--output",
            os.path.join(tempfile.gettempdir(), file_name)]
    client = get_client_arf_to_json(rule, args)
    rules = {'rules': [rule]}
    result_src = client.prepare_data(rules)

    time.sleep(1)  # wait for change time in saved rule name

    file_name = str(uuid.uuid4()) + ".json"
    args = ["--output", result_src[-1]]
    client1 = get_client_arf_to_json(rule, args)
    result_src_second_rule = client1.prepare_data(rules)

    assert result_src == result_src_second_rule

    data = None
    with open(result_src[-1], 'r') as file_:
        data = json.load(file_)
    rules_id = list(data.keys())

    assert len(rules_id) == 2
    assert data[rules_id[0]] == data[rules_id[1]]

    referenc_result = TestTools.get_data_json(
        'test_commands/test_data/referenc_result_data_json.json')
    assert referenc_result[
        "xccdf_org.ssgproject.content_rule_package_abrt_removed"] == data[rules_id[0]]


def test_creation_json_two_selected_rules():
    rule = 'xccdf_org.ssgproject.content_rule_package_abrt_removed'
    rule_1 = 'xccdf_org.ssgproject.content_rule_disable_host_auth'
    file_name = str(uuid.uuid4()) + ".json"
    args = ["--output",
            os.path.join(tempfile.gettempdir(), file_name)]
    client = get_client_arf_to_json(rule, args)
    rules = {'rules': [rule, rule_1]}
    result_src = client.prepare_data(rules)

    data = None
    with open(result_src[-1], 'r') as file_:
        data = json.load(file_)
    rules_id = list(data.keys())
    assert len(rules_id) == 2

    referenc_result = TestTools.get_data_json(
        'test_commands/test_data/referenc_result_data_json.json')
    assert referenc_result[
        "xccdf_org.ssgproject.content_rule_package_abrt_removed"] == data[rules_id[0]]
    assert rule_1 in rules_id[1]


@pytest.mark.parametrize("args, result", [
    (
        ["--show-not-selected-rules"],
        EXPECTED_RULES_ID,
    ),
    (
        ["--show-not-selected-rules", "--show-failed-rules"],
        [EXPECTED_RULES_ID[0]],
    ),
])
def test_get_questions_with_parameters(capsys, args, result):
    pytest.importorskip("inquirer")
    rule = r'_package_\w+_removed'
    client = get_client_arf_to_json(rule, args)
    TestTools.get_questions_not_selected(capsys, client, result)


def test_get_questions_with_option_show_failed_rules():
    pytest.importorskip("inquirer")
    rule = r'_package_\w+_removed'
    client = get_client_arf_to_json(rule, ["--show-failed-rules"])
    TestTools.get_questions_with_option_show_failed_rules(client)


def test_get_questions():
    pytest.importorskip("inquirer")
    rule = r'_package_\w+_removed'
    client = get_client_arf_to_json(rule)
    out = client.get_questions()[0].choices
    assert out == EXPECTED_RULES_ID


@pytest.mark.parametrize("part_of_id_rule, result", [
    ('xccdf_org.ssgproject.', 184),
    (r'_package_\w+_removed', 2),
    ('fips', 1),
    ('audit', 110),
    ('password', 15),
])
def test_search_rules_id(part_of_id_rule, result):
    client = get_client_arf_to_json(part_of_id_rule)
    assert len(client.search_rules_id()) == result