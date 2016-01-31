#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
#
# Copyright © 2003 - 2016 Michal Čihař <michal@cihar.com>
#
# This file is part of python-gammu <http://wammu.eu/python-gammu/>
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
Example for reading data from phone and convering it to and from
vCard, vTodo, vCalendar
"""

from __future__ import print_function
import gammu
import sys


def main():
    state_machine = gammu.StateMachine()
    if len(sys.argv) == 2:
        state_machine.ReadConfig(Filename=sys.argv[1])
    else:
        state_machine.ReadConfig()
    state_machine.Init()

    # For calendar entry

    # Read entry from phone
    entry = state_machine.GetNextCalendar(Start=True)

    # Convert it to vCard
    vc_entry = gammu.EncodeVCALENDAR(entry)
    ic_entry = gammu.EncodeICALENDAR(entry)

    # Convert it back to entry
    print(gammu.DecodeVCS(vc_entry))
    print(gammu.DecodeICS(ic_entry))

    # For todo entry

    # Read entry from phone
    entry = state_machine.GetNextToDo(Start=True)

    # Convert it to vCard
    vt_entry = gammu.EncodeVTODO(entry)
    it_entry = gammu.EncodeITODO(entry)

    # Convert it back to entry
    print(gammu.DecodeVCS(vt_entry))
    print(gammu.DecodeICS(it_entry))

    # For memory entry

    # Read entry from phone
    entry = state_machine.GetNextMemory(Start=True, Type='ME')

    # Convert it to vCard
    vc_entry = gammu.EncodeVCARD(entry)

    # Convert it back to entry
    print(gammu.DecodeVCARD(vc_entry))


if __name__ == '__main__':
    main()
