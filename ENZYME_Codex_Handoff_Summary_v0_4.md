# ENZYME v0.4 — Codex CLI Handoff (Summary + Next Task)

Generated: 2026-02-13

This document is designed to be pasted into **Codex CLI** (or attached as context) so Codex can pick up the ENZYME project without prior chat history.

---

## 0) Repository

- Repo: `https://github.com/ponnhide/ENZYME`
- Branch: `main`
- License: MIT

---

## 1) Project Goal (What ENZYME does)

ENZYME is a framework to formalize wet‑lab experimental protocols written in natural language into a machine-checkable representation (**ENZYME‑IR**), then:

1) **Lower** high‑level macros into a small trusted core,
2) **Validate** structural correctness and controlled vocabulary,
3) **Score** protocol quality (completeness / ambiguity / environment fit),
4) **Report** findings as a human-readable summary.

ENZYME is inspired by “small trusted kernels” (Lean-like philosophy) and by QUEEN’s “few primitive operations” idea, adapted to wet‑lab protocols:

- **Device-run segments** vs **human/manual actions** must be explicit.
- **Observation-driven decisions** must be representable as first-class steps.

---

## 2) ENZYME‑IR: HL‑IR vs Core‑IR (Key Concept)

ENZYME uses two IR levels:

### HL‑IR (high-level)

- Easier for humans/LLMs to produce.
- May include **macros**, e.g.:
  - `incubate`, `centrifuge`, `thermocycle`, `measure`
- HL‑IR is converted to Core‑IR by `enzyme compile` (lowering).

### Core‑IR (trusted kernel input)

Core‑IR **must use only these 7 core ops**:

1. `allocate`
2. `transfer`      (human manual transfer/add/remove)
3. `manipulate`    (human manual technique beyond simple transfer)
4. `run_device`    (device-operated process; no manual prep inside)
5. `observe`       (human or instrument readout captured as data)
6. `annotate`      (notes / provenance / ambiguous text)
7. `dispose`

Core design principle:

- `run_device` is strictly “machine does the process.”
- Human actions must be `transfer` / `manipulate`.
- Observation must be explicit via `observe`, enabling objective validation and graph branching.

---

## 3) Controlled Vocabulary (Registry)

Registry control is a major part of ENZYME validation:

- `manipulate.params.action_kind`
- `run_device.params.device_kind`
- `observe.params.modality`
- `observe.params.features` keys (feature vocabulary)

Rules:

- Values must be in `registry/registry_v0_4.json` (or declared under `registries.custom` in the IR).
- `detail_level` controls whether missing/unknown vocabulary is treated as warning vs error.

---

## 4) Repository Structure (Current)

At repo root, the following exist (as shown in the GitHub file tree + README):

- `src/enzyme/` — Python implementation (CLI + core modules)
- `pyproject.toml` — packaging
- `tests/` — pytest suite
- `enzyme_ir/` — JSON Schemas:
  - `enzyme_ir/schema_hl.json`
  - `enzyme_ir/schema_core.json`
- `registry/registry_v0_4.json` — vocabulary + required settings keys
- `fixtures/` — fixture inputs + expected golden outputs:
  - `fixtures/protocolsio_fixture.json`
  - `fixtures/expected_hl.json`
  - `fixtures/expected_core.json`
- `fixtures/generated/` — generated outputs (reproducible via script)
- `examples/` — example HL/Core IR JSON files:
  - `examples/*_hl_v0_4.json`
  - `examples/*_core_v0_4.json`
- `examples/generated/` — generated validation/score/report outputs
- `scripts/generate_artifacts.py` — regenerates bundled artifacts
- `AGENTS.md` — contribution rules / quality gates
- `ENZYME_Spec_v0_4.*` — spec documents

---

## 5) Quickstart (As per README)

```bash
pip install -e .
python scripts/generate_artifacts.py
pytest -q
```

Artifact checks:

```bash
python scripts/generate_artifacts.py --check
```

CLI pipeline:

```bash
enzyme import protocolsio --in fixtures/protocolsio_fixture.json --out /tmp/hl.json
enzyme compile --in /tmp/hl.json --out /tmp/core.json
enzyme validate --in /tmp/core.json --out /tmp/validation.json
enzyme score --in /tmp/core.json --validation /tmp/validation.json --out /tmp/scores.json
enzyme report --in /tmp/core.json --validation /tmp/validation.json --scores /tmp/scores.json --format md --out /tmp/report.md
```

---

## 6) Safety / Publication Policy (Important)

For public artifacts (examples, reports, benchmarks):

- Do NOT add actionable wet-lab parameters (exact temperatures, times, concentrations, volumes).
- Use placeholders such as `X_*` / `PROGRAM_*` / symbolic values.
- ENZYME work focuses on **formalization + validation + scoring**, not on producing executable wet-lab protocols.

---

## 7) Development Rules (AGENTS.md intent)

Treat these as “source of truth”:

- Spec: `ENZYME_Spec_v0_4.md`
- Schemas: `enzyme_ir/schema_hl.json`, `enzyme_ir/schema_core.json`
- Registry: `registry/registry_v0_4.json`
- Fixtures + expected outputs: `fixtures/*`

Do not change spec/fixtures lightly; updates should be deliberate and accompanied by updated tests and regeneration.

---
