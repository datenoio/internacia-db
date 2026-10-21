# Retired intblock IDs without replacements

This document tracks removed intblock records that do **not** have an equivalent current intblock. Unlike a rename or merge, a retirement has no `target`; do not place it in `data/intblocks_aliases.yaml` because alias validation correctly requires every target to exist. Update joins and caches to handle the absence of the retired ID after regenerating dataset exports.

The change below corrects an entity-type error rather than asserting that the named media service ceased operations. Historical YAML remains recoverable from Git, but the entity does not belong in a reference dataset of international organizations, treaties, and named country groups.

| Retired ID | Retired in | Reason | Downstream action |
|---|---|---|---|
| `TELESUR` | Unreleased (reviewed 2026-09-30) | La Nueva Televisión del Sur (T.V. SUR) C.A. is a Venezuelan commercial company, not an international organization with member states; the seven exported country links did not represent membership. | Remove `TELESUR` from intblock and membership queries, do not resolve it to a different organization, and model verifiable dated shareholder relationships in a separate corporate dataset if needed. |

The legal-form basis is the [2014 Venezuelan court decision](https://caracas.tsj.gob.ve/DECISIONES/2014/JUNIO/2258-12-2564-14-164-14.HTML), the operator's [terms of use](https://www.telesurtv.net/terminos-de-uso/), and a [2020 court decision](https://historico.tsj.gob.ve/decisiones/scon/enero/309498-0003-29120-2020-20-0038.HTML) discussing its shareholder book without supplying a reliable current list. See the [scope-taxonomy OpenSpec design](../openspec/changes/complete-intblock-scope-taxonomy/design.md) and the `[Unreleased]` changelog for migration context.
