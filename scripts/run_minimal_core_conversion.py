#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Optional

from llm_client import LLMClient, LLMClientError
import run_paper_benchmark as rpb


def _slug(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "model"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _build_prompt(input_name: str, unit_title: str, text: str) -> str:
    return (
        "Convert this protocol unit into ENZYME Core-IR JSON v0.4 using core ops only. "
        "Return JSON only.\n\n"
        f"Paper: {input_name}\n"
        "Group: minimal_test\n"
        f"Unit title: {unit_title}\n\n"
        "Protocol text:\n"
        f"{text.strip()}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run minimal direct-core conversion for one protocol text.")
    parser.add_argument(
        "--input-text",
        default="tests/minimal_inputs/colony_genotyping_pcr_abstract.txt",
        help="Path to input protocol text.",
    )
    parser.add_argument(
        "--unit-title",
        default="Colony genotyping PCR (abstract, non-operational)",
        help="Unit title used in prompt context.",
    )
    parser.add_argument("--out-dir", default="results_minimal_core_conversion")
    parser.add_argument("--llm-base-url", default="http://127.0.0.1:8000/v1")
    parser.add_argument("--llm-model", required=True)
    parser.add_argument("--llm-reasoning-effort", choices=["low", "medium", "high"], default="")
    parser.add_argument("--max-tokens", type=int, default=12000)
    parser.add_argument(
        "--core-system-prompt",
        default="scripts/prompts/enzyme_core_system_prompt.md",
        help="Core system prompt path.",
    )
    parser.add_argument(
        "--repro-profile",
        default="profiles/reproducibility_profile.strict.v0_1.json",
        help="Optional reproducibility profile path.",
    )
    parser.add_argument("--enable-rule-pack", action="store_true")
    args = parser.parse_args()

    input_text_path = Path(args.input_text)
    prompt_path = Path(args.core_system_prompt)
    repro_profile_path = Path(args.repro_profile) if args.repro_profile else None
    input_text = _read(input_text_path)
    system_prompt = _read(prompt_path)
    user_prompt = _build_prompt(input_text_path.name, args.unit_title, input_text)

    model_tag = _slug(args.llm_model)
    run_dir = Path(args.out_dir) / model_tag
    enzyme_dir = run_dir / "enzyme"
    log_path = run_dir / "run.log"
    input_ir_path = enzyme_dir / "unit_001.direct_core.json"
    out_prefix = enzyme_dir / "unit_001"
    run_dir.mkdir(parents=True, exist_ok=True)

    (run_dir / "prompt_user.txt").write_text(user_prompt, encoding="utf-8")
    (run_dir / "prompt_system.txt").write_text(system_prompt, encoding="utf-8")

    llm = LLMClient(
        base_url=args.llm_base_url,
        model=args.llm_model,
        reasoning_effort=(args.llm_reasoning_effort or None),
    )

    summary: dict[str, Any] = {
        "input_text": str(input_text_path),
        "model": args.llm_model,
        "llm_base_url": args.llm_base_url,
        "ir_mode": "direct-core",
        "status": "failed",
        "error": None,
        "score_100": None,
        "repro_score_100": None,
    }
    try:
        generated = llm.chat_json(system_prompt, user_prompt, max_tokens=args.max_tokens)
        if not isinstance(generated, dict):
            raise RuntimeError("LLM output is not a JSON object")
        _write_json(run_dir / "raw_llm_output.json", generated)

        norm_log: list[str] = []
        generated = rpb.canonicalize_hl_ir(
            generated,
            source_name=input_text_path.name,
            unit_title=args.unit_title,
            apply_synonyms=args.enable_rule_pack,
            normalization_log=norm_log,
            force_ir_kind="core",
        )
        if norm_log:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("a", encoding="utf-8") as f:
                for line in norm_log:
                    f.write(f"norm: {line}\n")

        repair_hints = rpb.detect_repair_hints(generated)
        if args.enable_rule_pack and repair_hints:
            repaired = rpb.attempt_hl_repair(llm, system_prompt, generated, repair_hints, ir_mode="direct-core")
            if isinstance(repaired, dict):
                repair_log: list[str] = []
                generated = rpb.canonicalize_hl_ir(
                    repaired,
                    source_name=input_text_path.name,
                    unit_title=args.unit_title,
                    apply_synonyms=True,
                    normalization_log=repair_log,
                    force_ir_kind="core",
                )
                if repair_log:
                    with log_path.open("a", encoding="utf-8") as f:
                        for line in repair_log:
                            f.write(f"repair_norm: {line}\n")
            with log_path.open("a", encoding="utf-8") as f:
                f.write(f"repair_hints: {len(repair_hints)}\n")

        _write_json(input_ir_path, generated)

        repro_profile: Optional[Path] = None
        if repro_profile_path is not None and repro_profile_path.exists():
            repro_profile = repro_profile_path

        ok, err = rpb.run_enzyme_pipeline(
            input_ir_path,
            out_prefix,
            log_path,
            repro_profile=repro_profile,
            ir_mode="direct-core",
            strict_lowering=False,
        )
        if not ok:
            raise RuntimeError(err or "run_enzyme_pipeline failed")

        scores_path = out_prefix.with_suffix(".scores.json")
        scores = json.loads(_read(scores_path))
        summary["score_100"] = rpb.extract_total_score_100(scores)
        summary["repro_score_100"] = rpb.extract_repro_score_100(scores)
        summary["status"] = "ok"
    except (LLMClientError, RuntimeError, Exception) as exc:
        summary["error"] = str(exc)

    _write_json(run_dir / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if summary["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())

