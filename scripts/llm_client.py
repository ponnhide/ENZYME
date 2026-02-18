#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib import error, request


class LLMClientError(RuntimeError):
    pass


@dataclass
class LLMClient:
    base_url: str = "http://localhost:8000/v1"
    model: str = "gpt-oss-120b"
    timeout_sec: int = 300
    reasoning_effort: Optional[str] = None

    def _effective_max_tokens(self, requested: int) -> int:
        lowered = self.model.lower()
        if "qwen" in lowered:
            return 16384
        return requested

    def _effective_reasoning_max_tokens(self, total_tokens: int) -> Optional[int]:
        lowered = self.model.lower()
        if "qwen" in lowered:
            return min(8192, total_tokens)
        return None

    def _effective_timeout(self) -> int:
        lowered = self.model.lower()
        if "qwen" in lowered:
            return min(self.timeout_sec, 300)
        return self.timeout_sec

    @staticmethod
    def _response_format_unsupported(message: str) -> bool:
        lowered = message.lower()
        tokens = [
            "response_format",
            "json_schema",
            "unsupported",
            "not support",
            "unknown field",
            "extra inputs are not permitted",
        ]
        return any(tok in lowered for tok in tokens)

    @staticmethod
    def _max_tokens_too_large(message: str) -> bool:
        lowered = message.lower()
        tokens = [
            "max_tokens",
            "max_completion_tokens",
            "too large",
            "maximum context length",
        ]
        return all(tok in lowered for tok in ["max", "token"]) and any(tok in lowered for tok in tokens)

    @staticmethod
    def _stringify_parts(value: Any) -> Optional[str]:
        if isinstance(value, str):
            text = value.strip()
            return text if text else None
        if isinstance(value, list):
            parts: List[str] = []
            for item in value:
                if isinstance(item, str):
                    s = item.strip()
                    if s:
                        parts.append(s)
                    continue
                if isinstance(item, dict):
                    for key in ("text", "content", "reasoning", "reasoning_content"):
                        v = item.get(key)
                        if isinstance(v, str) and v.strip():
                            parts.append(v.strip())
            if parts:
                return "\n".join(parts).strip()
        return None

    def _extract_choice_text(self, choice0: Any) -> Optional[str]:
        if not isinstance(choice0, dict):
            return None

        msg = choice0.get("message")
        text_candidates: List[Any] = []
        if isinstance(msg, dict):
            text_candidates.extend(
                [
                    msg.get("content"),
                    msg.get("reasoning"),
                    msg.get("reasoning_content"),
                ]
            )
        text_candidates.extend(
            [
                choice0.get("text"),
                choice0.get("reasoning"),
                choice0.get("reasoning_content"),
            ]
        )

        for candidate in text_candidates:
            extracted = self._stringify_parts(candidate)
            if extracted:
                return extracted
        return None

    def _chat_once(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 8192,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        url = self.base_url.rstrip("/") + "/chat/completions"
        effective_max_tokens = self._effective_max_tokens(max_tokens)
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0,
            "max_tokens": effective_max_tokens,
        }
        reasoning_max_tokens = self._effective_reasoning_max_tokens(effective_max_tokens)
        if reasoning_max_tokens is not None:
            payload["reasoning_max_tokens"] = reasoning_max_tokens
        if self.reasoning_effort:
            payload["reasoning_effort"] = self.reasoning_effort
        if response_format is not None:
            payload["response_format"] = response_format
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with request.urlopen(req, timeout=self._effective_timeout()) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="replace"))
        except error.HTTPError as exc:
            detail = exc.reason
            try:
                raw = exc.read().decode("utf-8", errors="replace")
                if raw.strip():
                    detail = raw
            except Exception:
                pass
            raise LLMClientError(f"LLM request failed (HTTP {exc.code}): {detail}") from exc
        except error.URLError as exc:
            raise LLMClientError(f"LLM request failed: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise LLMClientError(f"LLM response is not valid JSON: {exc}") from exc

        try:
            choice0 = data["choices"][0]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMClientError("LLM response missing choices[0]") from exc

        content = self._extract_choice_text(choice0)
        if not isinstance(content, str) or not content.strip():
            raise LLMClientError("LLM response missing textual content in choices[0]")
        return content

    @staticmethod
    def _extract_json_candidate(text: str) -> str:
        stripped = text.strip()
        # Some "thinking" models may emit hidden-thought sections.
        stripped = re.sub(r"<think>.*?</think>", "", stripped, flags=re.DOTALL | re.IGNORECASE).strip()
        if stripped.startswith("```"):
            match = re.search(r"```(?:json)?\s*(.*?)\s*```", stripped, flags=re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        # Fallback: extract the first top-level JSON object/array candidate.
        start_obj = stripped.find("{")
        start_arr = stripped.find("[")
        starts = [i for i in [start_obj, start_arr] if i >= 0]
        if starts:
            start = min(starts)
            candidate = stripped[start:].strip()
            # Trim trailing prose after final closing bracket.
            for closer in ["}", "]"]:
                if candidate.endswith(closer):
                    return candidate
            end_obj = candidate.rfind("}")
            end_arr = candidate.rfind("]")
            end = max(end_obj, end_arr)
            if end >= 0:
                return candidate[: end + 1].strip()
        return stripped

    def chat_json(self, system_prompt: str, user_prompt: str, max_tokens: int = 8192) -> Any:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        response_format = {"type": "json_object"}
        token_budgets = []
        t = max_tokens
        while t >= 1024:
            token_budgets.append(t)
            t //= 2
        if not token_budgets or token_budgets[-1] != 1024:
            token_budgets.append(1024)

        first: Optional[str] = None
        last_err: Optional[Exception] = None
        for budget in token_budgets:
            try:
                first = self._chat_once(messages, max_tokens=budget, response_format=response_format)
                break
            except LLMClientError as exc:
                msg = str(exc)
                last_err = exc
                if self._response_format_unsupported(msg):
                    first = self._chat_once(messages, max_tokens=budget, response_format=None)
                    break
                if self._max_tokens_too_large(msg):
                    continue
                raise
        if first is None:
            if last_err is not None:
                raise last_err
            raise LLMClientError("LLM request failed before receiving content")
        candidate = self._extract_json_candidate(first)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            retry_messages = messages + [
                {
                    "role": "assistant",
                    "content": first,
                },
                {
                    "role": "user",
                    "content": (
                        "Your previous response was not valid JSON. "
                        "Reply with exactly one valid JSON object only. "
                        "No markdown fences, no explanations, no surrounding text."
                    ),
                },
            ]
            retry_max_tokens = max_tokens
            try:
                second = self._chat_once(
                    retry_messages,
                    max_tokens=retry_max_tokens,
                    response_format=response_format,
                )
            except LLMClientError as exc:
                msg = str(exc)
                if self._response_format_unsupported(msg):
                    second = self._chat_once(retry_messages, max_tokens=retry_max_tokens, response_format=None)
                elif self._max_tokens_too_large(msg):
                    second = None
                    for budget in token_budgets:
                        try:
                            second = self._chat_once(
                                retry_messages,
                                max_tokens=budget,
                                response_format=response_format,
                            )
                            break
                        except LLMClientError as inner_exc:
                            inner_msg = str(inner_exc)
                            if self._response_format_unsupported(inner_msg):
                                second = self._chat_once(
                                    retry_messages,
                                    max_tokens=budget,
                                    response_format=None,
                                )
                                break
                            if self._max_tokens_too_large(inner_msg):
                                continue
                            raise
                    if second is None:
                        raise
                else:
                    raise
            candidate2 = self._extract_json_candidate(second)
            try:
                return json.loads(candidate2)
            except json.JSONDecodeError as exc:
                raise LLMClientError("LLM JSON parse failed after 1 retry") from exc
