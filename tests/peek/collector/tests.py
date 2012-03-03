from unittest2 import TestCase
from peek.collector import Collector


def collect():
    collector = Collector()
    collector.start()

    function_one(' world')

    collector.stop()

    return collector


def function_one(arg):
    # a comment
    foo = arg
    bar = 'hello'
    function_two(foo, bar)


def function_two(foo, bar):
    result = bar + foo
    return result


class CollectorIntegrationTestCase(TestCase):
    def test_does_trace(self):
        collector = collect()

        data = collector.get_results()
        self.assertGreater(len(data), 0)

        key = 9
        self.assertIn(key, data)
        result = data[key]

        self.assertIn('filename', result)
        self.assertEquals(result['filename'], __file__)
        self.assertIn('module', result)
        self.assertEquals(result['module'], __name__)
        self.assertIn('function', result)
        self.assertEquals(result['function'], 'function_one')
        self.assertIn('num_calls', result)
        self.assertEquals(result['num_calls'], 1)
        self.assertIn('time_spent', result)
        self.assertGreater(result['time_spent'], 0)

        self.assertIn('children', result)
        calls = result['children']
        self.assertEquals(len(calls), 5, calls.keys())

        child_key = 20
        self.assertIn(child_key, calls)
        result = calls[child_key]

        self.assertIn('filename', result)
        self.assertEquals(result['filename'], __file__)
        self.assertIn('module', result)
        self.assertEquals(result['module'], __name__)
        self.assertIn('function', result)
        self.assertEquals(result['function'], 'function_two')
        self.assertIn('num_calls', result)
        self.assertEquals(result['num_calls'], 1)
        self.assertIn('time_spent', result)
        self.assertGreater(result['time_spent'], 0)

        self.assertIn('children', result)
        calls = result['children']
        self.assertEquals(len(calls), 3, calls.keys())

