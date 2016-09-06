
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details


class AnaGondaError(RuntimeError):
    """Base AnaGonda error
    """


class RegistryError(AnaGondaError):
    """Fired when an error is encountered in the registry
    """


class GoGetError(AnaGondaError):
    """Raised on go get errors
    """
