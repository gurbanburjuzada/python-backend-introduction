"""
TOPIC: Decorators
PURPOSE: Understand what decorators are, how to build them, and where they appear in real projects.
LEVEL: required for Junior | interview weight: HIGH

A decorator is a function that wraps another function (or class) to add behaviour
before/after it runs — without modifying the original source.
Syntactic sugar: @decorator above a def is identical to: func = decorator(func)
"""

import time
import functools
import logging
from typing import Callable

# ── 0. THE MECHANICS (read this before anything else) ───────────────────────
#
# def my_decorator(func):          # receives the original function
#     @functools.wraps(func)       # preserves __name__, __doc__ of the original
#     def wrapper(*args, **kwargs):
#         # ... do something before
#         result = func(*args, **kwargs)
#         # ... do something after
#         return result
#     return wrapper               # returns the NEW function that replaces the original
#
# Without @functools.wraps, func.__name__ becomes "wrapper" — breaks logging,
# introspection, and pytest output. Always include it.


def timer(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[timer] {func.__name__} took {elapsed: .4f}s")
        return result
    return wrapper


@timer
def slow_query():
    time.sleep(0.1)
    return "Done"

# slow_query()  →  [timer] slow_query took 0.1001s
# Industry: profiling during development; in production you'd use structured
# logging or an APM tool (Datadog, OpenTelemetry) instead of print.


# ── 2. LOGGING DECORATOR ────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def log_call(func: Callable):
    """Logs entry, exit, and any exception for the wrapped function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logging.info("Calling %s | args=%s, kwargs=%s", func.__name__, args, kwargs)
        try:
            result = func(*args, **kwargs)
            logging.info("%s returned %s", func.__name__, result)
            return result
        except Exception as exc:
            logging.info("%s raised the exception %s", func.__name__, exc)
            raise   # re-raise so the caller still gets the exception
    return wrapper


@log_call
def divide(a, b):
    return a / b

# Industry: wrap service-layer functions or API handlers to get automatic
# request/response logs without cluttering business logic.


# ── 3. RETRY DECORATOR (parametrised) ───────────────────────────────────────
# A decorator that accepts arguments needs an extra layer of nesting:
#   retry(3)        → returns a decorator
#   decorator(func) → returns wrapper

def retry(times: int = 3, exceptions: tuple = (Exception, ), delay: float = 0.0):
    """Retry a function up to `times` attempts on specified exceptions."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    logging.warning("%s failed (attempt %d/%d) with exception: %s",
                                    func.__name__, attempt, times, exc)
                    if delay:
                        time.sleep(delay)
            raise last_exc
        return wrapper
    return decorator


@retry(times=3, exceptions=(ConnectionError, ), delay=0.5)
def fetch_data(url: str) -> dict:
    # Simulates an unreliable network call
    raise ConnectionError("timeout")

# Industry: essential for HTTP clients, DB connections, and message-broker
# consumers where transient failures are expected.


# ── 4. CACHING DECORATOR ────────────────────────────────────────────────────
# functools.lru_cache is the built-in version — know it cold.

from functools import lru_cache


@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# fibonacci(50) runs instantly; without caching it would take minutes.
# lru_cache stores (args) → result. Only works when args are hashable.
# fibonacci.cache_info()  →  CacheInfo(hits=48, misses=51, ...)
# fibonacci.cache_clear() →  clears the cache


# Manual version (when you need more control, e.g. TTL or custom key):
def simple_cache(func):
    cache: dict = {}

    @functools.wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper

# ── 5. ACCESS CONTROL / AUTHENTICATION ──────────────────────────────────────
# This pattern is everywhere in Flask and FastAPI.


def require_auth(func: Callable) -> Callable:
    """Simulates a route guard. In real FastAPI you'd use Depends()."""
    @functools.wraps(func)
    def wrapper(request: dict, *args, **kwargs):
        if not request.get("user"):
            raise PermissionError("Unauthenticated")
        return func(request, *args, **kwargs)
    return wrapper


@require_auth
def get_profile(request: dict) -> dict:
    return {"user": request["user"], "data": "..."}

# get_profile({"user": "alice"})  → ok
# get_profile({})                 → PermissionError

# ── 6. CLASS-BASED DECORATOR ────────────────────────────────────────────────
# A class with __call__ can act as a decorator. Useful when the decorator
# needs to maintain state across calls.


class CountCalls:
    def __init__(self, func: Callable):
        functools.update_wrapper(self, func)   # equivalent @functools.wraps
        self.func = func
        self.call_count = 0

    def __call__(self, *args, **kwargs):
        self.call_count += 1
        print(f"[CountCalls] {self.func.__name__} called {self.call_count} time(s)")
        return self.func(*args, **kwargs)


@CountCalls
def greet(name: str) -> str:
    return f"Hello, {name}"

# greet("Alice") → [CountCalls] greet called 1 time(s)
# greet("Bob")   → [CountCalls] greet called 2 time(s)
# greet.call_count  → 2


# ── 7. STACKING DECORATORS ──────────────────────────────────────────────────
# Decorators apply bottom-up. The one closest to def is applied first.

@timer
@log_call
def compute(x: int) -> int:
    return x ** 5

# Equivalent to: compute = timer(log_call(compute))
# Execution order: timer's wrapper → log_call's wrapper → actual compute()

# ── 8. BUILT-IN DECORATORS TO KNOW ─────────────────────────────────────────


class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def area(self) -> float:
        return 3.14159 * self._radius ** 2

    @staticmethod              # no self, no cls; pure class function
    def validate_radius(r: int):
        return r < 0

    @classmethod               # receives the class (cls), not the instance
    def from_diameter(cls, diameter: float) -> "Circle":
        return cls(diameter / 2)   # factory pattern -- alternative constructor


c = Circle.from_diameter(10)

# c.area            → 78.53...
# Circle.validate_radius(-1)  → False

# @property:       computed attribute, avoids exposing raw fields
# @staticmethod:   utility that logically belongs to the class but needs no instance
# @classmethod:    alternative constructors (from_json, from_dict, from_env, etc.)
#                  also used in Django model managers


# ── INTERVIEW QUESTIONS THIS FILE COVERS ────────────────────────────────────
# Q: What is a decorator?
#    → A callable that takes a function and returns a new function with added behaviour.
#
# Q: Why functools.wraps?
#    → Preserves __name__ and __doc__. Without it, all decorated functions look
#      like "wrapper" to debuggers, loggers, and test frameworks.
#
# Q: How do you make a decorator that accepts arguments?
#    → Add one more nesting level: argument-receiver → decorator → wrapper.
#      (Section 3 above — the retry decorator.)
#
# Q: Can a class be a decorator?
#    → Yes. Implement __init__ to accept the function and __call__ to run it.
#      (Section 6 — CountCalls.)
#
# Q: What is an async decorator?
#    → Use async def wrapper(...) and await func(...) inside it.
#      Required when decorating coroutines (async def functions).
