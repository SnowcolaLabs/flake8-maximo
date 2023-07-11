import ast
from collections import defaultdict
import importlib_metadata


MAX100 = "MAX100 count() called on mboSet: {set_name} more than once"
MAX101 = "MAX101 count() called on mboSet: {set_name} within a loop"
MAX102 = "MAX102 Literal: {literal} used instead of MboConstant"


class MboVisitor(ast.NodeVisitor):
    def __init__(self, tree):
        self.tree = tree
        self.mbo_sets = {}
        self.mbo_count_calls = defaultdict(int)
        self.MAX100_counts = {}
        self.problems = []


    def visit_Assign(self, node):
        if isinstance(node.value, ast.Call) and not isinstance(node.value.func, ast.Name) and node.value.func.attr == "getMboSet":
            if node.targets and node.value.args:
                self.mbo_sets[node.targets[0].id] = node.value.args[0]

        self.generic_visit(node)

    def visit_Call(self, node):
        self.check_MAX102(node)
        self.generic_visit(node)

    def visit_For(self, node):
        self.check_MAX101(node)
        self.generic_visit(node)

    def visit_While(self, node):
        self.check_MAX101(node)
        self.generic_visit(node)

    def check_MAX100(self, node):
        self.check_counts(self.tree)
        self.record_count_errors()

    def check_counts(self, node):
        if isinstance(node, ast.FunctionDef):
            self.record_count_errors()
            self.MAX100_counts = {}  # Reset object counts for each function

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'count':
                obj_name = self.get_object_name(node.func.value)
                if obj_name and (obj_name in self.mbo_sets.keys()):
                    self.MAX100_counts[obj_name] = self.MAX100_counts.get(obj_name, [])
                    obj = self.MAX100_counts.get(obj_name, [])
                    obj.append((node.lineno, node.col_offset))

        # Traverse recursively
        for child_node in ast.iter_child_nodes(node):
            self.check_counts(child_node)

    def record_count_errors(self):
        if self.MAX100_counts:
            for obj_name, lines in self.MAX100_counts.items():
                if lines and (len(lines) > 1):
                    for line in lines: #returns all lines contributing to the problems
                        self.problems.append((line[0],line[1],MAX100.format(set_name=obj_name)))

    def get_object_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self.get_object_name(node.value)

    def check_MAX101(self, body):
        for node in ast.walk(body):
            if isinstance(node, ast.Call):
                if self.is_mbo_count_call(node):
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

    def run(self):
        self.visit(self.tree)
        self.check_MAX100(self.tree)
 

class Plugin:
    name = __name__
    version = importlib_metadata.version(__name__)

    def __init__(self, tree):
        self._tree = tree



    def run(self):
        mbo_visitor = MboVisitor(self._tree)
        mbo_visitor.run()

        for line, col, msg in mbo_visitor.problems:
            yield line, col, msg, type(self)

