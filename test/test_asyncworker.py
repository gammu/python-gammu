# -*- coding: UTF-8 -*-
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
import gammu.asyncworker
from .test_dummy import DummyTest


WORKER_EXPECT = [
    ('Init', None),
    ('GetIMEI', '999999999999999'),
    ('GetManufacturer', 'Gammu'),
    ('GetModel', 'Gammu'),
    ('Terminate', None)
]

class AsyncWorkerDummyTest(DummyTest):
    results = []

    async def test_worker_async(self):
        self.results = []
        worker = gammu.asyncworker.GammuAsyncWorker()
        worker.configure(self.get_statemachine().GetConfig())
        self.results.append(('Init', await worker.init_async()))
        self.results.append(('GetIMEI', await worker.get_imei_async()))
        self.results.append(('GetManufacturer', await worker.get_manufacturer_async()))
        self.results.append(('GetModel', await worker.get_model_async()))
        self.results.append(('Terminate', await worker.terminate_async()))
        self.maxDiff = None
        self.assertEqual(WORKER_EXPECT, self.results)

