from .utils import rf_test


def test_exclude_suffix(tmp_path):
    paths = "__pycache__/foo.pyc bar.pyc a".split()
    filter_rules = ["- *.pyc"]
    result = rf_test(tmp_path, filter_rules, paths)
    assert len(result.matches) == 3  # should be __pycache__, a, and .rsync-filter
    assert 'foo.pyc' not in result.names
    assert 'bar.pyc' not in result.names


def test_wildcard_anchor(tmp_path):
    paths = "a/1 bar/2 a/bat a/ban".split()
    filter_rules = ["- /b*"]
    result = rf_test(tmp_path, filter_rules, paths)
    assert len(result.matches) == len(".rsync_filter a a/1 a/bat a/ban".split())
    assert 'bar/2' not in result.names
    assert 'a/bat' in result.names
    assert 'a/ban' in result.names
