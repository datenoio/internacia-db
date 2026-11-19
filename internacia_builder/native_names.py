"""Country ``native_names``: an entity's names in its own languages.

Keys follow the record's ``languages[]`` through ``data/vocabs/language_codes.yaml``. ``official``
comes from the Wikidata official name (P1448) and ``common`` from the Wikidata label, falling back
to the native label (P1705) when the label repeats ``official``. Aliases are never used. Shared by
``scripts/enrich_countries.py`` and the country validators (openspec: fix-country-native-names).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from internacia_builder.paths import project_root

VOCAB_PARTS = ("data", "vocabs", "language_codes.yaml")
OFFICIAL_NAME = "P1448"
NATIVE_LABEL = "P1705"
END_TIME = "P582"
CHINESE = "zh"
# Wikidata codes for Chinese, by entity: the script the entity itself uses.
CHINESE_CODES = {
    "CN": ("zh-hans", "zh-cn"),
    "SG": ("zh-hans", "zh-sg"),
    "TW": ("zh-tw", "zh-hant"),
    "HK": ("zh-hk", "zh-hant"),
    "MO": ("zh-mo", "zh-hant"),
}
CHINESE_DEFAULT = ("zh-hans",)
ALL_CHINESE_CODES = tuple(sorted({c for codes in CHINESE_CODES.values() for c in codes} | {CHINESE}))

_VOCAB_CACHE: dict[str, dict[str, Any]] | None = None


def load_language_codes(root: Path | None = None) -> dict[str, dict[str, Any]]:
    """``{ISO 639-3 code: vocabulary entry}``; cached for the project root."""
    global _VOCAB_CACHE
    if root is None and _VOCAB_CACHE is not None:
        return _VOCAB_CACHE
    path = (root or project_root()).joinpath(*VOCAB_PARTS)
    entries = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    vocab = {str(e["id"]): e for e in entries if isinstance(e, dict) and e.get("id")}
    if root is None:
        _VOCAB_CACHE = vocab
    return vocab


def language_ids(record: dict[str, Any]) -> list[str]:
    """ISO 639-3 codes in ``languages[]``, in order, without duplicates."""
    codes = [str(lang.get("code") or "") for lang in record.get("languages") or [] if isinstance(lang, dict)]
    return list(dict.fromkeys(c for c in codes if c))


def allowed_keys(record: dict[str, Any], vocab: dict[str, dict[str, Any]]) -> set[str]:
    """Map keys the record's languages permit, whether or not Wikidata can name them."""
    return {str(vocab[c]["key"]) for c in language_ids(record) if c in vocab}


def wikidata_codes(record: dict[str, Any], vocab: dict[str, dict[str, Any]]) -> dict[str, tuple[str, ...]]:
    """``{map key: Wikidata language codes to try, in order}`` for languages that have codes."""
    out: dict[str, tuple[str, ...]] = {}
    for code in language_ids(record):
        entry = vocab.get(code)
        if not entry or not entry.get("wikidata_codes"):
            continue
        key = str(entry["key"])
        codes = tuple(str(c) for c in entry["wikidata_codes"])
        if key == CHINESE:
            codes = CHINESE_CODES.get(str(record.get("code") or ""), CHINESE_DEFAULT) + codes
        out[key] = tuple(dict.fromkeys(out.get(key, ()) + codes))
    return out


def requested_languages(records: list[dict[str, Any]], vocab: dict[str, dict[str, Any]]) -> list[str]:
    """Every Wikidata language code needed to build ``native_names`` for ``records``."""
    codes: set[str] = set()
    for record in records:
        for values in wikidata_codes(record, vocab).values():
            codes.update(values)
    return sorted(codes)


def _statements(entity: dict[str, Any], prop: str) -> list[tuple[str, str]]:
    """``(language, text)`` of current monolingual statements, preferred rank first."""
    found: list[tuple[int, int, str, str]] = []
    for order, claim in enumerate((entity.get("claims") or {}).get(prop) or []):
        value = ((claim.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        rank = claim.get("rank")
        if not isinstance(value, dict) or rank == "deprecated" or (claim.get("qualifiers") or {}).get(END_TIME):
            continue
        text = str(value.get("text") or "").strip()
        if text:
            found.append((0 if rank == "preferred" else 1, order, str(value.get("language") or ""), text))
    return [(lang, text) for _, _, lang, text in sorted(found)]


def _in_codes(statements: list[tuple[str, str]], codes: tuple[str, ...]) -> list[str]:
    return [text for code in codes for lang, text in statements if lang == code]


def build_native_names(
    record: dict[str, Any], entity: dict[str, Any], vocab: dict[str, dict[str, Any]]
) -> dict[str, dict[str, str]]:
    """``native_names`` for ``record`` from its Wikidata ``entity`` (claims and labels).

    For each language: ``official`` is the first P1448 value (by code order, then rank, then
    statement order) that differs from ``common``; ``common`` is the label, or the first P1705
    value that differs from ``official`` when the label is missing or repeats it. Missing
    values are omitted, and so is a language with neither.
    """
    labels = entity.get("labels") or {}
    official_names = _statements(entity, OFFICIAL_NAME)
    native_labels = _statements(entity, NATIVE_LABEL)
    names: dict[str, dict[str, str]] = {}
    for key, codes in sorted(wikidata_codes(record, vocab).items()):
        common = next(
            (str(labels[c]["value"]).strip() for c in codes if (labels.get(c) or {}).get("value")), None
        )
        candidates = _in_codes(official_names, codes)
        official = next((t for t in candidates if t != common), candidates[0] if candidates else None)
        if common is None or common == official:
            common = next((t for t in _in_codes(native_labels, codes) if t != official), common)
        entry = {k: v for k, v in (("official", official), ("common", common)) if v}
        if entry:
            names[key] = entry
    return names


def check_native_name_keys(record: dict[str, Any], vocab: dict[str, dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Every ``native_names`` key must be one of the record's mapped ``languages[]``."""
    vocab = vocab if vocab is not None else load_language_codes()
    allowed = allowed_keys(record, vocab)
    issues = []
    for key in sorted(str(k) for k in (record.get("native_names") or {})):
        if key not in allowed:
            issues.append({
                "issue_type": "NATIVE_NAME_LANGUAGE",
                "field": f"native_names.{key}",
                "current_value": key,
                "suggested_action": (
                    f"native_names key '{key}' is not one of the record's languages "
                    f"({sorted(allowed) or 'none'}); names in other languages belong in other_names"
                ),
            })
    return issues
