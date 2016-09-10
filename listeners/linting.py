
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import inspect
import sublime

class BackgroundLinter(linting.BackgroundLinter):
    """Background linter, can be turned off via plugin settings
    """

    def __init__(self):
        kwargs = {'lang': 'Go', 'linters': {'on_post_save': all_linters}}
        super(BackgroundLinter, self).__init__(**kwargs)
        self.check_auto_lint = True

    def lint(self) -> None:
        stack = inspect.stack()
        caller = stack[1][3]
        self.run_linter = self.linters.get(caller, fast_linter)
        super(BackgroundLinter, self).lint()
