#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
#
# Copyright © 2003 - 2018 Michal Čihař <michal@cihar.com>
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
'''
python-gammu - Phone communication libary
Gammu asynchronous wrapper example with asyncio. This allows your application to care
only about handling received data and not about phone communication
details.
'''

import sys
import pprint
pp = pprint.PrettyPrinter(indent=4)

import gammu
import gammu.asyncworker
import asyncio


def sms_callback(messages):
    pp.pprint(messages)

async def send_message_async(state_machine, number, message):
    smsinfo = {
        'Class': -1,
        'Unicode': False,
        'Entries':  [
            {
                'ID': 'ConcatenatedTextLong',
                'Buffer': message
            }
        ]}
    # Encode messages
    encoded = gammu.EncodeSMS(smsinfo)
    # Send messages
    for message in encoded:
        # Fill in numbers
        message['SMSC'] = {'Location': 1}
        message['Number'] = number
        # Actually send the message
        await state_machine.send_sms_async(message)

async def get_network_info(worker):
    info = await worker.GetNetworkInfoAsync()
    print('NetworkName:',info['NetworkName'])
    print('  State:',info['State'])
    print('  NetworkCode:',info['NetworkCode'])
    print('  CID:',info['CID'])
    print('  LAC:',info['LAC'])

async def get_info(state_machine):
    print('Phone infomation:')
    manufacturer = await state_machine.GetManufacturer()
    print(('{0:<15}: {1}'.format('Manufacturer', manufacturer)))
    model = await state_machine.GetModel()
    print(('{0:<15}: {1} ({2})'.format('Model', model[0], model[1])))
    imei = await state_machine.GetIMEI()
    print(('{0:<15}: {1}'.format('IMEI', imei)))
    firmware = await state_machine.GetFirmware()
    print(('{0:<15}: {1}'.format('Firmware', firmware[0])))

async def main():

    # Get the current event loop.
    loop = asyncio.get_running_loop()

    gammu.SetDebugFile(sys.stderr)
    gammu.SetDebugLevel('textall')

    config = dict(Device="/dev/ttyS6", Connection="at")
    worker = gammu.asyncworker.GammuAsyncWorker(loop)
    worker.configure(config)

    try:
        await worker.init_async()

        print(await worker.get_signal_quality_async())

        await send_message_async(worker, '6700', 'BAL')

        # Just a busy waiting for event
        # We need to keep communication with phone to get notifications
        print('Press Ctrl+C to interrupt')
        while 1:
            try:
                signal = await worker.get_signal_quality_async()
                print('Signal is at {0:d}%'.format(signal['SignalPercent']))
            except Exception as e:
                print('Exception reading signal: {0}'.format(e))

            await asyncio.sleep(30)

    except Exception as e:
        print('Exception:')
        print(e)

    print("Terminate Start")
    await worker.terminate_async()
    print("Terminate Done")

if __name__ == '__main__':
    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(main())
    finally:
        event_loop.close()

