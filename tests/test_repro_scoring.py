from enzyme.registry import Registry
from enzyme.scoring import score_core


def _validation_ok():
    return {"issues": []}


def _profile():
    return {
        "profile_name": "unit_test_profile",
        "profile_version": "0.1",
        "categories": [
            {
                "id": "reagent_ident",
                "weight": 0.5,
                "scope": {"type": "resource", "resource_types": ["material"]},
                "required_fields": ["name", "vendor", "catalog_number", "lot_number"],
                "no_items_score": 0.0,
            },
            {
                "id": "device_run",
                "weight": 0.5,
                "scope": {"type": "step", "ops": ["run_device"]},
                "required_fields_by_op": {"run_device": ["device_kind", "program", "device_ref"]},
                "no_items_score": 0.0,
            },
        ],
    }


def _base_core():
    return {
        "schema_version": "0.4",
        "ir_kind": "core",
        "metadata": {"title": "t", "source": {"type": "unit"}},
        "resources": {
            "materials": [{"id": "m1", "name": "buffer", "vendor": "V", "catalog_number": "C1", "lot_number": "L1"}],
            "containers": [],
            "equipment": [],
            "samples": [],
            "data": [],
        },
        "protocol": {
            "detail_level": 1,
            "steps": [
                {
                    "id": "s1",
                    "op": "run_device",
                    "inputs": [],
                    "outputs": [],
                    "params": {"device_kind": "incubator", "program": {"program_name": "P1"}, "device_ref": "eq1"},
                }
            ],
            "start_step_id": "s1",
            "edges": [{"from": "s1", "to": "s1"}],
        },
    }


def test_reproducibility_extension_is_optional():
    registry = Registry.from_file("registry/registry_v0_4.json")
    scores = score_core(_base_core(), _validation_ok(), registry)
    assert "reproducibility" not in scores


def test_reproducibility_missing_fields_are_penalized():
    registry = Registry.from_file("registry/registry_v0_4.json")
    profile = _profile()

    good = _base_core()
    bad = _base_core()
    bad["resources"]["materials"][0].pop("lot_number")
    bad["protocol"]["steps"][0]["params"].pop("device_ref")

    good_scores = score_core(good, _validation_ok(), registry, reproducibility_profile=profile)
    bad_scores = score_core(bad, _validation_ok(), registry, reproducibility_profile=profile)

    assert good_scores["reproducibility"]["total_100"] > bad_scores["reproducibility"]["total_100"]
    assert bad_scores["reproducibility"]["missing_fields"]["lot_number"] >= 1
    assert bad_scores["reproducibility"]["missing_fields"]["run_device.device_ref"] >= 1


def test_recommended_fields_are_tracked_separately():
    registry = Registry.from_file("registry/registry_v0_4.json")
    profile = {
        "profile_name": "recommended_field_profile",
        "profile_version": "0.1",
        "categories": [
            {
                "id": "traceability",
                "weight": 1.0,
                "scope": {"type": "metadata"},
                "required_fields": ["title", "source"],
                "recommended_fields": ["protocol_id"],
                "recommended_weight": 0.25,
            }
        ],
    }
    core = _base_core()
    out = score_core(core, _validation_ok(), registry, reproducibility_profile=profile)
    detail = out["reproducibility"]["category_details"][0]

    assert detail["missing_checks"] == 0
    assert detail["missing_recommended_checks"] == 1
    reasons = {d["reason"] for d in out["reproducibility"]["deductions"]}
    assert "missing_recommended_fields" in reasons
