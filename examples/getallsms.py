#!/usr/bin/env python

import gammu

state_machine = gammu.StateMachine()
state_machine.ReadConfig()
state_machine.Init()

status = state_machine.GetSMSStatus()

remain = status['SIMUsed'] + status['PhoneUsed'] + status['TemplatesUsed']

start = True

try:
    while remain > 0:
        if start:
            sms = state_machine.GetNextSMS(Start=True, Folder=0)
            start = False
        else:
            sms = state_machine.GetNextSMS(
                Location=sms[0]['Location'], Folder=0
            )
        remain = remain - len(sms)

        for m in sms:
            print()
            print('%-15s: %s' % ('Number', m['Number']))
            print('%-15s: %s' % ('Date', str(m['DateTime'])))
            print('%-15s: %s' % ('State', m['State']))
            print('\n%s' % m['Text'])
except gammu.ERR_EMPTY:
    # This error is raised when we've reached last entry
    # It can happen when reported status does not match real counts
    print('Failed to read all messages!')
