import time
from contextlib import contextmanager

@contextmanager
def stopwatch():
    t0 = time.perf_counter()
    try:
        yield
    finally:
        globals()['_last_elapsed_ms'] = (time.perf_counter() - t0) * 1000.0

def last_elapsed_ms(default=None):
    return globals().get('_last_elapsed_ms', default)
