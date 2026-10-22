"""
TOPIC: Dunder (Magic / Special) Methods
PURPOSE: Understand what dunder methods are, which ones matter, and how Python
         calls them implicitly — so your classes integrate naturally with the language.
LEVEL: required for Junior | interview weight: HIGH

"Dunder" = Double UNDERscore on both sides: __init__, __repr__, etc.
Python calls these automatically in response to operators and built-in functions.
You define them; Python decides when to call them.

x + y        →  x.__add__(y)
len(x)       →  x.__len__()
str(x)       →  x.__str__()
x == y       →  x.__eq__(y)
with x:      →  x.__enter__() / x.__exit__(...)
for i in x:  →  x.__iter__() / x.__next__()
"""

from __future__ import annotations
from typing import Iterator

# ══════════════════════════════════════════════════════════════════════════════
# WORKING EXAMPLE: A Money class — used across all sections below
# ══════════════════════════════════════════════════════════════════════════════


class Money:
    """
    Represents an amount in a specific currency.
    Demonstrates the most important dunder methods in one coherent class.
    """
    def __init__(self, amount: float, currency: str = "USD"):
        # ── __init__ ─────────────────────────────────────────────────────────
        # Called after the object is created (by __new__).
        # Initialises the instance. NOT a constructor — the object already exists.
        self.amount = round(amount, 2)
        self.currency = currency.upper()

    # ── __repr__ vs __str__ ──────────────────────────────────────────────────
    # __repr__: unambiguous, for DEVELOPERS. Should ideally be eval()-able.
    #           Called by repr(obj), in the REPL, and inside containers (lists, dicts).
    # __str__:  human-readable, for END USERS.
    #           Called by str(obj) and print(obj).
    # Rule: always define __repr__. Define __str__ only if you need a different
    # user-facing format. If __str__ is missing, Python falls back to __repr__.

    def __repr__(self):
        return f"Money(amount={self.amount}, currency='{self.currency}'"

    def __str__(self):
        return f"{self.currency} {self.amount:.2f}"

    # ── __eq__ and __hash__ ──────────────────────────────────────────────────
    # __eq__: called by ==. By default compares object identity (same as `is`).
    # __hash__: called by hash(obj) and needed for dict keys and set membership.
    #
    # CRITICAL RULE: if you define __eq__, Python sets __hash__ = None by default,
    # making the object unhashable (can't be put in a set or used as a dict key).
    # If you want hashability, you MUST define __hash__ too.

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented   # let Python try the other side
        return self.amount == other.amount and self.currency == other.currency

    def __hash__(self) -> int:
        # Must be consistent with __eq__: objects that compare equal must hash equal
        return hash((self.amount, self.currency))

    # ── ARITHMETIC OPERATORS ─────────────────────────────────────────────────
    # __add__:  a + b   (also __sub__, __mul__, __truediv__, __floordiv__, __mod__)
    # __radd__: b + a when a doesn't know how to handle b (reflected add)

    def __add__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __radd__(self, other):
        # Enables sum ([Money(1), Money(2)) which starts with 0 + Money(1)
        if other == 0:
            return self
        return self.__add__(other)

    def __mul__(self, factor: float) -> Money:
        return Money(self.amount + factor, self.currency)

    def __rmul__(self, factor: float) -> Money:
        return self.__mul__(factor)   # so both `2 * money` and `money * 2` work

    # ── COMPARISON OPERATORS ─────────────────────────────────────────────────
    # __lt__, __le__, __gt__, __ge__ enable <, <=, >, >=
    # Tip: define __lt__ and use @functools.total_ordering to get the rest for free.

    def __lt__(self, other) -> bool:
        if not isinstance(other, Money) or self.currency != other.currency:
            return NotImplemented
        return self.amount < other.amount

    # ── __bool__ ─────────────────────────────────────────────────────────────
    # Called by bool(obj) and by `if obj:` / `while obj:`.
    # If not defined, Python falls back to __len__ (0 = False).

    def __bool__(self):
        return self.amount != 0

    # ── __abs__ ─────────────────────────────────────────────────────────────

    def __abs__(self):
        return Money(abs(self.amount), self.currency)


# Quick demo — none of this required explicit method calls:
a = Money(10.50)
b = Money(4.50)
print(a)  # USD 10.50         ← __str__
print(repr(a))  # Money(...)        ← __repr__
print(a + b)  # USD 15.00         ← __add__
print(a == b)  # False             ← __eq__
print(a > b)  # True              ← __lt__ (Python inverts it)
print(bool(Money(0)))  # False          ← __bool__
print(sum([a, b]))  # USD 15.00         ← __radd__

# ══════════════════════════════════════════════════════════════════════════════
# OBJECT LIFECYCLE: __new__ vs __init__
# ══════════════════════════════════════════════════════════════════════════════


class Singleton:
    """
    Classic Singleton using __new__ — ensures only one instance ever exists.
    (In production you'd use a module-level variable or dependency injection,
    but this illustrates __new__ clearly.)
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        # __new__ is the TRUE constructor — it creates and returns the object.
        # __init__ receives the already-created object and populates it.
        # Control object creation here (caching, pooling, immutability).
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, value: int):
        self.value = value


s1 = Singleton(1)
s2 = Singleton(2)
print(s1 == s2)
print(s1 is s2)   # True — same object
print(s1.value)   # 2    — __init__ ran again on the existing object

# __new__ is rarely overridden. You need it for:
# - Singletons
# - Immutable subclasses (subclassing int, str, tuple)
# - Metaclass magic


# ══════════════════════════════════════════════════════════════════════════════
# CONTAINER PROTOCOL: __len__, __getitem__, __contains__, __iter__
# ══════════════════════════════════════════════════════════════════════════════

class Wordlist:
    """A list of words that supports natural Python container operations."""
    def __init__(self, words: list[str]):
        self._words = words

    def __len__(self):
        return len(self._words)   # enables: len(wl)

    def __getitem__(self, index):
        return self._words[index]   # enables: wl[0], wl[1:3], wl[-1]
                                    # also makes the object iterable as fallback

    def __contains__(self, item: str) -> bool:
        return item.lower() in (w.lower() for w in self._words)   # enables: "hello" in wl

    def __iter__(self) -> Iterator[str]:
        return iter(self._words)     # enables: for word in wl:


wl = Wordlist(["Python", "is", "great"])
print(len(wl))          # 3
print(wl[1])            # is
print("python" in wl)   # True   (case-insensitive __contains__)
print(list(wl))         # ["Python", "is", "great"]

# ══════════════════════════════════════════════════════════════════════════════
# CALLABLE OBJECTS: __call__
# ══════════════════════════════════════════════════════════════════════════════


class Multiplier:
    """
    An object that behaves like a function.
    Industry use: stateful callables, function factories, ML model wrappers.
    """
    def __init__(self, factor: float) -> None:
        self.factor = factor

    def __call__(self, value: float) -> float:
        return self.factor * value


double = Multiplier(2)
triple = Multiplier(3)
print(double(5))   # 10  ← looks like a function call
print(triple(5))   # 15

# callable(double)  → True
# Industry: sklearn's transformers, FastAPI dependency callables,
# class-based decorators (see decorators.py § 6).


# ══════════════════════════════════════════════════════════════════════════════
# ATTRIBUTE ACCESS: __getattr__, __setattr__, __getattribute__
# ══════════════════════════════════════════════════════════════════════════════

class LazyConfig:
    """
    __getattr__ is called only when normal attribute lookup FAILS.
    Use it to provide defaults or load attributes lazily.
    """
    def __init__(self, data: dict):
        # Use object.__setattr__ here to avoid recursion with our own __setattr__
        object.__setattr__(self, "_data", data)

    def __getattr__(self, name: str):
        # Only called when `name` is NOT found through normal means
        try:
            return self._data[name]
        except KeyError:
            return AttributeError(f"Config has no key '{name}'")

    def __setattr__(self, name: str, value):
        # Called for EVERY attribute assignment, including in __init__
        # Without the object.__setattr__ guard above, this would recurse infinitely.
        self._data[name] = value


cfg = LazyConfig({"debug": True, "port": 8000})
print(cfg.debug)   # True  ← from _data via __getattr__
cfg.host = "localhost"
print(cfg.host)   # localhost


# __getattr__ vs __getattribute__:
# __getattr__      → called only when normal lookup fails (safe to override)
# __getattribute__ → called for EVERY attribute access (dangerous; easy to infinite loop)
# Almost always use __getattr__. Only override __getattribute__ for proxies/wrappers.


# ══════════════════════════════════════════════════════════════════════════════
# QUICK REFERENCE — FULL DUNDER MAP
# ══════════════════════════════════════════════════════════════════════════════
#
# LIFECYCLE
#   __new__(cls)              object creation (before __init__)
#   __init__(self)            initialisation
#   __del__(self)             called when object is garbage collected (avoid relying on this)
#
# REPRESENTATION
#   __repr__(self)            repr(obj)  — for developers
#   __str__(self)             str(obj), print(obj)  — for users
#   __format__(self, spec)    format(obj, spec), f"{obj:spec}"
#
# COMPARISON & HASHING
#   __eq__(self, other)       ==
#   __ne__(self, other)       != (defaults to not __eq__)
#   __lt__, __le__            <, <=
#   __gt__, __ge__            >, >=
#   __hash__(self)            hash(obj), dict keys, set membership
#
# ARITHMETIC
#   __add__, __radd__         +  (r-variant: reflected, e.g. 0 + obj)
#   __sub__, __rsub__         -
#   __mul__, __rmul__         *
#   __truediv__, __floordiv__ /, //
#   __mod__                   %
#   __pow__                   **
#   __neg__, __pos__, __abs__ unary -, +, abs()
#
# CONTAINER PROTOCOL
#   __len__(self)             len(obj)
#   __getitem__(self, key)    obj[key]
#   __setitem__(self, key, v) obj[key] = v
#   __delitem__(self, key)    del obj[key]
#   __contains__(self, item)  item in obj
#   __iter__(self)            iter(obj), for loops
#   __next__(self)            next(obj)
#   __reversed__(self)        reversed(obj)
#
# ATTRIBUTE ACCESS
#   __getattr__(self, name)        fallback attribute lookup
#   __getattribute__(self, name)   ALL attribute access
#   __setattr__(self, name, val)   ALL attribute assignment
#   __delattr__(self, name)        del obj.attr
#
# CALLABLE
#   __call__(self, *args, **kw)    obj(...)
#
# CONTEXT MANAGER
#   __enter__(self)                with obj as x: (see context_managers.py)
#   __exit__(self, exc_t, exc_v, tb)
#
# BOOL / NUMERIC
#   __bool__(self)            bool(obj), if obj:
#   __int__, __float__        int(obj), float(obj)
#   __index__(self)           used for slicing, bin(), hex()


# ── INTERVIEW QUESTIONS THIS FILE COVERS ────────────────────────────────────
# Q: What is __repr__ vs __str__?
#    → __repr__ is for developers (unambiguous, REPL/logging). __str__ is for
#      end users (readable). If __str__ is missing, Python falls back to __repr__.
#      Always define __repr__; only define __str__ when the two should differ.
#
# Q: What is __init__ vs __new__?
#    → __new__ creates and RETURNS the object (true constructor).
#      __init__ receives the already-created object and sets it up.
#      Override __new__ for Singletons, immutable subclasses, or metaclasses.
#
# Q: Why define __hash__ when you define __eq__?
#    → Python sets __hash__ = None when you define __eq__, making the object
#      unhashable. If you want it usable as a dict key or in a set, define both.
#      Objects that compare equal must produce the same hash.
#
# Q: What is __call__?
#    → Makes an instance callable like a function: obj(). Used for stateful
#      callables, class-based decorators, and ML model wrappers.
#
# Q: __getattr__ vs __getattribute__?
#    → __getattr__ is the fallback, called only when normal lookup fails (safe).
#      __getattribute__ intercepts ALL attribute access (dangerous, infinite-loop risk).
