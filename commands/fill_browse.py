
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

from anaconda_go.lib import go, cache
from anaconda_go.lib.helpers import get_settings
from anaconda_go.lib.plugin import create_subprocess, ProgressBar


class AnacondaGoFillBrowse(sublime_plugin.WindowCommand):
    """Get Go packages browse data from the system
    """

    def run(self, standalone=False) -> None:
        panel = self.window.create_output_panel('browse')
        panel.settings().set('wrap_width', 120)
        panel.settings().set("scroll_past_end", False)
        panel.assign_syntax('Packages/Text/Plain text.tmLanguage')
        self.output = panel
        self.window.create_output_panel('browse')
        if standalone or get_settings(
                self.window.active_view(), 'anaconda_go_verbose', True):
            self.window.run_command('show_panel', {'panel': 'output.browse'})
        sublime.set_timeout_async(lambda: self._run(), 0)
        messages = {
            'start': 'Building packages navigation cache...',
            'end': 'done!',
            'fail': 'The package navigation cache could not be build!',
            'timeout': ''
        }
        self.pbar = ProgressBar(messages)
        self.pbar.start()

    def _run(self) -> None:

        try:
            if get_settings(
                self.window.active_view(),
                    'anaconda_go_packages_cache_persistence', False):
                cache.load_package_cache()

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
                self.pbar.terminate(status=self.pbar.Status.FAILURE)
                return

            self.process(out.decode('utf8'))
        except:
            print(traceback.print_exc())

    def is_enabled(self):
        """This is disabled for Windows for now
        """

        return os.name != 'nt'

    def process(self, data: str) -> None:
        """Process the output from go list (that is not valid JSON btw)
        """

        gurucmd = os.path.join(go.GOPATH, 'bin', 'guru')
        json_data = json.loads('[' + data.replace('}\n{', '},\n{') + ']')
        for package in json_data:
            self.print_to_panel('{} -> '.format(package['ImportPath']))
            if cache.package_in_cache(package):
                self.print_to_panel('already in cache, nothing to do\n')
                continue

            try:
                fname = os.path.join(package['Dir'], package['GoFiles'][0])
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

                grep = check_output(args, shell=True, **kwargs)
            except Exception as error:
                self.print_to_panel(str(error))
                continue

            try:
                offset = int(grep.decode().split(':')[0]) + len('package ') + 1
            except Exception as e:
                print('while parsing grep/findstr output for {}: {}\t{}'.format(  # noqa
                    ' '.join(args), e, grep.decode())
                )
                continue
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
            cache.append(package)

        self.pbar.terminate()
        if get_settings(
                self.window.active_view(),
                'anaconda_go_packages_cache_persistence', False):
            cache.persist_package_cache()

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
