
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os

try:
    import sublime
except ImportError:
    # is not possible to import sublime module outside ST3 context
    pass

from .plugin import anaconda_helpers


def get_settings(view, name, default=None):
    """get settings
    """

    if view is None:
        return None

    plugin_settings = sublime.load_settings('Anaconda_GO.sublime-settings')
    if name == 'anaconda_go_linters':
        local = view.settings().get(name)
        if local is not None:
            local_linters = [list(l.keys())[0] for l in local]
            for linter in plugin_settings.get(name, []):
                for linter_name in linter:
                    if linter_name not in local_linters:
                        local.append(linter)
            return local

    return view.settings().get(name, plugin_settings.get(name, default))


def get_symbol(src, linenum, offset):
    """get the symbol under the cursor
    """

    symbols = [' ', '"', '\'', '(', '[', '{', '&', '*']
    endings = [')', ']', '}']
    start, end = None, None
    line = src.splitlines()[linenum]
    try:
        if len(line) == 0 or line[offset] in symbols:
            return ""
    except IndexError:
        # let's move the cursor one character backwards
        offset -= 1
        if len(line) == 0 or line[offset] in symbols:
            return ""

    line_end = len(line)
    for i in range(line_end):
        if i < offset and start is None:
            ri = offset - i
            if ri == 0:
                start = 0

            if line[ri-1] in symbols or line[ri-1] in endings:
                start = ri

        if i >= offset:
            if i == line_end:
                end = line_end

            if line[i] in symbols or line[i] in endings:
                end = i
                break

    return line[start:end]


def get_working_directory(view):
    """Return back the project file directory if any or current file one
    """

    pfilename = sublime.active_window().project_file_name()
    if pfilename is not None:
        return os.path.dirname(pfilename)

    return os.path.dirname(view.file_name())


def get_scope(view, GOPATH):
    """Try to automatically determine the Guru scope
    """

    for path in GOPATH.split(':'):
        if path in view.file_name():
            # always add main scope
            sc = []
            sc.append(view.window().folders()[0].partition(
                os.path.join(path, 'src'))[-1][1:]
            )
            try:
                sc.append(os.path.dirname(
                    view.file_name().partition(
                        os.path.join(path, 'src'))[2])[1:]
                )
                return ','.join(sc)
            except:
                pass

    return ''


# reuse anaconda helper functions
get_view = anaconda_helpers.get_view
active_view = anaconda_helpers.active_view
project_name = anaconda_helpers.project_name
check_linting = anaconda_helpers.check_linting
get_window_view = anaconda_helpers.get_window_view


__all__ = [
    'get_settings', 'active_view', 'get_view', 'get_window_view',
]
