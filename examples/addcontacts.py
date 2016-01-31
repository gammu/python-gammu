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

from __future__ import print_function
import gammu
import sys


def main():
    if len(sys.argv) != 3:
        print(
            'This requires two parameters: '
            'memory_type and backup file (eg. vcard)!'
        )
        sys.exit(1)

    state_machine = gammu.StateMachine()
    state_machine.ReadConfig()
    state_machine.Init()

    memory = sys.argv[1]
    filename = sys.argv[2]

    backup = gammu.ReadBackup(filename)

    for item in backup['PhonePhonebook']:
        item['MemoryType'] = memory
        loc = state_machine.AddMemory(item)
        print(('Added item to location %d' % loc))


if __name__ == '__main__':
    main()
