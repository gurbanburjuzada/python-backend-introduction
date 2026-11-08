"""
TOPIC: Structural Design Patterns
PURPOSE: Understand patterns that define HOW objects and classes are composed
         into larger structures — without changing their interfaces.
LEVEL: required for Junior | interview weight: HIGH

Structural patterns answer: "how do I connect these objects/classes together
cleanly, without making them tightly coupled to each other?"

Patterns covered:
  1. Adapter   — make incompatible interfaces work together
  2. Facade    — simplify a complex subsystem behind one clean interface
  3. Decorator — add behaviour by wrapping (structural version of the pattern)
  4. Proxy     — control access to an object
  5. Composite — treat individual objects and groups of them the same way
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable

# ══════════════════════════════════════════════════════════════════════════════
# 1. ADAPTER — translate one interface into another
# ══════════════════════════════════════════════════════════════════════════════
# Use when: you have existing code with an interface you can't change, but you
# need it to work with another interface.
# Real examples: third-party payment gateways, legacy API clients, different
# storage backends (S3/local disk), multiple SMS providers.


# Your app's expected interface:
class SMSProvider(ABC):
    @abstractmethod
    def send_sms(self, phone: str, message: str) -> bool:
        pass


# Third-party SDK you cannot modify — has a completely different interface:
class TwilioSDK:
    def messages_create(self, to: str, from_: str, body: str) -> dict:
        print(f"[Twilio] Sending '{body}' to {to} from {from_}")
        return {"sid": "SM123", "status": "queued"}


class SendBirdSDK:
    def dispatch(self, recipient: str, content: str, sender_id: str) -> int:
        print(f"[SenBird] Dispatching to {recipient}: {content}")
        return 200


# Adapters — wrap the third-party SDK to match YOUR interface:
class TwilioAdapter(SMSProvider):
    def __init__(self, sdk: TwilioSDK, from_number: str):
        self._sdk = sdk
        self._from = from_number

    def send_sms(self, phone: str, message: str) -> bool:
        result = self._sdk.messages_create(to=phone, from_=self._from, body=message)
        return result["status"] == "queued"


class SendBirdAdapter(SMSProvider):
    def __init__(self, sdk: SendBirdSDK, sender_id: str):
        self._sdk = sdk
        self._sender_id = sender_id

    def send_sms(self, phone: str, message: str) -> bool:
        status = self._sdk.dispatch(recipient=phone, content=message, sender_id=self._sender_id)
        return status == 200


def notify_user(provider: SMSProvider, phone: str, msg: str):
    """This function knows nothing about Twilio or Sendbird — only SMSProvider."""
    ok = provider.send_sms(phone, msg)
    print("Sent!" if ok else "Failed.")


# Swap providers by swapping the adapter — zero changes to notify_user:
notify_user(provider=TwilioAdapter(TwilioSDK(), "+15005550006"), phone="+994501234567", msg="Hello")
notify_user(provider=SendBirdAdapter(SendBirdSDK(), "app-001"), phone="+994501234567", msg="Hello")


# Industry: payment gateways (Stripe/PayPal behind one PaymentProvider interface),
# storage backends (S3/MinIO/local behind one FileStorage interface),
# LLM providers (OpenAI/Anthropic/Gemini behind one LLMClient interface).


# ══════════════════════════════════════════════════════════════════════════════
# 2. FACADE — one clean surface over a messy subsystem
# ══════════════════════════════════════════════════════════════════════════════
# Use when: a subsystem has many moving parts that callers shouldn't need to
# coordinate themselves.
# Real examples: a service class in Django/FastAPI that orchestrates DB + cache
# + email + events, an SDK that wraps multiple API calls.

class UserRepository:
    def create(self, email: str, hashed_pw: str) -> dict:
        print(f"[DB] Insert user email={email}")
        return {"id": 42, "email": email}

    def find_by_email(self, email: str) -> dict | None:
        print(f"[DB] Select user WHERE email={email}")
        return None   # simulating "not found"


class PasswordHasher:
    def hash(self, plain: str) -> str:
        return f"hashed:{plain}"   # bcrypt/argon2 in reality


class EmailService:
    def send_welcome(self, email: str):
        print(f"[Email] Sending email to {email}")


class CacheService:
    def set(self, key: str, value: dict, ttl: int = 300):
        print(f"[Cache] Set {key} (ttl={ttl}s)")


class AnalyticsService:
    def track(self, event: str, properties: dict):
        print(f"[Analytics] {event}: {properties}")


class UserRegistrationFacade:
    """
    The Facade. Caller calls register() — one method.
    All the orchestration is hidden in here.
    """
    def __init__(self):
        self._repo = UserRepository()
        self._hasher = PasswordHasher()
        self._email = EmailService()
        self._cache = CacheService()
        self._analytics = AnalyticsService()

    def register(self, email: str, password: str) -> dict:
        if self._repo.find_by_email(email):
            raise ValueError("Email already registered.")
        hashed = self._hasher.hash(password)
        user = self._repo.create(email, hashed)
        self._email.send_welcome(email)
        self._cache.set(f"user:{user['id']}", user)
        self._analytics.track("user_registered", {"email": email})
        return user


facade = UserRegistrationFacade()
facade.register("alice@gmail.com", "securepass")

# The route handler (FastAPI/Flask) just calls facade.register() — it has no idea
# about hashing, caching, or analytics. That's the whole point.
#
# Industry: Service classes in Django apps, use-case classes in Clean Architecture,
# the `requests` library itself (facade over urllib3 + connection pooling + cookies).


# ══════════════════════════════════════════════════════════════════════════════
# 3. DECORATOR (structural) — wrap an object to add behaviour
# ══════════════════════════════════════════════════════════════════════════════
# Use when: you want to add responsibilities to an object at runtime without
# subclassing. Key difference from Python's @decorator: this is an OOP pattern
# where the wrapper implements the SAME INTERFACE as what it wraps.
# Both can be stacked (layered) without knowing about each other.
#
# Real examples: logging wrappers, caching wrappers, compression middleware,
# Django middleware stack, WSGI/ASGI middleware.


class DataSource(ABC):
    @abstractmethod
    def write(self, data: str) -> None:
        pass

    @abstractmethod
    def read(self) -> str:
        pass


class FileDataSource(DataSource):
    """The concrete component being wrapped."""
    def __init__(self, filename: str):
        self.filename = filename
        self._content = ""

    def write(self, data) -> None:
        self._content = f"[File] writing to {self.filename}"
        self._content = data

    def read(self) -> str:
        return self._content


class DataSourceDecorator(DataSource):
    """Base decorator — holds a reference to the wrapped component."""
    def __init__(self, source: DataSource):
        self._source = source

    def write(self, data) -> None:
        self._source.write(data)   # delegate by default

    def read(self) -> str:
        return self._source.read()


class EncryptionDecorator(DataSourceDecorator):
    def write(self, data: str) -> None:
        encrypted = f"ENC({data})"
        print("[Encryption] Encrypting before write")
        return self._source.write(encrypted)

    def read(self) -> str:
        raw = self._source.read()
        decrypted = raw.replace("ENC(", "").rstrip(")")
        print(f"[Encryption] Decrypting after read")
        return decrypted


class CompressionDecorator(DataSourceDecorator):
    def write(self, data) -> None:
        compressed = f"ZIP({data})"
        print("[Compression] Compressing before write")
        return self._source.write(compressed)

    def read(self) -> str:
        raw = self._source.read()
        return raw.replace("ZIP(", "").rstrip(")")


# Stack decorators — each wraps the previous transparently:
source = FileDataSource("data.txt")
source = CompressionDecorator(source)   # adds compression
source = EncryptionDecorator(source)    # adds encryption on top


source.write("Hello World!")
# [Encryption] Encrypting...
# [Compression] Compressing...
# [File] Writing...

print(source.read())  # "Hello, World!" — transparently decrypted + decompressed

# IMPORTANT distinction:
# Python's @decorator  → function-level wrapping, works at definition time
# OOP Decorator pattern → object-level wrapping, works at runtime, both implement
#                         the same interface, can be stacked arbitrarily


# ══════════════════════════════════════════════════════════════════════════════
# 4. PROXY — control access to an object
# ══════════════════════════════════════════════════════════════════════════════
# Use when: you want to add access control, lazy loading, logging, or caching
# in front of an object, transparently to the caller.
# The proxy implements the SAME interface as the real object.
#
# Sub-types:
#   Virtual Proxy  — lazy initialisation (create expensive object only when needed)
#   Protection Proxy — access control
#   Caching Proxy  — cache results (most common in backend code)

class UserService(ABC):
    @abstractmethod
    def get_user(self, user: int) -> dict:
        pass


class RealUserService(UserService):
    def get_user(self, user_id: int) -> dict:
        print(f"[DB] Fetching user with id {user_id} from database...")
        return {"id": user_id, "name": f"User_{user_id}", "email": f"user{user_id}@example.com"}


class CachingUserServiceProxy(UserService):
    """
    Caching proxy — same interface as RealUserService.
    Caller doesn't know it's talking to a proxy.
    """
    def __init__(self, real_service: UserService):
        self._service = real_service
        self._cache: dict[int, dict] = {}

    def get_user(self, user_id: int) -> dict:
        if user_id not in self._cache:
            self._cache[user_id] = self._service.get_user(user_id)
            print(f"[Cache] Cached user {user_id}")
        else:
            print(f"[Cache] HIT for user {user_id}")

        return self._cache[user_id]


service = CachingUserServiceProxy(RealUserService())
service.get_user(1)   # DB query + cache set
service.get_user(1)   # cache hit — no DB query
service.get_user(2)   # DB query + cache set

# Proxy vs Decorator:
# Both wrap an object with the same interface.
# Proxy: controls/manages ACCESS to the object (lazy load, auth, cache).
# Decorator: ADDS behaviour (compression, encryption, logging) — can be stacked.
# In practice the distinction is conceptual; the implementation looks similar.

# Industry: Redis caching layer in front of a DB service, feature flags,
# Django's LazyObject (lazy authentication), ORM lazy loading of relations.


# ══════════════════════════════════════════════════════════════════════════════
# 5. COMPOSITE — tree structures where leaves and branches are treated the same
# ══════════════════════════════════════════════════════════════════════════════
# Use when: objects form part-whole hierarchies (trees) and you want to treat
# individual items and groups identically.
# Real examples: file system (file/directory), UI widgets, permission groups,
# menu systems, HTML DOM.

class FileSystemItem(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def size(self) -> int:
        pass

    @abstractmethod
    def display(self, indent: int = 0) -> None:
        pass


class File(FileSystemItem):
    """Leaf - no children"""
    def __init__(self, name: str, size_bytes: int):
        super().__init__(name)
        self._size = size_bytes

    def size(self) -> int:
        return self._size

    def display(self, indent: int = 0) -> None:
        print(" " * indent + f"📄 {self.name} ({self._size}B)")


class Directory(FileSystemItem):
    """Composite — contains other FileSystemItems (files or subdirectories)."""
    def __init__(self, name: str):
        super().__init__(name)
        self._children: list[FileSystemItem] = []

    def add(self, item: FileSystemItem):
        self._children.append(item)

    def size(self) -> int:
        return sum(child.size() for child in self._children)

    def display(self, indent: int = 0) -> None:
        print(" " * indent + f"📁 {self.name}/")
        for child in self._children:
            child.display(indent + 2)


# Building a Tree
root = Directory("project")
src = Directory("src")
src.add(File("main.py", 1200))
src.add(File("utils.py", 800))

tests = Directory("tests")
tests.add(File("tests_main.py", 600))

root.add(src)
root.add(tests)
root.add(File("README.md", 300))

root.display()
# 📁 project/
#   📁 src/
#     📄 main.py (1200B)
#     📄 utils.py (800B)
#   📁 tests/
#     📄 test_main.py (600B)
#   📄 README.md (300B

print(f"Total Size: {root.size()}B")  # 2900B — recursed through the whole tree

# The key: root.size() calls the same method whether the child is a File or
# a Directory. The caller doesn't care which it is.
# Industry: permission systems (user can be in a group, group can be in another group),
# UI component trees, rule engines (rule can be a single check or a group of checks).


# ── PATTERN COMPARISON ───────────────────────────────────────────────────────
# ┌────────────┬──────────────────────────────────────────────────────────────┐
# │ Pattern    │ Core question it answers                                     │
# ├────────────┼──────────────────────────────────────────────────────────────┤
# │ Adapter    │ How do I make two incompatible interfaces work together?     │
# │ Facade     │ How do I hide a complex subsystem behind a simple interface? │
# │ Decorator  │ How do I add behaviour to an object without subclassing?     │
# │ Proxy      │ How do I control access to an object transparently?         │
# │ Composite  │ How do I treat individual items and groups the same way?     │
# └────────────┴──────────────────────────────────────────────────────────────┘

# Adapter vs Facade:
# Adapter: makes ONE existing thing fit a different interface (translation).
# Facade: makes MANY things look like ONE simple interface (simplification).

# Decorator vs Proxy:
# Both wrap an object with the same interface.
# Decorator: adds new behaviour, designed to be stacked.
# Proxy: controls access/lifecycle, usually one layer.


# ── INTERVIEW QUESTIONS THIS FILE COVERS ────────────────────────────────────
# Q: What is the Adapter pattern? Give a real example.
#    → Wraps an incompatible interface so it matches what the caller expects.
#      Example: wrapping Twilio and Sendbird SDKs behind a single SMSProvider
#      interface — swap providers without touching the calling code.
#
# Q: What is the Facade pattern? How is it different from Adapter?
#    → Facade simplifies a complex subsystem into one clean interface.
#      Adapter translates one interface into another.
#      Facade is about simplification; Adapter is about compatibility.
#
# Q: What is the structural Decorator pattern? How does it differ from
#    Python's @decorator?
#    → Both wrap an object/function. The OOP Decorator wraps an OBJECT
#      that implements the same interface, so wrappers are stackable at runtime.
#      Python's @decorator wraps a FUNCTION at definition time.
#
# Q: When would you use a Proxy?
#    → When you need to control access to an object: caching results,
#      lazy initialisation, logging, or authentication — transparently to the caller.
#
# Q: What problem does Composite solve?
#    → When you have a tree structure and want to treat leaves and branches
#      with identical code. Avoids if isinstance(item, Directory) everywhere.
