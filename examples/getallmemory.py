#!/usr/bin/env python

import gammu
import sys

state_machine = gammu.StateMachine()
state_machine.ReadConfig()
state_machine.Init()

if len(sys.argv) != 2:
    print 'This requires one parameter with memory type!'
    sys.exit(1)

type = sys.argv[1]

status = state_machine.GetMemoryStatus(Type=type)

remain = status['Used']

start = True

while remain > 0:
    if start:
        entry = state_machine.GetNextMemory(Start=True, Type=type)
        start = False
    else:
        entry = state_machine.GetNextMemory(
            Location=entry['Location'], Type=type
        )
    remain = remain - 1

    print
    print '%-15s: %d' % ('Location', entry['Location'])
    for v in entry['Entries']:
        print '%-15s: %s' % (v['Type'], str(v['Value']))
