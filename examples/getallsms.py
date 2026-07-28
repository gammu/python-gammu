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


import gammu


def get_next_sms(state_machine, previous):
    if previous is None:
        return state_machine.GetNextSMS(Start=True, Folder=0)
    return state_machine.GetNextSMS(Location=previous[0]["Location"], Folder=0)


def main() -> None:
    state_machine = gammu.StateMachine()
    state_machine.ReadConfig()
    state_machine.Init()

    status = state_machine.GetSMSStatus()

    remain = status["SIMUsed"] + status["PhoneUsed"] + status["TemplatesUsed"]

    sms = None
    while remain > 0:
        try:
            sms = get_next_sms(state_machine, sms)
        except gammu.ERR_EMPTY:
            # This error is raised when we've reached last entry
            # It can happen when reported status does not match real counts
            print("Failed to read all messages!")
            break
        remain -= len(sms)

        for message in sms:
            print()
            print(f"{'Number':<15}: {message['Number']}")
            print(f"{'Date':<15}: {message['DateTime']!s}")
            print(f"{'State':<15}: {message['State']}")
            print(f"\n{message['Text']}")


if __name__ == "__main__":
    main()
