"""
TOPIC: Comprehensions
PURPOSE: All four forms, practical patterns, and when NOT to use them.
LEVEL: required for Junior | interview weight: MEDIUM

You probably know the basics. This file focuses on the parts people miss:
dict/set forms, nested loops, walrus operator, and the performance/readability tradeoffs.
"""
import re

# ── 1. ALL FOUR FORMS ────────────────────────────────────────────────────────

words = ["hello", "world", "python", "none", ""]

list_comp = [w.upper() for w in words]     # List Comprehension
set_comp = {w.lower() for w in words}      # Set Comprehension
dict_comp = {w: len(w) for w in words}     # Dictionary Comprehension
gen_expr = (w for w in words)              # Generator expression (Lazy), not a comprehension actually

# set and dict use {} — the difference is key:value vs just value.
# A bare {} creates an empty dict, NOT an empty set. Use set() for an empty set.

# ── 2. FILTERING ─────────────────────────────────────────────────────────────

clean = [w for w in words if w and w.lower() != "none"]
# → ["hello", "world", "python"]
# if clause runs BEFORE the expression — cheap guard first, expensive transform after.

# Multiple conditions:
clean_long = [w for w in words if len(w) > 4]

# ── 3. DICT COMPREHENSIONS — most underused form ─────────────────────────────

# Invert a mapping
original = {"a": 1, "b": 2, "c": 3}
inverted = {v: k for k, v in original.items()}   # → {1: "a", 2: "b", 3: "c"}

# From parallel lists (zip)
keys = ["id", "name", "age"]
values = [42, "Alice", 30]
combined = {k: v for k, v in zip(keys, values)}    # → {"id": 42, "name": "Alice", "age": 30}

# Filter a dict (keep only certain keys)
data = {"id": 1, "name": "Alice", "age": 30, "password": "secret", "email": "a@b.com"}
safe = {k: v for k, v in data.items() if k != "password"}
# Industry: serializing API responses without sensitive fields.

# ── 4. NESTED LOOPS ──────────────────────────────────────────────────────────

matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [n for row in matrix for n in row]   # → [1, 2, 3, 4, 5, 6, 7, 8, 9]
# Read left-to-right: "for row in matrix" is the outer loop, "for n in row" is inner.
# Same order as writing nested for-loops — outer first, inner second.

# With filter:
evens = [num for row in matrix for num in row if num % 2 == 0]   # → [2, 4, 6, 8]

# Cartesian Product (all pairs)
colours = ["red", "blue", "yellow"]
sizes = ["S", "M", "L"]
pairs = [(c, s) for c in colours for s in sizes]
# → [("red","S"), ("red","M"), ("red","L"), ("blue","S"), ...]

# ── 5. NESTED COMPREHENSION (comprehension inside a comprehension) ────────────
# Different from nested loops above — the inner comprehension is the EXPRESSION.

matrix_T = [[row[i] for row in matrix] for i in range(len(matrix[0]))]   # transpose

# → [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
# Outer loop iterates columns, inner loop picks one element per row.
# These get hard to read fast — prefer explicit loops beyond two levels.


# ── 6. WALRUS OPERATOR (:=) — assign and use in one expression ───────────────
# Python 3.8+. Lets you compute a value, assign it to a variable, AND use it
# in the same expression — avoiding calling the function twice.

logs = ["ERROR 500", "INFO success", "ERROR 404", "DEBUG detail"]

# Without walrus — match() is called twice:
errors = [m.group() for line in logs if re.match(r"ERROR", line)
          for m in [re.match(r"ERROR (\d+)", line)] if m]

# With walrus — clean and efficient:
errors = [m.group(1) for line in logs if (m := re.match(r"ERROR (\d+)", line))]
# → ["500", "404"]
# := assigns the result of re.match to `m` and the truthiness of `m` is the filter.

# Another common case — avoid computing something expensive twice:
results = [processed for item in range(20)
           if (processed := item ** 2) > 50]

# ── 7. WHEN NOT TO USE A COMPREHENSION ───────────────────────────────────────

# ❌ Side effects — don't use comprehensions just to loop:
# [print(x) for x in items]   ← works but wrong idiom; use a for loop
# [db.save(x) for x in items] ← same problem

# ❌ Complex logic — if the expression needs more than one line, use a loop:
# [very_long_transform(x) if condition_a(x) else other_transform(x)
#  for x in items if condition_b(x) and condition_c(x)]
# ← technically valid, practically unreadable

# ❌ When you need the index and item both — zip(range, items) works but
#    enumerate in a for-loop is cleaner for anything non-trivial.

# ✅ Sweet spot: one transformation, one optional filter, short expression.

# ── 8. PERFORMANCE NOTE ──────────────────────────────────────────────────────
# List comprehension is faster than an equivalent for-loop + .append() because
# it avoids the repeated attribute lookup on `list.append` each iteration.
# The difference is small (<2x) — never the bottleneck in real code.
# Use generator expressions instead of list comprehensions when:
#   - You only iterate once
#   - You pass directly to sum(), any(), all(), max(), min()
#   - The source data is large

total = sum(x ** 2 for x in range(1_000_000))     # -8 MB saved vs list comprehension
found = any(z > 9999 for z in range(1_000_000))   # short-circuits on first True

# ── INTERVIEW QUESTIONS THIS FILE COVERS ────────────────────────────────────
# Q: What is the difference between a list comprehension and a generator expression?
#    → List comp: evaluates all values immediately, returns a list, uses [].
#      Generator expr: lazy, computes one value at a time, uses (), single-use.
#
# Q: How do you invert a dictionary with a comprehension?
#    → {v: k for k, v in d.items()}  — only correct if values are unique and hashable.
#
# Q: In a nested loop comprehension, which loop is outer?
#    → The first `for` clause is the outer loop — same reading order as
#      writing explicit nested for-loops.
#
# Q: What is the walrus operator and when is it useful in comprehensions?
#    → := assigns a value to a variable as part of an expression.
#      Useful in comprehensions to compute a value once and both filter and
#      use it — avoids calling an expensive function twice.
