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
import unittest
import gammu
import tempfile
import shutil
import os.path

DUMMY_DIR = os.path.join(os.path.dirname(__file__), 'data', 'gammu-dummy')
CONFIGURATION = '''
# Configuration for Gammu testsuite

[gammu]
model = dummy
connection = none
port = {path}/gammu-dummy
gammuloc = /dev/null
logformat = none

[smsd]
commtimeout = 1
debuglevel = 255
logfile = stderr
service = sql
driver = sqlite3
sql = sqlite
database = smsd.db
dbdir = {path}
'''


class DummyTest(unittest.TestCase):
    test_dir = None
    config_name = None

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        dummy_dir = os.path.join(self.test_dir, 'gammu-dummy')
        self.config_name = os.path.join(self.test_dir, '.gammurc')
        shutil.copytree(DUMMY_DIR, dummy_dir)
        with open(self.config_name, 'w') as handle:
            handle.write(CONFIGURATION.format(path=self.test_dir))

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def get_statemachine(self):
        state_machine = gammu.StateMachine()
        state_machine.ReadConfig(Filename=self.config_name)
        state_machine.Init()
        return state_machine


class BasicDummyTest(DummyTest):
    def test_model(self):
        state_machine = self.get_statemachine()
        self.assertEqual(state_machine.GetModel()[1], 'Dummy')

    def test_diverts(self):
        state_machine = self.get_statemachine()
        diverts = state_machine.GetCallDivert()
        self.assertEqual(
            diverts,
            [{
                'CallType': 'All',
                'Timeout': 0,
                'Number': '',
                'DivertType': 'AllTypes'
            }]
        )

        state_machine.SetCallDivert('AllTypes', 'All', '123456789')
        diverts = state_machine.GetCallDivert()
        self.assertEqual(
            diverts,
            [{
                'CallType': 'All',
                'Timeout': 0,
                'Number': '123456789',
                'DivertType': 'AllTypes'
            }]
        )

    def test_dial(self):
        state_machine = self.get_statemachine()
        state_machine.DialVoice('123456')

    def test_battery(self):
        state_machine = self.get_statemachine()
        status = state_machine.GetBatteryCharge()
        self.assertEqual(
            status,
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
            }
        )

    def test_memory(self):
        state_machine = self.get_statemachine()
        status = state_machine.GetMemoryStatus(Type='ME')

        remain = status['Used']

        self.assertEquals(status['Used'], 3)

        start = True

        while remain > 0:
            if start:
                entry = state_machine.GetNextMemory(Start=True, Type='ME')
                start = False
            else:
                entry = state_machine.GetNextMemory(Location=entry['Location'], Type='ME')
            remain = remain - 1


    def test_calendar(self):
        state_machine = self.get_statemachine()
        status = state_machine.GetCalendarStatus()

        remain = status['Used']

        self.assertEquals(status['Used'], 2)

        start = True

        while remain > 0:
            if start:
                entry = state_machine.GetNextCalendar(Start=True)
                start = False
            else:
                entry = state_machine.GetNextCalendar(Location=entry['Location'])
            remain = remain - 1

    def test_sms(self):
        state_machine = self.get_statemachine()
        status = state_machine.GetSMSStatus()

        remain = status['SIMUsed'] + status['PhoneUsed'] + status['TemplatesUsed']

        self.assertEquals(remain, 6)

        start = True

        sms = []

        while remain > 0:
            if start:
                sms.append(state_machine.GetNextSMS(Start=True, Folder=0))
                start = False
            else:
                sms.append(state_machine.GetNextSMS(Location=sms[-1][0]['Location'], Folder=0))
            remain = remain - len(sms)

        data = gammu.LinkSMS(sms)

        for item in data:
            message = gammu.DecodeSMS(item)
            if message is None:
                self.assertEquals(item[0]['UDH']['Type'], 'NoUDH')

    def test_todo(self):
        state_machine = self.get_statemachine()
        status = state_machine.GetToDoStatus()

        remain = status['Used']

        self.assertEquals(status['Used'], 2)

        start = True

        while remain > 0:
            if start:
                entry = state_machine.GetNextToDo(Start = True)
                start = False
            else:
                entry = state_machine.GetNextToDo(Location = entry['Location'])
            remain = remain - 1

    def test_sms_folders(self):
        state_machine = self.get_statemachine()
        folders = state_machine.GetSMSFolders()
        self.assertEquals(len(folders), 5)

    def ussd_callback(self, state_machine, response, data):
        '''
        Callback on USSD data.
        '''
        self.assertEquals(response, 'USSD')
        self.assertEquals(data['Text'], 'Reply for 1234')
        self.assertEquals(data['Status'], 'NoActionNeeded')

    def test_ussd(self):
        state_machine = self.get_statemachine()
        state_machine.SetIncomingCallback(self.ussd_callback)
        state_machine.SetIncomingUSSD()
        state_machine.DialService('1234')
