
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os

from anaconda_go.lib import go
from anaconda_go.lib.plugin import typing
from anaconda_go.lib.panels import ExplorerPanel
from anaconda_go.lib.plugin import Worker, Callback, is_code
from anaconda_go.lib.helpers import get_settings, active_view

import sublime
import sublime_plugin


class AnacondaGoExploreBase(sublime_plugin.WindowCommand):
    """Base class for all the epxlorer classes
    """

    def run(self) -> None:
        try:
            view = self.window.active_view()
            self.view = view
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

        return is_code(active_view(), lang='go')

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


class AnacondaGoExplorePackageFuncs(AnacondaGoExploreBase):
    """Get package funcs
    """

    method = 'get_package_funcs'

    def run(self) -> None:
        try:
            view = self.window.active_view()
            self.view = view
            data = {
                'vid': view.id(),
                'dir_path': os.path.dirname(view.file_name()),
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


class AnacondaGoExplorePackageStructs(AnacondaGoExploreBase):
    """Get package funcs
    """

    method = 'get_package_structs'

    def run(self) -> None:
        try:
            view = self.window.active_view()
            self.view = view
            data = {
                'vid': view.id(),
                'dir_path': os.path.dirname(view.file_name()),
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


class AnacondaGoExplorePackageDecls(AnacondaGoExploreBase):
    """Get the package declarations
    """

    method = 'get_package_decls'

    def run(self) -> None:
        try:
            view = self.window.active_view()
            self.view = view
            scope = get_settings(view, 'anaconda_go_guru_scope')
            data = {
                'vid': view.id(),
                'scope': scope if scope is not None else self.scope(view),
                'code': view.substr(sublime.Region(0, view.size())),
                'path': view.file_name(),
                'buf': self.modified_buffer(view),
                'go_env': {
                    'GOROOT': go.GOROOT,
                    'GOPATH': go.GOPATH,
                    'CGO_ENABLED': go.CGO_ENABLED
                },
                'method': 'get_package_decls',
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

    def scope(self, view):
        """Try to automatically determine the Guru scope
        """

        if go.GOPATH in view.file_name():
            try:
                return os.path.dirname(
                    view.file_name().partition(
                        os.path.join(go.GOPATH, 'src'))[2])[1:]
            except:
                pass

        return ''

    def modified_buffer(self, view: sublime.View) -> str:
        """Guru needs this to use unsaved buffers instead of files
        """

        code = view.substr(sublime.Region(0, view.size()))
        return '\n'.join([
            view.file_name(), str(len(code.encode('utf8'))), code
        ])


class AnacondaGoExploreSymbolUnderCursor(AnacondaGoExplorePackageDecls):
    """Analyze and browse the symbol under cursor
    """

    method = 'analyze_symbol'

    def run(self, operation='analyze') -> None:
        self.operation = operation
        try:
            view = self.window.active_view()
            self.view = view
            scope = get_settings(view, 'anaconda_go_guru_scope')
            data = {
                'vid': self.view.id(),
                'scope': scope if scope is not None else self.scope(view),
                'code': view.substr(sublime.Region(0, view.size())),
                'offset': view.text_point(*view.rowcol(view.sel()[0].begin())),
                'path': view.file_name(),
                'buf': self.modified_buffer(view),
                'mode': self.operation,
                'go_env': {
                    'GOROOT': go.GOROOT,
                    'GOPATH': go.GOPATH,
                    'CGO_ENABLED': go.CGO_ENABLED
                },
                'method': 'analyze_symbol',
                'handler': 'anaGonda'
            }
            Worker().execute(
                Callback(
                    on_success=self.on_success,
                    on_failure=self._on_failure,
                    on_timeout=self._on_timeout
                ),
                **data
            )
        except Exception as err:
            print('anaconda_go: {}'.format(self.method.replace('_', '')))
            print(err)

    def on_success(self, data):
        """Called when the callback returns with a value from the JsonServer
        """

        if self.operation == 'analyze':
            ExplorerPanel(self.view).doc(data)
        else:
            ExplorerPanel(self.view).run(data)
