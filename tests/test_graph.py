import pytest

from oval_graph.oval_node import OvalNode

import tests.any_test_help


def test_bad_tree():
    with pytest.raises(Exception, match="don't has any child"):
        assert bad_tree()


def test_bad_tree_only_and_no_child():
    with pytest.raises(Exception, match="has child!"):
        assert tree_only_and()


def test_bad_tree_only_or_no_child():
    with pytest.raises(Exception, match="has child!"):
        assert tree_only_or()


def test_bad_tree_with_bad_type_of_node():
    with pytest.raises(Exception, match="err- unknown type"):
        assert tree_with_bad_type()


def test_bad_tree_with_bad_value_of_operator():
    with pytest.raises(Exception, match="err- unknown operator"):
        assert tree_with_bad_value_of_operator()


def test_bad_tree_with_bad_value_of_value():
    with pytest.raises(Exception, match="err- unknown value"):
        assert tree_with_bad_value_of_value()


def test_bad_tree_with_bad_value_of_negation():
    with pytest.raises(Exception, match="negation is bool"):
        assert tree_with_bad_value_of_negation()


# degenered trees


def bad_tree():
    """
         t
         |
        and
         |
         t
    """
    t = OvalNode(
        1, "value", "true", False, None, [
           OvalNode(
               2, "operator", "and", False, None, [
                   OvalNode(
                       3, "value", "true", False, None)])])
    return


def tree_only_or():
    """
        or
    """
    Tree = OvalNode(1, "operator", 'or', False, None)
    return


def tree_only_and():
    """
        and
    """
    Tree = OvalNode(1, "operator", 'and', False, None)
    return


def tree_with_bad_value_of_operator():
    Tree = OvalNode(1, "operator", 'nad', False, None)
    return


def tree_with_bad_value_of_value():
    Tree = OvalNode(1, "value", 'and', False, None)
    return


def tree_with_bad_type():
    Tree = OvalNode(1, "car", 'and', False, None)
    return


def tree_with_bad_value_of_negation():
    Tree = OvalNode(1, "operator", "true", False, None, [
        OvalNode(2, "value", 'true', "random_string", None)])
    return

# normal trees


def test_UPPERCASETree():
    t = OvalNode(
        1, "OPERATOR", "AND", False, None, [
           OvalNode(
               2, "VALUE", "TRUE", False, None), OvalNode(
               3, "VALUE", "NOTAPPL", False, None)])


def test_bigOvalTree():
    Tree = OvalNode(1, 'operator', 'and', False, None, [
        OvalNode(2, 'value', "false", False, None),
        OvalNode(3, 'operator', "xor", False, None, [
            OvalNode(4, 'value', 'true', False, None),
            OvalNode(5, 'operator', 'one', False, None, [
                OvalNode(6, 'value', 'noteval', False, None),
                OvalNode(7, 'value', 'true', False, None),
                OvalNode(8, 'value', 'notappl', False, None)
            ]
            ),
            OvalNode(9, 'value', 'error', False, None)
        ]
        ),
        OvalNode(10, 'operator', 'or', False, None, [
            OvalNode(11, 'value', "unknown", False, None),
            OvalNode(12, 'value', "true", False, None)
        ]
        )
    ]
    )

    test_data_src = 'test_data/bigOvalTree.json'
    dict_of_tree = tests.any_test_help.any_get_test_data_json(test_data_src)
    tests.any_test_help.any_test_treeEvaluation_with_tree(Tree, "false")
    tests.any_test_help.any_test_tree_to_dict_of_tree(Tree, dict_of_tree)
    tests.any_test_help.find_any_node(Tree, 5)
    tests.any_test_help.any_test_dict_to_tree(dict_of_tree)

###################################################


def test_treeRepr():
    """
        and
         |
         f
    """
    Tree = OvalNode(1, 'operator', 'and', False, None, [
        OvalNode(2, 'value', "false", False, None)
    ]
    )
    assert str(Tree) == "and"


def test_add_to_tree():
    """
        and
         |
         f
    """

    test_data_src = 'test_data/add_to_tree.json'
    dict_of_tree = tests.any_test_help.any_get_test_data_json(test_data_src)

    Tree = OvalNode(1, 'operator', 'and', False, None, [
        OvalNode(2, 'value', "false", False, None)
    ]
    )
    Tree1 = OvalNode(3, 'value', "true", False, None)
    Tree.add_to_tree(1, Tree1)
    assert Tree.save_tree_to_dict() == dict_of_tree


def test_ChangeValueTree():
    """
        and
        /|\
       t t or
          / \
         f   t
    """
    Tree = OvalNode(1, 'operator', 'and', False, None, [
        OvalNode(2, 'value', "true", False, None),
        OvalNode(3, 'value', "false", False, None),
        OvalNode(4, 'operator', 'or', False, None, [
            OvalNode(5, 'value', "false", False, None),
            OvalNode(6, 'value', "true", False, None)
        ]
        )
    ]
    )

    Tree.change_tree_value(3, "true")
    tests.any_test_help.any_test_treeEvaluation_with_tree(Tree, "true")


def test_node_operator_negate():
    """
        !and
         |
         f
    """
    Tree = OvalNode(1, 'operator', 'and', True, None, [
        OvalNode(2, 'value', "false", False, None)
    ]
    )
    tests.any_test_help.any_test_treeEvaluation_with_tree(Tree, "true")


def test_node_operator_negate1():
    """
        and
         |
         t
    """
    Tree = OvalNode(1, 'operator', 'and', False, None, [
        OvalNode(2, 'value', "true", False, None)
    ]
    )
    tests.any_test_help.any_test_treeEvaluation_with_tree(Tree, "true")


def test_node_operator_negate1():
    """
        and
         |
         t
    """
    Tree = OvalNode(1, 'operator', 'and', False, None, [
        OvalNode(2, 'value', "true", False, None)
    ]
    )
    tests.any_test_help.any_test_treeEvaluation_with_tree(Tree, "true")


def test_node_value_negate():
    """
        and
         |
         !f
    """
    Tree = OvalNode(1, 'operator', 'and', False, None, [
        OvalNode(2, 'value', "True", True, None)
    ]
    )
    tests.any_test_help.any_test_treeEvaluation_with_tree(Tree, "true")


def test_node_value_negate1():
    """
        and
         |
         !t
    """
    Tree = OvalNode(1, 'operator', 'and', False, None, [
        OvalNode(2, 'value', "false", True, None)
    ]
    )
    tests.any_test_help.any_test_treeEvaluation_with_tree(Tree, "false")
