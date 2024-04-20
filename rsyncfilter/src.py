import os
import re
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Iterator, Generator


def find_files_up(filename, startdir=".") -> Generator[str, None, None]:
    """Searches current directory for filename. If filename isn't found, does a
    reverse-recursive search up the parent directory chain until it's found.
    Returns a generator for all files found. Doesn't cross filesystem boundary,
    for example won't leave a mounted path."""
    absdir = os.path.realpath(startdir)
    if not os.path.isdir(absdir):
        return
    startdev = os.stat(absdir).st_dev

    while True:
        abscfg = os.path.join(absdir, filename)
        if os.path.isfile(abscfg):
            yield abscfg
        elif absdir == "/":
            break
        absdir = os.path.realpath(os.path.join(absdir, ".."))
        if os.stat(absdir).st_dev != startdev:
            break


class RsyncFilterException(Exception):
    pass

"""
Rsync builds an ordered list of filter rules as specified on the
command-line and/or read-in from files.  New style filter rules have
the following syntax:

    RULE [PATTERN_OR_FILENAME]
    RULE,MODIFIERS [PATTERN_OR_FILENAME]

You have your choice of using either short or long RULE names. If you use a
short-named rule, the ',' separating the RULE from the MODIFIERS is optional.
The PATTERN or FILENAME that follows (when present) must come after either a
single space or an underscore (_). Any additional spaces and/or underscores are
considered to be a part of the pattern name.
"""

@dataclass
class Rule:
    basepath: str
    prefix: str  # -+.:HSPR!
    modifiers: str | None  # /!Csrpx
    relpath: str | None  # either path or pattern is set, not both
    pattern: str | None  # contains *?[


class RsyncFilter:
    SHORTS_RE = re.compile(r"[-+.:HSPR!](,?[/!Csrpx])?[ _](.+)")

    def __init__(self, top_path='.'):
        self.rules: list[Rule] = []
        self.top_path = top_path
        self._find_rsync_filter_file_up(top_path)

    def scandir(self, path=None, follow_symlinks=False) -> Iterator[os.DirEntry]:
        path = path or self.top_path
        # TODO raise exception if path is not part of top_path
        for entry in os.scandir(path):
            if self._is_included(entry):
                if entry.is_dir(follow_symlinks=follow_symlinks):
                    yield from self.scandir(entry.path, follow_symlinks=follow_symlinks)
                else:
                    yield entry

    def _is_included(self, entry: os.DirEntry) -> bool:
        abspath = entry.path
        for rule in self.rules:
            parts = entry.path.split(rule.basepath)
            if parts[0] != '':  # entry does not start with basepath
                continue
            relpath = parts[1]
            if relpath[0] == '/':
                relpath = relpath[1:]
            if entry.is_dir():  # always terminate dirs in / so rules work correctly
                relpath += '/'
            if rule.prefix == '+':
                if relpath == rule.relpath:
                    return True
        return False

    def _find_rsync_filter_file_up(self, path):
        for filterfile in find_files_up(".rsync-filter", path):
            self._parse_filter_file(filterfile)

    def _parse_filter_file(self, path):
        basepath = os.path.dirname(path)
        for line in open(path, "rt"):
            if line[0] == '#':
                continue
            parsed = self._parse_filter_line(line)
            new_rule = Rule(basepath=basepath, prefix=parsed.prefix, modifiers=parsed.modifiers, relpath=parsed.path_pattern, pattern=None)
            self.rules.append(new_rule)

    def _parse_filter_line(self, line) -> SimpleNamespace:
        # see if this is a short prefix
        shorts_re = re.compile(r"([-+.:HSPR!])(,?[/!Csrpx])?[ _](.+)\n?")
        matches = shorts_re.match(line)
        if matches:
            return SimpleNamespace(prefix=matches[1], modifiers=matches[2], path_pattern=matches[3])
        # see if it's a long prefix
        first, sep, second = line.partition(' ')
        if sep != ' ':
            raise "malformed"
        rule, maybe_sep, maybe_modifier = first.partition(',')
        raise "unimpl"



    def path_is_decendent(self, path) -> bool:
        "Path is a descendent of top_path."
        pass
