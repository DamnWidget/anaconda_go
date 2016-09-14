
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

from functools import partial

from anaconda_go.lib.plugin import typing

import sublime


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
            quick_panel_options.append(
                [option['ident'], option['full'], location]
            )
        self.point = self.view.sel()[0]
        self.view.window().show_quick_panel(
            quick_panel_options, self._on_select,
            on_highlight=partial(self._on_select, transient=True)
        )

    def _on_select(self, index, transient=False):
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
        if opt['keywork'] == 'package':
            # TODO: This could happen when we explore data from GuRu
            raise RuntimeError('TODO: Package browsing not implemented yet')

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
