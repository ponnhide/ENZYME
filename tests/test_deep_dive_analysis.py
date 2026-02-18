import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from deep_dive_analysis import analyze_records, iter_score_records


def test_iter_score_records_keeps_missing_repro_as_none(tmp_path: Path):
    run_dir = tmp_path / "results"
    score_path = run_dir / "nat_protocols" / "paper_a" / "enzyme" / "unit_001.scores.json"
    score_path.parent.mkdir(parents=True, exist_ok=True)
    score_path.write_text(json.dumps({"total_100": 55, "scores": {}, "top_factors": {}}), encoding="utf-8")

    unit_txt = run_dir / "nat_protocols" / "paper_a" / "protocol_units" / "unit_001.txt"
    unit_txt.parent.mkdir(parents=True, exist_ok=True)
    unit_txt.write_text("PCR amplification", encoding="utf-8")

    records = iter_score_records(run_dir, patterns={})
    assert len(records) == 1
    assert records[0]["default_100"] == 55.0
    assert records[0]["repro_100"] is None


def test_analyze_records_handles_all_missing_repro():
    records = [
        {
            "group": "nat_protocols",
            "paper": "p1",
            "unit": "unit_001",
            "labels": [],
            "default_100": 60.0,
            "repro_100": None,
            "scores": {},
            "top_factors": {},
            "missing_fields": {},
            "category_scores": {},
            "deductions": [],
            "viability_pass": None,
        },
        {
            "group": "nat_protocols",
            "paper": "p2",
            "unit": "unit_001",
            "labels": [],
            "default_100": 62.0,
            "repro_100": None,
            "scores": {},
            "top_factors": {},
            "missing_fields": {},
            "category_scores": {},
            "deductions": [],
            "viability_pass": None,
        },
    ]
    deep_dive, _ = analyze_records(records)
    assert deep_dive["by_group_corr_default_repro"]["nat_protocols"] is None


def test_analyze_records_corr_uses_aligned_pairs():
    records = [
        {
            "group": "nat_protocols",
            "paper": "p1",
            "unit": "unit_001",
            "labels": [],
            "default_100": 10.0,
            "repro_100": 20.0,
            "scores": {},
            "top_factors": {},
            "missing_fields": {},
            "category_scores": {},
            "deductions": [],
            "viability_pass": True,
        },
        {
            "group": "nat_protocols",
            "paper": "p1",
            "unit": "unit_002",
            "labels": [],
            "default_100": 30.0,
            "repro_100": 40.0,
            "scores": {},
            "top_factors": {},
            "missing_fields": {},
            "category_scores": {},
            "deductions": [],
            "viability_pass": True,
        },
    ]
    deep_dive, _ = analyze_records(records)
    corr = deep_dive["by_group_corr_default_repro"]["nat_protocols"]
    assert corr is not None
    assert corr > 0.99
