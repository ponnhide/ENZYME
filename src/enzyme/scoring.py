from __future__ import annotations

from collections import Counter
from math import isnan
from typing import Any

from .registry import Registry, build_custom_registry


def _issue_factors(issues: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(issue["code"] for issue in issues)
    return dict(counts)


def _score_structural(issues: list[dict[str, Any]]) -> float:
    if any(issue["severity"] == "error" for issue in issues):
        return 0.0
    warn_count = sum(1 for issue in issues if issue["severity"] == "warn")
    info_count = sum(1 for issue in issues if issue["severity"] == "info")
    penalty = min(1.0, warn_count * 0.05 + info_count * 0.01)
    return round(1.0 - penalty, 3)


def _score_param(protocol: dict[str, Any]) -> float:
    required = 0
    present = 0
    for step in protocol.get("steps", []):
        if step.get("op") == "transfer":
            required += 1
            if isinstance(step.get("params", {}).get("amount"), dict):
                present += 1
        if step.get("op") == "run_device":
            required += 1
            if step.get("params", {}).get("program"):
                present += 1
        if step.get("op") == "observe":
            required += 1
            if step.get("params", {}).get("features") is not None:
                present += 1
    if required == 0:
        return 1.0
    return round(present / required, 3)


def _score_vocab(protocol: dict[str, Any], registry: Registry, custom: dict[str, Any]) -> float:
    total = 0
    known = 0
    for step in protocol.get("steps", []):
        if step.get("op") == "manipulate":
            total += 1
            action_kind = step.get("params", {}).get("action_kind")
            if action_kind in registry.action_kinds or action_kind in custom.get("action_kinds", {}):
                known += 1
        if step.get("op") == "run_device":
            total += 1
            device_kind = step.get("params", {}).get("device_kind")
            if device_kind in registry.device_kinds or device_kind in custom.get("device_kinds", {}):
                known += 1
        if step.get("op") == "observe":
            modality = step.get("params", {}).get("modality")
            total += 1
            if modality in registry.modalities or modality in custom.get("modalities", set()):
                known += 1
            features = step.get("params", {}).get("features", {})
            for key in _observe_feature_keys(features):
                total += 1
                if key in registry.observation_features or key in custom.get("observation_features", {}):
                    known += 1
    if total == 0:
        return 1.0
    return round(known / total, 3)


def _observe_feature_keys(features: Any) -> list[str]:
    if isinstance(features, dict):
        return [key for key in features.keys() if isinstance(key, str)]
    if isinstance(features, list):
        keys: list[str] = []
        for item in features:
            if isinstance(item, str) and item.strip():
                keys.append(item.strip())
                continue
            if isinstance(item, dict):
                name = item.get("name")
                if isinstance(name, str) and name.strip():
                    keys.append(name.strip())
        return keys
    return []


def _score_ident(resources: dict[str, Any]) -> float:
    items = []
    for key in ("materials", "equipment", "containers", "samples"):
        items.extend(resources.get(key, []) or [])
    if not items:
        return 0.5
    hits = 0
    for item in items:
        if item.get("vendor") or item.get("catalog_number") or item.get("model"):
            hits += 1
        if item.get("identifiers"):
            hits += 1
    return round(min(1.0, hits / (len(items) * 2)), 3)


def _score_ambiguity(data: dict[str, Any]) -> float:
    ambiguous = 0
    total = 0

    def visit(node: Any) -> None:
        nonlocal ambiguous, total
        if isinstance(node, dict):
            if "symbol" in node:
                ambiguous += 1
            if "range" in node:
                ambiguous += 1
            if "value" in node or "symbol" in node or "range" in node:
                total += 1
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for item in node:
                visit(item)

    visit(data)
    if total == 0:
        return 1.0
    return round(max(0.0, 1.0 - ambiguous / total), 3)


def _score_exec_env(data: dict[str, Any]) -> float:
    protocol = data.get("protocol", {})
    steps = protocol.get("steps", [])
    run_devices = [step for step in steps if step.get("op") == "run_device"]
    if not run_devices:
        return 0.5
    with_ref = sum(1 for step in run_devices if step.get("params", {}).get("device_ref"))
    containers = data.get("resources", {}).get("containers", [])
    has_capacity = any(container.get("max_volume") for container in containers)
    score = with_ref / max(1, len(run_devices))
    if has_capacity:
        score = min(1.0, score + 0.2)
    return round(score, 3)


_ACTIONABLE_OPS = {"transfer", "manipulate", "run_device", "observe", "dispose"}
_PROCEDURE_HINT_OPS = _ACTIONABLE_OPS | {"allocate"}
_SPECIFICITY_SKIP_KEYS = {
    "note",
    "description",
    "rationale",
    "comment",
    "message",
    "label",
    "title",
}
_UNKNOWN_TOKENS = {
    "unknown",
    "n/a",
    "na",
    "none",
    "not specified",
    "unspecified",
    "tbd",
    "to be determined",
}


def _score_procedure(protocol: dict[str, Any]) -> float:
    steps = [s for s in protocol.get("steps", []) if isinstance(s, dict)]
    if not steps:
        return 0.0

    procedure_like = sum(1 for step in steps if str(step.get("op", "")).strip() in _PROCEDURE_HINT_OPS)
    actionable = sum(1 for step in steps if str(step.get("op", "")).strip() in _ACTIONABLE_OPS)
    base = procedure_like / max(1, len(steps))
    if actionable == 0:
        base = min(base, 0.4)
    return round(max(0.0, min(1.0, base)), 3)


def _is_unknown_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        lowered = value.strip().lower()
        if not lowered:
            return True
        if lowered in _UNKNOWN_TOKENS:
            return True
        if lowered.startswith("unknown"):
            return True
        return False
    if isinstance(value, dict):
        val = value.get("value")
        unit = value.get("unit")
        if isinstance(val, str) and _is_unknown_value(val):
            return True
        if isinstance(unit, str) and _is_unknown_value(unit):
            return True
        if val is None and unit is None:
            return True
    return False


def _iter_specificity_values(node: Any) -> list[Any]:
    if isinstance(node, dict):
        values: list[Any] = []
        for key, value in node.items():
            if str(key).lower() in _SPECIFICITY_SKIP_KEYS:
                continue
            if isinstance(value, (dict, list)):
                values.extend(_iter_specificity_values(value))
            else:
                values.append(value)
        return values
    if isinstance(node, list):
        values: list[Any] = []
        for item in node:
            values.extend(_iter_specificity_values(item))
        return values
    return [node]


def _score_specificity(data: dict[str, Any]) -> float:
    values: list[Any] = []
    protocol = data.get("protocol", {})
    for step in protocol.get("steps", []):
        if not isinstance(step, dict):
            continue
        params = step.get("params", {})
        if isinstance(params, dict):
            values.extend(_iter_specificity_values(params))
    resources = data.get("resources", {})
    if isinstance(resources, dict):
        for key in ("materials", "containers", "equipment", "samples"):
            for item in resources.get(key, []) or []:
                if isinstance(item, dict):
                    values.extend(_iter_specificity_values(item))

    filtered = [v for v in values if isinstance(v, (str, int, float, dict)) or v is None]
    if not filtered:
        return 0.5
    unknown = sum(1 for value in filtered if _is_unknown_value(value))
    score = 1.0 - (unknown / max(1, len(filtered)))
    return round(max(0.0, min(1.0, score)), 3)


def _score_coverage(protocol: dict[str, Any]) -> float:
    steps = [s for s in protocol.get("steps", []) if isinstance(s, dict)]
    if not steps:
        return 0.0

    actionable = 0
    annotate = 0
    other = 0
    for step in steps:
        op = str(step.get("op", "")).strip()
        if op in _ACTIONABLE_OPS:
            actionable += 1
        elif op == "annotate":
            annotate += 1
        else:
            other += 1
    if actionable == 0:
        return 0.0
    denom = actionable + (0.75 * annotate) + (0.25 * other)
    return round(max(0.0, min(1.0, actionable / max(1e-9, denom))), 3)


def _compute_total(scores: dict[str, float]) -> float:
    if not scores:
        return 0.0
    return round(sum(scores.values()) / len(scores), 3)


def compute_total_100(total: Any) -> int:
    if not isinstance(total, (int, float)):
        return 0
    if isinstance(total, float) and isnan(total):
        return 0

    raw = float(total) * 100.0
    total_100 = int(raw + 0.5)
    return max(0, min(100, total_100))


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _canonical_action_kind(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    v = value.strip().lower().replace("-", "_").replace(" ", "_")
    synonyms = {
        "seal": "label",
        "labeling": "label",
        "resuspension": "resuspend",
        "wash": "rinse",
        "washing": "rinse",
    }
    return synonyms.get(v, v)


def _canonical_device_kind(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    v = value.strip().lower().replace("-", "_").replace(" ", "_")
    synonyms = {
        "thermal_cycler": "thermocycler",
        "pcr_machine": "thermocycler",
        "qpcr_instrument": "amplicon_readout_system",
        "sequencer": "amplicon_readout_system",
        "illumina_sequencer": "amplicon_readout_system",
        "gel_electrophoresis": "imager",
    }
    return synonyms.get(v, v)


def _canonical_modality(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    v = value.strip().lower().replace("-", "_").replace(" ", "_")
    synonyms = {
        "instrument": "instrument_readout",
        "qpcr": "instrument_readout",
        "gel_band": "visual",
    }
    return synonyms.get(v, v)


def _normalize_resources(data: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    resources = _safe_dict(data.get("resources"))
    normalized: dict[str, list[dict[str, Any]]] = {
        "material": [x for x in _safe_list(resources.get("materials")) if isinstance(x, dict)],
        "sample": [x for x in _safe_list(resources.get("samples")) if isinstance(x, dict)],
        "container": [x for x in _safe_list(resources.get("containers")) if isinstance(x, dict)],
        "equipment": [x for x in _safe_list(resources.get("equipment")) if isinstance(x, dict)],
    }

    type_map = {
        "reagent": "material",
        "material": "material",
        "sample": "sample",
        "container": "container",
        "instrument": "equipment",
        "equipment": "equipment",
        "device": "equipment",
    }
    for entity in _safe_list(data.get("entities")):
        if not isinstance(entity, dict):
            continue
        mapped = type_map.get(str(entity.get("type", "")).lower())
        if mapped:
            normalized[mapped].append(entity)
    return normalized


def _normalize_steps(data: dict[str, Any]) -> list[dict[str, Any]]:
    protocol = _safe_dict(data.get("protocol"))
    steps = _safe_list(protocol.get("steps"))
    if not steps:
        steps = _safe_list(data.get("steps"))
    out = [step for step in steps if isinstance(step, dict)]
    for step in out:
        params = _safe_dict(step.get("params"))
        if step.get("op") == "manipulate" and "action_kind" in params:
            params["action_kind"] = _canonical_action_kind(params.get("action_kind"))
        if step.get("op") == "run_device" and "device_kind" in params:
            params["device_kind"] = _canonical_device_kind(params.get("device_kind"))
        if step.get("op") == "observe" and "modality" in params:
            params["modality"] = _canonical_modality(params.get("modality"))
        step["params"] = params
    return out


def _lookup_field_value(node: dict[str, Any], field: str) -> Any:
    parts = field.split(".")
    candidates: list[Any] = [node]

    if isinstance(node.get("params"), dict):
        candidates.append(node["params"])
    if isinstance(node.get("properties"), dict):
        candidates.append(node["properties"])
    if isinstance(node.get("metadata"), dict):
        candidates.append(node["metadata"])
    if isinstance(node.get("meta"), dict):
        candidates.append(node["meta"])

    for base in candidates:
        cur: Any = base
        ok = True
        for part in parts:
            if not isinstance(cur, dict) or part not in cur:
                ok = False
                break
            cur = cur.get(part)
        if ok:
            return cur
    return None


def _is_filled(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return len(value) > 0
    return True


def _evaluate_resource_category(
    category: dict[str, Any],
    resources: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    scope = _safe_dict(category.get("scope"))
    resource_types = [str(x).lower() for x in _safe_list(scope.get("resource_types"))]
    required_fields = [str(x) for x in _safe_list(category.get("required_fields"))]
    recommended_fields = [str(x) for x in _safe_list(category.get("recommended_fields"))]
    recommended_weight = float(category.get("recommended_weight", 0.5))
    if not required_fields and not recommended_fields:
        return {"score": 0.0, "applicable_items": 0, "required_checks": 0, "missing_checks": 0, "missing_fields": {}}

    targets: list[dict[str, Any]] = []
    for resource_type in resource_types:
        targets.extend(resources.get(resource_type, []))

    no_items_score = float(category.get("no_items_score", 0.0))
    if not targets:
        return {"score": no_items_score, "applicable_items": 0, "required_checks": 0, "missing_checks": 0, "missing_fields": {}}

    required_checks = 0
    missing_checks = 0
    recommended_checks = 0
    missing_recommended_checks = 0
    missing_fields: Counter[str] = Counter()
    missing_fields_required: Counter[str] = Counter()
    missing_fields_recommended: Counter[str] = Counter()
    for item in targets:
        for field in required_fields:
            required_checks += 1
            if not _is_filled(_lookup_field_value(item, field)):
                missing_checks += 1
                missing_fields[field] += 1
                missing_fields_required[field] += 1
        for field in recommended_fields:
            recommended_checks += 1
            if not _is_filled(_lookup_field_value(item, field)):
                missing_recommended_checks += 1
                missing_fields[field] += 1
                missing_fields_recommended[field] += 1

    score_denom = required_checks + (recommended_weight * recommended_checks)
    score_numer = missing_checks + (recommended_weight * missing_recommended_checks)
    if score_denom == 0:
        score = 0.0
    else:
        score = max(0.0, 1.0 - (score_numer / score_denom))
    return {
        "score": round(score, 3),
        "applicable_items": len(targets),
        "required_checks": required_checks,
        "missing_checks": missing_checks,
        "recommended_checks": recommended_checks,
        "missing_recommended_checks": missing_recommended_checks,
        "recommended_weight": recommended_weight,
        "missing_fields": dict(missing_fields),
        "missing_fields_required": dict(missing_fields_required),
        "missing_fields_recommended": dict(missing_fields_recommended),
    }


def _evaluate_step_category(
    category: dict[str, Any],
    steps: list[dict[str, Any]],
) -> dict[str, Any]:
    scope = _safe_dict(category.get("scope"))
    ops = [str(x) for x in _safe_list(scope.get("ops"))]
    required_fields = [str(x) for x in _safe_list(category.get("required_fields"))]
    recommended_fields = [str(x) for x in _safe_list(category.get("recommended_fields"))]
    required_by_op = _safe_dict(category.get("required_fields_by_op"))
    recommended_by_op = _safe_dict(category.get("recommended_fields_by_op"))
    recommended_weight = float(category.get("recommended_weight", 0.5))

    targets = [step for step in steps if not ops or step.get("op") in ops]
    no_items_score = float(category.get("no_items_score", 0.0))
    if not targets:
        return {"score": no_items_score, "applicable_items": 0, "required_checks": 0, "missing_checks": 0, "missing_fields": {}}

    required_checks = 0
    missing_checks = 0
    recommended_checks = 0
    missing_recommended_checks = 0
    missing_fields: Counter[str] = Counter()
    missing_fields_required: Counter[str] = Counter()
    missing_fields_recommended: Counter[str] = Counter()
    for step in targets:
        op = str(step.get("op", ""))
        op_fields = [str(x) for x in _safe_list(required_by_op.get(op))]
        op_fields_recommended = [str(x) for x in _safe_list(recommended_by_op.get(op))]
        check_fields = op_fields if op_fields else required_fields
        check_fields_recommended = op_fields_recommended if op_fields_recommended else recommended_fields
        for field in check_fields:
            required_checks += 1
            if not _is_filled(_lookup_field_value(step, field)):
                missing_checks += 1
                missing_fields[f"{op}.{field}"] += 1
                missing_fields_required[f"{op}.{field}"] += 1
        for field in check_fields_recommended:
            recommended_checks += 1
            if not _is_filled(_lookup_field_value(step, field)):
                missing_recommended_checks += 1
                missing_fields[f"{op}.{field}"] += 1
                missing_fields_recommended[f"{op}.{field}"] += 1

    score_denom = required_checks + (recommended_weight * recommended_checks)
    score_numer = missing_checks + (recommended_weight * missing_recommended_checks)
    if score_denom == 0:
        score = 0.0
    else:
        score = max(0.0, 1.0 - (score_numer / score_denom))
    return {
        "score": round(score, 3),
        "applicable_items": len(targets),
        "required_checks": required_checks,
        "missing_checks": missing_checks,
        "recommended_checks": recommended_checks,
        "missing_recommended_checks": missing_recommended_checks,
        "recommended_weight": recommended_weight,
        "missing_fields": dict(missing_fields),
        "missing_fields_required": dict(missing_fields_required),
        "missing_fields_recommended": dict(missing_fields_recommended),
    }


def _evaluate_settings_category(category: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
    settings = _safe_dict(data.get("settings"))
    required_fields = [str(x) for x in _safe_list(category.get("required_fields"))]
    recommended_fields = [str(x) for x in _safe_list(category.get("recommended_fields"))]
    recommended_weight = float(category.get("recommended_weight", 0.5))
    if not required_fields and not recommended_fields:
        return {"score": 0.0, "applicable_items": 1, "required_checks": 0, "missing_checks": 0, "missing_fields": {}}

    required_checks = len(required_fields)
    missing_checks = 0
    recommended_checks = len(recommended_fields)
    missing_recommended_checks = 0
    missing_fields: Counter[str] = Counter()
    missing_fields_required: Counter[str] = Counter()
    missing_fields_recommended: Counter[str] = Counter()
    for field in required_fields:
        if not _is_filled(_lookup_field_value(settings, field)):
            missing_checks += 1
            missing_fields[field] += 1
            missing_fields_required[field] += 1
    for field in recommended_fields:
        if not _is_filled(_lookup_field_value(settings, field)):
            missing_recommended_checks += 1
            missing_fields[field] += 1
            missing_fields_recommended[field] += 1
    score_denom = required_checks + (recommended_weight * recommended_checks)
    score_numer = missing_checks + (recommended_weight * missing_recommended_checks)
    score = max(0.0, 1.0 - (score_numer / score_denom)) if score_denom else 0.0
    return {
        "score": round(score, 3),
        "applicable_items": 1,
        "required_checks": required_checks,
        "missing_checks": missing_checks,
        "recommended_checks": recommended_checks,
        "missing_recommended_checks": missing_recommended_checks,
        "recommended_weight": recommended_weight,
        "missing_fields": dict(missing_fields),
        "missing_fields_required": dict(missing_fields_required),
        "missing_fields_recommended": dict(missing_fields_recommended),
    }


def _evaluate_metadata_category(category: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
    meta = _safe_dict(data.get("metadata"))
    if not meta:
        meta = _safe_dict(data.get("meta"))
    required_fields = [str(x) for x in _safe_list(category.get("required_fields"))]
    recommended_fields = [str(x) for x in _safe_list(category.get("recommended_fields"))]
    recommended_weight = float(category.get("recommended_weight", 0.5))
    if not required_fields and not recommended_fields:
        return {"score": 0.0, "applicable_items": 1, "required_checks": 0, "missing_checks": 0, "missing_fields": {}}

    required_checks = len(required_fields)
    missing_checks = 0
    recommended_checks = len(recommended_fields)
    missing_recommended_checks = 0
    missing_fields: Counter[str] = Counter()
    missing_fields_required: Counter[str] = Counter()
    missing_fields_recommended: Counter[str] = Counter()
    for field in required_fields:
        if not _is_filled(_lookup_field_value(meta, field)):
            missing_checks += 1
            missing_fields[field] += 1
            missing_fields_required[field] += 1
    for field in recommended_fields:
        if not _is_filled(_lookup_field_value(meta, field)):
            missing_recommended_checks += 1
            missing_fields[field] += 1
            missing_fields_recommended[field] += 1
    score_denom = required_checks + (recommended_weight * recommended_checks)
    score_numer = missing_checks + (recommended_weight * missing_recommended_checks)
    score = max(0.0, 1.0 - (score_numer / score_denom)) if score_denom else 0.0
    return {
        "score": round(score, 3),
        "applicable_items": 1,
        "required_checks": required_checks,
        "missing_checks": missing_checks,
        "recommended_checks": recommended_checks,
        "missing_recommended_checks": missing_recommended_checks,
        "recommended_weight": recommended_weight,
        "missing_fields": dict(missing_fields),
        "missing_fields_required": dict(missing_fields_required),
        "missing_fields_recommended": dict(missing_fields_recommended),
    }


def _load_repro_categories(profile: dict[str, Any]) -> list[dict[str, Any]]:
    categories = _safe_list(profile.get("categories"))
    out: list[dict[str, Any]] = []
    for cat in categories:
        if not isinstance(cat, dict):
            continue
        cat_id = str(cat.get("id", "")).strip()
        if not cat_id:
            continue
        weight = cat.get("weight", 1.0)
        try:
            weight_float = max(0.0, float(weight))
        except Exception:
            weight_float = 0.0
        normalized = dict(cat)
        normalized["id"] = cat_id
        normalized["weight"] = weight_float
        out.append(normalized)
    return out


def _flow_input_refs(step: dict[str, Any]) -> list[tuple[str, str]]:
    refs = []
    for ref in _safe_list(step.get("inputs")):
        if not isinstance(ref, dict):
            continue
        kind = str(ref.get("kind", "")).strip().lower()
        ref_id = str(ref.get("id", "")).strip()
        if kind and ref_id:
            refs.append((kind, ref_id))
    return refs


def _flow_output_refs(step: dict[str, Any]) -> list[tuple[str, str]]:
    refs = []
    for ref in _safe_list(step.get("outputs")):
        if not isinstance(ref, dict):
            continue
        kind = str(ref.get("kind", "")).strip().lower()
        ref_id = str(ref.get("id", "")).strip()
        if kind and ref_id:
            refs.append((kind, ref_id))
    return refs


def check_flow_integrity(data: dict[str, Any]) -> dict[str, Any]:
    protocol = _safe_dict(data.get("protocol"))
    steps = _normalize_steps(data)
    edges = [e for e in _safe_list(protocol.get("edges")) if isinstance(e, dict)]

    init_ids: dict[str, set[str]] = {
        "material": {str(x.get("id")) for x in _safe_list(_safe_dict(data.get("resources")).get("materials")) if isinstance(x, dict) and x.get("id")},
        "container": {str(x.get("id")) for x in _safe_list(_safe_dict(data.get("resources")).get("containers")) if isinstance(x, dict) and x.get("id")},
        "equipment": {str(x.get("id")) for x in _safe_list(_safe_dict(data.get("resources")).get("equipment")) if isinstance(x, dict) and x.get("id")},
        "sample": {str(x.get("id")) for x in _safe_list(_safe_dict(data.get("resources")).get("samples")) if isinstance(x, dict) and x.get("id")},
        "data": {str(x.get("id")) for x in _safe_list(_safe_dict(data.get("resources")).get("data")) if isinstance(x, dict) and x.get("id")},
    }

    produced: dict[str, list[dict[str, Any]]] = {}
    consumed_ids: Counter[str] = Counter()
    issues: list[dict[str, Any]] = []

    for i, step in enumerate(steps):
        sid = str(step.get("id", f"s{i+1}"))
        for kind, ref_id in _flow_input_refs(step):
            if ref_id in init_ids.get(kind, set()):
                consumed_ids[ref_id] += 1
                continue
            producers = produced.get(ref_id, [])
            if not producers:
                issues.append({"code": "FLOW_INPUT_WITHOUT_SOURCE", "severity": "warn", "path": f"/protocol/steps/{sid}/inputs", "message": f"Input {kind}:{ref_id} has no producer or initial resource."})
                continue
            if not any(p["idx"] < i for p in producers):
                issues.append({"code": "FLOW_ORDER_VIOLATION", "severity": "warn", "path": f"/protocol/steps/{sid}/inputs", "message": f"Input {kind}:{ref_id} is produced only by same/later steps."})
            if not any(p["kind"] == kind for p in producers):
                issues.append({"code": "FLOW_KIND_MISMATCH", "severity": "warn", "path": f"/protocol/steps/{sid}/inputs", "message": f"Input kind mismatch for {ref_id}: expected {kind}."})
            consumed_ids[ref_id] += 1
        for kind, ref_id in _flow_output_refs(step):
            produced.setdefault(ref_id, []).append({"kind": kind, "idx": i, "step_id": sid})

    out_degree: Counter[str] = Counter()
    for edge in edges:
        frm = str(edge.get("from", ""))
        if frm:
            out_degree[frm] += 1
    sink_step_ids = {str(s.get("id")) for s in steps if out_degree.get(str(s.get("id")), 0) == 0}

    final_ids = set()
    for ref in _safe_list(protocol.get("outputs")):
        if isinstance(ref, dict) and ref.get("id"):
            final_ids.add(str(ref.get("id")))
    for step in steps:
        sid = str(step.get("id"))
        if sid in sink_step_ids:
            for _, ref_id in _flow_output_refs(step):
                final_ids.add(ref_id)

    for ref_id, producer_entries in produced.items():
        if consumed_ids.get(ref_id, 0) > 0:
            continue
        if ref_id in final_ids:
            continue
        issues.append({"code": "FLOW_UNUSED_INTERMEDIATE", "severity": "info", "path": "/protocol/steps", "message": f"Output {ref_id} is never consumed and not marked final."})

    penalty_weights = {
        "FLOW_INPUT_WITHOUT_SOURCE": 0.2,
        "FLOW_ORDER_VIOLATION": 0.15,
        "FLOW_KIND_MISMATCH": 0.1,
        "FLOW_UNUSED_INTERMEDIATE": 0.05,
    }
    penalty = 0.0
    for issue in issues:
        penalty += penalty_weights.get(issue["code"], 0.05)
    penalty = min(1.0, penalty)
    score = round(1.0 - penalty, 3)
    return {
        "score": score,
        "applicable_items": len(steps),
        "required_checks": 0,
        "missing_checks": 0,
        "missing_fields": {},
        "issues": issues,
        "issue_counts": dict(Counter(x["code"] for x in issues)),
    }


def score_reproducibility(data: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    categories = _load_repro_categories(profile)
    if not categories:
        return {
            "profile_name": profile.get("profile_name", "unnamed"),
            "profile_version": profile.get("profile_version", "0"),
            "total": 0.0,
            "total_100": 0,
            "category_scores": {},
            "category_details": [],
            "missing_fields": {},
        }

    resources = _normalize_resources(data)
    steps = _normalize_steps(data)

    category_scores: dict[str, float] = {}
    category_details: list[dict[str, Any]] = []
    missing_fields_all: Counter[str] = Counter()
    flow_issue_counts: Counter[str] = Counter()
    deductions: list[dict[str, Any]] = []
    non_flow_scores: list[float] = []
    flow_score = 1.0
    for category in categories:
        scope_type = str(_safe_dict(category.get("scope")).get("type", "")).lower()
        if scope_type == "resource":
            detail = _evaluate_resource_category(category, resources)
        elif scope_type == "step":
            detail = _evaluate_step_category(category, steps)
        elif scope_type == "settings":
            detail = _evaluate_settings_category(category, data)
        elif scope_type == "metadata":
            detail = _evaluate_metadata_category(category, data)
        elif scope_type == "flow":
            detail = check_flow_integrity(data)
        else:
            detail = {"score": 0.0, "applicable_items": 0, "required_checks": 0, "missing_checks": 0, "missing_fields": {}}

        cat_id = category["id"]
        weight = float(category["weight"])
        score = float(detail["score"])
        category_scores[cat_id] = round(score, 3)
        if scope_type == "flow":
            flow_score = score
        else:
            non_flow_scores.append(score)
        category_details.append(
            {
                "id": cat_id,
                "weight": weight,
                "score": round(score, 3),
                "applicable_items": detail["applicable_items"],
                "required_checks": detail.get("required_checks", 0),
                "missing_checks": detail.get("missing_checks", 0),
                "recommended_checks": detail.get("recommended_checks", 0),
                "missing_recommended_checks": detail.get("missing_recommended_checks", 0),
                "recommended_weight": detail.get("recommended_weight", 0.5),
                "missing_fields": detail.get("missing_fields", {}),
                "missing_fields_required": detail.get("missing_fields_required", {}),
                "missing_fields_recommended": detail.get("missing_fields_recommended", {}),
                "issues": detail.get("issues", []),
                "issue_counts": detail.get("issue_counts", {}),
            }
        )
        for field, count in _safe_dict(detail.get("missing_fields", {})).items():
            try:
                missing_fields_all[str(field)] += int(count)
            except Exception:
                continue
        if detail.get("issue_counts"):
            for code, count in _safe_dict(detail.get("issue_counts")).items():
                try:
                    flow_issue_counts[str(code)] += int(count)
                except Exception:
                    continue
        if detail.get("missing_checks", 0):
            deductions.append(
                {
                    "category": cat_id,
                    "reason": "missing_required_fields",
                    "missing_checks": int(detail.get("missing_checks", 0)),
                    "required_checks": int(detail.get("required_checks", 0)),
                }
            )
        if detail.get("missing_recommended_checks", 0):
            deductions.append(
                {
                    "category": cat_id,
                    "reason": "missing_recommended_fields",
                    "missing_checks": int(detail.get("missing_recommended_checks", 0)),
                    "required_checks": int(detail.get("recommended_checks", 0)),
                    "recommended_weight": float(detail.get("recommended_weight", 0.5)),
                }
            )
        if detail.get("issue_counts"):
            deductions.append(
                {
                    "category": cat_id,
                    "reason": "flow_issues",
                    "issue_counts": detail.get("issue_counts", {}),
                }
            )

    total = round(sum(non_flow_scores) / len(non_flow_scores), 3) if non_flow_scores else 0.0
    critical_flow_codes = {"FLOW_INPUT_WITHOUT_SOURCE", "FLOW_ORDER_VIOLATION", "FLOW_KIND_MISMATCH"}
    viability_critical = {k: v for k, v in flow_issue_counts.items() if k in critical_flow_codes and v > 0}
    viability_pass = len(viability_critical) == 0
    return {
        "profile_name": profile.get("profile_name", "unnamed"),
        "profile_version": profile.get("profile_version", "0"),
        "total": total,
        "total_100": compute_total_100(total),
        "total_mode": "equal_average_non_flow",
        "category_scores": category_scores,
        "category_details": category_details,
        "missing_fields": dict(missing_fields_all),
        "flow_issue_counts": dict(flow_issue_counts),
        "viability_gate": {
            "pass": viability_pass,
            "flow_score": round(flow_score, 3),
            "critical_issue_counts": viability_critical,
        },
        "deductions": deductions,
    }


def score_core(
    data: dict[str, Any],
    validation: dict[str, Any],
    registry: Registry,
    reproducibility_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    issues = validation.get("issues", [])
    custom = build_custom_registry(data)
    protocol = data.get("protocol", {})
    resources = data.get("resources", {})

    scores = {
        "S_structural": _score_structural(issues),
        "S_param": _score_param(protocol),
        "S_vocab": _score_vocab(protocol, registry, custom),
        "S_ident": _score_ident(resources),
        "S_ambiguity": _score_ambiguity(data),
        "S_exec_env": _score_exec_env(data),
        "S_procedure": _score_procedure(protocol),
        "S_specificity": _score_specificity(data),
        "S_coverage": _score_coverage(protocol),
    }
    total = _compute_total(scores)

    result = {
        "total": total,
        "total_100": compute_total_100(total),
        "scores": scores,
        "top_factors": _issue_factors(issues),
    }
    if reproducibility_profile is not None:
        result["reproducibility"] = score_reproducibility(data, reproducibility_profile)
    return result
