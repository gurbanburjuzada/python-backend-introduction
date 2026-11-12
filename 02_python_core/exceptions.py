"""
TOPIC: Exceptions
PURPOSE: Understand Python's exception system fully — hierarchy, handling,
         custom exceptions, and patterns you'll see in real backend code.
LEVEL: required for Junior | interview weight: HIGH

Exceptions are not just error messages. They are objects that carry information
up the call stack until something handles them — or the program crashes.
"""

# ── 0. THE EXCEPTION HIERARCHY ───────────────────────────────────────────────
#
# BaseException
# ├── SystemExit            ← raised by sys.exit() — do NOT catch with Exception
# ├── KeyboardInterrupt     ← Ctrl+C — do NOT catch with Exception
# ├── GeneratorExit         ← when a generator is closed
# └── Exception             ← everything you normally work with
#     ├── ValueError        ← right type, wrong value:  int("abc")
#     ├── TypeError         ← wrong type entirely:       "a" + 1
#     ├── KeyError          ← missing dict key:          d["missing"]
#     ├── IndexError        ← out of range:              lst[999]
#     ├── AttributeError    ← no such attribute:         None.strip()
#     ├── FileNotFoundError ← (subclass of OSError)
#     ├── PermissionError   ← (subclass of OSError)
#     ├── RuntimeError      ← generic "something went wrong at runtime"
#     ├── NotImplementedError ← abstract methods not yet implemented
#     ├── StopIteration     ← generator/iterator exhausted
#     └── ... many more
#
# KEY RULE: catch Exception, not BaseException.
# `except BaseException` catches SystemExit and KeyboardInterrupt too —
# your program will ignore Ctrl+C and sys.exit(), which is almost never right.

import logging
import contextlib


# ══════════════════════════════════════════════════════════════════════════════
# 1. try / except / else / finally — the FULL syntax
# ══════════════════════════════════════════════════════════════════════════════

def read_config(path: str) -> dict:
    try:
        with open(path) as f:
            data = f.read()
        result = {"raw": data}

    except FileNotFoundError:
        # Specific exception first — most specific to least specific.
        print(f"Config file not found: {path}")
        result = {}
    except (PermissionError, OSError) as exc:
        # Catch multiple exception types in one clause.
        # `as exc` binds the exception object so you can inspect it.
        print(f"Could not read file {exc}")
        result = {}
    except Exception as exc:
        # Broad catch-all — always last. Log and re-raise in real code (see §3).
        print(f"Unexpected Error {exc}")
        raise
    else:
        # Runs ONLY if no exception was raised in the try block.
        # This is the "success path" — cleaner than cramming it into try.
        # Most developers don't know this clause exists — it comes up in interviews.
        print("File read successfully!")
    finally:
        # ALWAYS runs — exception or not, return or not.
        # Use for cleanup that must happen regardless (close files, release locks).
        # Note: open() inside a `with` already handles this, but the pattern applies
        # to any resource not managed by a context manager.
        print("read_config finished")

    return result

# ══════════════════════════════════════════════════════════════════════════════
# 2. CUSTOM EXCEPTIONS — the right way
# ══════════════════════════════════════════════════════════════════════════════
# In real projects you never raise raw ValueError("user not found").
# You define a hierarchy that matches your domain. This lets callers
# catch exactly what they care about.


class AppError(Exception):
    """Base for all application exceptions. Catch this to handle any app error."""
    pass


class ValidationError(AppError):
    """Raised when input data fails validation"""
    def __init__(self, field, message):
        self.field = field
        self.message = message
        super().__init__(f"Validation failed in '{field}': {message}")


class NotFoundError(AppError):
    """Raised when requested resource does not exist"""
    def __init__(self, resource: str, identifier):
        self.resource = resource
        self.identifier = identifier
        super().__init__(f"{resource} with id={identifier!r} not found")


class PermissionError(AppError):
    """Raised when authenticated user lacks permission"""
    pass


#Usage:
def get_user(user_id: int) -> dict:
    users = {1: {"name": "ALice"}}
    if user_id not in users:
        raise NotFoundError("User", user_id)
    return users[user_id]

try:
    get_user(999)
except NotFoundError as exc:
    print(exc)              # User with id=999 not found
    print(exc.resource)     # User
    print(exc.identifier)   # 999

except AppError:
    # Catches any app error — fallback if you don't need the specifics
    pass

# Industry pattern: FastAPI, Flask, and Django all let you register exception
# handlers by exception type. A clean hierarchy means clean HTTP error mapping:
#   NotFoundError        → 404
#   ValidationError      → 422
#   PermissionDeniedError → 403
#   AppError (catch-all) → 500


# ══════════════════════════════════════════════════════════════════════════════
# 3. RAISING, RE-RAISING, AND CHAINING
# ══════════════════════════════════════════════════════════════════════════════

# ── raise ────────────────────────────────────────────────────────────────────
def validate_age(age: int):
    if not isinstance(age, int):
        raise TypeError(f"age must be int, got {type(age).__name__}")
    if age < 0 or age > 150:
        raise ValidationError("age", f"must be in 0-150, got {age}")

# ── bare raise — re-raise the current exception ──────────────────────────────
def process():
    try:
        validate_age(-5)
    except ValidationError:
        print("Logging the Error ...")
        raise   # re-raises the same exception with the original traceback intact
                # NEVER do: raise exc  — that resets the traceback to this line

# ── raise ... from — exception chaining ──────────────────────────────────────
# When you catch one exception and raise another, chain them so the original
# context is not lost. Python shows both in the traceback.


def load_user_from_db(user_id: int):
    try:
        # Simulate a DB driver error
        raise ConnectionError("DB connection refused")
    except ConnectionError as exc:
        raise NotFoundError("User", user_id) from exc
    # Traceback will say:
    # "The above exception was the direct cause of the following exception"

    # Suppress chaining (when you intentionally don't want the original cause shown):

# ══════════════════════════════════════════════════════════════════════════════
# 4. REAL-WORLD PATTERNS
# ══════════════════════════════════════════════════════════════════════════════
# ── 4a. Log and re-raise (the correct catch-all pattern) ─────────────────────


logger = logging.getLogger(__name__)


def service_call():
    try:
        pass     # do work
    except AppError:
        raise   # known errors bubble up — let the caller or framework handle them
    except Exception as exc:
        logger.exception("Unexpected error in service call")
        raise RuntimeError("Internal server error") from exc
        # logger.exception() logs the full traceback automatically

# ── 4b. contextlib.suppress — intentional silent swallow ─────────────────────


def delete_if_exists(path: str):
    with contextlib.suppress(FileNotFoundError):
        import os; os.remove(path)
    # Cleaner than: try: os.remove(path) except FileNotFoundError: pass

# ── 4c. Returning sentinel vs raising — when to choose which ─────────────────
# Return None/False/empty:  when "not found" is a normal, expected outcome
# Raise an exception:       when "not found" is exceptional and callers must handle it
#
# Bad: def get_user(id) → returns None silently → caller forgets to check → AttributeError later
# Good: raise NotFoundError → caller is forced to handle it → crash is loud and early

# ── 4d. Grouping exception info on the object ─────────────────────────────────


class BulkValidationError(AppError):
    """Collect multiple validation errors before raising once."""
    def __init__(self, errors: str):
        self.errors = errors
        super().__init__(f"{len(errors)} validation error(s): {errors}")


def validate_form(data: dict):
    errors = []
    if not data.get("email"):
        errors.append({"field": "email", "msg": "required"})
    if not data.get("name"):
        errors.append({"field": "name", "msg": "required"})
    if errors:
        raise BulkValidationError(errors)

    return errors

# FastAPI / Pydantic use this exact pattern internally.

# ── INTERVIEW QUESTIONS THIS FILE COVERS ────────────────────────────────────
# Q: What does the else clause in try/except do?
#    → Runs ONLY when no exception was raised in the try block. Useful to
#      separate the "success continuation" from the try body itself.
#
# Q: What is the difference between Exception and BaseException?
#    → BaseException is the root of everything, including SystemExit and
#      KeyboardInterrupt. Exception is the root of all "normal" errors.
#      Always catch Exception unless you specifically need the others.
#
# Q: How do you re-raise an exception without losing the traceback?
#    → Bare `raise` with no argument. Writing `raise exc` resets the traceback
#      to the current line, making debugging harder.
#
# Q: What is exception chaining (`raise X from Y`)?
#    → Explicitly links a new exception to its cause. Python includes both in
#      the traceback. Use it when translating low-level errors (DB, network)
#      into domain exceptions.
#
# Q: When should you raise vs return None?
#    → Raise when the absence is unexpected and callers must handle it.
#      Return None/empty when "not found" is a normal outcome callers can
#      optionally check.
