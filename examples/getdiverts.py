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

diverts = state_machine.GetCallDivert()

for x in diverts:
    print x
