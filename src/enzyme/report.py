from __future__ import annotations

from typing import Any


def render_report(
    core_ir: dict[str, Any],
    validation: dict[str, Any],
    scores: dict[str, Any],
    fmt: str = "md",
) -> str:
    if fmt != "md":
        raise ValueError(f"Unsupported format: {fmt}")

    issues = validation.get("issues", [])
    score_values = scores.get("scores", {})
    lines = [
        "# ENZYME Report",
        "",
        f"**Schema version:** {core_ir.get('schema_version')}",
        f"**IR kind:** {core_ir.get('ir_kind')}",
        f"**Validation:** {'PASS' if validation.get('pass') else 'FAIL'}",
        "",
        "## Scores",
    ]

    for key, value in score_values.items():
        lines.append(f"- **{key}**: {value}")

    lines.extend(["", "## Issues"])
    if not issues:
        lines.append("No issues reported.")
    else:
        for issue in issues:
            lines.append(
                f"- `{issue['code']}` ({issue['severity']}): {issue['message']} at {issue['path']}"
            )

    return "\n".join(lines) + "\n"
