from enzyme.lowering import lower_to_core


def test_lowering_macros():
    hl = {
        "schema_version": "0.4",
        "ir_kind": "hl",
        "metadata": {"title": "Macro Test", "source": {"type": "unit"}},
        "resources": {"materials": [], "containers": [], "equipment": [], "samples": [], "data": []},
        "protocol": {
            "detail_level": 0,
            "steps": [
                {"id": "s1", "op": "thermocycle", "params": {"profile_name": "p1"}},
                {"id": "s2", "op": "incubate", "params": {"program_name": "prog"}},
                {"id": "s3", "op": "centrifuge", "params": {"program_name": "spin"}},
                {
                    "id": "s4",
                    "op": "measure",
                    "params": {"device_kind": "plate_reader", "program_name": "read"},
                },
            ],
            "start_step_id": "s1",
            "edges": [
                {"from": "s1", "to": "s2"},
                {"from": "s2", "to": "s3"},
                {"from": "s3", "to": "s4"},
            ],
            "step_order": ["s1", "s2", "s3", "s4"],
        },
    }

    core = lower_to_core(hl)
    steps = {step["id"]: step for step in core["protocol"]["steps"]}

    assert steps["s1"]["op"] == "run_device"
    assert steps["s1"]["params"]["device_kind"] == "thermocycler"
    assert steps["s2"]["params"]["device_kind"] == "incubator"
    assert steps["s3"]["params"]["device_kind"] == "centrifuge"

    assert "s4.1" in steps
    assert "s4.2" in steps
    assert steps["s4.1"]["op"] == "run_device"
    assert steps["s4.2"]["op"] == "observe"

    edge_pairs = {(edge["from"], edge["to"]) for edge in core["protocol"]["edges"]}
    assert ("s3", "s4.1") in edge_pairs
    assert ("s4.1", "s4.2") in edge_pairs
    assert core["protocol"]["step_order"][-2:] == ["s4.1", "s4.2"]
