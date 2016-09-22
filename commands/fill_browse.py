
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import json
import shlex
import traceback
import subprocess
from subprocess import PIPE, check_output

import sublime
import sublime_plugin

from anaconda_go.lib import go
from anaconda_go.lib.plugin import create_subprocess


class AnacondaGoFillBrowse(sublime_plugin.WindowCommand):
    """Get Go packages browse data from the system
    """

    def run(self) -> None:
        panel = self.window.create_output_panel('browse')
        panel.settings().set('wrap_width', 160)
        panel.settings().set("scroll_past_end", False)
        panel.assign_syntax('Packages/Text/Plain text.tmLanguage')
        self.output = panel
        self.window.create_output_panel('browse')
        self.window.run_command('show_panel', {'panel': 'output.browse'})
        sublime.set_timeout_async(lambda: self._run(), 0)

    def _run(self) -> None:

        try:
            self.env = os.environ.copy()
            self.env.update({'GOROOT': go.GOROOT, 'GOPATH': go.GOPATH})
            gocmd = os.path.join(go.GOROOT, 'bin', 'go')
            golist = create_subprocess(
                shlex.split(gocmd + ' list -json all', posix=os.name != 'nt'),
                stdout=PIPE, stdin=PIPE, env=self.env
            )
            msg = 'Getting list of golang packages from the system...\n'
            self.print_to_panel(msg)
            out, err = golist.communicate()
            if err is not None and len(err) > 0:
                self.print_to_panel(err.decode('utf8'))
                return

            self.process(out.decode('utf8'))
        except:
            print(traceback.print_exc())

    def process(self, data: str) -> None:
        """Process the output from go list (that is not valid JSON btw)
        """

        gurucmd = os.path.join(go.GOPATH, 'bin', 'guru')
        json_data = json.loads('[' + data.replace('}\n{', '},\n{') + ']')
        for package in json_data:
            self.print_to_panel('{} -> '.format(package['ImportPath']))
            fname = os.path.join(package['Dir'], package['GoFiles'][0])
            try:
                args = []
                kwargs = {}
                if os.name == 'posix':
                    args = shlex.split('grep -b "package {}" {}'.format(
                        package['Name'], fname
                    ), posix=True)
                else:
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    kwargs['startupinfo'] = startupinfo
                    args = shlex.split(
                        'findstr /O /R /C:"package {}" {}'.format(
                            package['Name'], fname
                        ), posix=False
                    )
                grep = check_output(args, **kwargs)
            except Exception as error:
                self.print_to_panel(str(error))
                continue

            offset = int(grep.decode().split(':')[0]) + len('package ') + 1
            args = shlex.split('{} -json -scope {} describe {}:#{}'.format(
                gurucmd, package['ImportPath'], fname, offset)
            )
            guru = create_subprocess(
                args, stdout=PIPE, stderr=PIPE, env=self.env)
            out, err = guru.communicate()
            if err is not None and len(err) > 0:
                self.print_to_panel(err.decode('utf8'))
                continue

            self.print_to_panel('Done\n')
            package['Guru'] = json.loads(out.decode('utf8'))

        go.PACKAGE_BROWSE = json_data
        self.print_to_panel(
            '\nPackages browse cache loaded, set the option '
            '"anaconda_go_verbose" as "false" in the configuration '
            'if you do not want to see this panel everytime that you '
            'start your Sublime Text 3\n\n'
            'Note: you can generate this cache at any time using the '
            'Command Palette'
        )

    def print_to_panel(self, msg: str) -> None:
        """Print the given message into the exec panel
        """

        self.output.run_command(
            'append', {'characters': msg, 'force': True, 'scroll_to_end': True}
        )
