
# Copyright (C) 2014 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import sublime

from ..anagonda import anaGonda
from ..anaconda_plugin import Enum, unique


@unique
class RuntimeStatus(Enum):

    """Runtime status unique enumeration
    """

    stopped = 'stopped'
    outdated = 'outdated'
    updated = 'updated'
    broken = 'broken'
    compiling = 'compiling'
    installing = 'installing'
    prepared = 'prepared'
    available = 'available'
    running = 'running'
    stopping = 'stopping'


class Runtime:

    """Anaconda Go runtime
    """

    def __init__(self, root, path, cgo, version):
        self.state = RuntimeStatus.stopped
        self.anagonda = None
        self.start(root, path, cgo, version)

    def start(self, root, path, cgo, version):
        """Start the Go runtime
        """

        if self.state != RuntimeStatus.stopped:
            raise RuntimeError(
                'AnacondaGO: Go Runtime start has been called but the runtime '
                'status is currently {}'.format(self.state.value)
            )

        self._get_anagonda(root, path, cgo)
        self.anagonda.prepare(version)
        self.anagonda.start()

    def _detect_anagonda(self, root, path, cgo):
        """Get and pre-initialize anagonda object
        """

        home = os.path.join(sublime.packages_path(), 'User', 'anaGonda')
        self.anagonda = anaGonda(root, path, cgo, home)
