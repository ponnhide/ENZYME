#!/usr/bin/env python3
"""Deep-dive analysis for ENZYME paper benchmark outputs."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


SCORE_COMPONENTS = [
    "S_structural",
    "S_vocab",
    "S_param",
    "S_ident",
    "S_exec_env",
    "S_ambiguity",
    "S_procedure",
    "S_specificity",
    "S_coverage",
]


def _to_float(value, default=None):
    try:
        return float(value)
    except Exception:
        return default


def load_category_rules(path: Path) -> Dict[str, List[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out: Dict[str, List[str]] = {}
    for row in data.get("categories", []):
        if not isinstance(row, dict):
            continue
        cat_id = str(row.get("id", "")).strip()
        pats = [x for x in row.get("patterns", []) if isinstance(x, str)]
        if cat_id and pats:
            out[cat_id] = pats
    return out


def classify_experiment_labels(text: str, patterns: Dict[str, List[str]]) -> List[str]:
    lowered = text.lower()
    labels = []
    for cat, pats in patterns.items():
        if any(re.search(pattern, lowered) for pattern in pats):
            labels.append(cat)
    return labels


def iter_score_records(run_dir: Path, patterns: Dict[str, List[str]]) -> List[dict]:
    records = []
    for score_path in run_dir.glob("**/enzyme/unit_*.scores.json"):
        rel = score_path.relative_to(run_dir)
        parts = rel.parts
        if len(parts) < 4:
            continue
        group, paper = parts[0], parts[1]
        unit = score_path.name.replace(".scores.json", "")
        unit_txt = run_dir / group / paper / "protocol_units" / f"{unit}.txt"
        unit_text = unit_txt.read_text(encoding="utf-8", errors="ignore") if unit_txt.exists() else ""
        labels = classify_experiment_labels(unit_text, patterns)

        with score_path.open() as f:
            obj = json.load(f)
        repro = obj.get("reproducibility")
        if not isinstance(repro, dict):
            repro = None

        records.append(
            {
                "group": group,
                "paper": paper,
                "unit": unit,
                "labels": labels,
                "default_100": _to_float(obj.get("total_100"), 0.0),
                "repro_100": _to_float((repro or {}).get("total_100"), None),
                "scores": obj.get("scores", {}),
                "top_factors": obj.get("top_factors", {}),
                "missing_fields": (repro or {}).get("missing_fields", {}),
                "category_scores": (repro or {}).get("category_scores", {}),
                "deductions": (repro or {}).get("deductions", []),
                "viability_pass": (None if repro is None else bool((repro or {}).get("viability_gate", {}).get("pass", False))),
            }
        )
    return records


def analyze_records(records: List[dict]) -> Tuple[dict, dict]:
    groups = sorted({r["group"] for r in records})
    deep_dive = {"units": len(records)}
    by_group_default_deficit = {}
    by_group_top_default_issues = {}
    by_group_repro_category_means = {}
    by_group_missing_field_prevalence = {}
    by_group_repro_deductions = {}
    by_group_corr_default_repro = {}

    for group in groups:
        rs = [r for r in records if r["group"] == group]
        n = len(rs)
        deficits = {c: 0.0 for c in SCORE_COMPONENTS}
        issue_counter = Counter()
        missing_counter = Counter()
        category_values = defaultdict(list)
        deduction_counter = Counter()
        deduction_missing = defaultdict(int)
        deduction_required = defaultdict(int)
        xs, ys = [], []

        for r in rs:
            if r["repro_100"] is not None:
                xs.append(r["default_100"])
                ys.append(r["repro_100"])
            for comp in SCORE_COMPONENTS:
                deficits[comp] += max(0.0, 1.0 - float(r["scores"].get(comp, 0.0)))
            if isinstance(r["top_factors"], dict):
                issue_counter.update(r["top_factors"])
            for key, val in r["missing_fields"].items():
                if val:
                    missing_counter[key] += 1
            for cat, val in r["category_scores"].items():
                category_values[cat].append(float(val))
            for d in r["deductions"]:
                cat = d.get("category", "unknown")
                deduction_counter[cat] += 1
                deduction_missing[cat] += int(d.get("missing_checks", 0))
                deduction_required[cat] += int(d.get("required_checks", 0))

        deficit_total = sum(deficits.values()) or 1.0
        by_group_default_deficit[group] = {
            "n": n,
            "deficit_sum": deficits,
            "deficit_share": {k: deficits[k] / deficit_total for k in SCORE_COMPONENTS},
        }
        by_group_top_default_issues[group] = issue_counter.most_common(12)
        by_group_repro_category_means[group] = {
            cat: (sum(vals) / len(vals) if vals else None) for cat, vals in category_values.items()
        }
        by_group_missing_field_prevalence[group] = [
            {"field": k, "count": v, "rate": v / n} for k, v in missing_counter.most_common(20)
        ]
        by_group_repro_deductions[group] = [
            {
                "category": cat,
                "events": ev,
                "avg_missing_checks_per_event": deduction_missing[cat] / ev if ev else 0.0,
                "avg_coverage_per_event": (
                    1.0 - (deduction_missing[cat] / deduction_required[cat]) if deduction_required[cat] else None
                ),
            }
            for cat, ev in deduction_counter.most_common(12)
        ]

        if len(xs) >= 2 and len(ys) >= 2:
            mx = sum(xs) / len(xs)
            my = sum(ys) / len(ys)
            num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
            den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
            by_group_corr_default_repro[group] = num / den if den else None
        else:
            by_group_corr_default_repro[group] = None

    deep_dive["by_group_default_deficit"] = by_group_default_deficit
    deep_dive["by_group_top_default_issues"] = by_group_top_default_issues
    deep_dive["by_group_repro_category_means"] = by_group_repro_category_means
    deep_dive["by_group_missing_field_prevalence"] = by_group_missing_field_prevalence
    deep_dive["by_group_repro_deductions"] = by_group_repro_deductions
    deep_dive["by_group_corr_default_repro"] = by_group_corr_default_repro

    category_agg = []
    distribution = Counter()
    for group in groups:
        rs_group = [r for r in records if r["group"] == group]
        for r in rs_group:
            if r["labels"]:
                for label in r["labels"]:
                    distribution[(group, label)] += 1
            else:
                distribution[(group, "other")] += 1

        labels = set()
        for r in rs_group:
            labels.update(r["labels"])
        for label in sorted(labels):
            subset = [r for r in rs_group if label in r["labels"]]
            n = len(subset)
            if n < 3:
                continue
            repro_subset = [r["repro_100"] for r in subset if r["repro_100"] is not None]
            issue_counter = Counter()
            missing_counter = Counter()
            deduction_counter = Counter()
            for r in subset:
                if isinstance(r["top_factors"], dict):
                    issue_counter.update(r["top_factors"])
                for key, val in r["missing_fields"].items():
                    if val:
                        missing_counter[key] += 1
                for d in r["deductions"]:
                    deduction_counter[d.get("category", "unknown")] += 1

            category_agg.append(
                {
                    "group": group,
                    "category": label,
                    "n": n,
                    "default_mean": sum(r["default_100"] for r in subset) / n,
                    "repro_mean": (sum(repro_subset) / len(repro_subset) if repro_subset else None),
                    "low_default_rate": sum(1 for r in subset if r["default_100"] <= 50) / n,
                    "low_repro_rate": (
                        sum(1 for v in repro_subset if v <= 15) / len(repro_subset) if repro_subset else None
                    ),
                    "top_issues": issue_counter.most_common(5),
                    "top_missing": [
                        {"field": k, "count": v, "rate": v / n} for k, v in missing_counter.most_common(6)
                    ],
                    "top_deduction_category": deduction_counter.most_common(5),
                }
            )

    category_out = {
        "units": len(records),
        "categories": category_agg,
        "distribution": [{"group": g, "category": c, "n": n} for (g, c), n in sorted(distribution.items())],
    }
    return deep_dive, category_out


def write_flat_category_csv(category_out: dict, out_csv: Path) -> None:
    def _fmt(value):
        if value is None:
            return ""
        return round(value, 3)

    rows = []
    for c in category_out["categories"]:
        rows.append(
            {
                "group": c["group"],
                "category": c["category"],
                "n": c["n"],
                "default_mean": _fmt(c["default_mean"]),
                "repro_mean": _fmt(c["repro_mean"]),
                "low_default_rate": _fmt(c["low_default_rate"]),
                "low_repro_rate": _fmt(c["low_repro_rate"]),
            }
        )
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "group",
                "category",
                "n",
                "default_mean",
                "repro_mean",
                "low_default_rate",
                "low_repro_rate",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Deep-dive analysis for ENZYME benchmark results")
    parser.add_argument("--run-dir", required=True, help="e.g. results_ablation/with_rulepack_full_llm")
    parser.add_argument("--out-dir", default="results_ablation/analysis", help="Output directory")
    parser.add_argument("--category-rules", default="scripts/config/experiment_category_rules.v1.json")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    out_dir = Path(args.out_dir)
    patterns = load_category_rules(Path(args.category_rules))
    records = iter_score_records(run_dir, patterns)
    deep_dive, category_out = analyze_records(records)

    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "deep_dive_with_full_llm.json").open("w", encoding="utf-8") as f:
        json.dump(deep_dive, f, indent=2)
    with (out_dir / "deep_dive_experiment_categories.json").open("w", encoding="utf-8") as f:
        json.dump(category_out, f, indent=2)
    write_flat_category_csv(category_out, out_dir / "deep_dive_experiment_categories.csv")

    print(f"records={len(records)}")
    print(f"wrote: {out_dir / 'deep_dive_with_full_llm.json'}")
    print(f"wrote: {out_dir / 'deep_dive_experiment_categories.json'}")
    print(f"wrote: {out_dir / 'deep_dive_experiment_categories.csv'}")


if __name__ == "__main__":
    main()
