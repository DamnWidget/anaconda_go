
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
from subprocess import PIPE

import sublime
import sublime_plugin

from anaconda_go.lib import go
from anaconda_go.lib.plugin import is_code, create_subprocess
from anaconda_go.lib.helpers import get_settings


class AnacondaGoFormatSync(sublime_plugin.TextCommand):
    """Execute goimports/gofmt command in a buffer
    """

    def get_binary(self, name):
        """Get absolute path of a go binary
        """

        if go.GOBIN:
            binary_path = os.path.join(go.GOBIN, name)
            if os.path.exists(binary_path):
                return binary_path

        for path in go.GOPATH.split(':'):
            binary_path = os.path.join(path, 'bin', name)
            if os.path.exists(binary_path):
                return binary_path

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

    def get_formatter_cmd(self, name, path):
        formatter = self.get_binary(name)
        if not formatter:
            raise RuntimeError('{} not found...'.format(name))

        args = get_settings(self.view, 'anaconda_go_{}_args'.format(name), [])
        args = [formatter] + args + [path]

        return args

    def run(self, edit, path=None):

        if path is None:
            path = self.view.file_name()
        code = self.view.substr(sublime.Region(0, self.view.size()))
        try:
            self.view.set_read_only(True)
            use_goimports = get_settings(self.view, 'anaconda_go_format_with_goimports', True)
            if use_goimports:
                self.format('goimports', code, path, edit)

            self.view.set_read_only(True)
            use_gofmt = get_settings(self.view, 'anaconda_go_format_with_gofmt', False)
            if use_gofmt:
                self.format('gofmt', code, path, edit)
        except Exception:
            self.view.set_read_only(False)
            raise
        finally:
            self.view.set_read_only(False)

    def format(self, formatter, code, path, edit):
        """Run formatter and modify the buffer if needed
        """

        formatter_cmd = self.get_formatter_cmd(formatter, path)
        proc = create_subprocess(formatter_cmd, stdout=PIPE, stderr=PIPE, env=self.env)

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
