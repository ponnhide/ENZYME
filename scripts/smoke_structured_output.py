#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List, Optional
from urllib import error, request


def _stringify_parts(value: Any) -> Optional[str]:
    if isinstance(value, str):
        s = value.strip()
        return s if s else None
    if isinstance(value, list):
        parts: List[str] = []
        for item in value:
            if isinstance(item, str):
                s = item.strip()
                if s:
                    parts.append(s)
            elif isinstance(item, dict):
                for key in ("text", "content", "reasoning", "reasoning_content"):
                    v = item.get(key)
                    if isinstance(v, str) and v.strip():
                        parts.append(v.strip())
        if parts:
            return "\n".join(parts).strip()
    return None


def _extract_choice_text(choice0: Any) -> Optional[str]:
    if not isinstance(choice0, dict):
        return None
    msg = choice0.get("message")
    candidates: List[Any] = []
    if isinstance(msg, dict):
        candidates.extend([msg.get("content"), msg.get("reasoning"), msg.get("reasoning_content")])
    candidates.extend([choice0.get("text"), choice0.get("reasoning"), choice0.get("reasoning_content")])
    for candidate in candidates:
        out = _stringify_parts(candidate)
        if out:
            return out
    return None


def _json_schema_response_format() -> Dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "smoke_schema",
            "strict": True,
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "required": ["status", "steps", "score"],
                "properties": {
                    "status": {"type": "string", "enum": ["ok"]},
                    "steps": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 2,
                        "maxItems": 5,
                    },
                    "score": {"type": "integer", "minimum": 0, "maximum": 100},
                },
            },
        },
    }


def _json_object_response_format() -> Dict[str, Any]:
    return {"type": "json_object"}


def _validate_payload(obj: Any) -> Optional[str]:
    if not isinstance(obj, dict):
        return "response is not a JSON object"
    if obj.get("status") != "ok":
        return "status != ok"
    steps = obj.get("steps")
    if not isinstance(steps, list) or len(steps) < 2:
        return "steps must be a list with at least 2 entries"
    if not all(isinstance(x, str) and x.strip() for x in steps):
        return "steps entries must be non-empty strings"
    score = obj.get("score")
    if not isinstance(score, int) or score < 0 or score > 100:
        return "score must be an integer between 0 and 100"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test for structured outputs with OpenAI-compatible chat API")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    parser.add_argument("--model", required=True)
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--reasoning-max-tokens", type=int, default=512)
    parser.add_argument("--timeout-sec", type=int, default=120)
    parser.add_argument(
        "--response-format",
        choices=["json_schema", "json_object"],
        default="json_schema",
        help="Structured output mode to test",
    )
    args = parser.parse_args()

    messages = [
        {
            "role": "system",
            "content": (
                "Return JSON only. Do not add markdown. "
                "Produce status='ok', steps as short strings, and score as integer."
            ),
        },
        {
            "role": "user",
            "content": (
                "Create a tiny protocol summary with two to four steps and score. "
                "If schema exists, obey it exactly."
            ),
        },
    ]

    payload: Dict[str, Any] = {
        "model": args.model,
        "messages": messages,
        "temperature": 0,
        "max_tokens": args.max_tokens,
        "reasoning_max_tokens": args.reasoning_max_tokens,
    }
    if args.response_format == "json_schema":
        payload["response_format"] = _json_schema_response_format()
    else:
        payload["response_format"] = _json_object_response_format()

    url = args.base_url.rstrip("/") + "/chat/completions"
    req = request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=args.timeout_sec) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
    except error.HTTPError as exc:
        detail = exc.reason
        try:
            raw = exc.read().decode("utf-8", errors="replace")
            if raw.strip():
                detail = raw
        except Exception:
            pass
        print(f"[FAIL] HTTP {exc.code}: {detail}")
        return 2
    except Exception as exc:
        print(f"[FAIL] request failed: {exc}")
        return 2

    try:
        choice0 = data["choices"][0]
    except Exception:
        print("[FAIL] missing choices[0]")
        print(json.dumps(data, ensure_ascii=False)[:1200])
        return 3

    text = _extract_choice_text(choice0)
    if not text:
        print("[FAIL] missing textual content in choices[0]")
        print(json.dumps(choice0, ensure_ascii=False)[:1200])
        return 3

    try:
        obj = json.loads(text)
    except Exception as exc:
        print(f"[FAIL] content is not valid JSON: {exc}")
        print(text[:1200])
        return 4

    err = _validate_payload(obj)
    if err is not None:
        print(f"[FAIL] schema validation failed: {err}")
        print(json.dumps(obj, ensure_ascii=False, indent=2)[:1200])
        return 5

    print("[PASS] structured output parsed and validated")
    print(json.dumps(obj, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
