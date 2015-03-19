#!/usr/bin/env python
# Example for reading calendar from phone

import gammu

# Create object for talking with phone
state_machine = gammu.StateMachine()

# Read the configuration (~/.gammurc)
state_machine.ReadConfig()

# Connect to the phone
state_machine.Init()

# Get number of calendar entries
status = state_machine.GetCalendarStatus()

remain = status['Used']

start = True

while remain > 0:
    # Read the entry
    if start:
        entry = state_machine.GetNextCalendar(Start=True)
        start = False
    else:
        entry = state_machine.GetNextCalendar(Location=entry['Location'])
    remain = remain - 1

    # Display it
    print()
    print('%-20s: %d' % ('Location', entry['Location']))
    print('%-20s: %s' % ('Type', entry['Type']))
    for v in entry['Entries']:
        print('%-20s: %s' % (v['Type'], str(v['Value'])))
