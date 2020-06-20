# -*- coding: utf-8 -*-

from __future__ import division

__copyright__ = "Copyright (C) 2020 Dong Zhuang"

__license__ = """
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import os
from subprocess import Popen, PIPE

from django.core.checks import Critical
from django.core.exceptions import ImproperlyConfigured

from django.core.files import File
from django.core.management.base import CommandError
from django.utils.encoding import (
    DEFAULT_LOCALE_ENCODING, force_text)
from django.utils.text import format_lazy

from typing import Any, Text, List, Tuple, Optional  # noqa


# {{{ Constants

ALLOWED_COMPILER = ['latex', 'xelatex', 'xelatex']
ALLOWED_LATEX2IMG_FORMAT = ['png', 'svg']

ALLOWED_COMPILER_FORMAT_COMBINATION = (
    ("latex", "png"),
    ("latex", "svg"),
    ("xelatex", "png"),
    ("xelatex", "png")
)

# }}}


def string_concat(*strings):
    # type: (Any) -> Text
    return format_lazy("{}" * len(strings), *strings)


# {{{ subprocess popen wrapper

def popen_wrapper(args, os_err_exc_type=CommandError,
                  stdout_encoding='utf-8', **kwargs):
    # type: (...) -> Tuple[Text, Text, int]
    """
    Extended from django.core.management.utils.popen_wrapper.
    `**kwargs` is added so that more kwargs can be added.

    This method is especially to solve UnicodeDecodeError
    raised on Windows platform where the OS stdout is not utf-8.

    Friendly wrapper around Popen

    Returns stdout output, stderr output and OS status code.
    """

    try:
        p = Popen(args, stdout=PIPE,
                  stderr=PIPE, close_fds=os.name != 'nt', **kwargs)
    except OSError as e:
        raise os_err_exc_type from e

    output, errors = p.communicate()
    return (
        force_text(output, stdout_encoding, strings_only=True,
                   errors='strict'),
        force_text(errors, DEFAULT_LOCALE_ENCODING,
                   strings_only=True, errors='replace'),
        p.returncode
    )

# }}}


# {{{ file read and write

def file_read(filename):
    # type: (Text) -> bytes
    '''Read the content of a file and close it properly.'''
    with open(filename, 'rb') as f:
        ff = File(f)
        content = ff.read()
    return content


def file_write(filename, content):
    # type: (Text, bytes) -> None
    '''Write into a file and close it properly.'''
    with open(filename, 'wb') as f:
        ff = File(f)
        ff.write(content)

# }}}


# {{{ get error log abstracted

LATEX_ERR_LOG_BEGIN_LINE_STARTS = "\n! "
LATEX_ERR_LOG_END_LINE_STARTS = "\nHere is how much of TeX's memory"
LATEX_LOG_OMIT_LINE_STARTS = (
    "See the LaTeX manual or LaTeX",
    "Type  H <return>  for",
    " ...",
    # more
)


def get_abstract_latex_log(log):
    # type: (Text) -> Text
    '''abstract error msg from latex compilation log'''
    msg = log.split(LATEX_ERR_LOG_BEGIN_LINE_STARTS)[1]\
        .split(LATEX_ERR_LOG_END_LINE_STARTS)[0]

    if LATEX_LOG_OMIT_LINE_STARTS:
        msg = "\n".join(
            line for line in msg.splitlines()
            if (not line.startswith(LATEX_LOG_OMIT_LINE_STARTS)
                and
                line.strip() != ""))
    return msg

# }}}


def get_all_indirect_subclasses(cls):
    # type: (Any) -> List[Any]
    all_subcls = []

    for subcls in cls.__subclasses__():
        if not subcls.__subclasses__():
            # has no child
            all_subcls.append(subcls)
        all_subcls.extend(get_all_indirect_subclasses(subcls))

    return list(set(all_subcls))


def replace_latex_space_seperator(s):
    # type: (Text) -> Text
    """
    "{{", "}}", "{%", %}", "{#" and "#}" are used in jinja
    template, so we have to put spaces between those
    characters in latex source in the latex macro.
    To compile the source, we are now removing the spaces.
    """
    pattern_list = [
        r'{ {',
        r'} }',
        r'{ #',
        r'# }',
        r'{ %',
        r'% }'
        ]
    for pattern in pattern_list:
        while pattern in s:
            s = s.replace(pattern, pattern.replace(" ", ""))

    return s


class CriticalCheckMessage(Critical):
    def __init__(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        super(CriticalCheckMessage, self).__init__(*args, **kwargs)
        self.obj = self.obj or ImproperlyConfigured.__name__


# vim: foldmethod=marker
