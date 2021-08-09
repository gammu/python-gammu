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

state_machine = gammu.StateMachine()
state_machine.ReadConfig()
state_machine.Init()

status = state_machine.GetSMSStatus()

remain = status["SIMUsed"] + status["PhoneUsed"] + status["TemplatesUsed"]

sms = []
start = True

try:
    while remain > 0:
        if start:
            cursms = state_machine.GetNextSMS(Start=True, Folder=0)
            start = False
        else:
            cursms = state_machine.GetNextSMS(Location=cursms[0]["Location"], Folder=0)
        remain = remain - len(cursms)
        sms.append(cursms)
except gammu.ERR_EMPTY:
    # This error is raised when we've reached last entry
    # It can happen when reported status does not match real counts
    print("Failed to read all messages!")

data = gammu.LinkSMS(sms)

for x in data:
    v = gammu.DecodeSMS(x)

    m = x[0]
    print()
    print("{:<15}: {}".format("Number", m["Number"]))
    print("{:<15}: {}".format("Date", str(m["DateTime"])))
    print("{:<15}: {}".format("State", m["State"]))
    print("{:<15}: {}".format("Folder", m["Folder"]))
    print("{:<15}: {}".format("Validity", m["SMSC"]["Validity"]))
    loc = []
    for m in x:
        loc.append(str(m["Location"]))
    print("{:<15}: {}".format("Location(s)", ", ".join(loc)))
    if v is None:
        print("\n{}".format(m["Text"]))
    else:
        for e in v["Entries"]:
            print()
            print("{:<15}: {}".format("Type", e["ID"]))
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
