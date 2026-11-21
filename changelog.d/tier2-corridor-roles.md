### Added

- 20 linear transport corridors with route roles (`transport`, `corridor`), checked on 2026-11-21
  against government, intergovernmental, operator and project-finance sources. Each is in the
  reviewed manifest `data/schemas/include_roles_pilot.yaml`:
  - Asia: `CPEC` (CN, PK `terminal`; `project`, `partof: BRI`), `TRILATERALHIGHWAY`
    (India–Myanmar–Thailand), `BTKRAILWAY` (Baku–Tbilisi–Kars), `ITIRAILWAY`
    (Islamabad–Tehran–Istanbul), `TRANSAFGHANRAILWAY` (planned, UZ–AF–PK), `DEVELOPMENTROAD`
    (IQ, TR; Qatar and the UAE are memorandum parties only) and `GMSSECCENTRAL` (GMS Southern
    Economic Corridor, central subcorridor: TH, KH, VN).
  - Europe: `RAILBALTICA` (EE, LV, LT, PL) and `VIABALTICA` (PL, LT, LV, EE). Finland is not
    on either route.
  - Africa: `MAPUTOCORRIDOR`, `LAPSSET` (KE, SS and ET all `terminal`), `TAZARARAILWAY`,
    `ADDISDJIBOUTIRAILWAY`, `WBNLDC` (Walvis Bay–Ndola–Lubumbashi), `TRANSCUNENE`,
    `DOUALANDJAMENA` and `DOUALABANGUI`.
  - Americas: `BIOCEANICCORRIDOR` (BR, PY, AR, CL), `INTEROCEANICHIGHWAY` (BR, PE) and
    `PACIFICCORRIDOR` (Mesoamerican Pacific Corridor, Mexico to Panama).
  The manifest also defers 14 corridors, with reasons, because they branch, have no defined
  ends or have only one terminal country:
  - the China–Mongolia–Russia, New Eurasian Land Bridge and China–Central Asia–West Asia
    corridors;
  - BCIM;
  - Kaladan, whose two ends are both in India;
  - IMEC;
  - the nine TEN-T European Transport Corridors;
  - Nacala, Beira and the wider Dar es Salaam corridor;
  - the GMS North–South and Southern corridors as wholes;
  - CAREC corridors 1 to 6.
  `BRI` lists `CPEC` among its suborganizations.
