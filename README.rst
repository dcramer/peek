Peek
====

**This project is still under development**

Peek is a profiling tool which aims to help you track down the core performance problems in your Python application.

It does this by installing a trace hook, which looks at every Python call (similar to line_profiler), and records
how long that call took.


Credits
-------

The implementation of the tracer and several of the "hacks" required to get things like this in place are heavily
inspired by Ned Batchelder's coverage.py project.