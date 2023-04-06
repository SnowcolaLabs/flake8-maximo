import ast
from typing import Set

from flake8_maximo import Plugin


def _resuts(s: str) -> Set[str]:
    tree = ast.parse(s)
    plugin = Plugin(tree)
    return {f"{line}:{col} {msg}" for line, col, msg, _ in plugin.run()}


def test_trivia_case():
    assert _resuts("") == set()
