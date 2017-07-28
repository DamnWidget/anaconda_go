
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import time
import tempfile
import sublime_plugin

import sublime

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
            filename = os.path.join(tempfile.gettempdir(), view.file_name())
            buf = view.substr(sublime.Region(0, view.size()))
            self._save_tmp_buffer(buf, filename)
            view.run_command(
                'anaconda_go_format_sync', args={"path": filename}
            )
            self._remove_tmp_buffer(filename)

        AnacondaGoAutoFormatEventListener._last_save = time.time()

    def _save_tmp_buffer(self, buf, file_name):
        """Save the buffer to a temporary file
        """

        with open(file_name, 'wt') as fd:
            fd.write(buf)

    def _remove_tmp_buffer(self, file_name):
        """Remove the temporary buffer from the file system
        """

        os.remove(file_name)
