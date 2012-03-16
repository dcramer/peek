"""
peek.runner
~~~~~~~~~~~

A large majority of the CLI and its implementation are from Ned Batchelder's coverage.py.

:copyright: 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

import imp
import os.path
import sys


BUILTINS = sys.modules['__builtin__']


class ExceptionDuringRun(Exception):
    pass


class NoSource(Exception):
    pass


def run_python_file(filename, args, package=None, collector=None):
    """Run a python file as if it were the main program on the command line.

    `filename` is the path to the file to execute, it need not be a .py file.
    `args` is the argument array to present as sys.argv, including the first
    element naming the file being executed.  `package` is the name of the
    enclosing package, if any.

    """
    # Create a module to serve as __main__
    old_main_mod = sys.modules['__main__']
    main_mod = imp.new_module('__main__')
    sys.modules['__main__'] = main_mod
    main_mod.__file__ = filename
    if package:
        main_mod.__package__ = package
    main_mod.__builtins__ = sys.modules['__builtin__']

    # Set sys.argv and the first path element properly.
    old_argv = sys.argv
    old_path0 = sys.path[0]
    sys.argv = args
    if package:
        sys.path[0] = ''
    else:
        sys.path[0] = os.path.abspath(os.path.dirname(filename))

    try:
        # Open the source file.
        try:
            source_file = open(filename, 'rU')
        except IOError:
            raise NoSource("No file to run: %r" % filename)

        try:
            source = source_file.read()
        finally:
            source_file.close()

        # We have the source.  `compile` still needs the last line to be clean,
        # so make sure it is, then compile a code object from it.
        if source[-1] != '\n':
            source += '\n'
        code = compile(source, filename, "exec")

        # Execute the source file.
        try:
            exec code in main_mod.__dict__
        except SystemExit:
            # The user called sys.exit().  Just pass it along to the upper
            # layers, where it will be handled.
            raise
        except:
            # Something went wrong while executing the user code.
            # Get the exc_info, and pack them into an exception that we can
            # throw up to the outer loop.  We peel two layers off the traceback
            # so that the coverage.py code doesn't appear in the final printed
            # traceback.
            typ, err, tb = sys.exc_info()
            raise ExceptionDuringRun(typ, err, tb.tb_next.tb_next)
    finally:
        # Restore the old __main__
        sys.modules['__main__'] = old_main_mod

        # Restore the old argv and path
        sys.argv = old_argv
        sys.path[0] = old_path0


def main(argv=None):
    from optparse import OptionParser

    if argv is None:
        argv = sys.argv[1:]

    usage = "python -m peek [-o output_file_path] scriptfile [arg] ..."
    parser = OptionParser(usage=usage)
    parser.allow_interspersed_args = False
    parser.add_option('-o', '--output', dest="output",
        help="Save stats to <outfile> directory", default=None)

    if not argv:
        parser.print_usage()
        sys.exit(2)

    (options, args) = parser.parse_args()
    sys.argv[:] = args

    if len(args) > 0:
        progname = args[0]
        sys.path.insert(0, os.path.dirname(progname))

        from peek.collector import Collector
        from peek.reporter import HTMLReporter

        collector = Collector(log=(not options.output))
        collector.start()

        try:
            run_python_file(progname, args)
        finally:
            collector.stop()

            reporter = HTMLReporter(progname, collector, output=options.output)
            reporter.report()

    else:
        parser.print_usage()


if __name__ == '__main__':
    main()
