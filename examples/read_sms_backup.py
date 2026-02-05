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


def main() -> None:
    if len(sys.argv) != 2:
        print("This requires parameter: backup file!")
        sys.exit(1)

    charsetencoder = codecs.getencoder(sys.getdefaultencoding())

    filename = sys.argv[1]

    backup = gammu.ReadSMSBackup(filename)

    # Make nested array
    messages = [[message] for message in backup]

    data = gammu.LinkSMS(messages)

    for message in data:  # noqa: PLR1702
        decoded = gammu.DecodeSMS(message)

        part = message[0]
        print()
        print(f"{'Number':<15}: {part['Number']}")
        print(f"{'Date':<15}: {part['DateTime']!s}")
        print(f"{'State':<15}: {part['State']}")
        print(f"{'Folder':<15}: {part['Folder']}")
        print(f"{'Validity':<15}: {part['SMSC']['Validity']}")
        loc = []
        for part in message:
            loc.append(str(part["Location"]))
        print(f"{'Location(s)':<15}: {', '.join(loc)}")
        if decoded is None:
            print(f"\n{charsetencoder(part['Text'], 'replace')[0]}")
        else:
            for entries in decoded["Entries"]:
                print()
                print(f"{'Type':<15}: {entries['ID']}")
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
