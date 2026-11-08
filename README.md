# python-backend-prep

A personal reference repository for Python backend development — built during the
Andersen Labs traineeship and intended as a long-term revision resource.

Each file covers one topic: why it exists, how it works mechanically, how it
appears in real projects, and what interviewers ask about it. Files are kept
under ~200 lines so they stay readable and scannable.

---

## Repository structure

```
python-backend-prep/
│
├── 01_software_engineering/     # Principles, patterns, architecture
│   ├── oop_solid_dry_kiss_yagni.py
│   ├── design_patterns_creational.py   # Singleton, Factory, Builder
│   ├── design_patterns_structural.py   # Adapter, Facade, Decorator
│   ├── design_patterns_behavioral.py   # Observer, Strategy, Command
│   ├── code_smells_refactoring.py
│   ├── tdd_bdd_ddd.md
│   └── microservices_vs_monolith.md
│
├── 02_python_core/              # Advanced Python mechanics
│   ├── decorators.py
│   ├── generators.py
│   ├── context_managers.py
│   ├── dunder_methods.py
│   ├── exceptions.py
│   ├── comprehensions.py
│   ├── scopes_closures.py
│   ├── type_hints_annotations.py
│   └── memory_gc.py
│
├── 03_oop_advanced/             # OOP beyond the basics
│   ├── mro_multiple_inheritance.py
│   ├── metaclasses.py
│   ├── abstract_base_classes.py
│   └── encapsulation.py
│
├── 04_concurrency/              # Threading, multiprocessing, async
│   ├── gil_overview.md
│   ├── threading_examples.py
│   ├── multiprocessing_examples.py
│   └── asyncio_coroutines.py
│
├── 05_testing/                  # Unit, integration, mocking
│   ├── unit_integration_functional.md
│   ├── pytest_basics.py
│   ├── unittest_basics.py
│   ├── mocking.py
│   └── fixtures_factories.py
│
├── 06_databases/                # SQL, NoSQL, indexing, transactions
│   ├── sql_nosql_overview.md
│   ├── indexes.md
│   ├── transactions_acid.md
│   └── sharding_replication.md
│
├── 07_networking/               # HTTP, REST, protocols
│   ├── osi_tcp_ip.md
│   ├── http_https.md
│   ├── rest_principles.md
│   └── websockets_rpc.md
│
├── 08_frameworks_and_tools/     # FastAPI, ORM, Docker, auth
│   ├── fastapi_quickstart.py
│   ├── orm_sqlalchemy.py
│   ├── wsgi_asgi.md
│   ├── docker_basics.md
│   ├── message_brokers.md
│   └── auth_jwt_oauth.md
│
└── 09_git_and_workflow/         # Git internals and CI/CD
    ├── git_commands.md
    └── ci_cd_overview.md
```

---

## Progress tracker

### 01 · Software Engineering
| File | Status |
|---|---|
| `oop_solid_dry_kiss_yagni.py` | ⬜ not started |
| `design_patterns_creational.py` | ✅ done |
| `design_patterns_structural.py` | ✅ done |
| `design_patterns_behavioral.py` | ⬜ not started |
| `code_smells_refactoring.py` | ⬜ not started |
| `tdd_bdd_ddd.md` | ⬜ not started |
| `microservices_vs_monolith.md` | ⬜ not started |

### 02 · Python Core
| File | Status |
|---|---|
| `decorators.py` | ✅ done |
| `generators.py` | ✅ done |
| `context_managers.py` | ✅ done |
| `dunder_methods.py` | ✅ done |
| `exceptions.py` | ✅ done |
| `comprehensions.py` | ✅ done |
| `scopes_closures.py` | ⬜ not started |
| `type_hints_annotations.py` | ⬜ not started |
| `memory_gc.py` | ⬜ not started |

### 03 · OOP Advanced
| File | Status |
|---|---|
| `mro_multiple_inheritance.py` | ⬜ not started |
| `metaclasses.py` | ⬜ not started |
| `abstract_base_classes.py` | ⬜ not started |
| `encapsulation.py` | ⬜ not started |

### 04 · Concurrency
| File | Status |
|---|---|
| `gil_overview.md` | ⬜ not started |
| `threading_examples.py` | ⬜ not started |
| `multiprocessing_examples.py` | ⬜ not started |
| `asyncio_coroutines.py` | ⬜ not started |

### 05 · Testing
| File | Status |
|---|---|
| `unit_integration_functional.md` | ⬜ not started |
| `pytest_basics.py` | ⬜ not started |
| `unittest_basics.py` | ⬜ not started |
| `mocking.py` | ⬜ not started |
| `fixtures_factories.py` | ⬜ not started |

### 06 · Databases
| File | Status |
|---|---|
| `sql_nosql_overview.md` | ⬜ not started |
| `indexes.md` | ⬜ not started |
| `transactions_acid.md` | ⬜ not started |
| `sharding_replication.md` | ⬜ not started |

### 07 · Networking
| File | Status |
|---|---|
| `osi_tcp_ip.md` | ⬜ not started |
| `http_https.md` | ⬜ not started |
| `rest_principles.md` | ⬜ not started |
| `websockets_rpc.md` | ⬜ not started |

### 08 · Frameworks and Tools
| File | Status |
|---|---|
| `fastapi_quickstart.py` | ⬜ not started |
| `orm_sqlalchemy.py` | ⬜ not started |
| `wsgi_asgi.md` | ⬜ not started |
| `docker_basics.md` | ⬜ not started |
| `message_brokers.md` | ⬜ not started |
| `auth_jwt_oauth.md` | ⬜ not started |

### 09 · Git and Workflow
| File | Status |
|---|---|
| `git_commands.md` | ⬜ not started |
| `ci_cd_overview.md` | ⬜ not started |

---

## Suggested learning order

The folders are numbered deliberately. Work through them in order — later topics
depend on earlier ones.

```
02_python_core          ← start here; everything else builds on these
03_oop_advanced         ← extends 02
01_software_engineering ← patterns make more sense once you know OOP well
05_testing              ← start writing tests early, even while learning
04_concurrency          ← asyncio requires generators (02) to make sense
06_databases            ← theory; pair with 08 ORM in practice
07_networking           ← theory; pair with 08 FastAPI in practice
08_frameworks_and_tools ← puts everything together
09_git_and_workflow     ← ongoing; reference as needed
```

**Priority within each folder:** topics with ⭐⭐⭐ interview weight in their
folder README come first. If the traineeship starts before you finish a folder,
skip to `08_frameworks_and_tools/fastapi_quickstart.py` and
`06_databases/transactions_acid.md` — those are day-one practical.

---

## File conventions

Every `.py` file follows this internal structure:

```
docstring         — topic, purpose, level, core idea
── Section 0      — why this feature exists (the problem it solves)
── Section 1..N   — mechanics with annotated, runnable examples
── Real-world      — how this appears in actual backend projects
── Interview Q&A  — questions and model answers at the bottom
```

`.md` files (conceptual topics with no runnable code) follow:

```
# Topic
## What it is
## The problem it solves
## How it works
## Real-world usage
## Interview Q&A
```

---

## How to use this repo

**Learning mode** — read a file top to bottom. Run it with `python filename.py`
to see the output. Uncomment the example lines marked with `# ←` to experiment.

**Revision mode** — jump to the Interview Q&A section at the bottom of any file.
If you can answer every question without reading the file, you're good.

**During the traineeship** — when you encounter a pattern in real code that you
don't fully understand, find the relevant file here and read just that section.
The section headers are designed to be skimmable.

---

## Background

Built alongside the Andersen Labs Python backend traineeship (2026).
Topics sourced from the traineeship curriculum and interview evaluation sheet.
Goal: cover everything from the Junior-level evaluation in depth, with emphasis
on understanding over memorisation.
