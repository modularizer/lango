## Goal

Build a **code language translator**, starting with **Python ↔ TypeScript**, then expanding to more languages over time.

The system should combine:

* **Deterministic transformations** where rules are clear and safe
* **AI-assisted translation** where ambiguity or stylistic judgment is required

AI should never “free-hand” everything — it operates through **explicit tools and stages**.

---

## Core Philosophy

* Deterministic first, AI last
* Every transformation should be **inspectable, testable, and reversible**
* Prefer **structure-aware translation** over text-based rewriting
* Make the system configurable enough to support:

  * Different Python versions
  * Different TS dialects (Node, Deno, browser)
  * Future languages

---

## Codebase Structure

### 1. Deterministic Translation Tools

Pure, rule-based components that:

* Parse code into structured representations
* Transform syntax where mappings are obvious
* Preserve formatting, comments, and structure when possible

Examples:

* Python `for` → TS `for…of`
* Python imports → TS imports
* Type hints → TS types (where 1:1)

These tools **must never guess**.

---

### 2. Custom AI Instructions + CLI

AI is used only when:

* Multiple valid translations exist
* Semantics depend on intent
* Language features don’t map cleanly

The AI is given:

* A **CLI interface** to run deterministic tools
* Annotated source code from earlier stages
* Clear instructions on:

  * What it may change
  * What it must preserve
  * Which dialect rules to follow

Think: AI as a *planner + resolver*, not a transformer.

---

### 3. Tests

Tests exist at multiple layers:

* Parsing correctness
* Deterministic transformation correctness
* Semantic equivalence (where possible)
* Regression tests for known edge cases

Tests are language-pair specific but share a common framework.

---

### 4. Code Editor Web Demo

A visual playground that:

* Shows original code
* Shows intermediate stages
* Shows final output
* Lets users toggle:

  * Dialects
  * Strictness
  * AI vs deterministic steps

This doubles as debugging and education.

---

## Language & Project Preferences

### Python

* Target **Python 3.10+**
* Support older versions via compatibility modes
* Prefer modern syntax:

  * `list[str]`
  * `X | None`
  * Structural pattern matching (optional)

### TypeScript

* Strong typing by default
* Configurable strictness
* Dialect profiles:

  * Node
  * Browser
  * Deno

---

## Project Configuration

* Entire codebase written in **Python3.10+**
  * `list | None` instead of `Optional[list]`, `list[str]` instead of `List[str]`
* Use **pyproject.toml**
* Absolute imports everywhere
  (except relative imports inside `__init__.py`)
* CLI registered as a script
* **Pydantic everywhere** for:

  * AST models
  * Config
  * Translation plans
  * AI instructions

---

## Architecture Style

* **Functional** for discrete transformations
* **Object-oriented** for:

  * Planning
  * Orchestration
  * Translation pipelines

Everything should be:

* Readable
* Modular
* Over-configurable (by design)

---

## Translation Run Stages

### 1. Comment / Annotation Stage

* Copy source code into a **commented mirror**
* Do **not** change logic
* Label:

  * Each function
  * Each block
  * Tricky lines

For each section:

* Can this be directly translated?
* Which deterministic tool applies?
* Are multiple valid translations possible?
* Should AI decide?

This becomes the AI’s map.

---

### 2. Deterministic Pass

Apply all safe, rule-based transformations:

* Syntax mappings
* Imports
* Obvious type conversions
* Structural rewrites

Anything uncertain is left untouched but flagged.

---

### 3. AI Resolution Pass

AI:

* Reads annotations
* Uses the CLI tools
* Resolves ambiguous or semantic gaps
* Produces final code for the target language

No blind rewriting allowed.

---

## Tooling: `ast` and `inspect`

### `ast`

Primary backbone for Python:

* Parse Python into a structured tree
* Identify functions, classes, scopes, imports
* Preserve exact source positions
* Enable precise annotations

Used for:

* Deterministic transformations
* Comment-stage labeling
* Semantic analysis

---

### `inspect`

Used for **runtime-aware translation**, when needed:

* Source retrieval
* Signature introspection
* Decorator resolution
* Type hints as actually resolved

Useful when translating:

* Libraries
* Framework code
* Metaprogramming-heavy Python

---

## Language Differences (Python ↔ TypeScript)

### Easy / Deterministic

* Loops
* Conditionals
* Function definitions (basic)
* Imports
* Simple types

### Medium / Needs Context

* Async patterns
* Exceptions
* Class inheritance
* Generics
* Default mutability

### Hard / AI Needed

* Dynamic typing tricks
* Metaclasses
* Monkey patching
* Duck typing assumptions
* Pythonic idioms without TS equivalents

Some things **cannot** be translated faithfully — those should be:

* Flagged
* Explained
* Configurable (fail vs warn)

---

## Next Expansion Goals

* Dialect preference system
* Python version compatibility matrix
* Language-agnostic intermediate representation
* More language pairs (Rust, Go, Java)

