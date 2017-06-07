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
import gammu.worker
from .test_dummy import DummyTest


WORKER_EXPECT = [
    ('Init', None, 'ERR_NONE', 100),
    ('GetManufacturer', 'Gammu', 'ERR_NONE', 100),
    ('GetSIMIMSI', '994299429942994', 'ERR_NONE', 100),
    ('GetIMEI', '999999999999999', 'ERR_NONE', 100),
    ('GetOriginalIMEI', '666666666666666', 'ERR_NONE', 100),
    ('GetManufactureMonth', 'April', 'ERR_NONE', 100),
    ('GetProductCode', 'DUMMY-001', 'ERR_NONE', 100),
    ('GetHardware', 'FOO DUMMY BAR', 'ERR_NONE', 100),
    ('CustomGetInfo', ('unknown', 'Dummy'), 'ERR_NONE', 50),
    (
        'CustomGetInfo',
        {
            'BatteryVoltage': 4200,
            'PhoneTemperature': 22,
            'BatteryTemperature': 22,
            'ChargeState': 'BatteryConnected',
            'ChargeVoltage': 4200,
            'BatteryCapacity': 2000,
            'BatteryPercent': 100,
            'ChargeCurrent': 0,
            'PhoneCurrent': 500
        },
        'ERR_NONE',
        100
    ),
    (
        'GetMemory',
        {
            'MemoryType': 'SM',
            'Location': 1,
            'Entries': [
                {
                    'AddError': 1,
                    'Type': 'Text_Name',
                    'Location': 'Unknown',
                    'Value': 'firstname lastname'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test1'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test2'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test3'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test4'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test5'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test6'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test7'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test8'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test9'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test10'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test11'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test12'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test13'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test14'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test15'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test16'
                }
            ]
        },
        'ERR_NONE',
        100
    ),
    (
        'CustomGetAllMemory',
        {
            'MemoryType': 'SM',
            'Location': 1,
            'Entries': [
                {
                    'AddError': 1,
                    'Type': 'Text_Name',
                    'Location': 'Unknown',
                    'Value': 'firstname lastname'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test1'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test2'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test3'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test4'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test5'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test6'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test7'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test8'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test9'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test10'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test11'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test12'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test13'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test14'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test15'
                },
                {
                    'AddError': 1,
                    'Type': 'Text_Note',
                    'Location': 'Unknown',
                    'Value': 'Test16'
                }
            ]
        },
        'ERR_NONE',
        20
    ),
    ('CustomGetAllMemory', None, 'ERR_EMPTY', 40),
    ('CustomGetAllMemory', None, 'ERR_EMPTY', 60),
    ('CustomGetAllMemory', None, 'ERR_EMPTY', 80),
    ('CustomGetAllMemory', None, 'ERR_EMPTY', 100),
    (
        'GetSMSC',
        {
            'DefaultNumber': '',
            'Format': 'Text',
            'Number': '123456',
            'Validity': 'NA',
            'Location': 1,
            'Name': 'Default'
        },
        'ERR_NONE',
        100
    ),
    ('Terminate', None, 'ERR_NONE', 100)
]


class WorkerDummyTest(DummyTest):
    results = []

    def callback(self, name, result, error, percents):
        self.results.append((name, result, error, percents))

    def test_worker(self):
        self.results = []
        worker = gammu.worker.GammuWorker(self.callback)
        worker.configure(self.get_statemachine().GetConfig())
        # We can directly invoke commands
        worker.enqueue('GetManufacturer')
        worker.enqueue('GetSIMIMSI')
        worker.enqueue('GetIMEI')
        worker.enqueue('GetOriginalIMEI')
        worker.enqueue('GetManufactureMonth')
        worker.enqueue('GetProductCode')
        worker.enqueue('GetHardware')
        worker.enqueue('GetDateTime')
        # We can create compound tasks
        worker.enqueue('CustomGetInfo', commands=[
            'GetModel',
            'GetBatteryCharge'
        ])
        # We can pass parameters
        worker.enqueue('GetMemory', ('SM', 1))
        # We can create compound tasks with parameters:
        worker.enqueue('CustomGetAllMemory', commands=[
            ('GetMemory', ('SM', 1)),
            ('GetMemory', ('SM', 2)),
            ('GetMemory', ('SM', 3)),
            ('GetMemory', ('SM', 4)),
            ('GetMemory', ('SM', 5))
        ])
        worker.initiate()
        # We can also pass commands with named parameters
        worker.enqueue('GetSMSC', {'Location': 1})
        worker.terminate()

        # Remove GetDateTime from comparing as the value changes
        for i in range(len(self.results)):
            if self.results[i][0] == 'GetDateTime':
                self.assertEqual(self.results[i][2], 'ERR_NONE')
                self.assertEqual(self.results[i][3], 100)
                del self.results[i]
                break

        self.maxDiff = None
        self.assertEqual(WORKER_EXPECT, self.results)

    def test_incoming(self):
        self.check_incoming_call()
        self.results = []
        self._called = False
        worker = gammu.worker.GammuWorker(self.callback)
        worker.configure(self.get_statemachine().GetConfig())
        worker.initiate()
        worker.enqueue('SetIncomingCallback', (self.call_callback, ))
        worker.enqueue('SetIncomingCall')
        self.fake_incoming_call()
        worker.terminate()
        self.assertTrue(self._called)
