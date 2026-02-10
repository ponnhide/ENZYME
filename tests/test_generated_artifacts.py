import subprocess
from pathlib import Path

from enzyme.io import load_json


def test_generated_artifacts_are_up_to_date():
    result = subprocess.run(
        ["python", "scripts/generate_artifacts.py", "--check"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_fixture_generated_matches_expected():
    generated_hl = load_json("fixtures/generated/protocolsio_fixture.hl.json")
    expected_hl = load_json("fixtures/expected_hl.json")
    generated_core = load_json("fixtures/generated/protocolsio_fixture.core.json")
    expected_core = load_json("fixtures/expected_core.json")

    assert generated_hl == expected_hl
    assert generated_core == expected_core


def test_examples_generated_core_match_reference_if_present():
    for hl_path in sorted(Path("examples").glob("*_hl_v0_4.json")):
        base = hl_path.name.removesuffix("_hl_v0_4.json")
        expected_core = Path("examples") / f"{base}_core_v0_4.json"
        generated_core = Path("examples/generated") / f"{base}.core.json"
        if expected_core.exists():
            assert load_json(generated_core) == load_json(expected_core)
