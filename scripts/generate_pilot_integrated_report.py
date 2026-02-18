#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def _to_float(v):
    try:
        if v is None or v == "":
            return None
        return float(v)
    except Exception:
        return None


def _mean(xs: List[float]) -> Optional[float]:
    vals = [x for x in xs if x is not None]
    return statistics.mean(vals) if vals else None


def _median(xs: List[float]) -> Optional[float]:
    vals = [x for x in xs if x is not None]
    return statistics.median(vals) if vals else None


def _pearson(x: List[Optional[float]], y: List[Optional[float]]) -> Optional[float]:
    pts = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
    if len(pts) < 2:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    num = sum((a - mx) * (b - my) for a, b in pts)
    den = math.sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys))
    if den == 0:
        return None
    return num / den


def _fmt(v, nd=3) -> str:
    if v is None:
        return "NA"
    return f"{v:.{nd}f}"


def _load_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    return list(csv.DictReader(path.open(encoding="utf-8")))


def _model_group_summary_from_long(long_rows: List[Dict[str, str]]) -> Dict[Tuple[str, str], dict]:
    out = {}
    keyset = sorted({(r["model"], r["group"]) for r in long_rows})
    for model, group in keyset:
        subset = [r for r in long_rows if r["model"] == model and r["group"] == group]
        totals = [_to_float(r.get("mean_total_score_100")) for r in subset]
        repros = [_to_float(r.get("mean_repro_score_100")) for r in subset]
        units = [_to_float(r.get("num_units")) for r in subset]
        out[(model, group)] = {
            "papers": len(subset),
            "total_mean": _mean(totals),
            "total_median": _median(totals),
            "repro_mean": _mean(repros),
            "repro_median": _median(repros),
            "units_mean": _mean(units),
            "units_sum": sum(int(u) for u in units if u is not None),
        }
    for model in sorted({r["model"] for r in long_rows}):
        subset = [r for r in long_rows if r["model"] == model]
        totals = [_to_float(r.get("mean_total_score_100")) for r in subset]
        repros = [_to_float(r.get("mean_repro_score_100")) for r in subset]
        units = [_to_float(r.get("num_units")) for r in subset]
        out[(model, "all")] = {
            "papers": len(subset),
            "total_mean": _mean(totals),
            "total_median": _median(totals),
            "repro_mean": _mean(repros),
            "repro_median": _median(repros),
            "units_mean": _mean(units),
            "units_sum": sum(int(u) for u in units if u is not None),
        }
    return out


def _collect_flow_metrics(run_dir: Path, model_label: str) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for flow_path in sorted(run_dir.glob("*/*/paper_flow_graph.json")):
        group = flow_path.parts[-3]
        paper = flow_path.parts[-2]
        d = json.loads(flow_path.read_text(encoding="utf-8"))
        summary_path = run_dir / group / paper / "paper_summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}

        m_graph = ((d.get("material_flow") or {}).get("inter_unit_graph") or {})
        l_graph = ((d.get("logical_flow") or {}).get("inter_unit_graph") or {})
        inter_graph = d.get("inter_unit_graph") or {}
        m_int = ((d.get("material_flow") or {}).get("integrity") or {})
        l_int = ((d.get("logical_flow") or {}).get("integrity") or {})
        c_int = d.get("combined_integrity") or {}

        m_nodes = len(m_graph.get("nodes", []) or [])
        l_nodes = len(l_graph.get("nodes", []) or [])
        i_nodes = len(inter_graph.get("nodes", []) or [])
        nodes = max(m_nodes, l_nodes, i_nodes)
        m_edges = len(m_graph.get("edges", []) or [])
        l_edges = len(l_graph.get("edges", []) or [])
        i_edges = len(inter_graph.get("edges", []) or [])

        row = {
            "model": model_label,
            "group": group,
            "paper": paper,
            "nodes": nodes,
            "material_edges": m_edges,
            "logical_edges": l_edges,
            "inter_edges": i_edges,
            "material_edge_density": (None if nodes <= 1 else m_edges / (nodes * (nodes - 1))),
            "logical_edge_density": (None if nodes <= 1 else l_edges / (nodes * (nodes - 1))),
            "material_isolated_rate": _to_float(m_int.get("isolated_unit_rate")),
            "logical_isolated_rate": _to_float(l_int.get("isolated_unit_rate")),
            "combined_isolated_rate": _to_float(c_int.get("isolated_unit_rate")),
            "material_pass": bool(m_int.get("pass", False)),
            "logical_pass": bool(l_int.get("pass", False)),
            "combined_pass": bool(c_int.get("pass", False)),
            "mean_total_score_100": _to_float(summary.get("mean_total_score_100")),
            "mean_repro_score_100": _to_float(summary.get("mean_repro_score_100")),
            "num_units": _to_float(summary.get("number_of_units")),
        }
        rows.append(row)
    return rows


def _aggregate_flow(flow_rows: List[Dict[str, object]]) -> Dict[Tuple[str, str], Dict[str, Optional[float]]]:
    out = {}
    keyset = sorted({(r["model"], r["group"]) for r in flow_rows})
    for model, group in keyset:
        rs = [r for r in flow_rows if r["model"] == model and r["group"] == group]
        out[(model, group)] = {
            "papers": len(rs),
            "nodes_mean": _mean([r["nodes"] for r in rs]),
            "material_edges_mean": _mean([r["material_edges"] for r in rs]),
            "logical_edges_mean": _mean([r["logical_edges"] for r in rs]),
            "material_nonzero_rate": _mean([1.0 if r["material_edges"] > 0 else 0.0 for r in rs]),
            "logical_nonzero_rate": _mean([1.0 if r["logical_edges"] > 0 else 0.0 for r in rs]),
            "combined_pass_rate": _mean([1.0 if r["combined_pass"] else 0.0 for r in rs]),
            "combined_isolated_rate_mean": _mean([r["combined_isolated_rate"] for r in rs]),
            "corr_repro_vs_connectivity": _pearson(
                [r["mean_repro_score_100"] for r in rs],
                [None if r["combined_isolated_rate"] is None else (1.0 - r["combined_isolated_rate"]) for r in rs],
            ),
            "corr_total_vs_connectivity": _pearson(
                [r["mean_total_score_100"] for r in rs],
                [None if r["combined_isolated_rate"] is None else (1.0 - r["combined_isolated_rate"]) for r in rs],
            ),
        }
    return out


def _load_category_outputs(run_dir: Path, model_label: str) -> Tuple[List[dict], List[dict]]:
    path = run_dir / "analysis_repro" / "deep_dive_experiment_categories.json"
    if not path.exists():
        return [], []
    d = json.loads(path.read_text(encoding="utf-8"))
    cat_rows = []
    for r in d.get("categories", []):
        cat_rows.append(
            {
                "model": model_label,
                "group": r.get("group"),
                "category": r.get("category"),
                "n": r.get("n"),
                "default_mean": _to_float(r.get("default_mean")),
                "repro_mean": _to_float(r.get("repro_mean")),
                "low_default_rate": _to_float(r.get("low_default_rate")),
                "low_repro_rate": _to_float(r.get("low_repro_rate")),
            }
        )
    dist_rows = []
    for r in d.get("distribution", []):
        dist_rows.append(
            {
                "model": model_label,
                "group": r.get("group"),
                "category": r.get("category"),
                "n": r.get("n"),
            }
        )
    return cat_rows, dist_rows


def _write_csv(path: Path, rows: List[Dict[str, object]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate integrated pilot report.")
    parser.add_argument("--comparison-dir", default="results_pilot_comparison_v2")
    parser.add_argument("--gpt-run", default="results_pilot_gptoss_medium_v2")
    parser.add_argument("--qwen-run", default="results_pilot_qwen_instruct_medium_v2")
    parser.add_argument("--gpt-label", default="gpt-oss-120b-medium-v2")
    parser.add_argument("--qwen-label", default="qwen3-next-80b-a3b-instruct-fp8-v2")
    parser.add_argument("--out-md", default="results_pilot_comparison_v2/pilot_integrated_report.md")
    args = parser.parse_args()

    comparison_dir = Path(args.comparison_dir)
    gpt_run = Path(args.gpt_run)
    qwen_run = Path(args.qwen_run)
    out_md = Path(args.out_md)

    long_rows = _load_csv(comparison_dir / "pilot_compare_repro_long.csv")
    corr_rows = _load_csv(comparison_dir / "pilot_model_correlation.csv")
    signif_rows = _load_csv(comparison_dir / "repro_group_significance.csv")
    model_group_summary = _model_group_summary_from_long(long_rows)

    gpt_label = args.gpt_label
    qwen_label = args.qwen_label

    flow_rows = _collect_flow_metrics(gpt_run, gpt_label) + _collect_flow_metrics(qwen_run, qwen_label)
    flow_summary = _aggregate_flow(flow_rows)

    gpt_cat_rows, gpt_dist_rows = _load_category_outputs(gpt_run, gpt_label)
    qwen_cat_rows, qwen_dist_rows = _load_category_outputs(qwen_run, qwen_label)
    category_rows = gpt_cat_rows + qwen_cat_rows
    distribution_rows = gpt_dist_rows + qwen_dist_rows

    _write_csv(
        comparison_dir / "pilot_flow_paper_metrics.csv",
        flow_rows,
        [
            "model",
            "group",
            "paper",
            "nodes",
            "material_edges",
            "logical_edges",
            "inter_edges",
            "material_edge_density",
            "logical_edge_density",
            "material_isolated_rate",
            "logical_isolated_rate",
            "combined_isolated_rate",
            "material_pass",
            "logical_pass",
            "combined_pass",
            "mean_total_score_100",
            "mean_repro_score_100",
            "num_units",
        ],
    )
    _write_csv(
        comparison_dir / "pilot_flow_group_summary.csv",
        [
            {"model": k[0], "group": k[1], **v}
            for k, v in sorted(flow_summary.items(), key=lambda x: (x[0][0], x[0][1]))
        ],
        [
            "model",
            "group",
            "papers",
            "nodes_mean",
            "material_edges_mean",
            "logical_edges_mean",
            "material_nonzero_rate",
            "logical_nonzero_rate",
            "combined_pass_rate",
            "combined_isolated_rate_mean",
            "corr_repro_vs_connectivity",
            "corr_total_vs_connectivity",
        ],
    )
    _write_csv(
        comparison_dir / "pilot_category_distribution_long.csv",
        distribution_rows,
        ["model", "group", "category", "n"],
    )
    _write_csv(
        comparison_dir / "pilot_category_scores_long.csv",
        category_rows,
        ["model", "group", "category", "n", "default_mean", "repro_mean", "low_default_rate", "low_repro_rate"],
    )

    lines: List[str] = []
    lines.append("# Pilot Integrated Report (Scores + Categories + Flow)")
    lines.append("")
    lines.append("## Scope")
    gpt_all = model_group_summary.get((gpt_label, "all"), {})
    qwen_all = model_group_summary.get((qwen_label, "all"), {})
    lines.append("- Corpus: nat_protocols (14 papers) + nat_siblings (20 papers), total 34 papers.")
    lines.append(
        (
            f"- Models: {gpt_label} ({int(gpt_all.get('units_sum') or 0)} units), "
            f"{qwen_label} ({int(qwen_all.get('units_sum') or 0)} units)."
        )
    )
    lines.append("")

    lines.append("## Score Summary")
    for model in [gpt_label, qwen_label]:
        p = model_group_summary.get((model, "nat_protocols"), {})
        s = model_group_summary.get((model, "nat_siblings"), {})
        lines.append(f"### {model}")
        lines.append(
            f"- total mean (protocols/siblings): {_fmt(p.get('total_mean'))} / {_fmt(s.get('total_mean'))}"
        )
        lines.append(
            f"- repro mean (protocols/siblings): {_fmt(p.get('repro_mean'))} / {_fmt(s.get('repro_mean'))}"
        )
        lines.append(
            f"- delta total (protocols-siblings): {_fmt((p.get('total_mean') or 0) - (s.get('total_mean') or 0))}"
        )
        lines.append(
            f"- delta repro (protocols-siblings): {_fmt((p.get('repro_mean') or 0) - (s.get('repro_mean') or 0))}"
        )
    lines.append("")

    lines.append("## Repro Significance (nat_protocols vs nat_siblings)")
    if signif_rows:
        for row in signif_rows:
            lines.append(f"### {row['model']}")
            lines.append(
                f"- Mann-Whitney p(two-sided): {_fmt(_to_float(row.get('mannwhitney_p_two_sided')), 6)}"
            )
            lines.append(
                f"- Welch t p(two-sided): {_fmt(_to_float(row.get('welch_p_two_sided')), 6)}"
            )
            lines.append(f"- Cohen d: {_fmt(_to_float(row.get('cohen_d')))}")
            lines.append(f"- Cliff delta: {_fmt(_to_float(row.get('cliffs_delta')))}")
    lines.append("")

    lines.append("## Flow Connectivity Summary")
    for model in [gpt_label, qwen_label]:
        for group in ["nat_protocols", "nat_siblings"]:
            row = flow_summary.get((model, group), {})
            lines.append(f"### {model} / {group}")
            lines.append(f"- papers: {int(row.get('papers') or 0)}")
            lines.append(f"- mean nodes per paper: {_fmt(row.get('nodes_mean'))}")
            lines.append(f"- mean material edges: {_fmt(row.get('material_edges_mean'))}")
            lines.append(f"- mean logical edges: {_fmt(row.get('logical_edges_mean'))}")
            lines.append(
                f"- nonzero-edge rate (material/logical): {_fmt(row.get('material_nonzero_rate'))} / {_fmt(row.get('logical_nonzero_rate'))}"
            )
            lines.append(f"- combined pass rate: {_fmt(row.get('combined_pass_rate'))}")
            lines.append(f"- combined isolated rate mean: {_fmt(row.get('combined_isolated_rate_mean'))}")
            lines.append(
                f"- corr(repro, connectivity=1-isolated_rate): {_fmt(row.get('corr_repro_vs_connectivity'))}"
            )
    lines.append("")

    lines.append("## Category Highlights (unit-level)")
    for model in [gpt_label, qwen_label]:
        lines.append(f"### {model}")
        for group in ["nat_protocols", "nat_siblings"]:
            dist_subset = [r for r in distribution_rows if r["model"] == model and r["group"] == group]
            dist_subset = sorted(dist_subset, key=lambda x: int(x["n"]), reverse=True)[:5]
            lines.append(f"- {group} top categories by unit count:")
            for r in dist_subset:
                score_row = next(
                    (
                        c
                        for c in category_rows
                        if c["model"] == model and c["group"] == group and c["category"] == r["category"]
                    ),
                    None,
                )
                repro_mean = score_row["repro_mean"] if score_row else None
                lines.append(
                    f"  - {r['category']}: n={r['n']}, repro_mean={_fmt(repro_mean)}"
                )
    lines.append("")

    lines.append("## Model Correlation")
    for row in corr_rows:
        n_value = row.get("papers", row.get("n", "NA"))
        spearman_total = _to_float(row.get("spearman_total"))
        spearman_repro = _to_float(row.get("spearman_repro"))
        lines.append(
            f"- group={row['group']} (n={n_value}): "
            f"pearson_total={_fmt(_to_float(row.get('pearson_total')))}, "
            f"pearson_repro={_fmt(_to_float(row.get('pearson_repro')))}, "
            f"spearman_total={_fmt(spearman_total)}, "
            f"spearman_repro={_fmt(spearman_repro)}"
        )
    lines.append("")

    lines.append("## Artifacts")
    lines.append("- Score comparisons: `pilot_compare_repro_summary.md`, `pilot_compare_repro_pairwise.csv`")
    lines.append("- Repro tests: `repro_group_significance.md`, `repro_group_jitter_box.png`")
    lines.append("- Correlation plots: `model_correlation_total_grid.png`, `model_correlation_repro_grid.png`")
    lines.append("- Flow tables: `pilot_flow_paper_metrics.csv`, `pilot_flow_group_summary.csv`")
    lines.append("- Category tables: `pilot_category_distribution_long.csv`, `pilot_category_scores_long.csv`")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote: {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
