import jsonschema

from enzyme.io import load_json


def test_schema_hl_and_core():
    schema_hl = load_json("enzyme_ir/schema_hl.json")
    schema_core = load_json("enzyme_ir/schema_core.json")
    hl = load_json("fixtures/expected_hl.json")
    core = load_json("fixtures/expected_core.json")

    jsonschema.Draft202012Validator(schema_hl).validate(hl)
    jsonschema.Draft202012Validator(schema_core).validate(core)
