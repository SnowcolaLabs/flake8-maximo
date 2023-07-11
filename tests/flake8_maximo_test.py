import ast
from typing import Set

from flake8_maximo import Plugin

def _results(s):
    tree = ast.parse(s)
    plugin = Plugin(tree)
    return {"{line}:{col} {msg}".format(line=line, col=col+1, msg=msg) for line, col, msg, _ in plugin.run()}

def test_trivial():
    assert _results("""""") == set()

def test_MAX100_mbo_set_multiple_count_with_no_assignment():
    test_code = """
testSet = mbo.getMboSet('TESTSET')
if testSet.count() == 0:
    pass
if testSet.count() >3:
    pass
    """
    ret = _results(test_code)
    assert ret == {'3:4 MAX100 count() called on mboSet: testSet more than once','5:4 MAX100 count() called on mboSet: testSet more than once'}

def test_MAX101_mbo_set_count_in_for_loop():
    test_code = """
testSet = mbo.getMboSet('TESTSET')
for x in range(5):
    testSet.count()
    """
    ret = _results(test_code)
    assert ret == {'4:5 MAX101 count() called on mboSet: testSet within a loop'}

def test_MAX101_mbo_set_count_in_while_loop():
    test_code = """
testSet = mbo.getMboSet('TESTSET')
while True:
    testSet.count()
    """
    ret = _results(test_code)
    assert ret == {'4:5 MAX101 count() called on mboSet: testSet within a loop'}

def test_MAX102_literals_instead_of_mboConsts():
    test_code = 'mbo.setValue("ATGISFEATUREID",mbo.getString("ATANCESTORGISFEATUREID.GISFEATUREID"),2L)'
    ret = _results(test_code)
    assert ret == {'1:1 MAX102 Literal: 2L used instead of MboConstant'}

def test_MAX100_false_pos_on_same_symbol_different_functions():
    test_code = """
def abc():
    testSet = mbo.getMboSet('TESTSET')
    x = testSet.count()
def cde():
    testSet = mbo.getMboSet('TESTSET')
    x = testSet.count()
    """
    ret = _results(test_code)
    assert ret == set()
