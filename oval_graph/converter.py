import re
import uuid

from .oval_node import OvalNode


class Converter():
    def __init__(self, tree):
        self.VALUE_TO_BOOTSTRAP_COLOR = {
            "true": "text-success",
            "false": "text-danger",
            "error": "text-dark",
            "unknown": "text-dark",
            "noteval": "text-dark",
            "notappl": "text-dark"
        }

        self.VALUE_TO_ICON = {
            "true": "glyphicon glyphicon-ok text-success",
            "false": "glyphicon glyphicon-remove text-danger",
            "error": "glyphicon glyphicon-question-sign text-dark",
            "unknown": "glyphicon glyphicon-question-sign text-dark",
            "noteval": "glyphicon glyphicon-question-sign text-dark",
            "notappl": "glyphicon glyphicon-question-sign text-dark"
        }

        if isinstance(tree, OvalNode):
            self.tree = tree
        else:
            raise ValueError('err - this is not tree created from OvalNodes')

    def _get_node_icon(self):
        values = self._get_node_style()
        return dict(
            color=self.VALUE_TO_BOOTSTRAP_COLOR[values['negation_color']],
            icon=self.VALUE_TO_ICON[values['test_value']],
        )

    def get_comment(self):
        if self.tree.comment is not None:
            return str(self.tree.comment)
        return ""

    def to_JsTree_dict(self):
        icons = self._get_node_icon()
        label = self._get_label()
        out = {
            'text': (str(label['negation'] if label['negation'] else "") +
                     ' <strong><span class="' + icons['color'] + '">' +
                     label['str'] + '</span></strong>' +
                     ' <i>' + self.get_comment() + '</i>'
                     ),
            "icon": icons['icon'],
            "state": {
                "opened": True}}
        if self.tree.children:
            out['children'] = [Converter(child).to_JsTree_dict()
                               for child in self.tree.children]
        return out

    def _get_node_style(self):
        value = self.tree.evaluate_tree()
        out_color = None
        if value is None:
            if self.tree.negation:
                out_color = self.negate_bool(self.tree.value)
            else:
                out_color = self.tree.value
            value = self.tree.value
        else:
            if self.tree.negation:
                out_color = self.negate_bool(value)
            else:
                out_color = value
        return dict(
            negation_color=out_color,
            test_value=value,
        )

    def get_negation_character(self, value):
        return ('<strong><span class="' +
                self.VALUE_TO_BOOTSTRAP_COLOR[value] +
                '">&not;</strong></span>')

    def _get_label(self):
        out = dict(negation=None, str="")
        if self.tree.node_type == 'value':
            if self.tree.negation:
                out['negation'] = self.get_negation_character(self.tree.value)
            out['str'] = re.sub(
                '(oval:ssg-test_|oval:ssg-)|(:def:1|:tst:1)', '', str(self.tree.node_id))
            return out
        else:
            if str(self.tree.node_id).startswith('xccdf_org'):
                out['str'] = re.sub(
                    '(xccdf_org.ssgproject.content_)', '', str(
                        self.tree.node_id))
                return out
            else:
                if self.tree.negation:
                    out['negation'] = self.get_negation_character(
                        self.tree.evaluate_tree())
                out['str'] = (self.tree.value).upper()
                return out

    def negate_bool(self, value):
        values = {
            "true": "false",
            "false": "true",
        }
        return values[str(value)]
