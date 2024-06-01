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

    @property
    def dir_only(self):
        return self.relpath.endswith('/')

    @property
    def anchor_only(self):
        return self.relpath.startswith('/')

    @property
    def parts(self):
        return self.relpath.removeprefix('/').removesuffix('/').split('/')

    def is_a_subset_of(self, candparts) -> bool:
        n = len(self.parts)
        for i in range(0, len(candparts), n):
            candrange = candparts[i:i + n]
            if self.parts == candrange:
                return True
        return False

    @property
    def relpath_clean(self):
        return '/'.join(self.parts)


class RsyncFilter:
    SHORTS_RE = re.compile(r"[-+.:HSPR!](,?[/!Csrpx])?[ _](.+)")

    def __init__(self, top_path='.', explain_mode=False):
        self.rules: list[Rule] = []
        self.top_path = top_path
        self._find_rsync_filter_file_up(top_path)
        self.explain_mode = explain_mode

    def scandir(self, path=None, follow_symlinks=False) -> Iterator[os.DirEntry]:
        path = path or self.top_path
        # TODO raise exception if path is not part of top_path
        for entry in os.scandir(path):
            is_included = self._is_included(entry)
            if is_included:
                if entry.is_dir(follow_symlinks=follow_symlinks):
                    yield from self.scandir(entry.path, follow_symlinks=follow_symlinks)
                yield entry

    def _is_included(self, entry: os.DirEntry) -> bool:
        for rule in self.rules:
            basepath, relpath = entry.path.split(rule.basepath)
            if basepath != '':
                self.explain(f"candidate {entry.path} does not start with rule basepath: {rule.basepath}")
                continue

            if rule.dir_only:
                if entry.is_symlink():
                    self.explain(f"rule is dir only but candidate {entry.path} is a symlink")
                    continue
                if not entry.is_dir():
                    self.explain(f"rule is dir only but candidate {entry.path} is not a directory")
                    continue

            entryparts = relpath.removeprefix('/').split('/')
            if rule.anchor_only and entryparts[0] != rule.parts[0]:
                self.explain(f"rule is an anchor but candidate {entry.path} is not at the top of the basepath: {rule.basepath}")
                continue

            if rule.prefix == '+':
                if relpath == rule.relpath:
                    return True
                if relpath == rule.relpath.removeprefix('/'):
                    return True
            elif rule.prefix == '-':
                if rule.relpath == '*':
                    return False
                if rule.is_a_subset_of(entryparts):
                    return False
            else:
                raise RsyncFilterException("unsupported prefix:", rule.prefix)
        return True

    def _find_rsync_filter_file_up(self, path):
        for filterfile in find_files_up(".rsync-filter", path):
            self._parse_filter_file(filterfile)

    def _parse_filter_file(self, path):
        basepath = os.path.dirname(path)
        for line in open(path, "rt"):
            if line[0] == '#':
                continue
            parsed = self._parse_filter_line(line)
            new_rule = Rule(basepath=basepath, prefix=parsed.prefix, modifiers=parsed.modifiers, relpath=parsed.relpath, pattern=parsed.pattern)
            self.rules.append(new_rule)

    def _parse_filter_line(self, line) -> SimpleNamespace:
        # see if this is a short prefix
        shorts_re = re.compile(r"([-+.:HSPR!])(,?[/!Csrpx])?[ _](.+)\n?")
        matches = shorts_re.match(line)
        if matches:
            return SimpleNamespace(prefix=matches[1], modifiers=matches[2], relpath=matches[3], pattern=None)
        # see if it's a long prefix
        first, sep, second = line.partition(' ')
        if sep != ' ':
            raise "malformed"
        rule, maybe_sep, maybe_modifier = first.partition(',')
        raise "unimpl"

    def _parse_path_pattern(self, maybe_pattern) -> tuple:
        return (maybe_pattern, None)
    """ TODO:
Rsync  chooses between doing a simple string match and wildcard matching by checking if the pattern contains one of these three wildcard
       characters: '*', '?', and '[' :

       o      a '?' matches any single character except a slash (/).
       o      a '*' matches zero or more non-slash characters.
       o      a '**' matches zero or more characters, including slashes.
       o      a '[' introduces a character class, such as [a-z] or [[:alpha:]], that must match one character.
       o      a trailing *** in the pattern is a shorthand that allows you to match a directory and all its contents using a single rule.   For example, specifying "dir_name/***" will match both the "dir_name" directory (as if "dir_name/" had been specified) and everything in the directory (as if "dir_name/**" had been specified).
       o      a  backslash  can be used to escape a wildcard character, but it is only interpreted as an escape character if at least one wild‐ card character is present in the match pattern. For instance, the pattern "foo\bar"  matches  that  single  backslash  literally, while the pattern "foo\bar*" would need to be changed to "foo\\bar*" to avoid the "\b" becoming just "b".
	"""

    def path_is_decendent(self, path) -> bool:
        "Path is a descendent of top_path."
        pass

    def explain(self, *args):
        if self.explain_mode:
            print(*args)
