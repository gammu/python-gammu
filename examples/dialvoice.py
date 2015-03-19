#!/usr/bin/env python

import gammu
import sys

# Create object for talking with phone
state_machine = gammu.StateMachine()

# Read the configuration (~/.gammurc or from command line)
if len(sys.argv) >= 2:
    state_machine.ReadConfig(Filename=sys.argv[1])
    del sys.argv[1]
else:
    state_machine.ReadConfig()

# Connect to the phone
state_machine.Init()

# Check whether we have a number to dial
if len(sys.argv) != 2:
    print('Usage: dialvoice.py NUMBER')
    sys.exit(1)

# Dial a number
state_machine.DialVoice(sys.argv[1])
