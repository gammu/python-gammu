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
'''
Service numbers dialogue example.
'''

from __future__ import print_function
import gammu
import sys

REPLY = False


def callback(state_machine, callback_type, data):
    '''
    Callback on USSD data.
    '''
    global REPLY
    if callback_type != 'USSD':
        print('Unexpected event type: %s' % callback_type)
        sys.exit(1)

    REPLY = True

    print('Network reply:')
    print('Status: %s' % data['Status'])
    print(data['Text'])

    if data['Status'] == 'ActionNeeded':
        do_service(state_machine)


def init():
    '''
    Intializes gammu and callbacks.
    '''
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
        print('Incoming USSD notification is not supported.')
        sys.exit(1)
    return state_machine


def do_service(state_machine):
    '''
    Main code to talk with worker.
    '''
    global REPLY

    if len(sys.argv) >= 3:
        code = sys.argv[2]
        del sys.argv[2]
    else:
        prompt = 'Enter code (empty string to end): '
        try:
            code = raw_input(prompt)
        except NameError:
            code = input(prompt)
    if code != '':
        print('Talking to network...')
        REPLY = False
        state_machine.DialService(code)
        loops = 0
        while not REPLY and loops < 10:
            state_machine.ReadDevice()
            loops += 1


def main():
    state_machine = init()
    print('This example shows interaction with network using service codes')
    do_service(state_machine)


if __name__ == '__main__':
    main()
