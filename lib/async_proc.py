
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import time
import threading
import subprocess

PIPE = subprocess.PIPE


class AsyncProc:
    """
    AsyncProc is just a thin wrapper around subprocess.Popen using
    threads to non block on wait and be able to stream output in realtime
    """

    class Status:
        NONE = None
        RUNNING = 'running'
        DONE = 'done'
        FAILED = 'fail'
        TIMED_OUT = 'timed_out'

    def __init__(self, callback, *args, **kwargs):
        self.exit = False
        self.error = None
        self.watchers = []
        self.popen_args = args
        self.callbak = callback
        self.status = self.Status.NONE

        if 'cwd' not in kwargs:
            kwargs['cwd'] = os.getcwd()

        if os.name == 'nt':
            kwargs['startupinfo'] = self.startupinfo

        self.popen_kwargs = kwargs

    @property
    def startupinfo(self):
        """Return back the startupinfo config for Windows
        """

        sinfo = subprocess.STARTUPINFO()
        sinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        return sinfo

    @property
    def elapsed(self):
        """Return back the number of seconds since start
        """

        return time.time() - self.started_at

    def poll(self):
        """Fine wrapper around self.proc.poll
        """

        return self.proc.poll()

    def add_watcher(self, watcher):
        """Add a new watcher to the proccess watchers list
        """

        self.watchers.append(watcher)

    def run(self):
        """Run this AsyncProc
        """

        self.started_at = time.time()
        if self.status != self.Status.NONE:
            print('error: this proccess is already finished!')
            return

        self.status = self.Status.RUNNING
        print(self.popen_kwargs)
        self.proc = subprocess.Popen(
            self.popen_args, stdout=PIPE, stderr=PIPE, **self.popen_kwargs
        )
        if self.proc is None:
            self.status = self.Status.FAILED
            self.error = 'AsyncProc inner proccess is None after call Popen'
            self.callback({'status': 'failed', 'msg': self.error})
            return

        threading.Thread(target=self.monitor_stdout).start()
        threading.Thread(target=self.monitor_stderr).start()

    def broadcast(self, msg):
        """Broadcast a message to all the watchers
        """

        [w.notify(self, msg) for w in self.watchers]

    def monitor_stdout(self):
        """Monitor self.proc.stdout
        """

        while True:
            data = os.read(self.proc.stdout.fileno(), 0x8000)
            if len(data) == 0:
                self.proc.stdout.close()
                [w.complete(self) for w in self.watchers]
                if self.error is None:
                    self.status = self.Status.DONE
                break

            [w.notify(self, data) for w in self.watchers]

    def monitor_stderr(self):
        """Monitor self.proc.stderr
        """

        while True:
            data = os.read(self.proc.stderr.fileno(), 0x8000)
            if len(data) == 0:
                self.proc.stderr.close()
                break
            self.error = data.decode()
            self.status = self.Status.FAILED
            [w.notify(self, data, True) for w in self.watchers]
