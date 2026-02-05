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
Gammu asynchronous wrapper example with asyncio.

This allows your application to care only about handling received data and not
about phone communication details.
"""

import asyncio
import sys

import gammu
import gammu.asyncworker


async def send_message_async(state_machine, number, message) -> None:
    smsinfo = {
        "Class": -1,
        "Unicode": False,
        "Entries": [{"ID": "ConcatenatedTextLong", "Buffer": message}],
    }
    # Encode messages
    encoded = gammu.EncodeSMS(smsinfo)
    # Send messages
    for encoded_message in encoded:
        # Fill in numbers
        encoded_message["SMSC"] = {"Location": 1}
        encoded_message["Number"] = number
        # Actually send the message
        await state_machine.send_sms_async(encoded_message)


async def get_network_info(worker) -> None:
    info = await worker.get_network_info_async()
    print("NetworkName:", info["NetworkName"])

    # If NetworkName is empty, look it up in the GSMNetworks database
    if not info["NetworkName"] and info["NetworkCode"]:
        network_code = info["NetworkCode"]
        if network_code in gammu.GSMNetworks:
            print("  NetworkName (from DB):", gammu.GSMNetworks[network_code])
        else:
            print("  NetworkName (from DB): Unknown network code")

    print("  State:", info["State"])
    print("  NetworkCode:", info["NetworkCode"])
    print("  CID:", info["CID"])
    print("  LAC:", info["LAC"])


async def get_info(worker) -> None:
    print("Phone information:")
    manufacturer = await worker.get_manufacturer_async()
    print(f"{'Manufacturer':<15}: {manufacturer}")
    model = await worker.get_model_async()
    print(f"{'Model':<15}: {model[0]} ({model[1]})")
    imei = await worker.get_imei_async()
    print(f"{'IMEI':<15}: {imei}")
    firmware = await worker.get_firmware_async()
    print(f"{'Firmware':<15}: {firmware[0]}")


async def main() -> None:
    gammu.SetDebugFile(sys.stderr)
    gammu.SetDebugLevel("textall")

    config = {"Device": "/dev/ttyS6", "Connection": "at"}
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
                print(f"Signal is at {signal['SignalPercent']:d}%")
            except Exception as e:  # noqa: BLE001
                print(f"Exception reading signal: {e}")

            await asyncio.sleep(10)

    except Exception as e:  # noqa: BLE001
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
