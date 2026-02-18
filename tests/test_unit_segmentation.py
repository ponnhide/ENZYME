import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from run_paper_benchmark import clean_segmentation_text, postprocess_units, select_candidate_excerpt


def test_clean_segmentation_text_removes_table_overview_and_caption():
    raw = """
NATURE PROTOCOLS PROTOCOL
Stage Timing Experiments Step(s)
hPSCs d-1 Aggregate formation 1-10
50 uM Y27632

Figure 1 | Workflow overview
Materials and Methods
1 Wash cells with PBS.
2 Add medium and incubate.
""".strip()
    cleaned = clean_segmentation_text(raw)
    assert "Stage Timing Experiments Step(s)" not in cleaned
    assert "Figure 1 | Workflow overview" not in cleaned
    assert "1 Wash cells with PBS." in cleaned


def test_postprocess_units_merges_short_fragment_with_neighbor():
    units = [
        {
            "title": "Aggregate formation",
            "text": "2 × 105 cells per mL on 6-well low-attachment plate 50 μM Y27632",
            "rationale": "setup",
        },
        {
            "title": "Wash hPSCs",
            "text": "1 Wash hPSCs with 0.5 mM EDTA and replace medium.",
            "rationale": "step",
        },
    ]
    merged, stats = postprocess_units(units, max_units=10, min_chars=120, min_words=20)
    assert len(merged) == 1
    assert "2 × 105 cells per mL" in merged[0]["text"]
    assert "Wash hPSCs" in merged[0]["text"]
    assert stats["merged_short_forward"] >= 1


def test_select_candidate_excerpt_prefers_procedural_cues_beyond_head():
    prefix = "background discussion " * 2000
    tail = "1 Add medium and incubate cells for 30 min at 37 C."
    text = f"{prefix}\n{tail}\n"
    excerpt = select_candidate_excerpt(text, max_chars=800)
    assert "Add medium and incubate cells" in excerpt
