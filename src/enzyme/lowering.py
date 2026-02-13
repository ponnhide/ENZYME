from __future__ import annotations

from copy import deepcopy
from typing import Any


MACRO_MAP = {
    "thermocycle": ("thermocycler", "profile_name"),
    "incubate": ("incubator", "program_name"),
    "centrifuge": ("centrifuge", "program_name"),
}


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


def lower_to_core(hl_ir: dict[str, Any]) -> dict[str, Any]:
    core_ir = deepcopy(hl_ir)
    core_ir["ir_kind"] = "core"

    steps_out: list[dict[str, Any]] = []
    edges_out: list[dict[str, Any]] = []
    measure_internal_edges: dict[str, dict[str, Any]] = {}
    id_map: dict[str, list[str]] = {}

    for step in hl_ir.get("protocol", {}).get("steps", []):
        op = step.get("op")
        if op in MACRO_MAP:
            device_kind, program_key = MACRO_MAP[op]
            new_step = deepcopy(step)
            new_step["op"] = "run_device"
            program_value = step.get("params", {}).get(program_key)
            device_ref = step.get("params", {}).get("device_ref")
            new_step["params"] = {
                "device_kind": device_kind,
                "program": {program_key: program_value},
            }
            if device_ref is not None:
                new_step["params"]["device_ref"] = device_ref
            if op in {"incubate", "centrifuge"} and "outputs" not in new_step:
                new_step["outputs"] = []
            _inherit_metadata(step, new_step, step.get("id"), include_parent=False)
            steps_out.append(new_step)
            id_map[step.get("id")] = [step.get("id")]
        elif op == "measure":
            run_id = f"{step.get('id')}.1"
            observe_id = f"{step.get('id')}.2"
            run_step = {
                "id": run_id,
                "op": "run_device",
                "label": f"{step.get('label')} (run)" if step.get("label") else None,
                "inputs": deepcopy(step.get("inputs", [])),
                "params": {
                    "device_kind": step.get("params", {}).get("device_kind"),
                    "program": {
                        "program_name": step.get("params", {}).get("program_name")
                    },
                },
            }
            if "outputs" in step:
                run_step["outputs"] = deepcopy(step.get("outputs", []))
            device_ref = step.get("params", {}).get("device_ref")
            if device_ref is not None:
                run_step["params"]["device_ref"] = device_ref
            _inherit_metadata(step, run_step, step.get("id"), include_parent=True)

            observe_step = {
                "id": observe_id,
                "op": "observe",
                "label": f"{step.get('label')} (observe)" if step.get("label") else None,
                "inputs": deepcopy(step.get("inputs", [])),
                "params": {
                    "modality": "instrument_readout",
                    "features": {},
                },
            }
            if "outputs" in step:
                observe_step["outputs"] = deepcopy(step.get("outputs", []))
            else:
                observe_step["outputs"] = [{"kind": "data", "id": f"data:{step.get('id')}_measurement"}]
            _inherit_metadata(step, observe_step, step.get("id"), include_parent=True)

            steps_out.extend([run_step, observe_step])
            measure_internal_edges[step.get("id")] = {"from": run_id, "to": observe_id}
            id_map[step.get("id")] = [run_id, observe_id]
        else:
            steps_out.append(deepcopy(step))
            id_map[step.get("id")] = [step.get("id")]

    internal_added: set[str] = set()
    for edge in hl_ir.get("protocol", {}).get("edges", []):
        from_step = edge.get("from")
        if from_step in measure_internal_edges and from_step not in internal_added:
            edges_out.append(measure_internal_edges[from_step])
            internal_added.add(from_step)

        from_ids = id_map.get(from_step, [from_step])
        to_ids = id_map.get(edge.get("to"), [edge.get("to")])
        edges_out.append(
            {
                "from": from_ids[-1],
                "to": to_ids[0],
                **{k: v for k, v in edge.items() if k not in {"from", "to"}},
            }
        )

    for measure_id, internal_edge in measure_internal_edges.items():
        if measure_id not in internal_added:
            edges_out.append(internal_edge)

    protocol = deepcopy(hl_ir.get("protocol", {}))
    protocol["steps"] = steps_out
    protocol["edges"] = edges_out
    if protocol.get("step_order"):
        new_order: list[str] = []
        for step_id in protocol.get("step_order", []):
            new_order.extend(id_map.get(step_id, [step_id]))
        protocol["step_order"] = new_order
    if protocol.get("start_step_id"):
        protocol["start_step_id"] = id_map.get(
            protocol.get("start_step_id"), [protocol.get("start_step_id")]
        )[0]
    core_ir["protocol"] = protocol
    return core_ir
