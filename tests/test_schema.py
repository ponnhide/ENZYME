from enzyme.io import load_json


def test_schema_files_exist_and_versions():
    schema_hl = load_json("enzyme_ir/schema_hl.json")
    schema_core = load_json("enzyme_ir/schema_core.json")

    assert schema_hl["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema_core["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema_hl["properties"]["schema_version"]["const"] == "0.4"
    assert schema_core["properties"]["schema_version"]["const"] == "0.4"
