#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
from scipy import stats


def _to_float(value: str):
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def _detect_columns(fieldnames: List[str]) -> Tuple[str, str, str, str]:
    total_cols = [c for c in fieldnames if c.endswith("_total")]
    repro_cols = [c for c in fieldnames if c.endswith("_repro")]
    if len(total_cols) != 2 or len(repro_cols) != 2:
        raise ValueError("Unexpected pairwise schema for total/repro columns")
    return total_cols[0], total_cols[1], repro_cols[0], repro_cols[1]


def _pearson(xs: List[float], ys: List[float]):
    if len(xs) < 2:
        return None
    return stats.pearsonr(xs, ys).statistic


def _spearman(xs: List[float], ys: List[float]):
    if len(xs) < 2:
        return None
    return stats.spearmanr(xs, ys).statistic


def _fmt(value, digits=3):
    if value is None:
        return "NA"
    return f"{value:.{digits}f}"


def _subset_points(rows: List[Dict[str, str]], xcol: str, ycol: str, group: str | None):
    xs, ys = [], []
    for row in rows:
        if group is not None and row["group"] != group:
            continue
        x = _to_float(row[xcol])
        y = _to_float(row[ycol])
        if x is None or y is None:
            continue
        xs.append(x)
        ys.append(y)
    return xs, ys


def _plot_corr_grid(
    rows: List[Dict[str, str]],
    xcol: str,
    ycol: str,
    title: str,
    out_png: Path,
) -> None:
    groups = [None, "nat_protocols", "nat_siblings"]
    labels = ["all", "nat_protocols", "nat_siblings"]
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharex=False, sharey=False)

    for ax, g, label in zip(axes, groups, labels):
        xs, ys = _subset_points(rows, xcol, ycol, g)
        n = len(xs)
        ax.scatter(xs, ys, s=38, alpha=0.85, color="#1f77b4", edgecolors="none")

        if n >= 2:
            lr = stats.linregress(xs, ys)
            x_min, x_max = min(xs), max(xs)
            if x_min == x_max:
                x_min -= 1.0
                x_max += 1.0
            x_line = [x_min, x_max]
            y_line = [lr.slope * x + lr.intercept for x in x_line]
            ax.plot(x_line, y_line, color="#d62728", linewidth=1.6)

            p = _pearson(xs, ys)
            s = _spearman(xs, ys)
            txt = f"n={n}\nPearson={_fmt(p)}\nSpearman={_fmt(s)}"
            ax.text(
                0.02,
                0.98,
                txt,
                transform=ax.transAxes,
                va="top",
                ha="left",
                fontsize=9,
                bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "none"},
            )
        else:
            ax.text(0.02, 0.98, f"n={n}", transform=ax.transAxes, va="top", ha="left", fontsize=9)

        lo = min(xs + ys) if xs and ys else 0
        hi = max(xs + ys) if xs and ys else 1
        if hi <= lo:
            hi = lo + 1
        pad = (hi - lo) * 0.08
        lo -= pad
        hi += pad
        ax.plot([lo, hi], [lo, hi], "--", color="gray", linewidth=1)
        ax.set_xlim(lo, hi)
        ax.set_ylim(lo, hi)
        ax.set_title(label)
        ax.grid(alpha=0.2)
        ax.set_xlabel(xcol)
        ax.set_ylabel(ycol)

    fig.suptitle(title)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="Plot model correlation scatter grids.")
    parser.add_argument(
        "--pairwise-csv",
        default="results_pilot_comparison_v2/pilot_compare_repro_pairwise.csv",
        help="Pairwise comparison CSV path.",
    )
    parser.add_argument("--out-dir", default="results_pilot_comparison_v2")
    args = parser.parse_args()

    pairwise_csv = Path(args.pairwise_csv)
    out_dir = Path(args.out_dir)

    rows = list(csv.DictReader(pairwise_csv.open(encoding="utf-8")))
    if not rows:
        raise SystemExit("No rows in pairwise csv")

    x_total, y_total, x_repro, y_repro = _detect_columns(rows[0].keys())

    out_total = out_dir / "model_correlation_total_grid.png"
    out_repro = out_dir / "model_correlation_repro_grid.png"

    _plot_corr_grid(
        rows=rows,
        xcol=x_total,
        ycol=y_total,
        title="Model Correlation (Total Score): all / nat_protocols / nat_siblings",
        out_png=out_total,
    )
    _plot_corr_grid(
        rows=rows,
        xcol=x_repro,
        ycol=y_repro,
        title="Model Correlation (Repro Score): all / nat_protocols / nat_siblings",
        out_png=out_repro,
    )

    print(f"wrote: {out_total}")
    print(f"wrote: {out_repro}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
