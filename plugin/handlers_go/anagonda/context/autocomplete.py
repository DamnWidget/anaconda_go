
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import sys
import json
import shlex
from subprocess import PIPE

from process import spawn

from .error import AnaGondaError
from .base import AnaGondaContext

_go_get = 'github.com/nsf/gocode'


class AutoCompleteError(AnaGondaError):
    """Fired on autocompletion errors
    """


class AutoComplete(AnaGondaContext):
    """Context to run the gocode tool into anaconda_go
    """

    def __init__(self, code, path, offset, add_params, env_ctx):
        self._bin_found = None
        self.path = path
        self.offset = offset
        self.add_params = add_params
        self.code = code.encode() if sys.version_info >= (3,) else code
        super(AutoComplete, self).__init__(env_ctx, _go_get)

    def __enter__(self):
        """Check binary existence and perform the command
        """

        super(AutoComplete, self).__enter__()
        if self._bin_found is False:
            raise AutoCompleteError('{} not found...'.format(self.binary))

        return self.autocomplete()

    def autocomplete(self):
        """Autocomplete the word under cursor using the given data
        """

        args = shlex.split('{0} -f json autocomplete {1} c{2}'.format(
            self.binary, self.path, self.offset), posix=os.name != 'nt'
        )
        print(' '.join(args))
        gocode = spawn(
            args, stdin=PIPE, stdout=PIPE, stderr=PIPE, env=self.env
        )
        out, err = gocode.communicate(self.code)
        if err is not None and len(err) > 0:
            if sys.version_info >= (3,):
                err = err.decode('utf8')
            raise AutoCompleteError(err)

        if sys.version_info >= (3,):
            out = out.decode('utf8')

        try:
            completions = json.loads(out)
        except Exception as error:
            raise AutoCompleteError(error)

        comps = []
        lguide = self._calculate_lguide(completions[1])
        if len(completions) > 0:
            for elem in completions[1]:
                comps.append((
                    '{0}{1} {2} {3}'.format(
                        elem['name'], ' ' * (lguide - len(elem['name'])),
                        elem['class'], elem['type']
                    ), self._snipet(elem)
                ))

        return comps

    def _snipet(self, data):
        """Compose an snippet for the auto completion
        """

        if not self.add_params or data['class'] != 'func':
            return data['name']

        snippet = '{0}('.format(data['name'])
        begin = data['type'].find('(')
        if begin == -1:
            return data['name']

        end = -1
        paren_found = 1
        for i in range(begin + 1, len(data['type'])):
            if data['type'][i] == '(':
                paren_found += 1
            elif data['type'][i] == ')':
                paren_found -= 1
            if paren_found == 0:
                if i < len(data['type']):
                    end = i
                    break

        if end == -1:
            return data['name']

        tmp = []
        count = 1
        split_data = data['type'][begin+1:end].split(',')
        for param in split_data:
            param = param.replace('{', '\\{').replace('}', '\\}')
            snippet_param = ''
            if '(' in param:
                tmp.append(param)
            elif ')' in param:
                tmp.append(param)
                snippet_param = ','.join(tmp).strip()
            else:
                snippet_param = param.strip()

            snippet_param = '${{{0}:{1}}}'.format(count, snippet_param)
            if count < len(split_data):
                snippet_param = '{0}, '.format(snippet_param)
            snippet = '{0}{1}'.format(snippet, snippet_param)
            count += 1

        return '{0})'.format(snippet)

    def _calculate_lguide(self, comps):
        """Calculate the max string for completions and return it back
        """

        lguide = 0
        for elem in comps:
            comp_string = elem['name']
            lguide = max(lguide, len(comp_string))

        return lguide

    @property
    def binary(self):
        """Return back the binary path
        """

        return os.path.join(self.env['GOPATH'], 'bin', 'gocode')
