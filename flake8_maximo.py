import ast
from collections import defaultdict
import importlib_metadata


MAX100 = "MAX100 count() called on mboSet: {set_name} more than once"
MAX101 = "MAX101 count() called on mboSet: {set_name} within a loop"
MAX102 = "MAX102 Literal: {literal} used instead of MboConstant"


class MboVisitor(ast.NodeVisitor):
    def __init__(self):
        self.mbo_sets = {}
        self.mbo_count_calls = defaultdict(int)
        self.problems = []

    def visit_Assign(self, node):
        if isinstance(node.value, ast.Call) and not isinstance(node.value.func, ast.Name) and node.value.func.attr == "getMboSet":
            print(node.lineno)
            self.mbo_sets[node.targets[0].id] = node.value.args[0]
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        print(node)

    def visit_Call(self, node):
        self.check_MAX100(node)
        self.check_MAX102(node)
        self.generic_visit(node)

    def visit_For(self, node):
        self.check_MAX101(node)
        self.generic_visit(node)

    def visit_While(self, node):
        self.check_MAX101(node)
        self.generic_visit(node)

    def check_MAX100(self, node):
        if not hasattr(node.func, "value"):
            return
        if self.is_mbo_count_call(node):
            self.mbo_count_calls[node.func.value.id] += 1
            if self.mbo_count_calls[node.func.value.id] > 1:
                self.problems.append(
                    (
                        node.lineno,
                        node.col_offset,
                        MAX100.format(set_name=node.func.value.id),
                    )
                )

    def check_MAX101(self, body):
        for node in ast.walk(body):
            if isinstance(node, ast.Call):
                if self.is_mbo_count_call(node):  # self.visit_Call(node):
                    self.problems.append(
                        (
                            node.lineno,
                            node.col_offset,
                            MAX101.format(set_name=node.func.value.id),
                        )
                    )

    def check_MAX102(self, node):
        if not hasattr(node.func, "value"):
            return
        if not hasattr(node.func.value, "id"):
            return
        if isinstance(node.func.value.id, str) and 'mbo' in node.func.value.id.lower():
            for arg in node.args:
                if isinstance(arg, ast.Num):
                    if type(arg.n) == long:
                        self.problems.append((node.lineno, node.col_offset, MAX102.format(literal="{}L".format(arg.n))))

    def is_mbo_count_call(self, node):
        try:
            res = (
            hasattr(node.func, "value")
            and node.func.attr == "count"
            and node.func.value.id in self.mbo_sets.keys()
        )
        except AttributeError as e:
            return False
        return res

class Plugin:
    name = __name__
    version = importlib_metadata.version(__name__)

    def __init__(self, tree):
        self._tree = tree

    def run(self):
        mbo_visitor = MboVisitor()

        mbo_visitor.visit(self._tree)
        print(mbo_visitor.mbo_count_calls)
        print(mbo_visitor.mbo_sets)
        for line, col, msg in mbo_visitor.problems:
            yield line, col, msg, type(self)
