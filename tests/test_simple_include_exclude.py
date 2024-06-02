from .utils import rf_test


"""
SIMPLE INCLUDE/EXCLUDE EXAMPLE
    With the following file tree created on the sending side:

        mkdir x/
        touch x/file.txt
        mkdir x/y/
        touch x/y/file.txt
        touch x/y/zzz.txt
        mkdir x/z/
        touch x/z/file.txt

    Then  the  following  rsync  command  will transfer the file
    "x/y/file.txt" and the directories needed to hold it, resulting in the
    path "/tmp/x/y/file.txt" existing on the remote host:

        rsync -ai -f'+ x/' -f'+ x/y/' -f'+ x/y/file.txt' -f'- *' x host:/tmp/
"""

def test_simple_include_exclude_from_man_page(tmp_path):
    return
    paths = ["x/file.txt", "x/y/file.txt", "x/y/zzz.txt", "x/z/file.txt"]
    filter_rules = [
        '+ x/'
        '+ x/y/'
        '+ x/y/file.txt'
        '- *'
    ]
    result = rf_test(tmp_path, filter_rules, paths)
    assert len(result.matches) == 4  # should be x, x/y, x/y/file.txt and .rsync-filter
    assert 'x/y/file.txt' in result.names


"""
The following command does not need an include of the "x" directory because it
is not a part of the transfer (note the traililng slash). Running this command
would copy just "/tmp/x/file.txt" because the "y" and "z" dirs get excluded:

    rsync -ai -f'+ file.txt' -f'- *' x/ host:/tmp/x/

This command would omit the zzz.txt file while copying "x" and everything else
it contains:

    rsync -ai -f'- zzz.txt' x host:/tmp/
"""


def test_exclude_one_file(tmp_path):
    paths = "a b c".split()
    filter_rules = ["- b"]
    result = rf_test(tmp_path, filter_rules, paths)
    assert len(result.matches) == 3  # should be a, c, and .rsync-filter
    assert 'b' not in result.names


def test_exclude_one_dir(tmp_path):
    paths = "a/1 b/2 c".split()
    filter_rules = ["- b"]
    result = rf_test(tmp_path, filter_rules, paths)
    assert len(result.matches) == 4  # should be a, a/1, c, and .rsync-filter
    assert 'b' not in result.names
    assert '2' not in result.names


def test_exclude_all_include_one(tmp_path):
    paths = "a/1 b/2 c".split()
    filter_rules = ["+ .rsync-filter", "- *"]
    result = rf_test(tmp_path, filter_rules, paths)
    assert len(result.matches) == 1
    assert '.rsync-filter' in result.names
