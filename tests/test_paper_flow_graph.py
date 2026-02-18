import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from run_paper_benchmark import UnitResult, build_paper_flow_graph


def _write_core(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_material_flow_connects_units_when_refs_match(tmp_path: Path):
    enzyme_dir = tmp_path / "enzyme"
    _write_core(
        enzyme_dir / "unit_001.core.json",
        {
            "protocol": {
                "steps": [
                    {
                        "id": "s1",
                        "op": "transfer",
                        "inputs": [],
                        "outputs": [{"kind": "sample", "id": "s_lib"}],
                        "params": {},
                    }
                ],
                "edges": [],
            }
        },
    )
    _write_core(
        enzyme_dir / "unit_002.core.json",
        {
            "protocol": {
                "steps": [
                    {
                        "id": "s1",
                        "op": "run_device",
                        "inputs": [{"kind": "sample", "id": "s_lib"}],
                        "outputs": [{"kind": "data", "id": "d1"}],
                        "params": {},
                    }
                ],
                "edges": [],
            }
        },
    )

    units = [
        {"title": "library prep", "text": "prepare sample library"},
        {"title": "sequencing", "text": "sequence prepared library"},
    ]
    results = [
        UnitResult(unit_id="unit_001", title="library prep", score_100=70, status="ok"),
        UnitResult(unit_id="unit_002", title="sequencing", score_100=72, status="ok"),
    ]

    graph = build_paper_flow_graph(units, results, enzyme_dir)
    assert len(graph["material_flow"]["inter_unit_graph"]["edges"]) == 1
    assert graph["material_flow"]["integrity"]["isolated_unit_count"] == 0
    assert graph["combined_integrity"]["isolated_unit_count"] == 0


def test_logical_flow_links_without_material_refs(tmp_path: Path):
    enzyme_dir = tmp_path / "enzyme"
    _write_core(
        enzyme_dir / "unit_001.core.json",
        {
            "protocol": {
                "steps": [{"id": "s1", "op": "run_device", "inputs": [], "outputs": [], "params": {}}],
                "edges": [],
            }
        },
    )
    _write_core(
        enzyme_dir / "unit_002.core.json",
        {
            "protocol": {
                "steps": [{"id": "s1", "op": "transfer", "inputs": [], "outputs": [], "params": {}}],
                "edges": [],
            }
        },
    )

    units = [
        {
            "title": "Reporter amplicon generation",
            "text": "HEK293 reporter cells were processed to generate amplicon library.",
        },
        {
            "title": "PCR of reporter amplicon",
            "text": "Then reporter amplicon library was amplified by PCR from harvested cells.",
        },
    ]
    results = [
        UnitResult(unit_id="unit_001", title="u1", score_100=65, status="ok"),
        UnitResult(unit_id="unit_002", title="u2", score_100=68, status="ok"),
    ]

    graph = build_paper_flow_graph(units, results, enzyme_dir)
    assert len(graph["material_flow"]["inter_unit_graph"]["edges"]) == 0
    assert len(graph["logical_flow"]["inter_unit_graph"]["edges"]) >= 1
    assert graph["logical_flow"]["integrity"]["isolated_unit_count"] < 2
    assert graph["combined_integrity"]["isolated_unit_count"] < 2
