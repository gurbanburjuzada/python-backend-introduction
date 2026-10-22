"""
TOPIC: Generators
PURPOSE: Understand all three ways to create generators, how they differ internally,
         and why they exist in real backend codebases.
LEVEL: required for Junior | interview weight: HIGH

Core idea: a generator produces values ONE AT A TIME and pauses between each one.
It does not build the entire result in memory — it computes the next value only
when asked. This is called "lazy evaluation".

Contrast:
  list(range(10_000_000))    → allocates ~80 MB right now
  (i for i in range(10_000_000))  → allocates ~200 bytes, values computed on demand
"""

from typing import Generator, Iterator

# ── THE THREE WAYS TO CREATE A GENERATOR ────────────────────────────────────
#
#  1. Generator function  → uses `yield` inside a def
#  2. Generator expression → (expr for x in iterable)
#  3. Class with __iter__ + __next__  → manual iterator protocol
#
# They all produce objects that implement the ITERATOR PROTOCOL:
#   __iter__(self)  → returns self
#   __next__(self)  → returns next value, raises StopIteration when exhausted
#
# So yes — under the hood they all behave identically from the caller's side.
# The difference is only in HOW you write them, not what you get.


# ══════════════════════════════════════════════════════════════════════════════
# 1. GENERATOR FUNCTION (most common — use this by default)
# ══════════════════════════════════════════════════════════════════════════════

def count_up(start: int, stop: int) -> Generator[int, None, None]:
    """
    Yields integers from start to stop-1.
    Generator[YieldType, SendType, ReturnType] — SendType/ReturnType are None here.
    """
    current = start
    while current < stop:
        yield current  # pauses here, returns current to the caller
        current += 1   # resumes HERE on the next next() call


gen = count_up(0, 3)
# gen is a generator object — nothing has run yet. "Lazy."
print(next(gen))   # -> 0; runs until the first yield keyword
print(next(gen))   # -> 1; resumes after yield, runs until next yield
print(next(gen))
# next(gen)        # StopIteration Error, no more yields left

# In practice you rarely call next() manually — you just iterate:
for value in count_up(0, 5):
    print(value)

# ── 1a. YIELDING FROM ANOTHER ITERABLE: yield from ─────────────────────────


def flatten(nested: list) -> Generator:
    """Flattens one level of nesting"""
    for sublist in nested:
        yield from sublist  # delegates to the inner iterable
        # yield from is equivalent to: for item in sublist: yield item; it has loop inside
        # but yield from also forwards .send() and .throw() correctly


list(flatten([[1, 2], [3, 6, 7], [1, 8], [5, 7, 9]]))

# Industry: used to chain generators, walk directory trees, flatten DB result sets.


# ── 1b. GENERATOR WITH RETURN VALUE ─────────────────────────────────────────
# A generator CAN have a return statement. The value is not yielded —
# it becomes the .value of the StopIteration exception.
# Rarely used directly, but important for yield from delegation.

def producer() -> Generator[int, None, str]:
    yield 1
    yield 2
    return "all done"


gen = producer()

try:
    while True:
        print(next(gen))
except StopIteration as e:
    print(e.value)   # -> "all done"

# ══════════════════════════════════════════════════════════════════════════════
# 2. GENERATOR EXPRESSION (shorthand for simple cases)
# ══════════════════════════════════════════════════════════════════════════════

cubes = (x ** 3 for x in range(1, 11))   # generator object, nothing computed yet
odd_cubes = (z ** 3 for z in range(1, 11) if z % 2 == 1)   # with filter

# Key rule: use () not [] when, otherwise list will be created
# Passing directly to a function that iterates: no extra parenthesis needed

total = sum(x ** 2 for x in range(100))

# Generator expression vs list comprehension:
#   [x**2 for x in range(n)]  → list, all values in memory immediately
#   (x**2 for x in range(n))  → generator, one value at a time
#
# When to use which:
#   - Need random access (items[5])?      → list
#   - Need len()?                         → list
#   - Just iterating once, possibly huge? → generator expression
#   - Passing to sum(), any(), all()?     → generator expression

# A generator expression can only be iterated ONCE. After exhaustion it's empty.
gen = (x for x in range(3))
list(gen)  # → [0, 1, 2]
list(gen)  # → []  ← already exhausted

# ══════════════════════════════════════════════════════════════════════════════
# 3. CLASS-BASED ITERATOR (manual __iter__ + __next__)
# ══════════════════════════════════════════════════════════════════════════════
# Use this when your generator needs to maintain complex state, support
# reset/reuse, or integrate into a class hierarchy.


class Range:
    """Reimplements range to illustrate the iterator protocol"""
    def __init__(self, start: int, stop: int, step: int = 1):
        self.start = start
        self.stop = stop
        self.step = step
        self.current = start   # mutable state lives on the instance

    def __iter__(self) -> "Range":
        self.current = self.start   # reset on each for loop
        return self   # the object is its own iterator

    def __next__(self) -> int:
        if self.current >= self.stop:
            raise StopIteration
        value = self.current
        self.current += self.step
        return value


r = Range(0, 12, 2)
list(r)   # -> [0, 2, 4, 6, 8]
list(r)   # -> [0, 2, 4, 6, 8] works again because __iter__ resets the state

# Contrast with a generator function: once a generator function's object is
# exhausted, it stays exhausted. You must call the function again to get a
# fresh generator. The class above can be reused because __iter__ resets state.

# WHEN TO CHOOSE CLASS OVER FUNCTION:
# ┌──────────────────────────────┬─────────────────────────────────────────┐
# │ Generator function / expr    │ Class-based iterator                    │
# ├──────────────────────────────┼─────────────────────────────────────────┤
# │ Simple sequential logic      │ Complex internal state                  │
# │ Single-use iteration         │ Needs to be restarted/reused            │
# │ 90% of real-world cases      │ Needs extra methods (peek, reset, seek) │
# └──────────────────────────────┴─────────────────────────────────────────┘


# ══════════════════════════════════════════════════════════════════════════════
# 4. .send() — TWO-WAY COMMUNICATION WITH A GENERATOR
# ══════════════════════════════════════════════════════════════════════════════
# yield is an EXPRESSION, not just a statement. It both yields a value OUT
# and receives a value IN via .send().

def running_average() -> Generator[float, float, None]:
    """
    Receives numbers via .send(), yields the running average back.
    This is a coroutine-style generator — it's a data consumer, not a producer.
    """
    total = 0.0
    count = 0
    while True:
        value = yield (total / count if count else 0)
        # ^ yields the current average, then PAUSES.
        # When .send(x) is called, x is assigned to `value` and execution resumes.
        total += value
        count += 1


avg = running_average()
next(avg)   # MUST call next() (or send(None)) first to advance to the
            # first yield — this is called "priming" the generator.
avg.send(10)   # -> 10; total = 0 + 10, count = 0 + 1 = 1
avg.send(30)   # -> 20; total = 10 + 30 = 40, count = 1 + 1 = 2
avg.send(50)   # -> 30; total = 40 + 50 = 90, count = 2 + 1 = 3

# .send() vs next():
#   next(gen)      is exactly equivalent to  gen.send(None)
#   gen.send(x)    resumes the generator AND passes x as the value of the yield expression

# Industry: .send() is the foundation of asyncio's coroutine machinery.
# In modern Python you use `async def / await` instead of .send() directly,
# but understanding .send() explains WHY await works the way it does.


# ══════════════════════════════════════════════════════════════════════════════
# 5. REAL-WORLD INDUSTRY PATTERNS
# ══════════════════════════════════════════════════════════════════════════════

# ── 5a. STREAMING LARGE FILES / DB RESULTS ──────────────────────────────────
# Never load a million-row result set into a list. Use a generator.

def read_large_file(path: str):
    with open(path, "r") as f:
        for line in f:
            yield line.strip()

# In SQLAlchemy / Django ORM you'd use .yield_per() or cursor streaming.
# The pattern is identical: yield one row, let the caller process it,
# then fetch the next — without loading the whole result.

# ── 5b. PIPELINE / PROCESSING CHAINS ────────────────────────────────────────
# Generators compose naturally into data pipelines. Each stage pulls from
# the previous only when it needs the next item — fully lazy end-to-end.


def parse_ints(lines):
    for line in lines:
        try:
            yield int(line)
        except ValueError:
            pass  # skip non-numeric lines


def only_even(numbers):
    for num in numbers:
        if num % 2 == 0:
            yield num

# Pipeline: read → parse → filter → sum (nothing loads into memory)
# lines = read_large_file("numbers.txt")
# numbers = parse_ints(lines)
# evens = only_even(numbers)
# total = sum(evens)

# Industry: ETL jobs, log processing, CSV import pipelines, Kafka consumer loops.

# ── 5c. PAGINATION ──────────────────────────────────────────────────────────


def paginate(query_func, page_size: int = 100):
    """
    Yields items from a paginated API/DB one by one
    hiding th pagination logic from the caller
    """
    page = 0
    while True:
        batch = query_func(offset=page * page_size, limit=page_size)
        if not batch:
            return
        yield from batch
        page += 1

# Caller just does: for user in paginate(db.get_users): ...
# They don't know or care that it's paginated underneath.

# ── 5d. INFINITE SEQUENCES ──────────────────────────────────────────────────


def id_generator(prefix: str = "ID"):
    """Generate unique IDs indefinitely"""
    counter = 0
    while True:
        yield f"{prefix}-{counter:06d}"
        counter += 1


gen = id_generator("ORDER")
next(gen)   # -> "ORDER-000000"
next(gen)   # -> "ORDER-000001"
# Never call list() on this - it runs forever.

# ── INTERVIEW QUESTIONS THIS FILE COVERS ────────────────────────────────────
# Q: Why use a generator instead of a list?
#    → Memory efficiency. A generator computes values on demand; a list holds
#      all values at once. Crucial for large files, DB results, or infinite sequences.
#
# Q: What is StopIteration?
#    → The exception a generator raises when it has no more values to yield.
#      for-loops catch it silently; next() propagates it unless you pass a default.
#
# Q: How do you implement a generator using a class?
#    → Define __iter__ (returns self) and __next__ (returns next value or raises
#      StopIteration). Class-based iterators can be reset; generator functions cannot.
#
# Q: What does .send() do?
#    → Resumes the generator AND passes a value in, which becomes the result of
#      the yield expression inside the generator. You must prime with next() first.
#      It's the mechanism behind asyncio coroutines.
#
# Q: What is an async generator?
#    → An async def function that contains yield. You iterate it with
#      `async for` instead of `for`. Used for streaming async data sources
#      (e.g. reading from an async DB cursor or websocket).
