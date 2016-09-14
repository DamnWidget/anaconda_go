
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details


class Explorer(object):
    """Helper class to normalize output given by explorer tools
    """

    def __init__(self, definitions):
        self._definitions = definitions

    @property
    def definition(self):
        """Normalize Guru and Godef definitions
        """

        if self._definitions['tool'] == 'guru':
            path, line, col = self._definitions['objpos'].split(':')
            return [(path, int(line), int(col))]

        return [(
            self._definitions['filename'],
            self._definitions['line'],
            self._definitions['column'])
        ]

    def to_jump(self):
        """Normalize to JediUsages format
        """

        return [
            (e['filename'], e['line'], e['col'])
            for e in self._definitions['decls']
        ]

    def to_explore(self):
        """Normalize motion output for explorer mode
        """

        return self._definitions['decls']
