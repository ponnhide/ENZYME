from enzyme.registry import Registry
from enzyme.scoring import score_core
from enzyme.validator import validate_core


def make_core(detail_level: int):
    return {
        "schema_version": "0.4",
        "ir_kind": "core",
        "metadata": {"title": "Kernel Test", "source": {"type": "unit"}},
        "resources": {"materials": [], "containers": [], "equipment": [], "samples": [], "data": []},
        "protocol": {
            "detail_level": detail_level,
            "steps": [
                {
                    "id": "s1",
                    "op": "manipulate",
                    "params": {"action_kind": "unknown_action"},
                }
            ],
            "start_step_id": "s1",
            "edges": [{"from": "s1", "to": "s1"}],
        },
    }


def test_registry_detail_level_switch():
    registry = Registry.from_file("registry/registry_v0_4.json")
    low = validate_core(make_core(0), "enzyme_ir/schema_core.json", registry)
    high = validate_core(make_core(1), "enzyme_ir/schema_core.json", registry)

    low_issue = next(issue for issue in low["issues"] if issue["code"] == "UNKNOWN_ACTION_KIND")
    high_issue = next(issue for issue in high["issues"] if issue["code"] == "UNKNOWN_ACTION_KIND")

    assert low_issue["severity"] == "warn"
    assert high_issue["severity"] == "error"


def test_schema_normalization_accepts_expression_shorthand_and_null_source_fields():
    registry = Registry.from_file("registry/registry_v0_4.json")
    core = {
        "schema_version": "0.4",
        "ir_kind": "core",
        "metadata": {
            "title": "Normalization Test",
            "source": {"type": "manual", "id": None, "uri": None},
        },
        "resources": {
            "materials": [],
            "containers": [{"id": "ct:a", "type": "tube"}],
            "equipment": [],
            "samples": [],
            "data": [],
        },
        "protocol": {
            "detail_level": 0,
            "steps": [
                {"id": "s1", "op": "annotate", "params": {"note": "start"}},
                {
                    "id": "s2",
                    "op": "observe",
                    "inputs": [{"kind": "container", "id": "ct:a"}],
                    "outputs": [{"kind": "data", "id": "data:obs0"}],
                    "params": {"modality": "microscope", "features": {"confluency": None}},
                },
            ],
            "start_step_id": "s1",
            "edges": [
                {"from": "s1", "to": "s2"},
                {
                    "from": "s2",
                    "to": "s2",
                    "condition": {
                        "op": "ge",
                        "left": {"ref": "data:obs0.features.confluency"},
                        "right": {"symbol": "THRESH"},
                    },
                },
            ],
        },
    }
    validation = validate_core(core, "enzyme_ir/schema_core.json", registry)
    assert validation["pass"], validation["issues"]


def test_observe_features_list_does_not_crash_validation_or_scoring():
    registry = Registry.from_file("registry/registry_v0_4.json")
    core = {
        "schema_version": "0.4",
        "ir_kind": "core",
        "metadata": {
            "title": "Observe Features List",
            "source": {"type": "unit"},
        },
        "resources": {
            "materials": [],
            "containers": [{"id": "ct:a", "type": "tube"}],
            "equipment": [],
            "samples": [],
            "data": [],
        },
        "protocol": {
            "detail_level": 0,
            "steps": [
                {
                    "id": "s1",
                    "op": "observe",
                    "inputs": [{"kind": "container", "id": "ct:a"}],
                    "outputs": [],
                    "params": {
                        "modality": "microscope",
                        "features": ["confluency"],
                    },
                }
            ],
            "start_step_id": "s1",
            "edges": [{"from": "s1", "to": "s1"}],
        },
    }
    validation = validate_core(core, "enzyme_ir/schema_core.json", registry)
    assert validation["pass"], validation["issues"]
    scores = score_core(core, validation, registry)
    assert isinstance(scores.get("total"), float)
