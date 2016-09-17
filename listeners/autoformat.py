
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import sublime_plugin

from anaconda_go.lib.plugin import is_code
from anaconda_go.lib.helpers import get_settings


class AnacondaGoAutoFormatEventListener(sublime_plugin.EventListener):
    """AnacondaGO goimports formatter event listener class
    """

    def on_pre_save(self, view: sublime_plugin.sublime.View) -> None:
        """Called just before the file is going to be saved
        """

        auto_format = get_settings(view, 'anaconda_go_auto_format', False)
        if auto_format and is_code(view, lang='go'):
            view.run_command('anaconda_go_format')
