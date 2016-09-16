
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

from contextlib import contextmanager

import sublime


@contextmanager
def unlock(panel):
    """Unlocks panel read only yields and lock again
    """

    panel.set_read_only(False)
    yield
    panel.set_read_only(True)


class RTPanel:
    """A thin wrapper class around sublime panels to show RT information
    """

    def __init__(self, success=None, failure=None):
        self._panel = None
        if success is not None:
            self.on_success = success
        if failure is not None:
            self.on_failure = failure

        self.create_rtpanel()

    def create_rtpanel(self):
        """Create or retrieve a Sublime Output Panel
        """

        self._panel = sublime.active_window().create_output_panel(
            'anaconda_go_rt_panel'
        )
        self._panel.set_read_only(True)
        self._panel.settings().set('scroll_past_end', False)

    def show_panel(self):
        """Show the inner panel
        """

        self._panel.show(0)
        sublime.active_window().run_command(
            'show_panel', {'panel': 'output.anaconda_go_rt_panel'}
        )

    def update(self, data):
        """Update panel data
        """

        with unlock(self._panel):
            self._panel.run_command(
                'append', {
                    'characters': data, 'force': True, 'scroll_to_end': True
                }
            )

    def notify(self, proc, data, error=False):
        """Impelements notify to get notifications from AsyncProc
        """

        if type(data) is bytes:
            data = data.decode('utf8')
        self.update(data)

    def complete(self, proc):
        """Implements complete to complete operations when AsyncProc is done
        """

        if proc.poll() != 0:
            if hasattr(self, 'on_failure'):
                self.on_failure(proc)
        else:
            if hasattr(self, 'on_success'):
                self.on_success(proc)
