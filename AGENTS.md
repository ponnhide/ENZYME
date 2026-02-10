# ENZYME project instructions (v0.4)

## Source of truth
- spec: ENZYME_Spec_v0_4.md
- schemas: enzyme_ir.schema.v0_4.json / enzyme_core_ir.schema.v0_4.json
- registry: enzyme_registry.v0_4.json
- fixtures: expected_*_v0_4.json

## Rules
- Do not invent missing requirements. Follow the spec exactly.
- Treat schema/registry/fixtures as authoritative artifacts (copy them as-is).
- If spec and artifacts disagree, STOP and report the conflict.

## Quality gates
- Implement MVP end-to-end: import -> HL-IR -> compile(lower) -> Core-IR -> validate -> score -> report -> CLI.
- Add tests that use the provided fixtures as golden outputs.
