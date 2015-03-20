#!/usr/bin/env python
#
# Example for usage of GetNextFileFolder, which is oriented at
#
# gammu --getfilesystem
#
# Without argument you get a hierarchical list, provide flat as
# argument and get somethink like (not exactly!)
#
# gammu --getfilesystem -flatall
#
# Matthias Blaesing <matthias.blaesing@rwth-aachen.de>

import gammu
import locale
from optparse import OptionParser
parser = OptionParser(usage="usage: %prog [options]")

parser.add_option("-c", "--config",
                  action="store", type="string",
                  dest="config", default=None,
                  help="Config file path")
parser.add_option("-f", "--flat",
                  action="store_true",
                  dest="flat", default=False,
                  help="Flat listing")
parser.add_option("-l", "--level",
                  action="store_true",
                  dest="level", default=False,
                  help="Level listing")
(options, args) = parser.parse_args()

# Init gammu module
state_machine = gammu.StateMachine()
if options.config is not None:
    state_machine.ReadConfig(Filename=options.config)
else:
    state_machine.ReadConfig()
state_machine.Init()

# Get wished listing from commandline (if provided - else asume level)
# On commandline level or flat can be provided as parameters
if options.flat:
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
            spacer = ""

            for i in range(1, (level-1)):
                spacer = spacer + " |   "
            if(level > 1):
                spacer = spacer + " |-- "

            title = '"' + file_obj["Name"] + '"'
            if file_obj["Folder"]:
                title = "Folder " + title
            print(attrib + spacer + title)
        file_obj = NextFile()


if __name__ == '__main__':
    Main()
