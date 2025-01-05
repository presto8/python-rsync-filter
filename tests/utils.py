import os
from pathlib import Path
from rsyncfilter import RsyncFilter
from types import SimpleNamespace


def create_file(path: Path, contents: str = ""):
    "Returns SimpleNamespace(path, contents, size, sha256)"
    if not os.path.exists(path.parent):
        path.parent.mkdir(parents=True)
    path.write_text(contents)
    return SimpleNamespace(path=path, contents=contents, size=len(contents))


def create_dir(path: Path):
    if not os.path.exists(path):
        path.mkdir(parents=True)


def rf_factory(tmp_path, rules):
    filterfile = tmp_path / ".rsync-filter"
    filterfile.write_text('\n'.join(rules))
    return RsyncFilter(tmp_path)


def rf_helper(tmp_path, rules) -> SimpleNamespace:
    rf = rf_factory(tmp_path, rules)
    matches = list(rf.scandir())
    prefix = f"{tmp_path}/"
    names = [match.path.removeprefix(prefix) for match in matches]
    return SimpleNamespace(matches=matches, names=names)


def create_files(tmp_path, files):
    for filename in files:
        entry = tmp_path / filename
        if filename.endswith('/'):
            create_dir(entry)
        else:
            create_file(entry)


def rf_test(tmp_path, rules: list[str], files: list[str]) -> SimpleNamespace:
    create_files(tmp_path, files)
    return rf_helper(tmp_path, rules)
