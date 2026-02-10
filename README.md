# ENZYME v0.4 MVP

ENZYME represents experimental protocols as JSON (ENZYME-IR), lowers human/macros into a core set of operations, validates them with a registry-aware kernel, computes quality scores, and emits human-readable reports.

## Concepts

- **HL-IR vs Core-IR**: HL-IR allows macros and flexible step ops. Core-IR must use only the core ops: `allocate`, `transfer`, `manipulate`, `run_device`, `observe`, `annotate`, `dispose`.
- **Lowering**: HL-IR is lowered to Core-IR by expanding macros (`thermocycle`, `incubate`, `centrifuge`, `measure`).
- **Human vs Device boundaries**:
  - `run_device` is used for automated device operation.
  - `transfer` and `manipulate` represent human actions.
  - `observe` captures observations.
- **Registry control**: `manipulate.action_kind`, `run_device.device_kind`, and `observe` vocabularies are validated against the registry or declared custom vocabularies.

## CLI Usage

```bash
enzyme import protocolsio --in fixtures/protocolsio_fixture.json --out /tmp/hl.json
enzyme compile --in /tmp/hl.json --out /tmp/core.json
enzyme validate --in /tmp/core.json --out /tmp/validation.json
enzyme score --in /tmp/core.json --validation /tmp/validation.json --out /tmp/scores.json
enzyme report --in /tmp/core.json --validation /tmp/validation.json --scores /tmp/scores.json --format md --out /tmp/report.md
```

## Testing

```bash
pytest
```

## Included artifacts

- `enzyme_ir/schema_hl.json` and `enzyme_ir/schema_core.json`
- `registry/registry_v0_4.json`
- `fixtures/protocolsio_fixture.json`
- `fixtures/expected_hl.json`
- `fixtures/expected_core.json`
- `examples/*_hl_v0_4.json` and `examples/*_core_v0_4.json`
