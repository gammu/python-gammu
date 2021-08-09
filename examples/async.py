#!/usr/bin/env python
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
"""
python-gammu - Phone communication libary
Gammu asynchronous wrapper example with asyncio. This allows your application to care
only about handling received data and not about phone communication
details.
"""

import asyncio
import sys

import gammu
import gammu.asyncworker


async def send_message_async(state_machine, number, message):
    smsinfo = {
        "Class": -1,
        "Unicode": False,
        "Entries": [{"ID": "ConcatenatedTextLong", "Buffer": message}],
    }
    # Encode messages
    encoded = gammu.EncodeSMS(smsinfo)
    # Send messages
    for message in encoded:
        # Fill in numbers
        message["SMSC"] = {"Location": 1}
        message["Number"] = number
        # Actually send the message
        await state_machine.send_sms_async(message)


async def get_network_info(worker):
    info = await worker.get_network_info_async()
    print("NetworkName:", info["NetworkName"])
    print("  State:", info["State"])
    print("  NetworkCode:", info["NetworkCode"])
    print("  CID:", info["CID"])
    print("  LAC:", info["LAC"])


async def get_info(worker):
    print("Phone infomation:")
    manufacturer = await worker.get_manufacturer_async()
    print("{:<15}: {}".format("Manufacturer", manufacturer))
    model = await worker.get_model_async()
    print("{:<15}: {} ({})".format("Model", model[0], model[1]))
    imei = await worker.get_imei_async()
    print("{:<15}: {}".format("IMEI", imei))
    firmware = await worker.get_firmware_async()
    print("{:<15}: {}".format("Firmware", firmware[0]))


async def main():

    gammu.SetDebugFile(sys.stderr)
    gammu.SetDebugLevel("textall")

    config = dict(Device="/dev/ttyS6", Connection="at")
    worker = gammu.asyncworker.GammuAsyncWorker()
    worker.configure(config)

    try:
        await worker.init_async()

        await get_info(worker)
        await get_network_info(worker)

        await send_message_async(worker, "6700", "BAL")

        # Just a busy waiting for event
        # We need to keep communication with phone to get notifications
        print("Press Ctrl+C to interrupt")
        while 1:
            try:
                signal = await worker.get_signal_quality_async()
                print("Signal is at {:d}%".format(signal["SignalPercent"]))
            except Exception as e:
                print(f"Exception reading signal: {e}")

            await asyncio.sleep(10)

    except Exception as e:
        print("Exception:")
        print(e)

    print("Terminate Start")
    await worker.terminate_async()
    print("Terminate Done")


if __name__ == "__main__":
    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(main())
    finally:
        event_loop.close()
