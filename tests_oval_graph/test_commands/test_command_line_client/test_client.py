import os

import pytest

from oval_graph.command_line_client.client import Client

PATCH_TO_REPORT = '../../global_test_data/ssg-fedora-ds-arf.xml'


def get_client(rule, optional_args=None):
    top_patch = os.path.dirname(os.path.realpath(__file__))
    patch = os.path.join(top_patch, PATCH_TO_REPORT)
    args = [patch, rule]
    if optional_args is not None:
        args.extend(optional_args)
    return Client(args)


def test_search_rules_id_not_implemented_error():
    part_of_id_rule = 'xccdf_org.ssgproject.'
    client = get_client(part_of_id_rule)
    with pytest.raises(NotImplementedError):
        assert client.search_rules_id()


def test_get_questions_not_implemented_error():
    regex = r'_package_\w+_removed'
    client = get_client(regex)
    with pytest.raises(NotImplementedError):
        assert client.get_questions()[0].choices


def test_get_only_fail_rules_not_implemented_error():
    part_of_id_rule = 'xccdf_org.ssgproject.'
    client = get_client(part_of_id_rule)
    with pytest.raises(NotImplementedError):
        assert client.get_only_fail_rule(['rule-id'])