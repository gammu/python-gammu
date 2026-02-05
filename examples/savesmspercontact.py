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


import errno
import os
import re

import gammu


def createFolderIfNotExist(path) -> None:
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def getInternationalizedNumber(number):
    if not number:
        return "Unknown"

    if number.startswith("0"):
        return number.replace("0", "+49", 1)
    return number


def getFilename(mydir, mysms):
    if mysms[0]["DateTime"]:
        return mysms[0]["DateTime"].strftime("%Y-%m-%d-%Hh%Mm%Ss")

    # no date available so calculate unknown number
    myfiles = os.listdir(mydir)

    nextitem = 0
    for i in myfiles:
        match = re.match(r"^Unknown-([0-9]*)", i)
        if match and int(match.group(1)) > nextitem:
            nextitem = int(match.group(1))

    return f"Unknown-{nextitem + 1!s}"


def saveSMS(mysms, all_contacts) -> None:
    my_number = getInternationalizedNumber(mysms[0]["Number"])

    try:
        mydir = all_contacts[my_number]
    except KeyError:
        mydir = my_number

    createFolderIfNotExist(mydir)

    myfile = getFilename(mydir, mysms)

    with open(os.path.join(mydir, myfile), "a", encoding="utf-8") as handle:
        handle.writelines(i["Text"] for i in mysms)
        handle.write("\n")


def getContacts(state_machine):
    # Get all contacts
    remaining = state_machine.GetMemoryStatus(Type="SM")["Used"]
    contacts = {}

    start = True

    try:
        while remaining > 0:
            if start:
                memory_entry = state_machine.GetNextMemory(Start=True, Type="SM")
                start = False
            else:
                memory_entry = state_machine.GetNextMemory(
                    Location=memory_entry["Location"], Type="SM"
                )
                remaining -= 1

            numbers = []
            for entry in memory_entry["Entries"]:
                if entry["Type"] == "Text_FirstName":
                    name = entry["Value"]
                else:
                    numbers.append(getInternationalizedNumber(entry["Value"]))

            for number in numbers:
                contacts[number] = name

    except gammu.ERR_EMPTY:
        # error is raised if memory is empty (this induces wrong reported
        # memory status)
        print("Failed to read contacts!")

    return contacts


def getAndDeleteAllSMS(state_machine):
    # Read SMS memory status ...
    memory = state_machine.GetSMSStatus()
    # ... and calculate number of messages
    remaining = memory["SIMUsed"] + memory["PhoneUsed"]

    # Get all sms
    start = True
    entries = []

    try:
        while remaining > 0:
            if start:
                entry = state_machine.GetNextSMS(Folder=0, Start=True)
                start = False
            else:
                entry = state_machine.GetNextSMS(
                    Folder=0, Location=entry[0]["Location"]
                )

            remaining -= 1
            entries.append(entry)

            # delete retrieved sms
            state_machine.DeleteSMS(Folder=0, Location=entry[0]["Location"])

    except gammu.ERR_EMPTY:
        # error is raised if memory is empty (this induces wrong reported
        # memory status)
        print("Failed to read messages!")

    # Link all SMS when there are concatenated messages
    return gammu.LinkSMS(entries)


def main() -> None:
    # Get all contacts
    state_machine = gammu.StateMachine()
    state_machine.ReadConfig()
    state_machine.Init()
    contacts = getContacts(state_machine)
    state_machine.Terminate()

    # Get all sms
    # why in two steps? ERR_TIMEOUT is raised without closing the connection
    state_machine = gammu.StateMachine()
    state_machine.ReadConfig()
    state_machine.Init()
    messages = getAndDeleteAllSMS(state_machine)
    state_machine.Terminate()

    for message in messages:
        saveSMS(message, contacts)


if __name__ == "__main__":
    main()
