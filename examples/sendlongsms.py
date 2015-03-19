#!/usr/bin/env python
# Sample script to show how to send long (multipart) SMS

import gammu
import sys

# Create object for talking with phone
state_machine = gammu.StateMachine()

# Optionally load config file as defined by first parameter
if len(sys.argv) >= 2:
    # Read the configuration from given file
    state_machine.ReadConfig(Filename=sys.argv[1])
    # Remove file name from args list
    del sys.argv[1]
else:
    # Read the configuration (~/.gammurc)
    state_machine.ReadConfig()

# Check parameters
if len(sys.argv) != 2:
    print 'Usage: sendlongsms.py [configfile] RECIPIENT_NUMBER'
    sys.exit(1)

# Connect to the phone
state_machine.Init()


# Create SMS info structure
smsinfo = {
    'Class': 1,
    'Unicode': False,
    'Entries':  [
        {
            'ID': 'ConcatenatedTextLong',
            'Buffer':
                'Very long python-gammu testing message '
                'sent from example python script. '
                'Very long python-gammu testing message '
                'sent from example python script. '
                'Very long python-gammu testing message '
                'sent from example python script. '
        }
    ]}

# Encode messages
encoded = gammu.EncodeSMS(smsinfo)

# Send messages
for message in encoded:
    # Fill in numbers
    message['SMSC'] = {'Location': 1}
    message['Number'] = sys.argv[1]

    # Actually send the message
    state_machine.SendSMS(message)
