#!/usr/bin/env python

from __future__ import print_function
import gammu
import sys

state_machine = gammu.StateMachine()
state_machine.ReadConfig()
state_machine.Init()

if len(sys.argv) != 2:
    print('This requires one parameter with memory type!')
    sys.exit(1)

memory_type = sys.argv[1]

status = state_machine.GetMemoryStatus(Type=memory_type)

remain = status['Used']

location = 1

while remain > 0:
    try:
        entry = state_machine.GetMemory(Type=memory_type, Location=location)
        print()
        print('%-15s: %d' % ('Location', entry['Location']))
        for v in entry['Entries']:
            print('%-15s: %s' % (v['Type'], str(v['Value'])))
        remain = remain - 1
    except gammu.ERR_EMPTY:
        pass
    location = location + 1
