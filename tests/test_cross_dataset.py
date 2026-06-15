"""Unit tests for cross-dataset include resolution."""

import validate_countries as vc


def _setup(tmp_path, intblock_yaml: str):
    countries_dir = tmp_path / "data" / "countries"
    intblocks_dir = tmp_path / "data" / "intblocks" / "intorg"
    countries_dir.mkdir(parents=True)
    intblocks_dir.mkdir(parents=True)
    (countries_dir / "US.yaml").write_text("code: US\nname: United States\n", encoding="utf-8")
    (intblocks_dir / "ORG.yaml").write_text(intblock_yaml, encoding="utf-8")
    return countries_dir, intblocks_dir.parent


def test_resolved_country_include_passes(tmp_path):
    countries_dir, intblocks_dir = _setup(
        tmp_path,
        "id: ORG\nincludes:\n- id: US\n  name: United States\n  type: country\n  status: member\n",
    )
    errors, warnings = vc.validate_intblock_refs(countries_dir, intblocks_dir, {})
    assert errors == []
    assert warnings == []


def test_unresolved_country_include_warns_by_default(tmp_path):
    countries_dir, intblocks_dir = _setup(
        tmp_path,
        "id: ORG\nincludes:\n- id: ZZ\n  name: Nowhere\n  type: country\n  status: member\n",
    )
    errors, warnings = vc.validate_intblock_refs(countries_dir, intblocks_dir, {})
    assert errors == []
    assert any("'ZZ'" in w for w in warnings)


def test_unresolved_country_include_error_mode(tmp_path):
    countries_dir, intblocks_dir = _setup(
        tmp_path,
        "id: ORG\nincludes:\n- id: ZZ\n  name: Nowhere\n  type: country\n  status: member\n",
    )
    config = {"unresolved_country_includes": {"mode": "error"}}
    errors, warnings = vc.validate_intblock_refs(countries_dir, intblocks_dir, config)
    assert any("'ZZ'" in e for e in errors)


def test_allowlisted_include_passes(tmp_path):
    countries_dir, intblocks_dir = _setup(
        tmp_path,
        "id: ORG\nincludes:\n- id: ZZ\n  name: Special\n  type: country\n  status: member\n",
    )
    config = {"special_entity_allowlist": ["ZZ"]}
    errors, warnings = vc.validate_intblock_refs(countries_dir, intblocks_dir, config)
    assert errors == []
    assert warnings == []


def test_cis2_entity_codes_resolve_when_profiles_exist(tmp_path):
    countries_dir, intblocks_dir = _setup(
        tmp_path,
        "id: ORG\nincludes:\n- id: XA\n  name: Abkhazia\n  type: country\n  status: member\n",
    )
    (countries_dir / "XA.yaml").write_text(
        "code: XA\nname: Abkhazia\nentity_type: disputed_territory\ncode_status: user_assigned\n",
        encoding="utf-8",
    )
    errors, warnings = vc.validate_intblock_refs(countries_dir, intblocks_dir, {})
    assert errors == []
    assert warnings == []


def test_deferred_ids_no_longer_special_cased(tmp_path):
    countries_dir, intblocks_dir = _setup(
        tmp_path,
        "id: ORG\nincludes:\n- id: XA\n  name: Abkhazia\n  type: country\n  status: member\n",
    )
    errors, warnings = vc.validate_intblock_refs(countries_dir, intblocks_dir, {})
    assert errors == []
    assert any("unresolved" in w for w in warnings)
    assert not any("deferred policy" in w for w in warnings)


def test_organization_includes_ignored(tmp_path):
    countries_dir, intblocks_dir = _setup(
        tmp_path,
        "id: ORG\nincludes:\n- id: ZZ\n  name: Some Org\n  type: organization\n  status: member\n",
    )
    errors, warnings = vc.validate_intblock_refs(countries_dir, intblocks_dir, {})
    assert errors == []
    assert warnings == []
