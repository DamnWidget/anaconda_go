
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

from lib import anaconda_handler

from .anagonda.metalinter import MetaLinter
from .commands.doc import Doc
from .commands.goto import Goto
from .commands.lint import Lint
from .commands.impl import Impl
from .commands.peers import Peers
from .commands.callees import Callees
from .commands.callers import Callers
from .commands.gogetdoc import GoGetDoc
from .commands.pointsto import Pointsto
from .commands.next_func import NextFunc
from .commands.prev_func import PrevFunc
from .commands.goimports import Goimports
from .commands.referrers import Referrers
from .commands.autocomplete import Gocode
from .commands.callstack import Callstack
from .commands.file_funcs import FileFuncs
from .commands.implements import Implements
from .commands.file_structs import FileStructs
from .commands.file_symbols import FileSymbols
from .commands.package_funcs import PackageFuncs
from .commands.enclosing_func import EnclosingFunc
from .commands.analyze_symbol import AnalyzeSymbol
from .commands.package_structs import PackageStructs
from .commands.package_symbols import PackageSymbols, PackageSymbolsCursor


class AnagondaHandler(anaconda_handler.AnacondaHandler):
    """Handle requests to manage go binaries related operations
    """

    __handler_type__ = 'anaGonda'

    def autocomplete(self, code, path, offset, add_params, go_env):
        """Call autocompletion registry context and return a result
        """

        Gocode(
            self.callback, self.uid, self.vid,
            code, path, offset, add_params, go_env
        )

    def goto(self, code, path, settings, go_env):
        """Call definitions registry context and return a result
        """

        Goto(self.callback, self.uid, self.vid, code, path, settings, go_env)

    def next_func(self, file_path, offset, parse_comments, go_env):
        """Call motion to get next function information
        """

        NextFunc(
            self.callback, self.uid, self.vid,
            file_path, offset, parse_comments, go_env
        )

    def prev_func(self, file_path, offset, parse_comments, go_env):
        """Call motion to get the prev funcion information
        """

        PrevFunc(
            self.callback, self.uid, self.vid,
            file_path, offset, parse_comments, go_env
        )

    def enclosing(self, file_path, offset, parse_comments, go_env):
        """Call motion to get the enclosing function information
        """

        EnclosingFunc(
            self.callback, self.uid, self.vid,
            file_path, offset, parse_comments, go_env
        )

    def get_file_funcs(self, file_path, parse_comments, go_env):
        """Call motion to get the functions declared in the file
        """

        FileFuncs(
            self.callback, self.uid, self.vid,
            file_path, parse_comments, go_env
        )

    def get_file_structs(self, file_path, parse_comments, go_env):
        """Call motion to get the structs declared in the file
        """

        FileStructs(
            self.callback, self.uid, self.vid,
            file_path, parse_comments, go_env
        )

    def get_package_funcs(self, dir_path, parse_comments, go_env):
        """Call motion to get the functions declared within the package
        """

        PackageFuncs(
            self.callback, self.uid, self.vid,
            dir_path, parse_comments, go_env
        )

    def get_package_structs(self, dir_path, parse_comments, go_env):
        """Call motion to get the structs declared within the package
        """

        PackageStructs(
            self.callback, self.uid, self.vid,
            dir_path, parse_comments, go_env
        )

    def get_file_decls(self, file_path, parse_comments, go_env):
        """Call motion to get the file declarations
        """

        FileSymbols(
            self.callback, self.uid, self.vid,
            file_path, parse_comments, go_env
        )

    def get_package_decls(self, scope, code, path, buf, go_env):
        """Call motion to get the package declarations
        """

        PackageSymbols(
            self.callback, self.uid, self.vid,
            scope, code, path, buf, go_env
        )

    def fast_lint(self, filepath, settings, go_env):
        """Call gometalinter fast linters only
        """

        Lint(
            self.callback, self.uid, self.vid,
            filepath, MetaLinter.lint_fast_only(settings), go_env
        )

    def slow_lint(self, filepath, settings, go_env):
        """Call gometalinter slow linters only
        """

        Lint(
            self.callback, self.uid, self.vid,
            filepath, MetaLinter.lint_slow_only(settings), go_env
        )

    def all_lint(self, filepath, settings, go_env):
        """Call gometalinter all linters
        """

        Lint(
            self.callback, self.uid, self.vid,
            filepath, MetaLinter.lint_all(settings), go_env
        )

    def impl(self, receiver, iface, go_env):
        """Call Impl with the given receiver and interface
        """

        Impl(self.callback, self.uid, self.vid, receiver, iface, go_env)

    def goimports(self, code, path, go_env):
        """Call goimports with the given code
        """

        Goimports(self.callback, self.uid, self.vid, code, path, go_env)

    def analyze_symbol(self, scope, code, offset, path, buf, mode, go_env):
        """Analyze the symbol under the cursor
        """

        if mode == 'browse':
            PackageSymbolsCursor(
                self.callback, self.uid, self.vid,
                scope, code, path, buf, offset, go_env
            )
        else:
            AnalyzeSymbol(
                self.callback, self.uid, self.vid,
                scope, offset, path, buf, go_env
            )

    def doc(self, path, expr, private, force, offset, buf, go_env):
        """Get documentation of the symbol under the cursor
        """

        if go_env.pop('GO_VERSION') >= [1, 6] and not force:
            GoGetDoc(
                self.callback, self.uid, self.vid, path, offset, buf, go_env)
        else:
            Doc(self.callback, self.uid, self.vid, path, expr, private, go_env)

    def callees(self, scope, path, offset, modified_buffer, go_env):
        """Get possible callees for a function call
        """

        Callees(
            self.callback, self.uid, self.vid,
            scope, path, offset, modified_buffer, go_env
        )

    def callers(self, scope, path, offset, modified_buffer, go_env):
        """Get possible callees for a function call
        """

        Callers(
            self.callback, self.uid, self.vid,
            scope, path, offset, modified_buffer, go_env
        )

    def callstack(self, scope, path, offset, modified_buffer, go_env):
        """Get current function call stack (if possible)
        """

        Callstack(
            self.callback, self.uid, self.vid,
            scope, path, offset, modified_buffer, go_env
        )

    def pointsto(self, scope, path, offset, modified_buffer, go_env):
        """Get current function call stack (if possible)
        """

        Pointsto(
            self.callback, self.uid, self.vid,
            scope, path, offset, modified_buffer, go_env
        )

    def referrers(self, scope, path, offset, modified_buffer, go_env):
        """Get referrers to the current symbol under cursor
        """

        Referrers(
            self.callback, self.uid, self.vid,
            scope, path, offset, modified_buffer, go_env
        )

    def implements(self, scope, path, offset, modified_buffer, go_env):
        """Retrieve information about interface implementations
        """

        Implements(
            self.callback, self.uid, self.vid,
            scope, path, offset, modified_buffer, go_env
        )

    def peers(self, scope, path, offset, modified_buffer, go_env):
        """Retrieve information about channels
        """

        Peers(
            self.callback, self.uid, self.vid,
            scope, path, offset, modified_buffer, go_env
        )
