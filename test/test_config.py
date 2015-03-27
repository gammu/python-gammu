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
import tempfile
import gammu
import sys

PDU_DATA = '079124602009999002AB098106845688F8907080517375809070805183018000'


class ConfigTest(unittest.TestCase):
    def test_config_bool(self):
        state_machine = gammu.StateMachine()
        state_machine.SetConfig(
            0,
            {
                'StartInfo': True,
                'UseGlobalDebugFile': True,
                'DebugFile': None,
                'SyncTime': True,
                'Connection': 'at',
                'LockDevice': True,
                'DebugLevel': 'textalldate',
                'Device': '',
                'Model': '',
            },
        )
        cfg = state_machine.GetConfig(0)
        self.assertEqual(cfg['StartInfo'], 1)

    def test_config_string(self):
        state_machine = gammu.StateMachine()
        state_machine.SetConfig(
            0,
            {
                'StartInfo': 'yes',
                'UseGlobalDebugFile': 'no',
                'DebugFile': 'dbg.log',
                'SyncTime': 'true',
                'Connection': 'fbus',
                'LockDevice': 'FALSE',
                'DebugLevel': 'textall',
                'Device': '',
                'Model': '',
            },
        )
        cfg = state_machine.GetConfig(0)
        self.assertEqual(cfg['StartInfo'], 1)

    def test_config_none(self):
        state_machine = gammu.StateMachine()
        state_machine.SetConfig(
            0,
            {
                'StartInfo': None,
                'UseGlobalDebugFile': None,
                'DebugFile': 'dbg.log',
                'SyncTime': 'true',
                'Connection': 'dlr3',
                'LockDevice': 'NO',
                'DebugLevel': 'binary',
                'Device': '',
                'Model': '',
            },
        )
        cfg = state_machine.GetConfig(0)
        self.assertEqual(cfg['StartInfo'], 0)


class DebugTest(unittest.TestCase):
    def setUp(self):
        gammu.SetDebugLevel('textall')

    def check_operation(self, filename):
        """
        Executes gammu operation which causes debug logs.
        """
        sms = gammu.DecodePDU(PDU_DATA.decode('hex'))
        if filename is not None:
            with open(filename, 'r') as handle:
                self.assertIn('SMS type: Status report', handle.read())

    def test_file(self):
        testfile = tempfile.NamedTemporaryFile(suffix='.debug')
        try:
            gammu.SetDebugFile(testfile.file)
            self.check_operation(testfile.name)
        finally:
            testfile.close()

    def test_filename(self):
        testfile = tempfile.NamedTemporaryFile(suffix='.debug')
        try:
            gammu.SetDebugFile(testfile.name)
            self.check_operation(testfile.name)
        finally:
            testfile.close()

    def test_none(self):
        gammu.SetDebugFile(None)
        self.check_operation(None)

    def test_nothing(self):
        gammu.SetDebugLevel('nothing')
        testfile = tempfile.NamedTemporaryFile(suffix='.debug')
        try:
            gammu.SetDebugFile(testfile.file)
            self.check_operation(None)
            with open(testfile.name, 'r') as handle:
                self.assertEqual('', handle.read())
        finally:
            testfile.close()
