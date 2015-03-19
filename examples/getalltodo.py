#!/usr/bin/env python

import gammu

state_machine = gammu.StateMachine()
state_machine.ReadConfig()
state_machine.Init()

status = state_machine.GetToDoStatus()

remain = status['Used']

start = True

while remain > 0:
    if start:
        entry = state_machine.GetNextToDo(Start=True)
        start = False
    else:
        entry = state_machine.GetNextToDo(Location=entry['Location'])
    remain = remain - 1

    print()
    print('%-15s: %d' % ('Location', entry['Location']))
    print('%-15s: %s' % ('Priority', entry['Priority']))
    for v in entry['Entries']:
        print('%-15s: %s' % (v['Type'], str(v['Value'])))
