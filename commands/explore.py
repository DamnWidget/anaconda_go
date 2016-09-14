
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

from anaconda_go.lib import go
from anaconda_go.lib.plugin import typing
from anaconda_go.lib.helpers import get_settings
from anaconda_go.lib.panels import ExplorerPanel
from anaconda_go.lib.plugin import Worker, Callback, is_code

import sublime
import sublime_plugin


class AnacondaGoExploreBase(sublime_plugin.WindowCommand):
    """Base class for all the epxlorer classes
    """

    def run(self) -> None:
        try:
            view = self.window.active_view()
            data = {
                'vid': view.id(),
                'file_path': view.file_name(),
                'parse_comments': get_settings(
                    view, 'anaconda_go_motion_parse_comments', False
                ),
                'go_env': {
                    'GOROOT': go.GOROOT,
                    'GOPATH': go.GOPATH,
                    'CGO_ENABLED': go.CGO_ENABLED
                },
                'method': self.method,
                'handler': 'anaGonda'
            }
            Worker().execute(
                Callback(
                    on_success=ExplorerPanel(view).run,
                    on_failure=self._on_failure,
                    on_timeout=self._on_timeout
                ),
                **data
            )
        except Exception as err:
            print('anaconda_go: {}'.format(self.method.replace('_', ' ')))
            print(err)

    def is_enabled(self) -> bool:
        """Determine if this command is enabled or not
        """

        if len(sublime.active_window().views()) == 0:
            return False

        if not go.ANAGONDA_PRESENT:
            return False

        return is_code(self.view, lang='go')

    def _on_failure(self, data: typing.Dict) -> None:
        """Fired on failures from the callback
        """

        print('anaconda_go: {}'.format(self.method.replace('_', ' ')))
        print(data['error'])

    def _on_timeout(self, _):
        """Fired when the callback times out
        """

        print('anaconda_go: {} timed out'.format(
            self.method.replace('_', ' '))
        )


class AnacondaGoExploreFileFuncs(AnacondaGoExploreBase):
    """Get all the functions defined in the file
    """

    method = 'get_file_funcs'


class AnacondaGoExploreFileStructs(AnacondaGoExploreBase):
    """Get all the structs defined in the file
    """

    method = 'get_file_structs'


class AnacondaGoExploreFileDecls(AnacondaGoExploreBase):
    """Get file funcs and structs
    """

    method = 'get_file_decls'
