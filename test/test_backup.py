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
                    len(backup['PhonePhonebook']) +
                    len(backup['SIMPhonebook']),
                    len(backup_2['PhonePhonebook']) +
                    len(backup_2['SIMPhonebook']),
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

    def test_calendar(self):
        entry = gammu.ReadBackup(
            os.path.join(TEST_DIR, 'rrule.ics')
        )['Calendar'][0]

        # Convert it to vCard
        vc_entry = gammu.EncodeVCALENDAR(entry)
        ic_entry = gammu.EncodeICALENDAR(entry)

        # Convert it back to entry
        entry2 = gammu.DecodeVCS(vc_entry)
        entry3 = gammu.DecodeICS(ic_entry)

        self.assertEqual(entry2['Type'], entry3['Type'])

    def test_todo(self):
        entry = gammu.ReadBackup(
            os.path.join(TEST_DIR, '02.vcs')
        )['ToDo'][0]

        # Convert it to vCard
        vt_entry = gammu.EncodeVTODO(entry)
        it_entry = gammu.EncodeITODO(entry)

        # Convert it back to entry
        entry2 = gammu.DecodeVCS(vt_entry)
        entry3 = gammu.DecodeICS(it_entry)

        self.assertEqual(entry2['Type'], entry3['Type'])

    def test_contact(self):
        entry = gammu.ReadBackup(
            os.path.join(TEST_DIR, 'gammu.vcf')
        )['PhonePhonebook'][0]

        # Convert it to vCard
        vc_entry = gammu.EncodeVCARD(entry)

        # Convert it back to entry
        entry2 = gammu.DecodeVCARD(vc_entry)

        self.assertEqual(entry, entry2)
