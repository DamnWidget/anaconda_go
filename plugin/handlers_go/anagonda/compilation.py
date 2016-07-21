
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import sys
import shlex
from subprocess import PIPE

from process import spawn


class AnagondaCompileError(RuntimeError):
    """Fired on compilation issues
    """


class Target(object):
    """This class encapsulates compilation logic per target
    """

    _library_path = os.path.join(os.path.dirname(__file__), 'lib')
    _binary_path = os.path.join(os.path.dirname(__file__), 'bin')
    _src_path = os.path.join(os.path.dirname(__file__), 'src')
    __computed_cwd = None

    def __init__(self, ctx):
        self._env = {
            'GOROOT': ctx.goroot,
            'GOPATH': ctx.gopath,
            'CGO_ENABLED': '1' if ctx.cgo_enabled else '0'
        }
        self.type = ctx.type
        self.pre_compilation_steps = ctx.steps

    @property
    def cmd(self):
        """Construct the compilation cmd line
        """

        file_name = {'bin': self.bin_name, 'lib': self.lib_name}.get(self.type)
        path = os.path.join({
            'bin': self._binary_path, 'lib': self._binary_path
        }.get(self.type), file_name)
        return 'go build -ldflags\'-s -w\' -buildmode={} -o {} {}'.format(
            {'bin': 'default', 'lib': 'c-shared'}.get(self.type),
            path, self._src_path
        )

    @property
    def cwd(self):
        """Get the configured working directory if any or return OS one
        """

        if self.__computed_cwd is None:
            self.__computed_cwd = getattr(self, 'cwd', os.getcwd())

        return self.__computed_cwd

    @property
    def env(self):
        """Compute the environment to use during compilation
        """

        if self.__computed_env is None:
            self.__computed_env = {}
            for k, v in os.environ.copy():
                if type(k) is not str:
                    k = str(k)
                self.__computed_env[k] = v

            self.__computed_env.update(self._env)

        return self.__computed_env

    @property
    def lib_ext(self):
        """Return back the library extension depending on the platform
        """

        return {'darwin': 'dylib', 'linux': 'so'}.get(sys.platform, 'dll')

    @property
    def lib_name(self):
        """Construct the shared lib file name and return it back
        """

        return 'anaGonda-{0}.{1}'.format(self.ver, self.lib_ext)

    @property
    def bin_name(self):
        """Construct the binary file name and return it back
        """

        ext = 'exe' if os.name != 'posix' else 'bin'
        return 'anaGonda-{0}.{1}'.format(self.ver, ext)

    def compile(self):
        """Compile wrapper
        """

        try:
            self._compile()
        except Exception as e:
            raise AnagondaCompileError(
                'while compiling target {0}: {1}\n'.format(self.type, e)
            )

    def _compile(self):
        """Compile the target
        """

        env = os.environ.copy()
        env.update(self._env)
        pre_compilation_steps = getattr(self, 'pre_compilation_steps', None)
        if pre_compilation_steps is not None:
            for step in pre_compilation_steps:
                args = shlex.split(step['cmd'], posix=os.name == 'posix')
                proc = spawn(
                    args, stdout=PIPE, stderr=PIPE, env=env, cdw=self.cwd
                )
                output, err = proc.communicate()
                if err is not None and len(err) > 0:
                    if sys.version_info >= (3):
                        raise AnagondaCompileError(err.decode('utf8'))
                    else:
                        raise AnagondaCompileError(err)

                if sys.version_info >= (3):
                    print(output.decode('utf8'))
                else:
                    print(output)

        args = shlex.split(self.cmd, posix=os.name == 'posix')
        cmd = spawn(args, stdout=PIPE, stderr=PIPE, env=env, cwd=self.cwd)
        out, err = cmd.communicate()
        if err is not None and len(err) > 0:
            if sys.version_info >= (3):
                raise AnagondaCompileError(err.decode('utf8'))
            else:
                raise AnagondaCompileError(err)

        if sys.version_info >= (3):
            print(output.decode('utf8'))
        else:
            print(output)


class CFFIOffLine(object):
    """Compile a CFFI library off line to steep things up
    """

    def __init__(self, path):
        self._path = path
        self._current_path = os.getcwd()
        self._error = None

    def __enter__(self):
        """Cd into compilation directory and return a ref to self
        """

        os.chdir(self._path)
        return self

    def __exit__(self, *ext):
        """Delete intermediate files and go back to the initial directory
        """

        if self._error is None:
            os.unlink('_anaconda.c')
            os.unlink('_anaconda.o')

        os.chdir(self._current_path)

    def compile(self):
        """Compile a Python ready to import C shared library file for anaGonda
        """

        from cffi import FFI
        try:
            ffi = FFI()
            ffi.set_source(
                '_anagonda',
                '#include "{}"'.format(self._c_header),
                extra_objects=[os.path.join(self._library_path, self._c_shared_lib)],  # noqa
                include_dirs=[self._library_path]
            )

            ffi.cdef('''// AnaGonda C Definitions
                void FreeMemory(char *);
                _Bool SetEnvironment(char *, char *, _Bool);
                _Bool CleanSocket();
                char * GetEnv();
                char * AutoComplete(char *, char *, int);
            ''')

            ffi.compile(verbose=False)
        except Exception as e:
            self._error = 'while compiling ffi_off_line: {}'.format(e)
            raise AnagondaCompileError(self._error)
