
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

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

        args = shlex.split('\'{0}\' -f json autocomplete \'{1}\' c{2}'.format(
            self.binary, self.path, self.offset)
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
        if len(completions) > 0:
            lguide = self._calculate_lguide(completions[1])
            for elem in completions[1]:
                comps.append((
                    '{0}{1} {2} {3}'.format(
                        elem['name'], ' ' * (lguide - len(elem['name'])),
                        elem['class'], elem['type']
                    ), self._snippet(elem)
                ))

        return comps

    def _snippet(self, data):
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
        params = []
        between_parenthesis = False
        split_data = data['type'][begin + 1:end].split(',')
        for param in split_data:
            param = param.replace('{', '\\{').replace('}', '\\}')
            snippet_param = ''
            if '(' in param:
                tmp.append(param)
                between_parenthesis = True
                continue
            elif ')' in param:
                tmp.append(param)
                snippet_param = ','.join(tmp).strip()
                between_parenthesis = False
            else:
                if between_parenthesis:
                    tmp.append(param)
                    continue
                snippet_param = param.strip()

            params.append('${{{0}:{1}}}'.format(len(params) + 1, snippet_param))  # noqa

        return '{0}{1})'.format(snippet, ', '.join(params))

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

        return self.get_binary('gocode')
