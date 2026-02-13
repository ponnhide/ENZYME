from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from enzyme.importers.protocolsio import import_protocolsio
from enzyme.io import load_json
from enzyme.lowering import lower_to_core
from enzyme.registry import Registry
from enzyme.report import render_report
from enzyme.scoring import score_core
from enzyme.validator import validate_core


def canonicalize(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: canonicalize(data[k]) for k in sorted(data)}
    if isinstance(data, list):
        return [canonicalize(x) for x in data]
    return data


def normalize_validation(validation: dict[str, Any]) -> dict[str, Any]:
    issues = validation.get("issues", [])
    validation = dict(validation)
    validation["issues"] = sorted(
        issues,
        key=lambda x: (
            x.get("severity", ""),
            x.get("code", ""),
            x.get("path", ""),
            x.get("message", ""),
        ),
    )
    return validation


def normalize_scores(scores: dict[str, Any]) -> dict[str, Any]:
    scores = dict(scores)
    top = scores.get("top_factors", {})
    scores["top_factors"] = {k: top[k] for k in sorted(top)}
    return scores


def write_text(path: Path, content: str, check: bool) -> bool:
    if path.exists():
        current = path.read_text(encoding="utf-8")
        if current == content:
            return False
    if check:
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return False


def write_json(path: Path, data: Any, check: bool) -> bool:
    text = json.dumps(canonicalize(data), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return write_text(path, text, check)


def generate_fixture(check: bool) -> list[str]:
    changed: list[str] = []
    registry = Registry.from_file(ROOT / "registry" / "registry_v0_4.json")

    fixture_input = load_json(ROOT / "fixtures" / "protocolsio_fixture.json")
    hl = import_protocolsio(fixture_input)
    core = lower_to_core(hl)
    validation = normalize_validation(validate_core(core, str(ROOT / "enzyme_ir" / "schema_core.json"), registry))
    scores = normalize_scores(score_core(core, validation, registry))
    report = render_report(core, validation, scores, fmt="md")

    targets = {
        ROOT / "fixtures" / "generated" / "protocolsio_fixture.hl.json": hl,
        ROOT / "fixtures" / "generated" / "protocolsio_fixture.core.json": core,
        ROOT / "fixtures" / "generated" / "protocolsio_fixture.validation.json": validation,
        ROOT / "fixtures" / "generated" / "protocolsio_fixture.scores.json": scores,
    }
    for path, data in targets.items():
        if write_json(path, data, check):
            changed.append(str(path.relative_to(ROOT)))

    if write_text(ROOT / "fixtures" / "generated" / "protocolsio_fixture.report.md", report, check):
        changed.append("fixtures/generated/protocolsio_fixture.report.md")

    expected_hl = load_json(ROOT / "fixtures" / "expected_hl.json")
    expected_core = load_json(ROOT / "fixtures" / "expected_core.json")
    if hl != expected_hl:
        raise SystemExit("Generated fixture HL does not match fixtures/expected_hl.json")
    if core != expected_core:
        raise SystemExit("Generated fixture Core does not match fixtures/expected_core.json")

    return changed


def generate_examples(check: bool) -> list[str]:
    changed: list[str] = []
    registry = Registry.from_file(ROOT / "registry" / "registry_v0_4.json")

    for hl_path in sorted((ROOT / "examples").glob("*_hl_v0_4.json")):
        base = hl_path.name.removesuffix("_hl_v0_4.json")
        hl = load_json(hl_path)
        core = lower_to_core(hl)
        validation = normalize_validation(validate_core(core, str(ROOT / "enzyme_ir" / "schema_core.json"), registry))
        scores = normalize_scores(score_core(core, validation, registry))
        report = render_report(core, validation, scores, fmt="md")

        outputs = {
            ROOT / "examples" / "generated" / f"{base}.core.json": core,
            ROOT / "examples" / "generated" / f"{base}.validation.json": validation,
            ROOT / "examples" / "generated" / f"{base}.scores.json": scores,
        }
        for path, data in outputs.items():
            if write_json(path, data, check):
                changed.append(str(path.relative_to(ROOT)))

        if write_text(ROOT / "examples" / "generated" / f"{base}.report.md", report, check):
            changed.append(f"examples/generated/{base}.report.md")

        expected_core_path = ROOT / "examples" / f"{base}_core_v0_4.json"
        if expected_core_path.exists():
            expected_core = load_json(expected_core_path)
            if core != expected_core:
                raise SystemExit(f"Generated core does not match {expected_core_path.relative_to(ROOT)}")

    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    changed = []
    changed.extend(generate_fixture(check=args.check))
    changed.extend(generate_examples(check=args.check))

    if args.check and changed:
        print("Generated artifacts are out of date:")
        for path in changed:
            print(f" - {path}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
