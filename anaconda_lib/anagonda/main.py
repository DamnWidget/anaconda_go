
# Copyright (C) 2014 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import subprocess

from ..anaconda_plugin import create_subprocess


class anaGonda:

    """This object controls the anaGonda Go server and anything related to
    """

    def __init__(self, goroot, gopath, cgo, home):
        self.goroot = goroot
        self.gopath = gopath
        self.cgo = cgo
        self.home = home

    def prepare(self, version):
        """Prepare the anaGonda environment, compile the binary if necessary
        """

        self._check_home()
        self._check_binary(version)

    def _chech_home(self):
        """
        Check for the existance of the home dir, if it doesn't
        exists create it
        """

        log = self._log
        if not os.path.exists(self.home):
            log('directory {} does not exists, creating it'.format(self.home))
            os.mkdir(self.home)

    def _check_binary(self, version):
        """
        Check for the existance of the anaGonda.bin binary file, in
        case that it doesn't exists, generate it
        """

        log = self._log
        binary_file = 'anaGonda-{version}.bin'.format(version)
        if not os.path.exists(os.path.join(self.home, binary_file)):
            log('binary version {version} not found....'.format(version))
            self._remove_old_versions()
            self._compile(binary_file)

    def _remove_old_versions(self):
        """Seek and remove old anaGonda versions
        """

        log = self._log
        files = [
            x for x in os.listdir(self.home) if x.startswith('anaGonda-')]
        if len(files) > 0:
            log('\tfound {old_versions}...'.format(
                ', '.join(files)
            ))
            for f in files:
                log('\tuninstalling {old}...'.format(f))
                os.unlink(os.path.join(self.home, f))
        else:
            log('\tno older versions found...')

    def _compile(self, name):
        """Compile anaGonda application
        """

        log = self._log
        compile_path = os.path.abspath(__file__)
        args = ['go', 'build', '-v', '-x', '-o', name, compile_path]
        try:
            proc = create_subprocess(args, stdout=subprocess.PIPE)
        except:
            log(
                'we couldn\'t spawn the Go compiler process, it\'s possible '
                'that there is some environent configuration problem. Make '
                'sure that you have Go installed and you have configured '
                'your GOROOT and GOPATH environemnt variables and the go '
                'binary is in your PATH'
            )
            return False

        output, _ = proc.communicate()
        if output != '':
            for line in output.splitlines():
                log(line)

        if not os.path.exists(name):
            return False

        return True

    def _log(self, msg):
        """Convenience log method
        """

        log_string = '{class_name}: {msg}'.format(self.__class__.__name__, msg)
        print(log_string)
