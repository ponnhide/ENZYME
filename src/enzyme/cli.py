from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from . import io
from .importers.protocolsio import import_protocolsio
from .lowering import lower_to_core
from .registry import Registry
from .report import render_report
from .scoring import score_core
from .validator import validate_core

app = typer.Typer(add_completion=False)
console = Console()


def _find_repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "enzyme_ir" / "schema_core.json").exists():
            return parent
    return Path.cwd()


ROOT = _find_repo_root()
SCHEMA_CORE = ROOT / "enzyme_ir" / "schema_core.json"
REGISTRY_PATH = ROOT / "registry" / "registry_v0_4.json"


@app.command("import")
def import_cmd(
    source: str = typer.Argument(..., help="Source type (e.g., protocolsio)"),
    input_path: Path = typer.Option(..., "--in", exists=True, readable=True),
    output_path: Path = typer.Option(..., "--out"),
) -> None:
    if source != "protocolsio":
        raise typer.BadParameter("Only protocolsio import is supported in MVP.")
    data = io.load_json(input_path)
    hl_ir = import_protocolsio(data)
    io.write_json(output_path, hl_ir)
    console.print(f"Imported HL-IR to {output_path}")


@app.command("compile")
def compile_cmd(
    input_path: Path = typer.Option(..., "--in", exists=True, readable=True),
    output_path: Path = typer.Option(..., "--out"),
) -> None:
    hl_ir = io.load_json(input_path)
    core_ir = lower_to_core(hl_ir)
    io.write_json(output_path, core_ir)
    console.print(f"Compiled Core-IR to {output_path}")


@app.command("validate")
def validate_cmd(
    input_path: Path = typer.Option(..., "--in", exists=True, readable=True),
    output_path: Path = typer.Option(..., "--out"),
) -> None:
    core_ir = io.load_json(input_path)
    registry = Registry.from_file(REGISTRY_PATH)
    validation = validate_core(core_ir, str(SCHEMA_CORE), registry)
    io.write_json(output_path, validation)
    console.print(f"Validation results written to {output_path}")


@app.command("score")
def score_cmd(
    input_path: Path = typer.Option(..., "--in", exists=True, readable=True),
    validation_path: Path = typer.Option(..., "--validation", exists=True, readable=True),
    output_path: Path = typer.Option(..., "--out"),
) -> None:
    core_ir = io.load_json(input_path)
    validation = io.load_json(validation_path)
    registry = Registry.from_file(REGISTRY_PATH)
    scores = score_core(core_ir, validation, registry)
    io.write_json(output_path, scores)
    console.print(f"Scores written to {output_path}")


@app.command("report")
def report_cmd(
    input_path: Path = typer.Option(..., "--in", exists=True, readable=True),
    validation_path: Path = typer.Option(..., "--validation", exists=True, readable=True),
    scores_path: Path = typer.Option(..., "--scores", exists=True, readable=True),
    fmt: str = typer.Option("md", "--format"),
    output_path: Path = typer.Option(..., "--out"),
) -> None:
    core_ir = io.load_json(input_path)
    validation = io.load_json(validation_path)
    scores = io.load_json(scores_path)
    report = render_report(core_ir, validation, scores, fmt=fmt)
    output_path.write_text(report, encoding="utf-8")
    console.print(f"Report written to {output_path}")


if __name__ == "__main__":
    app()
