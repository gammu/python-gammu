#!/usr/bin/env python
# vim: expandtab sw=4 ts=4 sts=4:
#
# Copyright © 2003 - 2018 Matthias Blaesing <matthias.blaesing@rwth-aachen.de>
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
Filesystem testing.

This file should provide me with a test frame for the filesystem
functions. It can't be run automatically, but you should be able
to decide, whether the output looks sensible.

BEWARE - the test WILL TOUCH AND WRITE FILESYSTEM!!

I assume you call the script from the directory were it lays and
have the graphic there and you have write permission there and that
there is a file called cgi.jpg to be used as test file

READY:
- DeleteFile
- AddFilePart
- GetFilePart
- GetNextRootFolder
- GetNextFileFolder
- GetFolderListing
- SetFileAttributes
- DeleteFolder
- GetFileSystemStatus
- AddFolder
"""

import argparse
import datetime
import sys
from pathlib import Path

import gammu


def main() -> None:  # noqa: PLR0912, PLR0915, C901
    parser = argparse.ArgumentParser(usage="usage: %(prog)s [options]")

    parser.add_argument(
        "-c",
        "--config",
        action="store",
        type=str,
        dest="config",
        default=None,
        help="Config file path",
    )
    parser.add_argument(
        "-f",
        "--folder",
        action="store",
        type=str,
        dest="folder",
        default=None,
        help="Folder to be used for testing",
    )
    parser.add_argument(
        "-t",
        "--test-file",
        action="store",
        type=str,
        dest="testfile",
        default="./data/cgi.jpg",
        help="Local file to be used for testing",
    )
    args = parser.parse_args()

    if args.folder is None:
        print("You have to select folder where testing will be done!")
        print("And even better, you should read the script before you run it.")
        sys.exit(1)

    if not Path(args.testfile).exists():
        print("You have to select file which will be used for testing!")
        sys.exit(1)

    state_machine = gammu.StateMachine()
    if args.config is not None:
        state_machine.ReadConfig(Filename=args.config)
    else:
        state_machine.ReadConfig()
    state_machine.Init()

    # Check GetFileSystemStatus
    print("Expectation: Info about filesystem usage")
    try:
        fs_info = state_machine.GetFileSystemStatus()
        fs_info["Total"] = fs_info["Free"] + fs_info["Used"]
        print("Used: {Used:d}, Free: {Free:d}, Total: {Total:d}".format(**fs_info))
    except gammu.ERR_NOTSUPPORTED:
        print("You will have to live without this knowledge")

    # Check DeleteFile
    print("\n\nExpectation: Deleting cgi.jpg from memorycard")
    try:
        state_machine.DeleteFile(f"{args.folder}/cgi.jpg")
    except gammu.ERR_FILENOTEXIST:
        print("Oh well - we copy it now ;-) (You SHOULD read this)")

    # Check AddFilePart
    print("\n\nExpectation: Put cgi.jpg onto Memorycard on phone")
    file_object = Path(args.testfile)
    file_content = file_object.read_bytes()
    file_stat = file_object.stat()
    ttime = datetime.datetime.fromtimestamp(file_stat[8])
    file_f = {
        "ID_FullName": args.folder,
        "Name": "cgi.jpg",
        "Modified": ttime,
        "Folder": 0,
        "Level": 1,
        "Used": file_stat[6],
        "Buffer": file_content,
        "Type": "Other",
        "Protected": 0,
        "ReadOnly": 0,
        "Hidden": 0,
        "System": 0,
        "Handle": 0,
        "Pos": 0,
        "Finished": 0,
    }
    while not file_f["Finished"]:
        file_f = state_machine.AddFilePart(file_f)

    # Check GetFilePart
    print("\n\nExpectation: Get cgi.jpg from memorycard and write it as test.jpg")
    file_f = {"ID_FullName": f"{args.folder}/cgi.jpg", "Finished": 0}
    while not file_f["Finished"]:
        file_f = state_machine.GetFilePart(file_f)
    Path("./test.jpg").write_bytes(file_f["Buffer"])

    # Check correct transfer
    print("\n\nExpectation: test.jpg and cgi.jpg to be the same")
    f1 = Path(args.testfile).read_bytes()
    f2 = Path("./test.jpg").read_bytes()
    if f1 == f2:
        print("Same files")
    else:
        print("Files differ!")

    Path("./test.jpg").unlink()

    # Check GetNextRootFolder
    print("\n\nExpectation: Root Folder List")
    try:
        file_obj = state_machine.GetNextRootFolder("")
        while 1:
            print(f"{file_obj['ID_FullName']} - {file_obj['Name']}")
            try:
                file_obj = state_machine.GetNextRootFolder(file_obj["ID_FullName"])
            except gammu.ERR_EMPTY:
                break
    except gammu.ERR_NOTSUPPORTED:
        print("Not supported...")

    # Check GetNextFileFolder
    print("\n\nExpectation: Info for a file of the phone (cgi.jpg)")
    file_f = state_machine.GetNextFileFolder(1)
    while 1:
        if file_f["Name"] != "cgi.jpg":
            file_f = state_machine.GetNextFileFolder(0)
        else:
            attribute = ""
            if file_f["Protected"]:
                attribute += "P"
            if file_f["ReadOnly"]:
                attribute += "R"
            if file_f["Hidden"]:
                attribute += "H"
            if file_f["System"]:
                attribute += "S"
            print(f"ID:         {file_f['ID_FullName']}")
            print(f"Name:       {file_f['Name']}")
            print(f"Folder:     {file_f['Folder']!s}")
            print(f"Used:       {file_f['Used']!s}")
            print(f"Modified:   {file_f['Modified'].strftime('%x %X')}")
            print(f"Type:       {file_f['Type']}")
            print(f"Level:      {file_f['Level']!s}")
            print(f"Attribute:  {attribute}")

            break

    # Check SetFileAttributes
    # Protected is spared, as my mobile nokia 6230i says it's unsupported
    print(
        "\n\nExpectation: Modifying attributes "
        "(readonly=1, protected=0, system=1, hidden=1)"
    )
    state_machine.SetFileAttributes(f"{args.folder}/cgi.jpg", 1, 0, 1, 1)

    # Check GetFolderListing
    print("\n\nExpectation: Listing of cgi.jpg's properties")
    file_f = state_machine.GetFolderListing(args.folder, 1)
    while 1:
        if file_f["Name"] != "cgi.jpg":
            file_f = state_machine.GetFolderListing(args.folder, 0)
        else:
            attribute = ""
            if file_f["Protected"]:
                attribute += "P"
            if file_f["ReadOnly"]:
                attribute += "R"
            if file_f["Hidden"]:
                attribute += "H"
            if file_f["System"]:
                attribute += "S"
            print(f"ID:         {file_f['ID_FullName']}")
            print(f"Name:       {file_f['Name']}")
            print(f"Folder:     {file_f['Folder']!s}")
            print(f"Used:       {file_f['Used']!s}")
            print(f"Modified:   {file_f['Modified'].strftime('%x %X')}")
            print(f"Type:       {file_f['Type']}")
            print(f"Level:      {file_f['Level']!s}")
            print(f"Attribute:  {attribute}")

            break

    # Check DeleteFile
    print("\n\nExpectation: Deletion of cgi.jpg from memorycard")
    try:
        state_machine.DeleteFile(f"{args.folder}cgi.jpg")
        print("Deleted")
    except gammu.ERR_FILENOTEXIST:
        print("Something is wrong ...")

    # Check AddFolder
    print('\n\nExpectation: Creation of a folder on the memorycard "42alpha"')
    state_machine.AddFolder(args.folder), "42alpha"

    # Check GetFolderListing again *wired*
    print("\n\nExpectation: Print properties of newly created folder")
    file_f = state_machine.GetFolderListing(args.folder, 1)
    while 1:
        if file_f["Name"] != "42alpha":
            file_f = state_machine.GetFolderListing(args.folder, 0)
        else:
            attribute = ""
            if file_f["Protected"]:
                attribute += "P"
            if file_f["ReadOnly"]:
                attribute += "R"
            if file_f["Hidden"]:
                attribute += "H"
            if file_f["System"]:
                attribute += "S"
            print(f"ID:         {file_f['ID_FullName']}")
            print(f"Name:       {file_f['Name']}")
            print(f"Folder:     {file_f['Folder']!s}")
            print(f"Used:       {file_f['Used']!s}")
            print(f"Modified:   {file_f['Modified'].strftime('%x %X')}")
            print(f"Type:       {file_f['Type']}")
            print(f"Level:      {file_f['Level']!s}")
            print(f"Attribute:  {attribute}")

            break

    # Check DeleteFolder
    print('\n\nExpectation: Deletion of previously created folder "42alpha"')
    state_machine.DeleteFolder(f"{args.folder}/42alpha")


if __name__ == "__main__":
    main()
