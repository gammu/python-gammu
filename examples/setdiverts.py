#!/usr/bin/env python

import gammu
import sys

state_machine = gammu.StateMachine()

if len(sys.argv) >= 2:
    state_machine.ReadConfig(Filename=sys.argv[1])
    del sys.argv[1]
else:
    state_machine.ReadConfig()
state_machine.Init()

if len(sys.argv) != 2:
    print('Usage: setdiverts.py NUMBER')
    sys.exit(1)

state_machine.SetCallDivert('AllTypes', 'All', sys.argv[1])
diverts = state_machine.GetCallDivert()

for x in diverts:
    print(x)
