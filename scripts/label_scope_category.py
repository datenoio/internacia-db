#!/usr/bin/env python3
"""Suggest scope_category labels; never mutate source YAML.

The legacy directory heuristic is advisory only. A reviewed manifest and
``backfill_scope_category.py`` are required for any data change.
"""

from __future__ import annotations

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
    "wbgroup",
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
}

TREATY_DIRS = {"agreement", "fta", "protocol"}
FORUM_DIRS = {"forum"}


def heuristic(path: Path, data: dict) -> str | None:
    rid = str(data.get("id") or path.stem)
    if rid in EXPLICIT:
        return EXPLICIT[rid]
    parent = path.parent.name
    bt = {str(b).lower() for b in (data.get("blocktype") or [])}
    if parent in REF_DIRS or bt & REF_DIRS:
        return "reference_enumeration"
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


def main() -> None:
    suggested = 0
    scanned = 0
    for path in sorted(INTBLOCKS.rglob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        scanned += 1
        # Never overwrite manually reviewed labels, including EXPLICIT ones.
        if data.get("scope_category") or data.get("status") != "formal":
            continue
        desired = heuristic(path, data)
        if not desired:
            continue
        print(f"Suggestion only: {data.get('id') or path.stem} -> {desired} ({path})")
        suggested += 1
    print(f"Suggested {suggested} / {scanned} intblock file(s); no source files changed")


if __name__ == "__main__":
    main()
