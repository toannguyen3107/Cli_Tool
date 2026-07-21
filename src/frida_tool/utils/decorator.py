import functools
from frida_tool.utils.color_utils import ANSI
import time
def splitstmtadb(func):
    def wrapper(*args, **kwargs):
        # Code to be executed before the decorated function
        print(f"{ANSI.GREEN}Running command: adb {args[0]}{ANSI.RESET}")
        # Call the decorated function
        result = func(*args, **kwargs)
        return result
    # Return the wrapper function
    return wrapper
def splitstmt(func):
    def wrapper(*args, **kwargs):
        # Code to be executed before the decorated function
        print(f"{ANSI.GREEN}Running command: {args[0]}{ANSI.RESET}")
        # Call the decorated function
        result = func(*args, **kwargs)
        return result
    # Return the wrapper function
    return wrapper
def header(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"\n----------------------{ANSI.RED}{ANSI.BOLD}Running: {func.__name__}{ANSI.RESET}----------------------\n")
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"\n----------------------{ANSI.RED}{ANSI.BOLD}Done: {func.__name__} (Elapsed Time: {elapsed_time:.2f} seconds){ANSI.RESET}----------------------\n")
        return result
    return wrapper
