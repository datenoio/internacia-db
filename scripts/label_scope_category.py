#!/usr/bin/env python3
"""Apply scope_category to intblocks via surgical YAML edits.

Labels EXPLICIT high-visibility ids, reference-enumeration directories, and
heuristic categories for remaining formal records missing the field.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
INTBLOCKS = ROOT / "data" / "intblocks"

EXPLICIT: dict[str, str] = {
    "UN": "igo",
    "NATO": "igo",
    "EU": "igo",
    "AU": "igo",
    "AFUNION": "igo",
    "ASEAN": "igo",
    "OAS": "igo",
    "WTO": "igo",
    "IMF": "igo",
    "WB": "igo",
    "IBRD": "igo",
    "WHO": "igo",
    "UNESCO": "igo",
    "ILO": "igo",
    "FAO": "igo",
    "ICAO": "igo",
    "INTERPOL": "igo",
    "ICRC": "igo",
    "OECD": "igo",
    "OSCE": "igo",
    "COE": "igo",
    "CEFTA": "treaty_body",
    "EEA": "treaty_body",
    "UNFCCC": "treaty_body",
    "CBD": "treaty_body",
    "UNCLOS": "treaty_body",
    "PARISAGREEMENT": "treaty_body",
    "KYOTOPROTOCOL": "treaty_body",
    "G7": "policy_forum",
    "G20": "policy_forum",
    "G8": "policy_forum",
    "FATF": "policy_forum",
    "FATFGREYLIST": "policy_forum",
    "ARF": "policy_forum",
    "BRICS": "policy_forum",
    "SEECP": "policy_forum",
    "RCC": "policy_forum",
}

REF_DIRS = {
    "geographic",
}

ORG_DIRS = {
    "political",
    "intorg",
    "unagency",
    "bank",
    "court",
    "military",
    "sports",
    "postal",
    "transport",
    "energy",
    "environment",
    "health",
    "education",
    "research",
    "scientific",
    "standards",
    "intelligence",
    "audit",
    "aviation",
    "parliamentary",
    "wbgroup",
}

TREATY_DIRS = {"agreement", "fta", "protocol"}
FORUM_DIRS = {"forum"}


def heuristic(path: Path, data: dict) -> str | None:
    rid = str(data.get("id") or path.stem)
    if rid in EXPLICIT:
        return EXPLICIT[rid]
    parent = path.parent.name
    if parent in REF_DIRS:
        return "reference_enumeration"
    bt = {str(b).lower() for b in (data.get("blocktype") or [])}
    legal = str(data.get("legal_status") or "").lower()
    if "agreement" in bt or legal == "treaty" or parent in TREATY_DIRS:
        return "treaty_body"
    if parent in FORUM_DIRS or "forum" in bt:
        return "policy_forum"
    if parent in ORG_DIRS or bt & {
        "political",
        "intorg",
        "unagency",
        "bank",
        "court",
        "military",
        "sports",
    }:
        return "igo"
    return None


def apply_category(path: Path, category: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if re.search(rf"^scope_category:\s*{re.escape(category)}\s*$", text, re.M):
        return False
    if re.search(r"^scope_category:\s*\S+", text, re.M):
        new = re.sub(r"^scope_category:\s*\S+.*$", f"scope_category: {category}", text, count=1, flags=re.M)
    elif re.search(r"^status:\s*\S+", text, re.M):
        new = re.sub(r"^(status:\s*\S+.*)$", rf"\1\nscope_category: {category}", text, count=1, flags=re.M)
    else:
        new = re.sub(r"^(id:\s*\S+.*)$", rf"\1\nscope_category: {category}", text, count=1, flags=re.M)
    if new == text:
        return False
    path.write_text(new, encoding="utf-8")
    return True


def main() -> None:
    updated = 0
    scanned = 0
    for path in sorted(INTBLOCKS.rglob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        scanned += 1
        # Only fill missing (do not overwrite manual labels unless EXPLICIT).
        existing = data.get("scope_category")
        rid = str(data.get("id") or path.stem)
        if existing and rid not in EXPLICIT:
            continue
        desired = heuristic(path, data)
        if not desired:
            continue
        if apply_category(path, desired):
            updated += 1
    print(f"Updated scope_category on {updated} / {scanned} intblock file(s)")


if __name__ == "__main__":
    main()
