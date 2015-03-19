#!/usr/bin/env python

import gammu
import time


def Callback(state_machine, type, data):
    '''
    This callback receives notification about incoming event.

    @param state_machine: state machine which invoked action
    @type state_machine: gammu.StateMachine
    @param type: type of action, one of Call, SMS, CB, USSD
    @type type: string
    @param data: event data
    @type data: hash
    '''
    print 'Received incoming event type %s, data:' % type
    print data


# Create state machine
state_machine = gammu.StateMachine()
# Read gammurc
state_machine.ReadConfig()
# Initialize state machine and connect to phone
state_machine.Init()
# Set callback handler for incoming notifications
state_machine.SetIncomingCallback(Callback)

# Enable notifications from calls
try:
    state_machine.SetIncomingCall()
except gammu.ERR_NOTSUPPORTED:
    print 'Incoming calls notification is not supported.'

# Enable notifications from cell broadcast
try:
    state_machine.SetIncomingCB()
except gammu.ERR_NOTSUPPORTED:
    print 'Incoming CB notification is not supported.'
except gammu.ERR_SOURCENOTAVAILABLE:
    print 'Cell broadcasts support not enabled in Gammu.'

# Enable notifications from incoming SMS
try:
    state_machine.SetIncomingSMS()
except gammu.ERR_NOTSUPPORTED:
    print 'Incoming SMS notification is not supported.'

# Enable notifications for incoming USSD
try:
    state_machine.SetIncomingUSSD()
except gammu.ERR_NOTSUPPORTED:
    print 'Incoming USSD notification is not supported.'

# Just a busy waiting for event
# We need to keep communication with phone to get notifications
print 'Press Ctrl+C to interrupt'
while 1:
    q = state_machine.GetSignalQuality()
    print 'Signal is at %d%%' % q['SignalPercent']
    time.sleep(1)
