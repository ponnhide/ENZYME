# ENZYME Pilot Evaluation Report (Nat Protocols vs Nat Siblings, GPT-OSS vs Qwen)

## Abstract
This report summarizes empirical validation of the current ENZYME implementation (v0.4 MVP) along three axes: (i) implementation validity of the structuring pipeline, (ii) behavior of the scoring system, and (iii) practical usefulness for life-science protocol assessment when flow and category information are integrated. The benchmark corpus contains 34 papers (`nat_protocols=14`, `nat_siblings=20`). Models are `gpt-oss-120b-medium` and `Qwen3-Next-80B-A3B-Instruct-FP8`.

As a conceptual basis, we reference the QUEEN paper (Nature Communications, 2022, s41467-022-30588-x), which advocates reducing complex processes to reusable minimal operations while preserving operation history for reproducibility and inheritability.

Main findings are consistent across outputs. Qwen tends to score higher on `default(total)`, whereas GPT-OSS tends to score higher on `reproducibility`. At group level, both models show the same direction: `siblings > protocols (total)` and `protocols > siblings (repro)`. Reproducibility group gaps are statistically significant for both models (Mann-Whitney and Welch), with large effect sizes. Cross-model correlations are high overall and in siblings, but near zero within protocols, indicating a stable structure where macro-level group trends align while micro-level within-group rankings do not.

These findings show that ENZYME is not only a single quality score: it can explicitly separate reproducibility-relevant quality (traceability, QC, flow consistency) from general structuring quality. This pilot supports meaningful scientific discussion of ENZYME utility at the current stage. Larger-scale validation and weight optimization remain necessary for stronger generalization claims.

---

## 1. ENZYME Core Implementation and Design Intent

### 1.0 Conceptual basis (alignment with QUEEN)
Reference: https://www.nature.com/articles/s41467-022-30588-x

The QUEEN paper proposes decomposition of DNA construction into minimal core operations while preserving operation history in a regenerable form (quining). ENZYME's policy of narrowing core functions follows the same principle: keep the trusted kernel minimal and push extensibility to peripheral layers.

Corresponding ENZYME design choices:

- Fixed minimal core operations: `allocate/transfer/manipulate/run_device/observe/annotate/dispose` (`README.md`, `ENZYME_Spec_v0_4.md:59-61`)
- Lower high-level procedures into core operations: `lower_to_core` (`src/enzyme/lowering.py:29-136`)
- Preserve history/metadata for reproducibility and inheritance analysis: unit metadata, flow graph, deductions (`scripts/run_paper_benchmark.py:1373-1431`, `src/enzyme/scoring.py:675-752`)

### 1.1 E2E pipeline (import -> compile -> validate -> score -> report)
ENZYME CLI exposes `import/compile/validate/score/report` as a serial workflow (`src/enzyme/cli.py:33-105`).

- `import`: protocols.io JSON to HL-IR (`src/enzyme/cli.py:33-45`, `src/enzyme/importers/protocolsio.py:6-99`)
- `compile`: HL-IR to Core-IR via lowering (`src/enzyme/cli.py:47-56`, `src/enzyme/lowering.py:29-136`)
- `validate`: schema + registry + graph + refs + units/ranges (`src/enzyme/validator.py:372-395`)
- `score`: default 6-axis scoring + optional reproducibility extension (`src/enzyme/scoring.py:755-784`)
- `report`: markdown reporting (`src/enzyme/report.py:6-45`)

This architecture matches the specification goal of a small trusted core and two-layer evaluation (`ENZYME_Spec_v0_4.md:1-83`, `ENZYME_Spec_v0_4.md:413-464`).

### 1.2 Core methods for structuring (HL -> Core) and rationale
The central lowering function is `lower_to_core` (`src/enzyme/lowering.py:29-136`).

- Macro expansions:
  - `thermocycle/incubate/centrifuge` -> `run_device` (`src/enzyme/lowering.py:7-11`, `39-56`)
  - `measure` -> `run_device + observe` (`57-97`)
- Provenance transfer through `annotations.lowered_from` (`14-27`)
- Edge rewiring and `step_order` reconstruction (`102-135`)

Design intent: preserve expressive flexibility at HL while forcing a normalized, validator-friendly kernel representation.

### 1.3 Kernel Validator implementation and intent
`validate_core` performs integrated validation (`src/enzyme/validator.py:372-395`):

- JSON Schema validation (`39-56`, `376-377`)
- Core-op constraints (`276-289`)
- Registry consistency (action/device/modality/features) (`141-201`)
- Reference consistency (refs/edges) (`204-248`)
- Basic graph consistency (`start_step_id`, edges) (`251-273`)
- Unit parsing (pint) and observe-range constraints (`291-369`)

The warn/error behavior for unknown vocabulary via `detail_level` (`145`) is aligned with the spec's intended granularity control.

### 1.4 Default 6-axis scoring details
`score_core` computes six axes and uses their arithmetic mean for `total` (`src/enzyme/scoring.py:766-775`).

- `S_structural`: severity-based (errors can collapse score; warns/info reduce) (`15-22`)
- `S_param`: required-parameter fill ratio for `transfer/run_device/observe` (`24-43`)
- `S_vocab`: known-token ratio from registry/custom registry (`45-72`)
- `S_ident`: completeness of vendor/catalog/model/identifier (`91-104`)
- `S_ambiguity`: penalties from symbol/range ambiguity density (`106-129`)
- `S_exec_env`: execution-context completeness (device refs, container capacity) (`131-143`)

Intent: capture not only structural correctness but also information density required for reuse/re-execution.

### 1.5 Reproducibility scoring details and intent
Reproducibility is profile-driven (`profiles/reproducibility_profile.strict.v0_1.json`) with categories:
`reagent_ident, sample_ident, device_ident, container_ident, param_completeness, qc_completeness, traceability, safety_disposal, flow_integrity`.

Important implementation points:

- Category-level detail output (missing fields, deductions, issue counts) (`src/enzyme/scoring.py:629-752`)
- `flow_integrity` treated as a viability gate (`733-750`)
- `repro.total` uses equal-average over non-flow categories (`732`, `741`)
  - `total_mode = equal_average_non_flow`

This matches the current MVP policy: avoid weight bias initially, observe deficiency structure first, then optimize weights later.

### 1.6 Two-layer flow implementation
ENZYME includes two distinct flow assessments.

1. Intra-unit flow (scoring side)
- `check_flow_integrity` (`src/enzyme/scoring.py:548-626`)
- Detects: `FLOW_INPUT_WITHOUT_SOURCE`, `FLOW_ORDER_VIOLATION`, `FLOW_KIND_MISMATCH`, `FLOW_UNUSED_INTERMEDIATE`
- Penalty-weighted flow score (`607-617`)

2. Inter-unit flow within a paper (benchmark side)
- `build_paper_flow_graph` (`scripts/run_paper_benchmark.py:886-1082`)
- `material_flow`: strict sample/data reference match (`949-966`)
- `logical_flow`: timeline window + shared target terms + continuity cues + op patterns (`967-1038`)
- `combined_integrity`: integrated material/logical metric (`1052-1061`)

Intent: explicitly separate strict material handoff from textual procedural dependency and make both observable.

### 1.7 Unit category assignment
Classification is implemented in two stages.

- Generation-time labeling plus split-quality audit (`scripts/run_paper_benchmark.py:251-325`)
  - Rule file: `scripts/config/experiment_category_rules.v1.json`
  - Flags: `UNIT_TOO_SHORT_*`, `UNIT_NO_EXPERIMENT_CATEGORY`, `UNIT_CATEGORY_OVERMIXED`
- Analysis-time category aggregation (`scripts/deep_dive_analysis.py:26-83`, `169-225`)
  - Re-derives labels from unit text and outputs group/category summaries

Intent: identify which experiment types lose which reproducibility-relevant information, beyond a single global score.

---

## 2. Experimental Setup and Data

- Corpus: `nat_protocols=14`, `nat_siblings=20`, total 34 papers
- Models:
  - `gpt-oss-120b-medium-v2`
  - `qwen3-next-80b-a3b-instruct-fp8-v2`
- Run integrity:
  - GPT: 34 papers, 315 units, paper failures=0, missing total=0, missing repro=0
  - Qwen: 34 papers, 288 units, paper failures=0, missing total=0, missing repro=0
  - Source: `results_pilot_comparison_v2/pilot_run_integrity.csv`

Output artifacts:
- Score comparison: `pilot_compare_repro_summary.md`, `pilot_compare_repro_pairwise.csv`
- Significance: `repro_group_significance.md`, `repro_group_significance.csv`
- Correlation: `pilot_model_correlation.csv`, `model_correlation_*_grid.png`
- Flow: `pilot_flow_group_summary.csv`, `pilot_flow_paper_metrics.csv`
- Category: `pilot_category_distribution_long.csv`, `pilot_category_scores_long.csv`
- Nat Protocols repro list: `nat_protocols_repro_only.csv`

---

## 3. Results (from all generated outputs)

### 3.1 Overall comparison (default/repro)
Source: `results_pilot_comparison_v2/pilot_compare_repro_summary.md`

- Compared papers: 34
- Default wins (GPT/Qwen/Tie): 9 / 23 / 2
- Repro wins (GPT/Qwen/Tie): 24 / 5 / 5
- Mean delta default (GPT-Qwen): -5.120
- Mean delta repro (GPT-Qwen): +4.098

Interpretation:
- Qwen tends to score higher on default metrics.
- GPT tends to score higher on reproducibility metrics.
- ENZYME separates formatting/structuring quality from reproducibility-relevant information density.

### 3.2 Group means (protocols vs siblings)
Source: `results_pilot_comparison_v2/pilot_compare_repro_summary.md`

- GPT
  - total: protocols 57.986 vs siblings 69.785 (Delta=-11.799)
  - repro: protocols 26.986 vs siblings 16.548 (Delta=+10.438)
- Qwen
  - total: protocols 59.316 vs siblings 77.558 (Delta=-18.242)
  - repro: protocols 23.971 vs siblings 11.691 (Delta=+12.280)

Direction is consistent across both models:
- `siblings > protocols` in total
- `protocols > siblings` in reproducibility

### 3.3 Significance of repro group gap
Source: `results_pilot_comparison_v2/repro_group_significance.md`

- GPT
  - Mann-Whitney p=0.000404
  - Welch t p=0.000005
  - Cohen d=1.732, Cliff delta=0.725
- Qwen
  - Mann-Whitney p=0.000011
  - Welch t p=0.000001
  - Cohen d=2.134, Cliff delta=0.882

Conclusion:
- Reproducibility gap between protocols and siblings is strongly significant for both models.
- Effect sizes are large and practically meaningful.

### 3.4 Cross-model correlation (paper level)
Source: `results_pilot_comparison_v2/pilot_model_correlation.csv`

- all (n=34)
  - pearson_total=0.735, pearson_repro=0.760
- nat_protocols (n=14)
  - pearson_total=-0.056, pearson_repro=-0.131
- nat_siblings (n=20)
  - pearson_total=0.761, pearson_repro=0.795

Interpretation:
- Model agreement is high overall and in siblings.
- Within protocols, ranking agreement is weak.
- This does not contradict group-level agreement, because mean-level contrast and within-group rank correlation are different statistics.

### 3.5 Nat Protocols repro values (explicit reference)
Source: `results_pilot_comparison_v2/nat_protocols_repro_only.csv`

Among 14 protocols papers, GPT-better / tie / Qwen-better cases coexist.
Examples with larger gaps:

- `s41596-025-01197-x`: GPT 35.0 vs Qwen 15.8 (Delta=+19.2)
- `s41596-020-00474-1`: GPT 23.7 vs Qwen 8.5 (Delta=+15.2)
- `s41596-025-01236-7`: GPT 28.4 vs Qwen 31.5 (Delta=-3.1)

This mixture explains near-zero rank correlation within protocols.

### 3.6 Flow analysis
Source: `results_pilot_comparison_v2/pilot_flow_group_summary.csv`

- GPT / protocols
  - material_nonzero_rate=0.50
  - logical_nonzero_rate=0.857
  - combined_pass_rate=0.143
  - combined_isolated_rate_mean=0.400
  - corr(repro, connectivity)=0.690
- GPT / siblings
  - combined_pass_rate=0.000
  - combined_isolated_rate_mean=0.658
  - corr(repro, connectivity)=0.758
- Qwen / protocols
  - material_nonzero_rate=0.643
  - logical_nonzero_rate=1.000
  - combined_pass_rate=0.571
  - combined_isolated_rate_mean=0.179
  - corr(repro, connectivity)=0.658
- Qwen / siblings
  - combined_pass_rate=0.100
  - combined_isolated_rate_mean=0.503
  - corr(repro, connectivity)=0.606

Implication:
- Connectivity (`1 - isolated_rate`) is positively correlated with reproducibility.
- Flow information provides a meaningful auxiliary axis for reproducibility assessment.

### 3.7 Category analysis
Sources: `results_pilot_comparison_v2/pilot_category_distribution_long.csv`, `pilot_category_scores_long.csv`

Representative high-frequency categories:
- protocols: `cell_culture`, `centrifugation`, `microscopy_imaging`
- siblings: higher ratio of `other`, followed by `cell_culture`, `sequencing_library_prep`, `molecular_cloning`

Category-wise repro means differ across groups even within shared categories (e.g., `cell_culture`). This suggests contribution from reporting-style differences (ID/traceability/QC/flow expression), not only domain mix.

---

## 4. What these results show about ENZYME impact potential

### 4.1 Degree of evidence at pilot stage
This pilot demonstrates ENZYME utility on three fronts.

1. Independent reproducibility axis
- Cases with high default but low repro are explicitly separated.
- Useful for exposing the gap between polished narrative methods and actual rerunnability.

2. Integrated flow evaluation
- Two-layer flow (strict material + logical procedure) quantifies unit connectivity.
- Positive connectivity-repro correlation supports practical validity of flow-based diagnostics.

3. Experiment-type-specific deficiency diagnostics
- Category-level missing fields/deductions patterns are observable.
- Improvement targets can be stated concretely by category.

Overall assessment: ENZYME has reached a stage of medium-to-high practical usefulness as a reproducibility audit library for experimental methods.

### 4.2 Practical value to the biology community
The key value is not leaderboard position, but operational use:

- Methods quality audit before submission
- In-lab protocol standardization and missing-information detection
- Quantification of hidden reproducibility deficits across paper collections
- Safety-oriented quality gates for LLM-generated protocols

Separating `repro.total` from viability gating is implementation-critical because reproducibility enrichment and executability repair can be optimized independently.

---

## 5. Limitations

1. Pilot size is 34 papers; statistical robustness is moderate.
2. Qwen produced fewer units (288 vs 315), so split differences may still affect comparisons.
3. Category assignment is regex-centric and sensitive to lexical variation.
4. `logical_flow` is heuristic (`heuristic_v0_1`) and may have false positives/negatives.
5. Equal-average weighting is appropriate for MVP neutrality, but final optimal weighting is unresolved.

---

## 6. Future development potential (including full Nat Protocols scale)

### 6.1 Questions enabled at full Nat Protocols scale
If full-corpus structuring is achieved, ENZYME can support:

- Field-level reproducibility maps (cell/molecular/imaging/etc.)
- Year-wise trends in methods reporting quality
- Cross-journal comparisons (Nat Protocols vs other venues)
- Category-level bottleneck profiling (e.g., frequent `sample_ident` deficits)
- Causal hypotheses linking flow connectivity and external replication outcomes (when external replication labels are available)

### 6.2 Implementation roadmap (priority)
1. Upgrade `logical_flow`
- Introduce dependency parsing, coreference, and entity linking.
2. Strengthen category classification
- Hybrid of regex and embedding/NER.
3. Learn weights
- Keep equal-average as baseline; fit weights using external reproducibility outcomes.
4. Counterfactual diagnostics
- Estimate expected repro gain when specific missing fields are completed.
5. Quality assurance
- Add regression tests for analysis scripts and reporting pipeline.

### 6.3 Expected academic impact
At the current stage, ENZYME can already support publishable claims that:

- Methods quality can be decomposed into formal validity and reproducibility information layers.
- A common IR can compare protocols across experimental domains.
- For LLM-generated protocols, ENZYME offers explainability beyond a single scalar score.

Pilot evidence is sufficient to justify full-scale expansion.

---

## 7. Conclusion
This pilot shows that ENZYME:

- runs stably as an E2E implementation,
- integrates score/repro/flow/category in a single analysis framework,
- provides practical quantitative axes for reproducibility discussion in life-science methods.

The next phase is statistical hardening at larger scale and upgrades of logical flow, category modeling, and weight estimation. With these, ENZYME has strong potential to become objective audit infrastructure for methods reporting.

---

## Appendix A. Main artifacts cited in this report

### A1. Summary outputs
- `results_pilot_comparison_v2/pilot_compare_repro_summary.md`
- `results_pilot_comparison_v2/pilot_compare_repro_pairwise.csv`
- `results_pilot_comparison_v2/pilot_run_integrity.csv`

### A2. Statistics
- `results_pilot_comparison_v2/repro_group_significance.md`
- `results_pilot_comparison_v2/repro_group_significance.csv`
- `results_pilot_comparison_v2/pilot_model_correlation.csv`

### A3. Visualizations
- `results_pilot_comparison_v2/repro_group_jitter_box.png`
- `results_pilot_comparison_v2/model_correlation_total_grid.png`
- `results_pilot_comparison_v2/model_correlation_repro_grid.png`

### A4. Flow and category outputs
- `results_pilot_comparison_v2/pilot_flow_paper_metrics.csv`
- `results_pilot_comparison_v2/pilot_flow_group_summary.csv`
- `results_pilot_comparison_v2/pilot_category_distribution_long.csv`
- `results_pilot_comparison_v2/pilot_category_scores_long.csv`
- `results_pilot_comparison_v2/nat_protocols_repro_only.csv`

### A5. Code references
- `src/enzyme/cli.py:33`
- `src/enzyme/lowering.py:29`
- `src/enzyme/validator.py:372`
- `src/enzyme/scoring.py:15`
- `src/enzyme/scoring.py:548`
- `src/enzyme/scoring.py:629`
- `scripts/run_paper_benchmark.py:251`
- `scripts/run_paper_benchmark.py:886`
- `scripts/run_paper_benchmark.py:1398`
- `scripts/deep_dive_analysis.py:39`

### A6. Conceptual reference
- QUEEN paper (Nature Communications, 2022): `https://www.nature.com/articles/s41467-022-30588-x`
