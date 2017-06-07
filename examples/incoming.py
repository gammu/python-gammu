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


def callback(state_machine, callback_type, data):
    '''
    This callback receives notification about incoming event.

    @param state_machine: state machine which invoked action
    @type state_machine: gammu.StateMachine
    @param callback_type: type of action, one of Call, SMS, CB, USSD
    @type callback_type: string
    @param data: event data
    @type data: hash
    '''
    print('Received incoming event type {0}, data:'.format(callback_type))
    print(data)


def try_enable(call, name):
    try:
        call()
    except gammu.ERR_NOTSUPPORTED:
        print('{0} notification is not supported.'.format(name))
    except gammu.ERR_SOURCENOTAVAILABLE:
        print('{0} notification is not enabled in Gammu.'.format(name))


def main():
    # Create state machine
    state_machine = gammu.StateMachine()
    # Read gammurc
    state_machine.ReadConfig()
    # Initialize state machine and connect to phone
    state_machine.Init()
    # Set callback handler for incoming notifications
    state_machine.SetIncomingCallback(callback)

    # Enable notifications from calls
    try_enable(state_machine.SetIncomingCall, 'Incoming calls')

    # Enable notifications from cell broadcast
    try_enable(state_machine.SetIncomingCB, 'Incoming cell broadcasts')

    # Enable notifications from incoming SMS
    try_enable(state_machine.SetIncomingSMS, 'Incoming SMS')

    # Enable notifications for incoming USSD
    try_enable(state_machine.SetIncomingUSSD, 'Incoming USSD')

    # Just a busy waiting for event
    # We need to keep communication with phone to get notifications
    print('Press Ctrl+C to interrupt')
    while 1:
        signal = state_machine.GetSignalQuality()
        print('Signal is at {0:d}%'.format(signal['SignalPercent']))
        time.sleep(1)

if __name__ == '__main__':
    main()
