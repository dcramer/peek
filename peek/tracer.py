"""
peek.tracer
~~~~~~~~~~~


Code is inspired and originally based on ``coverage.py``.

:copyright: 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

import sys
import time
from collections import OrderedDict


class Tracer(object):
    """
    A tracer which records timing information for every executed line.

    Statistics generated from the Tracer resemble the following:

    OrderedDict([("filename:function_name", {
        "filename": "filename",
        "module": "module.name",
        "function": "function_name',
        "num_calls": 0,
        "time_spent": 0,
        "calls": OrderedDict([
            # recursive input same as root
        ])
    })])
    """
    def __init__(self, logger=None):
        self.cur_file_data = None
        self.last_time = 0
        self.data_stack = []
        self.last_exc_back = None
        self.last_exc_firstlineno = 0
        self.logger = logger

    def _get_data_struct(self, frame):
        filename = frame.f_code.co_filename
        function_name = frame.f_code.co_name
        f_globals = getattr(frame, 'f_globals', {})
        module_name = f_globals.get('__name__')
        return {
            "filename": filename,
            "module": module_name,
            "function": function_name,
            "num_calls": 0,
            "time_spent": 0,
            "calls": OrderedDict(),
        }

    def _trace(self, frame, event, arg_unused):
        """
        The trace function passed to sys.settrace.
        """
        cur_time = time.time()

        if self.logger:
            self.logger.debug("trace event: %s %r @%d" % (
                  event, frame.f_code.co_filename, frame.f_lineno))

        if self.last_exc_back:
            if frame == self.last_exc_back:
                # Someone forgot a return event.
                self.cur_file_data, self.last_time = self.data_stack.pop()
                # TODO: is this correct?
                self.cur_file_data['time_spent'] += (cur_time - self.last_time)

            self.last_exc_back = None

        if event == 'call':
            # Entering a new function context.  Decide if we should trace
            # in this file.

            # Append it to the stack
            self.data_stack.append((self.cur_file_data, cur_time))

            filename = frame.f_code.co_filename
            function_name = frame.f_code.co_name
            key = '%s:%s' % (filename, function_name)

            if key not in self.cur_file_data['calls']:
                self.cur_file_data['calls'][key] = self._get_data_struct(frame)

            self.cur_file_data = self.cur_file_data['calls'][key]
            self.cur_file_data['num_calls'] += 1

            # TODO: do we need this
            # Set the last_line to -1 because the next arc will be entering a
            # code block, indicated by (-1, n).
            # self.last_line = -1

        elif event == 'line':
            # Record an executed line.
            if self.cur_file_data is not None:
                # TODO
                pass
                # self.cur_file_data[frame.f_lineno] = None
            # self.last_line = frame.f_lineno

        elif event == 'return':
            # Leaving this function, pop the filename stack.
            if self.cur_file_data:
                self.cur_file_data['time_spent'] += (cur_time - self.last_time)
            self.cur_file_data, self.last_time = self.data_stack.pop()

        elif event == 'exception':
            self.last_exc_back = frame.f_back
            self.last_exc_firstlineno = frame.f_code.co_firstlineno

        return self._trace

    def start(self):
        """
        Start this Tracer.

        Return a Python function suitable for use with sys.settrace().
        """
        sys.settrace(self._trace)
        return self._trace

    def stop(self):
        """
        Stop this Tracer.
        """
        if hasattr(sys, "gettrace") and self.logger:
            if sys.gettrace() != self._trace:
                msg = "Trace function changed, measurement is likely wrong: %r"
                self.logger.warn(msg % sys.gettrace())
        sys.settrace(None)

    def get_stats(self):
        """
        Return a dictionary of statistics, or None.
        """
        return None
