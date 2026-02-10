from __future__ import annotations

from datetime import date
from typing import Any


def import_protocolsio(data: dict[str, Any]) -> dict[str, Any]:
    payload = data.get("payload", {})
    protocol_guid = payload.get("guid")
    today = date(2026, 2, 9).isoformat()

    materials = []
    for material in payload.get("materials", []) or []:
        mat_id = material.get("id")
        materials.append(
            {
                "id": f"mat:{mat_id}",
                "name": material.get("name"),
                "vendor": (material.get("vendor") or {}).get("name"),
                "catalog_number": material.get("sku"),
                "identifiers": {
                    "protocols_io_material_id": mat_id,
                    "url": material.get("url"),
                },
            }
        )

    steps = []
    step_lookup: dict[str, str] = {}
    for step in payload.get("steps", []) or []:
        step_guid = step.get("guid")
        step_id = f"pstep:{step_guid}"
        step_lookup[step_guid] = step_id
        steps.append(
            {
                "id": step_id,
                "op": "annotate",
                "label": f"{step.get('section')}: step {step.get('id')}",
                "params": {"note": step.get("step")},
                "provenance": {
                    "source": "protocols_io",
                    "protocol_guid": protocol_guid,
                    "step_guid": step_guid,
                    "step_id": step.get("id"),
                    "section": step.get("section"),
                },
            }
        )

    edges = []
    step_order: list[str] = []
    previous_guid_to_step = {s.get("guid"): s for s in payload.get("steps", []) or []}
    start_step = next(
        (step for step in payload.get("steps", []) or [] if step.get("previous_guid") is None),
        None,
    )

    if start_step:
        current = start_step
        while current:
            current_id = step_lookup.get(current.get("guid"))
            if current_id:
                step_order.append(current_id)
            next_step = next(
                (
                    step
                    for step in payload.get("steps", []) or []
                    if step.get("previous_guid") == current.get("guid")
                ),
                None,
            )
            if next_step:
                from_id = step_lookup.get(current.get("guid"))
                to_id = step_lookup.get(next_step.get("guid"))
                if from_id and to_id:
                    edges.append({"from": from_id, "to": to_id})
            current = next_step

    return {
        "schema_version": "0.4",
        "ir_kind": "hl",
        "metadata": {
            "title": payload.get("title"),
            "version": "0.4-example",
            "source": {
                "type": "protocols_io",
                "id": protocol_guid,
                "uri": payload.get("url"),
                "retrieved_at": today,
            },
            "created_at": today,
        },
        "resources": {
            "materials": materials,
            "containers": [],
            "equipment": [],
            "samples": [],
            "data": [],
        },
        "protocol": {
            "detail_level": 0,
            "steps": steps,
            "start_step_id": step_order[0] if step_order else None,
            "edges": edges,
            "step_order": step_order,
        },
    }
