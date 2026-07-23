import threading
from functools import wraps
from typing import Callable, Any

def debounce(wait_sec: float) -> Callable:
    """
    Decorator that delays a function's execution until after 'wait_sec'
    seconds have elapsed since the last time it was invoked.
    """
    def decorator(func: Callable) -> Callable:
        # Track the active timer container across calls
        timer: threading.Timer | None = None

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> None:
            nonlocal timer

            # Cancel the previous timer if it's still waiting
            if timer is not None:
                timer.cancel()

            # Schedule the function to run after the quiet period
            timer = threading.Timer(wait_sec, func, args=args, kwargs=kwargs)
            timer.start()

        return wrapper
    return decorator
