#!/usr/bin/env python

import gammu
import time
import collections

# Whether be a bit more verbose
verbose = False


def ReplyTest(message):
    if message['Number'] == '999':
        # No reply to this number
        return None
    return 'Reply to %s' % message['Text']


# Reply function, first element is matching string, second can be:
#  - string = fixed string will be sent as reply
#  - function = function will be called with SMS data and it's result will be
#    sent
#  - None = no reply
replies = [
    ('1/1 www:', 'This is test'),
    ('1/2 www:', ReplyTest),
    ('2/2 www:', None),
]


def Callback(state_machine, type, data):
    if verbose:
        print('Received incoming event type %s, data:' % type)
    if type != 'SMS':
        print('Unsupported event!')
    if 'Number' not in data:
        data = state_machine.GetSMS(data['Folder'], data['Location'])[0]
    if verbose:
        print(data)

    for reply in replies:
        if data['Text'].startswith(reply[0]):
            if isinstance(reply[1], collections.Callable):
                response = reply[1](data)
            else:
                response = reply[1]

            if response is not None:
                message = {
                    'Text': response,
                    'SMSC': {'Location': 1},
                    'Number': data['Number']
                }
                if verbose:
                    print(message)
                state_machine.SendSMS(message)
            else:
                if verbose:
                    print('No reply!')
            break


state_machine = gammu.StateMachine()
state_machine.ReadConfig()
state_machine.Init()
state_machine.SetIncomingCallback(Callback)
try:
    state_machine.SetIncomingSMS()
except gammu.ERR_NOTSUPPORTED:
    print('Your phone does not support incoming SMS notifications!')

# We need to keep communication with phone to get notifications
print('Press Ctrl+C to interrupt')
while 1:
    time.sleep(1)
    status = state_machine.GetBatteryCharge()
    print('Battery is at %d%%' % status['BatteryPercent'])
