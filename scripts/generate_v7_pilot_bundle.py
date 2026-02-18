#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import matplotlib.pyplot as plt
from scipy import stats


GROUPS = ("nat_protocols", "nat_siblings")
NP3_PAPERS = ("s41596-019-0213-z", "s41596-021-00562-w", "s41596-023-00827-6")


@dataclass(frozen=True)
class RunSpec:
    label: str
    root: Path


def _to_float(v: Any) -> float | None:
    try:
        if v is None:
            return None
        return float(v)
    except Exception:
        return None


def _score_from_json(d: dict[str, Any]) -> tuple[float | None, float | None]:
    total = _to_float(d.get("total_100"))
    if total is None:
        t = _to_float(d.get("total"))
        if t is not None:
            total = t * 100.0 if t <= 1.0 else t

    repro_raw = d.get("reproducibility")
    repro = None
    if isinstance(repro_raw, dict):
        repro = _to_float(repro_raw.get("total_100"))
        if repro is None:
            rr = _to_float(repro_raw.get("total"))
            if rr is not None:
                repro = rr * 100.0 if rr <= 1.0 else rr
    else:
        repro = _to_float(repro_raw)
        if repro is not None and repro <= 1.0:
            repro *= 100.0
    return total, repro


def _iter_score_files(enzyme_dir: Path) -> Iterable[Path]:
    for f in sorted(enzyme_dir.glob("unit_*.scores.json")):
        if ".core." in f.name:
            continue
        yield f


def collect_paper_scores(run: RunSpec) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group in GROUPS:
        gdir = run.root / group
        if not gdir.exists():
            continue
        for pdir in sorted([p for p in gdir.iterdir() if p.is_dir()]):
            enzyme_dir = pdir / "enzyme"
            if not enzyme_dir.exists():
                continue
            totals: list[float] = []
            repros: list[float] = []
            for sf in _iter_score_files(enzyme_dir):
                d = json.loads(sf.read_text(encoding="utf-8"))
                t, r = _score_from_json(d)
                if t is not None and r is not None:
                    totals.append(t)
                    repros.append(r)
            if not totals:
                continue
            rows.append(
                {
                    "model": run.label,
                    "group": group,
                    "paper": pdir.name,
                    "unit_n": len(totals),
                    "paper_total_mean": sum(totals) / len(totals),
                    "paper_repro_mean": sum(repros) / len(repros),
                }
            )
    return rows


def collect_flow_rows(run: RunSpec) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for flow_path in sorted(run.root.glob("*/*/paper_flow_graph.json")):
        group = flow_path.parts[-3]
        paper = flow_path.parts[-2]
        d = json.loads(flow_path.read_text(encoding="utf-8"))
        c = d.get("combined_integrity") or {}
        rows.append(
            {
                "model": run.label,
                "group": group,
                "paper": paper,
                "combined_isolated_rate": _to_float(c.get("isolated_unit_rate")),
                "combined_pass": 1 if bool(c.get("pass", False)) else 0,
            }
        )
    return rows


def _mean(xs: list[float]) -> float | None:
    if not xs:
        return None
    return sum(xs) / len(xs)


def _median(xs: list[float]) -> float | None:
    if not xs:
        return None
    ys = sorted(xs)
    n = len(ys)
    if n % 2 == 1:
        return ys[n // 2]
    return (ys[n // 2 - 1] + ys[n // 2]) / 2.0


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(ys) < 2 or len(xs) != len(ys):
        return None
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    denx = sum((a - mx) ** 2 for a in xs)
    deny = sum((b - my) ** 2 for b in ys)
    den = math.sqrt(denx * deny)
    if den == 0:
        return None
    return num / den


def _fmt(v: float | None, nd: int = 3) -> str:
    if v is None:
        return "NA"
    return f"{v:.{nd}f}"


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _group_stats(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    models = sorted({str(r["model"]) for r in rows})
    for model in models:
        for group in GROUPS:
            ss = [r for r in rows if r["model"] == model and r["group"] == group]
            totals = [float(r["paper_total_mean"]) for r in ss]
            repros = [float(r["paper_repro_mean"]) for r in ss]
            units = [float(r["unit_n"]) for r in ss]
            out.append(
                {
                    "model": model,
                    "group": group,
                    "paper_n": len(ss),
                    "total_mean": _mean(totals),
                    "total_median": _median(totals),
                    "repro_mean": _mean(repros),
                    "repro_median": _median(repros),
                    "units_mean": _mean(units),
                    "units_sum": sum(units),
                }
            )
    return out


def _significance_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    models = sorted({str(r["model"]) for r in rows})
    for model in models:
        p = [float(r["paper_repro_mean"]) for r in rows if r["model"] == model and r["group"] == "nat_protocols"]
        s = [float(r["paper_repro_mean"]) for r in rows if r["model"] == model and r["group"] == "nat_siblings"]
        if len(p) < 2 or len(s) < 2:
            continue
        mw = stats.mannwhitneyu(p, s, alternative="two-sided")
        welch = stats.ttest_ind(p, s, equal_var=False)
        pooled = math.sqrt(((len(p) - 1) * stats.tvar(p) + (len(s) - 1) * stats.tvar(s)) / max(1, len(p) + len(s) - 2))
        d = ((sum(p) / len(p)) - (sum(s) / len(s))) / pooled if pooled > 0 else None
        out.append(
            {
                "model": model,
                "protocols_n": len(p),
                "siblings_n": len(s),
                "protocols_mean_repro": _mean(p),
                "siblings_mean_repro": _mean(s),
                "delta_protocols_minus_siblings": (_mean(p) or 0.0) - (_mean(s) or 0.0),
                "mannwhitney_u": float(mw.statistic),
                "mannwhitney_p": float(mw.pvalue),
                "welch_t": float(welch.statistic) if welch.statistic is not None else None,
                "welch_p": float(welch.pvalue) if welch.pvalue is not None else None,
                "cohen_d": d,
            }
        )
    return out


def _correlation_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    models = sorted({str(r["model"]) for r in rows})
    groups = ("all",) + GROUPS
    for group in groups:
        if group == "all":
            a = [r for r in rows if r["model"] == models[0]]
            b = [r for r in rows if r["model"] == models[1]]
        else:
            a = [r for r in rows if r["model"] == models[0] and r["group"] == group]
            b = [r for r in rows if r["model"] == models[1] and r["group"] == group]
        by_a = {(str(r["group"]), str(r["paper"])): r for r in a}
        by_b = {(str(r["group"]), str(r["paper"])): r for r in b}
        keys = sorted(set(by_a.keys()) & set(by_b.keys()))
        xt = [float(by_a[k]["paper_total_mean"]) for k in keys]
        yt = [float(by_b[k]["paper_total_mean"]) for k in keys]
        xr = [float(by_a[k]["paper_repro_mean"]) for k in keys]
        yr = [float(by_b[k]["paper_repro_mean"]) for k in keys]
        out.append(
            {
                "group": group,
                "n": len(keys),
                "pearson_total": _pearson(xt, yt),
                "pearson_repro": _pearson(xr, yr),
            }
        )
    return out


def _plot_repro_box(rows: list[dict[str, Any]], out_png: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    models = sorted({str(r["model"]) for r in rows})
    for i, model in enumerate(models):
        ax = axes[i]
        p = [float(r["paper_repro_mean"]) for r in rows if r["model"] == model and r["group"] == "nat_protocols"]
        s = [float(r["paper_repro_mean"]) for r in rows if r["model"] == model and r["group"] == "nat_siblings"]
        ax.boxplot([p, s], labels=["protocols", "siblings"], showmeans=True)
        ax.set_title(model)
        ax.set_ylabel("Reproducibility score (paper mean)")
        for j, vals in enumerate([p, s], start=1):
            jitter_x = [j + (k - len(vals) / 2) * 0.01 for k in range(len(vals))]
            ax.scatter(jitter_x, vals, s=12, alpha=0.6)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=180)
    plt.close(fig)


def _plot_correlation(rows: list[dict[str, Any]], out_png: Path, score_key: str, ylabel: str) -> None:
    models = sorted({str(r["model"]) for r in rows})
    a_label, b_label = models[0], models[1]
    by_a = {(str(r["group"]), str(r["paper"])): r for r in rows if r["model"] == a_label}
    by_b = {(str(r["group"]), str(r["paper"])): r for r in rows if r["model"] == b_label}
    groups = ("nat_protocols", "nat_siblings")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for i, group in enumerate(groups):
        keys = sorted(k for k in set(by_a.keys()) & set(by_b.keys()) if k[0] == group)
        xs = [float(by_a[k][score_key]) for k in keys]
        ys = [float(by_b[k][score_key]) for k in keys]
        axes[i].scatter(xs, ys, s=24)
        corr = _pearson(xs, ys)
        axes[i].set_title(f"{group} (n={len(keys)}, r={_fmt(corr, 3)})")
        axes[i].set_xlabel(a_label)
        axes[i].set_ylabel(b_label if i == 0 else "")
        if xs and ys:
            low = min(xs + ys)
            high = max(xs + ys)
            axes[i].plot([low, high], [low, high], linestyle="--", linewidth=1)
    fig.suptitle(ylabel)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=180)
    plt.close(fig)


def _plot_v7_deltas(delta_rows: list[dict[str, Any]], out_png: Path) -> None:
    papers = [str(r["paper"]) for r in delta_rows]
    gpt_total = [float(r["gpt_total_delta_v7_minus_v5"]) for r in delta_rows]
    qwen_total = [float(r["qwen_total_delta_v7_minus_v5"]) for r in delta_rows]
    gpt_repro = [float(r["gpt_repro_delta_v7_minus_v5"]) for r in delta_rows]
    qwen_repro = [float(r["qwen_repro_delta_v7_minus_v5"]) for r in delta_rows]

    x = list(range(len(papers)))
    width = 0.18

    fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharex=True)
    axes[0].bar([i - 1.5 * width for i in x], gpt_total, width=width, label="GPT")
    axes[0].bar([i - 0.5 * width for i in x], qwen_total, width=width, label="Qwen")
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set_title("Total delta (v7 - v5)")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(papers, rotation=20, ha="right")
    axes[0].legend()

    axes[1].bar([i + 0.5 * width for i in x], gpt_repro, width=width, label="GPT")
    axes[1].bar([i + 1.5 * width for i in x], qwen_repro, width=width, label="Qwen")
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[1].set_title("Repro delta (v7 - v5)")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(papers, rotation=20, ha="right")
    axes[1].legend()

    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=180)
    plt.close(fig)


def _build_np3_delta(v5_rows: list[dict[str, Any]], v7_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    idx_v5 = {(str(r["model"]), str(r["paper"])): r for r in v5_rows if r["group"] == "nat_protocols" and r["paper"] in NP3_PAPERS}
    idx_v7 = {(str(r["model"]), str(r["paper"])): r for r in v7_rows if r["group"] == "nat_protocols" and r["paper"] in NP3_PAPERS}
    out: list[dict[str, Any]] = []
    for paper in NP3_PAPERS:
        gpt_old = idx_v5.get(("gpt-oss-120b", paper))
        gpt_new = idx_v7.get(("gpt-oss-120b", paper))
        q_old = idx_v5.get(("qwen3-next-80b-a3b-instruct-fp8", paper))
        q_new = idx_v7.get(("qwen3-next-80b-a3b-instruct-fp8", paper))
        if not all([gpt_old, gpt_new, q_old, q_new]):
            continue
        out.append(
            {
                "paper": paper,
                "gpt_total_v5": gpt_old["paper_total_mean"],
                "gpt_total_v7": gpt_new["paper_total_mean"],
                "gpt_total_delta_v7_minus_v5": gpt_new["paper_total_mean"] - gpt_old["paper_total_mean"],
                "gpt_repro_v5": gpt_old["paper_repro_mean"],
                "gpt_repro_v7": gpt_new["paper_repro_mean"],
                "gpt_repro_delta_v7_minus_v5": gpt_new["paper_repro_mean"] - gpt_old["paper_repro_mean"],
                "gpt_units_v5": gpt_old["unit_n"],
                "gpt_units_v7": gpt_new["unit_n"],
                "qwen_total_v5": q_old["paper_total_mean"],
                "qwen_total_v7": q_new["paper_total_mean"],
                "qwen_total_delta_v7_minus_v5": q_new["paper_total_mean"] - q_old["paper_total_mean"],
                "qwen_repro_v5": q_old["paper_repro_mean"],
                "qwen_repro_v7": q_new["paper_repro_mean"],
                "qwen_repro_delta_v7_minus_v5": q_new["paper_repro_mean"] - q_old["paper_repro_mean"],
                "qwen_units_v5": q_old["unit_n"],
                "qwen_units_v7": q_new["unit_n"],
            }
        )
    return out


def _write_report_ja(
    out_md: Path,
    bundle_dir: Path,
    v5_group: list[dict[str, Any]],
    v5_sig: list[dict[str, Any]],
    v5_corr: list[dict[str, Any]],
    np3_delta: list[dict[str, Any]],
) -> None:
    def gs(model: str, group: str, key: str) -> float | None:
        row = next((r for r in v5_group if r["model"] == model and r["group"] == group), None)
        return None if row is None else _to_float(row.get(key))

    def sig(model: str, key: str) -> float | None:
        row = next((r for r in v5_sig if r["model"] == model), None)
        return None if row is None else _to_float(row.get(key))

    def corr(group: str, key: str) -> float | None:
        row = next((r for r in v5_corr if r["group"] == group), None)
        return None if row is None else _to_float(row.get(key))

    gpt = "gpt-oss-120b"
    qwen = "qwen3-next-80b-a3b-instruct-fp8"

    gpt_total_delta = (gs(gpt, "nat_protocols", "total_mean") or 0.0) - (gs(gpt, "nat_siblings", "total_mean") or 0.0)
    gpt_repro_delta = (gs(gpt, "nat_protocols", "repro_mean") or 0.0) - (gs(gpt, "nat_siblings", "repro_mean") or 0.0)
    q_total_delta = (gs(qwen, "nat_protocols", "total_mean") or 0.0) - (gs(qwen, "nat_siblings", "total_mean") or 0.0)
    q_repro_delta = (gs(qwen, "nat_protocols", "repro_mean") or 0.0) - (gs(qwen, "nat_siblings", "repro_mean") or 0.0)

    gpt_np3_total = _mean([_to_float(r["gpt_total_delta_v7_minus_v5"]) or 0.0 for r in np3_delta])
    gpt_np3_repro = _mean([_to_float(r["gpt_repro_delta_v7_minus_v5"]) or 0.0 for r in np3_delta])
    q_np3_total = _mean([_to_float(r["qwen_total_delta_v7_minus_v5"]) or 0.0 for r in np3_delta])
    q_np3_repro = _mean([_to_float(r["qwen_repro_delta_v7_minus_v5"]) or 0.0 for r in np3_delta])

    lines: list[str] = []
    lines.append("# ENZYME v7 パイロット報告（JA）")
    lines.append("")
    lines.append("## 要旨")
    lines.append(
        "本報告は、ENZYMEのv7（unit抽出改善 + 追加スコア成分）を、(A) v5全件再スコア基準と、"
        "(B) v7実行済み3本（nat_protocols）で評価した。"
        "思想的背景としては、操作を最小核へ還元し履歴を保持するQUEENの設計思想（Nature Communications, 2022, s41467-022-30588-x）に準拠する。"
    )
    lines.append(
        f"v5全件の再集計では、GPT/Qwenともに protocols-siblings で total が正（GPT={_fmt(gpt_total_delta)}, Qwen={_fmt(q_total_delta)}）、"
        f"repro も正（GPT={_fmt(gpt_repro_delta)}, Qwen={_fmt(q_repro_delta)}）となり、"
        "以前観測されていた『protocolsのtotalが低い』傾向は現行スコア定義では再現しなかった。"
    )
    lines.append(
        f"一方、v7の3本比較では total は低下（GPT={_fmt(gpt_np3_total)}, Qwen={_fmt(q_np3_total)}; v7-v5）、"
        f"repro は上昇（GPT={_fmt(gpt_np3_repro)}, Qwen={_fmt(q_np3_repro)}）し、"
        "単位分割の圧縮と手順性重視スコアのトレードオフが明確化した。"
    )
    lines.append("")
    lines.append("## 1. 実装と評価設計")
    lines.append("- Core IR: `allocate/transfer/manipulate/run_device/observe/annotate/dispose`")
    lines.append("- Lowering: HL表現をCoreへ正規化（`src/enzyme/lowering.py`）")
    lines.append("- Validation: schema + registry + refs + graph")
    lines.append("- Score: `S_structural/S_param/S_vocab/S_ident/S_ambiguity/S_exec_env` に加えて `S_procedure/S_specificity/S_coverage`")
    lines.append("- Repro: strict profile（non-flowカテゴリの等重み平均 + flow viability gate）")
    lines.append("")
    lines.append("## 2. データと比較軸")
    lines.append("- v5全件: `results_pilot_v5_gpt_directcore`, `results_pilot_v5_qwen_fp8_directcore`")
    lines.append("- v7実行: `results_probe_v7_gpt_segfix_directcore_np3`, `results_probe_v7_qwen_segfix_directcore_np3`（nat_protocols 3本）")
    lines.append("- 3本: s41596-019-0213-z, s41596-021-00562-w, s41596-023-00827-6")
    lines.append("")
    lines.append("## 3. v5全件（再スコア後）の主結果")
    lines.append(
        f"- GPT total mean: protocols {_fmt(gs(gpt, 'nat_protocols', 'total_mean'))} vs siblings {_fmt(gs(gpt, 'nat_siblings', 'total_mean'))}"
    )
    lines.append(
        f"- GPT repro mean: protocols {_fmt(gs(gpt, 'nat_protocols', 'repro_mean'))} vs siblings {_fmt(gs(gpt, 'nat_siblings', 'repro_mean'))}"
    )
    lines.append(
        f"- Qwen total mean: protocols {_fmt(gs(qwen, 'nat_protocols', 'total_mean'))} vs siblings {_fmt(gs(qwen, 'nat_siblings', 'total_mean'))}"
    )
    lines.append(
        f"- Qwen repro mean: protocols {_fmt(gs(qwen, 'nat_protocols', 'repro_mean'))} vs siblings {_fmt(gs(qwen, 'nat_siblings', 'repro_mean'))}"
    )
    lines.append(
        f"- Repro有意差（GPT）: Mann-Whitney p={_fmt(sig(gpt, 'mannwhitney_p'), 6)}, Welch p={_fmt(sig(gpt, 'welch_p'), 6)}, d={_fmt(sig(gpt, 'cohen_d'))}"
    )
    lines.append(
        f"- Repro有意差（Qwen）: Mann-Whitney p={_fmt(sig(qwen, 'mannwhitney_p'), 6)}, Welch p={_fmt(sig(qwen, 'welch_p'), 6)}, d={_fmt(sig(qwen, 'cohen_d'))}"
    )
    lines.append(
        f"- モデル間相関: all(total={_fmt(corr('all', 'pearson_total'))}, repro={_fmt(corr('all', 'pearson_repro'))}), "
        f"protocols(total={_fmt(corr('nat_protocols', 'pearson_total'))}, repro={_fmt(corr('nat_protocols', 'pearson_repro'))})"
    )
    lines.append("")
    lines.append("## 4. v7（3本）差分")
    lines.append(f"- 平均差分 v7-v5 / GPT: total {_fmt(gpt_np3_total)}, repro {_fmt(gpt_np3_repro)}")
    lines.append(f"- 平均差分 v7-v5 / Qwen: total {_fmt(q_np3_total)}, repro {_fmt(q_np3_repro)}")
    lines.append("- 解釈: 分割の短片化は改善したが、Qwenではunit数圧縮が強く、totalの低下要因になった。")
    lines.append("- 解釈: repro上昇は、手順記述密度の改善と欠損表現減少の影響が大きい。")
    lines.append("")
    lines.append("## 5. 妥当性と限界")
    lines.append("- 現行指標はNat Protocols専用ルールではなく、journal名を入力に使わない。")
    lines.append("- ただし手順性・実行性を高く評価する設計バイアスは意図的に存在する。")
    lines.append("- v7はまだ3本評価で、群比較の主張はv5全件の補助線付きで解釈すべき。")
    lines.append("")
    lines.append("## 6. 結論")
    lines.append(
        "ENZYMEは、形式化品質と再現性品質を分離して定量できる実装段階に到達している。"
        "v7では『repro上昇とtotal低下のトレードオフ』が可視化され、"
        "次段は unit分割安定化とflow/coverage校正を同時に進めるのが合理的である。"
    )
    lines.append("")
    lines.append("## 図表")
    lines.append(f"- `{bundle_dir.name}/fig_v5_repro_box_jitter.png`")
    lines.append(f"- `{bundle_dir.name}/fig_v5_corr_total.png`")
    lines.append(f"- `{bundle_dir.name}/fig_v5_corr_repro.png`")
    lines.append(f"- `{bundle_dir.name}/fig_v7_np3_delta.png`")
    lines.append("")
    lines.append("## 主要CSV")
    lines.append(f"- `{bundle_dir.name}/v5_full_paper_scores.csv`")
    lines.append(f"- `{bundle_dir.name}/v5_group_stats.csv`")
    lines.append(f"- `{bundle_dir.name}/v5_repro_significance.csv`")
    lines.append(f"- `{bundle_dir.name}/v5_model_correlation.csv`")
    lines.append(f"- `{bundle_dir.name}/v7_np3_delta_vs_v5.csv`")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_report_en(
    out_md: Path,
    bundle_dir: Path,
    v5_group: list[dict[str, Any]],
    v5_sig: list[dict[str, Any]],
    v5_corr: list[dict[str, Any]],
    np3_delta: list[dict[str, Any]],
) -> None:
    def gs(model: str, group: str, key: str) -> float | None:
        row = next((r for r in v5_group if r["model"] == model and r["group"] == group), None)
        return None if row is None else _to_float(row.get(key))

    def sig(model: str, key: str) -> float | None:
        row = next((r for r in v5_sig if r["model"] == model), None)
        return None if row is None else _to_float(row.get(key))

    def corr(group: str, key: str) -> float | None:
        row = next((r for r in v5_corr if r["group"] == group), None)
        return None if row is None else _to_float(row.get(key))

    gpt = "gpt-oss-120b"
    qwen = "qwen3-next-80b-a3b-instruct-fp8"

    gpt_total_delta = (gs(gpt, "nat_protocols", "total_mean") or 0.0) - (gs(gpt, "nat_siblings", "total_mean") or 0.0)
    gpt_repro_delta = (gs(gpt, "nat_protocols", "repro_mean") or 0.0) - (gs(gpt, "nat_siblings", "repro_mean") or 0.0)
    q_total_delta = (gs(qwen, "nat_protocols", "total_mean") or 0.0) - (gs(qwen, "nat_siblings", "total_mean") or 0.0)
    q_repro_delta = (gs(qwen, "nat_protocols", "repro_mean") or 0.0) - (gs(qwen, "nat_siblings", "repro_mean") or 0.0)

    gpt_np3_total = _mean([_to_float(r["gpt_total_delta_v7_minus_v5"]) or 0.0 for r in np3_delta])
    gpt_np3_repro = _mean([_to_float(r["gpt_repro_delta_v7_minus_v5"]) or 0.0 for r in np3_delta])
    q_np3_total = _mean([_to_float(r["qwen_total_delta_v7_minus_v5"]) or 0.0 for r in np3_delta])
    q_np3_repro = _mean([_to_float(r["qwen_repro_delta_v7_minus_v5"]) or 0.0 for r in np3_delta])

    lines: list[str] = []
    lines.append("# ENZYME v7 Pilot Report (EN)")
    lines.append("")
    lines.append("## Abstract")
    lines.append(
        "This report evaluates ENZYME v7 (unit-segmentation hardening + expanded scoring) using two views: "
        "(A) full v5 corpus re-scored under the current scoring definition, and "
        "(B) v7 runs on 3 Nat Protocols papers. "
        "The conceptual basis follows the QUEEN design principle (Nature Communications, 2022, s41467-022-30588-x): "
        "reduce complex processes to a minimal trusted operation kernel while preserving process history."
    )
    lines.append(
        f"On full v5 re-scored data, both models show protocols-siblings positive deltas for total "
        f"(GPT={_fmt(gpt_total_delta)}, Qwen={_fmt(q_total_delta)}) and repro "
        f"(GPT={_fmt(gpt_repro_delta)}, Qwen={_fmt(q_repro_delta)}), which does not reproduce the old failure mode "
        "where protocols had lower total than siblings."
    )
    lines.append(
        f"On v7 3-paper deltas (v7-v5), total decreases (GPT={_fmt(gpt_np3_total)}, Qwen={_fmt(q_np3_total)}) "
        f"while repro increases (GPT={_fmt(gpt_np3_repro)}, Qwen={_fmt(q_np3_repro)}), "
        "revealing a trade-off between stricter procedural extraction and score composition."
    )
    lines.append("")
    lines.append("## 1. Implementation and Evaluation Design")
    lines.append("- Core IR: `allocate/transfer/manipulate/run_device/observe/annotate/dispose`")
    lines.append("- Lowering: normalize HL descriptions into Core (`src/enzyme/lowering.py`)")
    lines.append("- Validation: schema + registry + refs + graph checks")
    lines.append("- Scoring: legacy six axes plus `S_procedure/S_specificity/S_coverage`")
    lines.append("- Reproducibility: strict profile with equal-average non-flow total and flow viability gate")
    lines.append("")
    lines.append("## 2. Data and Comparison Axes")
    lines.append("- Full v5: `results_pilot_v5_gpt_directcore`, `results_pilot_v5_qwen_fp8_directcore`")
    lines.append("- v7 run: `results_probe_v7_gpt_segfix_directcore_np3`, `results_probe_v7_qwen_segfix_directcore_np3` (3 Nat Protocols papers)")
    lines.append("- Papers: s41596-019-0213-z, s41596-021-00562-w, s41596-023-00827-6")
    lines.append("")
    lines.append("## 3. Main Results on Full v5 (re-scored)")
    lines.append(
        f"- GPT total mean: protocols {_fmt(gs(gpt, 'nat_protocols', 'total_mean'))} vs siblings {_fmt(gs(gpt, 'nat_siblings', 'total_mean'))}"
    )
    lines.append(
        f"- GPT repro mean: protocols {_fmt(gs(gpt, 'nat_protocols', 'repro_mean'))} vs siblings {_fmt(gs(gpt, 'nat_siblings', 'repro_mean'))}"
    )
    lines.append(
        f"- Qwen total mean: protocols {_fmt(gs(qwen, 'nat_protocols', 'total_mean'))} vs siblings {_fmt(gs(qwen, 'nat_siblings', 'total_mean'))}"
    )
    lines.append(
        f"- Qwen repro mean: protocols {_fmt(gs(qwen, 'nat_protocols', 'repro_mean'))} vs siblings {_fmt(gs(qwen, 'nat_siblings', 'repro_mean'))}"
    )
    lines.append(
        f"- Repro significance (GPT): Mann-Whitney p={_fmt(sig(gpt, 'mannwhitney_p'), 6)}, Welch p={_fmt(sig(gpt, 'welch_p'), 6)}, d={_fmt(sig(gpt, 'cohen_d'))}"
    )
    lines.append(
        f"- Repro significance (Qwen): Mann-Whitney p={_fmt(sig(qwen, 'mannwhitney_p'), 6)}, Welch p={_fmt(sig(qwen, 'welch_p'), 6)}, d={_fmt(sig(qwen, 'cohen_d'))}"
    )
    lines.append(
        f"- Cross-model correlation: all(total={_fmt(corr('all', 'pearson_total'))}, repro={_fmt(corr('all', 'pearson_repro'))}), "
        f"protocols(total={_fmt(corr('nat_protocols', 'pearson_total'))}, repro={_fmt(corr('nat_protocols', 'pearson_repro'))})"
    )
    lines.append("")
    lines.append("## 4. v7 3-paper Delta Analysis")
    lines.append(f"- Mean v7-v5 delta / GPT: total {_fmt(gpt_np3_total)}, repro {_fmt(gpt_np3_repro)}")
    lines.append(f"- Mean v7-v5 delta / Qwen: total {_fmt(q_np3_total)}, repro {_fmt(q_np3_repro)}")
    lines.append("- Interpretation: short-fragment issues improved, but Qwen shows stronger unit compression in one paper, reducing total.")
    lines.append("- Interpretation: repro gain is consistent with higher procedural clarity and lower missingness.")
    lines.append("")
    lines.append("## 5. Validity and Limits")
    lines.append("- Metrics are not explicitly conditioned on journal label; no Nat Protocols-only feature exists in scoring.")
    lines.append("- There is intentional design bias toward procedural executability and reproducibility.")
    lines.append("- v7 claims remain preliminary because only 3 papers were re-run.")
    lines.append("")
    lines.append("## 6. Conclusion")
    lines.append(
        "ENZYME has reached a stage where structuring quality and reproducibility quality are separately quantifiable. "
        "v7 exposes a visible repro-total trade-off, providing actionable targets for the next cycle: "
        "stabilize unit segmentation while calibrating flow/coverage-sensitive scoring."
    )
    lines.append("")
    lines.append("## Figures")
    lines.append(f"- `{bundle_dir.name}/fig_v5_repro_box_jitter.png`")
    lines.append(f"- `{bundle_dir.name}/fig_v5_corr_total.png`")
    lines.append(f"- `{bundle_dir.name}/fig_v5_corr_repro.png`")
    lines.append(f"- `{bundle_dir.name}/fig_v7_np3_delta.png`")
    lines.append("")
    lines.append("## Main CSV outputs")
    lines.append(f"- `{bundle_dir.name}/v5_full_paper_scores.csv`")
    lines.append(f"- `{bundle_dir.name}/v5_group_stats.csv`")
    lines.append(f"- `{bundle_dir.name}/v5_repro_significance.csv`")
    lines.append(f"- `{bundle_dir.name}/v5_model_correlation.csv`")
    lines.append(f"- `{bundle_dir.name}/v7_np3_delta_vs_v5.csv`")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_slides_ja(out_md: Path) -> None:
    text = """# ENZYME v7 パイロット（JA）
## Nat Protocols / Nat Siblings と v7差分

- 評価対象: v5全件再スコア + v7 3本再実行
- モデル: gpt-oss-120b / qwen3-next-80b-a3b-instruct-fp8
- 背景思想: QUEEN (s41467-022-30588-x)

---
# 目的

- 形式化品質と再現性品質を分離評価できるか
- Nat Protocols特化バイアスなしに比較できるか
- v7変更が何を改善し何を悪化させたか

---
# 実装の核

- Core op最小化: allocate/transfer/manipulate/run_device/observe/annotate/dispose
- HL->Core Lowering + Validator + Scoring
- Reproはプロファイル駆動（equal-average non-flow）

---
# v5全件（再スコア）結果

- GPT: protocols total/repro が siblings より高い
- Qwen: protocols total/repro が siblings より高い
- 以前の「protocols total低下」傾向は現行定義では再現せず

---
# 統計と相関

- repro群差は両モデルで有意
- allではモデル相関が中程度以上
- protocols内の順位相関は低い

---
# v7（3本）差分

- total: GPT/Qwenともに低下
- repro: GPT/Qwenともに上昇
- Qwenはunit圧縮の影響が比較的大きい

---
# 解釈

- 分割品質改善は再現性軸に効く
- ただし過圧縮はcoverage/structuralを下げ得る
- 今回は trade-off の可視化に成功

---
# 結論と次アクション

- ENZYMEは実験手順の再現性監査として有用
- 次段:
- 1. unit分割安定化
- 2. flow/coverage校正
- 3. v7を全34本へ拡張
"""
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(text, encoding="utf-8")


def _write_slides_en(out_md: Path) -> None:
    text = """# ENZYME v7 Pilot (EN)
## Nat Protocols / Nat Siblings + v7 delta

- Scope: full v5 re-score + v7 rerun on 3 protocols papers
- Models: gpt-oss-120b / qwen3-next-80b-a3b-instruct-fp8
- Conceptual basis: QUEEN (s41467-022-30588-x)

---
# Objectives

- Separate structuring quality from reproducibility quality
- Check journal-specific bias risk
- Quantify what v7 improved and what degraded

---
# Implementation Core

- Minimal Core ops: allocate/transfer/manipulate/run_device/observe/annotate/dispose
- HL->Core lowering + validator + scoring
- Repro profile: equal-average over non-flow categories

---
# Full v5 Results (re-scored)

- Both models show protocols > siblings in total and repro
- Prior failure mode (protocols lower total) is not reproduced now
- Group gap remains strong on reproducibility

---
# Statistics and Correlation

- Repro group gap is significant for both models
- Cross-model correlation is moderate/high on all papers
- Within-protocol rank correlation is weak

---
# v7 Delta on 3 Papers

- Total: decreases for both models
- Repro: increases for both models
- Qwen shows larger unit-compression impact

---
# Interpretation

- Better segmentation quality helps reproducibility axis
- Over-compression can hurt coverage/structural score
- v7 successfully exposes the trade-off

---
# Conclusion and Next Steps

- ENZYME is useful as a reproducibility-audit framework
- Next:
- 1. stabilize segmentation behavior
- 2. calibrate flow/coverage-sensitive scoring
- 3. extend v7 rerun to all 34 papers
"""
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(text, encoding="utf-8")


def main() -> int:
    out_dir = Path("results_probe_v7_bundle")
    out_dir.mkdir(parents=True, exist_ok=True)

    v5_runs = [
        RunSpec("gpt-oss-120b", Path("results_pilot_v5_gpt_directcore")),
        RunSpec("qwen3-next-80b-a3b-instruct-fp8", Path("results_pilot_v5_qwen_fp8_directcore")),
    ]
    v7_runs = [
        RunSpec("gpt-oss-120b", Path("results_probe_v7_gpt_segfix_directcore_np3")),
        RunSpec("qwen3-next-80b-a3b-instruct-fp8", Path("results_probe_v7_qwen_segfix_directcore_np3")),
    ]

    v5_rows = []
    for run in v5_runs:
        v5_rows.extend(collect_paper_scores(run))
    v7_rows = []
    for run in v7_runs:
        v7_rows.extend(collect_paper_scores(run))

    v5_group = _group_stats(v5_rows)
    v5_sig = _significance_rows(v5_rows)
    v5_corr = _correlation_rows(v5_rows)
    v7_delta = _build_np3_delta(v5_rows, v7_rows)

    _write_csv(
        out_dir / "v5_full_paper_scores.csv",
        sorted(v5_rows, key=lambda r: (str(r["model"]), str(r["group"]), str(r["paper"]))),
        ["model", "group", "paper", "unit_n", "paper_total_mean", "paper_repro_mean"],
    )
    _write_csv(
        out_dir / "v7_np3_paper_scores.csv",
        sorted(v7_rows, key=lambda r: (str(r["model"]), str(r["group"]), str(r["paper"]))),
        ["model", "group", "paper", "unit_n", "paper_total_mean", "paper_repro_mean"],
    )
    _write_csv(
        out_dir / "v5_group_stats.csv",
        v5_group,
        ["model", "group", "paper_n", "total_mean", "total_median", "repro_mean", "repro_median", "units_mean", "units_sum"],
    )
    _write_csv(
        out_dir / "v5_repro_significance.csv",
        v5_sig,
        [
            "model",
            "protocols_n",
            "siblings_n",
            "protocols_mean_repro",
            "siblings_mean_repro",
            "delta_protocols_minus_siblings",
            "mannwhitney_u",
            "mannwhitney_p",
            "welch_t",
            "welch_p",
            "cohen_d",
        ],
    )
    _write_csv(
        out_dir / "v5_model_correlation.csv",
        v5_corr,
        ["group", "n", "pearson_total", "pearson_repro"],
    )
    _write_csv(
        out_dir / "v7_np3_delta_vs_v5.csv",
        v7_delta,
        [
            "paper",
            "gpt_total_v5",
            "gpt_total_v7",
            "gpt_total_delta_v7_minus_v5",
            "gpt_repro_v5",
            "gpt_repro_v7",
            "gpt_repro_delta_v7_minus_v5",
            "gpt_units_v5",
            "gpt_units_v7",
            "qwen_total_v5",
            "qwen_total_v7",
            "qwen_total_delta_v7_minus_v5",
            "qwen_repro_v5",
            "qwen_repro_v7",
            "qwen_repro_delta_v7_minus_v5",
            "qwen_units_v5",
            "qwen_units_v7",
        ],
    )

    _plot_repro_box(v5_rows, out_dir / "fig_v5_repro_box_jitter.png")
    _plot_correlation(v5_rows, out_dir / "fig_v5_corr_total.png", "paper_total_mean", "Cross-model correlation: total")
    _plot_correlation(v5_rows, out_dir / "fig_v5_corr_repro.png", "paper_repro_mean", "Cross-model correlation: repro")
    _plot_v7_deltas(v7_delta, out_dir / "fig_v7_np3_delta.png")

    _write_report_ja(out_dir / "ENZYME_v7_pilot_report_ja.md", out_dir, v5_group, v5_sig, v5_corr, v7_delta)
    _write_report_en(out_dir / "ENZYME_v7_pilot_report_en.md", out_dir, v5_group, v5_sig, v5_corr, v7_delta)
    _write_slides_ja(out_dir / "ENZYME_v7_pilot_slides_ja.md")
    _write_slides_en(out_dir / "ENZYME_v7_pilot_slides_en.md")

    v5_flow_rows = []
    for run in v5_runs:
        v5_flow_rows.extend(collect_flow_rows(run))
    _write_csv(
        out_dir / "v5_flow_paper_metrics.csv",
        sorted(v5_flow_rows, key=lambda r: (str(r["model"]), str(r["group"]), str(r["paper"]))),
        ["model", "group", "paper", "combined_isolated_rate", "combined_pass"],
    )

    print(f"wrote bundle: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
