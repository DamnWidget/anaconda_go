
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details


def importer():
    """Just import commands into context
    """

    # Add any new command import in here
    from anaconda_go.commands.impl import AnacondaGoImpl
    from anaconda_go.commands.goto import AnacondaGoGoto
