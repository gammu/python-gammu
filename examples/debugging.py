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

    Manufacturer = state_machine.GetManufacturer()
    Model = state_machine.GetModel()
    IMEI = state_machine.GetIMEI()
    Firmware = state_machine.GetFirmware()
    print('Phone infomation:')
    print(('%-15s: %s' % ('Manufacturer', Manufacturer)))
    print(('%-15s: %s (%s)' % ('Model', Model[0], Model[1])))
    print(('%-15s: %s' % ('IMEI', IMEI)))
    print(('%-15s: %s' % ('Firmware', Firmware[0])))


if __name__ == '__main__':
    main()
