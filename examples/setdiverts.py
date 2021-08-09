#!/usr/bin/env python
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


import sys

import gammu

state_machine = gammu.StateMachine()

if len(sys.argv) > 2:
    state_machine.ReadConfig(Filename=sys.argv[1])
    del sys.argv[1]
else:
    state_machine.ReadConfig()
state_machine.Init()

if len(sys.argv) != 2:
    print("Usage: setdiverts.py NUMBER")
    sys.exit(1)

state_machine.SetCallDivert("AllTypes", "All", sys.argv[1])
diverts = state_machine.GetCallDivert()

for x in diverts:
    print(x)
