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
import asyncio

import gammu.asyncworker

from .test_dummy import DummyTest

WORKER_EXPECT = [
    ("Init", None),
    ("GetIMEI", "999999999999999"),
    ("GetManufacturer", "Gammu"),
    (
        "GetNetworkInfo",
        {
            "CID": "FACE",
            "GPRS": "Attached",
            "LAC": "B00B",
            "NetworkCode": "999 99",
            "NetworkName": "",
            "PacketCID": "DEAD",
            "PacketLAC": "BEEF",
            "PacketState": "HomeNetwork",
            "State": "HomeNetwork",
        },
    ),
    ("GetModel", ("unknown", "Dummy")),
    # ('GetFirmware', ('1.41.0', '20150101', 1.41)), # Mock is returning different values between the local workstation on the CI build
    (
        "GetSignalQuality",
        {"BitErrorRate": 0, "SignalPercent": 42, "SignalStrength": 42},
    ),
    ("SendSMS", 255),
    ("SetIncomingCallback", None),
    ("SetIncomingSMS", None),
    ("pull_func", 1),
    ("Terminate", None),
]


def async_test(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(coro(*args, **kwargs))

    return wrapper


class AsyncWorkerDummyTest(DummyTest):
    results = []

    def callback(self, name, result, error, percents):
        self.results.append((name, result, error, percents))

    def my_pull_func(self, sm):
        self.results.append(("pull_func", sm.ReadDevice()))

    @async_test
    async def test_worker_async(self):
        self.results = []
        worker = gammu.asyncworker.GammuAsyncWorker(self.my_pull_func)
        worker.configure(self.get_statemachine().GetConfig())
        self.results.append(("Init", await worker.init_async()))
        self.results.append(("GetIMEI", await worker.get_imei_async()))
        self.results.append(("GetManufacturer", await worker.get_manufacturer_async()))
        self.results.append(("GetNetworkInfo", await worker.get_network_info_async()))
        self.results.append(("GetModel", await worker.get_model_async()))
        # self.results.append(('GetFirmware', await worker.get_firmware_async()))
        self.results.append(
            ("GetSignalQuality", await worker.get_signal_quality_async())
        )
        message = {
            "Text": "python-gammu testing message",
            "SMSC": {"Location": 1},
            "Number": "555-555-1234",
        }
        self.results.append(("SendSMS", await worker.send_sms_async(message)))
        with self.assertRaises(TypeError):
            await worker.send_sms_async(42)
        with self.assertRaises(Exception):
            await worker.send_sms_async(dict(42))
        self.results.append(
            (
                "SetIncomingCallback",
                await worker.set_incoming_callback_async(self.callback),
            )
        )
        self.results.append(("SetIncomingSMS", await worker.set_incoming_sms_async()))

        await asyncio.sleep(15)

        self.results.append(("Terminate", await worker.terminate_async()))
        self.maxDiff = None
        self.assertEqual(WORKER_EXPECT, self.results)
