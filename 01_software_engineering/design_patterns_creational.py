"""
TOPIC: Creational Design Patterns
PURPOSE: Understand patterns that control HOW objects are created — decoupling
         creation logic from the code that uses the objects.
LEVEL: required for Junior | interview weight: HIGH

Creational patterns answer: "who is responsible for creating this object,
and how do we keep that logic flexible and not scattered everywhere?"

Patterns covered:
  1. Singleton    — exactly one instance ever
  2. Factory      — delegate creation to a method (simple + method variants)
  3. Abstract Factory — families of related objects
  4. Builder      — step-by-step construction of complex objects
  5. Prototype    — create new objects by cloning existing ones
"""

from __future__ import annotations
import copy
import threading
from abc import ABC, abstractmethod
from typing import Any

# ══════════════════════════════════════════════════════════════════════════════
# 1. SINGLETON — one instance, globally accessible
# ══════════════════════════════════════════════════════════════════════════════
# Use when: exactly one object must coordinate something system-wide.
# Real examples: database connection pool, config loader, logger, cache client.
#
# WARNING: Singletons are often considered an anti-pattern in modern code
# because they introduce hidden global state and make testing hard.
# In Python, a module-level variable achieves the same effect more cleanly.
# Know the pattern for interviews; in real code prefer dependency injection.


class SingletonMeta(type):
    """
    Thread-safe Singleton via metaclass.
    The metaclass controls __call__, so every ClassName() returns the same instance.
    """
    _instances: dict = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class AppConfig(metaclass=SingletonMeta):
    """Application configuration — should exist exactly once."""

    def __init__(self):
        self.Debug = False
        self.db_url = "postgresql://localhost/prod"


cfg1 = AppConfig()
cfg2 = AppConfig()
assert cfg1 is cfg2  # True; same object

# The Pythonic alternative (no class needed):
# config.py
#   DEBUG = False
#   DB_URL = "postgresql://localhost/prod"
# Any module that does `import config` gets the same object.
# Python's module system is already a singleton.


# ══════════════════════════════════════════════════════════════════════════════
# 2. FACTORY METHOD — let subclasses decide which class to instantiate
# ══════════════════════════════════════════════════════════════════════════════
# Use when: you want to create objects without specifying the exact class,
# or when creation logic is too complex to repeat everywhere.
#
# There are two levels commonly called "factory":
#   A) Simple Factory — a plain function or static method that picks the class
#   B) Factory Method — a method defined in a base class, overridden by subclasses

# ── A) Simple Factory (most common in real Python code) ──────────────────────


class Notification(ABC):
    @abstractmethod
    def send(self, message: str):
        pass


class EmailNotification(Notification):
    def __init__(self, address: str):
        self.address = address

    def send(self, message: str) -> None:
        print(f"Email → {self.address}: {message}")


class SMSNotification(Notification):
    def __init__(self, phone):
        self.phone = phone

    def send(self, message) -> None:
        print(f"SMS → {self.phone}: {message}")


class PushNotification(Notification):
    def __init__(self, device_id):
        self.device_id = device_id

    def send(self, message: str) -> None:
        print(f"Push → {self.device_id}: {message}")


def create_notification(channel: str, target: str) -> Notification:
    """
    Simple factory function — centralises the if/elif so no caller
    needs to know which class to instantiate.
    """
    factories = {
        "email": EmailNotification,
        "sms": SMSNotification,
        "push": PushNotification
    }
    if channel not in factories:
        raise ValueError(f"Unknown notification channel: {channel}")

    return factories[channel](target)


n = create_notification("email", "alice@gmail.com")
n.send("Your order has shipped.")

# Industry: Django's authentication backends, serializer fields, payment gateways.
# A dict mapping keys to classes (as above) is cleaner than a long if/elif chain.

# ── B) Factory Method Pattern (OOP version) ──────────────────────────────────


class Exporter(ABC):
    """
    Base class defines the interface; subclasses decide the concrete format.
    The factory method is `build_formatter`.
    """

    @abstractmethod
    def build_formatter(self) -> "Formatter":
        """Factory method — subclasses override this."""
        pass

    def export(self, data: list[dict]) -> str:
        formatter = self.build_formatter()   # calls the factory method
        return formatter.format(data)


class Formatter(ABC):
    @abstractmethod
    def format(self, data: list[dict]):
        pass


class JSONFormatter(Formatter):
    def format(self, data):
        import json
        return json.dumps(data, indent=2)


class CSVFormatter(Formatter):
    def format(self, data):
        if not data:
            return ""
        headers = ",".join(data[0].keys())
        rows = [",".join(str(v) for v in row.values()) for row in data]
        return "\n".join([headers] + rows)


class JSONExporter(Exporter):
    def build_formatter(self):
        return JSONFormatter()


class CSVExporter(Exporter):
    def build_formatter(self):
        return CSVFormatter()


data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
print(JSONExporter().export(data))
print(CSVExporter().export(data))

# The caller (export()) never imports JSONFormatter or CSVFormatter directly.
# Adding XMLExporter later requires zero changes to existing code.


# ══════════════════════════════════════════════════════════════════════════════
# 3. ABSTRACT FACTORY — families of related objects
# ══════════════════════════════════════════════════════════════════════════════
# Use when: you need to create multiple related objects that must be used together,
# and you want to swap the entire family at once.
# Real example: UI theming (dark/light), database drivers (PostgreSQL/SQLite),
# cloud provider SDKs (AWS/GCP).


class Button(ABC):
    @abstractmethod
    def render(self) -> str:
        pass


class CheckBox(ABC):
    @abstractmethod
    def render(self) -> str:
        pass


# Concrete family A — Dark theme
class DarkButton(Button):
    def render(self): return "<button class='dark'>Click</button>"


class DarkCheckBox(CheckBox):
    def render(self): return "<input type='checkbox' class='dark'>"


# Concrete family B — Light theme
class LightButton(Button):
    def render(self): return "<button class='light'>Click</button>"


class LightCheckBox(CheckBox):
    def render(self): return "<input type='checkbox' class='light'>"


class UIFactory(ABC):
    """Abstract factory — defines what a UI family must provide."""
    @abstractmethod
    def create_button(self):
        pass

    @abstractmethod
    def create_checkbox(self):
        pass


class DarkThemeFactory(UIFactory):
    def create_button(self): return DarkButton()
    def create_checkbox(self): return DarkCheckBox()


class LightThemeFactory(UIFactory):
    def create_button(self): return LightButton()
    def create_checkbox(self): return LightCheckBox()


def render_ui(factory: UIFactory):
    """This function never imports any concrete class — only uses the factory."""
    btn = factory.create_button()
    chk = factory.create_checkbox()
    print(btn.render(), chk.render())


render_ui(DarkThemeFactory())
render_ui(LightThemeFactory())
# Swap the whole theme by changing one argument.

# Abstract Factory vs Factory Method:
#   Factory Method: one product, subclass picks the type.
#   Abstract Factory: a FAMILY of products, entire factory is swappable.


# ══════════════════════════════════════════════════════════════════════════════
# 4. BUILDER — step-by-step construction of complex objects
# ══════════════════════════════════════════════════════════════════════════════
# Use when: an object has many optional parameters and multiple valid
# configurations. Avoids telescoping constructors (__init__ with 12 arguments).
# Real examples: query builders (SQLAlchemy), HTTP request builders, report generators.


class QueryBuilder:
    """
    Fluent interface builder for SQL queries.
    Each method returns `self` so calls can be chained.
    """
    def __init__(self, table: str):
        self._table = table
        self._fields: list[str] = ["*"]
        self._wheres: list[str] = []
        self._order: str | None = None
        self._limit: int | None = None

    def select(self, *fields: str) -> QueryBuilder:
        self._fields = list(fields)
        return self

    def where(self, condition: str) -> QueryBuilder:
        self._wheres.append(condition)
        return self

    def order_by(self, field: str) -> QueryBuilder:
        self._order = field
        return self

    def limit(self, n: int) -> QueryBuilder:
        self._limit = n
        return self

    def build(self) -> str:
        query = f"SELECT {', '.join(self._fields)} FROM {self._table}"
        if self._wheres:
            query += " WHERE " + " AND ".join(self._wheres)
        if self._order:
            query += f" ORDER BY {self._order}"
        if self._limit:
            query += f" LIMIT {self._limit}"

        return query


query = (
    QueryBuilder("users")
    .select("id", "name", "email")
    .where("active = TRUE")
    .where("age > 18")
    .order_by("name")
    .limit(100)
    .build()
)
print(query)
# SELECT id, name, email FROM users WHERE active = TRUE AND age > 18
# ORDER BY name LIMIT 100

# Industry: SQLAlchemy's select() is a builder. Django ORM's QuerySet is a builder.
# FastAPI's TestClient uses a builder-style API for requests.
# Pydantic model creation with .model_copy(update={...}) is builder-like.

# ── Dataclass with builder for configuration objects ─────────────────────────
from dataclasses import dataclass, field


@dataclass
class ServerConfig:
    host: str = "localhost"
    port: int = 8000
    debug: bool = False
    workers: int = 4
    allowed_hosts: list[str] = field(default_factory=list)

    def with_port(self, port: int) -> ServerConfig:
        return ServerConfig(**{**self.__dict__, "port": port})

    def with_host(self, host: str) -> ServerConfig:
        return ServerConfig(**{**self.__dict__, "host": host})


config = (
    ServerConfig()
    .with_host("0.0.0.0")
    .with_port(443)
)

# Immutable builder pattern — each method returns a NEW config object.
# Useful when configs are shared and must not be mutated.


# ══════════════════════════════════════════════════════════════════════════════
# 5. PROTOTYPE — clone existing objects instead of building from scratch
# ══════════════════════════════════════════════════════════════════════════════
# Use when: object creation is expensive (loads from DB, heavy computation)
# and you need many slightly different versions.
# Real examples: default configs, document templates, game entity spawning.

class DocumentTemplate:
    def __init__(self, title: str, sections: list[str], metadata: dict):
        self.title = title
        self.sections = sections   # mutable — needs deep copy
        self.metadata = metadata   # mutable — needs deep copy

    def clone(self) -> DocumentTemplate:
        """Returns a deep copy — changes to the clone don't affect the original."""
        return copy.deepcopy(self)

    def __repr__(self):
        return f"DocumentTemplate(title={self.title!r}, sections={self.sections})"


invoice_template = DocumentTemplate(
    title="Invoice",
    sections=["Header", "Line Items", "Total", "Payment Terms"],
    metadata={"version": 1, "author": "finance-team"}
)

# Clone and customise — never touch the original template:
june_invoice = invoice_template.clone()
june_invoice.title = "Invoice - June 2026"
june_invoice.sections.append("Late Fee Notice")

print(invoice_template)   # unchanged
print(june_invoice)   # has the extra section

# copy.copy()     → shallow copy (nested objects still shared)
# copy.deepcopy() → deep copy   (full independence — what you almost always want)

# Industry: Celery task configs, Pydantic model defaults, test fixtures that
# need a "base object with one field changed" for each test case.


# ── PATTERN COMPARISON ───────────────────────────────────────────────────────
# ┌──────────────────┬─────────────────────────────────────────────────────┐
# │ Pattern          │ Core question it answers                            │
# ├──────────────────┼─────────────────────────────────────────────────────┤
# │ Singleton        │ How do I ensure only ONE instance exists?           │
# │ Simple Factory   │ Who decides which class to instantiate?             │
# │ Factory Method   │ How do subclasses plug in their own creation logic? │
# │ Abstract Factory │ How do I swap a whole FAMILY of objects at once?    │
# │ Builder          │ How do I construct a complex object step by step?   │
# │ Prototype        │ How do I create a new object from an existing one?  │
# └──────────────────┴─────────────────────────────────────────────────────┘


# ── INTERVIEW QUESTIONS THIS FILE COVERS ────────────────────────────────────
# Q: What is the Singleton pattern and what is its downside?
#    → Ensures one instance. Downside: hidden global state, hard to test
#      (you can't inject a different instance). Prefer module-level variables
#      or dependency injection in real Python code.
#
# Q: What is the difference between Factory Method and Abstract Factory?
#    → Factory Method: one product, subclass decides the concrete type.
#      Abstract Factory: a family of related products, entire factory is swappable.
#
# Q: When would you use Builder over a constructor with many arguments?
#    → When an object has many optional parameters or multiple valid
#      configurations. Builder makes the construction readable and
#      prevents invalid intermediate states.
#
# Q: What is the difference between copy.copy() and copy.deepcopy()?
#    → Shallow copy duplicates the outer object but shares nested objects.
#      Deep copy duplicates everything recursively — full independence.
#      Prototype almost always needs deepcopy.
#
# Q: Where do you see these patterns in Python frameworks?
#    → Singleton: module-level objects, connection pools.
#      Factory: Django serializer fields, authentication backends.
#      Builder: SQLAlchemy select(), Django ORM QuerySet, Pydantic models.
#      Prototype: test fixtures, document templates, Celery task configs.
