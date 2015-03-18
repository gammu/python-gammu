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
import glob
import tempfile
import os.path

TEST_DIR = os.path.join(os.path.dirname(__file__), 'data')
TEST_FILES_CALENDAR = (
    glob.glob(os.path.join(TEST_DIR, '*.ics')) +
    glob.glob(os.path.join(TEST_DIR, '*.vcs'))
)
TEST_FILES_CONTACTS = (
    glob.glob(os.path.join(TEST_DIR, '*.vcf'))
)
TEST_CONTACTS = ('.lmb', '.vcf', '.backup')
TEST_CALENDAR = ('.vcs', '.ics', '.backup')


class BackupTest(unittest.TestCase):
    def perform_test(self, filename, extensions):
        out_files = [
            tempfile.NamedTemporaryFile(suffix=extension)
            for extension in extensions
        ]
        out_backup = tempfile.NamedTemporaryFile(suffix='.backup')
        try:
            backup = gammu.ReadBackup(filename)
            for out in out_files:
                # Save to new format
                gammu.SaveBackup(out.name, backup)

                # Parse created file
                backup_2 = gammu.ReadBackup(out.name)

                # Check content length
                self.assertEqual(
                    len(backup['Calendar']),
                    len(backup_2['Calendar']),
                    'Failed to compare calendar in {0}'.format(filename)
                )
                self.assertEqual(
                    len(backup['PhonePhonebook']) + len(backup['SIMPhonebook']),
                    len(backup_2['PhonePhonebook']) + len(backup_2['SIMPhonebook']),
                    'Failed to compare phonebook in {0}'.format(filename)
                )

                # Try converting to .backup
                gammu.SaveBackup(out_backup.name, backup)
        finally:
            for handle in out_files:
                handle.close()
            out_backup.close()

    def test_convert_contacts(self):
        for filename in TEST_FILES_CONTACTS:
            self.perform_test(filename, TEST_CONTACTS)

    def test_convert_calendar(self):
        for filename in TEST_FILES_CALENDAR:
            self.perform_test(filename, TEST_CALENDAR)
