import os
import subprocess
import tempfile
import webbrowser

from .._builder_html_graph import BuilderHtmlGraph
from ..exceptions import NotChecked
from .client import Client


class ClientHtmlOutput(Client):
    def __init__(self, args):
        super().__init__(args)
        self.out = self.arg.output
        self.part = self.get_src('../parts')
        if hasattr(self.arg, 'all_in_one'):
            self.all_in_one = self.arg.all_in_one
            self.all_rules = True if self.all_in_one else self.arg.all
            self.html_builder = BuilderHtmlGraph(self.part, self.arg.verbose, self.all_in_one)
        self.display_html = True if self.out is None else self.arg.display
        self.web_browsers = []

    @staticmethod
    def get_src(src):
        _dir = os.path.dirname(os.path.realpath(__file__))
        return str(os.path.join(_dir, src))

    @staticmethod
    def get_start_of_file_name():
        return 'graph-of-'

    def prepare_data(self, rules):
        out_src = []
        oval_tree_dict = dict()
        self._prepare_data(rules, oval_tree_dict, out_src)
        self.open_results_in_web_browser(out_src)
        return out_src

    def _put_to_dict_oval_trees(self, dict_oval_trees, rule):
        """
        The function inserts into dict_oval_trees a dictionary from
        the rule with the key as the rule id.
        """
        raise NotImplementedError

    def _prepare_data(self, rules, dict_oval_trees, out_src):
        for rule in rules['rules']:
            try:
                self._put_to_dict_oval_trees(dict_oval_trees, rule)
                if not self.all_in_one:
                    self._build_and_save_html(
                        dict_oval_trees,
                        self._get_src_for_one_graph(rule),
                        dict(rules=[rule]),
                        out_src
                    )
                    dict_oval_trees = {}
            except NotChecked as error:
                start_red_color = '\033[91m'
                end_red_color = '\033[0m'
                print(start_red_color + str(error) + end_red_color)
        if self.all_in_one:
            self._build_and_save_html(
                dict_oval_trees, self.get_save_src(
                    'rules' + self._get_date()), rules, out_src)

    def _build_and_save_html(self, dict_oval_trees, src, rules, out_src):
        self.html_builder.save_html(dict_oval_trees, src, rules)
        out_src.append(src)

    def _get_src_for_one_graph(self, rule):
        return self.get_save_src(rule + self._get_date())

    def get_save_src(self, rule):
        if self.out is not None:
            os.makedirs(self.out, exist_ok=True)
            return os.path.join(
                self.out,
                self.get_start_of_file_name() + rule + '.html')
        return os.path.join(
            tempfile.gettempdir(),
            self.get_start_of_file_name() + rule + '.html')

    def open_results_in_web_browser(self, paths_to_results):
        if self.display_html:
            try:
                self.web_browsers.append(
                    subprocess.Popen(["firefox", *paths_to_results]))
            except subprocess.CalledProcessError:
                default_web_browser_name = webbrowser.get().name
                self.web_browsers.append(
                    subprocess.Popen([default_web_browser_name, *paths_to_results]))

    def kill_web_browsers(self):
        for web_browser in self.web_browsers:
            web_browser.kill()

    @staticmethod
    def arg_all_in_one(parser):
        parser.add_argument(
            '-i',
            '--all-in-one',
            action="store_true",
            default=False,
            help="Processes all rules into one file.")

    @staticmethod
    def arg_display(parser):
        parser.add_argument(
            '-d',
            '--display',
            action="store_true",
            default=False,
            help="Enables opening a web browser with a graph, when is used --output.")
