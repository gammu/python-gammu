"""Async extensions for gammu."""
import asyncio

import gammu
import gammu.worker


class GammuAsyncThread(gammu.worker.GammuThread):
    """Thread for phone communication."""

    def __init__(self, queue, config, callback, pull_func):
        """Initialize thread."""
        super().__init__(queue, config, callback, pull_func)

    def _do_command(self, future, cmd, params, percentage=100):
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
        except Exception as exception:  # pylint: disable=broad-except
            self._callback(future, None, exception, percentage)
        else:
            self._callback(future, result, None, percentage)


def gammu_pull_device(sm):
    sm.ReadDevice()


class GammuAsyncWorker(gammu.worker.GammuWorker):
    """Extend gammu worker class for async operations."""

    def worker_callback(self, name, result, error, percents):
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

    def __init__(self, pull_func=gammu_pull_device):
        """Initialize the worker class.

        @param callback: See L{GammuThread.__init__} for description.
        """
        super().__init__(self.worker_callback, pull_func)
        self._loop = asyncio.get_event_loop()
        self._init_future = None
        self._terminate_future = None
        self._thread = None
        self._pull_func = pull_func

    async def init_async(self):
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
        result = await future
        return result

    async def send_sms_async(self, message):
        """Send sms message via the phone."""
        future = self._loop.create_future()
        self.enqueue(future, commands=[("SendSMS", [message])])
        result = await future
        return result

    async def set_incoming_callback_async(self, callback):
        """Set the callback to call from phone."""
        future = self._loop.create_future()
        self.enqueue(future, commands=[("SetIncomingCallback", [callback])])
        result = await future
        return result

    async def set_incoming_sms_async(self):
        """Activate SMS notifications from phone."""
        future = self._loop.create_future()
        self.enqueue(future, commands=[("SetIncomingSMS", ())])
        result = await future
        return result

    async def terminate_async(self):
        """Terminate phone communication."""
        self._terminate_future = self._loop.create_future()
        self.enqueue("Terminate")
        await self._terminate_future

        while self._thread.is_alive():
            await asyncio.sleep(5)
        self._thread = None
