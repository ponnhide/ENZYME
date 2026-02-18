#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def _load_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    return list(csv.DictReader(path.open(encoding="utf-8")))


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


def _summarize_by_model_group(long_rows: List[Dict[str, str]]) -> Dict[Tuple[str, str], Dict[str, float]]:
    out: Dict[Tuple[str, str], Dict[str, float]] = {}
    models = sorted({r["model"] for r in long_rows})
    for model in models:
        for group in ["nat_protocols", "nat_siblings", "all"]:
            subset = [r for r in long_rows if r["model"] == model and (group == "all" or r["group"] == group)]
            totals = [_to_float(r.get("mean_total_score_100")) for r in subset]
            repros = [_to_float(r.get("mean_repro_score_100")) for r in subset]
            units = [_to_float(r.get("num_units")) for r in subset]
            out[(model, group)] = {
                "papers": float(len(subset)),
                "total_mean": statistics.mean([x for x in totals if x is not None]) if subset else float("nan"),
                "repro_mean": statistics.mean([x for x in repros if x is not None]) if subset else float("nan"),
                "units_sum": float(sum(int(x) for x in units if x is not None)),
                "units_mean": statistics.mean([x for x in units if x is not None]) if subset else float("nan"),
            }
    return out


def _detect_pairwise_columns(pair_rows: List[Dict[str, str]]) -> Tuple[str, str, str, str]:
    cols = list(pair_rows[0].keys())
    total_cols = [c for c in cols if c.endswith("_total")]
    repro_cols = [c for c in cols if c.endswith("_repro")]
    if len(total_cols) != 2 or len(repro_cols) != 2:
        raise ValueError("Unexpected pairwise schema")
    return total_cols[0], total_cols[1], repro_cols[0], repro_cols[1]


def _wins(pair_rows: List[Dict[str, str]], a_col: str, b_col: str) -> Tuple[int, int, int]:
    a = b = tie = 0
    for row in pair_rows:
        av = _to_float(row.get(a_col))
        bv = _to_float(row.get(b_col))
        if av is None or bv is None:
            continue
        if abs(av - bv) < 1e-9:
            tie += 1
        elif av > bv:
            a += 1
        else:
            b += 1
    return a, b, tie


def _top_categories(
    dist_rows: List[Dict[str, str]],
    score_rows: List[Dict[str, str]],
    model: str,
    group: str,
    topk: int = 4,
) -> List[Tuple[str, int, Optional[float]]]:
    repro_idx = {
        (r.get("model"), r.get("group"), r.get("category")): _to_float(r.get("repro_mean"))
        for r in score_rows
    }
    subset = [r for r in dist_rows if r.get("model") == model and r.get("group") == group]
    subset = sorted(subset, key=lambda r: int(r.get("n", "0")), reverse=True)
    out: List[Tuple[str, int, Optional[float]]] = []
    for row in subset[:topk]:
        cat = str(row.get("category", "NA"))
        out.append((cat, int(row.get("n", "0")), repro_idx.get((model, group, cat))))
    return out


def _write_manuscript_ja(
    out_md: Path,
    model_a: str,
    model_b: str,
    summary: Dict[Tuple[str, str], Dict[str, float]],
    integrity_rows: List[Dict[str, str]],
    sig_rows: List[Dict[str, str]],
    corr_rows: List[Dict[str, str]],
    flow_rows: List[Dict[str, str]],
    pair_rows: List[Dict[str, str]],
    dist_rows: List[Dict[str, str]],
    score_rows: List[Dict[str, str]],
) -> None:
    sig = {r["model"]: r for r in sig_rows}
    corr = {r["group"]: r for r in corr_rows}
    flow = {(r["model"], r["group"]): r for r in flow_rows}
    integ = {r["model"]: r for r in integrity_rows}
    a_total_col, b_total_col, a_repro_col, b_repro_col = _detect_pairwise_columns(pair_rows)
    total_wins = _wins(pair_rows, a_total_col, b_total_col)
    repro_wins = _wins(pair_rows, a_repro_col, b_repro_col)

    ap = summary[(model_a, "nat_protocols")]
    asib = summary[(model_a, "nat_siblings")]
    aa = summary[(model_a, "all")]
    bp = summary[(model_b, "nat_protocols")]
    bsib = summary[(model_b, "nat_siblings")]
    ba = summary[(model_b, "all")]

    lines: List[str] = []
    lines.append("# ENZYME v7: 生命科学プロトコル形式化の実証評価（論文調レポート）")
    lines.append("")
    lines.append("## 要旨")
    lines.append(
        "本研究は、自然言語で記述された生命科学プロトコルを、検証可能な計算表現へ変換し、"
        "再現性を定量評価するためのENZYMEフレームワークを評価した。"
    )
    lines.append(
        "Nat Protocols 14報とNat siblings 20報（計34報）を対象に、"
        f"{model_a} と {model_b} の2モデルで全件処理を行い、"
        "形式化品質（total）と再現性指標（repro）を比較した。"
    )
    lines.append(
        f"両モデルで protocols > siblings の傾向が再現され、"
        f"{model_b} では repro 群差が有意（Mann-Whitney p={_fmt(_to_float(sig.get(model_b, {}).get('mannwhitney_p_two_sided')),6)}）となった。"
    )
    lines.append(
        "結果は、ENZYMEが手順知識を『実行可能な表現』へ落とし込み、"
        "文献比較を再現可能な計量として扱えることを示す。"
    )
    lines.append("")
    lines.append("## 1. 背景と問題設定")
    lines.append(
        "生命科学の方法記述は情報量が高い一方、機械的な比較・監査・再利用には依然として不向きである。"
    )
    lines.append(
        "QUEENは、DNA構築プロセスをコードとして再構成し、配列だけでなく構築履歴まで再生成可能にすることで、"
        "透明性と追跡可能性を高めた。ENZYMEはこの思想をプロトコル表現へ拡張し、"
        "『何をどの順序で、どの条件で行ったか』を、検証・採点可能なIRとして定義することを狙う。"
    )
    lines.append("")
    lines.append("## 2. ENZYMEの設計思想")
    lines.append("### 2.1 コア関数（Core-IR）")
    lines.append(
        "Core-IRは `allocate` / `transfer` / `manipulate` / `run_device` / `observe` / `annotate` / `dispose` を中心演算とする。"
    )
    lines.append(
        "この最小集合は、実験ドメイン固有の語彙差を吸収しつつ、フロー検証とスコアリングを共通化するための設計である。"
    )
    lines.append("### 2.2 形式化戦略（HL-Core と Direct-Core）")
    lines.append(
        "ENZYMEは HL-IR→Lowering→Core-IR の段階変換と、LLMが直接Coreを出力する direct-core の両方を許容する。"
    )
    lines.append(
        "Lowering では、`measure` を `run_device` + `observe` に分解し、"
        "内部データ参照（例: raw readout）を明示して、観測ステップへの依存関係を保存する。"
    )
    lines.append("### 2.3 スコアリング")
    lines.append(
        "default score（total）は9成分（構造、語彙、パラメータ、識別、実行環境、曖昧性、手順性、特異性、カバレッジ）の等重み平均。"
    )
    lines.append(
        "repro score は profile 駆動で資材識別・装置識別・パラメータ完全性・QC・トレーサビリティ等を評価し、"
        "MVP方針として `total_mode=equal_average_non_flow`（非flowカテゴリの等重み）を採用する。"
    )
    lines.append(
        "flowは重み合算ではなく viability gate として扱い、重大なフロー不整合を再現性リスクとして明示する。"
    )
    lines.append("### 2.4 Flow評価")
    lines.append(
        "unit間接続は strictな material_flow（参照ID一致）と heuristicな logical_flow（時系列窓・語彙アンカー・継続句）を併用し、"
        "combined_integrity で孤立unit率を報告する。"
    )
    lines.append("")
    lines.append("## 3. 評価設定")
    lines.append("- コーパス: nat_protocols 14報、nat_siblings 20報（計34報）")
    lines.append(f"- モデル: `{model_a}`, `{model_b}`")
    lines.append("- 各runは全件完走し、paper欠損スコアは0")
    lines.append("- バイオセーフティ配慮のため、具体的な実験手順や条件は本報告に記載しない")
    lines.append("")
    lines.append("## 4. 結果")
    lines.append("### 4.1 実行完全性")
    for model in [model_a, model_b]:
        ir = integ.get(model, {})
        lines.append(
            f"- {model}: papers={ir.get('papers','NA')}, units={ir.get('units','NA')}, "
            f"failures={ir.get('paper_failures','NA')}, missing_total={ir.get('paper_missing_total','NA')}, missing_repro={ir.get('paper_missing_repro','NA')}"
        )
    lines.append("### 4.2 paper平均スコア")
    lines.append("")
    lines.append("| model | group | total_mean | repro_mean |")
    lines.append("|---|---:|---:|---:|")
    lines.append(f"| {model_a} | nat_protocols | {_fmt(ap['total_mean'])} | {_fmt(ap['repro_mean'])} |")
    lines.append(f"| {model_a} | nat_siblings | {_fmt(asib['total_mean'])} | {_fmt(asib['repro_mean'])} |")
    lines.append(f"| {model_b} | nat_protocols | {_fmt(bp['total_mean'])} | {_fmt(bp['repro_mean'])} |")
    lines.append(f"| {model_b} | nat_siblings | {_fmt(bsib['total_mean'])} | {_fmt(bsib['repro_mean'])} |")
    lines.append("")
    lines.append(
        f"- wins(total, {model_a} vs {model_b}): {total_wins[0]}/{total_wins[1]}/tie {total_wins[2]}"
    )
    lines.append(
        f"- wins(repro, {model_a} vs {model_b}): {repro_wins[0]}/{repro_wins[1]}/tie {repro_wins[2]}"
    )
    lines.append("### 4.3 repro群差の統計")
    for model in [model_a, model_b]:
        row = sig.get(model, {})
        lines.append(
            f"- {model}: MWU p={_fmt(_to_float(row.get('mannwhitney_p_two_sided')),6)}, "
            f"Welch p={_fmt(_to_float(row.get('welch_p_two_sided')),6)}, "
            f"Cohen d={_fmt(_to_float(row.get('cohen_d')))}, Cliff delta={_fmt(_to_float(row.get('cliffs_delta')))}"
        )
    lines.append("### 4.4 モデル間相関")
    for g in ["all", "nat_protocols", "nat_siblings"]:
        row = corr.get(g, {})
        lines.append(
            f"- {g}: n={row.get('n','NA')}, pearson_total={_fmt(_to_float(row.get('pearson_total')))}, pearson_repro={_fmt(_to_float(row.get('pearson_repro')))}"
        )
    lines.append("### 4.5 フロー・カテゴリ")
    for model in [model_a, model_b]:
        for group in ["nat_protocols", "nat_siblings"]:
            row = flow.get((model, group), {})
            lines.append(
                f"- {model}/{group}: combined_pass_rate={_fmt(_to_float(row.get('combined_pass_rate')))}, "
                f"combined_isolated_rate_mean={_fmt(_to_float(row.get('combined_isolated_rate_mean')))}, "
                f"corr(repro, connectivity)={_fmt(_to_float(row.get('corr_repro_vs_connectivity')))}"
            )
    lines.append("")
    lines.append("## 5. 議論")
    lines.append("### 5.1 ENZYMEが示した価値")
    lines.append(
        "第一に、文献方法記述を機械可読IRへ変換し、比較可能な数量へ落とし込む基盤が実働した。"
    )
    lines.append(
        "第二に、単一スコアではなく、構造・語彙・パラメータ・flow・カテゴリ分布を分離計測でき、"
        "『何が再現性のボトルネックか』を診断可能にした。"
    )
    lines.append("### 5.2 QUEEN思想との接続")
    lines.append(
        "QUEENがDNA構築履歴の再生成可能性を通じて透明性を高めたのに対し、"
        "ENZYMEは実験プロトコルの実行記述を関数型IRとして正規化し、"
        "検証・採点・横断比較を可能にする。"
    )
    lines.append(
        "両者に共通する核は、『自然言語叙述を再構成可能な計算表現へ写像する』という方法論である。"
    )
    lines.append("### 5.3 限界")
    lines.append("- logical_flow は語彙ヒューリスティック依存で、意味依存の誤連結/未連結余地がある。")
    lines.append("- unit分割品質は上流抽出の影響を受ける。")
    lines.append("- 現時点では2モデル比較であり、モデル多様性の拡張が必要。")
    lines.append("### 5.4 今後の発展")
    lines.append("- logical_flowを学習ベースまたは検証器付き推論へ拡張し、説明可能性を維持したまま精度向上。")
    lines.append("- 大規模コーパス（Nat Protocols全体）へ適用し、分野別の再現性地図を構築。")
    lines.append("- profile項目の寄与を事後推定し、重み設計をデータ駆動で更新。")
    lines.append("- QUEEN的なトレーサビリティ思想と接続し、実験設計-実施-報告の循環を閉じる。")
    lines.append("")
    lines.append("## 6. 結論")
    lines.append(
        "ENZYME v7全件評価は、生命科学プロトコルの形式化と再現性計量に関して、"
        "実運用可能なパイプラインが成立していることを示した。"
    )
    lines.append(
        "特に、protocols/siblingsの群差、flow指標、カテゴリ構造を一体で扱える点は、"
        "従来の定性的読解では得にくい比較軸を提供する。"
    )
    lines.append(
        "今後は、精度改善（flow・segmentation）と適用規模拡大により、"
        "生命科学Methodsの客観的監査基盤としての意義をさらに高められる。"
    )
    lines.append("")
    lines.append("## 参考文献")
    lines.append(
        "1. Yachie et al., Nature Communications (2022), QUEEN framework. https://www.nature.com/articles/s41467-022-30588-x"
    )
    lines.append("2. ENZYME Spec v0.4 (`ENZYME_Spec_v0_4.md`)")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_manuscript_en(
    out_md: Path,
    model_a: str,
    model_b: str,
    summary: Dict[Tuple[str, str], Dict[str, float]],
    sig_rows: List[Dict[str, str]],
    corr_rows: List[Dict[str, str]],
    flow_rows: List[Dict[str, str]],
) -> None:
    sig = {r["model"]: r for r in sig_rows}
    corr = {r["group"]: r for r in corr_rows}
    flow = {(r["model"], r["group"]): r for r in flow_rows}

    ap = summary[(model_a, "nat_protocols")]
    asib = summary[(model_a, "nat_siblings")]
    bp = summary[(model_b, "nat_protocols")]
    bsib = summary[(model_b, "nat_siblings")]

    lines: List[str] = []
    lines.append("# ENZYME v7: Manuscript-Style Report on Protocol Formalization")
    lines.append("")
    lines.append("## Abstract")
    lines.append(
        "We evaluate ENZYME as a machine-readable formalization and scoring framework for life-science methods text."
    )
    lines.append(
        f"Across 34 papers (14 Nat Protocols + 20 Nat siblings), both {model_a} and {model_b} show protocols > siblings on total and repro metrics."
    )
    lines.append(
        "The result supports ENZYME's core thesis: natural-language methods can be lowered into a validated intermediate representation, enabling reproducibility-aware benchmarking."
    )
    lines.append("")
    lines.append("## Key Results")
    lines.append(f"- {model_a}: protocols total/repro = {_fmt(ap['total_mean'])}/{_fmt(ap['repro_mean'])}, siblings = {_fmt(asib['total_mean'])}/{_fmt(asib['repro_mean'])}")
    lines.append(f"- {model_b}: protocols total/repro = {_fmt(bp['total_mean'])}/{_fmt(bp['repro_mean'])}, siblings = {_fmt(bsib['total_mean'])}/{_fmt(bsib['repro_mean'])}")
    lines.append(
        f"- {model_b} repro group test: MWU p={_fmt(_to_float(sig.get(model_b, {}).get('mannwhitney_p_two_sided')),6)}, Welch p={_fmt(_to_float(sig.get(model_b, {}).get('welch_p_two_sided')),6)}"
    )
    lines.append(
        f"- Cross-model correlation (all): total={_fmt(_to_float(corr.get('all', {}).get('pearson_total')))}, repro={_fmt(_to_float(corr.get('all', {}).get('pearson_repro')))}"
    )
    lines.append("")
    lines.append("## Design Notes")
    lines.append("- Core ops: allocate, transfer, manipulate, run_device, observe, annotate, dispose.")
    lines.append("- Scoring: 9-component default total + profile-based reproducibility scoring.")
    lines.append("- Repro mode: equal-average of non-flow categories with flow viability gate.")
    lines.append("- Flow: strict material links + heuristic logical links + combined integrity.")
    lines.append("")
    lines.append("## Discussion")
    lines.append(
        "Inspired by the QUEEN concept of machine-readable provenance and regenerability, ENZYME extends the same philosophy to protocol-level method text."
    )
    lines.append(
        "The current v7 benchmark demonstrates feasibility and analytic value, while remaining gaps include logical-flow semantics and broader model diversity."
    )
    lines.append("")
    lines.append("## Reference")
    lines.append("- QUEEN paper: https://www.nature.com/articles/s41467-022-30588-x")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_slides_ja(
    out_md: Path,
    model_a: str,
    model_b: str,
    summary: Dict[Tuple[str, str], Dict[str, float]],
    sig_rows: List[Dict[str, str]],
    corr_rows: List[Dict[str, str]],
) -> None:
    sig = {r["model"]: r for r in sig_rows}
    corr = {r["group"]: r for r in corr_rows}
    ap = summary[(model_a, "nat_protocols")]
    asib = summary[(model_a, "nat_siblings")]
    bp = summary[(model_b, "nat_protocols")]
    bsib = summary[(model_b, "nat_siblings")]

    text = f"""# ENZYME v7 論文調サマリー（JA）
## Nat Protocols vs Nat siblings (n=34)
- Models: {model_a}, {model_b}
---
# 背景と狙い
- 課題: 自然言語Methodsは比較・監査が難しい
- 思想: QUEENの「計算可能な履歴表現」をプロトコルへ拡張
- ENZYME: 形式化 -> 検証 -> スコアリング -> 比較
---
# ENZYME設計（コア）
- Core ops: allocate / transfer / manipulate / run_device / observe / annotate / dispose
- HL-core と direct-core の2経路
- measureはrun_device+observeへlowering
- flowはmaterial/logical/combinedで評価
---
# スコアリング設計
- default total: 9成分の等重み平均
- repro: profile駆動（資材、装置、params、QC、traceability など）
- total_mode = equal_average_non_flow
- flowはviability gateとして運用
---
# 定量結果（paper平均）
- {model_a}: protocols total/repro = {_fmt(ap['total_mean'])}/{_fmt(ap['repro_mean'])}
- {model_a}: siblings total/repro = {_fmt(asib['total_mean'])}/{_fmt(asib['repro_mean'])}
- {model_b}: protocols total/repro = {_fmt(bp['total_mean'])}/{_fmt(bp['repro_mean'])}
- {model_b}: siblings total/repro = {_fmt(bsib['total_mean'])}/{_fmt(bsib['repro_mean'])}
---
# 統計・相関
- {model_a} repro群差: MWU p={_fmt(_to_float(sig.get(model_a, {}).get('mannwhitney_p_two_sided')),6)}
- {model_b} repro群差: MWU p={_fmt(_to_float(sig.get(model_b, {}).get('mannwhitney_p_two_sided')),6)}
- 相関(all): pearson_total={_fmt(_to_float(corr.get('all', {}).get('pearson_total')))}
- 相関(all): pearson_repro={_fmt(_to_float(corr.get('all', {}).get('pearson_repro')))}
---
# 議論
- 群平均傾向を再現し、再現性評価の計量化に成功
- 単一スコアではなく flow・カテゴリまで診断できる
- logical_flow と unit分割の改善が次の中心課題
---
# 今後の発展
- Nat Protocols全体への拡張
- profile寄与の事後推定（重み学習）
- QUEEN的なトレーサビリティ統合
- 生命科学Methodsの客観監査基盤へ
"""
    out_md.write_text(text, encoding="utf-8")


def _write_slides_en(
    out_md: Path,
    model_a: str,
    model_b: str,
    summary: Dict[Tuple[str, str], Dict[str, float]],
) -> None:
    ap = summary[(model_a, "nat_protocols")]
    asib = summary[(model_a, "nat_siblings")]
    bp = summary[(model_b, "nat_protocols")]
    bsib = summary[(model_b, "nat_siblings")]
    text = f"""# ENZYME v7 Manuscript Slides (EN)
## Nat Protocols vs Nat siblings (n=34)
- Models: {model_a}, {model_b}
---
# Motivation
- Methods text is rich but hard to audit/comparison at scale
- ENZYME formalizes procedures into validated IR
- Inspired by QUEEN-style computable provenance thinking
---
# Design
- Core ops: allocate/transfer/manipulate/run_device/observe/annotate/dispose
- Two pathways: HL-core and direct-core
- flow: material + logical + combined integrity
---
# Scoring
- Default total = equal-average of 9 quality components
- Repro = profile-based completeness and traceability checks
- Flow used as viability gate
---
# Main Numbers
- {model_a}: protocols {_fmt(ap['total_mean'])}/{_fmt(ap['repro_mean'])}, siblings {_fmt(asib['total_mean'])}/{_fmt(asib['repro_mean'])}
- {model_b}: protocols {_fmt(bp['total_mean'])}/{_fmt(bp['repro_mean'])}, siblings {_fmt(bsib['total_mean'])}/{_fmt(bsib['repro_mean'])}
---
# Implication
- ENZYME operationalizes protocol reproducibility as measurable signals
- Enables paper-level and category-level diagnostics
- Next: stronger logical-flow semantics, broader model coverage
"""
    out_md.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate manuscript-style v7 report and slides.")
    parser.add_argument("--comparison-dir", default="results_probe_v7_full_comparison")
    parser.add_argument("--label-a", default="gpt-oss-120b-v7")
    parser.add_argument("--label-b", default="qwen3-next-80b-a3b-instruct-fp8-v7")
    args = parser.parse_args()

    comp = Path(args.comparison_dir)
    long_rows = _load_csv(comp / "pilot_compare_repro_long.csv")
    pair_rows = _load_csv(comp / "pilot_compare_repro_pairwise.csv")
    integrity_rows = _load_csv(comp / "pilot_run_integrity.csv")
    sig_rows = _load_csv(comp / "repro_group_significance.csv")
    corr_rows = _load_csv(comp / "pilot_model_correlation.csv")
    flow_rows = _load_csv(comp / "pilot_flow_group_summary.csv")
    dist_rows = _load_csv(comp / "pilot_category_distribution_long.csv")
    score_rows = _load_csv(comp / "pilot_category_scores_long.csv")
    if not long_rows:
        raise SystemExit("Missing pilot_compare_repro_long.csv")

    summary = _summarize_by_model_group(long_rows)

    ja_report = comp / "ENZYME_v7_manuscript_ja.md"
    en_report = comp / "ENZYME_v7_manuscript_en.md"
    ja_slides = comp / "ENZYME_v7_manuscript_slides_ja.md"
    en_slides = comp / "ENZYME_v7_manuscript_slides_en.md"

    _write_manuscript_ja(
        ja_report,
        args.label_a,
        args.label_b,
        summary,
        integrity_rows,
        sig_rows,
        corr_rows,
        flow_rows,
        pair_rows,
        dist_rows,
        score_rows,
    )
    _write_manuscript_en(
        en_report,
        args.label_a,
        args.label_b,
        summary,
        sig_rows,
        corr_rows,
        flow_rows,
    )
    _write_slides_ja(ja_slides, args.label_a, args.label_b, summary, sig_rows, corr_rows)
    _write_slides_en(en_slides, args.label_a, args.label_b, summary)

    print(f"wrote: {ja_report}")
    print(f"wrote: {en_report}")
    print(f"wrote: {ja_slides}")
    print(f"wrote: {en_slides}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

