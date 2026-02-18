#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def score_100(scores: Dict[str, Any]) -> Optional[float]:
    if "total_100" in scores:
        try:
            return float(scores["total_100"])
        except Exception:
            return None
    if "total" in scores:
        try:
            return float(scores["total"]) * 100.0
        except Exception:
            return None
    return None


def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate ENZYME benchmark scores and plot")
    parser.add_argument("--results", default="results", help="Results directory")
    args = parser.parse_args()

    results_root = Path(args.results)
    analysis_dir = results_root / "analysis"
    plots_dir = analysis_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    long_rows: List[Dict[str, Any]] = []
    for score_path in sorted(results_root.glob("*/**/enzyme/unit_*.scores.json")):
        try:
            rel = score_path.relative_to(results_root)
            group = rel.parts[0]
            paper = rel.parts[1]
        except Exception:
            continue

        unit = score_path.stem.replace(".scores", "")
        val = score_100(read_json(score_path))
        long_rows.append(
            {
                "group": group,
                "paper": paper,
                "unit": unit,
                "total_score_100": "" if val is None else f"{val:.6f}",
            }
        )

    write_csv(
        analysis_dir / "scores_long.csv",
        long_rows,
        ["group", "paper", "unit", "total_score_100"],
    )

    by_paper: Dict[tuple[str, str], List[float]] = defaultdict(list)
    for row in long_rows:
        if not row["total_score_100"]:
            continue
        by_paper[(row["group"], row["paper"])].append(float(row["total_score_100"]))

    paper_rows: List[Dict[str, Any]] = []
    for (group, paper), vals in sorted(by_paper.items()):
        paper_rows.append(
            {
                "group": group,
                "paper": paper,
                "num_units": len(vals),
                "mean_total_score_100": f"{statistics.mean(vals):.6f}",
                "median_total_score_100": f"{statistics.median(vals):.6f}",
            }
        )

    write_csv(
        analysis_dir / "scores_per_paper.csv",
        paper_rows,
        ["group", "paper", "num_units", "mean_total_score_100", "median_total_score_100"],
    )

    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        print(f"[analyze] matplotlib unavailable: {exc}")
        return 0

    groups = ["nat_protocols", "nat_siblings"]
    vals_by_group = {g: [] for g in groups}
    for row in long_rows:
        if row["group"] in vals_by_group and row["total_score_100"]:
            vals_by_group[row["group"]].append(float(row["total_score_100"]))

    box_data = [vals_by_group[g] for g in groups if vals_by_group[g]]
    box_labels = [g for g in groups if vals_by_group[g]]
    if box_data:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.boxplot(box_data, labels=box_labels)
        ax.set_title("Total ENZYME Score by Group")
        ax.set_ylabel("total_score_100")
        fig.tight_layout()
        fig.savefig(plots_dir / "total_score_boxplot.png", dpi=180)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(8, 5))
        vp = ax.violinplot(box_data, showmeans=True, showextrema=True)
        for body in vp["bodies"]:
            body.set_alpha(0.5)
        ax.set_xticks(range(1, len(box_labels) + 1))
        ax.set_xticklabels(box_labels)
        ax.set_title("Total ENZYME Score Distribution")
        ax.set_ylabel("total_score_100")
        fig.tight_layout()
        fig.savefig(plots_dir / "total_score_violin.png", dpi=180)
        plt.close(fig)

    units_by_group = {g: [] for g in groups}
    for row in paper_rows:
        if row["group"] in units_by_group:
            units_by_group[row["group"]].append(int(row["num_units"]))

    bar_labels = [g for g in groups if units_by_group[g]]
    if bar_labels:
        bar_vals = [statistics.mean(units_by_group[g]) for g in bar_labels]
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(bar_labels, bar_vals)
        ax.set_title("Mean Number of Protocol Units per Paper")
        ax.set_ylabel("mean num_units")
        fig.tight_layout()
        fig.savefig(plots_dir / "num_units_per_paper.png", dpi=180)
        plt.close(fig)

    print(f"[analyze] wrote CSVs and plots to {analysis_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
