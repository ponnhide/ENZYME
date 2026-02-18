from enzyme.scoring import check_flow_integrity, score_reproducibility


def test_flow_detects_missing_input_source():
    core = {
        "resources": {"materials": [], "containers": [], "equipment": [], "samples": [], "data": []},
        "protocol": {
            "steps": [
                {"id": "s1", "op": "transfer", "inputs": [{"kind": "sample", "id": "s_missing"}], "outputs": [{"kind": "sample", "id": "s1_out"}], "params": {}},
            ],
            "start_step_id": "s1",
            "edges": [{"from": "s1", "to": "s1"}],
        },
    }
    result = check_flow_integrity(core)
    codes = {x["code"] for x in result["issues"]}
    assert "FLOW_INPUT_WITHOUT_SOURCE" in codes


def test_flow_unused_output_not_penalized_when_final():
    core = {
        "resources": {"materials": [], "containers": [], "equipment": [], "samples": [], "data": []},
        "protocol": {
            "steps": [
                {"id": "s1", "op": "transfer", "inputs": [], "outputs": [{"kind": "sample", "id": "final_lib"}], "params": {}},
            ],
            "start_step_id": "s1",
            "edges": [{"from": "s1", "to": "s1"}],
            "outputs": [{"kind": "sample", "id": "final_lib"}],
        },
    }
    result = check_flow_integrity(core)
    codes = {x["code"] for x in result["issues"]}
    assert "FLOW_UNUSED_INTERMEDIATE" not in codes


def test_repro_separates_viability_gate_and_equal_non_flow_total():
    core = {
        "resources": {"materials": [], "containers": [], "equipment": [], "samples": [], "data": []},
        "protocol": {
            "steps": [
                {"id": "s1", "op": "transfer", "inputs": [{"kind": "sample", "id": "missing_in"}], "outputs": [{"kind": "sample", "id": "x"}], "params": {}},
            ],
            "start_step_id": "s1",
            "edges": [{"from": "s1", "to": "s1"}],
        },
        "metadata": {"title": "t", "source": {"type": "unit"}},
    }
    profile = {
        "profile_name": "p",
        "profile_version": "0.1",
        "categories": [
            {"id": "flow_integrity", "weight": 0.9, "scope": {"type": "flow"}},
            {"id": "traceability", "weight": 0.1, "scope": {"type": "metadata"}, "required_fields": ["title", "source"]},
        ],
    }
    out = score_reproducibility(core, profile)
    assert out["total_mode"] == "equal_average_non_flow"
    assert out["total"] == out["category_scores"]["traceability"]
    assert out["viability_gate"]["pass"] is False
