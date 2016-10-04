
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import time
import sublime_plugin

from anaconda_go.lib.plugin import is_code
from anaconda_go.lib.helpers import get_settings


class AnacondaGoAutoFormatEventListener(sublime_plugin.EventListener):
    """AnacondaGO goimports formatter event listener class
    """

    _last_save = time.time()

    def on_pre_save(self, view: sublime_plugin.sublime.View) -> None:
        """Called just before the file is going to be saved
        """

        if time.time() - self._last_save < 2:
            return

        auto_format = get_settings(view, 'anaconda_go_auto_format', False)
        if auto_format and is_code(view, lang='go'):
            view.run_command('anaconda_go_format')

        self._last_save = time.time()
