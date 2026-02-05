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

import contextlib
import datetime
import os.path
import pathlib
import platform
import shutil
import stat
import tempfile
import unittest

import pytest

import gammu

DUMMY_DIR = os.path.join(os.path.dirname(__file__), "data", "gammu-dummy")
TEST_FILE = os.path.join(os.path.dirname(__file__), "data", "sqlite-14.sql")
CONFIGURATION = """
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
"""


class DummyTest(unittest.TestCase):
    test_dir = None
    config_name = None
    dummy_dir = None
    _called = False
    _state_machine = None

    def setUp(self) -> None:
        self.test_dir = tempfile.mkdtemp()
        self.dummy_dir = os.path.join(self.test_dir, "gammu-dummy")
        self.config_name = os.path.join(self.test_dir, ".gammurc")
        shutil.copytree(DUMMY_DIR, self.dummy_dir)
        pathlib.Path(self.config_name).write_text(
            CONFIGURATION.format(path=self.test_dir), encoding="utf-8"
        )

    def tearDown(self) -> None:
        if self._state_machine:
            self._state_machine.Terminate()
        shutil.rmtree(self.test_dir)

    def get_statemachine(self):
        state_machine = gammu.StateMachine()
        state_machine.ReadConfig(Filename=self.config_name)
        state_machine.Init()
        self._state_machine = state_machine
        return state_machine

    def fake_incoming_call(self) -> None:
        """Fake incoming call."""
        filename = os.path.join(self.dummy_dir, "incoming-call")
        pathlib.Path(filename).write_text("\n", encoding="utf-8")

    def check_incoming_call(self) -> None:
        """Checks whether incoming call faking is supported."""
        current = tuple(int(x) for x in gammu.Version()[2].split("."))
        if current < (1, 37, 91):
            pytest.skip(f"Not supported in version {gammu.Version()[2]}")

    def call_callback(self, state_machine, response, data) -> None:
        """Callback on USSD data."""
        self._called = True
        assert response == "Call"
        assert data["Number"] == "+800123456"


class BasicDummyTest(DummyTest):  # noqa: PLR0904
    def test_model(self) -> None:
        state_machine = self.get_statemachine()
        assert state_machine.GetModel()[1] == "Dummy"

    def test_diverts(self) -> None:
        state_machine = self.get_statemachine()
        diverts = state_machine.GetCallDivert()
        assert diverts == [
            {"CallType": "All", "Timeout": 0, "Number": "", "DivertType": "AllTypes"}
        ]

        state_machine.SetCallDivert("AllTypes", "All", "123456789")
        diverts = state_machine.GetCallDivert()
        assert diverts == [
            {
                "CallType": "All",
                "Timeout": 0,
                "Number": "123456789",
                "DivertType": "AllTypes",
            }
        ]

    def test_dial(self) -> None:
        state_machine = self.get_statemachine()
        state_machine.DialVoice("123456")

    def test_battery(self) -> None:
        state_machine = self.get_statemachine()
        status = state_machine.GetBatteryCharge()
        assert status == {
            "BatteryVoltage": 4200,
            "PhoneTemperature": 22,
            "BatteryTemperature": 22,
            "ChargeState": "BatteryConnected",
            "ChargeVoltage": 4200,
            "BatteryCapacity": 2000,
            "BatteryPercent": 100,
            "ChargeCurrent": 0,
            "PhoneCurrent": 500,
        }

    def test_memory(self) -> None:
        state_machine = self.get_statemachine()
        status = state_machine.GetMemoryStatus(Type="ME")

        remain = status["Used"]

        assert status["Used"] == 3

        start = True

        while remain > 0:
            if start:
                entry = state_machine.GetNextMemory(Start=True, Type="ME")
                start = False
            else:
                entry = state_machine.GetNextMemory(
                    Location=entry["Location"], Type="ME"
                )
            remain -= 1

    def test_getmemory(self) -> None:
        state_machine = self.get_statemachine()

        location = state_machine.AddMemory(
            {
                "MemoryType": "SM",
                "Entries": [
                    {"Type": "Number_Mobile", "Value": "123456"},
                    {"Type": "Text_Name", "Value": "Jmeno"},
                ],
            }
        )

        read = state_machine.GetMemory("SM", location)
        assert len(read["Entries"]) == 2

    def test_calendar(self) -> None:
        state_machine = self.get_statemachine()
        status = state_machine.GetCalendarStatus()

        remain = status["Used"]

        assert status["Used"] == 2

        start = True

        while remain > 0:
            if start:
                entry = state_machine.GetNextCalendar(Start=True)
                start = False
            else:
                entry = state_machine.GetNextCalendar(Location=entry["Location"])
            remain -= 1

    def test_sms(self) -> None:
        state_machine = self.get_statemachine()
        status = state_machine.GetSMSStatus()

        remain = status["SIMUsed"] + status["PhoneUsed"] + status["TemplatesUsed"]

        assert remain == 6

        start = True

        sms = []

        while remain > 0:
            if start:
                sms.append(state_machine.GetNextSMS(Start=True, Folder=0))
                start = False
            else:
                sms.append(
                    state_machine.GetNextSMS(Location=sms[-1][0]["Location"], Folder=0)
                )
            remain -= len(sms)

        data = gammu.LinkSMS(sms)

        for item in data:
            message = gammu.DecodeSMS(item)
            if message is None:
                assert item[0]["UDH"]["Type"] == "NoUDH"

    def test_todo(self) -> None:
        state_machine = self.get_statemachine()
        status = state_machine.GetToDoStatus()

        remain = status["Used"]

        assert status["Used"] == 2

        start = True

        while remain > 0:
            if start:
                entry = state_machine.GetNextToDo(Start=True)
                start = False
            else:
                entry = state_machine.GetNextToDo(Location=entry["Location"])
            remain -= 1

    def test_sms_folders(self) -> None:
        state_machine = self.get_statemachine()
        folders = state_machine.GetSMSFolders()
        assert len(folders) == 5

    def ussd_callback(self, state_machine, response, data) -> None:
        """Callback on USSD data."""
        self._called = True
        assert response == "USSD"
        assert data["Text"] == "Reply for 1234"
        assert data["Status"] == "NoActionNeeded"

    def test_ussd(self) -> None:
        self._called = False
        state_machine = self.get_statemachine()
        state_machine.SetIncomingCallback(self.ussd_callback)
        state_machine.SetIncomingUSSD()
        state_machine.DialService("1234")
        assert self._called

    def test_sendsms(self) -> None:
        state_machine = self.get_statemachine()
        message = {
            "Text": "python-gammu testing message",
            "SMSC": {"Location": 1},
            "Number": "123456",
        }

        state_machine.SendSMS(message)

    def test_sendsms_long(self) -> None:
        state_machine = self.get_statemachine()
        text = (
            "Very long python-gammu testing message sent from example python script. "
        ) * 10
        smsinfo = {
            "Class": -1,
            "Unicode": False,
            "Entries": [{"ID": "ConcatenatedTextLong", "Buffer": text}],
        }

        # Encode messages
        encoded = gammu.EncodeSMS(smsinfo)

        assert len(encoded) == 5

        # Send messages
        for message in encoded:
            # Fill in numbers
            message["SMSC"] = {"Location": 1}
            message["Number"] = "123456"

            # Actually send the message
            state_machine.SendSMS(message)

    def test_filesystem(self) -> None:
        state_machine = self.get_statemachine()
        fs_info = state_machine.GetFileSystemStatus()
        assert fs_info == {
            "UsedImages": 0,
            "Used": 1000000,
            "UsedThemes": 0,
            "Free": 10101,
            "UsedSounds": 0,
        }

    def test_deletefile(self) -> None:
        state_machine = self.get_statemachine()
        with pytest.raises(gammu.ERR_FILENOTEXIST):
            state_machine.DeleteFile("testfolder/nonexisting.png")
        state_machine.DeleteFile("file5")

    def test_deletefolder(self) -> None:
        state_machine = self.get_statemachine()
        with pytest.raises(gammu.ERR_FILENOTEXIST):
            state_machine.DeleteFolder("testfolder")
        state_machine.AddFolder("", "testfolder")
        state_machine.DeleteFolder("testfolder")

    @unittest.skipIf(platform.system() == "Windows", "Not supported on Windows")
    def test_emoji_folder(self) -> None:
        state_machine = self.get_statemachine()
        name = "test-😘"
        with pytest.raises(gammu.ERR_FILENOTEXIST):
            state_machine.DeleteFolder(name)
        assert name == state_machine.AddFolder("", name)
        # Check the folder exists as expected on filesystem
        assert os.path.exists(os.path.join(self.dummy_dir, "fs", name))
        state_machine.DeleteFolder(name)

    def test_addfile(self) -> None:
        state_machine = self.get_statemachine()
        file_stat = os.stat(TEST_FILE)
        ttime = datetime.datetime.fromtimestamp(file_stat.st_mtime)
        content = pathlib.Path(TEST_FILE).read_bytes()
        file_f = {
            "ID_FullName": "testfolder",
            "Name": "sqlite.sql",
            "Modified": ttime,
            "Folder": 0,
            "Level": 1,
            "Used": file_stat.st_size,
            "Buffer": content,
            "Type": "Other",
            "Protected": 0,
            "ReadOnly": 0,
            "Hidden": 0,
            "System": 0,
            "Handle": 0,
            "Pos": 0,
            "Finished": 0,
        }
        state_machine.AddFolder("", "testfolder")
        while not file_f["Finished"]:
            file_f = state_machine.AddFilePart(file_f)

    def test_fileattributes(self) -> None:
        state_machine = self.get_statemachine()
        state_machine.SetFileAttributes(
            "file5", ReadOnly=1, Protected=0, System=1, Hidden=1
        )

    def test_getnextfile(self) -> None:
        state_machine = self.get_statemachine()
        file_f = state_machine.GetNextFileFolder(1)
        folders = 0
        files = 0
        while True:
            if file_f["Folder"]:
                folders += 1
            else:
                files += 1
            try:
                file_f = state_machine.GetNextFileFolder(0)
            except gammu.ERR_EMPTY:
                break
        assert folders == 3
        assert files == 6

    def test_save_ringtone_permissions(self) -> None:
        """Test that SaveRingtone creates files with restrictive permissions."""
        # Create a complete ringtone dictionary with all required fields
        ringtone = {
            "Name": "TestRingtone",
            "Notes": [
                {
                    "Type": "Note",
                    "Value": 113,  # Note value
                    "Tempo": 120,
                    "Scale": 220,  # Valid scale: 55, 110, 220, 440, or 880
                    "Style": "Natural",
                    "Note": "C",
                    "Duration": "1_4",
                    "DurationSpec": "NoSpecialDuration",
                }
            ],
        }

        # Test 1: Save using string filename
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".rttl") as f:
            temp_file = f.name
        os.unlink(temp_file)  # Remove it so SaveRingtone can create it fresh

        try:
            # Save the ringtone
            gammu.SaveRingtone(temp_file, ringtone, "rttl")

            # Check that the file was created
            assert os.path.exists(temp_file)

            # Check file permissions - should be owner read/write only
            # Skip permission check on Windows as it handles permissions differently
            if platform.system() != "Windows":
                file_stat = os.stat(temp_file)
                file_mode = stat.S_IMODE(file_stat.st_mode)

                # File should have owner read/write permissions (0o600)
                # Check that group and others don't have any permissions
                assert (file_mode & stat.S_IRWXG) == 0, (
                    f"Group has permissions: {oct(file_mode)}"
                )
                assert (file_mode & stat.S_IRWXO) == 0, (
                    f"Others have permissions: {oct(file_mode)}"
                )

                # Verify owner has read and write permissions
                assert (file_mode & stat.S_IRUSR) != 0, (
                    f"Owner missing read permission: {oct(file_mode)}"
                )
                assert (file_mode & stat.S_IWUSR) != 0, (
                    f"Owner missing write permission: {oct(file_mode)}"
                )
        finally:
            # Clean up - use try-except to handle case where file doesn't exist
            with contextlib.suppress(FileNotFoundError):
                os.unlink(temp_file)

        # Test 2: Test multiple formats to ensure comprehensive coverage
        formats_to_test = ["rttl", "ott", "imy"]
        for fmt in formats_to_test:
            with tempfile.NamedTemporaryFile(
                mode="wb", delete=False, suffix=f".{fmt}"
            ) as f:
                temp_file = f.name
            os.unlink(temp_file)

            try:
                gammu.SaveRingtone(temp_file, ringtone, fmt)
                assert os.path.exists(temp_file), f"File not created for format {fmt}"

                # Verify permissions for each format
                if platform.system() != "Windows":
                    file_stat = os.stat(temp_file)
                    file_mode = stat.S_IMODE(file_stat.st_mode)
                    assert (file_mode & stat.S_IRWXG) == 0, (
                        f"Format {fmt}: Group has permissions"
                    )
                    assert (file_mode & stat.S_IRWXO) == 0, (
                        f"Format {fmt}: Others have permissions"
                    )
            finally:
                with contextlib.suppress(FileNotFoundError):
                    os.unlink(temp_file)

    def test_incoming_call(self) -> None:
        self.check_incoming_call()
        self._called = False
        state_machine = self.get_statemachine()
        state_machine.SetIncomingCallback(self.call_callback)
        state_machine.SetIncomingCall()
        state_machine.GetSignalQuality()
        self.fake_incoming_call()
        state_machine.GetSignalQuality()
        assert self._called
