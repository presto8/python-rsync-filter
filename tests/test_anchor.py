from .utils import rf_test

"""
A  pattern  that  starts  with  a  /  is  anchored to the start of the transfer
path instead of the end.  For example, /foo/** or /foo/bar/** match only
leading elements in the path.  If the rule is read from a per-directory filter
file, the transfer path being matched will begin at the level of the filter
file instead of the top of the transfer.  See  the  section  on  ANCHORING
INCLUDE/EXCLUDE PATTERNS for a full discussion of how to specify a pattern that
matches at the root of the transfer.
"""


def test_anchor_file(tmp_path):
    paths = "a/b b".split()
    filter_rules = ["- /b"]
    result = rf_test(tmp_path, filter_rules, paths)

    assert len(result.matches) == len("a a/b .rsync-filter".split())
    assert 'b' not in result.names
    assert 'a/b' in result.names


def test_anchor_dir_only(tmp_path):
    paths = "a/b b".split()
    filter_rules = ["- /b/"]
    result = rf_test(tmp_path, filter_rules, paths)

    assert len(result.matches) == len("a a/b b .rsync-filter".split())
    assert 'b' in result.names
    assert 'a/b' in result.names


def test_anchor_subdir(tmp_path):
    paths = "a/b b/a/b".split()
    filter_rules = ["- /a/b"]
    result = rf_test(tmp_path, filter_rules, paths)

    assert len(result.names) == len("a b b/a b/a/b .rsync-filter".split())
    assert 'a/b' not in result.names
