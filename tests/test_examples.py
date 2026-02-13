from pathlib import Path

from enzyme.registry import Registry
from enzyme.validator import validate_core
from enzyme.io import load_json


def test_example_core_validate():
    registry = Registry.from_file("registry/registry_v0_4.json")
    examples = Path("examples").glob("*_core_v0_4.json")
    for example in examples:
        core = load_json(example)
        validation = validate_core(core, "enzyme_ir/schema_core.json", registry)
        assert validation["pass"], f"{example} failed validation"
