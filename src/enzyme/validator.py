from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

try:
    import jsonschema  # type: ignore
except Exception:  # pragma: no cover
    jsonschema = None

try:
    import pint  # type: ignore
except Exception:  # pragma: no cover
    pint = None

from .io import load_json
from .registry import Registry, build_custom_registry


@dataclass
class Issue:
    code: str
    severity: str
    path: str
    message: str
    suggested_fix: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if self.suggested_fix is None:
            data.pop("suggested_fix")
        return data


def _path_to_string(path_parts: list[Any]) -> str:
    return "/" + "/".join(str(part) for part in path_parts)


def _collect_schema_issues(data: dict[str, Any], schema_path: str) -> list[Issue]:
    if jsonschema is None:
        # Offline/minimal fallback: no external validator available.
        return []

    schema = load_json(schema_path)
    validator = jsonschema.Draft202012Validator(schema)
    issues = []
    for error in validator.iter_errors(data):
        issues.append(
            Issue(
                code="SCHEMA_INVALID",
                severity="error",
                path=_path_to_string(list(error.path)),
                message=error.message,
            )
        )
    return issues


def _registry_lookup(custom_registry: dict[str, Any], key: str, name: str) -> bool:
    if key == "modalities":
        return name in custom_registry.get("modalities", set())
    return name in custom_registry.get(key, {})


def _get_program_requirements(
    registry: Registry, custom_registry: dict[str, Any], device_kind: str
) -> list[str]:
    if device_kind in registry.device_kinds:
        return registry.device_kinds[device_kind].get("required_program_keys", [])
    if device_kind in custom_registry.get("device_kinds", {}):
        return custom_registry["device_kinds"][device_kind].get("required_program_keys", [])
    return []


def _check_registry(step: dict[str, Any], detail_level: int, registry: Registry, custom: dict[str, Any]) -> list[Issue]:
    issues: list[Issue] = []

    def unknown_issue(code: str, path: str, value: str) -> Issue:
        severity = "error" if detail_level >= 1 else "warn"
        return Issue(
            code=code,
            severity=severity,
            path=path,
            message=f"Unknown registry value: {value}",
            suggested_fix="Declare custom vocabulary or use a registry term.",
        )

    if step.get("op") == "manipulate":
        action_kind = step.get("params", {}).get("action_kind")
        if action_kind and action_kind not in registry.action_kinds and not _registry_lookup(
            custom, "action_kinds", action_kind
        ):
            issues.append(unknown_issue("UNKNOWN_ACTION_KIND", f"/protocol/steps/{step.get('id')}/params/action_kind", action_kind))

    if step.get("op") == "run_device":
        device_kind = step.get("params", {}).get("device_kind")
        if device_kind and device_kind not in registry.device_kinds and not _registry_lookup(
            custom, "device_kinds", device_kind
        ):
            issues.append(unknown_issue("UNKNOWN_DEVICE_KIND", f"/protocol/steps/{step.get('id')}/params/device_kind", device_kind))
        if device_kind:
            required_keys = _get_program_requirements(registry, custom, device_kind)
            program = step.get("params", {}).get("program", {})
            for key in required_keys:
                if key not in program:
                    issues.append(
                        Issue(
                            code="MISSING_REQUIRED_PROGRAM_KEY",
                            severity="error",
                            path=f"/protocol/steps/{step.get('id')}/params/program",
                            message=f"Missing required program key '{key}' for device_kind '{device_kind}'.",
                            suggested_fix="Add required program keys.",
                        )
                    )

    if step.get("op") == "observe":
        modality = step.get("params", {}).get("modality")
        if modality and modality not in registry.modalities and not _registry_lookup(
            custom, "modalities", modality
        ):
            issues.append(unknown_issue("UNKNOWN_MODALITY", f"/protocol/steps/{step.get('id')}/params/modality", modality))
        features = step.get("params", {}).get("features", {})
        for feature_key in features.keys():
            if feature_key not in registry.observation_features and not _registry_lookup(
                custom, "observation_features", feature_key
            ):
                issues.append(
                    unknown_issue(
                        "UNKNOWN_OBSERVATION_FEATURE",
                        f"/protocol/steps/{step.get('id')}/params/features/{feature_key}",
                        feature_key,
                    )
                )

    return issues


def _check_refs(data: dict[str, Any]) -> list[Issue]:
    issues: list[Issue] = []
    protocol = data.get("protocol", {})
    steps = {step.get("id") for step in protocol.get("steps", [])}
    resources = data.get("resources", {})
    resource_map = {
        "material": {item.get("id") for item in resources.get("materials", [])},
        "container": {item.get("id") for item in resources.get("containers", [])},
        "equipment": {item.get("id") for item in resources.get("equipment", [])},
        "sample": {item.get("id") for item in resources.get("samples", [])},
        "data": {item.get("id") for item in resources.get("data", [])},
    }

    for edge in protocol.get("edges", []):
        if edge.get("from") not in steps or edge.get("to") not in steps:
            issues.append(
                Issue(
                    code="STEP_ID_NOT_FOUND",
                    severity="error",
                    path="/protocol/edges",
                    message=f"Edge references missing step: {edge}",
                )
            )

    for step in protocol.get("steps", []):
        for ref_list_key in ("inputs", "outputs", "tacit_refs"):
            for ref in step.get(ref_list_key, []) or []:
                kind = ref.get("kind")
                ref_id = ref.get("id")
                normalized_ref_id = (
                    ref_id.removeprefix(f"{kind}:") if isinstance(ref_id, str) and isinstance(kind, str) else ref_id
                )
                known_ids = resource_map.get(kind, set())
                if kind in resource_map and ref_id not in known_ids and normalized_ref_id not in known_ids:
                    if kind in {"data", "sample"}:
                        continue
                    issues.append(
                        Issue(
                            code="REF_NOT_FOUND",
                            severity="error",
                            path=f"/protocol/steps/{step.get('id')}/{ref_list_key}",
                            message=f"Reference not found: {kind}:{ref_id}",
                        )
                    )
    return issues


def _check_graph(protocol: dict[str, Any]) -> list[Issue]:
    issues: list[Issue] = []
    step_ids = {step.get("id") for step in protocol.get("steps", [])}
    start_step_id = protocol.get("start_step_id")
    if not start_step_id or start_step_id not in step_ids:
        issues.append(
            Issue(
                code="START_STEP_NOT_FOUND",
                severity="error",
                path="/protocol/start_step_id",
                message="start_step_id is missing or invalid.",
            )
        )
    if not protocol.get("edges"):
        issues.append(
            Issue(
                code="EDGE_INVALID",
                severity="error",
                path="/protocol/edges",
                message="Protocol requires at least one edge.",
            )
        )
    return issues


def _check_core_ops(protocol: dict[str, Any], registry: Registry) -> list[Issue]:
    issues: list[Issue] = []
    for step in protocol.get("steps", []):
        if step.get("op") not in registry.core_ops:
            issues.append(
                Issue(
                    code="UNKNOWN_CORE_OP",
                    severity="error",
                    path=f"/protocol/steps/{step.get('id')}/op",
                    message=f"Unknown core op: {step.get('op')}",
                )
            )
    return issues


def _check_units(data: dict[str, Any]) -> list[Issue]:
    issues: list[Issue] = []
    registry = pint.UnitRegistry() if pint is not None else None

    def parse_unit(unit: str) -> bool:
        if registry is not None:
            try:
                registry.parse_units(unit)
                return True
            except Exception:
                return False
        # offline fallback: allow symbolic/alphabetic unit strings
        return bool(unit and isinstance(unit, str))

    def visit(node: Any, path: list[str]) -> None:
        if isinstance(node, dict):
            if "unit" in node and isinstance(node.get("unit"), str):
                unit = node.get("unit")
                if not parse_unit(unit):
                    issues.append(
                        Issue(
                            code="UNIT_PARSE_ERROR",
                            severity="error",
                            path=_path_to_string(path + ["unit"]),
                            message=f"Invalid unit: {unit}",
                        )
                    )
            for key, value in node.items():
                visit(value, path + [key])
        elif isinstance(node, list):
            for index, item in enumerate(node):
                visit(item, path + [str(index)])

    visit(data, [])
    return issues


def _check_ranges(protocol: dict[str, Any], registry: Registry) -> list[Issue]:
    issues: list[Issue] = []
    for step in protocol.get("steps", []):
        if step.get("op") != "observe":
            continue
        features = step.get("params", {}).get("features", {})
        for key, value in features.items():
            constraints = registry.observation_features.get(key, {}).get("constraints", {})
            if not constraints:
                continue
            numeric_value = None
            if isinstance(value, dict) and "value" in value:
                numeric_value = value.get("value")
            elif isinstance(value, dict) and "range" in value:
                numeric_value = value.get("range", {}).get("min")
            elif isinstance(value, (int, float)):
                numeric_value = value
            if numeric_value is None:
                continue
            min_val = constraints.get("min")
            max_val = constraints.get("max")
            if min_val is not None and numeric_value < min_val:
                issues.append(
                    Issue(
                        code="VALUE_OUT_OF_RANGE",
                        severity="error",
                        path=f"/protocol/steps/{step.get('id')}/params/features/{key}",
                        message=f"Value below minimum {min_val} for {key}",
                    )
                )
            if max_val is not None and numeric_value > max_val:
                issues.append(
                    Issue(
                        code="VALUE_OUT_OF_RANGE",
                        severity="error",
                        path=f"/protocol/steps/{step.get('id')}/params/features/{key}",
                        message=f"Value above maximum {max_val} for {key}",
                    )
                )
    return issues


def validate_core(
    data: dict[str, Any], schema_path: str, registry: Registry
) -> dict[str, Any]:
    issues: list[Issue] = []
    issues.extend(_collect_schema_issues(data, schema_path))

    protocol = data.get("protocol", {})
    detail_level = protocol.get("detail_level", 0)
    custom_registry = build_custom_registry(data)

    issues.extend(_check_core_ops(protocol, registry))
    for step in protocol.get("steps", []):
        issues.extend(_check_registry(step, detail_level, registry, custom_registry))
    issues.extend(_check_refs(data))
    issues.extend(_check_graph(protocol))
    issues.extend(_check_units(data))
    issues.extend(_check_ranges(protocol, registry))

    has_error = any(issue.severity == "error" for issue in issues)
    return {
        "pass": not has_error,
        "issues": [issue.to_dict() for issue in issues],
    }
