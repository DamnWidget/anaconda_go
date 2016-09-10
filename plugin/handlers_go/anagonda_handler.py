
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

from lib import anaconda_handler

from .anagonda import anaGonda
from .anagonda.metalinter import MetaLinter


class AnagondaHandler(anaconda_handler.AnacondaHandler):
    """Handle requests to manage go binaries related operations
    """

    __handler_type__ = 'anaGonda'

    def autocomplete(self, code, path, offset, go_env):
        """Call autocompletion registry context and return a result
        """

        return self._proccess('autocomplete', go_env, code, path, offset)

    def goto(self, code, path, settings, go_env):
        """Call definitions registry context and return a result
        """

        return self._proccess('definitions', go_env, code, path, settings)

    def next_func(self, file_path, offset, parse_comments, go_env):
        """Call motion to get next function information
        """

        return self._proccess(
            'motion', go_env, file_path, None,
            offset, 'next', None, parse_comments
        )

    def prev_func(self, file_path, offset, parse_comments, go_env):
        """Call motion to get the prev funcion information
        """

        return self._proccess(
            'motion', go_env, file_path, None,
            offset, 'prev', None, parse_comments
        )

    def enclosing(self, file_path, offset, parse_comments, go_env):
        """Call motion to get the enclosing function information
        """

        return self._proccess(
            'motion', go_env, file_path, None,
            offset, 'enclosing', None, parse_comments
        )

    def get_file_funcs(self, file_path, offset, parse_comments, go_env):
        """Call motion to get the functions declared in the file
        """

        return self._proccess(
            'motion', go_env, file_path, None,
            offset, 'decls', 'func', parse_comments
        )

    def get_file_structs(self, file_path, offset, parse_comments, go_env):
        """Call motion to get the structs declared in the file
        """

        return self._proccess(
            'motion', go_env, file_path, None,
            offset, 'decls', 'type', parse_comments
        )

    def get_package_funcs(self, dir_path, parse_comments, go_env):
        """Call motion to get the functions declared within the package
        """

        return self._proccess(
            'motion', go_env, None, dir_path,
            None, 'decls', 'func', parse_comments
        )

    def get_package_structs(self, dir_path, parse_comments, go_env):
        """Call motion to get the structs declared within the package
        """

        return self._proccess(
            'motion', go_env, None, dir_path,
            None, 'decls', 'func', parse_comments
        )

    def get_file_decls(self, file_path, offset, parse_comments, go_env):
        """Call motion to get the file declarations
        """

        return self._proccess(
            'motion', go_env, file_path, None,
            offset, 'decls', 'func,type', parse_comments
        )

    def get_package_decls(self, dir_path, parse_comments, go_env):
        """Call motion to get the package declarations
        """

        return self._proccess(
            'motion', go_env, None, dir_path,
            None, 'decls', 'func,type', parse_comments
        )

    def fast_lint(self, settings, go_env):
        """Call gometalinter fast linters only
        """

        return self._proccess(
            'lint', MetaLinter.lint_fast_only(settings), go_env
        )

    def slow_lint(self, settings, go_env):
        """Call gometalinter slow linters only
        """

        return self._proccess(
            'lint', MetaLinter.lint_slow_only(settings), go_env
        )

    def impl(self, receiver, iface, go_env):
        """Call Impl with the given receiver and interface
        """

        return self._process('impl', go_env, receiver, iface)

    def _proccess(self, method_name, go_env, *args, **kwargs):
        """Process the anaGonda command and return  back a valid response
        """

        try:
            anagonda = anaGonda(**go_env)
            method = getattr(anagonda, method_name, self._errback)
            self.callback({
                'success': True,
                'result': method(*args, **kwargs),
                'uid': self.uid,
                'vid': self.vid
            })
        except Exception as error:
            self.callback({
                'success': False,
                'error': error,
                'uid': self.uid,
                'vid': self.vid
            })

    def _errback(self, method_name):
        """Common errback to use on errors
        """

        raise RuntimeError('method {0} does not exists!'.format(method_name))
