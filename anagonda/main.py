
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import shlex
import subprocess

try:
    from anconda_go.lib.plugin import create_subprocess
except ImportError:
    def create_subprocess(*args, **kwargs):
        return subprocess.Popen(*args, **kwargs)


class anaGonda:
    """This object controls the anaGonda Go server and anything related to
    """

    _compile_path = './anagonda/src'

    def __init__(self, goroot, gopath, cgo, home):
        self.goroot = goroot
        self.gopath = gopath
        self.cgo = cgo
        self.home = home

    def prepare(self, version: str) -> None:
        """Prepare the anaGonda environment, compile the binary if necessary
        """

        self._check_home()
        self._check_binary(version)

    def _check_home(self) -> None:
        """
        Check for the existance of the home dir, if it doesn't
        exists create it
        """

        log = self._log
        if not os.path.exists(self.home):
            log('directory {} does not exists, creating it'.format(self.home))
            os.mkdir(self.home)

    def _check_binary(self, version: str) -> None:
        """
        Check for the existance of the anaGonda.bin binary file, in
        case that it doesn't exists, generate it
        """

        log = self._log
        binary_file = 'anaGonda-{}.bin'.format(version)
        if not os.path.exists(os.path.join(self.home, binary_file)):
            log('binary version {} not found....'.format(version))
            self._remove_old_versions()
            if self._compile(binary_file):
                self._install_binary(binary_file)
            else:
                print('Could not compile anaGonda binary!')

        library_file = 'anaGonda-{}.so'.format(version)
        if not os.path.exists(os.path.join('.', 'lib', library_file)):
            if self._compile_library(library_file):
                self._install_library(library_file)

    def _remove_old_versions(self) -> None:
        """Seek and remove old anaGonda versions
        """

        log = self._log
        files = [
            x for x in os.listdir(self.home) if x.startswith('anaGonda-')]
        if len(files) > 0:
            log('\tfound {}...'.format(
                ', '.join(files)
            ))
            for f in files:
                log('\tuninstalling {}...'.format(f))
                os.unlink(os.path.join(self.home, f))
        else:
            log('\tno older versions found...')

    def _compile(self, name: str) -> bool:
        """Compile anaGonda application
        """

        self._go_generate()
        return self._compile_commons(
            name,
            'go build -ldflags=\'-s -w\' -o {} {}'.format(
                name, self._compile_path
            )
        )

    def _compile_library(self, name: str) -> bool:
        return self._compile_commons(
            name,
            'go build -buildmode=c-shared -o {} {}'.format(
                name, self._compile_path
            )
        )

    def _compile_commons(self, name: str, arguments: str) -> bool:
        log = self._log
        args = shlex.split(arguments, posix=os.name == 'posix')
        try:
            proc = create_subprocess(
                args, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, shell=False
            )
        except:
            log(
                'we couldn\'t spawn the Go compiler process, it\'s possible '
                'that there is some environent configuration problem. Make '
                'sure that you have Go installed and you have configured '
                'your GOROOT and GOPATH environemnt variables and the go '
                'binary is in your PATH'
            )
            return False

        output, err = proc.communicate()
        if err is not None and err != '':
            log(err.decode('utf8'))

        if output != '':
            log(output.decode('utf8'))

        if not os.path.exists(name):
            return False

        return True

    def _go_generate(self) -> None:
        """Execute go generate in the target directory
        """

        log = self._log
        args = shlex.split(
            'go generate {}'.format(self._compile_path), posix=os.name != 'nt')
        log(' '.join(args))
        try:
            go_gen = create_subprocess(
                args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=False
            )
        except Exception as err:
            log('we couldn\'t execute go generate: %s'.format(err))
            return

        output, error = go_gen.communicate()
        if error is not None and error != '':
            log(error.decode('utf8'))

        if output != '':
            log(output.decode('utf8'))

    def _install_binary(self, binary_file: str) -> None:
        """Install the binary file on bin/anaGonda-version.bin
        """

        log = self._log
        os.rename(binary_file, os.path.join(self.home, binary_file))
        log('binary file installed on {}'.format(self.home))

    def _install_library(self, library_file: str) -> None:
        """Install the library file on lib/anaGonda-version.so
        """

        log = self._log
        destination = os.path.join('.', 'lib', library_file)
        os.rename(library_file, destination)
        log('library file installed on {}'.format(destination))

    def _log(self, msg: str) -> None:
        """Convenience log method
        """

        log_string = '{}: {}'.format(self.__class__.__name__, msg)
        print(log_string)
