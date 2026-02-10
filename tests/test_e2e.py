from enzyme.importers.protocolsio import import_protocolsio
from enzyme.lowering import lower_to_core
from enzyme.registry import Registry
from enzyme.report import render_report
from enzyme.scoring import score_core
from enzyme.validator import validate_core
from enzyme.io import load_json


def test_end_to_end_fixture():
    fixture = load_json("fixtures/protocolsio_fixture.json")
    expected_hl = load_json("fixtures/expected_hl.json")
    expected_core = load_json("fixtures/expected_core.json")

    hl = import_protocolsio(fixture)
    assert hl == expected_hl

    core = lower_to_core(hl)
    assert core == expected_core

    registry = Registry.from_file("registry/registry_v0_4.json")
    validation = validate_core(core, "enzyme_ir/schema_core.json", registry)
    scores = score_core(core, validation, registry)
    report = render_report(core, validation, scores, fmt="md")

    assert "# ENZYME Report" in report
    assert "Validation" in report
