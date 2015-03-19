#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
#
# Copyright © 2003 - 2015 Michal Čihař <michal@cihar.com>
#
# This file is part of Gammu <http://wammu.eu/>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
'''
Service numbers dialogue example.
'''

import gammu
import sys


def callback(state_machine, type, data):
    '''
    Callback on USSD data.
    '''
    if type != 'USSD':
        print 'Unexpected event type: %s' % type
        sys.exit(1)

    print 'Network reply:'
    print 'Status: %s' % data['Status']
    print data['Text']

    if data['Status'] == 'ActionNeeded':
        do_service(state_machine)


def init():
    '''
    Intializes gammu and callbacks.
    '''
    global state_machine
    state_machine = gammu.StateMachine()
    if len(sys.argv) >= 2:
        state_machine.ReadConfig(Filename=sys.argv[1])
    else:
        state_machine.ReadConfig()
    state_machine.Init()
    state_machine.SetIncomingCallback(callback)
    try:
        state_machine.SetIncomingUSSD()
    except gammu.ERR_NOTSUPPORTED:
        print 'Incoming USSD notification is not supported.'
        sys.exit(1)
    return state_machine


def do_service(state_machine):
    '''
    Main code to talk with worker.
    '''
    if len(sys.argv) >= 3:
        code = sys.argv[2]
        del sys.argv[2]
    else:
        print 'Enter code (empty string to end):',
        code = raw_input()
    if code != '':
        print 'Talking to network...'
        state_machine.DialService(code)


if __name__ == '__main__':
    state_machine = init()
    print('This example shows interaction with network using service codes')
    do_service(state_machine)
