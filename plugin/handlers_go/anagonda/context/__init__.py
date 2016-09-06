
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

from .impl import Impl
from .guru import Guru
from .godef import GoDef
from .motion import Motion
from .registry import Registry
from .autocomplete import AutoComplete

# register contexts
Registry.register(Impl)
Registry.register(Guru)
Registry.register(GoDef)
Registry.register(Motion)
Registry.register(AutoComplete)
