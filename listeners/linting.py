
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details


from anaconda_go.lib.plugin import linting
from anaconda_go.lib._sublime import run_linter


class BackgroundLinter(linting.BackgroundLinter):
    """Background linter, can be turned off via plugin settings
    """

    def __init__(self):
        super(BackgroundLinter, self).__init__(
            lang='Go', linter=run_linter, non_auto=True
        )

    def on_activated(self, view) -> None:
        """Called when a view gain the focus
        """

        self._erase_marks_if_no_linting(view)
