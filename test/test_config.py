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


@pytest.mark.parametrize(
    "key", ["Model", "DebugLevel", "Device", "Connection", "DebugFile"]
)
@pytest.mark.parametrize("as_bytes", [False, True])
def test_config_string_ownership(key, as_bytes) -> None:
    state_machine = gammu.StateMachine()
    for value in ("textall", "textalldate", "", "text"):
        state_machine.SetConfig(0, {key: value.encode() if as_bytes else value})
        assert state_machine.GetConfig(0)[key] == value

    state_machine.SetConfig(0, {key: None})
    expected = "" if key in {"Model", "DebugLevel"} else None
    assert state_machine.GetConfig(0)[key] == expected


@pytest.mark.parametrize(
    ("values", "message"),
    [
        ({"Model": 123}, "Non string value for Model"),
        ({"DebugLevel": 123}, "Non string value for DebugLevel"),
        ({"Device": 123}, "Non string value for Device"),
        ({"Unknown": "value"}, "Unknown key: Unknown"),
        ({123: "value"}, "Non string key in configuration values"),
    ],
)
def test_config_invalid_strings(values, message) -> None:
    state_machine = gammu.StateMachine()
    state_machine.SetConfig(0, {"Model": "original"})
    with pytest.raises(ValueError, match=message):
        state_machine.SetConfig(0, values)
    assert state_machine.GetConfig(0)["Model"] == "original"
    state_machine.SetConfig(0, {"Model": "replacement", "Localize": "ignored"})
    assert state_machine.GetConfig(0)["Model"] == "replacement"


class ConfigTest(unittest.TestCase):
    def test_config_sections(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "gammurc"
            config_file.write_text(
                "[gammu4]\nconnection = none\ndevice = /dev/null\n",
                encoding="utf-8",
            )

            state_machine = gammu.StateMachine()
            state_machine.ReadConfig(Section=4, Filename=str(config_file))
            state_machine.SetConfig(0, state_machine.GetConfig(4))

            cfg = state_machine.GetConfig(4)
            assert cfg["Connection"] == "none"
            assert cfg["Device"] == "/dev/null"

            with pytest.raises(
                ValueError,
                match="Requested configuration not available",
            ):
                state_machine.GetConfig(100)

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
