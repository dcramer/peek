from unittest2 import TestCase
from peek.collector import Collector


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
        collector = Collector()
        collector.start()

        function_one(' world')

        collector.stop()

        data = collector.get_calls()
        self.assertEquals(len(data), 1)

        key = '%s:function_one:5' % __file__
        self.assertIn(key, data)
        result = data[key]

        self.assertIn('f', result)
        self.assertEquals(result['f'], __file__)
        self.assertIn('m', result)
        self.assertEquals(result['m'], __name__)
        self.assertIn('fn', result)
        self.assertEquals(result['fn'], 'function_one')
        self.assertIn('n', result)
        self.assertEquals(result['n'], 1)
        self.assertIn('t', result)
        self.assertGreater(result['t'], 0)

        self.assertIn('c', result)
        calls = result['c']
        self.assertEquals(len(calls), 4)

        import pprint
        pprint.pprint(calls)

        child_key = '%s:function_two:12' % __file__
        self.assertIn(child_key, calls)
        result = calls[child_key]

        self.assertIn('f', result)
        self.assertEquals(result['f'], __file__)
        self.assertIn('m', result)
        self.assertEquals(result['m'], __name__)
        self.assertIn('fn', result)
        self.assertEquals(result['fn'], 'function_two')
        self.assertIn('n', result)
        self.assertEquals(result['n'], 1)
        self.assertIn('t', result)
        self.assertGreater(result['t'], 0)

        self.assertIn('c', result)
        calls = result['c']
        self.assertEquals(len(calls), 2)
