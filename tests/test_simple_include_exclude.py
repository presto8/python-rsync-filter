import os

from pathlib import Path
from types import SimpleNamespace

from rsyncfilter import RsyncFilter


def create_file(path: Path, contents: str = ""):
    "Returns SimpleNamespace(path, contents, size, sha256)"
    if not os.path.exists(path.parent):
        path.parent.mkdir()
    path.write_text(contents)
    return SimpleNamespace(path=path, contents=contents, size=len(contents))


def test_simple_include_exclude(tmp_path, tmpdir):
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
    files = ["x/file.txt", "x/y/file.txt", "x/y/zzz.txt", "x/z/file.txt"]
    for file in files:
        path = tmp_path / file
        create_file(path)

    content = [
        '+ x/\n'
        '+ x/y/\n'
        '+ x/y/file.txt\n'
        '- *\n'
    ]
    # TODO figure out why '\n'.join(content) doesn't work!?
    create_file(tmp_path / ".rsync-filter", contents=''.join(content))

    rf = RsyncFilter(tmp_path)
    matches = list(rf.scandir())
    assert len(matches) == 1
    assert matches[0].path.endswith('x/y/file.txt')

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

       Then  the  following  rsync  command  will transfer the file "x/y/file.txt" and the directories needed to hold it, resulting in the path
       "/tmp/x/y/file.txt" existing on the remote host:
 
           rsync -ai -f'+ x/' -f'+ x/y/' -f'+ x/y/file.txt' -f'- *' x host:/tmp/
 
       Aside: this copy could also have been accomplished using the -R option (though the 2 commands behave differently if  deletions  are  en‐
       abled):
 
           rsync -aiR x/y/file.txt host:/tmp/
 
       The following command does not need an include of the "x" directory because it is not a part of the transfer (note the traililng slash).
       Running this command would copy just "/tmp/x/file.txt" because the "y" and "z" dirs get excluded:
 
           rsync -ai -f'+ file.txt' -f'- *' x/ host:/tmp/x/
 
       This command would omit the zzz.txt file while copying "x" and everything else it contains:
 
           rsync -ai -f'- zzz.txt' x host:/tmp/
"""
