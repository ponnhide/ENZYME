#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def _to_float(v: str | None) -> Optional[float]:
    try:
        if v is None or v == "":
            return None
        return float(v)
    except Exception:
        return None


def _fmt(v: Optional[float], nd: int = 3) -> str:
    if v is None:
        return "NA"
    return f"{v:.{nd}f}"


def _load_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    return list(csv.DictReader(path.open(encoding="utf-8")))


def _summarize_long(long_rows: List[Dict[str, str]]) -> Dict[Tuple[str, str], Dict[str, float]]:
    out: Dict[Tuple[str, str], Dict[str, float]] = {}
    models = sorted({r["model"] for r in long_rows})
    for model in models:
        for group in ["nat_protocols", "nat_siblings", "all"]:
            if group == "all":
                subset = [r for r in long_rows if r["model"] == model]
            else:
                subset = [r for r in long_rows if r["model"] == model and r["group"] == group]
            totals = [_to_float(r.get("mean_total_score_100")) for r in subset]
            repros = [_to_float(r.get("mean_repro_score_100")) for r in subset]
            units = [_to_float(r.get("num_units")) for r in subset]
            out[(model, group)] = {
                "n": float(len(subset)),
                "total_mean": statistics.mean([x for x in totals if x is not None]) if subset else float("nan"),
                "repro_mean": statistics.mean([x for x in repros if x is not None]) if subset else float("nan"),
                "units_sum": float(sum(int(x) for x in units if x is not None)),
                "units_mean": statistics.mean([x for x in units if x is not None]) if subset else float("nan"),
            }
    return out


def _top_categories(
    dist_rows: List[Dict[str, str]],
    score_rows: List[Dict[str, str]],
    model: str,
    group: str,
    topk: int = 5,
) -> List[Tuple[str, int, Optional[float]]]:
    idx = {}
    for r in score_rows:
        idx[(r.get("model"), r.get("group"), r.get("category"))] = _to_float(r.get("repro_mean"))
    subset = [r for r in dist_rows if r.get("model") == model and r.get("group") == group]
    subset = sorted(subset, key=lambda r: int(r.get("n", "0")), reverse=True)[:topk]
    out: List[Tuple[str, int, Optional[float]]] = []
    for r in subset:
        cat = str(r.get("category"))
        out.append((cat, int(r.get("n", "0")), idx.get((model, group, cat))))
    return out


def _write_report_ja(
    out_path: Path,
    labels: Tuple[str, str],
    summary: Dict[Tuple[str, str], Dict[str, float]],
    signif_rows: List[Dict[str, str]],
    corr_rows: List[Dict[str, str]],
    flow_rows: List[Dict[str, str]],
    dist_rows: List[Dict[str, str]],
    score_rows: List[Dict[str, str]],
) -> None:
    gpt, qwen = labels
    sig_by_model = {r["model"]: r for r in signif_rows}
    corr_by_group = {r["group"]: r for r in corr_rows}
    flow_by_key = {(r["model"], r["group"]): r for r in flow_rows}

    lines: List[str] = []
    lines.append("# ENZYME v7 全件比較レポート（JA）")
    lines.append("")
    lines.append("## 1. 対象")
    lines.append("- コーパス: nat_protocols 14本 + nat_siblings 20本（計34本）")
    lines.append(f"- モデル: `{gpt}` / `{qwen}`")
    lines.append("")
    lines.append("## 2. スコア比較（paper mean）")
    for model in [gpt, qwen]:
        p = summary[(model, "nat_protocols")]
        s = summary[(model, "nat_siblings")]
        a = summary[(model, "all")]
        lines.append(f"### {model}")
        lines.append(
            f"- overall: total={_fmt(a['total_mean'])}, repro={_fmt(a['repro_mean'])}, units={int(a['units_sum'])}"
        )
        lines.append(
            f"- nat_protocols: total={_fmt(p['total_mean'])}, repro={_fmt(p['repro_mean'])}, units_mean={_fmt(p['units_mean'],2)}"
        )
        lines.append(
            f"- nat_siblings: total={_fmt(s['total_mean'])}, repro={_fmt(s['repro_mean'])}, units_mean={_fmt(s['units_mean'],2)}"
        )
        lines.append(
            f"- delta(protocols-siblings): total={_fmt(p['total_mean']-s['total_mean'])}, repro={_fmt(p['repro_mean']-s['repro_mean'])}"
        )
    lines.append("")
    lines.append("## 3. repro有意差（protocols vs siblings）")
    for model in [gpt, qwen]:
        row = sig_by_model.get(model)
        if not row:
            continue
        lines.append(f"### {model}")
        lines.append(
            f"- Mann-Whitney p={_fmt(_to_float(row.get('mannwhitney_p_two_sided')),6)}, Welch p={_fmt(_to_float(row.get('welch_p_two_sided')),6)}"
        )
        lines.append(
            f"- effect size: Cohen d={_fmt(_to_float(row.get('cohen_d')))}, Cliff delta={_fmt(_to_float(row.get('cliffs_delta')))}"
        )
    lines.append("")
    lines.append("## 4. モデル間相関（paper-level）")
    for group in ["all", "nat_protocols", "nat_siblings"]:
        row = corr_by_group.get(group, {})
        lines.append(
            f"- {group}: n={row.get('n','NA')}, pearson_total={_fmt(_to_float(row.get('pearson_total')))}, pearson_repro={_fmt(_to_float(row.get('pearson_repro')))}"
        )
    lines.append("")
    lines.append("## 5. フロー指標")
    for model in [gpt, qwen]:
        for group in ["nat_protocols", "nat_siblings"]:
            row = flow_by_key.get((model, group), {})
            lines.append(f"### {model} / {group}")
            lines.append(
                f"- nodes_mean={_fmt(_to_float(row.get('nodes_mean')))}, material_edges_mean={_fmt(_to_float(row.get('material_edges_mean')))}, logical_edges_mean={_fmt(_to_float(row.get('logical_edges_mean')))}"
            )
            lines.append(
                f"- combined_pass_rate={_fmt(_to_float(row.get('combined_pass_rate')))}, combined_isolated_rate_mean={_fmt(_to_float(row.get('combined_isolated_rate_mean')))}"
            )
            lines.append(
                f"- corr(repro, connectivity)={_fmt(_to_float(row.get('corr_repro_vs_connectivity')))}"
            )
    lines.append("")
    lines.append("## 6. カテゴリ上位（unit count）")
    for model in [gpt, qwen]:
        lines.append(f"### {model}")
        for group in ["nat_protocols", "nat_siblings"]:
            tops = _top_categories(dist_rows, score_rows, model, group, topk=5)
            lines.append(f"- {group}:")
            for cat, n, repro in tops:
                lines.append(f"  - {cat}: n={n}, repro_mean={_fmt(repro)}")
    lines.append("")
    lines.append("## 7. 生成物")
    lines.append("- `pilot_compare_repro_summary.md`")
    lines.append("- `repro_group_significance.md`")
    lines.append("- `model_correlation_total_grid.png` / `model_correlation_repro_grid.png`")
    lines.append("- `repro_group_jitter_box.png`")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_report_en(
    out_path: Path,
    labels: Tuple[str, str],
    summary: Dict[Tuple[str, str], Dict[str, float]],
    signif_rows: List[Dict[str, str]],
    corr_rows: List[Dict[str, str]],
    flow_rows: List[Dict[str, str]],
    dist_rows: List[Dict[str, str]],
    score_rows: List[Dict[str, str]],
) -> None:
    gpt, qwen = labels
    sig_by_model = {r["model"]: r for r in signif_rows}
    corr_by_group = {r["group"]: r for r in corr_rows}
    flow_by_key = {(r["model"], r["group"]): r for r in flow_rows}

    lines: List[str] = []
    lines.append("# ENZYME v7 Full-Corpus Comparison Report (EN)")
    lines.append("")
    lines.append("## 1. Scope")
    lines.append("- Corpus: 14 nat_protocols papers + 20 nat_siblings papers (34 total)")
    lines.append(f"- Models: `{gpt}` and `{qwen}`")
    lines.append("")
    lines.append("## 2. Score Comparison (paper means)")
    for model in [gpt, qwen]:
        p = summary[(model, "nat_protocols")]
        s = summary[(model, "nat_siblings")]
        a = summary[(model, "all")]
        lines.append(f"### {model}")
        lines.append(
            f"- overall: total={_fmt(a['total_mean'])}, repro={_fmt(a['repro_mean'])}, units={int(a['units_sum'])}"
        )
        lines.append(
            f"- nat_protocols: total={_fmt(p['total_mean'])}, repro={_fmt(p['repro_mean'])}, units_mean={_fmt(p['units_mean'],2)}"
        )
        lines.append(
            f"- nat_siblings: total={_fmt(s['total_mean'])}, repro={_fmt(s['repro_mean'])}, units_mean={_fmt(s['units_mean'],2)}"
        )
        lines.append(
            f"- delta(protocols-siblings): total={_fmt(p['total_mean']-s['total_mean'])}, repro={_fmt(p['repro_mean']-s['repro_mean'])}"
        )
    lines.append("")
    lines.append("## 3. Reproducibility Significance (protocols vs siblings)")
    for model in [gpt, qwen]:
        row = sig_by_model.get(model)
        if not row:
            continue
        lines.append(f"### {model}")
        lines.append(
            f"- Mann-Whitney p={_fmt(_to_float(row.get('mannwhitney_p_two_sided')),6)}, Welch p={_fmt(_to_float(row.get('welch_p_two_sided')),6)}"
        )
        lines.append(
            f"- effect size: Cohen d={_fmt(_to_float(row.get('cohen_d')))}, Cliff delta={_fmt(_to_float(row.get('cliffs_delta')))}"
        )
    lines.append("")
    lines.append("## 4. Cross-Model Correlation (paper-level)")
    for group in ["all", "nat_protocols", "nat_siblings"]:
        row = corr_by_group.get(group, {})
        lines.append(
            f"- {group}: n={row.get('n','NA')}, pearson_total={_fmt(_to_float(row.get('pearson_total')))}, pearson_repro={_fmt(_to_float(row.get('pearson_repro')))}"
        )
    lines.append("")
    lines.append("## 5. Flow Metrics")
    for model in [gpt, qwen]:
        for group in ["nat_protocols", "nat_siblings"]:
            row = flow_by_key.get((model, group), {})
            lines.append(f"### {model} / {group}")
            lines.append(
                f"- nodes_mean={_fmt(_to_float(row.get('nodes_mean')))}, material_edges_mean={_fmt(_to_float(row.get('material_edges_mean')))}, logical_edges_mean={_fmt(_to_float(row.get('logical_edges_mean')))}"
            )
            lines.append(
                f"- combined_pass_rate={_fmt(_to_float(row.get('combined_pass_rate')))}, combined_isolated_rate_mean={_fmt(_to_float(row.get('combined_isolated_rate_mean')))}"
            )
            lines.append(
                f"- corr(repro, connectivity)={_fmt(_to_float(row.get('corr_repro_vs_connectivity')))}"
            )
    lines.append("")
    lines.append("## 6. Top Categories (by unit count)")
    for model in [gpt, qwen]:
        lines.append(f"### {model}")
        for group in ["nat_protocols", "nat_siblings"]:
            tops = _top_categories(dist_rows, score_rows, model, group, topk=5)
            lines.append(f"- {group}:")
            for cat, n, repro in tops:
                lines.append(f"  - {cat}: n={n}, repro_mean={_fmt(repro)}")
    lines.append("")
    lines.append("## 7. Artifacts")
    lines.append("- `pilot_compare_repro_summary.md`")
    lines.append("- `repro_group_significance.md`")
    lines.append("- `model_correlation_total_grid.png` / `model_correlation_repro_grid.png`")
    lines.append("- `repro_group_jitter_box.png`")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_slides_ja(out_path: Path, labels: Tuple[str, str], summary: Dict[Tuple[str, str], Dict[str, float]]) -> None:
    gpt, qwen = labels
    gp = summary[(gpt, "nat_protocols")]
    gs = summary[(gpt, "nat_siblings")]
    qp = summary[(qwen, "nat_protocols")]
    qs = summary[(qwen, "nat_siblings")]
    text = f"""# ENZYME v7 全件比較（JA）
## Nat Protocols vs Nat Siblings
- 34 papers (protocols=14, siblings=20)
- Models: {gpt}, {qwen}
---
# スコア全体
- {gpt}
- total: protocols {_fmt(gp['total_mean'])} vs siblings {_fmt(gs['total_mean'])}
- repro: protocols {_fmt(gp['repro_mean'])} vs siblings {_fmt(gs['repro_mean'])}
- {qwen}
- total: protocols {_fmt(qp['total_mean'])} vs siblings {_fmt(qs['total_mean'])}
- repro: protocols {_fmt(qp['repro_mean'])} vs siblings {_fmt(qs['repro_mean'])}
---
# 解釈
- 両モデルで protocols > siblings（total/repro）
- ただし paper-level のモデル一致は中程度
- repro群差は Qwen で有意、GPTは有意傾向
---
# 参照図
- repro_group_jitter_box.png
- model_correlation_total_grid.png
- model_correlation_repro_grid.png
"""
    out_path.write_text(text, encoding="utf-8")


def _write_slides_en(out_path: Path, labels: Tuple[str, str], summary: Dict[Tuple[str, str], Dict[str, float]]) -> None:
    gpt, qwen = labels
    gp = summary[(gpt, "nat_protocols")]
    gs = summary[(gpt, "nat_siblings")]
    qp = summary[(qwen, "nat_protocols")]
    qs = summary[(qwen, "nat_siblings")]
    text = f"""# ENZYME v7 Full Comparison (EN)
## Nat Protocols vs Nat Siblings
- 34 papers (protocols=14, siblings=20)
- Models: {gpt}, {qwen}
---
# Score Summary
- {gpt}
- total: protocols {_fmt(gp['total_mean'])} vs siblings {_fmt(gs['total_mean'])}
- repro: protocols {_fmt(gp['repro_mean'])} vs siblings {_fmt(gs['repro_mean'])}
- {qwen}
- total: protocols {_fmt(qp['total_mean'])} vs siblings {_fmt(qs['total_mean'])}
- repro: protocols {_fmt(qp['repro_mean'])} vs siblings {_fmt(qs['repro_mean'])}
---
# Interpretation
- Both models show protocols > siblings (total and repro)
- Cross-model agreement is moderate at paper level
- Repro group difference is significant for Qwen; trend-level for GPT
---
# Figures
- repro_group_jitter_box.png
- model_correlation_total_grid.png
- model_correlation_repro_grid.png
"""
    out_path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate v7 full comparison reports/slides (JA/EN).")
    parser.add_argument("--comparison-dir", default="results_probe_v7_full_comparison")
    parser.add_argument("--label-a", default="gpt-oss-120b-v7")
    parser.add_argument("--label-b", default="qwen3-next-80b-a3b-instruct-fp8-v7")
    args = parser.parse_args()

    comp = Path(args.comparison_dir)
    long_rows = _load_csv(comp / "pilot_compare_repro_long.csv")
    signif_rows = _load_csv(comp / "repro_group_significance.csv")
    corr_rows = _load_csv(comp / "pilot_model_correlation.csv")
    flow_rows = _load_csv(comp / "pilot_flow_group_summary.csv")
    dist_rows = _load_csv(comp / "pilot_category_distribution_long.csv")
    score_rows = _load_csv(comp / "pilot_category_scores_long.csv")
    if not long_rows:
        raise SystemExit("missing long comparison CSV")

    summary = _summarize_long(long_rows)
    labels = (args.label_a, args.label_b)

    out_ja = comp / "ENZYME_v7_full_report_ja.md"
    out_en = comp / "ENZYME_v7_full_report_en.md"
    slides_ja = comp / "ENZYME_v7_full_slides_ja.md"
    slides_en = comp / "ENZYME_v7_full_slides_en.md"

    _write_report_ja(out_ja, labels, summary, signif_rows, corr_rows, flow_rows, dist_rows, score_rows)
    _write_report_en(out_en, labels, summary, signif_rows, corr_rows, flow_rows, dist_rows, score_rows)
    _write_slides_ja(slides_ja, labels, summary)
    _write_slides_en(slides_en, labels, summary)

    print(f"wrote: {out_ja}")
    print(f"wrote: {out_en}")
    print(f"wrote: {slides_ja}")
    print(f"wrote: {slides_en}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

