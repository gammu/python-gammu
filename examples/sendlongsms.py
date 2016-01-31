#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
#
# Copyright © 2003 - 2016 Michal Čihař <michal@cihar.com>
#
# This file is part of python-gammu <http://wammu.eu/python-gammu/>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
"""Sample script to show how to send long (multipart) SMS"""

from __future__ import print_function
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
    print('Usage: sendlongsms.py [configfile] RECIPIENT_NUMBER')
    sys.exit(1)

# Connect to the phone
state_machine.Init()


# Create SMS info structure
smsinfo = {
    'Class': -1,
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
