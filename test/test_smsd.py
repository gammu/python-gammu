# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
#
# Copyright © 2003 - 2015 Michal Čihař <michal@cihar.com>
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
from .test_dummy import DummyTest
import gammu.smsd
import os
import os.path
import threading
import time
import sqlite3

SQLITE_SCRIPT = os.path.join(os.path.dirname(__file__), 'data', 'sqlite.sql')
MESSAGE_1 = {
    'Text': 'python-gammu testing message',
    'SMSC': {'Location': 1},
    'Number': '1234567890'
}
MESSAGE_2 = {
    'Text': 'python-gammu second testing message',
    'SMSC': {'Location': 1},
    'Number': '1234567890'
}


class SMSDDummyTest(DummyTest):
    def setUp(self):
        super(SMSDDummyTest, self).setUp()
        database = sqlite3.connect(
            os.path.join(self.test_dir, 'smsd.db')
        )
        with open(SQLITE_SCRIPT, 'r') as handle:
            database.executescript(handle.read())

    def get_smsd(self):
        return gammu.smsd.SMSD(self.config_name)

    def test_init_error(self):
        self.assertRaises(TypeError, gammu.smsd.SMSD, Bar=1)

    def test_inject(self):
        smsd = self.get_smsd()
        smsd.InjectSMS([MESSAGE_1])

    def test_smsd(self):
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
            while retries < 2:
                status = smsd.GetStatus()
                if status['Sent'] >= 2:
                    break
                time.sleep(10)
                retries += 1

            self.assertEqual(
                status['Received'],
                2,
                'Messages were not received as expected (%d)!' %
                status['Received']
            )
            self.assertEqual(
                status['Sent'],
                2,
                'Messages were not sent as expected (%d)!' %
                status['Sent']
            )

            time.sleep(1)

        finally:
            # Signal SMSD to stop
            smsd.Shutdown()

            # Wait for it
            smsd_thread.join()
