#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_pdf_text.py

A practical, reproducible PDF → text extractor for ENZYME benchmarking.

Goals:
- Extract *raw* text as faithfully as possible (for LLM/ENZYME conversion).
- Preserve page provenance (optional JSON per page).
- Provide a light "clean" mode to reduce PDF line-wrapping artifacts.
- Avoid heavy dependencies; try the best available backend automatically.

Backends (auto order):
1) `pdftotext` (poppler)  — usually best for scientific PDFs
2) PyMuPDF (`fitz`)       — fast, good text extraction
3) pdfminer.six           — pure-python fallback

Notes:
- If your PDF is scanned (image-only), all of the above may output empty text.
  In that case, you need OCR (e.g., `ocrmypdf`, Tesseract). This script does not
  run OCR by default (to avoid surprising transformations of the source).

Usage examples:
  python extract_pdf_text.py paper.pdf -o paper.txt --pages-json paper.pages.json
  python extract_pdf_text.py paper.pdf -o paper.clean.txt --clean
  python extract_pdf_text.py paper.pdf -o out.txt --start "METHODS" --end "REFERENCES"

Author: ENZYME support utility
License: MIT (suggested)
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple


PAGE_BREAK = "\n\n" + ("=" * 14) + " PAGE {page} " + ("=" * 14) + "\n\n"


def which(cmd: str) -> Optional[str]:
    return shutil.which(cmd)


def _run_pdftotext(pdf_path: Path) -> List[str]:
    """
    Extract text using poppler's pdftotext, returning a list of page texts.

    Implementation detail:
    - We convert to a temporary text file using -layout for readability.
    - Then we split pages by form feed \f if present; otherwise return whole text as one page.
    """
    pdftotext = which("pdftotext")
    if not pdftotext:
        raise RuntimeError("pdftotext not available")

    tmp_txt = pdf_path.with_suffix(pdf_path.suffix + ".pdftotext.tmp.txt")
    try:
        # -layout: keep layout (helps headings/tables)
        # -enc UTF-8: avoid mojibake
        subprocess.run(
            [pdftotext, "-layout", "-enc", "UTF-8", str(pdf_path), str(tmp_txt)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        raw = tmp_txt.read_text(encoding="utf-8", errors="replace")
    finally:
        try:
            tmp_txt.unlink(missing_ok=True)
        except Exception:
            pass

    # Many pdftotext outputs contain form feed between pages
    if "\f" in raw:
        pages = raw.split("\f")
        # strip trailing whitespace; keep non-empty (but preserve empty pages if needed)
        return [p.rstrip() for p in pages]
    else:
        return [raw.rstrip()]


def _run_pymupdf(pdf_path: Path) -> List[str]:
    """
    Extract text using PyMuPDF, returning a list of page texts.
    """
    try:
        import fitz  # type: ignore
    except Exception as e:
        raise RuntimeError("PyMuPDF (fitz) not available") from e

    doc = fitz.open(str(pdf_path))
    pages: List[str] = []
    for i in range(len(doc)):
        page = doc.load_page(i)
        # "text" mode: plain text with line breaks
        txt = page.get_text("text")
        pages.append(txt.rstrip())
    doc.close()
    return pages


def _run_pdfminer(pdf_path: Path) -> List[str]:
    """
    Extract text using pdfminer.six. This is a fallback when other tools aren't available.
    """
    try:
        from pdfminer.high_level import extract_pages  # type: ignore
        from pdfminer.layout import LTTextContainer  # type: ignore
    except Exception as e:
        raise RuntimeError("pdfminer.six not available") from e

    pages: List[str] = []
    for page_layout in extract_pages(str(pdf_path)):
        chunks: List[str] = []
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                chunks.append(element.get_text())
        pages.append("".join(chunks).rstrip())
    return pages


def extract_pages_auto(pdf_path: Path, method: str) -> Tuple[str, List[str]]:
    """
    Returns (used_method, pages_text).
    """
    method = method.lower()
    if method not in {"auto", "pdftotext", "pymupdf", "pdfminer"}:
        raise ValueError(f"Unknown method: {method}")

    errors: List[str] = []

    def try_one(name: str):
        if name == "pdftotext":
            return _run_pdftotext(pdf_path)
        if name == "pymupdf":
            return _run_pymupdf(pdf_path)
        if name == "pdfminer":
            return _run_pdfminer(pdf_path)
        raise AssertionError(name)

    if method != "auto":
        return method, try_one(method)

    for candidate in ["pdftotext", "pymupdf", "pdfminer"]:
        try:
            pages = try_one(candidate)
            # Consider it successful if we got any non-whitespace across pages
            if any(p.strip() for p in pages):
                return candidate, pages
            else:
                errors.append(f"{candidate}: extracted empty text (possibly scanned PDF)")
        except Exception as e:
            errors.append(f"{candidate}: {e}")

    raise RuntimeError("All extraction methods failed:\n- " + "\n- ".join(errors))


def clean_text(text: str) -> str:
    """
    Light cleaning designed for LLM consumption:
    - dehyphenate line breaks where appropriate
    - normalize multiple spaces
    - keep paragraph breaks
    """
    # Remove hyphenation at line breaks: "micro-\nscope" -> "microscope"
    # Heuristic: hyphen followed by newline and a lowercase letter
    text = re.sub(r"(\w)-\n([a-z])", r"\1\2", text)

    # Convert Windows newlines
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Collapse runs of spaces (not newlines)
    text = re.sub(r"[ \t]+", " ", text)

    # Trim trailing spaces on each line
    text = "\n".join(line.rstrip() for line in text.split("\n"))

    # Collapse >3 consecutive blank lines to 2
    text = re.sub(r"\n{4,}", "\n\n\n", text)

    return text.strip() + "\n"


def slice_section(text: str, start_pat: Optional[str], end_pat: Optional[str]) -> str:
    """
    Extract a substring between start_pat and end_pat (regex, case-insensitive).
    If patterns are not found, return original text (best-effort).
    """
    if not start_pat and not end_pat:
        return text

    flags = re.IGNORECASE | re.MULTILINE
    start_i = 0
    if start_pat:
        m = re.search(start_pat, text, flags)
        if m:
            start_i = m.start()
        else:
            return text  # best-effort

    end_i = len(text)
    if end_pat:
        m2 = re.search(end_pat, text[start_i:], flags)
        if m2:
            end_i = start_i + m2.start()
        else:
            return text  # best-effort

    return text[start_i:end_i].strip() + "\n"


def format_pages(pages: List[str], with_page_breaks: bool) -> str:
    if not with_page_breaks:
        return "\n\n".join(p.strip() for p in pages if p is not None) + "\n"

    out_parts: List[str] = []
    for idx, p in enumerate(pages, start=1):
        out_parts.append(PAGE_BREAK.format(page=idx))
        out_parts.append(p.strip() + "\n")
    return "".join(out_parts)


def parse_page_ranges(spec: Optional[str], n_pages: int) -> List[int]:
    """
    Convert a spec like "1-3,5,7-" into 0-based page indices.
    Empty spec -> all pages.
    """
    if not spec:
        return list(range(n_pages))

    indices: List[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            a = a.strip()
            b = b.strip()
            start = int(a) if a else 1
            end = int(b) if b else n_pages
            for p in range(start, end + 1):
                if 1 <= p <= n_pages:
                    indices.append(p - 1)
        else:
            p = int(part)
            if 1 <= p <= n_pages:
                indices.append(p - 1)

    # de-dup while preserving order
    seen = set()
    out = []
    for i in indices:
        if i not in seen:
            out.append(i)
            seen.add(i)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract text from a PDF for ENZYME benchmarking.")
    ap.add_argument("pdf", type=str, help="Input PDF path")
    ap.add_argument("-o", "--out", type=str, required=True, help="Output .txt path")
    ap.add_argument("--method", type=str, default="auto", choices=["auto", "pdftotext", "pymupdf", "pdfminer"])
    ap.add_argument("--pages", type=str, default=None, help="Page ranges (1-based), e.g. '1-3,5,7-'")
    ap.add_argument("--pages-json", type=str, default=None, help="Optional output JSON with per-page text")
    ap.add_argument("--keep-page-breaks", action="store_true", help="Insert explicit page break markers")
    ap.add_argument("--clean", action="store_true", help="Apply light cleaning (recommended for LLM input)")
    ap.add_argument("--start", type=str, default=None, help="Regex for section start (case-insensitive)")
    ap.add_argument("--end", type=str, default=None, help="Regex for section end (case-insensitive)")

    args = ap.parse_args()

    pdf_path = Path(args.pdf).expanduser().resolve()
    if not pdf_path.exists():
        print(f"ERROR: PDF not found: {pdf_path}", file=sys.stderr)
        return 2

    used_method, pages = extract_pages_auto(pdf_path, args.method)

    page_idxs = parse_page_ranges(args.pages, len(pages))
    pages_sel = [pages[i] for i in page_idxs]

    combined = format_pages(pages_sel, with_page_breaks=args.keep_page_breaks)
    combined = slice_section(combined, args.start, args.end)
    if args.clean:
        combined = clean_text(combined)

    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(combined, encoding="utf-8", errors="replace")

    if args.pages_json:
        pages_json_path = Path(args.pages_json).expanduser().resolve()
        pages_json_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "source_pdf": str(pdf_path),
            "extraction_method": used_method,
            "pages_1based": [i + 1 for i in page_idxs],
            "page_text": [pages[i] for i in page_idxs],
        }
        pages_json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    # Print a short status line for logs
    nonempty = sum(1 for p in pages_sel if p.strip())
    print(f"[extract_pdf_text] method={used_method} pages={len(page_idxs)} nonempty_pages={nonempty} out={out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
