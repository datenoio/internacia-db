### Added

- 30 cross-border oil pipeline records (`oilpipeline`), checked on 2026-11-24, each with
  `origin`, `transit` and `destination` roles from an operator, government, intergovernmental or
  project-finance source:
  - Europe: `DRUZHBA` (Druzhba, Wikidata Q315654), `ADRIA` (Adria/JANAF, Q505616), `TAL`
    (Transalpine Pipeline, Q872783), `IKL` (Ingolstadt–Kralupy–Litvínov, Q443487), `RRP`
    (Rotterdam–Rhine Pipeline), `NORPIPEOIL` (Norpipe oil line, Ekofisk–Teesside) and
    `THESSALONIKISKOPJE` (Thessaloniki–Skopje products line).
  - Caspian, Russia and Central Asia: `WREP` (Baku–Supsa, Q2029336), `BAKUNOVOROSSIYSK` (Q2027452),
    `UZENATYRAUSAMARA` (Q4318120), `OMSKPAVLODARSHYMKENT` and `CHINARUSSIAOIL` (the
    Skovorodino–Mohe–Daqing branch of ESPO, Q10871729).
  - Middle East and Asia: `AB4` (Saudi Arabia–Bahrain), `MYANMARCHINAOIL` (crude line beside the
    `MYANMARCHINA` gas line), `MAPL` (Motihari–Amlekhgunj, Q105560381) and `IBFPL`
    (India–Bangladesh Friendship Pipeline, Q111795931).
  - Africa: `CHADCAMEROON` (Q5066537), `NIGERBENIN` (Q124031987), `GREATERNILE` (Q1757784),
    `PETRODAR`, `TAZAMA` (Q7690394), `BEIRAFERUKA` and `TRAPSA` (In Amenas–La Skhira).
  - Americas: `KEYSTONE` (Q1631056), `ENBRIDGEMAINLINE` (Q5375283), `EXPRESSPIPELINE`, `COCHIN`
    (Q97379914), `SOUTHERNLIGHTS`, `TRANSMOUNTAIN` (Q23074089) and `OTASA` (Oleoducto Trasandino,
    Q111687259).
  - Paused or disrupted flows are described in `notes` as of November 2026 (for example the
    northern Druzhba leg and Baku–Supsa). The 11 records without a Wikidata item are listed in
    `data/schemas/wikidata_exclusions.yaml`.

### Changed

- The `wikidata_id` completeness threshold for intblocks is 19% (was 18%): the new pipeline
  records without a Wikidata item take the missing rate to 18.3%.
