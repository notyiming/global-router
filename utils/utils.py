"""Utils Module"""

from time import time

def timeit(func):
    """Decorator to time function run time

    Args:
        func (_type_): function to time
    """

    def wrap_func(*args, **kwargs):
        t_1 = time()
        result = func(*args, **kwargs)
        t_2 = time()
        print(f"Function {func.__name__!r} executed in {(t_2-t_1):.4f}s")
        return result

    return wrap_func
