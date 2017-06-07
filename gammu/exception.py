# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
#
# Copyright © 2003 - 2017 Michal Čihař <michal@cihar.com>
#
# This file is part of python-gammu <https://wammu.eu/python-gammu/>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
'''
Gammu exceptions.
'''

import gammu._gammu

# Import base exception
from gammu import GSMError

__all__ = [
    'GSMError',
]

# Import all exceptions
for _name in dir(gammu._gammu):
    if not _name.startswith('ERR_'):
        continue
    _temp = __import__('gammu._gammu', globals(), locals(), [_name], 0)
    locals()[_name] = getattr(_temp, _name)
    __all__.append(_name)

# Cleanup
del _name
del _temp
del gammu
