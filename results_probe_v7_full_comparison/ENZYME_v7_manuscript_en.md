# ENZYME v7: Manuscript-Style Report on Protocol Formalization

## Abstract
We evaluate ENZYME as a machine-readable formalization and scoring framework for life-science methods text.
Across 34 papers (14 Nat Protocols + 20 Nat siblings), both gpt-oss-120b-v7 and qwen3-next-80b-a3b-instruct-fp8-v7 show protocols > siblings on total and repro metrics.
The result supports ENZYME's core thesis: natural-language methods can be lowered into a validated intermediate representation, enabling reproducibility-aware benchmarking.

## Key Results
- gpt-oss-120b-v7: protocols total/repro = 75.035/27.239, siblings = 72.126/23.188
- qwen3-next-80b-a3b-instruct-fp8-v7: protocols total/repro = 72.836/25.814, siblings = 66.691/19.065
- qwen3-next-80b-a3b-instruct-fp8-v7 repro group test: MWU p=0.031225, Welch p=0.003886
- Cross-model correlation (all): total=0.467, repro=0.355

## Design Notes
- Core ops: allocate, transfer, manipulate, run_device, observe, annotate, dispose.
- Scoring: 9-component default total + profile-based reproducibility scoring.
- Repro mode: equal-average of non-flow categories with flow viability gate.
- Flow: strict material links + heuristic logical links + combined integrity.

## Discussion
Inspired by the QUEEN concept of machine-readable provenance and regenerability, ENZYME extends the same philosophy to protocol-level method text.
The current v7 benchmark demonstrates feasibility and analytic value, while remaining gaps include logical-flow semantics and broader model diversity.

## Reference
- QUEEN paper: https://www.nature.com/articles/s41467-022-30588-x
