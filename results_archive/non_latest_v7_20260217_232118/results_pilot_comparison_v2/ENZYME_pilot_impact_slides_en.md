# ENZYME Pilot Results
## Nat Protocols vs Nat Siblings
### Structuring and reproducibility evaluation with GPT-OSS and Qwen

- Scope: 34 papers (protocols 14 / siblings 20)
- Models: `gpt-oss-120b-medium-v2`, `qwen3-next-80b-a3b-instruct-fp8-v2`
- Source: `results_pilot_comparison_v2/*`

---

## Conceptual Background (Relation to QUEEN)

- Reference paper: Nature Communications 2022, `s41467-022-30588-x`
- Core idea:
  - Reduce complex processes to minimal operations
  - Preserve operation history to improve regenerability
- ENZYME mapping:
  - Minimized core functions
  - High-level procedures lowered into core ops
  - History/evidence preserved in JSON

---

## ENZYME Implementation (E2E)

- CLI pipeline: `import -> compile -> validate -> score -> report`
- Implementation anchors:
  - `src/enzyme/cli.py:33-105`
  - `src/enzyme/lowering.py:29-136`
  - `src/enzyme/validator.py:372-395`
  - `src/enzyme/scoring.py:755-784`

---

## Core Design of Structuring

- Separation of HL-IR and Core-IR
- Macro expansions:
  - `thermocycle/incubate/centrifuge -> run_device`
  - `measure -> run_device + observe`
- Intent:
  - Keep generation flexibility (HL)
  - Keep validation strictness (Core)

---

## Scoring Design

- Default 6 axes:
  - `S_structural, S_param, S_vocab, S_ident, S_ambiguity, S_exec_env`
- `total = mean of 6 axes`
- Reproducibility extension:
  - Profile-driven category evaluation
  - `flow_integrity` as viability gate
  - `repro.total = equal mean of non-flow categories`

---

## Flow Design (Two Layers)

- Intra-unit flow (scoring-side)
  - Detect source/order/kind mismatch and unused intermediates
- Inter-unit flow within a paper (benchmark-side)
  - `material_flow` (strict reference match)
  - `logical_flow` (timeline + lexical anchors + continuity cues)
  - `combined_integrity`

---

## Unit Category Design

- Rule-based classification (regex)
- Split quality audits:
  - `UNIT_TOO_SHORT_*`
  - `UNIT_NO_EXPERIMENT_CATEGORY`
  - `UNIT_CATEGORY_OVERMIXED`
- Analysis outputs:
  - Group-wise category distribution
  - Category-wise repro mean

---

## Run Integrity

- GPT: 34 papers / 315 units / failure 0 / repro-missing 0
- Qwen: 34 papers / 288 units / failure 0 / repro-missing 0
- Source: `pilot_run_integrity.csv`

---

## Overall Comparison (34 papers)

- Default wins (GPT/Qwen/Tie): `9 / 23 / 2`
- Repro wins (GPT/Qwen/Tie): `24 / 5 / 5`
- Mean delta default (GPT-Qwen): `-5.120`
- Mean delta repro (GPT-Qwen): `+4.098`
- Source: `pilot_compare_repro_summary.md`

---

## Protocols vs Siblings (Group Means)

- GPT
  - total: `57.986 vs 69.785` (Delta `-11.799`)
  - repro: `26.986 vs 16.548` (Delta `+10.438`)
- Qwen
  - total: `59.316 vs 77.558` (Delta `-18.242`)
  - repro: `23.971 vs 11.691` (Delta `+12.280`)

---

## Repro Significance (protocols vs siblings)

- GPT
  - Mann-Whitney p=`0.000404`
  - Welch p=`0.000005`
  - Cohen d=`1.732`
- Qwen
  - Mann-Whitney p=`0.000011`
  - Welch p=`0.000001`
  - Cohen d=`2.134`
- Source: `repro_group_significance.md`

---

## Cross-Model Correlation (paper-level)

- all (n=34):
  - pearson_total=`0.735`, pearson_repro=`0.760`
- nat_protocols (n=14):
  - pearson_total=`-0.056`, pearson_repro=`-0.131`
- nat_siblings (n=20):
  - pearson_total=`0.761`, pearson_repro=`0.795`
- Source: `pilot_model_correlation.csv`

---

## Flow Highlights

- Mean combined isolated rate:
  - GPT: protocols `0.400`, siblings `0.658`
  - Qwen: protocols `0.179`, siblings `0.503`
- corr(repro, connectivity):
  - GPT: protocols `0.690`, siblings `0.758`
  - Qwen: protocols `0.658`, siblings `0.606`
- Source: `pilot_flow_group_summary.csv`

---

## Category Highlights

- Top in protocols: `cell_culture`, `centrifugation`, `microscopy_imaging`
- Top in siblings: `other`, `cell_culture`, `sequencing_library_prep`
- Repro mean differs across groups even within same category
- Source:
  - `pilot_category_distribution_long.csv`
  - `pilot_category_scores_long.csv`

---

## Interpretation

- Group-level trends are consistent across models:
  - siblings show higher total
  - protocols show higher repro
- But within-protocols rank correlation is low
- Therefore both can hold simultaneously:
  - agreement at macro trend level
  - disagreement at micro ranking level

---

## ENZYME Impact Potential (Current Stage)

- Separates structuring quality from reproducibility quality
- Integrates flow and category signals for root-cause analysis
- Practical for pre-submission audits, lab standardization, and LLM-generated protocol checks
- This pilot supports moving to larger-scale deployment

---

## Next Development Steps

1. Upgrade `logical_flow` (co-reference / dependency)
2. Hybrid category classifier (regex + embedding)
3. Weight optimization using external reproducibility outcomes
4. Scale to full Nat Protocols corpus for cross-domain mapping
5. Fix regression tests and reproducibility analysis pipeline

---

## Appendix (Main Artifacts)

- Full report: `ENZYME_pilot_impact_report_ja.md`
- Correlation plots: `model_correlation_total_grid.png`, `model_correlation_repro_grid.png`
- Significance plot: `repro_group_jitter_box.png`
- Full tables: `pilot_compare_repro_pairwise.csv`, `pilot_flow_paper_metrics.csv`, `pilot_category_scores_long.csv`
- Nat Protocols repro list: `nat_protocols_repro_only.csv`
