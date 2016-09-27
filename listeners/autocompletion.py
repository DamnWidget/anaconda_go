
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

from anaconda_go.lib import go
from anaconda_go.lib.helpers import get_settings
from anaconda_go.lib.plugin import completion, Worker, Callback, is_code

import sublime


class GoCompletionEventListener(completion.AnacondaCompletionEventListener):
    """Completion listener for anaconda_go
    """

    def on_query_completions(self, view, prefix, locations):
        """Fired directly from Sublime Text 3 events systems
        """

        if not is_code(view, lang='go'):
            return

        if not go.ANAGONDA_PRESENT:
            if go.AVAILABLE:
                go.init()
            else:
                return

        if self.ready_from_defer is True:
            completion_flags = 0

            if get_settings(view, 'suppress_word_completions', False):
                completion_flags = sublime.INHIBIT_WORD_COMPLETIONS

            if get_settings(view, 'suppress_explicit_completions', False):
                completion_flags |= sublime.INHIBIT_EXPLICIT_COMPLETIONS

            cpl = self.completions
            self.completions = []
            self.ready_from_defer = False

            return (cpl, completion_flags)

        code = view.substr(sublime.Region(0, view.size()))
        row, col = view.rowcol(locations[0])
        data = {
            'vid': view.id(),
            'path': view.file_name(),
            'code': code,
            'offset': view.text_point(row, col),
            'add_params': get_settings(
                view, 'anaconda_go_add_completion_params', True),
            'go_env': {
                'GOROOT': go.GOROOT,
                'GOPATH': go.GOPATH,
                'CGO_ENABLED': go.CGO_ENABLED
            },
            'method': 'autocomplete',
            'handler': 'anaGonda'
        }
        Worker.execute(
            Callback(
                on_success=self._complete,
                on_failure=self._on_failure,
                on_timeout=self._on_timeout
            ),
            **data
        )

    def _on_timeout(self, _):
        """Called when request times out
        """

        print('anaconda_go completion timed out...')

    def _on_failure(self, data):
        """Called when request fails
        """

        print('anaconda_go error: {}'.format(data['error']))

    def _on_modified(self, view):
        """Just override anaconda superclass func
        """

        return
