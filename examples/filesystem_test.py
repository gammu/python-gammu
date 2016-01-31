#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
#
# Copyright © 2003 - 2016 Matthias Blaesing <matthias.blaesing@rwth-aachen.de>
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
"""
This file should provide me with a test frame for the filesystem
functions. It can't be run automatically, but you should be able
to decide, wheather the output looks sensible

BEWARE - the test WILL TOUCH AND WRITE FILESYSTEM!!

I asume you call the script from the directory were it lays and
have the grafic there and you have write permission there and that
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

from __future__ import print_function
import gammu
import os
import datetime
import sys
from optparse import OptionParser


def main():
    parser = OptionParser(usage="usage: %prog [options]")

    parser.add_option("-c", "--config",
                      action="store", type="string",
                      dest="config", default=None,
                      help="Config file path")
    parser.add_option("-f", "--folder",
                      action="store", type="string",
                      dest="folder", default=None,
                      help="Folder to be used for testing")
    parser.add_option("-t", "--test-file",
                      action="store", type="string",
                      dest="testfile", default="./data/cgi.jpg",
                      help="Local file to be used for testing")
    (options, args) = parser.parse_args()

    if options.folder is None:
        print("You have to select folder where testing will be done!")
        print("And even better, you should read the script before you run it.")
        sys.exit(1)

    if not os.path.exists(options.testfile):
        print("You have to select file which will be used for testing!")
        sys.exit(1)

    state_machine = gammu.StateMachine()
    if options.config is not None:
        state_machine.ReadConfig(Filename=options.config)
    else:
        state_machine.ReadConfig()
    state_machine.Init()

    # Check GetFileSystemStatus
    print("Expection: Info about filesystem usage")
    try:
        fs_info = state_machine.GetFileSystemStatus()
        fs_info["Total"] = fs_info["Free"] + fs_info["Used"]
        print("Used: %(Used)d, Free: %(Free)d, Total: %(Total)d" % fs_info)
    except gammu.ERR_NOTSUPPORTED:
        print("You will have to live without this knowledge")

    # Check DeleteFile
    print("\n\nExpection: Deleting cgi.jpg from memorycard")
    try:
        state_machine.DeleteFile(unicode(options.folder + "/cgi.jpg"))
    except gammu.ERR_FILENOTEXIST:
        print("Oh well - we copy it now ;-) (You SHOULD read this)")

    # Check AddFilePart
    print("\n\nExpection: Put cgi.jpg onto Memorycard on phone")
    file_handle = open(options.testfile, "rb")
    file_stat = os.stat(options.testfile)
    ttime = datetime.datetime.fromtimestamp(file_stat[8])
    file_f = {
        "ID_FullName": options.folder,
        "Name": u"cgi.jpg",
        "Modified": ttime,
        "Folder": 0,
        "Level": 1,
        "Used": file_stat[6],
        "Buffer": file_handle.read(),
        "Type": "Other",
        "Protected": 0,
        "ReadOnly": 0,
        "Hidden": 0,
        "System": 0,
        "Handle": 0,
        "Pos": 0,
        "Finished": 0
    }
    while not file_f["Finished"]:
        file_f = state_machine.AddFilePart(file_f)

    # Check GetFilePart
    print(
        "\n\nExpection: Get cgi.jpg from memorycard and write it as test.jpg"
    )
    with open('./test.jpg', 'wb') as handle:
        file_f = {
            "ID_FullName": options.folder + "/cgi.jpg",
            "Finished": 0
        }
        while not file_f["Finished"]:
            file_f = state_machine.GetFilePart(file_f)
        handle.write(file_f["Buffer"])
        handle.flush()

    # Check correct transfer
    print("\n\nExpection: test.jpg and cgi.jpg to be the same")
    f1 = open(options.testfile, "rb")
    f2 = open("./test.jpg", "rb")
    if f1.read() == f2.read():
        print("Same files")
    else:
        print("Files differ!")

    os.remove("./test.jpg")

    # Check GetNextRootFolder
    print("\n\nExpection: Root Folder List")
    try:
        file_obj = state_machine.GetNextRootFolder(u"")
        while 1:
            print(file_obj["ID_FullName"] + " - " + file_obj["Name"])
            try:
                file_obj = state_machine.GetNextRootFolder(
                    file_obj["ID_FullName"]
                )
            except gammu.ERR_EMPTY:
                break
    except gammu.ERR_NOTSUPPORTED:
        print("Not supported...")

    # Check GetNextFileFolder
    print("\n\nExpection: Info for a file of the phone (cgi.jpg)")
    file_f = state_machine.GetNextFileFolder(1)
    while 1:
        if file_f["Name"] != "cgi.jpg":
            file_f = state_machine.GetNextFileFolder(0)
        else:
            attribute = ""
            if file_f["Protected"]:
                attribute = attribute + "P"
            if file_f["ReadOnly"]:
                attribute = attribute + "R"
            if file_f["Hidden"]:
                attribute = attribute + "H"
            if file_f["System"]:
                attribute = attribute + "S"
            print((
                "ID:         " + file_f["ID_FullName"] + "\n" +
                "Name:       " + file_f["Name"] + "\n" +
                "Folder:     " + str(file_f["Folder"]) + "\n" +
                "Used:       " + str(file_f["Used"]) + "\n" +
                "Modified:   " + file_f["Modified"].strftime("%x %X") + "\n" +
                "Type:       " + file_f["Type"] + "\n" +
                "Level:      " + str(file_f["Level"]) + "\n" +
                "Attribute:  " + attribute
            ))

            break

    # Check SetFileAttributes
    # Protected is spared, as my mobile nokia 6230i says it's unsupported
    print(
        "\n\nExpection: Modifying attributes "
        "(readonly=1, protected=0, system=1, hidden=1)"
    )
    state_machine.SetFileAttributes(
        unicode(options.folder + "/cgi.jpg"), 1, 0, 1, 1
    )

    # Check GetFolderListing
    print("\n\nExpection: Listing of cgi.jpg's properties")
    file_f = state_machine.GetFolderListing(unicode(options.folder), 1)
    while 1:
        if file_f["Name"] != "cgi.jpg":
            file_f = state_machine.GetFolderListing(unicode(options.folder), 0)
        else:
            attribute = ""
            if file_f["Protected"]:
                attribute = attribute + "P"
            if file_f["ReadOnly"]:
                attribute = attribute + "R"
            if file_f["Hidden"]:
                attribute = attribute + "H"
            if file_f["System"]:
                attribute = attribute + "S"
            print((
                "ID:         " + file_f["ID_FullName"] + "\n" +
                "Name:       " + file_f["Name"] + "\n" +
                "Folder:     " + str(file_f["Folder"]) + "\n" +
                "Used:       " + str(file_f["Used"]) + "\n" +
                "Modified:   " + file_f["Modified"].strftime("%x %X") + "\n" +
                "Type:       " + file_f["Type"] + "\n" +
                "Level:      " + str(file_f["Level"]) + "\n" +
                "Attribute:  " + attribute
            ))

            break

    # Check DeleteFile
    print("\n\nExpection: Deletion of cgi.jpg from memorycard")
    try:
        state_machine.DeleteFile(unicode(options.folder + "cgi.jpg"))
        print("Deleted")
    except gammu.ERR_FILENOTEXIST:
        print("Something is wrong ...")

    # Check AddFolder
    print("\n\nExpection: Creation of a folder on the memorycard \"42alpha\"")
    file_f = state_machine.AddFolder(unicode(options.folder), u"42alpha")

    # Check GetFolderListing again *wired*
    print("\n\nExpection: Print properties of newly created folder")
    file_f = state_machine.GetFolderListing(unicode(options.folder), 1)
    while 1:
        if file_f["Name"] != "42alpha":
            file_f = state_machine.GetFolderListing(unicode(options.folder), 0)
        else:
            attribute = ""
            if file_f["Protected"]:
                attribute = attribute + "P"
            if file_f["ReadOnly"]:
                attribute = attribute + "R"
            if file_f["Hidden"]:
                attribute = attribute + "H"
            if file_f["System"]:
                attribute = attribute + "S"
            print((
                "ID:         " + file_f["ID_FullName"] + "\n" +
                "Name:       " + file_f["Name"] + "\n" +
                "Folder:     " + str(file_f["Folder"]) + "\n" +
                "Used:       " + str(file_f["Used"]) + "\n" +
                "Modified:   " + file_f["Modified"].strftime("%x %X") + "\n" +
                "Type:       " + file_f["Type"] + "\n" +
                "Level:      " + str(file_f["Level"]) + "\n" +
                "Attribute:  " + attribute
            ))

            break

    # Check DeleteFolder
    print("\n\nExpection: Deletion of previously created folder \"42alpha\"")
    state_machine.DeleteFolder(unicode(options.folder + "/42alpha"))


if __name__ == '__main__':
    main()
