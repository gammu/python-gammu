#!/usr/bin/env python

from __future__ import print_function
import gammu
import sys


def main():
    # Global debug level
    gammu.SetDebugFile(sys.stderr)
    gammu.SetDebugLevel('textall')

    state_machine = gammu.StateMachine()
    state_machine.ReadConfig()

    # Use global debug stub regardless configuration
    c = state_machine.GetConfig(0)
    c['UseGlobalDebugFile'] = True
    state_machine.SetConfig(0, c)

    state_machine.Init()

    manufacturer = state_machine.GetManufacturer()
    model = state_machine.GetModel()
    imei = state_machine.GetIMEI()
    firmware = state_machine.GetFirmware()
    print('Phone infomation:')
    print(('%-15s: %s' % ('Manufacturer', manufacturer)))
    print(('%-15s: %s (%s)' % ('Model', model[0], model[1])))
    print(('%-15s: %s' % ('IMEI', imei)))
    print(('%-15s: %s' % ('Firmware', firmware[0])))


if __name__ == '__main__':
    main()
