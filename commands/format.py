
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
from subprocess import PIPE

import sublime
import sublime_plugin

from anaconda_go.lib import go
from anaconda_go.lib.plugin import is_code
from anaconda_go.lib.plugin import create_subprocess


class AnacondaGoFormatSync(sublime_plugin.TextCommand):
    """Execute goimports command in a buffer
    """

    @property
    def binary(self):
        """Get the goimports binary
        """

        if go.GOBIN:
            binary_path = os.path.join(go.GOBIN, 'goimports')
            if os.path.exists(binary_path):
                return binary_path

        for path in go.GOPATH.split(':'):
            binary_path = os.path.join(path, 'bin', 'goimports')
            if os.path.exists(binary_path):
                return binary_path

        return '/not/found'

    @property
    def env(self):
        """Prepare an environ with go vars and sanitization
        """

        env = {}
        curenv = os.environ.copy()
        for key in curenv:
            env[str(key)] = str(curenv[key])

        env.update({
            'GOPATH': go.GOPATH,
            'GOROOT': go.GOROOT,
            'GOBIN': go.GOBIN,
            'CGO_ENABLED': go.CGO_ENABLED
        })

        return env

    def run(self, edit, path=None):

        if path is None:
            path = self.view.file_name()
        code = self.view.substr(sublime.Region(0, self.view.size()))
        try:
            self.view.set_read_only(True)
            self.goimports(code, path, edit)
        except Exception:
            self.view.set_read_only(False)
            raise
        finally:
            self.view.set_read_only(False)

    def goimports(self, code, path, edit):
        """Run goimports and modify the buffer if needed
        """

        goimports = self.binary
        if goimports == '/not/found':
            raise RuntimeError('goimports not found...')

        args = [goimports, path]
        proc = create_subprocess(args, stdout=PIPE, stderr=PIPE, env=self.env)
        out, err = proc.communicate()
        if err is not None and len(err) > 0:
            raise RuntimeError(err.decode('utf8'))

        if out is not None and out != b'':
            out = out.decode('utf8')
            if code != out:
                region = sublime.Region(0, self.view.size())
                self.view.set_read_only(False)
                self.view.replace(edit, region, out)

    def is_enabled(self):
        """Determine if this command is enabled or not
        """

        if not go.ANAGONDA_PRESENT:
            return False

        return is_code(self.view, lang='go')

