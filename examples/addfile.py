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


import os
import sys

import gammu


def main():
    if len(sys.argv) != 3:
        print("This requires two parameters: file to upload and path!")
        sys.exit(1)

    with open(sys.argv[1], "rb") as handle:
        data = handle.read()

    state_machine = gammu.StateMachine()
    state_machine.ReadConfig()
    state_machine.Init()

    # Check AddFilePart
    print("\n\nExpection: Put specified file onto Memorycard on phone")
    file_f = {
        "ID_FullName": sys.argv[2],
        "Name": os.path.basename(sys.argv[1]),
        "Buffer": data,
        "Protected": 0,
        "ReadOnly": 0,
        "Hidden": 0,
        "System": 0,
        "Finished": 0,
        "Folder": 0,
        "Level": 0,
        "Type": "Other",
        "Pos": 0,
    }

    while not file_f["Finished"]:
        file_f = state_machine.AddFilePart(file_f)


if __name__ == "__main__":
    main()
