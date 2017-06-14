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
from __future__ import unicode_literals
import unittest
import gammu
import tempfile
import shutil
import datetime
import platform
import os.path

DUMMY_DIR = os.path.join(os.path.dirname(__file__), 'data', 'gammu-dummy')
TEST_FILE = os.path.join(os.path.dirname(__file__), 'data', 'sqlite-14.sql')
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
    dummy_dir = None
    _called = False
    _state_machine = None

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.dummy_dir = os.path.join(self.test_dir, 'gammu-dummy')
        self.config_name = os.path.join(self.test_dir, '.gammurc')
        shutil.copytree(DUMMY_DIR, self.dummy_dir)
        with open(self.config_name, 'w') as handle:
            handle.write(CONFIGURATION.format(path=self.test_dir))

    def tearDown(self):
        if self._state_machine:
            self._state_machine.Terminate()
        shutil.rmtree(self.test_dir)

    def get_statemachine(self):
        state_machine = gammu.StateMachine()
        state_machine.ReadConfig(Filename=self.config_name)
        state_machine.Init()
        self._state_machine = state_machine
        return state_machine

    def fake_incoming_call(self):
        """Fake incoming call"""
        filename = os.path.join(self.dummy_dir, 'incoming-call')
        with open(filename, 'w') as handle:
            handle.write('\n')

    def check_incoming_call(self):
        """Checks whether incoming call faking is supported"""
        current = tuple([int(x) for x in gammu.Version()[2].split('.')])
        if current < (1, 37, 91):
            raise unittest.SkipTest(
                'Not supported in version {0}'.format(gammu.Version()[2])
            )

    def call_callback(self, state_machine, response, data):
        '''
        Callback on USSD data.
        '''
        self._called = True
        self.assertEqual(response, 'Call')
        self.assertEqual(data['Number'], '+800123456')


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

        self.assertEqual(status['Used'], 3)

        start = True

        while remain > 0:
            if start:
                entry = state_machine.GetNextMemory(Start=True, Type='ME')
                start = False
            else:
                entry = state_machine.GetNextMemory(
                    Location=entry['Location'], Type='ME'
                )
            remain = remain - 1

    def test_getmemory(self):
        state_machine = self.get_statemachine()

        location = state_machine.AddMemory(
            {
                'MemoryType': 'SM',
                'Entries': [
                    {'Type': 'Number_Mobile', 'Value': '123456'},
                    {'Type': 'Text_Name', 'Value': 'Jmeno'},
                ]
            }
        )

        read = state_machine.GetMemory('SM', location)
        self.assertEqual(len(read['Entries']), 2)

    def test_calendar(self):
        state_machine = self.get_statemachine()
        status = state_machine.GetCalendarStatus()

        remain = status['Used']

        self.assertEqual(status['Used'], 2)

        start = True

        while remain > 0:
            if start:
                entry = state_machine.GetNextCalendar(Start=True)
                start = False
            else:
                entry = state_machine.GetNextCalendar(
                    Location=entry['Location']
                )
            remain = remain - 1

    def test_sms(self):
        state_machine = self.get_statemachine()
        status = state_machine.GetSMSStatus()

        remain = (
            status['SIMUsed'] +
            status['PhoneUsed'] +
            status['TemplatesUsed']
        )

        self.assertEqual(remain, 6)

        start = True

        sms = []

        while remain > 0:
            if start:
                sms.append(state_machine.GetNextSMS(Start=True, Folder=0))
                start = False
            else:
                sms.append(
                    state_machine.GetNextSMS(
                        Location=sms[-1][0]['Location'], Folder=0
                    )
                )
            remain = remain - len(sms)

        data = gammu.LinkSMS(sms)

        for item in data:
            message = gammu.DecodeSMS(item)
            if message is None:
                self.assertEqual(item[0]['UDH']['Type'], 'NoUDH')

    def test_todo(self):
        state_machine = self.get_statemachine()
        status = state_machine.GetToDoStatus()

        remain = status['Used']

        self.assertEqual(status['Used'], 2)

        start = True

        while remain > 0:
            if start:
                entry = state_machine.GetNextToDo(Start=True)
                start = False
            else:
                entry = state_machine.GetNextToDo(Location=entry['Location'])
            remain = remain - 1

    def test_sms_folders(self):
        state_machine = self.get_statemachine()
        folders = state_machine.GetSMSFolders()
        self.assertEqual(len(folders), 5)

    def ussd_callback(self, state_machine, response, data):
        '''
        Callback on USSD data.
        '''
        self._called = True
        self.assertEqual(response, 'USSD')
        self.assertEqual(data['Text'], 'Reply for 1234')
        self.assertEqual(data['Status'], 'NoActionNeeded')

    def test_ussd(self):
        self._called = False
        state_machine = self.get_statemachine()
        state_machine.SetIncomingCallback(self.ussd_callback)
        state_machine.SetIncomingUSSD()
        state_machine.DialService('1234')
        self.assertTrue(self._called)

    def test_sendsms(self):
        state_machine = self.get_statemachine()
        message = {
            'Text': 'python-gammu testing message',
            'SMSC': {'Location': 1},
            'Number': '123456',
        }

        state_machine.SendSMS(message)

    def test_sendsms_long(self):
        state_machine = self.get_statemachine()
        text = (
            'Very long python-gammu testing message sent '
            'from example python script. '
        ) * 10
        smsinfo = {
            'Class': -1,
            'Unicode': False,
            'Entries':  [
                {
                    'ID': 'ConcatenatedTextLong',
                    'Buffer': text
                }
            ]}

        # Encode messages
        encoded = gammu.EncodeSMS(smsinfo)

        self.assertEqual(len(encoded), 5)

        # Send messages
        for message in encoded:
            # Fill in numbers
            message['SMSC'] = {'Location': 1}
            message['Number'] = '123456'

            # Actually send the message
            state_machine.SendSMS(message)

    def test_filesystem(self):
        state_machine = self.get_statemachine()
        fs_info = state_machine.GetFileSystemStatus()
        self.assertEqual(
            fs_info,
            {
                'UsedImages': 0,
                'Used': 1000000,
                'UsedThemes': 0,
                'Free': 10101,
                'UsedSounds': 0
            }
        )

    def test_deletefile(self):
        state_machine = self.get_statemachine()
        self.assertRaises(
            gammu.ERR_FILENOTEXIST,
            state_machine.DeleteFile,
            'testfolder/nonexisting.png'
        )
        state_machine.DeleteFile('file5')

    def test_deletefolder(self):
        state_machine = self.get_statemachine()
        self.assertRaises(
            gammu.ERR_FILENOTEXIST,
            state_machine.DeleteFolder,
            'testfolder'
        )
        state_machine.AddFolder('', 'testfolder')
        state_machine.DeleteFolder('testfolder')

    @unittest.skipIf(platform.system() == 'Windows',
        'Not supported on Windows')
    def test_emoji_folder(self):
        state_machine = self.get_statemachine()
        name = 'test-😘'
        self.assertRaises(
            gammu.ERR_FILENOTEXIST,
            state_machine.DeleteFolder,
            name
        )
        self.assertEqual(
            name,
            state_machine.AddFolder('', name)
        )
        # Check the folder exists as expected on filesystem
        self.assertTrue(
            os.path.exists(os.path.join(self.dummy_dir, 'fs', name))
        )
        state_machine.DeleteFolder(name)

    def test_addfile(self):
        state_machine = self.get_statemachine()
        file_stat = os.stat(TEST_FILE)
        ttime = datetime.datetime.fromtimestamp(file_stat[8])
        with open(TEST_FILE, 'rb') as handle:
            content = handle.read()
        file_f = {
            "ID_FullName": 'testfolder',
            "Name": 'sqlite.sql',
            "Modified": ttime,
            "Folder": 0,
            "Level": 1,
            "Used": file_stat[6],
            "Buffer": content,
            "Type": "Other",
            "Protected": 0,
            "ReadOnly": 0,
            "Hidden": 0,
            "System": 0,
            "Handle": 0,
            "Pos": 0,
            "Finished": 0
        }
        state_machine.AddFolder('', 'testfolder')
        while not file_f["Finished"]:
            file_f = state_machine.AddFilePart(file_f)

    def test_fileattributes(self):
        state_machine = self.get_statemachine()
        state_machine.SetFileAttributes(
            'file5', ReadOnly=1, Protected=0, System=1, Hidden=1
        )

    def test_getnextfile(self):
        state_machine = self.get_statemachine()
        file_f = state_machine.GetNextFileFolder(1)
        folders = 0
        files = 0
        while 1:
            if file_f['Folder']:
                folders += 1
            else:
                files += 1
            try:
                file_f = state_machine.GetNextFileFolder(0)
            except gammu.ERR_EMPTY:
                break
        self.assertEqual(folders, 3)
        self.assertEqual(files, 6)

    def test_incoming_call(self):
        self.check_incoming_call()
        self._called = False
        state_machine = self.get_statemachine()
        state_machine.SetIncomingCallback(self.call_callback)
        state_machine.SetIncomingCall()
        state_machine.GetSignalQuality()
        self.fake_incoming_call()
        state_machine.GetSignalQuality()
        self.assertTrue(self._called)
