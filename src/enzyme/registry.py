from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .io import load_json


@dataclass(frozen=True)
class Registry:
    core_ops: set[str]
    action_kinds: dict[str, Any]
    device_kinds: dict[str, Any]
    modalities: set[str]
    observation_features: dict[str, Any]

    @classmethod
    def from_file(cls, path: str | Path) -> "Registry":
        data = load_json(path)
        return cls(
            core_ops=set(data.get("core_ops", [])),
            action_kinds=data.get("action_kinds", {}),
            device_kinds=data.get("device_kinds", {}),
            modalities=set(data.get("modalities", [])),
            observation_features=data.get("observation_features", {}),
        )


def _custom_registry_block(custom: dict[str, Any] | None, key: str) -> dict[str, Any]:
    if not custom:
        return {}
    entries = custom.get(key, [])
    output: dict[str, Any] = {}
    for entry in entries:
        name = entry.get("name")
        if name:
            output[name] = entry
    return output


def build_custom_registry(ir: dict[str, Any]) -> dict[str, dict[str, Any]]:
    registries = ir.get("registries", {})
    custom = registries.get("custom", {}) if isinstance(registries, dict) else {}
    return {
        "action_kinds": _custom_registry_block(custom, "action_kinds"),
        "device_kinds": _custom_registry_block(custom, "device_kinds"),
        "modalities": {entry.get("name") for entry in custom.get("modalities", [])}
        if isinstance(custom, dict)
        else set(),
        "observation_features": _custom_registry_block(custom, "observation_features"),
    }
