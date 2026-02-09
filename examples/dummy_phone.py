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
"""
Dummy driver example.

Test script to test several Gammu operations (usually using dummy driver, but
it depends on config).
"""

import sys

import gammu


def get_all_memory(state_machine, memory_type) -> None:
    status = state_machine.GetMemoryStatus(Type=memory_type)

    remain = status["Used"]

    start = True

    while remain > 0:
        if start:
            entry = state_machine.GetNextMemory(Start=True, Type=memory_type)
            start = False
        else:
            entry = state_machine.GetNextMemory(
                Location=entry["Location"], Type=memory_type
            )
        remain -= 1

        print()
        print(f"{'Location':<15}: {entry['Location']:d}")
        for v in entry["Entries"]:
            if v["Type"] in ("Photo"):
                print(f"{v['Type']:<15}: {repr(v['Value'])[:30]}...")
            else:
                print(f"{v['Type']:<15}: {v['Value']}")


def get_all_calendar(state_machine) -> None:
    status = state_machine.GetCalendarStatus()

    remain = status["Used"]

    start = True

    while remain > 0:
        if start:
            entry = state_machine.GetNextCalendar(Start=True)
            start = False
        else:
            entry = state_machine.GetNextCalendar(Location=entry["Location"])
        remain -= 1

        print()
        print(f"{'Location':<20}: {entry['Location']:d}")
        print(f"{'Type':<20}: {entry['Type']}")
        for v in entry["Entries"]:
            print(f"{v['Type']:<20}: {v['Value']}")


def get_battery_status(state_machine) -> None:
    status = state_machine.GetBatteryCharge()

    for x in status:
        if status[x] != -1:
            print(f"{x:20}: {status[x]}")


def get_all_sms(state_machine):
    status = state_machine.GetSMSStatus()

    remain = status["SIMUsed"] + status["PhoneUsed"] + status["TemplatesUsed"]

    start = True

    while remain > 0:
        if start:
            sms = state_machine.GetNextSMS(Start=True, Folder=0)
            start = False
        else:
            sms = state_machine.GetNextSMS(Location=sms[0]["Location"], Folder=0)
        remain -= len(sms)

    return sms


def print_sms_header(message, folders) -> None:
    print()
    print(f"{'Number':<15}: {message['Number']}")
    print(f"{'Date':<15}: {message['DateTime']}")
    print(f"{'State':<15}: {message['State']}")
    print(
        f"{'Folder':<15}: {folders[message['Folder']]['Name']} {folders[message['Folder']]['Memory']} ({message['Folder']:d})"
    )
    print(f"{'Validity':<15}: {message['SMSC']['Validity']}")


def print_all_sms(sms, folders) -> None:
    for m in sms:
        print_sms_header(m, folders)
        print(f"\n{m['Text']}")


def link_all_sms(sms, folders) -> None:
    data = gammu.LinkSMS([[msg] for msg in sms])

    for x in data:  # noqa: PLR1702
        v = gammu.DecodeSMS(x)

        m = x[0]
        print_sms_header(m, folders)
        loc = [str(m["Location"]) for m in x]
        print(f"{'Location(s)':<15}: {', '.join(loc)}")
        if v is None:
            print(f"\n{m['Text']}")
        else:
            for e in v["Entries"]:
                print()
                print(f"{'Type':<15}: {e['ID']}")
                if e["Bitmap"] is not None:
                    for bmp in e["Bitmap"]:
                        print("Bitmap:")
                        for row in bmp["XPM"][3:]:
                            print(row)
                    print()
                if e["Buffer"] is not None:
                    print("Text:")
                    print(e["Buffer"])
                    print()


def get_all_todo(state_machine) -> None:
    status = state_machine.GetToDoStatus()

    remain = status["Used"]

    start = True

    while remain > 0:
        if start:
            entry = state_machine.GetNextToDo(Start=True)
            start = False
        else:
            entry = state_machine.GetNextToDo(Location=entry["Location"])
        remain -= 1

        print()
        print(f"{'Location':<15}: {entry['Location']:d}")
        print(f"{'Priority':<15}: {entry['Priority']}")
        for v in entry["Entries"]:
            print(f"{v['Type']:<15}: {v['Value']}")


def get_sms_folders(state_machine):
    folders = state_machine.GetSMSFolders()
    for i, folder in enumerate(folders):
        print(f"Folder {i:d}: {folder['Name']} ({folder['Memory']})")
    return folders


def get_set_date_time(state_machine):
    dt = state_machine.GetDateTime()
    print(dt)
    state_machine.SetDateTime(dt)
    return dt


def main() -> None:
    if len(sys.argv) != 2:
        print("This requires one parameter with location of config file!")
        sys.exit(1)

    state_machine = gammu.StateMachine()
    state_machine.ReadConfig(Filename=sys.argv[1])
    state_machine.Init()
    smsfolders = get_sms_folders(state_machine)
    get_all_memory(state_machine, "ME")
    get_all_memory(state_machine, "SM")
    get_all_memory(state_machine, "MC")
    get_all_memory(state_machine, "RC")
    get_all_memory(state_machine, "DC")
    get_battery_status(state_machine)
    get_all_calendar(state_machine)
    get_all_todo(state_machine)
    smslist = get_all_sms(state_machine)
    print_all_sms(smslist, smsfolders)
    link_all_sms(smslist, smsfolders)
    get_set_date_time(state_machine)


if __name__ == "__main__":
    main()
