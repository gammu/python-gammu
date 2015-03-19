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

status = state_machine.GetBatteryCharge()

for x in status:
    if status[x] != -1:
        print("%20s: %s" % (x, status[x]))
