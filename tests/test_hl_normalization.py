import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from run_paper_benchmark import canonicalize_hl_ir


def test_canonicalize_hl_ir_moves_steps_and_builds_graph():
    raw = {
        "ir_version": "0.4",
        "kind": "enzyme_hl_ir",
        "meta": {"title": "t", "source": "src"},
        "entities": [{"id": "samp1", "type": "sample", "name": "sample"}],
        "steps": [
            {"id": "s1", "op": "transfer", "params": {"volume": "50 ul"}, "outputs": ["samp1"]},
            {"id": "s2", "op": "run_device", "params": {"device": "centrifuge", "duration": "2 min"}},
            {"id": "s3", "op": "run_device", "params": {"device_kind": "thermal cycler", "profile_name": "pcrA"}},
        ],
    }
    norm_log = []
    norm = canonicalize_hl_ir(raw, source_name="paper.pdf", unit_title="u", normalization_log=norm_log)

    assert norm["schema_version"] == "0.4"
    assert norm["ir_kind"] == "hl"
    assert "protocol" in norm
    assert norm["protocol"]["start_step_id"] == "s1"
    assert len(norm["protocol"]["steps"]) == 3
    assert len(norm["protocol"]["edges"]) >= 1

    step1 = norm["protocol"]["steps"][0]
    assert step1["op"] == "transfer"
    assert isinstance(step1["params"]["amount"], dict)
    assert step1["params"]["amount"]["unit"] == "ul"

    step2 = norm["protocol"]["steps"][1]
    assert step2["op"] == "run_device"
    assert step2["params"]["device_kind"] == "centrifuge"
    assert "program" in step2["params"]

    step3 = norm["protocol"]["steps"][2]
    assert step3["params"]["device_kind"] == "thermocycler"
    assert any("device_kind thermal cycler -> thermocycler" in x for x in norm_log)
