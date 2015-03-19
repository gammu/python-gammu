#!/usr/bin/env python

import gammu
import sys

if len(sys.argv) != 3:
    print(
        'This requires two parameters: '
        'memory_type and backup file (eg. vcard)!'
    )
    sys.exit(1)

state_machine = gammu.StateMachine()
state_machine.ReadConfig()
state_machine.Init()

memory = sys.argv[1]
filename = sys.argv[2]

backup = gammu.ReadBackup(filename)

for item in backup['PhonePhonebook']:
    item['MemoryType'] = memory
    loc = state_machine.AddMemory(item)
    print('Added item to location %d' % loc)
