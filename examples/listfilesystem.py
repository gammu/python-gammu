#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
#
# Copyright © 2003 - 2017 Matthias Blaesing <matthias.blaesing@rwth-aachen.de>
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
Example for usage of GetNextFileFolder, which is oriented at

gammu --getfilesystem

Without argument you get a hierarchical list, provide flat as
argument and get somethink like (not exactly!)

gammu --getfilesystem -flatall
"""

from __future__ import print_function
import gammu
import locale
import argparse
parser = argparse.ArgumentParser(usage="usage: %(prog)s [options]")

parser.add_argument("-c", "--config",
                    action="store", type=str,
                    dest="config", default=None,
                    help="Config file path")
parser.add_argument("-f", "--flat",
                    action="store_true",
                    dest="flat", default=False,
                    help="Flat listing")
parser.add_argument("-l", "--level",
                    action="store_true",
                    dest="level", default=False,
                    help="Level listing")
args = parser.parse_args()

# Init gammu module
state_machine = gammu.StateMachine()
if args.config is not None:
    state_machine.ReadConfig(Filename=args.config)
else:
    state_machine.ReadConfig()
state_machine.Init()

# Get wished listing from commandline (if provided - else asume level)
# On commandline level or flat can be provided as parameters
if args.flat:
    mode = "flat"
else:
    mode = "level"

# Set locale to default locale (here relevant for printing of date)
locale.setlocale(locale.LC_ALL, '')


# Wrapper around GetNextFileFolder, catching gammu.ERR_EMPTY
# for me, which should be after the last entry and returning "None"
#
# GetNextFileFolder gives us a dict with:
# 'Name' => Symbolic Name of the file (String)
# 'ID_FullName' => unique ID of the file (String)
# 'Used' => space used in bytes (integer)
# 'Modified' => Date of last change (datetime)
# 'Type' => Filetype as reported by phone (String)
# 'Folder' => Entry is a Folder (Bool)
# 'Level' => On which level of FS (Integer)
# 'Buffer' => ?? (String)
# File Attributes (Bool):
# 'Protected'
# 'ReadOnly'
# 'Hidden'
# 'System'
def NextFile(start=0):
    try:
        return state_machine.GetNextFileFolder(start)
    except gammu.ERR_EMPTY:
        return None


# Format File Attributes as String as a shorted Version
def FileToAttributeString(file_obj, filled=1):
    protected = readonly = hidden = system = ""
    if filled:
        protected = readonly = hidden = system = u" "
    if file_obj["Protected"]:
        protected = u"P"
    if file_obj["ReadOnly"]:
        readonly = u"R"
    if file_obj["Hidden"]:
        hidden = u"H"
    if file_obj["System"]:
        system = u"S"
    return protected + readonly + hidden + system


def Main():
    # Make sure we reset the pointer of the current entry to the first
    file_obj = NextFile(1)

    # Iterate over Files and print the Info
    while file_obj:
        if mode == "flat":
            # Output:
            # <ID>;<NAME>;<TYPE>;<MODDATE>;<SIZE>;<ATTRIBUTES>
            # We have to catch the situations, where no Modification Time is
            # provided
            try:
                time = file_obj["Modified"].strftime("%x %X") + ";"
            except AttributeError:
                time = ";"

            print((
                file_obj["ID_FullName"] + ";" +
                file_obj["Name"] + ";" +
                file_obj["Type"] + ";" +
                time + str(file_obj["Used"]) + ";" +
                FileToAttributeString(file_obj, 0)
            ))
        elif mode == "level":
            attrib = FileToAttributeString(file_obj, 1)
            level = file_obj["Level"]

            spacer = " |   " * (level - 2)

            if level > 1:
                spacer += " |-- "

            title = '"' + file_obj["Name"] + '"'
            if file_obj["Folder"]:
                title = "Folder " + title
            print(attrib + spacer + title)
        file_obj = NextFile()


if __name__ == '__main__':
    Main()
