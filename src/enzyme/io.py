from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def canonicalize(data: Any) -> Any:
    if isinstance(data, dict):
        return {key: canonicalize(data[key]) for key in sorted(data.keys())}
    if isinstance(data, list):
        return [canonicalize(item) for item in data]
    return data


def write_json(path: str | Path, data: Any) -> None:
    canonical = canonicalize(data)
    with Path(path).open("w", encoding="utf-8") as handle:
        json.dump(canonical, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
