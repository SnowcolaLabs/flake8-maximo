import sys
import ast
from typing import Any, Generator, Tuple, Type, List, Union
from collections import defaultdict

if sys.version_info < (3, 8):
    import importlib_metadata
else:
    import importlib.metadata as importlib_metadata

import importlib.metadata



MAX100 = "MAX100 count() called on mboSet: {set_name} more than once"

class MboVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.mbo_sets: Dict[str] = {}
        self.mbo_count_calls: Dict[int] = defaultdict(int)
        self.problems: List[Tuple[int, int, str]] = []

    def visit_Assign(self, node: ast.Assign)-> None:
        if isinstance(node.value, ast.Call) and node.value.func.attr == "getMboSet":
            self.mbo_sets[node.targets[0].id] = node.value.args[0].value
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> bool:
        if not hasattr(node.func, "value"):
            self.generic_visit(node)
            return
        if self.is_mbo_count_call(node): 
            self.mbo_count_calls[node.func.value.id] += 1 
            if self.mbo_count_calls[node.func.value.id] > 1:
                self.problems.append((node.lineno, node.col_offset, MAX100.format(set_name=node.func.value.id)))
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self.visit_loop_body(node)
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self.visit_loop_body(node)
        self.generic_visit(node)
    

    def is_mbo_count_call(self, node):
        return hasattr(node.func, "value") and node.func.attr == 'count' and node.func.value.id in self.mbo_sets.keys()


class Plugin:
    name = __name__
    version = importlib_metadata.version(__name__)

    def __init__(self, tree: ast.AST) -> None:
        self._tree = tree

    def run(self) -> Generator[Tuple[int, int, str, Type[Any]], None, None]:
        mbo_visitor = MboVisitor()
        mbo_visitor.visit(self._tree)
        for line, col, msg in mbo_visitor.problems:
            yield line, col, msg, type(self)

