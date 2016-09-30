
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
from collections import defaultdict

from anaconda_go.lib import go, cache
from anaconda_go.lib.plugin import typing
from anaconda_go.lib.panels import ExplorerPanel
from anaconda_go.lib.plugin import Worker, Callback, is_code
from anaconda_go.lib.helpers import get_settings, active_view, get_scope

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
        sublime.status_message(data['error'])

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
                'scope': scope if scope is not None else get_scope(view, go.GOPATH),  # noqa
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
                'scope': scope if scope is not None else get_scope(view, go.GOPATH),  # noqa
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


class AnacondaGoExplorePackages(sublime_plugin.WindowCommand):
    """Browse the full list of packages found in the system
    """

    def run(self, identificator: str ='') -> None:
        """Run the command using the given root (if any)
        """

        view = self.window.active_view()
        self.view = view
        symbols = []
        root = cache.lookup(identificator)
        #  root = self._lookup_root_into_cache(identificator)
        if root == '':
            sublime.error_message(
                'Could not find any data about \'{}\' in the cache'.format(
                    identificator
                )
            )
            return

        for symbol in self._sort(root):
            path, line, col = symbol['pos'].split(':')
            symbols.append({
                'filename': path,
                'line': int(line),
                'col': int(col),
                'ident': symbol['name'],
                'full': symbol['type'],
                'keyword': symbol['kind'],
                'show_filename': True,
            })

        if len(symbols) != 0:
            ExplorerPanel(self.view).run({'success': True, 'result': symbols})

    def _lookup_root_into_cache(self, root: str) -> typing.Dict:
        if root == '':
            root = cache.PACKAGES_CACHE[go.GOROOT]
        else:
            for pkg in cache.PACKAGES_CACHE[go.GOROOT]:
                guru = pkg.get('Guru')
                if guru is None:
                    continue
                path = guru['package'].get('path')
                if path is not None and path == root:
                    root = guru
                    break
                for member in guru['package'].get('members', []):
                    if member.get('name') == root:
                        root = member
                        break
                    for method in member.get('methods', []):
                        if method['name'] == root:
                            root = method
                            break

        return root

    def _sort(self, data: typing.Union[typing.List, typing.Dict]) -> typing.List:  # noqa
        """Sort the output by Package -> File -> Vars -> Type -> Funcs
        """

        if type(data) is list:
            # this is the top level from the cache
            return self._sort_packages(data)

        return self._sort_node(data)

    def _sort_packages(self, root: typing.List) -> typing.List:
        """Sort the root node that contains all the packages
        """

        symbols = []
        for pkg in root:
            pos = pkg.get('Guru', {}).get('package', {}).get('pos')
            if pos is None:
                pos = os.path.join(pkg['Dir'], pkg['GoFiles'][0]) + ':0:0'

            symbols.append({
                'pos': pos,
                'name': pkg['ImportPath'],
                'type': pkg.get('Guru', {}).get('desc'),
                'kind': 'package'
            })

        return symbols

    def _sort_node(self, node: typing.Dict) -> typing.List:
        """Sort the given node
        """

        symbols = []
        aggregated_data = defaultdict(lambda: [])
        tmp_elems = []
        if 'package' in node:
            tmp_elems = node['package'].get('members', [])
        else:
            tmp_elems = [node]

        for elem in tmp_elems:
            filename = elem['pos'].split(':')[0]
            aggregated_data[filename].append(elem)

        for filename, elems in aggregated_data.items():
            symbols += sorted(
                [e for e in elems if e['kind'] in ['var', 'const']],
                key=lambda x: x['pos']
            )
            symbols += sorted(
                [e for e in elems if e['kind'] in ['type']],
                key=lambda x: x['pos']
            )
            symbols += sorted(
                [e for e in elems if e['kind'] == 'func'],
                key=lambda x: x['pos']
            )
            for e in elems:
                if e['kind'] == 'type':
                    methods = []
                    for method in e.get('methods', []):
                        new_elem = method
                        new_elem['kind'] = 'func'
                        new_elem['type'] = method['name']
                        methods.append(new_elem)
                    symbols += sorted(methods, key=lambda x: x['pos'])

        return symbols
