import time
import logging
from config import DEBUG

FUNCTION_STATS = {}

def log_time(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        fname = func.__name__
        if fname not in FUNCTION_STATS:
            FUNCTION_STATS[fname] = {"counter": 0, "runtime": 0.0}
        FUNCTION_STATS[fname]["counter"] += 1
        FUNCTION_STATS[fname]["runtime"] += elapsed
        logging.info(f"[TIME] {fname} took {elapsed:.4f} seconds")
        return result
    if DEBUG.get("TIME_LOGGING"):
        return wrapper
    return func