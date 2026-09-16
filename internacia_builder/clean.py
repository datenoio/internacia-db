"""Normalization of source records so they conform to the export schemas."""

from __future__ import annotations

from typing import Any


def clean_data(data: list[dict[str, Any]], dataset_type: str) -> list[dict[str, Any]]:
    """
    Clean data to ensure consistency with schema.

    Fixes known issues:
    - Boolean 'lang' values (from 'no' parsed as False) -> converted to "no"
    - Inconsistent 'partof' field -> normalized to list of strings
    - Boolean values in string fields -> converted to strings
    - None values in required string fields -> converted to empty strings
    """
    cleaned_data = []

    # String fields that should never be None or bool
    string_fields = {
        "id",
        "status",
        "name",
        "founded",
        "geographic_scope",
        "wikidata_id",
        "legal_status",
        "description",
        "dissolved",
        "predecessor",
        "successor",
    }

    for item in data:
        # Deep copy to avoid modifying original if needed, but for now just modifying dict
        cleaned_item = item.copy()

        if dataset_type == "intblocks":
            # Fix boolean languages list
            if "languages" in cleaned_item:
                new_languages = []
                for lang in cleaned_item["languages"]:
                    if isinstance(lang, bool):
                        new_languages.append("no" if lang is False else "yes")
                    else:
                        new_languages.append(str(lang))
                cleaned_item["languages"] = new_languages

            # Normalize partof to list of strings
            if "partof" in cleaned_item:
                partof = cleaned_item["partof"]
                if partof is None:
                    cleaned_item["partof"] = []
                elif isinstance(partof, str):
                    cleaned_item["partof"] = [partof]
                elif isinstance(partof, dict):
                    # If it's a dict, it might be an ID->Name map or similar
                    # For now, let's just take keys if they look like IDs
                    cleaned_item["partof"] = list(partof.keys())
                elif isinstance(partof, list):
                    # Ensure all items are strings
                    cleaned_item["partof"] = [str(p) for p in partof]

            # Fix boolean values in string fields
            for field in string_fields:
                if field in cleaned_item:
                    if isinstance(cleaned_item[field], bool):
                        cleaned_item[field] = "yes" if cleaned_item[field] else "no"
                    elif cleaned_item[field] is None:
                        cleaned_item[field] = ""

            # Ensure includes fields are strings
            if "includes" in cleaned_item:
                for member in cleaned_item["includes"]:
                    if isinstance(member, dict):
                        for key in ["id", "name", "type", "status", "joined", "role", "note"]:
                            if key in member:
                                if isinstance(member[key], bool):
                                    member[key] = "yes" if member[key] else "no"
                                elif member[key] is None:
                                    member[key] = ""

            # Ensure links fields are strings
            if "links" in cleaned_item:
                for link in cleaned_item["links"]:
                    if isinstance(link, dict):
                        for key in ["url", "type"]:
                            if key in link:
                                if isinstance(link[key], bool):
                                    link[key] = "yes" if link[key] else "no"
                                elif link[key] is None:
                                    link[key] = ""

            # Ensure other_names fields are strings
            if "other_names" in cleaned_item:
                for name in cleaned_item["other_names"]:
                    if isinstance(name, dict):
                        for key in ["id", "name"]:
                            if key in name:
                                if isinstance(name[key], bool):
                                    name[key] = "yes" if name[key] else "no"
                                elif name[key] is None:
                                    name[key] = ""

            # Ensure acronyms fields are strings
            if "acronyms" in cleaned_item:
                for acronym in cleaned_item["acronyms"]:
                    if isinstance(acronym, dict):
                        for key in ["lang", "value"]:
                            if key in acronym:
                                if isinstance(acronym[key], bool):
                                    acronym[key] = "yes" if acronym[key] else "no"
                                elif acronym[key] is None:
                                    acronym[key] = ""

            # Ensure headquarters fields are strings/floats
            if "headquarters" in cleaned_item:
                hq = cleaned_item["headquarters"]
                if isinstance(hq, dict):
                    for key in ["city", "country"]:
                        if key in hq:
                            if isinstance(hq[key], bool):
                                hq[key] = "yes" if hq[key] else "no"
                            elif hq[key] is None:
                                hq[key] = ""
                    if "coordinates" in hq and isinstance(hq["coordinates"], dict):
                        for key in ["lat", "lng"]:
                            if key in hq["coordinates"]:
                                if isinstance(hq["coordinates"][key], bool):
                                    hq["coordinates"][key] = 0.0
                                elif hq["coordinates"][key] is None:
                                    hq["coordinates"][key] = 0.0

            # Ensure topics fields are strings
            if "topics" in cleaned_item:
                for topic in cleaned_item["topics"]:
                    if isinstance(topic, dict):
                        for key in ["key", "name"]:
                            if key in topic:
                                if isinstance(topic[key], bool):
                                    topic[key] = "yes" if topic[key] else "no"
                                elif topic[key] is None:
                                    topic[key] = ""

            # Normalize provenance entries (None -> [], None subfields -> "")
            prov = cleaned_item.get("provenance")
            if prov is None:
                cleaned_item["provenance"] = []
            elif isinstance(prov, list):
                for entry in prov:
                    if isinstance(entry, dict):
                        for key in ("field", "source", "url", "retrieved_at", "license"):
                            if key in entry and entry[key] is None:
                                entry[key] = ""

        if dataset_type == "countries":
            sub = cleaned_item.get("subregion")
            if isinstance(sub, str):
                cleaned_item["subregion"] = sub.strip()
            for key in ("region", "adminregion"):
                obj = cleaned_item.get(key)
                if isinstance(obj, dict) and isinstance(obj.get("value"), str):
                    obj["value"] = obj["value"].strip()

            if cleaned_item.get("borders") is None:
                cleaned_item["borders"] = []

            for field in ("population", "area", "gini"):
                val = cleaned_item.get(field)
                if isinstance(val, (int, float)) and field == "population":
                    cleaned_item[field] = {
                        "value": int(val),
                        "year": None,
                        "source": "legacy",
                        "source_id": "",
                    }
                elif isinstance(val, (int, float)) and field == "area":
                    cleaned_item[field] = {
                        "value": float(val),
                        "year": None,
                        "source": "legacy",
                        "source_id": "",
                    }
                elif isinstance(val, dict):
                    raw_year = val.get("year")
                    cleaned_item[field] = {
                        "value": val.get("value"),
                        # Unknown years export as null, never a fabricated 0.
                        "year": int(raw_year) if raw_year else None,
                        "source": str(val.get("source") or ""),
                        "source_id": str(val.get("source_id") or ""),
                    }

            cc = cleaned_item.get("capital_city")
            if isinstance(cc, dict):
                for coord in ("lat", "lng"):
                    if coord in cc and cc[coord] is not None:
                        try:
                            cc[coord] = float(cc[coord])
                        except (TypeError, ValueError):
                            cc[coord] = 0.0
                    elif coord not in cc:
                        cc[coord] = 0.0

            prov = cleaned_item.get("provenance")
            if prov is None:
                cleaned_item["provenance"] = []
            elif isinstance(prov, list):
                for entry in prov:
                    if isinstance(entry, dict):
                        for key in ("field", "source", "url", "retrieved_at", "license"):
                            if key in entry and entry[key] is None:
                                entry[key] = ""

        if dataset_type == "blocktypes":
            # Ensure other_names fields are strings
            if "other_names" in cleaned_item:
                if cleaned_item["other_names"] is None:
                    cleaned_item["other_names"] = []
                elif isinstance(cleaned_item["other_names"], list):
                    for name in cleaned_item["other_names"]:
                        if isinstance(name, dict):
                            for key in ["lang", "name"]:
                                if key in name:
                                    if isinstance(name[key], bool):
                                        name[key] = "yes" if name[key] else "no"
                                    elif name[key] is None:
                                        name[key] = ""
            # Ensure id and name are strings
            for field in ["id", "name"]:
                if field in cleaned_item:
                    if isinstance(cleaned_item[field], bool):
                        cleaned_item[field] = "yes" if cleaned_item[field] else "no"
                    elif cleaned_item[field] is None:
                        cleaned_item[field] = ""

        cleaned_data.append(cleaned_item)

    return cleaned_data
