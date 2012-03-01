"""
peek.collector
~~~~~~~~~~~~~~

:copyright: 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

__all__ = ('Collector',)

import sys
import threading
# TODO: handle Python < 2.7
from collections import OrderedDict
from peek.tracer import Tracer


class Collector(object):
    def __init__(self, logger=None, tracer=Tracer):
        self._collectors = []
        self._tracer_class = Tracer
        self.logger = logger
        self.reset()

    def _start_tracer(self):
        """
        Start a new Tracer object, and store it in self.tracers.
        """
        tracer = self._tracer_class(logger=self.logger)
        tracer.cur_file_data = self.data
        fn = tracer.start()
        self.tracers.append(tracer)
        return fn

    def _installation_trace(self, frame_unused, event_unused, arg_unused):
        """
        Called on new threads, installs the real tracer.
        """
        # Remove ourselves as the trace function
        sys.settrace(None)

        # Install the real tracer.
        fn = self._start_tracer()

        # Invoke the real trace function with the current event, to be sure
        # not to lose an event.
        if fn:
            fn = fn(frame_unused, event_unused, arg_unused)

        # Return the new trace function to continue tracing in this scope.
        return fn

    def reset(self):
        """
        Clear collected data, and prepare to collect more.
        """
        # A dictionary mapping filenames to dicts with linenumber keys,
        # or mapping filenames to dicts with linenumber pairs as keys.
        self.data = {
            "num_calls": 0,
            "time_spent": 0,
            "calls": OrderedDict(),
        }

        # Our active Tracers.
        self.tracers = []

    def start(self):
        """
        Start collecting trace information.
        """
        if self._collectors:
            self._collectors[-1].pause()
        self._collectors.append(self)

        # Check to see whether we had a fullcoverage tracer installed.
        traces0 = None
        if hasattr(sys, "gettrace"):
            fn0 = sys.gettrace()
            if fn0:
                tracer0 = getattr(fn0, '__self__', None)
                if tracer0:
                    traces0 = getattr(tracer0, 'traces', None)

        # Install the tracer on this thread.
        fn = self._start_tracer()

        if traces0:
            for args in traces0:
                (frame, event, arg), lineno = args
                fn(frame, event, arg, lineno=lineno)

        # Install our installation tracer in threading, to jump start other
        # threads.
        threading.settrace(self._installation_trace)

    def pause(self):
        """
        Pause tracing, but be prepared to `resume`.
        """
        for tracer in self.tracers:
            tracer.stop()
            stats = tracer.get_stats()
            if stats:
                print("\nCoverage.py tracer stats:")
                for k in sorted(stats.keys()):
                    print("%16s: %s" % (k, stats[k]))
        threading.settrace(None)

    def stop(self):
        """
        Stop collecting trace information.
        """
        assert self._collectors
        assert self._collectors[-1] is self

        self.pause()
        self.tracers = []

        # Remove this Collector from the stack, and resume the one underneath
        # (if any).
        self._collectors.pop()
        if self._collectors:
            self._collectors[-1].resume()

    def get_calls(self):
        # the first key should be our trace, lets ignore it
        # the last key should be our stop call, lets ignore it
        return dict((k, v) for k, v in self.data['calls'].items()[1:-1])
