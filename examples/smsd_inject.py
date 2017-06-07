#!/usr/bin/env python
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
"""Sample script to show how to send SMS through SMSD"""

from __future__ import print_function
import gammu.smsd
import sys

smsd = gammu.smsd.SMSD('/etc/gammu-smsdrc')

if len(sys.argv) != 2:
    print('Usage: smsd-inject.py RECIPIENT_NUMBER')
    sys.exit(1)

message = {
    'Text': 'python-gammu testing message',
    'SMSC': {'Location': 1},
    'Number': sys.argv[1]
}

smsd.InjectSMS([message])
