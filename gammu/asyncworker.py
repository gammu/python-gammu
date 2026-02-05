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
"""Async extensions for gammu."""

import asyncio

import gammu
import gammu.worker


class GammuAsyncThread(gammu.worker.GammuThread):
    """Thread for phone communication."""

    def __init__(self, queue, config, callback, pull_func) -> None:
        """Initialize thread."""
        super().__init__(queue, config, callback, pull_func)

    def _do_command(self, future, cmd, params, percentage=100) -> None:
        """Execute single command on phone."""
        func = getattr(self._sm, cmd)
        result = None
        try:
            if params is None:
                result = func()
            elif isinstance(params, dict):
                result = func(**params)
            else:
                result = func(*params)
        except gammu.GSMError as info:
            errcode = info.args[0]["Code"]
            error = gammu.ErrorNumbers[errcode]
            self._callback(future, result, error, percentage)
        # pylint: disable-next=broad-except
        except Exception as exception:  # noqa: BLE001
            self._callback(future, None, exception, percentage)
        else:
            self._callback(future, result, None, percentage)


def gammu_pull_device(sm) -> None:
    sm.ReadDevice()


class GammuAsyncWorker(gammu.worker.GammuWorker):
    """Extend gammu worker class for async operations."""

    def worker_callback(self, name, result, error, percents) -> None:
        """Execute command from the thread worker."""
        future = None
        if name == "Init" and self._init_future is not None:
            future = self._init_future
        elif name == "Terminate" and self._terminate_future is not None:
            # Set _kill to true on the base class to avoid waiting for termination
            self._thread._kill = True  # pylint: disable=protected-access
            future = self._terminate_future
        elif hasattr(name, "set_result"):
            future = name

        if future is not None:
            if error is None:
                self._loop.call_soon_threadsafe(future.set_result, result)
            else:
                exception = error
                if not isinstance(error, Exception):
                    exception = gammu.GSMError(error)
                self._loop.call_soon_threadsafe(future.set_exception, exception)

    def __init__(self, pull_func=gammu_pull_device) -> None:
        """
        Initialize the worker class.

        @param callback: See L{GammuThread.__init__} for description.
        """
        super().__init__(self.worker_callback, pull_func)
        self._loop = asyncio.get_event_loop()
        self._init_future = None
        self._terminate_future = None
        self._thread = None
        self._pull_func = pull_func

    async def init_async(self) -> None:
        """Connect to phone."""
        self._init_future = self._loop.create_future()

        self._thread = GammuAsyncThread(
            self._queue, self._config, self._callback, self._pull_func
        )
        self._thread.start()

        await self._init_future
        self._init_future = None

    async def get_imei_async(self):
        """Get the IMEI of the device."""
        future = self._loop.create_future()
        self.enqueue(future, commands=[("GetIMEI", ())])
        return await future

    async def get_network_info_async(self):
        """Get the network info in the device."""
        future = self._loop.create_future()
        self.enqueue(future, commands=[("GetNetworkInfo", ())])
        return await future

    async def get_manufacturer_async(self):
        """Get the manufacturer of the device."""
        future = self._loop.create_future()
        self.enqueue(future, commands=[("GetManufacturer", ())])
        return await future

    async def get_model_async(self):
        """Get the model of the device."""
        future = self._loop.create_future()
        self.enqueue(future, commands=[("GetModel", ())])
        return await future

    async def get_firmware_async(self):
        """Get the firmware version of the device."""
        future = self._loop.create_future()
        self.enqueue(future, commands=[("GetFirmware", ())])
        return await future

    async def get_signal_quality_async(self):
        """Get signal quality from phone."""
        future = self._loop.create_future()
        self.enqueue(future, commands=[("GetSignalQuality", ())])
        return await future

    async def send_sms_async(self, message):
        """Send sms message via the phone."""
        future = self._loop.create_future()
        self.enqueue(future, commands=[("SendSMS", [message])])
        return await future

    async def set_incoming_callback_async(self, callback):
        """Set the callback to call from phone."""
        future = self._loop.create_future()
        self.enqueue(future, commands=[("SetIncomingCallback", [callback])])
        return await future

    async def set_incoming_sms_async(self):
        """Activate SMS notifications from phone."""
        future = self._loop.create_future()
        self.enqueue(future, commands=[("SetIncomingSMS", ())])
        return await future

    async def terminate_async(self) -> None:
        """Terminate phone communication."""
        self._terminate_future = self._loop.create_future()
        self.enqueue("Terminate")
        await self._terminate_future

        await asyncio.to_thread(self._thread.join)

        self._thread = None
