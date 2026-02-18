from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any


CORE_OPS = {
    "allocate",
    "transfer",
    "manipulate",
    "run_device",
    "observe",
    "annotate",
    "dispose",
}


@dataclass(frozen=True)
class RunDeviceMacroRule:
    device_kind: str
    primary_program_keys: tuple[str, ...]
    ensure_outputs: bool = False


RUN_DEVICE_MACRO_RULES = {
    "thermocycle": RunDeviceMacroRule(
        device_kind="thermocycler",
        primary_program_keys=("profile_name",),
    ),
    "incubate": RunDeviceMacroRule(
        device_kind="incubator",
        primary_program_keys=("program_name",),
        ensure_outputs=True,
    ),
    "centrifuge": RunDeviceMacroRule(
        device_kind="centrifuge",
        primary_program_keys=("program_name",),
        ensure_outputs=True,
    ),
}

MEASURE_FEATURE_HINT_KEYS = (
    "features",
    "feature",
    "metrics",
    "metric",
    "readouts",
    "readout",
    "channels",
    "channel",
    "wavelength",
    "wavelengths",
    "signal",
    "signals",
)


class LoweringError(ValueError):
    pass


def _inherit_metadata(
    step: dict[str, Any],
    new_step: dict[str, Any],
    parent_id: str,
    include_parent: bool = False,
) -> None:
    annotations = deepcopy(step.get("annotations", {}))
    annotations.setdefault("lowered_from", step.get("op"))
    if include_parent:
        annotations.setdefault("parent", parent_id)
    new_step["annotations"] = annotations
    if "provenance" in step:
        new_step["provenance"] = deepcopy(step.get("provenance"))


def _validate_unique_step_ids(steps: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for step in steps:
        step_id = step.get("id")
        if not isinstance(step_id, str) or not step_id:
            continue
        if step_id in seen:
            duplicates.add(step_id)
        seen.add(step_id)
    if duplicates:
        dup_str = ", ".join(sorted(duplicates))
        raise LoweringError(f"Duplicate step ids found during lowering: {dup_str}")


def _collect_program_and_passthrough(
    params: dict[str, Any],
    primary_program_keys: tuple[str, ...],
) -> tuple[dict[str, Any], dict[str, Any]]:
    program: dict[str, Any] = {}
    consumed = set(primary_program_keys) | {"device_ref"}
    for key in primary_program_keys:
        if key in params and params[key] is not None:
            program[key] = deepcopy(params[key])

    passthrough: dict[str, Any] = {}
    for key, value in params.items():
        if key in consumed:
            continue
        if key not in program:
            program[key] = deepcopy(value)
        passthrough[key] = deepcopy(value)
    return program, passthrough


def _extract_measure_features(params: dict[str, Any]) -> Any:
    raw_features = params.get("features")
    if isinstance(raw_features, (dict, list)):
        return deepcopy(raw_features)
    if isinstance(raw_features, str) and raw_features.strip():
        return {"reported_feature": raw_features.strip()}

    feature_payload: dict[str, Any] = {}
    for key in MEASURE_FEATURE_HINT_KEYS:
        if key not in params:
            continue
        value = params.get(key)
        if value is None:
            continue
        feature_payload[key] = deepcopy(value)
    return feature_payload


def _normalize_refs(refs: Any) -> list[dict[str, Any]]:
    if not isinstance(refs, list):
        return []
    out: list[dict[str, Any]] = []
    for ref in refs:
        if isinstance(ref, dict):
            out.append(deepcopy(ref))
    return out


def _measure_output_refs(step: dict[str, Any]) -> list[dict[str, Any]]:
    outputs = _normalize_refs(step.get("outputs"))
    if outputs:
        return outputs
    sid = step.get("id") or "measure"
    return [{"kind": "data", "id": f"data:{sid}_measurement"}]


def _rewrite_edges(
    hl_edges: Any,
    id_map: dict[str, list[str]],
    measure_internal_edges: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    edges_out: list[dict[str, Any]] = []
    internal_added: set[str] = set()

    edges = hl_edges if isinstance(hl_edges, list) else []
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        from_step = edge.get("from")
        to_step = edge.get("to")

        if from_step in measure_internal_edges and from_step not in internal_added:
            edges_out.append(deepcopy(measure_internal_edges[from_step]))
            internal_added.add(from_step)

        from_ids = id_map.get(from_step, [from_step])
        to_ids = id_map.get(to_step, [to_step])
        rewritten = {k: deepcopy(v) for k, v in edge.items() if k not in {"from", "to"}}
        rewritten["from"] = from_ids[-1]
        rewritten["to"] = to_ids[0]
        edges_out.append(rewritten)

    for measure_id, internal_edge in measure_internal_edges.items():
        if measure_id not in internal_added:
            edges_out.append(deepcopy(internal_edge))
    return edges_out


def _rewrite_step_order(order: Any, id_map: dict[str, list[str]]) -> Any:
    if not isinstance(order, list):
        return order
    new_order: list[str] = []
    for step_id in order:
        new_order.extend(id_map.get(step_id, [step_id]))
    return new_order


def _rewrite_start_step(start_step_id: Any, id_map: dict[str, list[str]]) -> Any:
    if not start_step_id:
        return start_step_id
    return id_map.get(start_step_id, [start_step_id])[0]


def _lower_run_device_macro(step: dict[str, Any], rule: RunDeviceMacroRule) -> dict[str, Any]:
    new_step = deepcopy(step)
    params = step.get("params") if isinstance(step.get("params"), dict) else {}
    program, passthrough = _collect_program_and_passthrough(params, rule.primary_program_keys)

    new_step["op"] = "run_device"
    new_params: dict[str, Any] = {"device_kind": rule.device_kind, "program": program}
    device_ref = params.get("device_ref")
    if device_ref is not None:
        new_params["device_ref"] = deepcopy(device_ref)
    new_step["params"] = new_params

    if rule.ensure_outputs and "outputs" not in new_step:
        new_step["outputs"] = []

    _inherit_metadata(step, new_step, step.get("id"), include_parent=False)
    if passthrough:
        annotations = new_step.setdefault("annotations", {})
        if isinstance(annotations, dict):
            annotations.setdefault("lowered_param_passthrough", passthrough)
    return new_step


def _lower_measure_step(step: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any], list[str]]:
    sid = str(step.get("id", "measure"))
    run_id = f"{sid}.1"
    observe_id = f"{sid}.2"

    params = step.get("params") if isinstance(step.get("params"), dict) else {}
    run_program = deepcopy(params.get("program")) if isinstance(params.get("program"), dict) else {}
    if "program_name" in params and params.get("program_name") is not None:
        run_program.setdefault("program_name", deepcopy(params.get("program_name")))
    for key, value in params.items():
        if key in {"program", "program_name", "device_kind", "device_ref", "modality"}:
            continue
        if key in MEASURE_FEATURE_HINT_KEYS:
            continue
        if key not in run_program:
            run_program[key] = deepcopy(value)

    source_inputs = _normalize_refs(step.get("inputs"))
    source_outputs = _measure_output_refs(step)
    run_measurement_ref = {"kind": "data", "id": f"data:{sid}_raw"}

    run_step = {
        "id": run_id,
        "op": "run_device",
        "label": f"{step.get('label')} (run)" if step.get("label") else None,
        "inputs": deepcopy(source_inputs),
        "outputs": [run_measurement_ref],
        "params": {
            "device_kind": params.get("device_kind"),
            "program": run_program,
        },
    }
    device_ref = params.get("device_ref")
    if device_ref is not None:
        run_step["params"]["device_ref"] = deepcopy(device_ref)
    _inherit_metadata(step, run_step, step.get("id"), include_parent=True)

    observe_modality = params.get("modality") if params.get("modality") else "instrument_readout"
    observe_features = _extract_measure_features(params)
    observe_step = {
        "id": observe_id,
        "op": "observe",
        "label": f"{step.get('label')} (observe)" if step.get("label") else None,
        "inputs": [deepcopy(run_measurement_ref)],
        "params": {
            "modality": observe_modality,
            "features": observe_features,
        },
        "outputs": deepcopy(source_outputs),
    }
    if source_inputs:
        observe_step["params"]["target_refs"] = deepcopy(source_inputs)
    _inherit_metadata(step, observe_step, step.get("id"), include_parent=True)

    internal_edge = {"from": run_id, "to": observe_id}
    return [run_step, observe_step], internal_edge, [run_id, observe_id]


def lower_to_core(
    hl_ir: dict[str, Any],
    *,
    strict: bool = False,
    macro_rules: dict[str, RunDeviceMacroRule] | None = None,
) -> dict[str, Any]:
    core_ir = deepcopy(hl_ir)
    core_ir["ir_kind"] = "core"
    rules = macro_rules or RUN_DEVICE_MACRO_RULES

    steps_out: list[dict[str, Any]] = []
    edges_out: list[dict[str, Any]] = []
    measure_internal_edges: dict[str, dict[str, Any]] = {}
    id_map: dict[str, list[str]] = {}

    source_steps = hl_ir.get("protocol", {}).get("steps", [])
    if isinstance(source_steps, list):
        normalized_steps = [step for step in source_steps if isinstance(step, dict)]
    else:
        normalized_steps = []
    _validate_unique_step_ids(normalized_steps)

    for step in normalized_steps:
        op = step.get("op")
        step_id = step.get("id")
        if op in rules:
            new_step = _lower_run_device_macro(step, rules[op])
            steps_out.append(new_step)
            id_map[step_id] = [step_id]
        elif op == "measure":
            new_steps, internal_edge, lowered_ids = _lower_measure_step(step)
            steps_out.extend(new_steps)
            measure_internal_edges[step_id] = internal_edge
            id_map[step_id] = lowered_ids
        else:
            if strict and op not in CORE_OPS:
                sid = step.get("id", "<unknown>")
                raise LoweringError(f"Unsupported op in strict lowering: {op} (step {sid})")
            steps_out.append(deepcopy(step))
            id_map[step_id] = [step_id]

    protocol = deepcopy(hl_ir.get("protocol", {}))
    protocol["steps"] = steps_out
    edges_out = _rewrite_edges(protocol.get("edges"), id_map, measure_internal_edges)
    protocol["edges"] = edges_out
    protocol["step_order"] = _rewrite_step_order(protocol.get("step_order"), id_map)
    protocol["start_step_id"] = _rewrite_start_step(protocol.get("start_step_id"), id_map)
    core_ir["protocol"] = protocol
    return core_ir
