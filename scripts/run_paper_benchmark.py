#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from llm_client import LLMClient, LLMClientError


SUPPORTED_EXTS = {".pdf"}
MAX_SEGMENT_CANDIDATE_CHARS = 12000
MAX_HL_UNIT_TEXT_CHARS = 12000
DEVICE_KIND_SYNONYMS = {
    "thermal_cycler": "thermocycler",
    "pcr_machine": "thermocycler",
    "qpcr_instrument": "amplicon_readout_system",
    "illumina_sequencer": "amplicon_readout_system",
    "sequencer": "amplicon_readout_system",
    "gel_electrophoresis": "imager",
}
ACTION_KIND_SYNONYMS = {
    "washing": "rinse",
    "wash": "rinse",
    "sealing": "label",
    "seal": "label",
    "resuspension": "resuspend",
}
MODALITY_SYNONYMS = {
    "instrument": "instrument_readout",
    "qpcr": "instrument_readout",
}
CANONICAL_ACTION_KINDS = {
    "mix",
    "mix_gently",
    "resuspend",
    "rinse",
    "spread_on_plate",
    "pick_colony",
    "dislodge_cells",
    "label",
}
CANONICAL_DEVICE_KINDS = {
    "incubator",
    "thermocycler",
    "centrifuge",
    "plate_reader",
    "imager",
    "cell_counter",
    "dna_delivery_device",
    "amplicon_readout_system",
}
CANONICAL_MODALITIES = {"visual", "microscope", "instrument_readout"}
REQUIRED_PROGRAM_KEY_BY_DEVICE_KIND = {
    "incubator": "program_name",
    "thermocycler": "profile_name",
    "centrifuge": "program_name",
    "plate_reader": "program_name",
    "imager": "program_name",
    "cell_counter": "program_name",
    "dna_delivery_device": "program_name",
    "amplicon_readout_system": "program_name",
}
METHODS_HEADING_RE = re.compile(
    r"(?im)^\s*(?:\d+[\.)]\s*)?(materials\s+and\s+methods?|methods?|protocol|procedure|experimental\s+procedures?|method\s+details?)\s*$"
)
STOP_HEADING_RE = re.compile(
    r"(?im)^\s*(references|acknowledg(?:e)?ments?|supplementary\s+information|data\s+availability|code\s+availability|author\s+contributions?)\s*$"
)
TABLE_HEADER_LINE_RE = re.compile(r"(?i)\bstage\b.*\btiming\b.*\b(step(?:s)?|experiments?)\b")
CAPTION_LINE_RE = re.compile(
    r"(?i)^\s*(?:fig(?:ure)?|extended\s+data\s+fig(?:ure)?|supplementary\s+fig(?:ure)?|table)\s*[0-9a-zivx\.\-:()]*\b"
)
JOURNAL_BOILERPLATE_RE = re.compile(
    r"(?i)^\s*(?:\d+\s+)?NATURE\s+(?:PROTOCOLS|COMMUNICATIONS|MEDICINE|CHEMISTRY|BIOTECHNOLOGY)\b"
)
PROTOCOL_STEP_LINE_RE = re.compile(r"(?im)^\s*(?:\d{1,3}|[ivxlcdm]{1,6})[\.\)]\s+\S")
ACTIONABLE_CUE_RE = re.compile(
    r"(?i)\b(add|incubat|wash|resuspend|transfer|mix|centrifug|seed|collect|aspirat|remove|replace|stain|fix|harvest|thaw|culture|transfect|infect|measure|quantif|analy[sz]e)\b"
)


@dataclass
class UnitResult:
    unit_id: str
    title: str
    score_100: Optional[float]
    status: str
    error: Optional[str] = None
    repro_score_100: Optional[float] = None


LINKABLE_FLOW_KINDS = {"sample", "data"}
LOGICAL_FLOW_WINDOW = 3
LOGICAL_FLOW_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "into",
    "onto",
    "were",
    "was",
    "are",
    "that",
    "this",
    "then",
    "after",
    "before",
    "cells",
    "cell",
    "using",
    "used",
    "each",
    "per",
    "well",
    "plate",
    "medium",
    "buffer",
    "solution",
    "sample",
    "samples",
    "control",
    "controls",
}
LOGICAL_FLOW_ANCHOR_TOKENS = {
    "dna",
    "rna",
    "amplicon",
    "library",
    "plasmid",
    "colony",
    "culture",
    "lysate",
    "supernatant",
    "pellet",
    "transfection",
    "infection",
    "reporter",
    "sequencing",
    "pcr",
    "qpcr",
    "egfp",
    "hek293",
}
LOGICAL_CONTINUITY_RE = re.compile(
    r"\b(then|next|following|after|subsequent|resulting|harvested|collected|resuspended|transferred)\b",
    flags=re.IGNORECASE,
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def append_log(path: Path, message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{utc_now_iso()}] {message}\n"
    with path.open("a", encoding="utf-8") as f:
        f.write(line)


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def repro_profile_fingerprint(path: Optional[Path]) -> str:
    if path is None:
        return "none"
    return file_sha256(path)


def extract_repro_score_100(scores_json: Dict[str, Any]) -> Optional[float]:
    repro = scores_json.get("reproducibility")
    if not isinstance(repro, dict):
        return None
    if "total_100" in repro:
        try:
            return float(repro["total_100"])
        except Exception:
            return None
    if "total" in repro:
        try:
            return float(repro["total"]) * 100.0
        except Exception:
            return None
    return None


def _to_ref(value: Any, entity_kind: Dict[str, str]) -> Optional[Dict[str, str]]:
    if isinstance(value, dict) and "kind" in value and "id" in value:
        return {"kind": str(value["kind"]), "id": str(value["id"])}
    if not isinstance(value, str):
        return None
    raw = value.strip()
    if not raw:
        return None
    if ":" in raw:
        kind, ref_id = raw.split(":", 1)
        kind = kind.strip().lower()
        ref_id = ref_id.strip()
        if kind and ref_id:
            return {"kind": kind, "id": ref_id}
    inferred_kind = entity_kind.get(raw, "sample")
    return {"kind": inferred_kind, "id": raw}


def _parse_amount(value: Any) -> Any:
    if isinstance(value, dict):
        return value
    if isinstance(value, (int, float)):
        return {"value": float(value), "unit": "count"}
    if not isinstance(value, str):
        return value
    text = value.strip()
    m = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*([^\s].*)$", text)
    if not m:
        return value
    try:
        number = float(m.group(1))
    except Exception:
        return value
    unit = m.group(2).strip()
    if not unit:
        return value
    return {"value": number, "unit": unit}


def _sanitize_amount(value: Any) -> Any:
    if not isinstance(value, dict):
        return value
    if "unit" not in value:
        return value
    unit = value.get("unit")
    if not isinstance(unit, str):
        return value
    # If unit text is likely prose, keep amount as plain text to avoid unit parse errors.
    if len(unit.split()) >= 3 or " of " in unit:
        parts: List[str] = []
        if value.get("value") is not None:
            parts.append(str(value.get("value")))
        parts.append(unit.strip())
        return " ".join(x for x in parts if x).strip()
    return value


def _normalize_token(raw: Any) -> Any:
    if not isinstance(raw, str):
        return raw
    return raw.strip().lower().replace("-", "_").replace(" ", "_")


def _coerce_params_object(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, list):
        out: Dict[str, Any] = {}
        for item in value:
            if not isinstance(item, dict):
                continue
            key = item.get("key")
            if not isinstance(key, str) or not key.strip():
                continue
            out[key.strip()] = item.get("value")
        return out
    return {}


def load_experiment_category_rules(path: Path) -> Dict[str, Any]:
    data = json.loads(read_text(path))
    categories = []
    for raw in data.get("categories", []):
        if not isinstance(raw, dict):
            continue
        cat_id = str(raw.get("id", "")).strip()
        patterns = [p for p in raw.get("patterns", []) if isinstance(p, str) and p.strip()]
        if not cat_id or not patterns:
            continue
        categories.append({"id": cat_id, "patterns": patterns})
    return {
        "version": str(data.get("version", "1.0")),
        "min_hits": int(data.get("min_hits", 1)),
        "thresholds": dict(data.get("thresholds", {})),
        "categories": categories,
    }


def detect_experiment_categories(text: str, rules: Dict[str, Any]) -> List[Dict[str, Any]]:
    lowered = text.lower()
    min_hits = int(rules.get("min_hits", 1))
    out: List[Dict[str, Any]] = []
    for cat in rules.get("categories", []):
        cat_id = cat["id"]
        patterns = cat["patterns"]
        hits = 0
        matched = []
        for pattern in patterns:
            n = len(re.findall(pattern, lowered))
            if n > 0:
                hits += n
                matched.append(pattern)
        if hits >= min_hits:
            confidence = min(1.0, hits / max(1, len(patterns)))
            out.append(
                {
                    "id": cat_id,
                    "hits": hits,
                    "confidence": round(confidence, 3),
                    "matched_patterns": matched[:5],
                }
            )
    out.sort(key=lambda x: (-x["hits"], x["id"]))
    return out


def audit_unit_split_quality(unit_text: str, detected_categories: List[Dict[str, Any]], thresholds: Dict[str, Any]) -> Dict[str, Any]:
    text = unit_text.strip()
    char_count = len(text)
    word_count = len(re.findall(r"\b\w+\b", text))
    sentence_count = len(re.findall(r"[.!?;:]\s+", text)) + (1 if text else 0)
    categories = [c["id"] for c in detected_categories]

    min_chars = int(thresholds.get("min_chars", 120))
    min_words = int(thresholds.get("min_words", 20))
    max_categories = int(thresholds.get("max_categories_per_unit", 4))

    flags = []
    if char_count < min_chars:
        flags.append("UNIT_TOO_SHORT_CHARS")
    if word_count < min_words:
        flags.append("UNIT_TOO_SHORT_WORDS")
    if len(categories) == 0:
        flags.append("UNIT_NO_EXPERIMENT_CATEGORY")
    if len(categories) > max_categories:
        flags.append("UNIT_CATEGORY_OVERMIXED")

    return {
        "char_count": char_count,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "category_count": len(categories),
        "flags": flags,
    }


def canonicalize_hl_ir(
    hl_ir: Dict[str, Any],
    source_name: str,
    unit_title: str,
    apply_synonyms: bool = True,
    normalization_log: Optional[List[str]] = None,
    force_ir_kind: Optional[str] = None,
) -> Dict[str, Any]:
    data: Dict[str, Any] = dict(hl_ir)

    if "schema_version" not in data:
        if data.get("ir_version") is not None:
            data["schema_version"] = str(data.get("ir_version"))
        else:
            data["schema_version"] = "0.4"
    data["schema_version"] = "0.4"

    ir_kind = str(data.get("ir_kind", "")).lower()
    if force_ir_kind in {"hl", "core"}:
        data["ir_kind"] = force_ir_kind
    elif ir_kind not in {"hl", "core"}:
        data["ir_kind"] = "hl"

    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        meta = data.get("meta", {})
        title = unit_title
        source = {"type": "paper_pdf", "id": source_name}
        if isinstance(meta, dict):
            title = str(meta.get("title", title))
            if isinstance(meta.get("source"), str):
                source = {"type": "paper_pdf", "id": str(meta.get("source"))}
            elif isinstance(meta.get("source"), dict):
                source = meta["source"]
        metadata = {"title": title, "source": source}
    if not isinstance(metadata.get("source"), dict):
        metadata["source"] = {"type": "paper_pdf", "id": source_name}
    if not metadata.get("title"):
        metadata["title"] = unit_title
    data["metadata"] = metadata

    resources = data.get("resources")
    if not isinstance(resources, dict):
        resources = {"materials": [], "containers": [], "equipment": [], "samples": [], "data": []}
    for key in ["materials", "containers", "equipment", "samples", "data"]:
        if not isinstance(resources.get(key), list):
            resources[key] = []

    entity_kind: Dict[str, str] = {}
    entities = data.get("entities", [])
    if isinstance(entities, list):
        for ent in entities:
            if not isinstance(ent, dict):
                continue
            ent_id = str(ent.get("id", "")).strip()
            if not ent_id:
                continue
            ent_type = str(ent.get("type", "")).lower()
            props = ent.get("properties", {})
            if not isinstance(props, dict):
                props = {}
            entry = {"id": ent_id}
            if ent.get("name"):
                entry["name"] = ent.get("name")
            entry.update(props)
            if ent_type in {"reagent", "material", "consumable"}:
                resources["materials"].append(entry)
                entity_kind[ent_id] = "material"
            elif ent_type in {"container"}:
                if "type" not in entry:
                    entry["type"] = "generic_container"
                resources["containers"].append(entry)
                entity_kind[ent_id] = "container"
            elif ent_type in {"instrument", "equipment", "device"}:
                if "type" not in entry:
                    entry["type"] = "generic_equipment"
                resources["equipment"].append(entry)
                entity_kind[ent_id] = "equipment"
            elif ent_type in {"sample"}:
                resources["samples"].append(entry)
                entity_kind[ent_id] = "sample"
    data["resources"] = resources
    resource_kind_by_id: Dict[str, str] = {}
    for item in resources["materials"]:
        if isinstance(item, dict) and item.get("id"):
            resource_kind_by_id[str(item["id"])] = "material"
    for item in resources["containers"]:
        if isinstance(item, dict) and item.get("id"):
            resource_kind_by_id[str(item["id"])] = "container"
    for item in resources["equipment"]:
        if isinstance(item, dict) and item.get("id"):
            resource_kind_by_id[str(item["id"])] = "equipment"
    for item in resources["samples"]:
        if isinstance(item, dict) and item.get("id"):
            resource_kind_by_id[str(item["id"])] = "sample"

    protocol = data.get("protocol")
    if not isinstance(protocol, dict):
        protocol = {}

    steps = protocol.get("steps")
    if not isinstance(steps, list) or not steps:
        root_steps = data.get("steps")
        if isinstance(root_steps, list):
            steps = root_steps
        else:
            steps = []

    cleaned_steps: List[Dict[str, Any]] = []
    for idx, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            continue
        step = dict(step)
        if not step.get("id"):
            step["id"] = f"s{idx}"
        op = str(step.get("op", "")).strip()
        if not op:
            op = "annotate"
        step["op"] = op

        params = _coerce_params_object(step.get("params"))

        if op == "allocate":
            inferred_allocate_kind: Optional[str] = None
            outputs_raw = step.get("outputs")
            if isinstance(outputs_raw, list):
                for raw in outputs_raw:
                    if not isinstance(raw, dict):
                        continue
                    out_kind = str(raw.get("kind", "")).strip().lower()
                    if out_kind in {"material", "container", "equipment", "sample", "data"}:
                        inferred_allocate_kind = out_kind
                        break
            if inferred_allocate_kind is None:
                resource_ref = params.get("resource_ref")
                if isinstance(resource_ref, str) and resource_ref.strip():
                    ref_key = resource_ref.strip()
                    if ":" in ref_key:
                        prefix = ref_key.split(":", 1)[0].strip().lower()
                        if prefix in {"material", "container", "equipment", "sample", "data"}:
                            inferred_allocate_kind = prefix
                    if inferred_allocate_kind is None:
                        inferred_allocate_kind = resource_kind_by_id.get(ref_key)
            if "allocate_kind" not in params and inferred_allocate_kind is not None:
                params["allocate_kind"] = inferred_allocate_kind
                if normalization_log is not None:
                    normalization_log.append(f"{step['id']}: inferred allocate_kind={inferred_allocate_kind}")
        elif op == "transfer":
            if "amount" not in params and "volume" in params:
                params["amount"] = _parse_amount(params.pop("volume"))
                if normalization_log is not None:
                    normalization_log.append(f"{step['id']}: params.volume -> params.amount")
            if "amount" in params:
                params["amount"] = _sanitize_amount(params["amount"])
        elif op == "run_device":
            if "device_kind" not in params and "device" in params:
                device_val = str(params["device"]).strip().lower().replace(" ", "_")
                if device_val:
                    params["device_kind"] = device_val
                    if normalization_log is not None:
                        normalization_log.append(f"{step['id']}: params.device -> params.device_kind ({device_val})")
            if apply_synonyms and "device_kind" in params:
                before = params.get("device_kind")
                canonical = DEVICE_KIND_SYNONYMS.get(str(_normalize_token(before)), str(_normalize_token(before)))
                if canonical != before:
                    params["device_kind"] = canonical
                    if normalization_log is not None:
                        normalization_log.append(f"{step['id']}: device_kind {before} -> {canonical}")
            if "program" not in params:
                keep = {}
                for k in list(params.keys()):
                    if k in {"device_kind", "device_ref", "device"}:
                        continue
                    keep[k] = params[k]
                params["program"] = keep if keep else {}
            if not isinstance(params.get("program"), dict):
                params["program"] = _coerce_params_object(params.get("program"))
            device_kind = str(_normalize_token(params.get("device_kind")))
            required_key = REQUIRED_PROGRAM_KEY_BY_DEVICE_KIND.get(device_kind)
            if required_key:
                program = params.get("program", {})
                if required_key not in program:
                    alt_key = "profile_name" if required_key == "program_name" else "program_name"
                    if alt_key in program and program.get(alt_key) is not None:
                        program[required_key] = program.get(alt_key)
                        if normalization_log is not None:
                            normalization_log.append(f"{step['id']}: program.{alt_key} -> program.{required_key}")
                    elif required_key in params and params.get(required_key) is not None:
                        program[required_key] = params.get(required_key)
                        if normalization_log is not None:
                            normalization_log.append(f"{step['id']}: params.{required_key} -> program.{required_key}")
                    params["program"] = program
            if apply_synonyms and "device_kind" in params:
                device_kind = str(_normalize_token(params.get("device_kind")))
                if device_kind not in CANONICAL_DEVICE_KINDS:
                    op = "annotate"
                    step["op"] = op
                    params = {"text": f"unmapped device_kind in source: {params.get('device_kind')}"}
                    if normalization_log is not None:
                        normalization_log.append(f"{step['id']}: unknown device_kind -> annotate")
        elif op == "manipulate":
            if apply_synonyms and "action_kind" in params:
                before = params.get("action_kind")
                canonical = ACTION_KIND_SYNONYMS.get(str(_normalize_token(before)), str(_normalize_token(before)))
                if canonical != before:
                    params["action_kind"] = canonical
                    if normalization_log is not None:
                        normalization_log.append(f"{step['id']}: action_kind {before} -> {canonical}")
            if "action_kind" not in params:
                op = "annotate"
                step["op"] = op
                params = {"text": step.get("notes", "action_kind missing; converted from manipulate")}
                if normalization_log is not None:
                    normalization_log.append(f"{step['id']}: manipulate without action_kind -> annotate")
            elif apply_synonyms:
                action_kind = str(_normalize_token(params.get("action_kind")))
                if action_kind not in CANONICAL_ACTION_KINDS:
                    op = "annotate"
                    step["op"] = op
                    params = {"text": f"unmapped action_kind in source: {params.get('action_kind')}"}
                    if normalization_log is not None:
                        normalization_log.append(f"{step['id']}: unknown action_kind -> annotate")
        elif op == "observe":
            if apply_synonyms and "modality" in params:
                before = params.get("modality")
                canonical = MODALITY_SYNONYMS.get(str(_normalize_token(before)), str(_normalize_token(before)))
                if canonical != before:
                    params["modality"] = canonical
                    if normalization_log is not None:
                        normalization_log.append(f"{step['id']}: modality {before} -> {canonical}")
            params.setdefault("modality", "instrument_readout")
            params.setdefault("features", {})
            if apply_synonyms:
                modality = str(_normalize_token(params.get("modality")))
                if modality not in CANONICAL_MODALITIES:
                    op = "annotate"
                    step["op"] = op
                    params = {"text": f"unmapped modality in source: {params.get('modality')}"}
                    if normalization_log is not None:
                        normalization_log.append(f"{step['id']}: unknown modality -> annotate")

        step["params"] = params

        inputs = step.get("inputs", [])
        outputs = step.get("outputs", [])
        step["inputs"] = [ref for ref in (_to_ref(x, entity_kind) for x in (inputs if isinstance(inputs, list) else [])) if ref]
        step["outputs"] = [ref for ref in (_to_ref(x, entity_kind) for x in (outputs if isinstance(outputs, list) else [])) if ref]
        cleaned_steps.append(step)

    protocol["steps"] = cleaned_steps
    protocol["detail_level"] = 0
    if not protocol.get("start_step_id") and cleaned_steps:
        protocol["start_step_id"] = cleaned_steps[0]["id"]

    edges = protocol.get("edges")
    if not isinstance(edges, list) or not edges:
        edges = []
        for i in range(len(cleaned_steps) - 1):
            edges.append({"from": cleaned_steps[i]["id"], "to": cleaned_steps[i + 1]["id"]})
        if not edges and cleaned_steps:
            edges = [{"from": cleaned_steps[0]["id"], "to": cleaned_steps[0]["id"]}]
    protocol["edges"] = edges
    data["protocol"] = protocol

    # Add placeholder resources for referenced IDs that are otherwise undefined.
    existing: Dict[str, set[str]] = {
        "material": {str(x.get("id")) for x in resources["materials"] if isinstance(x, dict) and x.get("id")},
        "container": {str(x.get("id")) for x in resources["containers"] if isinstance(x, dict) and x.get("id")},
        "equipment": {str(x.get("id")) for x in resources["equipment"] if isinstance(x, dict) and x.get("id")},
        "sample": {str(x.get("id")) for x in resources["samples"] if isinstance(x, dict) and x.get("id")},
    }
    for step in cleaned_steps:
        for key in ("inputs", "outputs"):
            for ref in step.get(key, []):
                if not isinstance(ref, dict):
                    continue
                kind = str(ref.get("kind", "")).lower()
                ref_id = str(ref.get("id", "")).strip()
                if not ref_id:
                    continue
                if kind == "material" and ref_id not in existing["material"]:
                    resources["materials"].append({"id": ref_id, "name": ref_id})
                    existing["material"].add(ref_id)
                elif kind == "container" and ref_id not in existing["container"]:
                    resources["containers"].append({"id": ref_id, "name": ref_id, "type": "generic_container"})
                    existing["container"].add(ref_id)
                elif kind == "equipment" and ref_id not in existing["equipment"]:
                    resources["equipment"].append({"id": ref_id, "name": ref_id, "type": "generic_equipment"})
                    existing["equipment"].add(ref_id)
                elif kind == "sample" and ref_id not in existing["sample"]:
                    resources["samples"].append({"id": ref_id, "name": ref_id})
                    existing["sample"].add(ref_id)

    return data


def detect_repair_hints(hl_ir: Dict[str, Any]) -> List[str]:
    hints: List[str] = []
    protocol = hl_ir.get("protocol", {})
    steps = protocol.get("steps", []) if isinstance(protocol, dict) else []
    if not isinstance(steps, list):
        return ["protocol.steps is missing"]
    for step in steps:
        if not isinstance(step, dict):
            continue
        op = str(step.get("op", ""))
        sid = str(step.get("id", "unknown"))
        params = step.get("params") if isinstance(step.get("params"), dict) else {}
        if op == "transfer" and not isinstance(params.get("amount"), dict):
            hints.append(f"{sid}: transfer.amount missing or not structured")
        if op == "allocate" and not params.get("allocate_kind"):
            hints.append(f"{sid}: allocate.allocate_kind missing")
        if op == "run_device":
            if not params.get("device_kind"):
                hints.append(f"{sid}: run_device.device_kind missing")
            if "program" not in params:
                hints.append(f"{sid}: run_device.program missing")
            program = params.get("program") if isinstance(params.get("program"), dict) else {}
            device_kind = str(_normalize_token(params.get("device_kind")))
            required_key = REQUIRED_PROGRAM_KEY_BY_DEVICE_KIND.get(device_kind)
            if required_key and not program.get(required_key):
                hints.append(f"{sid}: run_device.program.{required_key} missing for device_kind={device_kind}")
        if op == "manipulate" and not params.get("action_kind"):
            hints.append(f"{sid}: manipulate.action_kind missing")
        if op == "observe":
            if not params.get("modality"):
                hints.append(f"{sid}: observe.modality missing")
            if params.get("features") is None:
                hints.append(f"{sid}: observe.features missing")
    resources = hl_ir.get("resources", {}) if isinstance(hl_ir.get("resources"), dict) else {}
    for idx, ent in enumerate(resources.get("containers", []) if isinstance(resources.get("containers"), list) else []):
        if isinstance(ent, dict) and not ent.get("type"):
            hints.append(f"resources.containers[{idx}].type missing")
    for idx, ent in enumerate(resources.get("equipment", []) if isinstance(resources.get("equipment"), list) else []):
        if isinstance(ent, dict) and not ent.get("type"):
            hints.append(f"resources.equipment[{idx}].type missing")
    return hints


def attempt_hl_repair(
    llm: LLMClient,
    hl_system_prompt: str,
    current_hl: Dict[str, Any],
    hints: List[str],
    ir_mode: str = "hl-core",
) -> Optional[Dict[str, Any]]:
    target_ir = "ENZYME Core-IR JSON v0.4" if ir_mode == "direct-core" else "ENZYME HL-IR JSON v0.4"
    prompt = (
        f"Repair this {target_ir}. Return JSON only. "
        "Do not invent experimental values. "
        "Only fix schema/key-shape mismatches and missing required structure. "
        "If a value is unknown, keep it as annotate text.\n\n"
        "Issues:\n- " + "\n- ".join(hints[:40]) + "\n\n"
        "Current IR JSON:\n" + json.dumps(current_hl, ensure_ascii=False)
    )
    try:
        repaired = llm.chat_json(hl_system_prompt, prompt, max_tokens=12000)
    except LLMClientError:
        return None
    return repaired if isinstance(repaired, dict) else None


def resolve_group_dir(papers_root: Path, group: str) -> Path:
    direct = papers_root / group
    if direct.exists():
        return direct
    if papers_root.name == "papers":
        alt = papers_root.with_name("paper") / group
        if alt.exists():
            return alt
    return direct


def extract_text(pdf_path: Path, out_txt: Path, log_path: Path) -> bool:
    script = Path(__file__).resolve().parent / "extract_pdf_text.py"
    cmd = [
        "python",
        str(script),
        str(pdf_path),
        "-o",
        str(out_txt),
        "--method",
        "auto",
        "--clean",
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        append_log(log_path, "extract failed: timeout (180s)")
        return False
    if proc.stdout.strip():
        append_log(log_path, proc.stdout.strip())
    if proc.returncode != 0:
        append_log(log_path, f"extract failed: {proc.stderr.strip()}")
        return False
    return True


def clean_segmentation_text(full_text: str) -> str:
    cleaned_lines: List[str] = []
    in_table_overview = False
    for raw_line in full_text.splitlines():
        line = raw_line.strip()
        if JOURNAL_BOILERPLATE_RE.match(line):
            continue
        if TABLE_HEADER_LINE_RE.search(line):
            in_table_overview = True
            continue
        if in_table_overview:
            if not line:
                in_table_overview = False
            continue
        if CAPTION_LINE_RE.match(line):
            continue
        cleaned_lines.append(raw_line)
    text = "\n".join(cleaned_lines)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _merge_spans(spans: List[Tuple[int, int]], text_len: int) -> List[Tuple[int, int]]:
    if not spans:
        return []
    normalized = sorted((max(0, s), min(text_len, e)) for s, e in spans if e > s)
    merged: List[Tuple[int, int]] = [normalized[0]]
    for start, end in normalized[1:]:
        prev_start, prev_end = merged[-1]
        if start <= prev_end + 120:
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return merged


def select_candidate_excerpt(text: str, max_chars: int) -> str:
    cleaned = clean_segmentation_text(text)
    if len(cleaned) <= max_chars:
        return cleaned

    spans: List[Tuple[int, int]] = []
    for m in PROTOCOL_STEP_LINE_RE.finditer(cleaned):
        spans.append((m.start() - 260, m.end() + 700))
    for m in ACTIONABLE_CUE_RE.finditer(cleaned):
        spans.append((m.start() - 160, m.end() + 280))
    merged = _merge_spans(spans, len(cleaned))

    parts: List[str] = []
    used = 0
    for start, end in merged:
        chunk = cleaned[start:end].strip()
        if not chunk:
            continue
        extra = len(chunk) + (5 if parts else 0)
        if used + extra > max_chars:
            remaining = max_chars - used - (5 if parts else 0)
            if remaining < 200:
                break
            chunk = chunk[:remaining].strip()
            extra = len(chunk) + (5 if parts else 0)
        parts.append(chunk)
        used += extra
        if used >= int(max_chars * 0.9):
            break

    if not parts:
        head = cleaned[: max_chars // 2].strip()
        tail_budget = max(0, max_chars - len(head) - 5)
        tail = cleaned[-tail_budget:].strip() if tail_budget > 0 else ""
        if tail:
            return f"{head}\n...\n{tail}"[:max_chars]
        return cleaned[:max_chars]

    excerpt = "\n...\n".join(parts)
    if len(excerpt) < int(max_chars * 0.6):
        tail_budget = max(0, max_chars - len(excerpt) - 5)
        tail = cleaned[-tail_budget:].strip() if tail_budget > 200 else ""
        if tail and tail not in excerpt:
            excerpt = f"{excerpt}\n...\n{tail}"[:max_chars]
    return excerpt[:max_chars]


def heuristic_sections(full_text: str) -> List[Dict[str, str]]:
    starts = [m for m in METHODS_HEADING_RE.finditer(full_text)]
    stops = [m.start() for m in STOP_HEADING_RE.finditer(full_text)]

    sections: List[Dict[str, str]] = []
    if starts:
        for i, m in enumerate(starts):
            start = m.start()
            next_start = starts[i + 1].start() if i + 1 < len(starts) else len(full_text)
            stop_after = [s for s in stops if s > start]
            stop = min(next_start, stop_after[0]) if stop_after else next_start
            chunk = full_text[start:stop].strip()
            if len(chunk) >= 800:
                title = m.group(1).strip().title()
                sections.append({"title": title, "text": chunk})

    if sections:
        return sections

    start_word = re.search(r"(?i)\bmaterials\s+and\s+methods?\b|\bmethods?\b", full_text)
    if start_word:
        start = start_word.start()
        stop_after = [s for s in stops if s > start]
        stop = stop_after[0] if stop_after else len(full_text)
        chunk = full_text[start:stop].strip()
        if len(chunk) >= 200:
            return [{"title": "Methods", "text": chunk}]

    fallback = full_text.strip()
    if not fallback:
        return []
    return [{"title": "Full Text Fallback", "text": fallback[:120000]}]


def build_segmentation_prompt(candidate_sections: List[Dict[str, str]], max_units: int) -> str:
    packed = []
    for i, sec in enumerate(candidate_sections, start=1):
        excerpt = select_candidate_excerpt(sec["text"], MAX_SEGMENT_CANDIDATE_CHARS)
        packed.append(f"## Candidate {i}: {sec['title']}\n{excerpt}")
    joined = "\n\n".join(packed)
    return (
        f"Extract up to {max_units} protocol units from the candidate text. "
        "Return JSON object with key `units` only.\n\n"
        f"{joined}"
    )


def normalize_units(units_payload: Any, max_units: int) -> List[Dict[str, str]]:
    if not isinstance(units_payload, dict):
        return []
    units = units_payload.get("units")
    if not isinstance(units, list):
        return []

    out: List[Dict[str, str]] = []
    for raw in units:
        if not isinstance(raw, dict):
            continue
        title = str(raw.get("title", "Untitled")).strip() or "Untitled"
        text = str(raw.get("text", "")).strip()
        rationale = str(raw.get("rationale", "")).strip()
        if not text:
            continue
        out.append({"title": title, "text": text, "rationale": rationale})
        if len(out) >= max_units:
            break
    return out


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def _looks_like_caption_or_non_protocol(title: str, text: str) -> bool:
    merged = f"{title}\n{text}".strip()
    if CAPTION_LINE_RE.match(merged):
        return True
    if TABLE_HEADER_LINE_RE.search(merged):
        return True
    if JOURNAL_BOILERPLATE_RE.match(merged):
        return True
    return False


def _looks_like_short_fragment(text: str, min_chars: int, min_words: int) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    if len(stripped) >= min_chars and _word_count(stripped) >= min_words:
        return False
    if PROTOCOL_STEP_LINE_RE.search(stripped):
        return False
    if ACTIONABLE_CUE_RE.search(stripped):
        return False
    return True


def postprocess_units(
    units: List[Dict[str, str]],
    max_units: int,
    min_chars: int,
    min_words: int,
) -> Tuple[List[Dict[str, str]], Dict[str, int]]:
    stats = {
        "dropped_caption_like": 0,
        "merged_short_forward": 0,
        "merged_short_backward": 0,
        "dropped_duplicate": 0,
    }
    if not units:
        return [], stats

    filtered: List[Dict[str, str]] = []
    for unit in units:
        title = str(unit.get("title", "Untitled")).strip() or "Untitled"
        text = str(unit.get("text", "")).strip()
        rationale = str(unit.get("rationale", "")).strip()
        if not text:
            continue
        if _looks_like_caption_or_non_protocol(title, text):
            stats["dropped_caption_like"] += 1
            continue
        filtered.append({"title": title, "text": text, "rationale": rationale})

    merged: List[Dict[str, str]] = []
    idx = 0
    while idx < len(filtered):
        cur = dict(filtered[idx])
        while _looks_like_short_fragment(cur["text"], min_chars, min_words) and idx + 1 < len(filtered):
            nxt = filtered[idx + 1]
            cur["text"] = f"{cur['text'].strip()}\n{nxt['text'].strip()}".strip()
            if not cur["rationale"]:
                cur["rationale"] = nxt.get("rationale", "")
            idx += 1
            stats["merged_short_forward"] += 1

        if _looks_like_short_fragment(cur["text"], min_chars, min_words) and merged:
            merged[-1]["text"] = f"{merged[-1]['text'].strip()}\n{cur['text'].strip()}".strip()
            stats["merged_short_backward"] += 1
        else:
            merged.append(cur)
        idx += 1

    deduped: List[Dict[str, str]] = []
    seen_text: Set[str] = set()
    for unit in merged:
        norm = re.sub(r"\s+", " ", unit.get("text", "").strip().lower())
        if not norm:
            continue
        if norm in seen_text:
            stats["dropped_duplicate"] += 1
            continue
        seen_text.add(norm)
        deduped.append(unit)

    if not deduped and filtered:
        deduped = [filtered[0]]
    return deduped[:max_units], stats


def fallback_units_from_heuristics(candidate_sections: List[Dict[str, str]], max_units: int) -> List[Dict[str, str]]:
    units: List[Dict[str, str]] = []
    for sec in candidate_sections:
        text = sec["text"].strip()
        if not text:
            continue
        units.append({"title": sec["title"], "text": text, "rationale": "heuristic fallback"})
        if len(units) >= max_units:
            break
    return units


def run_cmd(cmd: List[str], log_path: Path) -> tuple[bool, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.stdout.strip():
        append_log(log_path, f"stdout: {proc.stdout.strip()}")
    if proc.stderr.strip():
        append_log(log_path, f"stderr: {proc.stderr.strip()}")
    if proc.returncode != 0:
        return False, f"command failed ({proc.returncode}): {' '.join(cmd)}"
    return True, ""


def extract_total_score_100(scores_json: Dict[str, Any]) -> Optional[float]:
    if "total_100" in scores_json:
        try:
            return float(scores_json["total_100"])
        except Exception:
            return None
    if "total" in scores_json:
        try:
            return float(scores_json["total"]) * 100.0
        except Exception:
            return None
    return None


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _norm_ref(ref: Any) -> Optional[Tuple[str, str]]:
    if not isinstance(ref, dict):
        return None
    kind = str(ref.get("kind", "")).strip().lower()
    ref_id = str(ref.get("id", "")).strip()
    if not kind or not ref_id:
        return None
    return (kind, ref_id)


def _ref_token(kind: str, ref_id: str) -> str:
    return f"{kind}:{ref_id}"


def _collect_unit_refs(core_ir: Dict[str, Any]) -> Dict[str, Set[Tuple[str, str]]]:
    protocol = _safe_dict(core_ir.get("protocol"))
    steps = [s for s in _safe_list(protocol.get("steps")) if isinstance(s, dict)]
    in_refs: Set[Tuple[str, str]] = set()
    out_refs: Set[Tuple[str, str]] = set()
    for step in steps:
        for raw in _safe_list(step.get("inputs")):
            parsed = _norm_ref(raw)
            if parsed is not None:
                in_refs.add(parsed)
        for raw in _safe_list(step.get("outputs")):
            parsed = _norm_ref(raw)
            if parsed is not None:
                out_refs.add(parsed)
    return {"inputs": in_refs, "outputs": out_refs}


def _extract_unit_step_graph(core_ir: Dict[str, Any]) -> Dict[str, Any]:
    protocol = _safe_dict(core_ir.get("protocol"))
    steps = [s for s in _safe_list(protocol.get("steps")) if isinstance(s, dict)]
    step_nodes = []
    for i, step in enumerate(steps, start=1):
        sid = str(step.get("id", f"s{i}"))
        step_nodes.append({"id": sid, "op": str(step.get("op", ""))})

    step_edges = []
    for e in _safe_list(protocol.get("edges")):
        if not isinstance(e, dict):
            continue
        frm = str(e.get("from", "")).strip()
        to = str(e.get("to", "")).strip()
        if frm and to:
            step_edges.append({"from": frm, "to": to})
    return {
        "node_count": len(step_nodes),
        "edge_count": len(step_edges),
        "nodes": step_nodes,
        "edges": step_edges,
    }


def _extract_unit_ops(core_ir: Dict[str, Any]) -> List[str]:
    protocol = _safe_dict(core_ir.get("protocol"))
    steps = [s for s in _safe_list(protocol.get("steps")) if isinstance(s, dict)]
    return [str(step.get("op", "")).strip() for step in steps if str(step.get("op", "")).strip()]


def _logical_tokens(text: str) -> Set[str]:
    tokens = set()
    for tok in re.findall(r"[a-z][a-z0-9_]{2,}", text.lower()):
        if tok in LOGICAL_FLOW_STOPWORDS:
            continue
        tokens.add(tok)
    return tokens


def _flow_integrity_from_edges(
    unit_graphs: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    issue_code: str,
    issue_message: str,
) -> Dict[str, Any]:
    indeg: Counter[str] = Counter()
    outdeg: Counter[str] = Counter()
    for edge in edges:
        src = str(edge.get("from_unit", "")).strip()
        dst = str(edge.get("to_unit", "")).strip()
        if not src or not dst:
            continue
        outdeg[src] += 1
        indeg[dst] += 1

    isolated_units: List[str] = []
    for node in unit_graphs:
        uid = node["unit_id"]
        if not node["has_core"]:
            continue
        if indeg.get(uid, 0) == 0 and outdeg.get(uid, 0) == 0:
            isolated_units.append(uid)

    core_units = [n["unit_id"] for n in unit_graphs if n["has_core"]]
    isolated_rate = (len(isolated_units) / len(core_units)) if core_units else 0.0
    issues = []
    if isolated_units:
        issues.append(
            {
                "code": issue_code,
                "severity": "warn",
                "message": issue_message,
                "unit_ids": isolated_units,
            }
        )
    return {
        "pass": len(isolated_units) == 0,
        "isolated_unit_count": len(isolated_units),
        "isolated_unit_rate": round(isolated_rate, 3),
        "isolated_units": isolated_units,
        "issues": issues,
    }


def build_paper_flow_graph(
    units: List[Dict[str, str]],
    results: List[UnitResult],
    enzyme_dir: Path,
) -> Dict[str, Any]:
    status_by_unit = {r.unit_id: {"status": r.status, "error": r.error} for r in results}
    unit_graphs: List[Dict[str, Any]] = []
    in_refs_by_unit: Dict[str, Set[Tuple[str, str]]] = {}
    out_refs_by_unit: Dict[str, Set[Tuple[str, str]]] = {}
    all_out_refs_by_unit: Dict[str, Set[Tuple[str, str]]] = {}
    all_in_refs_by_unit: Dict[str, Set[Tuple[str, str]]] = {}
    tokens_by_unit: Dict[str, Set[str]] = {}
    text_by_unit: Dict[str, str] = {}
    ops_by_unit: Dict[str, List[str]] = {}

    for idx, unit in enumerate(units, start=1):
        unit_id = f"unit_{idx:03d}"
        core_path = enzyme_dir / f"{unit_id}.core.json"
        unit_title = unit.get("title", "")
        unit_text = unit.get("text", "")
        text_by_unit[unit_id] = f"{unit_title}\n{unit_text}"
        tokens_by_unit[unit_id] = _logical_tokens(text_by_unit[unit_id])
        unit_info = {
            "unit_id": unit_id,
            "title": unit_title,
            "has_core": core_path.exists(),
            "status": status_by_unit.get(unit_id, {}).get("status", "unknown"),
            "error": status_by_unit.get(unit_id, {}).get("error"),
            "step_graph": {"node_count": 0, "edge_count": 0, "nodes": [], "edges": []},
            "io_summary": {"input_refs": [], "output_refs": []},
        }
        if core_path.exists():
            try:
                core_ir = json.loads(read_text(core_path))
                refs = _collect_unit_refs(core_ir)
                step_graph = _extract_unit_step_graph(core_ir)
                ops_by_unit[unit_id] = _extract_unit_ops(core_ir)
                in_refs_by_unit[unit_id] = refs["inputs"]
                out_refs_by_unit[unit_id] = refs["outputs"]
                all_in_refs_by_unit[unit_id] = set(refs["inputs"])
                all_out_refs_by_unit[unit_id] = set(refs["outputs"])
                unit_info["step_graph"] = step_graph
                unit_info["io_summary"] = {
                    "input_refs": sorted(_ref_token(k, rid) for (k, rid) in refs["inputs"]),
                    "output_refs": sorted(_ref_token(k, rid) for (k, rid) in refs["outputs"]),
                }
            except Exception as exc:
                unit_info["has_core"] = False
                unit_info["status"] = "failed"
                unit_info["error"] = f"core parse error: {exc}"
                in_refs_by_unit[unit_id] = set()
                out_refs_by_unit[unit_id] = set()
                all_in_refs_by_unit[unit_id] = set()
                all_out_refs_by_unit[unit_id] = set()
                ops_by_unit[unit_id] = []
        else:
            in_refs_by_unit[unit_id] = set()
            out_refs_by_unit[unit_id] = set()
            all_in_refs_by_unit[unit_id] = set()
            all_out_refs_by_unit[unit_id] = set()
            ops_by_unit[unit_id] = []
        unit_graphs.append(unit_info)

    material_edge_map: Dict[Tuple[str, str], Set[str]] = {}
    for src in [u["unit_id"] for u in unit_graphs]:
        produced = {(k, rid) for (k, rid) in out_refs_by_unit.get(src, set()) if k in LINKABLE_FLOW_KINDS}
        if not produced:
            continue
        for dst in [u["unit_id"] for u in unit_graphs]:
            if src == dst:
                continue
            consumed = {(k, rid) for (k, rid) in in_refs_by_unit.get(dst, set()) if k in LINKABLE_FLOW_KINDS}
            shared = produced.intersection(consumed)
            if shared:
                key = (src, dst)
                material_edge_map.setdefault(key, set()).update(_ref_token(k, rid) for (k, rid) in shared)

    material_edges: List[Dict[str, Any]] = []
    for (src, dst), refs in sorted(material_edge_map.items()):
        material_edges.append({"from_unit": src, "to_unit": dst, "via_refs": sorted(refs), "n_refs": len(refs)})

    logical_edges: List[Dict[str, Any]] = []
    unit_ids = [u["unit_id"] for u in unit_graphs if u.get("has_core")]
    unit_index = {uid: i for i, uid in enumerate(unit_ids)}
    material_pairs = set(material_edge_map.keys())
    for src in unit_ids:
        src_idx = unit_index[src]
        src_tokens = tokens_by_unit.get(src, set())
        src_ops = ops_by_unit.get(src, [])
        src_out_all = all_out_refs_by_unit.get(src, set())
        for dst in unit_ids:
            if src == dst:
                continue
            dst_idx = unit_index[dst]
            if dst_idx <= src_idx:
                continue
            if (dst_idx - src_idx) > LOGICAL_FLOW_WINDOW:
                continue
            if (src, dst) in material_pairs:
                continue

            score = 0.0
            signals: List[str] = []
            shared_tokens: Set[str] = set()

            if dst_idx == src_idx + 1:
                score += 0.2
                signals.append("temporal_adjacency")

            dst_tokens = tokens_by_unit.get(dst, set())
            overlap = src_tokens.intersection(dst_tokens)
            anchor_overlap = overlap.intersection(LOGICAL_FLOW_ANCHOR_TOKENS)
            if anchor_overlap:
                score += min(0.45, 0.15 * len(anchor_overlap))
                signals.append("shared_target_terms")
                shared_tokens.update(anchor_overlap)
            elif len(overlap) >= 6:
                score += 0.15
                signals.append("shared_context_terms")
                shared_tokens.update(set(sorted(overlap)[:4]))

            dst_text = text_by_unit.get(dst, "")
            if LOGICAL_CONTINUITY_RE.search(dst_text):
                score += 0.2
                signals.append("continuity_cue")

            dst_ops = ops_by_unit.get(dst, [])
            dst_in_all = all_in_refs_by_unit.get(dst, set())
            if src_ops and dst_ops:
                src_last = src_ops[-1]
                dst_first = dst_ops[0]
                if src_last in {"transfer", "manipulate", "run_device", "observe"} and dst_first in {
                    "transfer",
                    "manipulate",
                    "run_device",
                    "observe",
                }:
                    score += 0.1
                    signals.append("step_dependency_pattern")
            if src_out_all and not dst_in_all:
                score += 0.1
                signals.append("implicit_input_dependency")

            if score >= 0.35 and signals:
                logical_edges.append(
                    {
                        "from_unit": src,
                        "to_unit": dst,
                        "confidence": round(min(1.0, score), 3),
                        "signals": signals,
                        "shared_terms": sorted(shared_tokens)[:8],
                    }
                )

    material_integrity = _flow_integrity_from_edges(
        unit_graphs,
        material_edges,
        issue_code="INTER_UNIT_ISOLATED_UNIT_MATERIAL",
        issue_message="One or more units are isolated in strict material-flow connectivity.",
    )
    logical_integrity = _flow_integrity_from_edges(
        unit_graphs,
        logical_edges,
        issue_code="INTER_UNIT_ISOLATED_UNIT_LOGICAL",
        issue_message="One or more units are isolated in heuristic logical-flow connectivity.",
    )
    combined_edges = [
        {"from_unit": e["from_unit"], "to_unit": e["to_unit"]}
        for e in material_edges
    ] + [{"from_unit": e["from_unit"], "to_unit": e["to_unit"]} for e in logical_edges]
    combined_integrity = _flow_integrity_from_edges(
        unit_graphs,
        combined_edges,
        issue_code="INTER_UNIT_ISOLATED_UNIT_COMBINED",
        issue_message="One or more units are isolated in combined material/logical flow connectivity.",
    )

    return {
        "graph_version": "0.2",
        "linkable_kinds": sorted(LINKABLE_FLOW_KINDS),
        "unit_graphs": unit_graphs,
        # Backward compatibility: expose strict material graph under legacy keys.
        "inter_unit_graph": {"nodes": [n["unit_id"] for n in unit_graphs], "edges": material_edges},
        "integrity": material_integrity,
        "material_flow": {
            "linkable_kinds": sorted(LINKABLE_FLOW_KINDS),
            "inter_unit_graph": {"nodes": [n["unit_id"] for n in unit_graphs], "edges": material_edges},
            "integrity": material_integrity,
        },
        "logical_flow": {
            "method": "heuristic_v0_1",
            "window_units": LOGICAL_FLOW_WINDOW,
            "inter_unit_graph": {"nodes": [n["unit_id"] for n in unit_graphs], "edges": logical_edges},
            "integrity": logical_integrity,
        },
        "combined_integrity": combined_integrity,
    }


def run_enzyme_pipeline(
    source_ir_path: Path,
    out_prefix: Path,
    log_path: Path,
    repro_profile: Optional[Path] = None,
    ir_mode: str = "hl-core",
    strict_lowering: bool = False,
) -> tuple[bool, Optional[str]]:
    core_path = out_prefix.with_suffix(".core.json")
    val_path = out_prefix.with_suffix(".validation.json")
    scores_path = out_prefix.with_suffix(".scores.json")
    report_path = out_prefix.with_suffix(".report.md")

    if ir_mode == "hl-core":
        compile_cmd = ["enzyme", "compile", "--in", str(source_ir_path), "--out", str(core_path)]
        compile_cmd.append("--strict-lowering" if strict_lowering else "--no-strict-lowering")
        ok, err = run_cmd(compile_cmd, log_path)
        if not ok:
            return False, err
    elif ir_mode == "direct-core":
        try:
            core_obj = json.loads(read_text(source_ir_path))
            write_json(core_path, core_obj)
        except Exception as exc:
            return False, f"failed to persist direct-core IR: {exc}"
    else:
        return False, f"unknown ir mode: {ir_mode}"

    ok, err = run_cmd(["enzyme", "validate", "--in", str(core_path), "--out", str(val_path)], log_path)
    if not ok:
        return False, err
    score_cmd = ["enzyme", "score", "--in", str(core_path), "--validation", str(val_path), "--out", str(scores_path)]
    if repro_profile is not None:
        score_cmd.extend(["--repro-profile", str(repro_profile)])
    ok, err = run_cmd(score_cmd, log_path)
    if not ok:
        return False, err
    ok, err = run_cmd(
        [
            "enzyme",
            "report",
            "--in",
            str(core_path),
            "--validation",
            str(val_path),
            "--scores",
            str(scores_path),
            "--format",
            "md",
            "--out",
            str(report_path),
        ],
        log_path,
    )
    if not ok:
        return False, err
    return True, None


def process_paper(
    pdf_path: Path,
    group: str,
    out_root: Path,
    llm: LLMClient,
    seg_prompt: str,
    hl_system_prompt: str,
    core_system_prompt: str,
    max_protocols: int,
    skip_existing: bool,
    repro_profile: Optional[Path],
    repro_profile_fp: str,
    enable_rule_pack: bool,
    category_rules: Dict[str, Any],
    ir_mode: str,
    strict_lowering: bool,
) -> None:
    paper_stem = pdf_path.stem
    paper_dir = out_root / group / paper_stem
    extracted_dir = paper_dir / "extracted"
    units_dir = paper_dir / "protocol_units"
    enzyme_dir = paper_dir / "enzyme"
    logs_dir = paper_dir / "logs"
    for p in [extracted_dir, units_dir, enzyme_dir, logs_dir]:
        p.mkdir(parents=True, exist_ok=True)

    paper_log = logs_dir / "pipeline.log"
    append_log(paper_log, f"processing {pdf_path.name}")

    full_txt = extracted_dir / "full.txt"
    if not (skip_existing and full_txt.exists() and full_txt.stat().st_size > 0):
        ok = extract_text(pdf_path, full_txt, paper_log)
        if not ok:
            summary = {
                "source_paper": str(pdf_path),
                "group": group,
                "ir_mode": ir_mode,
                "number_of_units": 0,
                "unit_scores": [],
                "mean_total_score_100": None,
                "median_total_score_100": None,
                "failure_reason": "text extraction failed",
                "created_at": utc_now_iso(),
            }
            write_json(paper_dir / "paper_summary.json", summary)
            return

    full_text = read_text(full_txt).strip()
    if not full_text:
        append_log(paper_log, "empty extracted text")
        summary = {
            "source_paper": str(pdf_path),
            "group": group,
            "ir_mode": ir_mode,
            "number_of_units": 0,
            "unit_scores": [],
            "mean_total_score_100": None,
            "median_total_score_100": None,
            "failure_reason": "no extractable text",
            "created_at": utc_now_iso(),
        }
        write_json(paper_dir / "paper_summary.json", summary)
        return

    units_json_path = units_dir / "units.json"
    units: List[Dict[str, str]] = []
    thresholds = category_rules.get("thresholds", {}) if isinstance(category_rules.get("thresholds"), dict) else {}
    min_unit_chars = int(thresholds.get("min_chars", 120))
    min_unit_words = int(thresholds.get("min_words", 20))
    if skip_existing and units_json_path.exists():
        try:
            units = normalize_units(json.loads(read_text(units_json_path)), max_protocols)
            units, _ = postprocess_units(
                units,
                max_units=max_protocols,
                min_chars=min_unit_chars,
                min_words=min_unit_words,
            )
        except Exception:
            units = []

    if not units:
        seg_text = clean_segmentation_text(full_text)
        if len(seg_text) != len(full_text):
            append_log(
                paper_log,
                f"segmentation text cleaned: raw_chars={len(full_text)} cleaned_chars={len(seg_text)}",
            )
        candidates = heuristic_sections(seg_text)
        append_log(paper_log, f"heuristic candidate sections={len(candidates)}")

        payload: Any = None
        try:
            payload = llm.chat_json(seg_prompt, build_segmentation_prompt(candidates, max_protocols), max_tokens=8192)
        except LLMClientError as exc:
            append_log(paper_log, f"LLM segmentation failed: {exc}")

        units = normalize_units(payload, max_protocols)
        post_stats: Dict[str, int] = {}
        if units:
            units, post_stats = postprocess_units(
                units,
                max_units=max_protocols,
                min_chars=min_unit_chars,
                min_words=min_unit_words,
            )
            if any(v > 0 for v in post_stats.values()):
                append_log(paper_log, f"unit postprocess stats={post_stats}")
        if not units:
            units = fallback_units_from_heuristics(candidates, max_protocols)
            units, post_stats = postprocess_units(
                units,
                max_units=max_protocols,
                min_chars=min_unit_chars,
                min_words=min_unit_words,
            )
            if any(v > 0 for v in post_stats.values()):
                append_log(paper_log, f"fallback unit postprocess stats={post_stats}")

        write_json(units_json_path, {"units": units, "created_at": utc_now_iso()})

    for i, unit in enumerate(units, start=1):
        unit_txt = units_dir / f"unit_{i:03d}.txt"
        if not (skip_existing and unit_txt.exists() and unit_txt.stat().st_size > 0):
            unit_txt.write_text(unit["text"].strip() + "\n", encoding="utf-8")

    unit_quality_audit: List[Dict[str, Any]] = []
    split_flag_counter: Counter[str] = Counter()
    for i, unit in enumerate(units, start=1):
        unit_id = f"unit_{i:03d}"
        text = unit.get("text", "")
        detected_categories = detect_experiment_categories(text, category_rules)
        split_audit = audit_unit_split_quality(text, detected_categories, category_rules.get("thresholds", {}))
        split_flag_counter.update(split_audit.get("flags", []))
        unit["detected_categories"] = detected_categories
        unit["split_audit"] = split_audit
        unit_quality_audit.append(
            {
                "unit_id": unit_id,
                "title": unit.get("title", ""),
                "detected_categories": detected_categories,
                "split_audit": split_audit,
            }
        )
    write_json(
        units_dir / "unit_quality_audit.json",
        {
            "rules_version": category_rules.get("version", "1.0"),
            "thresholds": category_rules.get("thresholds", {}),
            "units": unit_quality_audit,
        },
    )
    write_json(units_json_path, {"units": units, "created_at": utc_now_iso()})

    results: List[UnitResult] = []
    for i, unit in enumerate(units, start=1):
        unit_id = f"unit_{i:03d}"
        unit_log = logs_dir / f"{unit_id}.log"
        input_ir_suffix = "hl.json" if ir_mode == "hl-core" else "direct_core.json"
        input_ir_path = enzyme_dir / f"{unit_id}.{input_ir_suffix}"
        core_path = enzyme_dir / f"{unit_id}.core.json"
        val_path = enzyme_dir / f"{unit_id}.validation.json"
        scores_path = enzyme_dir / f"{unit_id}.scores.json"
        report_path = enzyme_dir / f"{unit_id}.report.md"
        meta_path = enzyme_dir / f"{unit_id}.meta.json"

        done = all(path.exists() for path in [input_ir_path, core_path, val_path, scores_path, report_path, meta_path])
        if done:
            try:
                meta = json.loads(read_text(meta_path))
                prior_fp = str(meta.get("repro_profile_fingerprint", "none"))
                prior_mode = str(meta.get("ir_mode", "hl-core"))
                if prior_fp != repro_profile_fp or prior_mode != ir_mode:
                    done = False
                    append_log(
                        unit_log,
                        (
                            "recompute needed: "
                            f"repro profile fingerprint changed ({prior_fp} -> {repro_profile_fp}) "
                            f"or ir_mode changed ({prior_mode} -> {ir_mode})"
                        ),
                    )
            except Exception:
                done = False
        if skip_existing and done:
            try:
                scores = json.loads(read_text(scores_path))
                meta = {
                    "source_paper": str(pdf_path),
                    "group": group,
                    "unit_id": unit_id,
                    "unit_title": unit["title"],
                    "detected_categories": unit.get("detected_categories", []),
                    "unit_split_audit": unit.get("split_audit", {}),
                    "text_hash_sha256": hashlib.sha256(unit["text"].encode("utf-8")).hexdigest(),
                    "repro_profile_path": (str(repro_profile) if repro_profile is not None else None),
                    "repro_profile_fingerprint": repro_profile_fp,
                    "ir_mode": ir_mode,
                    "created_at": utc_now_iso(),
                }
                write_json(meta_path, meta)
                results.append(
                    UnitResult(
                        unit_id=unit_id,
                        title=unit["title"],
                        score_100=extract_total_score_100(scores),
                        repro_score_100=extract_repro_score_100(scores),
                        status="skipped_existing",
                    )
                )
                continue
            except Exception:
                pass

        unit_text_for_llm = unit["text"]
        if len(unit_text_for_llm) > MAX_HL_UNIT_TEXT_CHARS:
            unit_text_for_llm = unit_text_for_llm[:MAX_HL_UNIT_TEXT_CHARS]

        prompt = (
            (
                "Convert this protocol unit into ENZYME HL-IR JSON v0.4. "
                "Return JSON only.\n\n"
                if ir_mode == "hl-core"
                else "Convert this protocol unit into ENZYME Core-IR JSON v0.4 using core ops only. "
                "Return JSON only.\n\n"
            )
            + f"Paper: {pdf_path.name}\n"
            + f"Group: {group}\n"
            + f"Unit title: {unit['title']}\n\n"
            + "Protocol text:\n"
            + f"{unit_text_for_llm}"
        )
        system_prompt = hl_system_prompt if ir_mode == "hl-core" else core_system_prompt

        try:
            generated_ir = llm.chat_json(system_prompt, prompt, max_tokens=12000)
        except LLMClientError as exc:
            append_log(unit_log, f"IR generation failed ({ir_mode}): {exc}")
            results.append(UnitResult(unit_id=unit_id, title=unit["title"], score_100=None, status="failed", error=str(exc)))
            continue

        if not isinstance(generated_ir, dict):
            err = "LLM IR output is not a JSON object"
            append_log(unit_log, err)
            results.append(UnitResult(unit_id=unit_id, title=unit["title"], score_100=None, status="failed", error=err))
            continue

        norm_log: List[str] = []
        generated_ir = canonicalize_hl_ir(
            generated_ir,
            source_name=pdf_path.name,
            unit_title=unit["title"],
            apply_synonyms=enable_rule_pack,
            normalization_log=norm_log,
            force_ir_kind=("hl" if ir_mode == "hl-core" else "core"),
        )
        if norm_log:
            append_log(unit_log, f"normalization changes={len(norm_log)}")
            for line in norm_log[:25]:
                append_log(unit_log, f"norm: {line}")
        repair_hints = detect_repair_hints(generated_ir)
        if enable_rule_pack and repair_hints:
            append_log(unit_log, f"repair pass hints={len(repair_hints)}")
            repaired = attempt_hl_repair(llm, system_prompt, generated_ir, repair_hints, ir_mode=ir_mode)
            if isinstance(repaired, dict):
                repair_norm_log: List[str] = []
                generated_ir = canonicalize_hl_ir(
                    repaired,
                    source_name=pdf_path.name,
                    unit_title=unit["title"],
                    apply_synonyms=enable_rule_pack,
                    normalization_log=repair_norm_log,
                    force_ir_kind=("hl" if ir_mode == "hl-core" else "core"),
                )
                if repair_norm_log:
                    append_log(unit_log, f"repair normalization changes={len(repair_norm_log)}")
                append_log(unit_log, "repair pass applied")
            else:
                append_log(unit_log, "repair pass skipped (LLM repair unavailable)")

        write_json(input_ir_path, generated_ir)

        out_prefix = enzyme_dir / unit_id
        ok, err = run_enzyme_pipeline(
            input_ir_path,
            out_prefix,
            unit_log,
            repro_profile=repro_profile,
            ir_mode=ir_mode,
            strict_lowering=strict_lowering,
        )
        if not ok:
            results.append(UnitResult(unit_id=unit_id, title=unit["title"], score_100=None, status="failed", error=err))
            continue

        try:
            scores = json.loads(read_text(scores_path))
            score_100 = extract_total_score_100(scores)
            repro_score_100 = extract_repro_score_100(scores)
        except Exception:
            score_100 = None
            repro_score_100 = None

        meta = {
            "source_paper": str(pdf_path),
            "group": group,
            "unit_id": unit_id,
            "unit_title": unit["title"],
            "detected_categories": unit.get("detected_categories", []),
            "unit_split_audit": unit.get("split_audit", {}),
            "text_hash_sha256": hashlib.sha256(unit["text"].encode("utf-8")).hexdigest(),
            "repro_profile_path": (str(repro_profile) if repro_profile is not None else None),
            "repro_profile_fingerprint": repro_profile_fp,
            "ir_mode": ir_mode,
            "created_at": utc_now_iso(),
        }
        write_json(meta_path, meta)
        results.append(
            UnitResult(
                unit_id=unit_id,
                title=unit["title"],
                score_100=score_100,
                repro_score_100=repro_score_100,
                status="ok",
            )
        )

    score_vals = [r.score_100 for r in results if r.score_100 is not None]
    repro_vals = [r.repro_score_100 for r in results if r.repro_score_100 is not None]
    summary = {
        "source_paper": str(pdf_path),
        "group": group,
        "ir_mode": ir_mode,
        "number_of_units": len(units),
        "unit_scores": [r.__dict__ for r in results],
        "mean_total_score_100": (statistics.mean(score_vals) if score_vals else None),
        "median_total_score_100": (statistics.median(score_vals) if score_vals else None),
        "mean_repro_score_100": (statistics.mean(repro_vals) if repro_vals else None),
        "median_repro_score_100": (statistics.median(repro_vals) if repro_vals else None),
        "failure_reason": None if units else "no protocol units identified",
        "created_at": utc_now_iso(),
        "unit_split_quality": {
            "rules_version": category_rules.get("version", "1.0"),
            "flag_counts": dict(split_flag_counter),
            "units_with_flags": [
                {
                    "unit_id": row["unit_id"],
                    "flags": row.get("split_audit", {}).get("flags", []),
                }
                for row in unit_quality_audit
                if row.get("split_audit", {}).get("flags")
            ],
        },
    }
    paper_flow_graph = build_paper_flow_graph(units, results, enzyme_dir)
    write_json(paper_dir / "paper_flow_graph.json", paper_flow_graph)
    summary["flow_graph"] = {
        "path": str(paper_dir / "paper_flow_graph.json"),
        "integrity": paper_flow_graph.get("integrity", {}),
        "material_integrity": _safe_dict(_safe_dict(paper_flow_graph.get("material_flow")).get("integrity")),
        "logical_integrity": _safe_dict(_safe_dict(paper_flow_graph.get("logical_flow")).get("integrity")),
        "combined_integrity": paper_flow_graph.get("combined_integrity", {}),
    }
    write_json(paper_dir / "paper_summary.json", summary)

def find_pdfs(group_dir: Path) -> List[Path]:
    if not group_dir.exists():
        return []
    return sorted([p for p in group_dir.iterdir() if p.suffix.lower() in SUPPORTED_EXTS and p.is_file()])


def main() -> int:
    parser = argparse.ArgumentParser(description="Run paper -> ENZYME benchmark pipeline")
    parser.add_argument("--papers-root", default="papers", help="Root directory containing group subdirs")
    parser.add_argument("--out", default="results", help="Output directory")
    parser.add_argument("--group", action="append", choices=["nat_protocols", "nat_siblings"], help="Group(s) to run")
    parser.add_argument("--max-papers-per-group", type=int, default=None, help="Optional cap for papers per group (smoke test)")
    parser.add_argument("--max-protocols-per-paper", type=int, default=10)
    parser.add_argument("--llm-base-url", default="http://localhost:8000/v1")
    parser.add_argument("--llm-model", default="gpt-oss-120b")
    parser.add_argument(
        "--ir-mode",
        default="hl-core",
        choices=["hl-core", "direct-core"],
        help="LLM output mode: HL then compile to Core, or direct Core generation.",
    )
    parser.add_argument(
        "--llm-reasoning-effort",
        default=None,
        choices=["low", "medium", "high"],
        help="Optional reasoning effort for chat-completions-compatible models.",
    )
    parser.add_argument("--category-rules", default="scripts/config/experiment_category_rules.v1.json")
    parser.add_argument("--repro-profile", default=None, help="Optional reproducibility profile JSON for enzyme score")
    parser.add_argument(
        "--require-repro-profile",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Require --repro-profile for benchmark runs (default: true).",
    )
    parser.add_argument(
        "--enable-rule-pack",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable synonym normalization + one-pass repair before ENZYME compile",
    )
    parser.add_argument(
        "--strict-lowering",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Enable strict lowering mode when --ir-mode=hl-core.",
    )
    parser.add_argument("--skip-existing", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    groups = args.group or ["nat_protocols", "nat_siblings"]
    papers_root = Path(args.papers_root)
    out_root = Path(args.out)

    prompt_dir = Path(__file__).resolve().parent / "prompts"
    seg_prompt = read_text(prompt_dir / "segment_protocol_prompt.md")
    hl_system_prompt = read_text(prompt_dir / "enzyme_system_prompt.md")
    core_system_prompt = read_text(prompt_dir / "enzyme_core_system_prompt.md")

    llm = LLMClient(base_url=args.llm_base_url, model=args.llm_model, reasoning_effort=args.llm_reasoning_effort)
    repro_profile = Path(args.repro_profile) if args.repro_profile else None
    if repro_profile is not None and not repro_profile.exists():
        parser.error(f"--repro-profile does not exist: {repro_profile}")
    if args.require_repro_profile and repro_profile is None:
        parser.error("--repro-profile is required (or use --no-require-repro-profile for legacy/default-only runs)")
    repro_profile_fp = repro_profile_fingerprint(repro_profile)
    category_rules = load_experiment_category_rules(Path(args.category_rules))

    for group in groups:
        group_dir = resolve_group_dir(papers_root, group)
        pdfs = find_pdfs(group_dir)
        if args.max_papers_per_group is not None and args.max_papers_per_group > 0:
            pdfs = pdfs[: args.max_papers_per_group]
        print(f"[benchmark] group={group} papers={len(pdfs)} source={group_dir}", flush=True)
        if not pdfs:
            continue
        for idx, pdf in enumerate(pdfs, start=1):
            print(f"[benchmark] {group} {idx}/{len(pdfs)} {pdf.name}", flush=True)
            process_paper(
                pdf_path=pdf,
                group=group,
                out_root=out_root,
                llm=llm,
                seg_prompt=seg_prompt,
                hl_system_prompt=hl_system_prompt,
                core_system_prompt=core_system_prompt,
                max_protocols=args.max_protocols_per_paper,
                skip_existing=args.skip_existing,
                repro_profile=repro_profile,
                repro_profile_fp=repro_profile_fp,
                enable_rule_pack=args.enable_rule_pack,
                category_rules=category_rules,
                ir_mode=args.ir_mode,
                strict_lowering=args.strict_lowering,
            )

    print("[benchmark] done", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
