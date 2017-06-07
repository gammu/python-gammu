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

from __future__ import print_function
import gammu
import sys


def main():
    state_machine = gammu.StateMachine()
    state_machine.ReadConfig()
    state_machine.Init()

    if len(sys.argv) != 2:
        print('This requires one parameter with memory type!')
        sys.exit(1)

    memory_type = sys.argv[1]

    status = state_machine.GetMemoryStatus(Type=memory_type)

    remain = status['Used']

    start = True

    while remain > 0:
        if start:
            entry = state_machine.GetNextMemory(Start=True, Type=memory_type)
            start = False
        else:
            entry = state_machine.GetNextMemory(
                Location=entry['Location'], Type=memory_type
            )
        remain = remain - 1

        print()
        print('{0:<15}: {1:d}'.format('Location', entry['Location']))
        for v in entry['Entries']:
            print('{0:<15}: {1}'.format(v['Type'], str(v['Value'])))


if __name__ == '__main__':
    main()
