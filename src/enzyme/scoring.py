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
            for key in features.keys():
                total += 1
                if key in registry.observation_features or key in custom.get("observation_features", {}):
                    known += 1
    if total == 0:
        return 1.0
    return round(known / total, 3)


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


def score_core(
    data: dict[str, Any], validation: dict[str, Any], registry: Registry
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
    }
    total = _compute_total(scores)

    return {
        "total": total,
        "total_100": compute_total_100(total),
        "scores": scores,
        "top_factors": _issue_factors(issues),
    }
