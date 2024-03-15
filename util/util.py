"""Utils Module"""

from functools import wraps
from time import time
from logs.gr_logger import gr_logger

def timeit(func):
    """Decorator to time function run time

    Args:
        func (Callable): function to time
    """

    @wraps(func)
    def wrap_func(*args, **kwargs):
        t_1 = time()
        result = func(*args, **kwargs)
        t_2 = time()
        gr_logger.debug(f"Function {func.__name__} executed in {(t_2-t_1):.4f}s")
        return result

    return wrap_func

def log_func(func):
    """Decorator to log the function with args

    Args:
        func (Callable): function to log
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            gr_logger.debug(f"Running: {func.__name__}")
            return func(*args, **kwargs)
        except Exception as ex:
            gr_logger.exception(ex)
    # wrapper.__doc__ = func.__doc__
    return wrapper
