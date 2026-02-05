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

import platform
import sqlite3
import threading
import time
from pathlib import Path

import pytest

import gammu
import gammu.smsd

from .test_dummy import DummyTest

MESSAGE_1 = {
    "Text": "python-gammu testing message",
    "SMSC": {"Location": 1},
    "Number": "1234567890",
}
MESSAGE_2 = {
    "Text": "python-gammu second testing message",
    "SMSC": {"Location": 1},
    "Number": "1234567890",
}
MAX_STATUS_RETRIES = 2


def get_script() -> Path:
    """
    Returns SQL script to create database.

    It returns correct script matching used Gammu version.
    """
    version = tuple(int(x) for x in gammu.Version()[0].split("."))

    if version < (1, 36, 7):
        dbver = 14
    elif version < (1, 37, 90):
        dbver = 15
    elif version < (1, 38, 5):
        dbver = 16
    else:
        dbver = 17

    print(f"Gammu version {version}, SMSD DB version {dbver}")

    return Path(__file__).parent / "data" / f"sqlite-{dbver}.sql"


class SMSDDummyTest(DummyTest):
    def setUp(self) -> None:
        if platform.system() == "Windows":
            pytest.skip("SMSD testing not supported on Windows (no DBI driver)")
        super().setUp()
        database = sqlite3.connect(self.test_dir / "smsd.db")
        script = Path(get_script()).read_text(encoding="utf-8")
        database.executescript(script)

        # Check if SMSD with SQLite driver is available
        # This will fail if Gammu was built without SQLite support
        try:
            smsd = gammu.smsd.SMSD(self.config_name)
            # Clean up the test instance
            del smsd
        except gammu.GSMError as exc:
            # Check if the error is related to SMSD configuration/driver
            error_info = exc.args[0] if exc.args else {}
            error_where = error_info.get("Where", "")
            error_code = error_info.get("Code", 0)

            # If error happens during SMSD_ReadConfig, it's likely a driver/config issue
            # Common error codes: 27 (ERR_UNKNOWN), 75 (DB driver initialization failed)
            if error_where == "SMSD_ReadConfig" or error_code in {27, 75}:
                pytest.skip(
                    "SMSD initialization failed (Gammu may be built without required database driver support)"
                )
            # Re-raise if it's a different error
            raise

    def get_smsd(self):
        return gammu.smsd.SMSD(self.config_name)

    def test_init_error(self) -> None:
        with pytest.raises(TypeError):
            gammu.smsd.SMSD(invalid_option=1)

    def test_inject(self) -> None:
        smsd = self.get_smsd()
        smsd.InjectSMS([MESSAGE_1])

    def test_smsd(self) -> None:
        smsd = self.get_smsd()

        # Inject SMS messages
        # Please note that SMSD is not thread safe, so you can not
        # use inject and main loop from different threads
        smsd.InjectSMS([MESSAGE_1])
        smsd.InjectSMS([MESSAGE_2])

        try:
            # Start SMSD thread
            smsd_thread = threading.Thread(target=smsd.MainLoop)
            smsd_thread.start()
            # We need to let it run for some time here to finish initialization
            time.sleep(10)

            # Show SMSD status
            retries = 0
            while retries < MAX_STATUS_RETRIES:
                status = smsd.GetStatus()
                if status["Sent"] >= 2:
                    break
                time.sleep(10)
                retries += 1

            assert status["Received"] == 2, (
                f"Messages were not received as expected ({status['Received']:d})!"
            )
            assert status["Sent"] == 2, (
                f"Messages were not sent as expected ({status['Sent']:d})!"
            )

            time.sleep(1)

        finally:
            # Signal SMSD to stop
            smsd.Shutdown()

            # Wait for it
            smsd_thread.join()

    def test_get_status_not_running(self) -> None:
        """
        Test that GetStatus raises exception when SMSD is not running.

        This test verifies the fix for the issue where GetStatus would cause
        Python to exit instead of raising an exception when SMSD is not running.
        The fix disables the exit_on_failure flag in the SMSD config.
        """
        smsd = self.get_smsd()
        # SMSD is not running, so GetStatus should raise an exception
        # instead of causing Python to exit
        with pytest.raises(gammu.GSMError):
            smsd.GetStatus()
