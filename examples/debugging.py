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


import sys

import gammu


def main():
    # Global debug level
    gammu.SetDebugFile(sys.stderr)
    gammu.SetDebugLevel("textall")

    state_machine = gammu.StateMachine()
    state_machine.ReadConfig()

    # Use global debug stub regardless configuration
    c = state_machine.GetConfig(0)
    c["UseGlobalDebugFile"] = True
    state_machine.SetConfig(0, c)

    state_machine.Init()

    manufacturer = state_machine.GetManufacturer()
    model = state_machine.GetModel()
    imei = state_machine.GetIMEI()
    firmware = state_machine.GetFirmware()
    print("Phone infomation:")
    print("{:<15}: {}".format("Manufacturer", manufacturer))
    print("{:<15}: {} ({})".format("Model", model[0], model[1]))
    print("{:<15}: {}".format("IMEI", imei))
    print("{:<15}: {}".format("Firmware", firmware[0]))


if __name__ == "__main__":
    main()
