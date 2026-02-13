from enzyme.registry import Registry
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
