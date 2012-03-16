"""
peek.tracer
~~~~~~~~~~~

This code is complicated as shit, but it basically recurses and captures
execution times in a tree. Below you'll find an example output structure
with expanded variable names.

Code is inspired and originally based on ``coverage.py``.

::

    {
        "filename": "my_test.py",

        "event": "call",

        # module and function are optional
        "module": "my.test",
        "function": "main",
        "lineno": 0,

        "num_calls": 0,  # same as len(calls)
        "time_spent": 0,

        "children": [
            {
                "event": "line",
                "source": "def main():",

                "num_calls": 0,
                "time_spent": 0,
            },
            {
                "event": "call",
                "source": "    __import__('foo')",

                "filename": "builtins_or_some_shit.py",
                "module": "__builtin__",
                "function": "__import__",
                "lineno": 5,

                "caller": {
                    "lineno": 5,
                }

                "num_calls": 0,
                "time_spent": 0,

                "children": [
                    {
                        "event": "line",
                        "source": "def __import__(foo):",

                        "num_calls": 0,
                        "time_spent": 0,
                    },
                    {
                        "event": "line",
                        "source": "    return sys.modules[foo]",

                        "num_calls": 0,
                        "time_spent": 0,
                    },
                ],
            },
            {
                "event": "return",
                "source": "    return True",

                "num_calls": 0,
                "time_spent": 0,
            },
        ],
    }


:copyright: 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

__all__ = ('Tracer',)

from collections import defaultdict
import inspect
import sys
import time


class Tracer(object):
    """
    A tracer which records timing information for every executed line.

    This code is complicated as hell because it has to determine where
    the origin is so it records the tree correctly.
    """
    def __init__(self, log=False):
        self.data = {}
        self.depth = 0
        self.pause_until = None
        self.data_stack = []
        self.last_exc_back = None
        self.last_exc_firstlineno = 0
        self.log = log

    def _get_struct(self, frame, event):
        filename = inspect.getfile(frame)
        function_name = frame.f_code.co_name
        f_globals = getattr(frame, 'f_globals', {})
        module_name = f_globals.get('__name__')

        try:
            source, lineno = inspect.getsourcelines(frame)
        except IOError:
            source, lineno = [], 0

        pre_frame = frame.f_back

        result = {
            "event": event,

            "filename": filename,
            "module": module_name,
            "function": function_name,

            "num_calls": 0,
            "time_spent": 0,

            "lineno": frame.f_lineno,

            "lines": dict(
                (num, {
                    "num_calls": 0,
                    "time_spent": 0,
                    "source": code[:-1],
                })
                for num, code in enumerate(source, lineno)
            ),

            "children": defaultdict(dict),
            # lineno: {
            #     function_name: struct
            # }
        }

        if pre_frame:
            result["caller"] = {
                "lineno": pre_frame.f_lineno,
            }

        return result

    def _trace(self, frame, event, arg_unused):
        """
        The trace function passed to sys.settrace.
        """
        cur_time = time.time()

        lineno = frame.f_lineno
        depth = self.depth

        filename = inspect.getfile(frame)

        if self.last_exc_back:
            if frame == self.last_exc_back:
                self.data['time_spent'] += (cur_time - self.start_time)
                self.depth -= 1

                self.data = self.data_stack.pop()

            self.last_exc_back = None

        if event == 'call':
            # Update our state
            self.depth += 1

            if self.log:
                print >> sys.stdout, '%s >> %s:%s' % (' ' * (depth - 1), filename, frame.f_code.co_name)

            # origin line number (where it was called from)
            o_lineno = frame.f_back.f_lineno

            if self.pause_until is not None:
                if depth == self.pause_until:
                    self.pause_until = None
                else:
                    return self._trace

            if o_lineno not in self.data['lines']:
                self.pause_until = depth

                return self._trace

            # Append it to the stack
            self.data_stack.append(self.data)

            call_sig = '%s:%s' % (inspect.getfile(frame), frame.f_code.co_name)

            if call_sig not in self.data['children']:
                self.data['children'][o_lineno][call_sig] = self._get_struct(frame, event)

            self.data = self.data['children'][o_lineno][call_sig]

            self.data['num_calls'] += 1

        elif event == 'line':
            # Record an executed line.
            if self.pause_until is None and lineno in self.data['lines']:
                self.data['lines'][lineno]['num_calls'] += 1
                self.data['lines'][lineno]['time_spent'] += (cur_time - self.start_time)

            if self.log:
                print >> sys.stdout, '%s -- %s:%s executing line %d' % (' ' * (depth - 1), filename, frame.f_code.co_name, lineno)

        elif event == 'return':
            timing = (cur_time - self.start_time)

            # Leaving this function, pop the filename stack.
            if self.pause_until is None:
                self.data['time_spent'] += timing
                self.data = self.data_stack.pop()
                self.data['time_spent'] += timing
                # self.data['lines'][lineno]['num_calls'] += 1
                # self.data['lines'][lineno]['time_spent'] += (cur_time - self.start_time)

            if self.log:
                print >> sys.stdout, '%s << %s:%s %.3fs' % (' ' * (depth - 1), filename, frame.f_code.co_name, timing)

            self.depth -= 1

        elif event == 'exception':
            self.last_exc_back = frame.f_back
            self.last_exc_firstlineno = frame.f_code.co_firstlineno

        return self._trace

    def start(self, origin):
        """
        Start this Tracer.

        Return a Python function suitable for use with sys.settrace().
        """
        self.start_time = time.time()
        self.pause_until = None
        self.data.update(self._get_struct(origin, 'origin'))
        self.data_stack.append(self.data)
        sys.settrace(self._trace)
        return self._trace

    def stop(self):
        """
        Stop this Tracer.
        """
        if hasattr(sys, "gettrace") and self.log:
            if sys.gettrace() != self._trace:
                msg = "Trace function changed, measurement is likely wrong: %r"
                print >> sys.stdout, msg % sys.gettrace()
        sys.settrace(None)
