#!/usr/bin/env python3
import itertools
import os
import re
import sys

if sys.version_info[0] < 3:
    raise RuntimeError('This needs to run on Python 3.')


def get_characters():
    """Find every Unicode character that is valid in a Python `identifier`_ but
    is not matched by the regex ``\w`` group.

    ``\w`` matches some characters that aren't valid in identifiers, but
    :meth:`str.isidentifier` will catch that later in lexing.

    All start characters are valid continue characters, so we only test for
    continue characters.

    _identifier: https://docs.python.org/3/reference/lexical_analysis.html#identifiers
    """
    for cp in range(sys.maxunicode + 1):
        s = chr(cp)

        if ('a' + s).isidentifier() and not re.match(r'\w', s):
            yield s


def collapse_ranges(data):
    """Given a sorted list of unique characters, generate ranges representing
    sequential code points.

    Source: https://stackoverflow.com/a/4629241/400617
    """
    for a, b in itertools.groupby(
        enumerate(data),
        lambda x: ord(x[1]) - x[0]
    ):
        b = list(b)
        yield b[0][1], b[-1][1]


def build_pattern(ranges):
    """Output the regex pattern for ranges of characters.

    One and two character ranges output the individual characters.
    """
    out = []

    for a, b in ranges:
        if a == b:  # single char
            out.append(a)
        elif ord(b) - ord(a) == 1:  # two chars, range is redundant
            out.append(a)
            out.append(b)
        else:
            out.append(f'{a}-{b}')

    return ''.join(out)


def main():
    """Build the regex pattern and write it to the file
    :file:`jinja/_identifier.py`.
    """
    pattern = build_pattern(collapse_ranges(get_characters()))
    filename = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', 'jinja', '_identifier.py'
    ))

    with open(filename, 'w', encoding='utf8') as f:
        f.write('# generated by scripts/generate_identifier_pattern.py\n')
        f.write(f'pattern = \'{pattern}\'\n')


if __name__ == '__main__':
    main()
