
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

"""AnacondaGO is a Go linting/autocompleter/IDE for Sublime Text 3
"""


import sublime
from anaconda_go.lib import go
from anaconda_go.plugin_version import anaconda_required_version

try:
    from Anaconda.version import version as anaconda_version
except ImportError:
    try:
        from anaconda.version import version as anaconda_version
    except ImportError:
        anaconda_version = (0, 0, 0)
    else:
        from anaconda_go.commands import *
        from anaconda_go.listeners import *
else:
    from anaconda_go.commands import *
    from anaconda_go.listeners import *


def plugin_loaded():
    if anaconda_required_version > anaconda_version:
        if sublime.ok_cancel_dialog(
            'AnacondaGO requires version {} or better of anaconda but '
            '{}'.format(
                '.'.join(str(i) for i in anaconda_required_version),
                '{} is installed'.format(
                    anaconda_version) if anaconda_version > (0, 0, 0) else 'is not installed'  # noqa
                ), 'Install Now'
        ):
            def on_installed():
                go.init()
                # sublime.message_dialog('Please, restart your Sublime Text')

            pkg = 'Package Control.package_control.package_installer'
            module = __import__(
                pkg, globals(), locals(), ['Package_installer'])
            t = module.PackageInstallerThread(
                module.PackageManager(), 'Anaconda', on_installed
            )
            t.start()
            module.ThreadProgress(
                t,
                'Installing dependency Anaconda',
                'Package Anaconda successfully installed',
            )
    else:
        go.init()
