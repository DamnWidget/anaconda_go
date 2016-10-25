
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import logging
import traceback

import sublime
import sublime_plugin

from anaconda_go.lib import go
from anaconda_go.lib.plugin import is_code
from anaconda_go.lib.plugin import Worker, Callback
from anaconda_go.lib.helpers import get_settings, get_window_view


class AnacondaGoFormat(sublime_plugin.TextCommand):
    """Execute goimports command in a buffer
    """

    data = None

    def run(self, edit):

        if self.data is not None:
            self.update_buffer(edit)
            return

        try:
            self.code = self.view.substr(sublime.Region(0, self.view.size()))
            data = {
                'vid': self.view.id(),
                'code': self.code,
                'path': self.view.file_name(),
                'go_env': {
                    'GOROOT': go.GOROOT,
                    'GOPATH': go.GOPATH,
                    'CGO_ENABLED': go.CGO_ENABLED
                },
                'method': 'goimports',
                'handler': 'anaGonda'
            }
            Worker().execute(
                Callback(
                    on_success=self.prepare_data,
                    on_failure=self.on_failure,
                    on_timeout=self.on_timeout
                ), **data
            )
        except Exception as error:
            logging.error(error)
            logging.debug(traceback.format_exc())

    def is_enabled(self):
        """Determine if this command is enabled or not
        """

        if not go.ANAGONDA_PRESENT:
            return False

        return is_code(self.view, lang='go')

    def prepare_data(self, data):
        """Prepare the returned data to overwrite our buffer
        """

        self.data = data
        self.view.run_command('anaconda_go_format')

    def update_buffer(self, edit):
        """Update and reload the buffer
        """

        results = self.data.get('result')
        view = get_window_view(self.data['vid'])
        if results is not None and results != '' and self.code != results:
            region = sublime.Region(0, view.size())
            view.replace(edit, region, results)
            if get_settings(view, 'anaconda_go_auto_format'):
                view.run_command('save')
                # sublime.set_timeout(lambda: view.run_command('save'), 0)

        self.data = None
        self.code = None

    def on_failure(self, data):
        """Called when callback return a failure
        """

        self.view.set_read_only(False)
        print('anaconda_go format error: {}'.format(data['error']))
        sublime.status_message(data['error'])

    def on_timeout(self):
        """Called when callback times out
        """

        print('anaconda_go format call timed out')
