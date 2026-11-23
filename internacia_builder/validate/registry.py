"""The rule registry shared by the CLI validators and ``analyze-quality``.

Every data-quality rule is listed here once, with the dataset it belongs to and its
severity in the validators (``error`` fails ``validate_countries``/``validate_intblocks``,
``warning`` is reported and fails them under ``--fail-on-warning``, ``None`` runs only in
``analyze-quality``). A ``dated`` warning rule compares a recorded date with today, so it
starts firing as time passes without any change to the data; ``--fail-on-warning`` reports
it but does not fail on it. Both consumers load
their inputs with :func:`load_context` and run the rules with :func:`run_rules`, so a rule
added here is enforced by the validators and reported by ``analyze-quality`` alike.

Checks that are not about record quality stay with their consumer: repository-state gates
(release identifier stability, changed records without ``last_verified``, the tier-1 roster)
and the validators' aggregate summaries (completeness and description-quality rates,
membership applicability and include-status totals).
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any

import yaml

from internacia_builder import wb_classification
from internacia_builder.paths import blocktypes_source_path
from internacia_builder.validate import (
    border_rules,
    completeness,
    country_rules,
    cross_rules,
    intblock_rules,
    trade_agreement_rules,
)
from internacia_builder.yaml_io import safe_load

Issue = dict[str, Any]

COUNTRIES = "countries"
INTBLOCKS = "intblocks"


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return safe_load(f)


def load_topic_aliases(path: Path) -> dict[str, str]:
    """Deprecated topic key -> canonical key, from data/schemas/topic_aliases.yaml."""
    if not path.exists():
        return {}
    data = load_yaml(path) or {}
    raw = data.get("aliases") or {}
    return {str(k): str(v.get("canonical", "")) for k, v in raw.items() if isinstance(v, dict)}


def load_topic_catalog(path: Path) -> set[str]:
    """Canonical topic keys from data/schemas/topics.yaml."""
    if not path.exists():
        return set()
    data = load_yaml(path) or {}
    return {str(k) for k in (data.get("topics") or {})}


def load_wikidata_exclusions(path: Path) -> set[str]:
    """Intblock ids exempt from the wikidata_id requirement."""
    if not path.exists():
        return set()
    data = load_yaml(path) or {}
    return {
        str(entry.get("id"))
        for entry in (data.get("exclusions") or [])
        if isinstance(entry, dict) and entry.get("id")
    }


def load_deprecated_blocktype_baseline(path: Path) -> dict[str, set[str]]:
    """Deprecated blocktype -> the record ids that carried it when it was deprecated."""
    if not path.exists():
        return {}
    data = load_yaml(path) or {}
    return {
        str(bt): {str(i) for i in (spec.get("ids") or [])}
        for bt, spec in (data.get("blocktypes") or {}).items()
        if isinstance(spec, dict)
    }


@dataclass
class Dataset:
    """Parsed YAML records of one dataset, with paths relative to the project root."""

    directory: Path
    records: list[dict[str, Any]] = field(default_factory=list)
    paths: list[str] = field(default_factory=list)
    errors: list[tuple[str, str]] = field(default_factory=list)
    file_count: int = 0

    @classmethod
    def load(cls, directory: Path, root: Path, pattern: str) -> Dataset:
        dataset = cls(directory)
        if not directory.exists():
            return dataset
        for path in sorted(directory.glob(pattern)):
            dataset.file_count += 1
            rel = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
            try:
                record = load_yaml(path)
            except yaml.YAMLError as exc:
                dataset.errors.append((rel, f"YAML parse error: {exc}"))
                continue
            if not isinstance(record, dict):
                dataset.errors.append((rel, "expected a mapping at the document root"))
                continue
            dataset.records.append(record)
            dataset.paths.append(rel)
        return dataset


@dataclass
class RuleContext:
    """Configuration and records the rules run against, loaded once per run."""

    root: Path
    countries: Dataset
    intblocks: Dataset
    country_schema: dict[str, Any]
    intblock_schema: dict[str, Any]
    countries_cfg: dict[str, Any]
    intblocks_cfg: dict[str, Any]
    crosswalk_policy: dict[str, Any]
    taxonomy: set[str]
    aliases: list[dict[str, Any]] | None
    attribute_migrations: list[dict[str, Any]] | None
    topic_aliases: dict[str, str]
    topic_catalog: set[str]
    includes_status_catalog: dict[str, dict[str, Any]]
    wikidata_exclusions: set[str]
    check_http: bool = False
    check_wikidata: bool = False
    blocktype_catalog: dict[str, dict[str, Any]] = field(default_factory=dict)
    deprecated_blocktype_baseline: dict[str, set[str]] = field(default_factory=dict)
    include_roles_catalog: dict[str, Any] = field(default_factory=dict)
    border_status: dict[str, Any] | None = None
    border_status_schema: dict[str, Any] = field(default_factory=dict)
    trade_agreements: Dataset | None = None
    trade_agreements_schema: dict[str, Any] = field(default_factory=dict)

    @cached_property
    def trade_agreement_ids(self) -> set[str]:
        if self.trade_agreements is None:
            return set()
        return {str(r["id"]) for r in self.trade_agreements.records if r.get("id")}

    def dataset(self, name: str) -> Dataset:
        return self.countries if name == COUNTRIES else self.intblocks

    @cached_property
    def country_codes(self) -> set[str]:
        return {str(r["code"]) for r in self.countries.records if r.get("code")}

    @cached_property
    def countries_by_code(self) -> dict[str, dict[str, Any]]:
        return {str(r["code"]): r for r in self.countries.records if r.get("code")}

    @cached_property
    def intblock_ids(self) -> set[str]:
        return {str(r["id"]) for r in self.intblocks.records if r.get("id")}

    @cached_property
    def alias_names(self) -> set[str]:
        return {str(a.get("alias") or "") for a in self.aliases or [] if isinstance(a, dict)} - {""}

    @property
    def igo_legal_status_allowlist(self) -> frozenset[str]:
        scope = self.intblocks_cfg.get("scope_category") or {}
        return frozenset(str(x) for x in (scope.get("igo_legal_status_allowlist") or []))

    @property
    def references_cfg(self) -> dict[str, Any]:
        return self.intblocks_cfg.get("references") or {}

    def allowlist(self, key: str) -> set[str]:
        return {str(x) for x in (self.references_cfg.get(key) or [])}

    @property
    def countries_provenance(self) -> dict[str, Any]:
        return self.countries_cfg.get("provenance") or {}

    @property
    def intblocks_provenance(self) -> dict[str, Any]:
        return (self.intblocks_cfg.get("fields") or {}).get("provenance") or {}

    @property
    def region_allowlist(self) -> set[str]:
        return {
            str(x)
            for x in ((self.countries_cfg.get("region_hierarchy") or {}).get("allowlist") or [])
        }

    @property
    def last_verified_max_age(self) -> int:
        return int((self.intblocks_cfg.get("quality") or {}).get("last_verified_max_age_months") or 0)


def load_context(
    root: Path,
    *,
    countries_dir: Path | None = None,
    intblocks_dir: Path | None = None,
    check_http: bool = False,
    check_wikidata: bool = False,
    datasets: tuple[str, ...] = (COUNTRIES, INTBLOCKS),
) -> RuleContext:
    """Load every rule input; raises if a schema or configuration file cannot be read.

    Datasets not in ``datasets`` are left empty (their rules then see no records).
    """
    schemas = root / "data" / "schemas"
    blocktypes_path = blocktypes_source_path(root)
    aliases_path = root / "data" / "intblocks_aliases.yaml"
    migrations_path = root / "data" / "attribute_intblock_migrations.yaml"
    border_status_path = root / "data" / "borders" / "border_status.yaml"
    trade_agreements_dir = root / "data" / "trade_agreements"
    blocktype_catalog: dict[str, dict[str, Any]] = {}
    if blocktypes_path.exists():
        blocktype_catalog = {
            str(b.get("id", "")): b for b in (load_yaml(blocktypes_path) or []) if isinstance(b, dict)
        }
    taxonomy: set[str] = set(blocktype_catalog)
    countries_dir = countries_dir or root / "data" / "countries"
    intblocks_dir = intblocks_dir or root / "data" / "intblocks"
    return RuleContext(
        root=root,
        countries=(Dataset.load(countries_dir, root, "*.yaml") if COUNTRIES in datasets
                   else Dataset(countries_dir)),
        intblocks=(Dataset.load(intblocks_dir, root, "**/*.yaml") if INTBLOCKS in datasets
                   else Dataset(intblocks_dir)),
        country_schema=json.loads((schemas / "countries.schema.json").read_text(encoding="utf-8")),
        intblock_schema=json.loads((schemas / "intblocks.schema.json").read_text(encoding="utf-8")),
        countries_cfg=load_yaml(schemas / "countries_completeness.yaml") or {},
        intblocks_cfg=load_yaml(schemas / "intblocks_completeness.yaml") or {},
        crosswalk_policy=load_yaml(schemas / "country_crosswalk_exclusions.yaml") or {},
        taxonomy=taxonomy,
        aliases=(load_yaml(aliases_path) or []) if aliases_path.exists() else None,
        attribute_migrations=(load_yaml(migrations_path) or []) if migrations_path.exists() else None,
        topic_aliases=load_topic_aliases(schemas / "topic_aliases.yaml"),
        topic_catalog=load_topic_catalog(schemas / "topics.yaml"),
        includes_status_catalog=completeness.load_includes_status_catalog(schemas),
        wikidata_exclusions=load_wikidata_exclusions(schemas / "wikidata_exclusions.yaml"),
        check_http=check_http,
        check_wikidata=check_wikidata,
        blocktype_catalog=blocktype_catalog,
        deprecated_blocktype_baseline=load_deprecated_blocktype_baseline(
            schemas / "deprecated_blocktypes_baseline.yaml"),
        include_roles_catalog=(load_yaml(schemas / "include_roles.yaml") or {})
        if (schemas / "include_roles.yaml").exists() else {},
        border_status=(load_yaml(border_status_path) or {}) if border_status_path.exists() else None,
        border_status_schema=json.loads((schemas / "border_status.schema.json").read_text(encoding="utf-8"))
        if (schemas / "border_status.schema.json").exists() else {},
        trade_agreements=(Dataset.load(trade_agreements_dir, root, "*.yaml")
                          if INTBLOCKS in datasets and trade_agreements_dir.exists() else None),
        trade_agreements_schema=json.loads((schemas / "trade_agreements.schema.json").read_text(encoding="utf-8"))
        if (schemas / "trade_agreements.schema.json").exists() else {},
    )


def _default_message(issue: Issue) -> str:
    return f"{issue['file_path']}: {issue['suggested_action']}"


def _action_only(issue: Issue) -> str:
    return str(issue["suggested_action"])


def _schema_message(issue: Issue) -> str:
    return f"{issue['file_path']}: {issue['field']}: {issue['message']}"


def _always(ctx: RuleContext) -> bool:
    return True


def _has_countries(ctx: RuleContext) -> bool:
    return ctx.countries.directory.exists()


@dataclass(frozen=True)
class Rule:
    """One check. Record rules get ``(ctx, record, rel_path)``; cross rules get ``ctx``.

    ``dated`` marks a freshness rule whose findings appear as the calendar advances (an age
    limit on a recorded date), so ``--fail-on-warning`` does not count them.
    """

    name: str
    dataset: str
    severity: str | None
    check: Callable[..., list[Issue]]
    cross: bool = False
    message: Callable[[Issue], str] = _default_message
    enabled: Callable[[RuleContext], bool] = _always
    dated: bool = False


def _record(name, dataset, severity, check, **kwargs) -> Rule:
    return Rule(name, dataset, severity, check, **kwargs)


def _cross(name, dataset, severity, check, **kwargs) -> Rule:
    return Rule(name, dataset, severity, check, cross=True, **kwargs)


E, W, REPORT = "error", "warning", None

COUNTRY_RULES: tuple[Rule, ...] = (
    _record("schema", COUNTRIES, E, lambda ctx, r, p: country_rules.check_country_schema(r, ctx.country_schema),
            message=_schema_message),
    _record("borders", COUNTRIES, E, lambda ctx, r, p: country_rules.check_country_borders(r)),
    _record("indicator years", COUNTRIES, E, lambda ctx, r, p: country_rules.check_country_indicator_years(r)),
    _record("filename", COUNTRIES, E, lambda ctx, r, p: country_rules.check_country_filename(r, p)),
    _record("indicator values", COUNTRIES, W, lambda ctx, r, p: country_rules.check_country_indicator_values(r)),
    _record("whitespace", COUNTRIES, W, lambda ctx, r, p: country_rules.check_country_whitespace(r),
            message=lambda i: f"{i['file_path']}: {i['field']} has leading/trailing whitespace"),
    _record("entity status", COUNTRIES, E, lambda ctx, r, p: country_rules.check_country_entity_status(r)),
    _record("entity flags", COUNTRIES, W, lambda ctx, r, p: country_rules.check_country_entity_flags(r)),
    _record("coordinates", COUNTRIES, W, lambda ctx, r, p: country_rules.check_country_coordinates(r)),
    _record("currency codes", COUNTRIES, W, lambda ctx, r, p: country_rules.check_country_currency_codes(r)),
    _record("provenance integrity", COUNTRIES, W, lambda ctx, r, p: country_rules.check_provenance_integrity(r)),
    _record("crosswalk provenance", COUNTRIES, E,
            lambda ctx, r, p: country_rules.check_country_crosswalk_provenance(r)),
    _record("provenance count", COUNTRIES, W,
            lambda ctx, r, p: country_rules.check_provenance_count(
                r, min_count=int(ctx.countries_provenance.get("min_count") or 0)),
            enabled=lambda ctx: int(ctx.countries_provenance.get("min_count") or 0) > 0),
    _record("tld", COUNTRIES, W, lambda ctx, r, p: country_rules.check_country_tld(r)),
    _record("calling codes", COUNTRIES, W, lambda ctx, r, p: country_rules.check_country_calling_codes(r)),
    _record("timezones", COUNTRIES, W, lambda ctx, r, p: country_rules.check_country_timezones(r)),
    _record("flag emoji", COUNTRIES, W, lambda ctx, r, p: country_rules.check_country_flag_emoji(r)),
    _record("landlocked", COUNTRIES, W, lambda ctx, r, p: country_rules.check_country_landlocked(r)),
    _record("attribute fields", COUNTRIES, E, lambda ctx, r, p: country_rules.check_country_attribute_fields(r)),
    _record("region hierarchy", COUNTRIES, W,
            lambda ctx, r, p: country_rules.check_country_region_hierarchy(r, ctx.region_allowlist)),
    _record("capital distance", COUNTRIES, W,
            lambda ctx, r, p: country_rules.check_country_capital_distance(r, ctx.countries_cfg)),
    _record("text encoding", COUNTRIES, W, lambda ctx, r, p: country_rules.check_country_text_encoding(r)),
    _record("native name languages", COUNTRIES, W, lambda ctx, r, p: country_rules.check_country_native_names(r)),
    _cross("duplicate identifiers", COUNTRIES, E,
           lambda ctx: country_rules.check_country_duplicates(ctx.countries.records, ctx.countries.paths),
           message=lambda i: (f"duplicate {i['field']} '{i['current_value']}' in {i['file_path']} "
                              f"and {i['other_path']}")),
    _cross("official ISO count", COUNTRIES, E,
           lambda ctx: country_rules.validate_official_iso_count(ctx.countries.records),
           message=lambda i: f"entity policy: {i['suggested_action']}"),
    _cross("crosswalk uniqueness", COUNTRIES, E,
           lambda ctx: country_rules.check_country_crosswalk_uniqueness(
               ctx.countries.records, ctx.countries.paths)),
    _cross("crosswalk policy", COUNTRIES, E,
           lambda ctx: country_rules.check_country_crosswalk_policy(
               ctx.countries.records, ctx.countries.paths, ctx.crosswalk_policy)),
    _cross("border resolution", COUNTRIES, E,
           lambda ctx: cross_rules.check_border_resolution(ctx.countries.records, ctx.countries.paths)),
    _cross("border reciprocity", COUNTRIES, W,
           lambda ctx: cross_rules.check_border_reciprocity(
               ctx.countries.records, ctx.countries.paths,
               cross_rules.load_border_reciprocity_allowlist(ctx.countries_cfg))),
    _cross("border status", COUNTRIES, E,
           lambda ctx: border_rules.check_border_status(
               ctx.border_status, ctx.border_status_schema, ctx.countries.records),
           message=lambda i: f"{i['file_path']}: {i['field']}: {i['suggested_action']}",
           enabled=lambda ctx: ctx.border_status is not None),
    _cross("border status freshness", COUNTRIES, W,
           lambda ctx: border_rules.check_border_status_freshness(ctx.border_status, ctx.last_verified_max_age),
           message=lambda i: f"{i['file_path']}: {i['field']}: {i['suggested_action']}",
           enabled=lambda ctx: ctx.border_status is not None and ctx.last_verified_max_age > 0,
           dated=True),
    _cross("parent entity references", COUNTRIES, W,
           lambda ctx: cross_rules.check_parent_entity_refs(ctx.countries.records, ctx.countries.paths)),
    _cross("completeness", COUNTRIES, REPORT,
           lambda ctx: country_rules.validate_completeness(ctx.countries.records, ctx.countries_cfg)),
    _record("provenance freshness", COUNTRIES, W,
            lambda ctx, r, p: country_rules.check_provenance_freshness(
                r, max_age_months=int(ctx.countries_provenance.get("max_age_months") or 0)),
            enabled=lambda ctx: int(ctx.countries_provenance.get("max_age_months") or 0) > 0,
            dated=True),
)

INTBLOCK_RULES: tuple[Rule, ...] = (
    _record("schema", INTBLOCKS, E, lambda ctx, r, p: intblock_rules.check_intblock_schema(r, ctx.intblock_schema),
            message=_schema_message),
    _cross("duplicate ids", INTBLOCKS, E,
           lambda ctx: intblock_rules.check_intblock_duplicates(ctx.intblocks.records, ctx.intblocks.paths),
           message=lambda i: f"duplicate id '{i['current_value']}' in {i['file_path']} and {i['other_path']}"),
    _record("filename", INTBLOCKS, E, lambda ctx, r, p: intblock_rules.check_intblock_filename(r, p)),
    _record("blocktypes", INTBLOCKS, E, lambda ctx, r, p: intblock_rules.check_intblock_blocktypes(r, ctx.taxonomy),
            message=lambda i: f"{i['file_path']}: unknown blocktype '{i['current_value']}'",
            enabled=lambda ctx: bool(ctx.taxonomy)),
    _record("directory alignment", INTBLOCKS, E,
            lambda ctx, r, p: intblock_rules.check_intblock_directory_alignment(r, p)),
    _cross("blocktype descriptions", INTBLOCKS, E,
           lambda ctx: intblock_rules.check_blocktype_descriptions(ctx.blocktype_catalog),
           enabled=lambda ctx: bool(ctx.blocktype_catalog)),
    _record("deprecated primary blocktype", INTBLOCKS, E,
            lambda ctx, r, p: intblock_rules.check_deprecated_primary_blocktype(r, ctx.blocktype_catalog)),
    _cross("deprecated blocktype ratchet", INTBLOCKS, E,
           lambda ctx: intblock_rules.check_deprecated_blocktype_ratchet(
               ctx.intblocks.records, ctx.intblocks.paths, ctx.blocktype_catalog,
               ctx.deprecated_blocktype_baseline, ctx.alias_names),
           enabled=lambda ctx: any(spec.get("deprecated") for spec in ctx.blocktype_catalog.values())),
    _cross("partof hierarchy", INTBLOCKS, E,
           lambda ctx: cross_rules.check_partof_hierarchy(ctx.intblocks.records, ctx.intblocks.paths)),
    _cross("wikidata completeness", INTBLOCKS, E,
           lambda ctx: cross_rules.check_wikidata_completeness(
               ctx.intblocks.records, ctx.intblocks.paths, ctx.wikidata_exclusions)),
    _record("topics present", INTBLOCKS, W, lambda ctx, r, p: intblock_rules.check_intblock_topics_present(r),
            message=lambda i: f"{i['file_path']}: missing topics"),
    _record("topics", INTBLOCKS, W,
            lambda ctx, r, p: intblock_rules.check_intblock_topics(r, ctx.topic_aliases, ctx.topic_catalog)),
    _cross("partof references", INTBLOCKS, W,
           lambda ctx: cross_rules.validate_partof_refs(ctx.intblocks.records, ctx.intblocks.paths),
           message=lambda i: f"{i['file_path']}: partof '{i['current_value']}' does not match any intblock id"),
    _record("lifecycle", INTBLOCKS, W, lambda ctx, r, p: intblock_rules.check_intblock_lifecycle(r)),
    _record("chronology", INTBLOCKS, W, lambda ctx, r, p: intblock_rules.check_intblock_chronology(r)),
    _record("include dates", INTBLOCKS, W, lambda ctx, r, p: intblock_rules.check_intblock_include_dates(r),
            message=lambda i: f"{i['file_path']}: {i['field']}: {i['suggested_action']}"),
    _record("membership consistency", INTBLOCKS, W,
            lambda ctx, r, p: intblock_rules.check_intblock_membership_consistency(r, ctx.intblocks_cfg)),
    _record("last verified", INTBLOCKS, W,
            lambda ctx, r, p: intblock_rules.check_intblock_last_verified(
                r, max_age_months=ctx.last_verified_max_age),
            enabled=lambda ctx: ctx.last_verified_max_age > 0,
            dated=True),
    _record("scope category", INTBLOCKS, E,
            lambda ctx, r, p: intblock_rules.check_intblock_scope_category(r, ctx.igo_legal_status_allowlist)),
    _record("institutional design", INTBLOCKS, E,
            lambda ctx, r, p: intblock_rules.check_intblock_institutional_design(r)),
    _record("veto holders under consensus", INTBLOCKS, W,
            lambda ctx, r, p: intblock_rules.check_intblock_veto_under_consensus(r)),
    _record("include roles", INTBLOCKS, E,
            lambda ctx, r, p: intblock_rules.check_intblock_include_roles(r, ctx.include_roles_catalog)),
    _cross("scope coverage", INTBLOCKS, E,
           lambda ctx: intblock_rules.check_scope_coverage(ctx.intblocks.records, ctx.intblocks_cfg),
           message=_action_only),
    _record("text encoding", INTBLOCKS, W, lambda ctx, r, p: intblock_rules.check_intblock_text_encoding(r)),
    _record("provenance integrity", INTBLOCKS, W, lambda ctx, r, p: country_rules.check_provenance_integrity(r)),
    _cross("lineage reciprocity", INTBLOCKS, W,
           lambda ctx: cross_rules.check_successor_reciprocity(ctx.intblocks.records, ctx.intblocks.paths)),
    _cross("partof/suborganization reciprocity", INTBLOCKS, W,
           lambda ctx: cross_rules.check_partof_suborg_reciprocity(
               ctx.intblocks.records, ctx.intblocks.paths)),
    _cross("alias integrity", INTBLOCKS, E,
           lambda ctx: cross_rules.validate_aliases(ctx.aliases or [], ctx.intblock_ids, ctx.trade_agreement_ids),
           message=_action_only, enabled=lambda ctx: ctx.aliases is not None),
    _cross("trade agreement files", INTBLOCKS, E,
           lambda ctx: trade_agreement_rules.check_trade_agreement_files(ctx.trade_agreements.errors),
           message=lambda i: f"{i['file_path']}: {i['suggested_action']}",
           enabled=lambda ctx: ctx.trade_agreements is not None),
    _cross("trade agreements", INTBLOCKS, E,
           lambda ctx: trade_agreement_rules.check_trade_agreements(
               ctx.trade_agreements.records, ctx.trade_agreements.paths, ctx.trade_agreements_schema,
               ctx.intblocks.records, ctx.country_codes, ctx.aliases),
           message=lambda i: f"{i['file_path']}: {i['field']}: {i['suggested_action']}",
           enabled=lambda ctx: ctx.trade_agreements is not None),
    _cross("trade agreement preference schemes", INTBLOCKS, E,
           lambda ctx: trade_agreement_rules.check_preference_schemes(
               ctx.trade_agreements.records, ctx.trade_agreements.paths, ctx.intblocks.records),
           message=lambda i: f"{i['file_path']}: {i['field']}: {i['suggested_action']}",
           enabled=lambda ctx: ctx.trade_agreements is not None),
    _cross("trade agreement party dates", INTBLOCKS, E,
           lambda ctx: trade_agreement_rules.check_party_dates(ctx.trade_agreements.records, ctx.trade_agreements.paths),
           message=lambda i: f"{i['file_path']}: {i['field']}: {i['suggested_action']}",
           enabled=lambda ctx: ctx.trade_agreements is not None),
    _cross("trade agreement intblock candidates", INTBLOCKS, REPORT,
           lambda ctx: trade_agreement_rules.check_intblock_candidates(
               ctx.trade_agreements.records, ctx.trade_agreements.paths),
           enabled=lambda ctx: ctx.trade_agreements is not None),
    _cross("trade agreement instruments before agreement", INTBLOCKS, REPORT,
           lambda ctx: trade_agreement_rules.check_instruments_before_agreement(
               ctx.trade_agreements.records, ctx.trade_agreements.paths, ctx.intblocks.records),
           enabled=lambda ctx: ctx.trade_agreements is not None),
    _cross("trade agreement freshness", INTBLOCKS, W,
           lambda ctx: trade_agreement_rules.check_trade_agreement_freshness(
               ctx.trade_agreements.records, ctx.trade_agreements.paths, ctx.last_verified_max_age),
           message=lambda i: f"{i['file_path']}: {i['field']}: {i['suggested_action']}",
           enabled=lambda ctx: ctx.trade_agreements is not None and ctx.last_verified_max_age > 0,
           dated=True),
    _cross("attribute migrations", INTBLOCKS, E,
           lambda ctx: cross_rules.validate_attribute_intblock_migrations(
               ctx.attribute_migrations or [], ctx.intblock_ids),
           message=lambda i: f"attribute migrations: {i['suggested_action']}",
           enabled=lambda ctx: ctx.attribute_migrations is not None),
    _cross("organizational references", INTBLOCKS, W,
           lambda ctx: cross_rules.check_org_refs(
               ctx.intblocks.records, ctx.intblocks.paths, ctx.alias_names,
               ctx.allowlist("org_ref_allowlist"))),
    _cross("country include resolution", INTBLOCKS, E,
           lambda ctx: cross_rules.validate_intblock_refs(
               ctx.countries.directory, ctx.intblocks.records, ctx.intblocks.paths, ctx.countries_cfg),
           enabled=_has_countries),
    _cross("headquarters countries", INTBLOCKS, W,
           lambda ctx: cross_rules.check_hq_country(
               ctx.intblocks.records, ctx.intblocks.paths, ctx.country_codes,
               set(ctx.countries_cfg.get("special_entity_allowlist") or [])),
           enabled=_has_countries),
    _record("founding members", INTBLOCKS, W,
            lambda ctx, r, p: intblock_rules.check_intblock_founding_members(r, ctx.country_codes),
            enabled=_has_countries),
    _cross("headquarters coordinates", INTBLOCKS, W,
           lambda ctx: cross_rules.check_hq_coordinates(
               ctx.intblocks.records, ctx.intblocks.paths, ctx.countries_by_code, ctx.intblocks_cfg),
           enabled=_has_countries),
    _cross("World Bank group rosters", INTBLOCKS, W,
           lambda ctx: wb_classification.check_wb_group_rosters(
               ctx.intblocks.records, ctx.intblocks.paths, ctx.countries_by_code),
           enabled=_has_countries),
    _cross("historical entity members", INTBLOCKS, W,
           lambda ctx: cross_rules.check_historical_entity_members(
               ctx.intblocks.records, ctx.intblocks.paths, ctx.countries_by_code),
           enabled=_has_countries),
    _cross("wikidata id uniqueness", INTBLOCKS, W,
           lambda ctx: cross_rules.check_duplicate_wikidata_ids(
               ctx.intblocks.paths, ctx.intblocks.records, ctx.allowlist("wikidata_duplicate_allowlist"))),
    _cross("acronym uniqueness", INTBLOCKS, W,
           lambda ctx: cross_rules.check_duplicate_acronyms(
               ctx.intblocks.records, ctx.intblocks.paths, ctx.allowlist("acronym_duplicate_allowlist"))),
    _record("provenance count", INTBLOCKS, W,
            lambda ctx, r, p: country_rules.check_provenance_count(
                r, min_count=int(ctx.intblocks_provenance.get("min_count") or 0)),
            enabled=lambda ctx: int(ctx.intblocks_provenance.get("min_count") or 0) > 0),
    _record("provenance freshness", INTBLOCKS, W,
            lambda ctx, r, p: country_rules.check_provenance_freshness(
                r, max_age_months=int(ctx.intblocks_provenance.get("max_age_months") or 0)),
            enabled=lambda ctx: int(ctx.intblocks_provenance.get("max_age_months") or 0) > 0,
            dated=True),
    _record("description quality", INTBLOCKS, REPORT,
            lambda ctx, r, p: intblock_rules.check_intblock_description_quality(r)),
    _record("deprecated include statuses", INTBLOCKS, W,
            lambda ctx, r, p: intblock_rules.check_deprecated_include_statuses(r, ctx.includes_status_catalog)),
    _record("includes contract", INTBLOCKS, REPORT,
            lambda ctx, r, p: intblock_rules.check_intblock_includes_contract(
                r, ctx.intblocks_cfg, ctx.includes_status_catalog)),
    _record("links", INTBLOCKS, REPORT,
            lambda ctx, r, p: intblock_rules.check_intblock_links(r, ctx.check_http, ctx.check_wikidata)),
    _cross("completeness", INTBLOCKS, REPORT,
           lambda ctx: country_rules.validate_completeness(
               ctx.intblocks.records, ctx.intblocks_cfg,
               null_checker=completeness.is_null_intblock_field, attach_field_priority=True)),
    _cross("duplicate links", INTBLOCKS, REPORT,
           lambda ctx: cross_rules.check_duplicate_links(
               ctx.countries.paths + ctx.intblocks.paths, ctx.countries.records + ctx.intblocks.records)),
    _cross("include display names", INTBLOCKS, W,
           lambda ctx: cross_rules.check_include_name_mismatch(
               ctx.intblocks.records, ctx.intblocks.paths, ctx.countries_by_code),
           enabled=_has_countries),
)

RULES: dict[str, tuple[Rule, ...]] = {COUNTRIES: COUNTRY_RULES, INTBLOCKS: INTBLOCK_RULES}


def record_id(dataset: str, record: dict[str, Any]) -> str:
    return str(record.get("code" if dataset == COUNTRIES else "id", "unknown"))


def run_rules(
    rules: tuple[Rule, ...] | list[Rule],
    ctx: RuleContext,
    *,
    validator: bool = False,
    on_rule: Callable[[Rule], None] | None = None,
) -> Iterator[tuple[Rule, Issue]]:
    """Run ``rules`` in order and yield each issue with the rule that raised it.

    Record issues get the record's ``file_path`` and ``record_id``; cross-record issues keep
    the ``file_path`` the rule set, or ``cross-record``. With ``validator=True`` the
    report-only rules are skipped.
    """
    for rule in rules:
        if (validator and rule.severity is None) or not rule.enabled(ctx):
            continue
        if on_rule:
            on_rule(rule)
        if rule.cross:
            for issue in rule.check(ctx):
                issue.setdefault("file_path", "cross-record")
                issue.setdefault("record_id", "cross-record")
                yield rule, issue
            continue
        data = ctx.dataset(rule.dataset)
        for record, rel in zip(data.records, data.paths, strict=True):
            for issue in rule.check(ctx, record, rel):
                issue["file_path"] = rel
                issue["record_id"] = record_id(rule.dataset, record)
                yield rule, issue


def validator_messages(
    dataset: str, ctx: RuleContext
) -> tuple[list[str], list[str], list[str]]:
    """Errors, warnings and dated warnings of the validator rules for ``dataset``, as CLI
    messages. Dated warnings come from ``dated`` rules and are not in ``warnings``."""
    errors: list[str] = []
    warnings: list[str] = []
    dated: list[str] = []
    for rule, issue in run_rules(RULES[dataset], ctx, validator=True):
        target = errors if rule.severity == E else dated if rule.dated else warnings
        target.append(rule.message(issue))
    return errors, warnings, dated
