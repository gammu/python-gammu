#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
#
# Copyright © 2003 - 2017 Michal Čihař <michal@cihar.com>
#
# This file is part of python-gammu <https://wammu.eu/python-gammu/>
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

from __future__ import print_function
import gammu
import time
import collections

# Whether be a bit more verbose
VERBOSE = False


def verbose_print(text):
    if VERBOSE:
        print(text)


def reply_test(message):
    if message['Number'] == '999':
        # No reply to this number
        return None
    return 'Reply to {0}'.format(message['Text'])


# Reply function, first element is matching string, second can be:
#  - string = fixed string will be sent as reply
#  - function = function will be called with SMS data and it's result will be
#    sent
#  - None = no reply
REPLIES = [
    ('1/1 www:', 'This is test'),
    ('1/2 www:', reply_test),
    ('2/2 www:', None),
]


def Callback(state_machine, callback_type, data):
    verbose_print('Received incoming event type {0}, data:'.format(callback_type))
    if callback_type != 'SMS':
        print('Unsupported event!')
    if 'Number' not in data:
        data = state_machine.GetSMS(data['Folder'], data['Location'])[0]
    verbose_print(data)

    for reply in REPLIES:
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
                verbose_print(message)
                state_machine.SendSMS(message)
            else:
                verbose_print('No reply!')
            break


def main():
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
        print('Battery is at {0:d}%'.format(status['BatteryPercent']))


if __name__ == '__main__':
    main()
