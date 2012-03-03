import time


def function_one(arg):
    # a comment
    foo = arg
    bar = 'hello'
    function_two(foo, bar)


def function_two(foo, bar):
    result = bar + ' ' + foo
    return result


def main():
    for n in xrange(10):
        function_one(str(n))
        time.sleep(0.1)

if __name__ == '__main__':
    main()
