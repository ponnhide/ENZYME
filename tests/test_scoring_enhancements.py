from enzyme.registry import Registry
from enzyme.scoring import score_core


def _validation_ok():
    return {"issues": []}


def _base_core(steps):
    return {
        "schema_version": "0.4",
        "ir_kind": "core",
        "metadata": {"title": "scoring test", "source": {"type": "unit"}},
        "resources": {"materials": [], "containers": [], "equipment": [], "samples": [], "data": []},
        "protocol": {
            "detail_level": 0,
            "steps": steps,
            "start_step_id": steps[0]["id"] if steps else "s1",
            "edges": [{"from": steps[0]["id"], "to": steps[0]["id"]}] if steps else [],
        },
    }


def test_annotate_heavy_protocol_gets_lower_procedure_and_coverage_scores():
    registry = Registry.from_file("registry/registry_v0_4.json")
    annotate_heavy = _base_core(
        [
            {"id": "s1", "op": "annotate", "params": {"note": "result summary"}},
            {"id": "s2", "op": "annotate", "params": {"note": "discussion sentence"}},
        ]
    )
    actionable = _base_core(
        [
            {
                "id": "s1",
                "op": "transfer",
                "params": {"amount": {"value": 10, "unit": "uL"}},
                "inputs": [{"kind": "sample", "id": "s_in"}],
                "outputs": [{"kind": "sample", "id": "s_out"}],
            },
            {
                "id": "s2",
                "op": "run_device",
                "params": {"device_kind": "incubator", "program": {"program_name": "P1"}, "device_ref": "eq1"},
                "inputs": [{"kind": "sample", "id": "s_out"}],
                "outputs": [{"kind": "sample", "id": "s_out2"}],
            },
        ]
    )

    score_a = score_core(annotate_heavy, _validation_ok(), registry)
    score_b = score_core(actionable, _validation_ok(), registry)

    assert score_a["scores"]["S_procedure"] < score_b["scores"]["S_procedure"]
    assert score_a["scores"]["S_coverage"] < score_b["scores"]["S_coverage"]


def test_unknown_parameter_values_reduce_specificity_score():
    registry = Registry.from_file("registry/registry_v0_4.json")
    concrete = _base_core(
        [
            {
                "id": "s1",
                "op": "transfer",
                "params": {"amount": {"value": 20, "unit": "uL"}, "source_ref": "a", "destination_ref": "b"},
                "inputs": [{"kind": "sample", "id": "a"}],
                "outputs": [{"kind": "sample", "id": "b"}],
            }
        ]
    )
    unknown = _base_core(
        [
            {
                "id": "s1",
                "op": "transfer",
                "params": {"amount": {"value": "unknown", "unit": "unknown"}, "source_ref": "a", "destination_ref": "b"},
                "inputs": [{"kind": "sample", "id": "a"}],
                "outputs": [{"kind": "sample", "id": "b"}],
            }
        ]
    )

    score_ok = score_core(concrete, _validation_ok(), registry)
    score_bad = score_core(unknown, _validation_ok(), registry)

    assert score_bad["scores"]["S_specificity"] < score_ok["scores"]["S_specificity"]
