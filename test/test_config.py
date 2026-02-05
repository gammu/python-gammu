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
#
import tempfile
import unittest
from pathlib import Path

import pytest

import gammu

from .test_sms import PDU_DATA


class ConfigTest(unittest.TestCase):
    def test_config_bool(self) -> None:
        state_machine = gammu.StateMachine()
        state_machine.SetConfig(
            0,
            {
                "StartInfo": True,
                "UseGlobalDebugFile": True,
                "DebugFile": None,
                "SyncTime": True,
                "Connection": "at",
                "LockDevice": True,
                "DebugLevel": "textalldate",
                "Device": "",
                "Model": "",
            },
        )
        cfg = state_machine.GetConfig(0)
        assert cfg["StartInfo"] == 1

    def test_config_string(self) -> None:
        state_machine = gammu.StateMachine()
        state_machine.SetConfig(
            0,
            {
                "StartInfo": "yes",
                "UseGlobalDebugFile": "no",
                "DebugFile": "dbg.log",
                "SyncTime": "true",
                "Connection": "fbus",
                "LockDevice": "FALSE",
                "DebugLevel": "textall",
                "Device": "",
                "Model": "",
            },
        )
        cfg = state_machine.GetConfig(0)
        assert cfg["StartInfo"] == 1

    def test_config_none(self) -> None:
        state_machine = gammu.StateMachine()
        state_machine.SetConfig(
            0,
            {
                "StartInfo": None,
                "UseGlobalDebugFile": None,
                "DebugFile": "dbg.log",
                "SyncTime": "true",
                "Connection": "dlr3",
                "LockDevice": "NO",
                "DebugLevel": "binary",
                "Device": "",
                "Model": "",
            },
        )
        cfg = state_machine.GetConfig(0)
        assert cfg["StartInfo"] == 0

    def test_init_error(self) -> None:
        with pytest.raises(TypeError):
            gammu.StateMachine(Bar=1)


class DebugTest(unittest.TestCase):
    def setUp(self) -> None:
        gammu.SetDebugLevel("textall")

    def check_operation(self, filename, handle=None) -> None:
        """Executes gammu operation which causes debug logs."""
        gammu.DecodePDU(PDU_DATA)
        gammu.SetDebugFile(None)
        if handle:
            handle.close()
        if filename is not None:
            content = Path(filename).read_text(encoding="utf-8")
            assert "SMS type: Status report" in content

    def test_file(self) -> None:
        testfile = tempfile.NamedTemporaryFile(suffix=".debug", delete=False)
        testfile.close()
        try:
            handle = Path(testfile.name).open("w", encoding="utf-8")
            gammu.SetDebugFile(handle)
            self.check_operation(testfile.name, handle)
        finally:
            gammu.SetDebugFile(None)
            Path(testfile.name).unlink()

    def test_filename(self) -> None:
        testfile = tempfile.NamedTemporaryFile(suffix=".debug", delete=False)
        testfile.close()
        try:
            gammu.SetDebugFile(testfile.name)
            self.check_operation(testfile.name)
        finally:
            gammu.SetDebugFile(None)
            Path(testfile.name).unlink()

    def test_none(self) -> None:
        gammu.SetDebugFile(None)
        self.check_operation(None)

    def test_nothing(self) -> None:
        gammu.SetDebugLevel("nothing")
        testfile = tempfile.NamedTemporaryFile(suffix=".debug", delete=False)
        testfile.close()
        try:
            gammu.SetDebugFile(testfile.name)
            self.check_operation(None)
            content = Path(testfile.name).read_text(encoding="utf-8")
            assert not content
        finally:
            gammu.SetDebugFile(None)
            Path(testfile.name).unlink()
