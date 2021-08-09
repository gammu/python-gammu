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


import codecs
import sys

import gammu


def main():
    if len(sys.argv) != 2:
        print("This requires parameter: backup file!")
        sys.exit(1)

    charsetencoder = codecs.getencoder(sys.getdefaultencoding())

    filename = sys.argv[1]

    backup = gammu.ReadSMSBackup(filename)

    # Make nested array
    messages = [[message] for message in backup]

    data = gammu.LinkSMS(messages)

    for message in data:
        decoded = gammu.DecodeSMS(message)

        part = message[0]
        print()
        print("{:<15}: {}".format("Number", part["Number"]))
        print("{:<15}: {}".format("Date", str(part["DateTime"])))
        print("{:<15}: {}".format("State", part["State"]))
        print("{:<15}: {}".format("Folder", part["Folder"]))
        print("{:<15}: {}".format("Validity", part["SMSC"]["Validity"]))
        loc = []
        for part in message:
            loc.append(str(part["Location"]))
        print("{:<15}: {}".format("Location(s)", ", ".join(loc)))
        if decoded is None:
            print("\n{}".format(charsetencoder(part["Text"], "replace")[0]))
        else:
            for entries in decoded["Entries"]:
                print()
                print("{:<15}: {}".format("Type", entries["ID"]))
                if entries["Bitmap"] is not None:
                    for bmp in entries["Bitmap"]:
                        print("Bitmap:")
                        for row in bmp["XPM"][3:]:
                            print(row)
                    print()
                if entries["Buffer"] is not None:
                    print("Text:")
                    print(charsetencoder(entries["Buffer"], "replace"))
                    print()


if __name__ == "__main__":
    main()
