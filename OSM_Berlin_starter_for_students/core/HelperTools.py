import time
import functools


def timer(func):
    """Print the runtime of the decorated function"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value      = func(*args, **kwargs)
        run_time   = time.perf_counter() - start_time
        print(" ====> Duration {:.2f} secs: {}".format(run_time, func.__doc__))
        return value
    return wrapper_timer
