# vim: expandtab sw=4 ts=4 sts=4:
#
# Copyright © 2003 - 2018 Michal Čihař <michal@cihar.com>
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
"""
Phone communication library - python wrapper for Gammu library.

Datetime and time values returned by Gammu have fixed-offset timezones, with UTC
used for zero offsets. Aware inputs preserve their UTC offset and wall-clock
fields, but not named timezone identities. Naive inputs retain a zero offset.
Offsets must be whole seconds strictly between -24 and 24 hours. Individual
phone backends and file formats may not preserve timezone information.
"""

from gammu._gammu import *  # ruff: ignore[undefined-local-with-import-star]

__version__ = "Gammu {}, python-gammu {}".format(*Version())  # ruff: ignore[undefined-local-with-import-star-usage]
