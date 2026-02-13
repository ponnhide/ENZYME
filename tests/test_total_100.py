from enzyme.io import load_json
from enzyme.registry import Registry
from enzyme.scoring import compute_total_100, score_core
from enzyme.validator import validate_core


def test_compute_total_100_rounding_and_clamping():
    assert compute_total_100(0.0) == 0
    assert compute_total_100(1.0) == 100
    assert compute_total_100(0.734) == 73
    assert compute_total_100(0.735) == 74
    assert compute_total_100(-0.1) == 0
    assert compute_total_100(1.2) == 100
    assert compute_total_100(None) == 0
    assert compute_total_100(float("nan")) == 0


def test_score_output_contains_total_100_with_formula():
    core = load_json("fixtures/generated/protocolsio_fixture.core.json")
    registry = Registry.from_file("registry/registry_v0_4.json")
    validation = validate_core(core, "enzyme_ir/schema_core.json", registry)
    scores = score_core(core, validation, registry)

    assert "total" in scores
    assert "total_100" in scores
    assert isinstance(scores["total_100"], int)
    assert 0 <= scores["total_100"] <= 100

    raw = float(scores["total"]) * 100.0
    expected = max(0, min(100, int(raw + 0.5)))
    assert scores["total_100"] == expected
