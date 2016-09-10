
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

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

    plugin_settings = sublime.load_settings('AnacondaGO.sublime-settings')
    return view.settings().get(name, plugin_settings.get(name, default))


def get_symbol(src, linenum, offset):
    """get the symbol under the cursor
    """

    symbols = [' ', '"', '\'', '(', '[', '{', '&', '*']
    endings = [')', ']', '}']
    start, end = None, None
    line = src.splitlines()[linenum]
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


# reuse anaconda helper functions
get_view = anaconda_helpers.get_view
active_view = anaconda_helpers.active_view
check_linting = anaconda_helpers.check_linting
get_window_view = anaconda_helpers.get_window_view


__all__ = [
    'get_settings', 'active_view', 'get_view', 'get_window_view',
]
