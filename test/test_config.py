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
import unittest
import tempfile
import gammu
from .test_sms import PDU_DATA


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

    def test_init_error(self):
        self.assertRaises(TypeError, gammu.StateMachine, Bar=1)


class DebugTest(unittest.TestCase):
    def setUp(self):
        gammu.SetDebugLevel('textall')

    def check_operation(self, filename):
        """
        Executes gammu operation which causes debug logs.
        """
        gammu.DecodePDU(PDU_DATA)
        if filename is not None:
            with open(filename, 'r') as handle:
                self.assertTrue('SMS type: Status report' in handle.read())

    def test_file(self):
        testfile = tempfile.NamedTemporaryFile(suffix='.debug')
        try:
            gammu.SetDebugFile(testfile.file)
            self.check_operation(testfile.name)
        finally:
            gammu.SetDebugFile(None)
            testfile.close()

    def test_filename(self):
        testfile = tempfile.NamedTemporaryFile(suffix='.debug')
        try:
            gammu.SetDebugFile(testfile.name)
            self.check_operation(testfile.name)
        finally:
            gammu.SetDebugFile(None)
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
            gammu.SetDebugFile(None)
            testfile.close()
