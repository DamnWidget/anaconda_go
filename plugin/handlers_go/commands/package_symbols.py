
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import logging
import traceback
from collections import defaultdict

from ..anagonda.context import guru
from commands.base import Command


class PackageSymbols(Command):
    """Run guru to get a detailed list of the package symbols
    """

    def __init__(self, callback, uid, vid, scope, code, path, buf, go_env):
        self.vid = vid
        self.scope = scope
        self.code = code
        self.path = path
        self.buf = buf
        self.go_env = go_env
        super(PackageSymbols, self).__init__(callback, uid)

    def run(self):
        """Run the command
        """

        try:
            offset = self.code.find('package ') + len('package ') + 1
            with guru.Guru(
                self.scope, 'describe', self.code, self.path,
                    offset, self.buf, self.go_env) as desc:

                symbols = []
                for symbol in self._sort(desc):
                    path, line, col = symbol['pos'].split(':')
                    symbols.append({
                        'filename': path,
                        'line': int(line),
                        'col': int(col),
                        'ident': symbol['name'],
                        'full': symbol['type'],
                        'keyword': symbol['kind'],
                        'show_filename': True
                    })
                self.callback({
                    'success': True,
                    'result': symbols,
                    'uid': self.uid,
                    'vid': self.vid
                })
        except Exception as error:
            logging.error(error)
            logging.debug(traceback.format_exc())
            self.callback({
                'success': False,
                'error': str(error),
                'uid': self.uid,
                'vid': self.vid
            })

    def _sort(self, desc):
        """Sort the output by File -> Vars -> Type -> Funcs
        """

        symbols = []
        aggregated_data = defaultdict(lambda: [])
        for elem in desc.get('package', {}).get('members', []):
            filename = elem['pos'].split(':')[0]
            aggregated_data[filename].append(elem)

        for filename, elems in aggregated_data.items():
            symbols += sorted(
                [e for e in elems if e['kind'] in ['var', 'const']],
                key=lambda x: x['pos']
            )
            symbols += sorted(
                [e for e in elems if e['kind'] == 'type'],
                key=lambda x: x['pos']
            )
            symbols += sorted(
                [e for e in elems if e['kind'] == 'func'],
                key=lambda x: x['pos']
            )
            for e in elems:
                if e['kind'] == 'type':
                    methods = []
                    for method in e.get('methods', []):
                        new_elem = method
                        new_elem['kind'] = 'func'
                        new_elem['type'] = method['name']
                        methods.append(new_elem)
                    symbols += sorted(methods, key=lambda x: x['pos'])

        return symbols
