"""Guard the relationship between the compact and extended LLM indexes.

llms-full.txt is documented as the *extended* index: every non-empty line of
llms.txt must appear in llms-full.txt so the two files cannot drift apart.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_llms_full_is_superset_of_llms_txt():
    compact = (ROOT / "llms.txt").read_text(encoding="utf-8")
    full_lines = {
        line.strip()
        for line in (ROOT / "llms-full.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    missing = [
        line.strip()
        for line in compact.splitlines()
        if line.strip() and line.strip() not in full_lines
    ]
    assert not missing, f"llms-full.txt is missing lines from llms.txt: {missing[:10]}"


def test_llms_full_is_larger_than_compact():
    compact_size = (ROOT / "llms.txt").stat().st_size
    full_size = (ROOT / "llms-full.txt").stat().st_size
    assert full_size > compact_size, (
        f"llms-full.txt ({full_size} B) must be larger than llms.txt ({compact_size} B)"
    )
