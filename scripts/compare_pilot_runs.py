#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

GROUPS = ("nat_protocols", "nat_siblings")


def _to_float(v) -> Optional[float]:
    try:
        if v is None or v == "":
            return None
        return float(v)
    except Exception:
        return None


def _mean(vals: List[Optional[float]]) -> Optional[float]:
    xs = [x for x in vals if x is not None]
    if not xs:
        return None
    return statistics.mean(xs)


def _median(vals: List[Optional[float]]) -> Optional[float]:
    xs = [x for x in vals if x is not None]
    if not xs:
        return None
    return statistics.median(xs)


def _pearson(xs: List[Optional[float]], ys: List[Optional[float]]) -> Optional[float]:
    pts = [(a, b) for a, b in zip(xs, ys) if a is not None and b is not None]
    if len(pts) < 2:
        return None
    x = [p[0] for p in pts]
    y = [p[1] for p in pts]
    mx = sum(x) / len(x)
    my = sum(y) / len(y)
    num = sum((a - mx) * (b - my) for a, b in pts)
    den = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
    if den == 0:
        return None
    return num / den


def _fmt(v: Optional[float], digits: int = 3) -> str:
    if v is None:
        return "NA"
    return f"{v:.{digits}f}"


def _load_run(run_dir: Path, label: str) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for group in GROUPS:
        group_dir = run_dir / group
        if not group_dir.exists():
            continue
        for paper_dir in sorted([p for p in group_dir.iterdir() if p.is_dir()]):
            summary_path = paper_dir / "paper_summary.json"
            if not summary_path.exists():
                continue
            import json

            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            rows.append(
                {
                    "model": label,
                    "group": group,
                    "paper": paper_dir.name,
                    "mean_total_score_100": _to_float(summary.get("mean_total_score_100")),
                    "mean_repro_score_100": _to_float(summary.get("mean_repro_score_100")),
                    "num_units": int(summary.get("number_of_units", 0) or 0),
                    "failure_reason": summary.get("failure_reason") or "",
                }
            )
    return rows


def _write_csv(path: Path, rows: List[Dict[str, object]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def _run_integrity(run_rows: List[Dict[str, object]]) -> Dict[str, object]:
    papers = len(run_rows)
    units = sum(int(r["num_units"]) for r in run_rows)
    failures = sum(1 for r in run_rows if str(r.get("failure_reason", "")).strip())
    missing_total = sum(1 for r in run_rows if r.get("mean_total_score_100") is None)
    missing_repro = sum(1 for r in run_rows if r.get("mean_repro_score_100") is None)
    return {
        "papers": papers,
        "units": units,
        "paper_failures": failures,
        "paper_missing_total": missing_total,
        "paper_missing_repro": missing_repro,
    }


def _model_group_stats(rows: List[Dict[str, object]], label: str) -> Dict[Tuple[str, str], Dict[str, Optional[float]]]:
    out: Dict[Tuple[str, str], Dict[str, Optional[float]]] = {}
    for group in GROUPS:
        subset = [r for r in rows if r["model"] == label and r["group"] == group]
        totals = [r["mean_total_score_100"] for r in subset]
        repros = [r["mean_repro_score_100"] for r in subset]
        units = [float(r["num_units"]) for r in subset]
        out[(label, group)] = {
            "papers": float(len(subset)),
            "total_mean": _mean(totals),
            "total_median": _median(totals),
            "repro_mean": _mean(repros),
            "repro_median": _median(repros),
            "units_total": sum(units),
            "units_mean": _mean(units),
        }
    all_subset = [r for r in rows if r["model"] == label]
    out[(label, "all")] = {
        "papers": float(len(all_subset)),
        "total_mean": _mean([r["mean_total_score_100"] for r in all_subset]),
        "total_median": _median([r["mean_total_score_100"] for r in all_subset]),
        "repro_mean": _mean([r["mean_repro_score_100"] for r in all_subset]),
        "repro_median": _median([r["mean_repro_score_100"] for r in all_subset]),
        "units_total": sum(float(r["num_units"]) for r in all_subset),
        "units_mean": _mean([float(r["num_units"]) for r in all_subset]),
    }
    return out


def _build_pairwise(
    rows_a: List[Dict[str, object]],
    rows_b: List[Dict[str, object]],
    label_a: str,
    label_b: str,
) -> List[Dict[str, object]]:
    by_key_a = {(r["group"], r["paper"]): r for r in rows_a}
    by_key_b = {(r["group"], r["paper"]): r for r in rows_b}
    keys = sorted(set(by_key_a.keys()).intersection(by_key_b.keys()))
    out: List[Dict[str, object]] = []
    for group, paper in keys:
        ra = by_key_a[(group, paper)]
        rb = by_key_b[(group, paper)]
        a_total = _to_float(ra.get("mean_total_score_100"))
        b_total = _to_float(rb.get("mean_total_score_100"))
        a_repro = _to_float(ra.get("mean_repro_score_100"))
        b_repro = _to_float(rb.get("mean_repro_score_100"))
        a_units = int(ra.get("num_units", 0) or 0)
        b_units = int(rb.get("num_units", 0) or 0)
        out.append(
            {
                "group": group,
                "paper": paper,
                f"{label_a}_total": a_total,
                f"{label_b}_total": b_total,
                "delta_total_a_minus_b": (None if a_total is None or b_total is None else a_total - b_total),
                f"{label_a}_repro": a_repro,
                f"{label_b}_repro": b_repro,
                "delta_repro_a_minus_b": (None if a_repro is None or b_repro is None else a_repro - b_repro),
                f"{label_a}_units": a_units,
                f"{label_b}_units": b_units,
                "delta_units_a_minus_b": a_units - b_units,
            }
        )
    return out


def _wins(pair_rows: List[Dict[str, object]], col_a: str, col_b: str) -> Tuple[int, int, int]:
    a = 0
    b = 0
    tie = 0
    for row in pair_rows:
        va = _to_float(row.get(col_a))
        vb = _to_float(row.get(col_b))
        if va is None or vb is None:
            continue
        if abs(va - vb) < 1e-9:
            tie += 1
        elif va > vb:
            a += 1
        else:
            b += 1
    return a, b, tie


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare two pilot run directories.")
    parser.add_argument("--run-a", required=True)
    parser.add_argument("--label-a", required=True)
    parser.add_argument("--run-b", required=True)
    parser.add_argument("--label-b", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    run_a = Path(args.run_a)
    run_b = Path(args.run_b)
    out_dir = Path(args.out_dir)

    rows_a = _load_run(run_a, args.label_a)
    rows_b = _load_run(run_b, args.label_b)
    long_rows = sorted(rows_a + rows_b, key=lambda r: (str(r["model"]), str(r["group"]), str(r["paper"])))

    _write_csv(
        out_dir / "pilot_compare_repro_long.csv",
        long_rows,
        [
            "model",
            "group",
            "paper",
            "mean_total_score_100",
            "mean_repro_score_100",
            "num_units",
            "failure_reason",
        ],
    )

    pair_rows = _build_pairwise(rows_a, rows_b, args.label_a, args.label_b)
    _write_csv(
        out_dir / "pilot_compare_repro_pairwise.csv",
        pair_rows,
        [
            "group",
            "paper",
            f"{args.label_a}_total",
            f"{args.label_b}_total",
            "delta_total_a_minus_b",
            f"{args.label_a}_repro",
            f"{args.label_b}_repro",
            "delta_repro_a_minus_b",
            f"{args.label_a}_units",
            f"{args.label_b}_units",
            "delta_units_a_minus_b",
        ],
    )

    corr_rows: List[Dict[str, object]] = []
    for group in ("all",) + GROUPS:
        subset = pair_rows if group == "all" else [r for r in pair_rows if r["group"] == group]
        xt = [_to_float(r.get(f"{args.label_a}_total")) for r in subset]
        yt = [_to_float(r.get(f"{args.label_b}_total")) for r in subset]
        xr = [_to_float(r.get(f"{args.label_a}_repro")) for r in subset]
        yr = [_to_float(r.get(f"{args.label_b}_repro")) for r in subset]
        corr_rows.append(
            {
                "group": group,
                "n": len(subset),
                "pearson_total": _pearson(xt, yt),
                "pearson_repro": _pearson(xr, yr),
            }
        )
    _write_csv(out_dir / "pilot_model_correlation.csv", corr_rows, ["group", "n", "pearson_total", "pearson_repro"])

    ia = _run_integrity(rows_a)
    ib = _run_integrity(rows_b)
    _write_csv(
        out_dir / "pilot_run_integrity.csv",
        [
            {"model": args.label_a, **ia},
            {"model": args.label_b, **ib},
        ],
        ["model", "papers", "units", "paper_failures", "paper_missing_total", "paper_missing_repro"],
    )

    stats = {}
    stats.update(_model_group_stats(long_rows, args.label_a))
    stats.update(_model_group_stats(long_rows, args.label_b))

    a_total_col = f"{args.label_a}_total"
    b_total_col = f"{args.label_b}_total"
    a_repro_col = f"{args.label_a}_repro"
    b_repro_col = f"{args.label_b}_repro"
    total_wins = _wins(pair_rows, a_total_col, b_total_col)
    repro_wins = _wins(pair_rows, a_repro_col, b_repro_col)

    mean_delta_total = _mean([_to_float(r.get("delta_total_a_minus_b")) for r in pair_rows])
    mean_delta_repro = _mean([_to_float(r.get("delta_repro_a_minus_b")) for r in pair_rows])

    lines: List[str] = []
    lines.append("# Pilot Comparison Summary")
    lines.append("")
    lines.append(f"- Compared papers: {len(pair_rows)}")
    lines.append(f"- Default wins ({args.label_a}/{args.label_b}/Tie): {total_wins[0]}/{total_wins[1]}/{total_wins[2]}")
    lines.append(f"- Repro wins ({args.label_a}/{args.label_b}/Tie): {repro_wins[0]}/{repro_wins[1]}/{repro_wins[2]}")
    lines.append(f"- Mean delta default ({args.label_a}-{args.label_b}): {_fmt(mean_delta_total)}")
    lines.append(f"- Mean delta repro ({args.label_a}-{args.label_b}): {_fmt(mean_delta_repro)}")

    for label in (args.label_a, args.label_b):
        lines.append("")
        lines.append(f"## {label}")
        all_stats = stats[(label, "all")]
        lines.append(f"- papers: {int(all_stats['papers'] or 0)}")
        lines.append(f"- units_total: {int(all_stats['units_total'] or 0)} (mean per paper: {_fmt(all_stats['units_mean'], 2)})")
        lines.append(f"- overall_total_mean: {_fmt(all_stats['total_mean'])}")
        lines.append(f"- overall_total_median: {_fmt(all_stats['total_median'])}")
        lines.append(f"- overall_repro_mean: {_fmt(all_stats['repro_mean'])}")
        lines.append(f"- overall_repro_median: {_fmt(all_stats['repro_median'])}")
        for group in GROUPS:
            gs = stats[(label, group)]
            lines.append(
                f"- {group}: n={int(gs['papers'] or 0)}, "
                f"total_mean={_fmt(gs['total_mean'])}, repro_mean={_fmt(gs['repro_mean'])}, units_mean={_fmt(gs['units_mean'], 2)}"
            )

    lines.append("")
    lines.append("## Protocols vs Siblings Delta")
    for label in (args.label_a, args.label_b):
        p = stats[(label, "nat_protocols")]
        s = stats[(label, "nat_siblings")]
        d_total = None if p["total_mean"] is None or s["total_mean"] is None else p["total_mean"] - s["total_mean"]
        d_repro = None if p["repro_mean"] is None or s["repro_mean"] is None else p["repro_mean"] - s["repro_mean"]
        lines.append(f"- {label}: total(protocols-siblings)={_fmt(d_total)}, repro(protocols-siblings)={_fmt(d_repro)}")

    (out_dir / "pilot_compare_repro_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote: {out_dir / 'pilot_compare_repro_long.csv'}")
    print(f"wrote: {out_dir / 'pilot_compare_repro_pairwise.csv'}")
    print(f"wrote: {out_dir / 'pilot_model_correlation.csv'}")
    print(f"wrote: {out_dir / 'pilot_run_integrity.csv'}")
    print(f"wrote: {out_dir / 'pilot_compare_repro_summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
