#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
import random
import statistics
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
from scipy import stats


def _to_float(value: str):
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def _cohen_d(a: List[float], b: List[float]):
    if len(a) < 2 or len(b) < 2:
        return None
    sa = statistics.stdev(a)
    sb = statistics.stdev(b)
    na = len(a)
    nb = len(b)
    pooled = math.sqrt(((na - 1) * sa * sa + (nb - 1) * sb * sb) / (na + nb - 2))
    if pooled == 0:
        return None
    return (statistics.mean(a) - statistics.mean(b)) / pooled


def _cliffs_delta(a: List[float], b: List[float]):
    if not a or not b:
        return None
    gt = 0
    lt = 0
    for x in a:
        for y in b:
            if x > y:
                gt += 1
            elif x < y:
                lt += 1
    return (gt - lt) / (len(a) * len(b))


def _fmt(value, ndigits: int = 4):
    if value is None:
        return "NA"
    return f"{value:.{ndigits}f}"


def _load_repro_by_model(path: Path) -> Dict[str, Dict[str, List[float]]]:
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    out: Dict[str, Dict[str, List[float]]] = {}
    for row in rows:
        model = row["model"]
        group = row["group"]
        val = _to_float(row.get("mean_repro_score_100", ""))
        if val is None:
            continue
        out.setdefault(model, {}).setdefault(group, []).append(val)
    return out


def _compute_stats(protocols: List[float], siblings: List[float]) -> Dict[str, float]:
    mwu = stats.mannwhitneyu(protocols, siblings, alternative="two-sided")
    welch = stats.ttest_ind(protocols, siblings, equal_var=False)
    return {
        "protocols_n": len(protocols),
        "siblings_n": len(siblings),
        "protocols_mean": statistics.mean(protocols),
        "siblings_mean": statistics.mean(siblings),
        "protocols_median": statistics.median(protocols),
        "siblings_median": statistics.median(siblings),
        "delta_mean_protocols_minus_siblings": statistics.mean(protocols) - statistics.mean(siblings),
        "delta_median_protocols_minus_siblings": statistics.median(protocols) - statistics.median(siblings),
        "mannwhitney_u": float(mwu.statistic),
        "mannwhitney_p_two_sided": float(mwu.pvalue),
        "welch_t": float(welch.statistic),
        "welch_p_two_sided": float(welch.pvalue),
        "cohen_d": _cohen_d(protocols, siblings),
        "cliffs_delta": _cliffs_delta(protocols, siblings),
    }


def _save_plot(
    repro_by_model: Dict[str, Dict[str, List[float]]],
    summary_rows: List[Dict[str, float]],
    out_png: Path,
) -> None:
    models = sorted(repro_by_model.keys())
    fig, axes = plt.subplots(1, len(models), figsize=(6 * len(models), 5), sharey=True)
    if len(models) == 1:
        axes = [axes]

    random.seed(42)
    colors = {"nat_protocols": "#1f77b4", "nat_siblings": "#ff7f0e"}
    for ax, model in zip(axes, models):
        p = repro_by_model[model].get("nat_protocols", [])
        s = repro_by_model[model].get("nat_siblings", [])
        box = ax.boxplot(
            [p, s],
            positions=[1, 2],
            widths=0.5,
            patch_artist=True,
            showfliers=False,
        )
        for patch, color in zip(box["boxes"], [colors["nat_protocols"], colors["nat_siblings"]]):
            patch.set_facecolor(color)
            patch.set_alpha(0.25)
            patch.set_edgecolor(color)
        for i, vals in enumerate([p, s], start=1):
            jitter_x = [i + (random.random() - 0.5) * 0.22 for _ in vals]
            color = colors["nat_protocols"] if i == 1 else colors["nat_siblings"]
            ax.scatter(jitter_x, vals, s=35, alpha=0.85, color=color, edgecolors="none")

        ax.set_xticks([1, 2])
        ax.set_xticklabels(["nat_protocols", "nat_siblings"], rotation=15)
        ax.set_title(model)
        ax.grid(axis="y", alpha=0.2)
        row = next(r for r in summary_rows if r["model"] == model)
        ymax = max(p + s) if (p + s) else 0
        ax.text(
            1.5,
            ymax + 1.2,
            f"MWU p={_fmt(row['mannwhitney_p_two_sided'], 3)}\nWelch p={_fmt(row['welch_p_two_sided'], 3)}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    axes[0].set_ylabel("paper mean repro score (0-100)")
    fig.suptitle("Reproducibility Score: nat_protocols vs nat_siblings", y=1.02)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="Significance test for repro score by group.")
    parser.add_argument(
        "--long-csv",
        default="results_pilot_comparison_v2/pilot_compare_repro_long.csv",
        help="Long-format comparison csv with mean_repro_score_100.",
    )
    parser.add_argument("--out-dir", default="results_pilot_comparison_v2")
    args = parser.parse_args()

    long_csv = Path(args.long_csv)
    out_dir = Path(args.out_dir)
    repro_by_model = _load_repro_by_model(long_csv)

    summary_rows: List[Dict[str, float]] = []
    for model in sorted(repro_by_model.keys()):
        protocols = repro_by_model[model].get("nat_protocols", [])
        siblings = repro_by_model[model].get("nat_siblings", [])
        if not protocols or not siblings:
            continue
        row = _compute_stats(protocols, siblings)
        row["model"] = model
        summary_rows.append(row)

    out_csv = out_dir / "repro_group_significance.csv"
    out_md = out_dir / "repro_group_significance.md"
    out_png = out_dir / "repro_group_jitter_box.png"
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    if summary_rows:
        fieldnames = ["model"] + [k for k in summary_rows[0].keys() if k != "model"]
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(summary_rows)

        lines = ["# Repro Group Significance (nat_protocols vs nat_siblings)", ""]
        for row in summary_rows:
            lines.append(f"## {row['model']}")
            lines.append(
                f"- n(protocols/siblings): {int(row['protocols_n'])}/{int(row['siblings_n'])}"
            )
            lines.append(
                f"- mean(protocols/siblings): {_fmt(row['protocols_mean'], 3)} / {_fmt(row['siblings_mean'], 3)}"
            )
            lines.append(
                f"- median(protocols/siblings): {_fmt(row['protocols_median'], 3)} / {_fmt(row['siblings_median'], 3)}"
            )
            lines.append(
                f"- delta mean (protocols-siblings): {_fmt(row['delta_mean_protocols_minus_siblings'], 3)}"
            )
            lines.append(
                f"- Mann-Whitney U p(two-sided): {_fmt(row['mannwhitney_p_two_sided'], 6)}"
            )
            lines.append(f"- Welch t p(two-sided): {_fmt(row['welch_p_two_sided'], 6)}")
            lines.append(f"- effect size (Cohen d): {_fmt(row['cohen_d'], 3)}")
            lines.append(f"- effect size (Cliff delta): {_fmt(row['cliffs_delta'], 3)}")
            lines.append("")
        out_md.write_text("\n".join(lines), encoding="utf-8")

        _save_plot(repro_by_model, summary_rows, out_png)

    print(f"wrote: {out_csv}")
    print(f"wrote: {out_md}")
    print(f"wrote: {out_png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
