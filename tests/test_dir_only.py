import os
from .utils import rf_helper, rf_test

"""
A pattern that ends with a / only matches a directory, not a regular file, symlink, or device.
"""

filter_rules = [
    "- b/"
]


def test_dir_only_positive(tmp_path, tmpdir):
    paths = "a/ b/".split()
    result = rf_test(tmp_path, filter_rules, paths)

    assert len(result.matches) == 2
    assert 'b' not in result.names
    assert 'a' in result.names


def test_dir_only_negative_regular_file(tmp_path, tmpdir):
    "Don't match a regular file"
    paths = "a b".split()
    result = rf_test(tmp_path, filter_rules, paths)
    print(result)

    assert len(result.matches) == 3
    assert 'b' in result.names
    assert 'a' in result.names


def test_dir_only_negative_symlink(tmp_path, tmpdir):
    "Don't match a symlink"
    for file_entry in "a b".split():
        (tmp_path / file_entry).symlink_to("/")

    result = rf_helper(tmp_path, filter_rules)
    assert len(result.matches) == 3
    assert 'b' in result.names
    assert 'a' in result.names


def test_dir_only_negative_device(tmp_path, tmpdir):
    "Don't match a device"
    for file_entry in "a b".split():
        os.mknod(tmp_path / file_entry)

    result = rf_helper(tmp_path, filter_rules)
    assert len(result.matches) == 3
    assert 'b' in result.names
    assert 'a' in result.names
