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
"""Example for reading calendar from phone"""

from __future__ import print_function
import gammu

# Create object for talking with phone
state_machine = gammu.StateMachine()

# Read the configuration (~/.gammurc)
state_machine.ReadConfig()

# Connect to the phone
state_machine.Init()

# Get number of calendar entries
status = state_machine.GetCalendarStatus()

remain = status['Used']

start = True

while remain > 0:
    # Read the entry
    if start:
        entry = state_machine.GetNextCalendar(Start=True)
        start = False
    else:
        entry = state_machine.GetNextCalendar(Location=entry['Location'])
    remain = remain - 1

    # Display it
    print()
    print('{0:<20}: {1:d}'.format('Location', entry['Location']))
    print('{0:<20}: {1}'.format('Type', entry['Type']))
    for v in entry['Entries']:
        print('{0:<20}: {1}'.format(v['Type'], str(v['Value'])))
