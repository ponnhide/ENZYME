# ENZYME v7 Manuscript Slides (EN)
## Nat Protocols vs Nat siblings (n=34)
- Models: gpt-oss-120b-v7, qwen3-next-80b-a3b-instruct-fp8-v7
---
# Motivation
- Methods text is rich but hard to audit/comparison at scale
- ENZYME formalizes procedures into validated IR
- Inspired by QUEEN-style computable provenance thinking
---
# Design
- Core ops: allocate/transfer/manipulate/run_device/observe/annotate/dispose
- Two pathways: HL-core and direct-core
- flow: material + logical + combined integrity
---
# Scoring
- Default total = equal-average of 9 quality components
- Repro = profile-based completeness and traceability checks
- Flow used as viability gate
---
# Main Numbers
- gpt-oss-120b-v7: protocols 75.035/27.239, siblings 72.126/23.188
- qwen3-next-80b-a3b-instruct-fp8-v7: protocols 72.836/25.814, siblings 66.691/19.065
---
# Implication
- ENZYME operationalizes protocol reproducibility as measurable signals
- Enables paper-level and category-level diagnostics
- Next: stronger logical-flow semantics, broader model coverage
