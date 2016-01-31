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


def main():
    state_machine = gammu.StateMachine()
    state_machine.ReadConfig()
    state_machine.Init()

    status = state_machine.GetSMSStatus()

    remain = status['SIMUsed'] + status['PhoneUsed'] + status['TemplatesUsed']

    start = True

    try:
        while remain > 0:
            if start:
                sms = state_machine.GetNextSMS(Start=True, Folder=0)
                start = False
            else:
                sms = state_machine.GetNextSMS(
                    Location=sms[0]['Location'], Folder=0
                )
            remain = remain - len(sms)

            for m in sms:
                print()
                print('%-15s: %s' % ('Number', m['Number']))
                print('%-15s: %s' % ('Date', str(m['DateTime'])))
                print('%-15s: %s' % ('State', m['State']))
                print('\n%s' % m['Text'])
    except gammu.ERR_EMPTY:
        # This error is raised when we've reached last entry
        # It can happen when reported status does not match real counts
        print('Failed to read all messages!')


if __name__ == '__main__':
    main()
