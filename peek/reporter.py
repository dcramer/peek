"""
peek.reporter
~~~~~~~~~~~~~

:copyright: 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

__all__ = ('Reporter',)

import json
import os
import os.path


class Reporter(object):
    def __init__(self, origin, collector, output=None):
        self.origin = origin
        self.collector = collector

        if output is None:
            output = os.path.join(os.getcwd(), 'peekhtml')

        self.output = os.path.normpath(output)

    def report(self):
        raise NotImplementedError


class HTMLReporter(Reporter):
    """
    An HTML reporter.

    This actually just dumps some JSON to a file, which a static HTML page will
    pull in and render.
    """
    # def _get_origin(self, data, origin):
    #     if origin in data:
    #         return {origin: data[origin]}

    #     for key, value in data.iteritems():
    #         if key.startswith(origin):
    #             return {key: value}

    #     for key, value in data.iteritems():
    #         return self._get_origin(value['children'], origin)

    # def get_files(self, calls, files=None):
    #     if files is None:
    #         files = set()
    #     for key, value in calls.iteritems():
    #         if 'f' in value:
    #             files.add(value['f'])
    #         if 'c' in value:
    #             self.get_files(value['c'], files)
    #     return files

    def report(self):
        results = self.collector.get_results()
        # calls = self._get_origin(self.collector.get_results(), self.origin)

        if not os.path.exists(self.output):
            os.makedirs(self.output)

        with open(os.path.join(self.output, 'data.json'), 'w') as fp:
            fp.write('Peek.load(' + json.dumps(results) + ');')
