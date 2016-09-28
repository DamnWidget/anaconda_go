
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
from functools import partial

from anaconda_go.lib.plugin import typing

import sublime
from Default.exec import ExecCommand


class ExplorerPanel:
    """Panel to support exploring commands
    """

    def __init__(self, view):
        self.view = view

    def run(self, data: typing.Dict =None) -> None:
        """Proccess the data coming from the tools
        """

        if data is not None and not data['success']:
            return self._unable_to_find()

        results = data['result']
        if len(results) == 0:
            return self._unable_to_find()

        self._show_options(results)

    def doc(self, data: typing.Dict =None) -> None:
        """Create a doc panel with the data coming from the tools
        """

        if data is not None and not data['success']:
            return self._unable_to_find()

        result = data['result']
        if len(result) == 0:
            return self._unable_to_find()
        data = result

        doc = ['']
        _type = data.get('detail')
        if _type is None:
            return self._unable_to_find()

        detail = data.get(_type)
        if detail is None:
            return self._unable_to_find()

        description = detail.get('type')
        if description is None:
            return self._unable_to_find()

        doc.append(description)
        doc.append('=' * 79)
        p = {'type': detail.get('namepos')}.get(_type, detail.get('objpos'))
        if p is not None:
            path, line, col = p.split(':')
            doc.append(p)

        namedef = detail.get('namedef')
        if namedef is not None:
            namedef = namedef.replace(
                '; ', '\n\t').replace('{', ' {\n\t').replace('}', '\n}')
            namedef = namedef.replace('struct {', 'struct {} {{'.format(
                description
            ), 1)
            doc.append(namedef)

        methods = detail.get('methods', [])
        if len(methods) > 0:
            doc.append('\nMethods ')
            for method in methods:
                doc.append('{}\n    {}\n'.format(
                    method['pos'], method['name'])
                )

        exe = ExecCommand(sublime.active_window())
        exe.run(
            shell_cmd='echo "{}\n"'.format('\n'.join(doc)),
            file_regex=r'(...*?):([0-9]*):([0-9]*)',
            quiet=True,
        )
        exe.hide_phantoms()

    def _unable_to_find(self):
        """Just show a message in the status bar
        """

        sublime.status_message('Unable to find {}'.format(
            self.view.substr(self.view.word(self.view.sel()[0]))
        ))

    def _show_options(self, options: typing.Dict) -> None:
        """Show a dropdown quickpanel with options on it
        """

        self._options = options
        quick_panel_options = []
        for option in options:
            location = 'file: {} line: {} column: {}'.format(
                option['filename'], option['line'], option['col']
            )
            ident = option['ident']
            if option.get('show_filename', False):
                ident = '{} ({})'.format(
                    option['ident'], os.path.basename(option['filename'])
                )
            quick_panel_options.append(
                [ident, option['full'], location]
            )

        self.point = self.view.sel()[0]
        self.view.window().show_quick_panel(
            quick_panel_options, self._on_select,
            on_highlight=partial(
                self._on_select, transient=True, highlight=True)
        )

    def _on_select(self, index, transient=False, highlight=False):
        """Called when the user selects an option in the quick panel
        """

        if index == -1:
            # restore view
            sublime.active_window().focus_view(self.view)
            self.view.show(self.point)

            if self.view.sel()[0] != self.point:
                self.view.sel().clear()
                self.view.sel().add(self.point)

            return

        opt = self._options[index]
        if opt['keyword'] == 'package' and not highlight:
            sublime.set_timeout(
                sublime.active_window().run_command(
                    'anaconda_go_explore_packages',
                    args={'identificator': opt['ident']}
                ), 0
            )
            return

        if opt['keyword'] != 'package' and highlight is True:
            self._jump(opt['filename'], opt['line'], opt['col'], transient)

    def _jump(self, filename: str, line: int =None,
              col: int =None, transient: bool =False) -> None:
        """Jump to the given destination
        """

        flags = sublime.ENCODED_POSITION
        if transient:
            flags |= sublime.TRANSIENT

        sublime.active_window().open_file(
            '{}:{}:{}'.format(filename, line or 0, col or 0), flags)
        self._toggle_indicator(line, col)

    def _toggle_indicator(self, line: int =0, col: int =0) -> None:
        """Toggle mark indicator for focus the cursor
        """

        pt = self.view.text_point(line - 1, col)
        region_name = 'anaconda.indicator.{}.{}'.format(self.view.id(), line)

        for i in range(3):
            delta = 300 * i * 2
            sublime.set_timeout(lambda: self.view.add_regions(
                region_name,
                [sublime.Region(pt, pt)],
                'comment',
                'bookmark',
                sublime.DRAW_EMPTY_AS_OVERWRITE
            ), delta)
            sublime.set_timeout(
                lambda: self.view.erase_regions(region_name),
                delta + 300
            )


class DocPanel:
    """General doc panel class
    """

    def __init__(self, view):
        self.view = view
        self.panel = view.window().create_output_panel('anaconda_go_doc')
        self.panel.settings().set('scroll_past_end', False)
        self.panel.settings().set('line_numbers', False)
        self.panel.settings().set('rulers', [])
        self.panel.assign_syntax('Packages/Text/Plain text.tmLanguage')
        self.view.window().create_output_panel('anaconda_go_doc')

    def show(self):
        """Show the doc panel
        """

        self.view.window().run_command(
            'show_panel', {'panel': 'output.anaconda_go_doc'}
        )

    def print(self, text: str, se: bool=False):
        """Print the given text into the panel
        """

        self.panel.run_command(
            'append', {'characters': text, 'force': True, 'scroll_to_end': se}
        )
