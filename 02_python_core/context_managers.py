"""
TOPIC: Context Managers
PURPOSE: Understand the with-statement protocol, all ways to implement one,
         and where they appear in real backend projects.
LEVEL: required for Junior | interview weight: HIGH

Core idea: a context manager guarantees that setup runs before a block of code
and teardown runs after it — even if an exception occurs inside the block.

The `with` statement is syntactic sugar for:
    obj.__enter__()       ← setup
    try:
        ...block...
    finally:
        obj.__exit__(...)  ← teardown (always runs)
"""

import contextlib
import threading
import time
import tempfile
import os

# ── 0. WHY THEY EXIST ───────────────────────────────────────────────────────
# Problem: resources (files, DB connections, locks, HTTP sessions) must always
# be released — even when exceptions happen. The naive try/finally works but is
# verbose and easy to forget.

# ❌ Without context manager — easy to forget the finally:
f = open("example.txt", "w")
try:
    f.write("hello")
finally:
    f.close()   # what if you forget this? resource leak.

# ✅ With context manager — teardown is guaranteed and implicit:
with open("example.txt", "w") as f:
    f.write("hello")
# f.close() was called automatically, even if f.write() raised an exception.

# ══════════════════════════════════════════════════════════════════════════════
# 1. CLASS-BASED CONTEXT MANAGER (__enter__ and __exit__)
# ══════════════════════════════════════════════════════════════════════════════


class DatabaseConnection:
    """
    Simulates a DB connection that must always be closed.
    This is the pattern SQLAlchemy sessions, psycopg2 connections, etc. follow.
    """
    def __init__(self, url: str):
        self.url = url
        self.connection = None

    def __enter__(self):
        print(f"Connecting to {self.url}")
        self.connection = {"url": self.url, "open": True}  # simulating a connection
        return self.connection   # this is what `as conn` binds to

    def __exit__(self, exc_type, exc_val, exc_tb):
        # exc_type, exc_val, exc_tb are None if no exception occurred.
        # They hold exception info if the block raised something.
        print("Closing the connection")
        if self.connection:
            self.connection["open"] = False

        if exc_type is not None:
            print(f"exception occurred: {exc_val}")

        return False
        # Return value controls exception suppression:
        #   False (or None) → exception propagates normally (almost always what you want)
        #   True            → exception is SUPPRESSED — the with-block appears to succeed
        # Suppressing is rare; only do it intentionally (e.g. ignoring FileNotFoundError).


with DatabaseConnection("postgresql://localhost/mydb") as conn:
    print(f"Connection to {conn}")
    # raise RuntimeError("something broke")  ← __exit__ still runs if this line is uncommented this

# ── The `as` clause ─────────────────────────────────────────────────────────
# `as conn` binds to the RETURN VALUE of __enter__, NOT to the context manager itself.
# Many beginners assume `as x` gives you the context manager — it gives you what
# __enter__ returns. open() returns a file object; Lock() returns the lock itself.

# ══════════════════════════════════════════════════════════════════════════════
# 2. GENERATOR-BASED: @contextlib.contextmanager (simpler for most cases)
# ══════════════════════════════════════════════════════════════════════════════
# Write a generator function with exactly one yield.
# Code BEFORE yield  →  __enter__
# The yielded value  →  what `as` binds to
# Code AFTER yield   →  __exit__


@contextlib.contextmanager
def timer(label: str):
    """Measures and prints execution time of the wrapped block."""
    start = time.perf_counter()
    try:
        yield   # nothing useful to bind with 'as' here, so yield None
    finally:
        elapsed = time.perf_counter() - start
        print(f"[{label}] {elapsed:.4f}s")


with timer("database query"):
    time.sleep(0.05)
# → [database query] 0.0502s

# ── With exception handling ──────────────────────────────────────────────────


@contextlib.contextmanager
def managed_transaction(session):
    """Commits on success, rolls back on any exception."""
    try:
        yield session
        session.commit()      # runs only if no exception in the block
    except Exception:
        session.rollback()    # runs only if an exception occurred
        raise                 # re-raise so the caller knows something failed
    finally:
        session.close()       # always runs

# Usage (SQLAlchemy style):
# with managed_transaction(db.session) as session:
#     session.add(User(name="Alice"))


# ══════════════════════════════════════════════════════════════════════════════
# 3. CONTEXTLIB UTILITIES WORTH KNOWING
# ══════════════════════════════════════════════════════════════════════════════

# ── 3a. contextlib.suppress — intentionally swallow specific exceptions ──────
with contextlib.suppress(FileNotFoundError):
    open("nonexistent_file.txt")

# No exception raised — execution continues normally.
# Industry: cleaning up temp files, optional cache reads.
# Equivalent to: try: ... except FileNotFoundError: pass — but more readable.

# ── 3b. contextlib.nullcontext — a no-op context manager ────────────────────
# Useful when a context manager is optional (e.g. lock only in threaded mode).

def process(data, lock=None):
    ctx = lock if lock is not None else contextlib.nullcontext()
    with ctx:
        # do work — works whether or not a lock was passed
        pass

# ── 3c. Multiple context managers in one line ────────────────────────────────
# with open("a.txt") as a, open("b.txt") as b:
#     b.write(a.read())
# Both are opened; both are guaranteed to be closed. Left-to-right setup,
# right-to-left teardown.


# ══════════════════════════════════════════════════════════════════════════════
# 4. REAL-WORLD INDUSTRY PATTERNS
# ══════════════════════════════════════════════════════════════════════════════

# ── 4a. Threading lock (most common use in concurrent code) ──────────────────
_lock = threading.Lock()
_counter = 0


def increment():
    global _counter
    with _lock:    # acquires the lock; releases it on exit even if exception
        _counter += 1
# Without the lock, two threads could read-modify-write simultaneously → race condition.

# ── 4b. Temporary directory (testing and file processing) ────────────────────


with tempfile.TemporaryDirectory() as tmpdir:
    path = os.path.join(tmpdir, "output.csv")
    with open(path, "w") as file:
        file.write("id,name\n1,Alice")
    # process the file
# ── 4c. Patching in tests (unittest.mock) ────────────────────────────────────
# from unittest.mock import patch
# with patch("myapp.services.send_email") as mock_send:
#     response = client.post("/register", json={"email": "a@b.com"})
#     mock_send.assert_called_once()
# patch restores the original function when the block exits.

# ── 4d. HTTP session reuse (requests / httpx) ────────────────────────────────
# import httpx
# with httpx.Client() as client:
#     r1 = client.get("https://api.example.com/users")
#     r2 = client.get("https://api.example.com/orders")
# Connection pool is closed when done — avoids leaving sockets open.


# ── INTERVIEW QUESTIONS THIS FILE COVERS ────────────────────────────────────
# Q: What is a context manager and why is it needed?
#    → It guarantees setup and teardown around a code block. Needed to safely
#      manage resources (files, connections, locks) even when exceptions occur.
#
# Q: If an exception occurs inside a with-block, does __exit__ still run?
#    → Yes. __exit__ always runs. The exception info is passed as
#      (exc_type, exc_val, exc_tb). Return False to let it propagate.
#
# Q: How do you implement a context manager using a class?
#    → Define __enter__ (setup, returns the resource) and __exit__
#      (teardown, receives exception info, returns bool for suppression).
#
# Q: How do you implement one using a decorator?
#    → Use @contextlib.contextmanager on a generator function with one yield.
#      Code before yield = __enter__; code after yield (in finally) = __exit__.
#
# Q: What does `as` bind to in a with-statement?
#    → The return value of __enter__, NOT the context manager object itself.
