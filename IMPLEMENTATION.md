## Folder tree (Python-only codebase)

```text
lango/
  pyproject.toml
  README.md

  src/
    lango/                          # package root
      __init__.py                  # relative imports allowed here only

      cli/
        __init__.py
        main.py                    # Typer entrypoint
        commands/
          __init__.py
          annotate.py              # stage 1
          deterministic.py         # stage 2
          ai.py                    # stage 3
          pipeline.py              # run all stages
          demo.py                  # optional: launch web demo

      config/
        __init__.py
        models.py                  # Pydantic config models
        load.py                    # load/merge config (toml/env/cli)
        defaults.py                # default profiles

      core/
        __init__.py
        models/
          __init__.py
          common.py                # FileRef, Span, Diagnostic, etc.
          plan.py                  # TranslationPlan, Step, ToolCall
          dialects.py              # DialectProfile models
        pipeline/
          __init__.py
          runner.py                # orchestrates stages
          context.py               # run context, paths, caches
          io.py                    # read/write/copy tree safely

      languages/
        __init__.py
        python/
          __init__.py
          parse.py                 # ast parsing + source map
          annotate.py              # stage 1 annotator (AST → labels)
          normalize.py             # formatting-safe normalization
          symbols.py               # scope/symbol table helpers
        typescript/
          __init__.py
          emit.py                  # emit TS from IR (later)
          dialects.py              # node/browser/deno profiles

      ir/
        __init__.py
        nodes.py                   # Pydantic IR node models
        convert/
          __init__.py
          py_to_ir.py              # deterministic: Python AST → IR
          ir_to_ts.py              # deterministic: IR → TS (easy subset)
          ts_to_ir.py              # later
          ir_to_py.py              # later

      deterministic/
        __init__.py
        registry.py                # register transforms/tools
        transforms/
          __init__.py
          imports.py               # py imports → normalized IR import nodes
          typing.py                # py typing → ts typing rules
          control_flow.py          # for/while/if mapping for easy subset
          functions.py             # basic defs, args, returns
          classes.py               # basic class skeleton mapping
        safety.py                  # “safe to apply?” checks

      ai/
        __init__.py
        prompts/
          __init__.py
          system_instructions.md   # your “AI rules”
          stage3_template.md       # templated plan prompt
        models.py                  # Pydantic: AIRequest/AIResponse
        tool_cli_schema.py         # describe allowed CLI calls
        orchestrator.py            # takes annotations + gaps → calls model
        apply.py                   # apply AI edits with guards

      testing/
        __init__.py
        golden/
          __init__.py
          harness.py               # golden file runner
          cases/                   # fixtures
        property/
          __init__.py
          generators.py            # small AST generators (optional)

      webdemo/
        __init__.py
        app.py                     # fastapi backend (optional)
        static/                    # built frontend artifacts (optional)
        frontend/                  # if you keep it here; or separate repo

      utils/
        __init__.py
        text.py                    # diff, patch, chunking
        hashing.py                 # cache keys
        subprocess.py              # safe process runner

  tests/
    test_annotate.py
    test_deterministic_subset.py
    test_pipeline_smoke.py
    golden_cases/
      py_to_ts/
        simple_functions/
          input.py
          expected.ts
          config.toml
```

### Why this split works

* `languages/` is where parsing + language-specific quirks live
* `ir/` is the “bridge” so you don’t build N² translators
* `deterministic/` holds transforms you can unit test hard
* `ai/` is isolated, so it can’t leak into deterministic logic
* `core/pipeline` is orchestration only

---

## Implementation approach (how the translator actually works)

### Key data types (Pydantic-first)

You’ll want Pydantic models for:

* **Span**: file, start/end offsets, start/end line/col
* **ChunkLabel**: “what this block is” + translation advice
* **Diagnostic**: severity, message, span, stage
* **DialectProfile**: (python_version, ts_target, strict, runtime)
* **TranslationPlan**: ordered steps, each with inputs/outputs + tool calls
* **IR nodes**: minimal but extensible (Module, Import, Func, Class, If, For…)

### Stage 1: Annotation

Input: Python source
Output: “commented mirror” + metadata JSON

Mechanics:

* Parse with `ast.parse`
* Walk nodes and compute spans (`lineno`, `end_lineno`, col offsets)
* Emit a **parallel file** that inserts comments like:

```py
# [lango] FUNC: direct mapping → deterministic.functions (args/return)
def foo(x: int) -> int:
    # [lango] IF: direct mapping → deterministic.control_flow
    if x > 0:
        ...
```

Also emit `annotations.json` next to it for the AI + tooling.

### Stage 2: Deterministic pass

Input: original + annotations
Output: intermediate IR + “partially translated TS” for easy subset

Mechanics:

* Python AST → IR (`py_to_ir.py`)
* Apply deterministic transforms (registry-driven)
* IR → TS emitter (only for supported nodes)
* Anything unsupported becomes:

  * a stub node in IR
  * a TS placeholder + diagnostic

### Stage 3: AI pass

Input: TS partial + annotations + diagnostics
Output: final TS

Mechanics:

* AI gets:

  * the *plan* (what remains)
  * the allowed CLI actions
  * the exact placeholder spans it can edit
* Guardrails:

  * AI only edits within known placeholders OR produces patch hunks
  * you validate patches apply cleanly and don’t touch forbidden regions

---

## First steps (build in the right order)

1. **Bootstrap project**

   * `pyproject.toml`, ruff/black/mypy, pytest
   * Typer CLI skeleton: `lango annotate`, `lango run`

2. **Core models**

   * `Span`, `Diagnostic`, `DialectProfile`, `TranslationPlan`
   * File IO utilities: copy tree → output workspace

3. **Python parsing + spans**

   * `languages/python/parse.py` returns `(ast_tree, source, source_map)`
   * Source map: node → Span (line/col → offsets)

4. **Annotation stage MVP**

   * Walk AST and label: module imports, classes, funcs, control flow
   * Write `*_commented.py` + `annotations.json`

5. **IR minimal**

   * Implement IR for: Module, Import, FuncDef, Call (basic), If, For, Return, Assign
   * Write `py_to_ir` for only those nodes

6. **TS emitter minimal**

   * Emit TS for the same easy subset
   * Anything else emits a placeholder + diagnostic

7. **Golden tests**

   * Start with 10 tiny Python snippets
   * Assert deterministic output TS matches expected for supported subset

8. **AI scaffolding (no real model yet)**

   * Define “tool CLI schema” + placeholder rules
   * Implement `ai.apply` that can take a patch and apply safely
   * You can stub the AI response during tests

---

## A practical plan (milestones)

### Milestone 1: “Deterministic subset works” (1–2 weeks)

* CLI: annotate + deterministic
* IR + emitter supports basics
* Golden tests passing

### Milestone 2: “Pipeline and diagnostics feel real” (next)

* `lango run` creates workspace, runs stages, outputs report.json
* Pretty CLI output (what succeeded/failed)

### Milestone 3: “AI pass integrated safely”

* Placeholders + guarded patching
* Configurable AI instructions by dialect profile
* Regression tests: AI cannot edit protected regions

### Milestone 4: “Web demo”

* Load input, show stages, show diagnostics
* Run pipeline locally and display outputs

