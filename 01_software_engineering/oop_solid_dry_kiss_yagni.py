"""
TOPIC: OOP Principles + SOLID + DRY / KISS / YAGNI
PURPOSE: Understand the guiding principles behind well-designed object-oriented
         code — what they mean, why they exist, and what violating them looks like.
LEVEL: required for Junior | interview weight: HIGH

These are not rules to memorise — they are diagnostic tools.
When code becomes hard to change, test, or understand, one of these principles
is usually being violated. Knowing them lets you name the problem and fix it.

Sections:
  1. OOP pillars — Encapsulation, Abstraction, Inheritance, Polymorphism
  2. SOLID       — five principles for class design
  3. DRY / KISS / YAGNI — three practical rules for everyday code
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

# ══════════════════════════════════════════════════════════════════════════════
# 1. THE FOUR OOP PILLARS
# ══════════════════════════════════════════════════════════════════════════════

# ── Encapsulation ─────────────────────────────────────────────────────────────
# Bundle data and the methods that operate on it into one unit.
# Hide internal state — only expose what callers need.
# Protects invariants: the object controls what changes are valid.


class BankAccount:
    def __init__(self, owner: str, initial_balance: float):
        self.owner = owner
        self._balance = initial_balance   # _ prefix: internal, don't touch directly

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount: float):
        if amount <= 0:
            raise AttributeError("Deposit must be positive")
        self._balance += amount

    def withdraw(self, amount):
        if amount <= 0:
            raise AttributeError("Withdrawal must be positive")
        if amount > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount

# Without encapsulation:
#   account._balance = -9999   ← breaks the invariant, nothing stops it
# With encapsulation, the only way to change balance is through deposit/withdraw,
# which enforce the rules every time.


# ── Abstraction ───────────────────────────────────────────────────────────────
# Expose WHAT something does, hide HOW it does it.
# Callers work with the interface; they don't need to know the implementation.

class PaymentProcessor(ABC):
    def charge(self, amount: float, currency: str) -> str:
        """Returns a transaction ID"""
        pass


class StripeProcessor(PaymentProcessor):
    def charge(self, amount: float, currency: str) -> str:
        # Stripe SDK calls hidden in here — caller never sees them
        print(f"[Stripe] Charging {amount} {currency}")
        return"txn_stripe_001"

# Caller only knows about .charge() — not about Stripe's internals.
# Swapping to PayPal = new class, zero changes to the caller.


# ── Inheritance ───────────────────────────────────────────────────────────────
# A subclass inherits attributes and methods from a parent class.
# Use for genuine IS-A relationships, not for code reuse alone.

class Vehicle:
    def __init__(self, make: str, speed_kmh: float):
        self.make = make
        self.speed_kmh = speed_kmh

    def describe(self) -> str:
        return f"{self.make} travelling at {self.speed_kmh} km/h"


class ElectricCar(Vehicle):
    def __init__(self, make: str, speed_kmh: float, battery_kwh: float):
        super().__init__(make, speed_kmh)
        self.battery_kwh = battery_kwh

    def describe(self) -> str:
        return super().describe() + f"(battery: {self.battery_kwh} kWh)"

# ElectricCar IS-A Vehicle — inheritance is appropriate here.
# Avoid: inheriting just to reuse a utility method when there's no IS-A relationship.
# "Favour composition over inheritance" — if in doubt, use composition instead.


# ── Polymorphism ──────────────────────────────────────────────────────────────
# Different objects respond to the same interface in their own way.
# The caller doesn't need to know which concrete type it has.

class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass


class Circle(Shape):
    def __init__(self, radius: float): self.radius = radius
    def area(self) -> float: return 3.14159 * self.radius ** 2


class Rectangle(Shape):
    def __init__(self, w: float, h: float): self.w, self.h = w, h
    def area(self) -> float: return self.w * self.h


def total_area(shapes: list[Shape]) -> float:
    return sum(s.area() for s in shapes)   # does not care which shape it is


shapes = [Circle(5), Rectangle(4, 6), Circle(3)]
print(total_area(shapes))   # works for any shape

# ══════════════════════════════════════════════════════════════════════════════
# 2. SOLID PRINCIPLES
# ══════════════════════════════════════════════════════════════════════════════

# ── S — Single Responsibility Principle (SRP) ─────────────────────────────────
# A class should have ONE reason to change.
# "One reason to change" means one part of the system owns it.


# ❌ Violation — this class does three different jobs:
class UserManagerBad:
    def create_user(self, email: str) -> dict: ...
    def send_welcome_email(self, user: dict): ...   # email concern mixed in
    def save_to_csv(self, users: list): ...   # persistence concern mixed in
    # If email format changes, this class changes.
    # If CSV format changes, this class changes.
    # If user creation rules change, this class changes. → 3 reasons to change.


# ✅ Fixed — each class has one reason to change:
class UserService:
    def create(self, email: str) -> dict:
        return {"id": 1, "email": email}


class EmailService:
    def send_welcome(self, user: dict):
        print(f"Welcome {user['email']}")


class UserCsvExporter:
    def export(self, users: list, path: str):
        print(f"Writing {len(users)} users to {path}")

# Industry signal: if you describe a class with "and" ("it creates users AND
# sends emails AND exports CSV"), it probably violates SRP.


# ── O — Open/Closed Principle (OCP) ──────────────────────────────────────────
# Open for extension, closed for modification.
# Add new behaviour by adding new code — not by changing existing code.

# ❌ Violation — adding a new discount type requires editing this function:
def candidate_discount_bad(order_type: str, price: float) -> float:
    if order_type == "regular":
        return price * 0.05
    elif order_type == "premium":
        return price * 0.15
    # Adding "enterprise" = edit this function = risk breaking existing types.

# ✅ Fixed — new discount type = new class, no changes to existing code:
class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, price: float) -> float:
        pass


class RegularDiscount(DiscountStrategy):
    def apply(self, price: float) -> float: return price * 0.05


class PremiumDiscount(DiscountStrategy):
    def apply(self, price: float) -> float: return price * 0.15


class EnterpriseDiscount(DiscountStrategy):   # added without touching anything else
    def apply(self, price: float) -> float: return price * 0.30

# Notice: OCP and Strategy pattern are the same idea from different angles.
# OCP is the principle; Strategy is the pattern that implements it.


# ── L — Liskov Substitution Principle (LSP) ──────────────────────────────────
# Subclasses must be substitutable for their base class without breaking the program.
# If you have code that works with Base, it must work with any Subclass.

# ❌ Violation — the classic Rectangle/Square problem:

class RectangleBad:
    def __init__(self): self.height = 0; self.width = 0
    def set_width(self, w): self.width = w
    def set_height(self, h): self.height = h
    def area(self): return self.width * self.height


class SquareBad(RectangleBad):
    def set_width(self, w):
        self.width = w; self.height = w

    def set_height(self, h):
        self.height = h; self.width = h


def test_rectangle(r: RectangleBad):
    r.set_width(4)
    r.set_height(5)
    assert r.area() == 20   # passes for Rectangle, FAILS for Square (area = 25)
    # Square broke the contract RectangleBad promised.

# ✅ Fix: Square is NOT a Rectangle behaviourally — don't inherit.
# Use separate classes or a common abstract Shape base instead.

# LSP in practice: if a subclass throws exceptions the base class doesn't,
# narrows accepted input, or removes functionality, it violates LSP.


# ── I — Interface Segregation Principle (ISP) ────────────────────────────────
# No class should be forced to implement methods it doesn't use.
# Prefer many small, specific interfaces over one large general one.

# ❌ Violation — a fat interface forces irrelevant implementations:

class WorkerBad(ABC):
    @abstractmethod
    def work(self): pass

    @abstractmethod
    def eat(self): pass     # robots don't eat

    @abstractmethod
    def sleep(self): pass   # robots don't sleep


class RobotBad(WorkerBad):
    def work(self): print("Robot is working")

    def eat(self): raise NotImplementedError   # forced to implement irrelevant method

    def sleep(self): raise NotImplementedError


# ✅ Fixed — split into focused interfaces:
class Workable(ABC):
    @abstractmethod
    def work(self): pass


class Feedable(ABC):
    @abstractmethod
    def eat(self): pass


class Restable(ABC):
    @abstractmethod
    def sleep(self): pass


class Human(Workable, Feedable, Restable):
    def work(self): print("Human is working")
    def eat(self): print("Human is eating")
    def sleep(self): print("Human is sleeping")


class Robot(Workable):
    def work(self): print("Robot is working")

# Robot only implements what it needs. No dead NotImplementedError stubs.

# Python note: Python uses duck typing, so formal interfaces via ABC are optional.
# But typing.Protocol lets you define structural interfaces without inheritance:
from typing import Protocol

class Chargeable(Protocol):
    def charge(self, amount: float, currency: str) -> str: ...
# Any class with a matching .charge() method satisfies this — no inheritance needed.


# ── D — Dependency Inversion Principle (DIP) ─────────────────────────────────
# High-level modules should not depend on low-level modules.
# Both should depend on abstractions.
# Abstractions should not depend on details — details depend on abstractions.

# ❌ Violation — high-level class directly imports and creates the low-level one:

class MySQLDatabaseBad:
    def save(self, data: dict): print(f"[MySQL] Saving {data}")


class UserServiceBad:
    def __init__(self, db: MySQLDatabaseBad):
        self._db = MySQLDatabaseBad()

    def create_user(self, email):
        return self._db.save({"email": email})


# ✅ Fixed — both depend on the abstraction (the interface):
class Database(ABC):
    @abstractmethod
    def save(self, data: dict): pass


class MySQLDatabase(Database):
    def save(self, data: dict): print(f"[MySQL] Saving {data}")


class InMemoryDatabase(Database):
    def __init__(self): self.records: list = []
    def save(self, data: dict): self.records.append(data)


class UserServiceGood:
    def __init__(self, db: Database):
        self._db = MySQLDatabase()

    def create_user(self, email):
        self._db.save({"email": email})


# In Production
svc = UserServiceGood(MySQLDatabase())
# In tests

fake_db = InMemoryDatabase()
svc = UserServiceGood(fake_db)
svc.create_user("test@example.com")
assert fake_db.records == [{"email": "test@example.com"}]

# DIP is the foundation of dependency injection — which is how FastAPI's
# Depends() system works, how Django's authentication backends work,
# and how virtually every testable service layer is structured.

# ══════════════════════════════════════════════════════════════════════════════
# 3. DRY / KISS / YAGNI
# ══════════════════════════════════════════════════════════════════════════════

# ── DRY — Don't Repeat Yourself ───────────────────────────────────────────────
# Every piece of knowledge should have a single, authoritative representation.
# Not just about copy-pasted code — also about duplicated logic and data.


# ❌ Violation — the 10% VAT rate is duplicated in three places:
def invoice_total_bad(price: float) -> float:
    return price + price * 0.10


def receipt_total_bad(price: float) -> float:
    return price + price * 0.10


def quote_total_bad(price: float) -> float:
    return price + price * 0.10

# When VAT changes to 12%, you must find and change three places.
# Miss one → silent bug.


# ✅ Fixed — the rate is defined once:
VAT_RATE = 0.10


def apply_vat(price: float) -> float:
    return price * (VAT_RATE + 1)


def incoive_total(price: float) -> float: return apply_vat(price)
def receipt_total(price: float) -> float: return apply_vat(price)
def quote_total(price: float) -> float: return apply_vat(price)

# DRY is not "never write similar-looking code". It is "never duplicate knowledge".
# Two functions that look similar but represent different business concepts
# are NOT a DRY violation — merging them would be wrong.


# ── KISS — Keep It Simple, Stupid ─────────────────────────────────────────────
# Prefer the simplest solution that works. Complexity is a cost — pay it only
# when the problem genuinely demands it.

# ❌ Over-engineered for no reason

class UserNameFormatterFactory:
    @staticmethod
    def get_formatter(self, strategy: str):
        strategies = {"upper": str.upper, "lower": str.lower}
        return strategies.get(strategy, str)


formatter = UserNameFormatterFactory.get_formatter(strategy="upper")
result = formatter("alice")


# ✅ The problem is a one-liner:
result = "alice".upper()

# KISS violations to watch for:
# - Abstractions with only one implementation (not yet)
# - Classes that exist just to hold one static method
# - Metaprogramming where a plain function would do
# - "I'll need this flexibility later" (see YAGNI)

# KISS does not mean "write bad code". It means don't add complexity
# that isn't justified by a current, real requirement.


# ── YAGNI — You Aren't Gonna Need It ─────────────────────────────────────────
# Don't build features or abstractions until you actually need them.
# Speculative code has a maintenance cost even when it's never used.

# ❌ Violation — adding plugin system, event hooks, and config loading
#    because "we might need it someday":

class UserServiceOverEngineered:
    def __init__(self, plugins=None, event_hooks=None, config_loading=None):
        self._plugins = plugins or []
        self._hooks = event_hooks or {}
        self._config = config_loading or {}

    def create_user(self, email: str):
        for plugin in self._plugins:   # nobody uses plugins yet
            plugin.before_create(email)
        # ... actual logic ...
        for hook in self._hooks.get("after_create", []):   # nobody uses hooks yet
            hook(email)


# ✅ Just write what you need today:
class UserServiceSimple:
    def create_user(self, email: str) -> dict:
        return {"id": 1, "email": email}

# YAGNI and OCP can seem to contradict each other:
# OCP says "design for extension". YAGNI says "don't add it until needed".
# Resolution: design for the extensions you KNOW are coming (OCP). Don't
# design for extensions you're just imagining (YAGNI).


# ── PRINCIPLES QUICK REFERENCE ───────────────────────────────────────────────
# ┌───────────────┬────────────────────────────────────────────────────────────┐
# │ Principle     │ One-line rule                                              │
# ├───────────────┼────────────────────────────────────────────────────────────┤
# │ Encapsulation │ Hide internal state; expose only a controlled interface    │
# │ Abstraction   │ Show what; hide how                                        │
# │ Inheritance   │ IS-A relationships only; prefer composition otherwise      │
# │ Polymorphism  │ Same interface, different behaviour per type               │
# ├───────────────┼────────────────────────────────────────────────────────────┤
# │ SRP           │ One class = one reason to change                          │
# │ OCP           │ Extend by adding; don't edit existing code                │
# │ LSP           │ Subclass must honour the base class contract               │
# │ ISP           │ Small focused interfaces > one fat interface               │
# │ DIP           │ Depend on abstractions, not concrete implementations       │
# ├───────────────┼────────────────────────────────────────────────────────────┤
# │ DRY           │ Every piece of knowledge has one authoritative source      │
# │ KISS          │ The simplest working solution wins                         │
# │ YAGNI         │ Don't build it until you actually need it                  │
# └───────────────┴────────────────────────────────────────────────────────────┘


# ── INTERVIEW QUESTIONS THIS FILE COVERS ────────────────────────────────────
# Q: What are the four pillars of OOP?
#    → Encapsulation (hide state), Abstraction (hide implementation),
#      Inheritance (IS-A hierarchy), Polymorphism (same interface, varied behaviour).
#
# Q: What does the Single Responsibility Principle mean in practice?
#    → A class should have one reason to change — owned by one part of the system.
#      Signal: if you describe the class with "and", it probably has too many jobs.
#
# Q: What is the Liskov Substitution Principle? Give a violation example.
#    → A subclass must be usable anywhere the base class is expected.
#      Classic violation: Square inheriting Rectangle — set_width breaks the
#      area contract because Square silently changes height too.
#
# Q: What is the Dependency Inversion Principle and why does it matter for testing?
#    → High-level code should depend on abstractions, not concrete classes.
#      Inject the dependency — then tests can inject a fake implementation
#      instead of a real DB or HTTP client.
#
# Q: What is the difference between DRY and KISS?
#    → DRY: don't duplicate knowledge — a fact should have one source of truth.
#      KISS: don't overcomplicate — use the simplest design that meets requirements.
#      They often apply together but target different problems.






