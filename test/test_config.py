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


class ConfigTest(unittest.TestCase):
    def test_config_bool(self):
        sm = gammu.StateMachine()
        sm.SetConfig(
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
        cfg = sm.GetConfig(0)
        self.assertEqual(cfg['StartInfo'], 1)

    def test_config_string(self):
        sm = gammu.StateMachine()
        sm.SetConfig(
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
        cfg = sm.GetConfig(0)
        self.assertEqual(cfg['StartInfo'], 1)

    def test_config_none(self):
        sm = gammu.StateMachine()
        sm.SetConfig(
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
        cfg = sm.GetConfig(0)
        self.assertEqual(cfg['StartInfo'], 0)
