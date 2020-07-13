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
'''
Asynchronous communication to phone.

Mostly you should use only L{GammuWorker} class, others are only helpers
which are used by this class.
'''

import gammu
import threading
import queue


class InvalidCommand(Exception):
    '''
    Exception indicating invalid command.
    '''
    def __init__(self, value):
        '''
        Initializes exception.

        @param value: Name of wrong command.
        @type value: string
        '''
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        '''
        Returns textual representation of exception.
        '''
        return 'Invalid command: "{0}"'.format(self.value)


def check_worker_command(command):
    '''
    Checks whether command is valid.

    @param command: Name of command.
    @type command: string
    '''
    if hasattr(gammu.StateMachine, command):
        return

    raise InvalidCommand(command)


class GammuCommand(object):
    '''
    Storage of single command for gammu.
    '''
    def __init__(self, command, params=None, percentage=100):
        '''
        Creates single command instance.
        '''
        check_worker_command(command)
        self._command = command
        self._params = params
        self._percentage = percentage

    def get_command(self):
        '''
        Returns command name.
        '''
        return self._command

    def get_params(self):
        '''
        Returns command params.
        '''
        return self._params

    def get_percentage(self):
        '''
        Returns percentage of current task.
        '''
        return self._percentage

    def __str__(self):
        '''
        Returns textual representation.
        '''
        if self._params is not None:
            return '{0} {1}'.format(self._command, self._params)
        else:
            return '{0} ()'.format(self._command)


class GammuTask(object):
    '''
    Storage of taks for gammu.
    '''
    def __init__(self, name, commands):
        '''
        Creates single command instance.

        @param name: Name of task.
        @type name: string
        @param commands: List of commands to execute.
        @type commands: list of tuples or strings
        '''
        self._name = name
        self._list = []
        self._pointer = 0
        for i in range(len(commands)):
            if isinstance(commands[i], tuple):
                cmd = commands[i][0]
                try:
                    params = commands[i][1]
                except IndexError:
                    params = None
            else:
                cmd = commands[i]
                params = None
            percents = round(100 * (i + 1) / len(commands))
            self._list.append(GammuCommand(cmd, params, percents))

    def get_next(self):
        '''
        Returns next command to be executed as L{GammuCommand}.
        '''
        result = self._list[self._pointer]
        self._pointer += 1
        return result

    def get_name(self):
        '''
        Returns task name.
        '''
        return self._name

def gammu_pull_device(state_machine):
    state_machine.ReadDevice()

class GammuThread(threading.Thread):
    '''
    Thread for phone communication.
    '''
    def __init__(self, queue, config, callback, pull_func = gammu_pull_device):
        '''
        Initialises thread data.

        @param queue: Queue with events.
        @type queue: queue.Queue object.

        @param config: Gammu configuration, same as
        L{StateMachine.SetConfig} accepts.
        @type config: hash

        @param callback: Function which will be called upon operation
        completing.
        @type callback: Function, needs to accept four params: name of
        completed operation, result of it, error code and percentage of
        overall operation. This callback is called from different
        thread, so please take care of various threading issues in other
        modules you use.
        '''
        threading.Thread.__init__(self)
        self._kill = False
        self._terminate = False
        self._sm = gammu.StateMachine()
        self._callback = callback
        self._queue = queue
        self._sm.SetConfig(0, config)
        self._pull_func = pull_func

    def _do_command(self, name, cmd, params, percentage=100):
        '''
        Executes single command on phone.
        '''
        func = getattr(self._sm, cmd)
        error = 'ERR_NONE'
        result = None
        try:
            if params is None:
                result = func()
            elif isinstance(params, dict):
                result = func(**params)
            else:
                result = func(*params)
        except gammu.GSMError as info:
            errcode = info.args[0]['Code']
            error = gammu.ErrorNumbers[errcode]

        self._callback(name, result, error, percentage)

    def run(self):
        '''
        Thread body, which handles phone communication. This should not
        be used from outside.
        '''
        start = True
        while not self._kill:
            try:
                if start:
                    task = GammuTask('Init', ['Init'])
                    start = False
                else:
                    # Wait at most ten seconds for next command
                    task = self._queue.get(True, 10)
                try:
                    while True:
                        cmd = task.get_next()
                        self._do_command(
                            task.get_name(),
                            cmd.get_command(),
                            cmd.get_params(),
                            cmd.get_percentage()
                        )
                except IndexError:
                    try:
                        if task.get_name() != 'Init':
                            self._queue.task_done()
                    except (AttributeError, ValueError):
                        pass
            except queue.Empty:
                if self._terminate:
                    break
                # Read the device to catch possible incoming events
                try:
                    self._pull_func(self._sm)
                except Exception as ex:
                    self._callback("ReadDevice", None, ex, 0)

    def kill(self):
        '''
        Forces thread end without emptying queue.
        '''
        self._kill = True

    def join(self, timeout=None):
        '''
        Terminates thread and waits for it.
        '''
        self._terminate = True
        threading.Thread.join(self, timeout)


class GammuWorker(object):
    '''
    Wrapper class for asynchronous communication with Gammu. It spaws
    own thread and then passes all commands to this thread. When task is
    done, caller is notified via callback.
    '''

    def __init__(self, callback, pull_func = gammu_pull_device):
        '''
        Initializes worker class.

        @param callback: See L{GammuThread.__init__} for description.
        '''
        self._thread = None
        self._callback = callback
        self._config = {}
        self._lock = threading.Lock()
        self._queue = queue.Queue()
        self._pull_func = pull_func

    def enqueue_command(self, command, params):
        '''
        Enqueues command.

        @param command: Command(s) to execute. Each command is tuple
        containing function name and it's parameters.
        @type command: tuple of list of tuples
        @param params: Parameters to command.
        @type params: tuple or string
        '''
        self._queue.put(GammuTask(command, [(command, params)]))

    def enqueue_task(self, command, commands):
        '''
        Enqueues task.

        @param command: Command(s) to execute. Each command is tuple
        containing function name and it's parameters.
        @type command: tuple of list of tuples
        @param commands: List of commands to execute.
        @type commands: list of tuples or strings
        '''
        self._queue.put(GammuTask(command, commands))

    def enqueue(self, command, params=None, commands=None):
        '''
        Enqueues command or task.

        @param command: Command(s) to execute. Each command is tuple
        containing function name and it's parameters.
        @type command: tuple of list of tuples
        @param params: Parameters to command.
        @type params: tuple or string
        @param commands: List of commands to execute. When this is not
        none, params are ignored and command is taken as task name.
        @type commands: list of tuples or strings
        '''
        if commands is not None:
            self.enqueue_task(command, commands)
        else:
            self.enqueue_command(command, params)

    def configure(self, config):
        '''
        Configures gammu instance according to config.

        @param config: Gammu configuration, same as
        L{StateMachine.SetConfig} accepts.
        @type config: hash
        '''
        self._config = config

    def abort(self):
        '''
        Aborts any remaining operations.
        '''
        raise NotImplementedError

    def initiate(self):
        '''
        Connects to phone.
        '''
        self._thread = GammuThread(self._queue, self._config, self._callback, self._pull_func)
        self._thread.start()

    def terminate(self, timeout=None):
        '''
        Terminates phone connection.
        '''
        self.enqueue('Terminate')
        self._thread.join(timeout)
        self._thread = None
