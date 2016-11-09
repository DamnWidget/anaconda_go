
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

ANACONDA_PLUGIN_AVAILABLE = False

try:
    from anaconda.anaconda_lib.worker import Worker
    from anaconda.listeners import linting, completion
    from anaconda.anaconda_lib.decorators import timeit
    from anaconda.anaconda_lib.callback import Callback
    from anaconda.anaconda_lib.jediusages import JediUsages
    from anaconda.version import version as anaconda_version
    from anaconda.anaconda_lib.helpers import get_window_view
    from anaconda.anaconda_lib.progress_bar import ProgressBar
    from anaconda.anaconda_lib.enum import Enum, IntEnum, unique
    from anaconda.anaconda_lib.explore_panel import ExplorerPanel
    from anaconda.anaconda_lib import helpers as anaconda_helpers
    from anaconda.anaconda_lib.helpers import is_code, create_subprocess
    from anaconda.anaconda_lib.linting import sublime as anaconda_sublime
    from anaconda.anaconda_lib.helpers import get_settings as aget_settings
    from anaconda.anaconda_lib import typing
except ImportError:
    try:
        from Anaconda.anaconda_lib.worker import Worker
        from Anaconda.listeners import linting, completion
        from Anaconda.anaconda_lib.decorators import timeit
        from Anaconda.anaconda_lib.callback import Callback
        from Anaconda.anaconda_lib.jediusages import JediUsages
        from Anaconda.version import version as anaconda_version
        from Anaconda.anaconda_lib.helpers import get_window_view
        from Anaconda.anaconda_lib.progress_bar import ProgressBar
        from Anaconda.anaconda_lib.enum import Enum, IntEnum, unique
        from Anaconda.anaconda_lib.explore_panel import ExplorerPanel
        from Anaconda.anaconda_lib import helpers as anaconda_helpers
        from Anaconda.anaconda_lib.helpers import is_code, create_subprocess
        from Anaconda.anaconda_lib.linting import sublime as anaconda_sublime
        from Anaconda.anaconda_lib.helpers import get_settings as aget_settings  # noqa
        from Anaconda.anaconda_lib import typing
    except ImportError as error:
        print(str(error))
        raise RuntimeError('Anaconda plugin is not installed!')
    else:
        ANACONDA_PLUGIN_AVAILABLE = True
else:
    ANACONDA_PLUGIN_AVAILABLE = True


__all__ = ['ANACONDA_PLUGIN_AVAILABLE']

if ANACONDA_PLUGIN_AVAILABLE:
    __all__ += [
        'Worker', 'Callback', 'ProgressBar', 'anaconda_sublime', 'is_code',
        'anaconda_version', 'linting', 'anaconda_helpers', 'timeit',
        'create_subprocess', 'Enum', 'IntEnum', 'unique', 'typing',
        'get_window_view', 'JediUsages', 'completion', 'aget_settings',
        'ExplorerPanel'
    ]
