"""
peek.collector
~~~~~~~~~~~~~~

:copyright: 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

__all__ = ('Collector',)

import inspect
import sys
import threading
from peek.tracer import Tracer


class Collector(object):
    def __init__(self, log=False, tracer=Tracer):
        self._tracer_class = Tracer
        self.log = log

    def _start_tracer(self, origin):
        """
        Start a new Tracer object, and store it in self.tracers.
        """
        tracer = self._tracer_class(log=self.log)
        tracer.data = self.data
        fn = tracer.start(origin)
        self.tracers.append(tracer)
        return fn

    def _installation_trace(self, origin):
        """
        Called on new threads, installs the real tracer.
        """
        def _wrapped(frame_unused, event_unused, arg_unused):
            # Remove ourselves as the trace function
            sys.settrace(None)

            # Install the real tracer.
            fn = self._start_tracer(origin)

            # Invoke the real trace function with the current event, to be sure
            # not to lose an event.
            if fn:
                fn = fn(frame_unused, event_unused, arg_unused)

            # Return the new trace function to continue tracing in this scope.
            return fn
        return _wrapped

    def reset(self):
        self.tracers = []
        self.data = {}

    def start(self):
        """
        Start collecting trace information.
        """
        origin = inspect.stack()[1][0]

        self.reset()

        # Install the tracer on this thread.
        self._start_tracer(origin)

        # Install our installation tracer in threading, to jump start other
        # threads.
        # threading.settrace(self._installation_trace(origin))

    def pause(self):
        """
        Pause tracing, but be prepared to resume.
        """
        for tracer in self.tracers:
            tracer.stop()
        threading.settrace(None)

    def stop(self):
        """
        Stop collecting trace information.
        """
        self.pause()
        self.tracers = []

    def get_results(self):
        # the first key should be our trace, lets ignore it
        # the last key is our collector
        return self.data
        # calls = self.data['children']
        # for key, call in calls.iteritems():
        #     print '%s:%s, line %d, %d calls' % (call.get('filename'), call.get('function'), call['lineno'], call['num_calls'])
        #     print '  ', call.get('source')
