
# Copyright (C) 2014 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import time
import sublime
from subprocess import PIPE

from Default.exec import ExecCommand
from anaconda_go.lib.helpers import project_name
from anaconda_go.lib.detector import GolangDetector
from anaconda_go.lib.plugin import create_subprocess


class GoWrapper:
    """This class hooks itself into the sys.modules
    """

    _go_dependencies = [
        'github.com/DamnWidget/godef',
        'golang.org/x/tools/cmd/guru',
        'github.com/fatih/motion',
        'github.com/josharian/impl',
        'github.com/nsf/gocode',
        'github.com/zmb3/gogetdoc',
        'gopkg.in/alecthomas/gometalinter.v1'
    ]

    def __init__(self) -> None:
        self._projects = {}

    @property
    def GOROOT(self) -> str:
        """Return a valid GOROOT for the current project
        """

        if self._project_name not in self._projects:
            self._detect()

        return self._projects[self._project_name]['root']

    @property
    def GOPATH(self) -> str:
        """Return a valid GOPATH for the current project
        """

        if self._project_name not in self._projects:
            self._projects[self._project_name] = {}
            self._detect()

        return self._projects[self._project_name]['path']

    @property
    def CGO_ENABLED(self) -> str:
        """Return a valid CGO_ENABLED for the current project
        """

        if self._project_name not in self._projects:
            self._projects[self._project_name] = {}
            self._detect()

        return self._projects[self._project_name]['cgo']

    @property
    def GOBIN(self) -> str:
        """Return a valid GOBIN for the current project
        """

        if self._project_name not in self._projects:
            self._projects[self._project_name] = {}
            self._detect()

        return self._projects[self._project_name]['bin']

    @property
    def AVAILABLE(self) -> bool:
        """Return if a Go instalation is avaiable for the current project
        """

        if self._project_name not in self._projects:
            self._detect()

        return self._projects[self._project_name]['available']

    @property
    def ANAGONDA_PRESENT(self) -> bool:
        """Return the anagonda present project variable
        """

        if self._project_name not in self._projects:
            self._detect()

        return self._projects[self._project_name]['anagonda']

    @property
    def _project_name(self) -> str:
        """Return the current project name
        """

        return project_name()

    @property
    def go_version(self) -> str:
        """Return back the version of the go compiler/runtime
        """

        args = '{} version'.format(self.go_binary).split()
        go = create_subprocess(args, stdout=PIPE)
        output, _ = go.communicate()

        try:
            return output.split()[2]
        except:
            return ''

    @property
    def go_binary(self) -> str:
        """Return back the go binary location if Go is detected
        """

        return os.path.join(self.GOROOT, 'bin', 'go')

    def init(self) -> None:
        """Initialize this project anagonda
        """

        if self.AVAILABLE is True:
            self.install_tools()

            def monitor():
                start = time.time()
                while not self.__tools_instaled() and time.time() - start <= 300:  # noqa
                    time.sleep(0.5)

                if time.time() - start >= 300:
                    sublime.message_dialog(
                        'Go utils not available for this project, look at the '
                        'log panel to fix any issue with your system, then '
                        'restart Sublime Text 3'
                    )
                else:
                    self._projects[self._project_name]['anagonda'] = True
                if os.name != 'nt':
                    sublime.set_timeout_async(
                        lambda: sublime.active_window().run_command(
                            'anaconda_go_fill_browse'), 0
                    )

            sublime.set_timeout_async(lambda: monitor(), 0)

    def install_tools(self):
        """Installs go tools for this project if not done yet
        """

        if self.__tools_instaled():
            return

        window = sublime.active_window()
        panel = window.get_output_panel('exec')
        panel.settings().set('wrap_width', 160)
        env = os.environ.copy()
        env.update({'GOPATH': self.GOPATH, 'GOROOT': self.GOROOT})
        exe = ExecCommand(window)
        exe.run(
            shell_cmd='{} get -x -u {}'.format(
                os.path.join(self.GOROOT, 'bin', 'go'),
                ' '.join(self._go_dependencies)
            ),
            file_regex=r'[ ]*File \"(...*?)\", line ([0-9]*)',
            env=env
        )

    def _detect(self) -> None:
        """Detect the Go env for this project
        """

        root, path, cgo = GolangDetector().detect()
        self._projects[self._project_name] = {
            'root': root,
            'path': path,
            'cgo': cgo,
            'bin': bin,
            'available': True,
            'anagonda': False
        }

    def _skeleton(self) -> None:
        """Create a skeleton of data, this prevents weird crahses on Windows
        """

        self._projects[self._project_name] = {
            'root': "",
            'path': "",
            'cgo': "1",
            'available': False,
            'anagonda': False
        }

    def __tools_instaled(self) -> bool:
        """Check if the go tools are installed
        """

        return all(
            [os.path.exists(os.path.join(self.GOPATH, 'src', p))
                for p in self._go_dependencies]
        )


go = GoWrapper()
