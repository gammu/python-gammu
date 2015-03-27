#!/usr/bin/env python

from __future__ import print_function
import gammu
import os
import sys


def main():
    if len(sys.argv) != 3:
        print('This requires two parameters: file to upload and path!')
        sys.exit(1)

    with open(sys.argv[1], 'rb') as handle:
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
        'Finished': 0,
        'Folder': 0,
        'Level': 0,
        'Type': 'Other',
        "Pos": 0,
    }

    while not file_f['Finished']:
        file_f = state_machine.AddFilePart(file_f)


if __name__ == "__main__":
    main()
