#!/usr/bin/env python3
"""Apply the 2026-11-23 walk of African trade agreements (tralac, AfCFTA Secretariat, AU).

One-off: run once from the repository root, then review the diff. It writes

* the per-party dates of the AfCFTA Agreement on the ``AfCFTA`` intblock roster
  (``includes[].joined`` is the date the Agreement entered into force for the party;
  signature, ratification and deposit go in ``includes[].note``), from the African Union
  status list of 22 May 2026, with the AfCFTA Secretariat's State Parties table and
  tralac's ratification tracker as cross-checks;
* the five Phase II protocols as ``instruments`` of the ``AfCFTA`` record;
* the TFTA entry into force for the 14 Member/Partner States that had deposited
  ratification by 25 July 2024 (SADC Secretariat), on the ``TFTA`` intblock roster;
* the AGOA extensions of 2026 (Public Laws 119-75 and 119-103) in ``notes``;
* new bilateral records that tralac lists and that a party government or the WTO dates
  (Morocco's trade and tariff conventions, the 1964 South Africa - Zimbabwe agreement and
  the Algeria - Mauritania negotiations), and the signature date of ``MWZA``.

tralac is the catalogue; no status or date comes from it.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DAY = "2026-11-23"

AU_LIST = (
    "https://au.int/sites/default/files/treaties/"
    "36437-sl-AGREEMENT_ESTABLISHING_THE_AFRICAN_CONTINENTAL_FREE_TRADE_AREA_1.pdf"
)
AU_TEXT = "https://au.int/sites/default/files/treaties/36437-treaty-consolidated_text_on_cfta_-_en.pdf"
SECRETARIAT_TABLE = "https://au-afcfta.org/state-parties/"
TRALAC_STATUS = "https://www.tralac.org/resources/infographic/13795-status-of-afcfta-ratification.html"
AU_SOMALIA = (
    "https://au.int/en/pressreleases/20260904/auc-chairperson-received-minister-commerce-and-industry-somalia"
)
SECRETARIAT_SOMALIA = (
    "https://au-afcfta.org/2026/08/from-ratification-to-the-first-shipment-the-afcfta-secretary-general-in-mogadishu/"
)
SADC_TFTA = (
    "https://www.sadc.int/latest-news/comesa-eac-sadc-tripartite-free-trade-area-come-force-25th-july-2024"
)
MCINET = "https://www.mcinet.gov.ma/fr/content/"
MCINET_PDF = "https://www.mcinet.gov.ma/sites/default/files/documents/"
DESTA = "https://www.designoftradeagreements.org/downloads/"

# African Union status list of 22 May 2026: signature, ratification or accession, deposit.
AU_STATUS = {
    "DZ": ("2018-03-21", "2021-06-07", "2021-06-23"),
    "AO": ("2018-03-21", "2020-10-06", "2020-11-04"),
    "BJ": ("2019-07-07", None, None),
    "BW": ("2019-02-10", "2023-02-16", "2023-02-19"),
    "BF": ("2018-03-21", "2019-05-27", "2019-05-29"),
    "BI": ("2018-07-02", "2021-06-17", "2021-08-26"),
    "CM": ("2018-03-21", "2020-01-31", "2020-12-01"),
    "CF": ("2018-03-21", "2020-04-09", "2020-09-22"),
    "CV": ("2018-03-21", "2020-11-13", "2022-02-05"),
    "TD": ("2018-03-21", "2018-06-29", "2018-07-02"),
    "CI": ("2018-03-21", "2018-11-13", "2018-11-23"),
    "KM": ("2018-03-21", "2023-02-11", "2023-02-19"),
    "CG": ("2018-03-21", "2019-02-07", "2019-02-10"),
    "DJ": ("2018-03-21", "2019-02-05", "2019-02-11"),
    "CD": ("2018-03-21", "2022-01-28", "2022-02-23"),
    "EG": ("2018-03-21", "2019-02-27", "2019-04-08"),
    "GQ": ("2018-03-21", "2019-06-28", "2019-07-02"),
    "ET": ("2018-03-21", "2019-03-23", "2019-04-10"),
    "GA": ("2018-03-21", "2019-07-02", "2019-07-07"),
    "GM": ("2018-03-21", "2019-04-11", "2019-04-16"),
    "GH": ("2018-03-21", "2018-05-07", "2018-05-10"),
    "GW": ("2019-02-08", "2022-08-08", "2022-08-31"),
    "GN": ("2018-03-21", "2018-07-31", "2018-10-16"),
    "KE": ("2018-03-21", "2018-05-06", "2018-05-10"),
    "LY": ("2018-03-21", None, None),
    "LS": ("2018-07-02", "2020-10-20", "2020-11-27"),
    "LR": ("2018-03-21", "2024-09-04", "2024-10-08"),
    "MG": ("2018-03-21", "2025-04-18", "2025-05-13"),
    "ML": ("2018-03-21", "2019-01-11", "2019-02-01"),
    "MW": ("2018-03-21", "2020-11-01", "2021-01-15"),
    "MA": ("2018-03-21", "2022-02-24", "2022-04-18"),
    "MZ": ("2018-03-21", "2023-06-20", "2023-07-05"),
    "MR": ("2018-03-21", "2019-01-31", "2019-02-11"),
    "MU": ("2018-03-21", "2019-09-30", "2019-10-07"),
    "NA": ("2018-07-02", "2019-01-25", "2019-02-01"),
    "NG": ("2019-07-07", "2020-12-03", "2020-12-05"),
    "NE": ("2018-03-21", "2018-05-28", "2018-06-19"),
    "RW": ("2018-03-21", "2018-05-25", "2018-05-26"),
    "ZA": ("2018-07-02", "2019-01-31", "2019-02-10"),
    "EH": ("2018-03-21", "2019-04-27", "2019-04-30"),
    "SN": ("2018-03-21", "2019-03-12", "2019-04-02"),
    "SC": ("2018-03-21", "2021-07-08", "2021-09-15"),
    "SL": ("2018-07-02", "2019-04-19", "2019-04-30"),
    "SO": ("2018-03-21", None, None),
    "SS": ("2018-03-21", None, None),
    "ST": ("2018-03-21", "2019-05-28", "2019-06-27"),
    "SD": ("2018-03-21", None, None),
    "SZ": ("2018-03-21", "2018-06-21", "2018-07-02"),
    "TZ": ("2018-03-21", "2022-01-17", "2022-01-17"),
    "TG": ("2018-03-21", "2019-01-09", "2019-04-02"),
    "TN": ("2018-03-21", "2020-09-07", "2020-11-27"),
    "UG": ("2018-03-21", "2018-11-20", "2019-02-09"),
    "ZM": ("2019-02-10", "2021-01-28", "2021-02-05"),
    "ZW": ("2018-03-21", "2019-04-25", "2019-05-24"),
}
AFCFTA_IN_FORCE = "2019-05-30"
SOMALIA_DEPOSIT = "2026-09-04"
# Where the AfCFTA Secretariat's State Parties table gives other dates than the AU list.
SECRETARIAT_CONFLICTS = {
    "DZ": "The AfCFTA Secretariat's State Parties table gives ratification on 15 December 2019 and deposit on 3 June 2021.",
    "SL": "The AfCFTA Secretariat's State Parties table gives ratification on 7 November 2018.",
}

PROTOCOLS = [
    ("investment", "Investment", "2023-02-19", 36, "45078-treaty-EN_AfCFTA_Protocol_on_Investment.pdf",
     "protocol-agreement-establishing-african-continental-free-trade-area-investment", ["investment"]),
    ("competition-policy", "Competition Policy", "2023-02-19", 36,
     "45080-treaty-EN_AfCFTA_Protocol_on_Competition_Policy.pdf",
     "protocol-agreement-establishing-african-continental-free-trade-area-competition-policy", None),
    ("intellectual-property-rights", "Intellectual Property Rights", "2023-02-19", 36,
     "45077-treaty-EN_AfCFTA_Protocol_on_Intellectual_Property_Rights.pdf",
     "protocol-agreement-establishing-african-continental-free-trade-area-intellectual-property", None),
    ("digital-trade", "Digital Trade", "2024-02-18", 37, "45079-treaty-EN_AfCFTA_Protocol_on_Digital_Trade.pdf",
     "protocol-agreement-establishing-african-continental-free-trade-area-digital-trade-0", None),
    ("women-and-youth-in-trade", "Women and Youth in Trade", "2024-02-18", 37,
     "45076-treaty-EN_AfCFTA_Protocol_on_Women_and_Youth_Trade.pdf",
     "protocol-agreement-establishing-african-continental-free-trade-area-women-and-youth-trade", None),
]

# SADC Secretariat, 24 July 2024: the 14 States that had deposited TFTA ratification.
TFTA_DEPOSITED = {"AO", "BW", "BI", "EG", "SZ", "KE", "LS", "MW", "NA", "RW", "ZA", "UG", "ZM", "ZW"}
TFTA_IN_FORCE = "2024-07-25"


def long_date(iso: str) -> str:
    year, month, day = iso.split("-")
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
              "October", "November", "December"]
    return f"{int(day)} {months[int(month) - 1]} {year}"


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def dump(path: Path, record: dict, width: int) -> None:
    path.write_text(yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=width), encoding="utf-8")


def prov(field: str, source: str, url: str | None = None) -> dict:
    entry = {"field": field, "source": source}
    if url:
        entry["url"] = url
    entry["retrieved_at"] = DAY
    return entry


def afcfta_roster() -> None:
    path = ROOT / "data/intblocks/fta/AfCFTA.yaml"
    record = load(path)
    for inc in record["includes"]:
        code = inc["id"]
        signed, ratified, deposited = AU_STATUS[code]
        inc.pop("joined", None)
        inc.pop("note", None)
        if code == "SO":
            inc["joined"] = SOMALIA_DEPOSIT
            inc["note"] = (
                f"Signed on {long_date(signed)}. Instrument of ratification deposited on 4 September 2026, after the "
                "African Union status list of 22 May 2026: tralac lists Somalia among the deposits as on that day, and "
                "the AU Commission Chairperson congratulated Somalia's Minister of Commerce and Industry on the "
                "ratification at AU headquarters that day. The AfCFTA Secretariat had announced the deposit for "
                "2 September 2026."
            )
            continue
        if deposited is None:
            inc["note"] = (
                f"Signed on {long_date(signed)}; no instrument of ratification deposited on the African Union status "
                "list of 22 May 2026."
            )
            continue
        inc["joined"] = AFCFTA_IN_FORCE if deposited < AFCFTA_IN_FORCE else deposited
        note = (
            f"Signed on {long_date(signed)}, ratified on {long_date(ratified)} and instrument deposited on "
            f"{long_date(deposited)} (African Union status list of 22 May 2026)."
        )
        if code in SECRETARIAT_CONFLICTS:
            note += " " + SECRETARIAT_CONFLICTS[code]
        inc["note"] = note
    record["notes"] = (
        "The roster is the 54 signatories on the African Union status list of 22 May 2026. Eritrea has not signed. "
        "`joined` is the date the Agreement entered into force for the State: 30 May 2019, thirty days after the "
        "22nd deposit (Article 23(1)), for the 24 States that deposited by then, and the date of deposit for the "
        "States that deposited later. Article 23(3) gives the date of deposit for an acceding State; the AU list does "
        "not separate ratification from accession. Signature, ratification and deposit dates are in each entry's "
        "`note`. Benin, Libya, South Sudan and Sudan had signed but not deposited an instrument on the AU list, and "
        "have no `joined` date. Somalia deposited its instrument on 4 September 2026, after that list. The AfCFTA "
        "Secretariat's State Parties table lags the AU list: it shows Botswana, Burundi, Comoros, Guinea-Bissau, "
        "Liberia, Madagascar, Mozambique and Seychelles as pending, and gives no deposit date for Cabo Verde, the "
        "Democratic Republic of the Congo, Morocco and Tanzania. The Protocols on Investment, Competition Policy, "
        "Intellectual Property Rights, Digital Trade and Women and Youth in Trade are instruments of the `AfCFTA` "
        "trade agreement record, not separate intblocks. Join on `AfCFTA` for the goods and services agreement."
    )
    record["last_verified"] = DAY
    record["provenance"] = [
        p for p in record["provenance"] if not (p.get("field") == "includes" and p.get("retrieved_at") == DAY)
    ] + [
        prov("includes", "African Union, status list of the AfCFTA Agreement (22 May 2026)", AU_LIST),
        prov("includes", "African Union, Agreement Establishing the AfCFTA, Article 23 (entry into force)", AU_TEXT),
        prov("includes", "African Union Commission, readout of 4 September 2026 (Somalia)", AU_SOMALIA),
        prov("notes", "AfCFTA Secretariat, State and Non-State Parties table", SECRETARIAT_TABLE),
        prov("notes", "tralac, Status of AfCFTA Ratification (7 September 2026), cross-check", TRALAC_STATUS),
    ]
    dump(path, record, 100000)


def afcfta_record() -> None:
    path = ROOT / "data/trade_agreements/AfCFTA.yaml"
    record = load(path)
    items = []
    for slug, topic, adopted, session, pdf, page, coverage in PROTOCOLS:
        item = {
            "id": f"protocol-{slug}",
            "kind": "supplementary_agreement",
            "name": f"Protocol to the Agreement Establishing the African Continental Free Trade Area on {topic}",
            "status": "signed",
            "signed": adopted,
        }
        if coverage:
            item["coverage"] = coverage
        item["notes"] = (
            f"Adopted by the {session}th Ordinary Session of the AU Assembly at Addis Ababa on {long_date(adopted)}; "
            "`signed` holds that date of adoption. Open for signature and ratification by the State Parties; it "
            "enters into force under Article 23(2) and (4) of the Agreement, thirty days after the 22nd instrument "
            "of ratification. The African Union treaty page gives no status list, and the instrument is not "
            f"recorded as in force on {DAY}."
        )
        item["provenance"] = [
            prov("instruments", "African Union, treaty page (date of adoption)", f"https://au.int/en/treaties/{page}"),
            prov("instruments", "African Union, treaty text (final provisions)",
                 f"https://au.int/sites/default/files/treaties/{pdf}"),
        ]
        items.append(item)
    # Instruments follow status, as on the other records that have them.
    record = {k: v for k, v in record.items() if k != "instruments"}
    out = {}
    for key, value in record.items():
        out[key] = value
        if key == "status":
            out["instruments"] = items
    record = out
    record["notes"] = (
        "Adopted at Kigali on 21 March 2018 and in force from 30 May 2019 (African Union status list, AfCFTA "
        "Secretariat); the African Union treaty page gives 22 May 2019. Trading under the agreement began on 1 January "
        "2021. Per-State signature, ratification, deposit and entry-into-force dates are on the `AfCFTA` intblock "
        "roster. The Phase II protocols on investment, competition policy and intellectual property rights (2023) and "
        "on digital trade and women and youth in trade (2024) are not in force."
    )
    record["last_verified"] = DAY
    record["provenance"].append(prov("instruments", "African Union, treaties list (AfCFTA protocols)",
                                     "https://au.int/en/treaties"))
    dump(path, record, 120)


def tfta() -> None:
    path = ROOT / "data/intblocks/trade/TFTA.yaml"
    record = load(path)
    for inc in record["includes"]:
        inc.pop("joined", None)
        inc.pop("note", None)
        if inc["id"] in TFTA_DEPOSITED:
            inc["joined"] = TFTA_IN_FORCE
            inc["note"] = (
                "One of the 14 Member/Partner States that had deposited an instrument of ratification when the "
                "Agreement entered into force on 25 July 2024 (SADC Secretariat)."
            )
        elif inc["id"] == "DJ":
            inc["note"] = (
                "Notified the COMESA Secretariat of its ratification on 20 June 2024; no deposit by the entry into "
                "force on 25 July 2024 (SADC Secretariat)."
            )
        else:
            inc["note"] = "No instrument of ratification deposited by the entry into force on 25 July 2024 (SADC Secretariat)."
    record["notes"] = (
        "The Tripartite Free Trade Area (TFTA) Agreement was launched and opened for signature at Sharm El Sheikh on "
        "10 June 2015. It entered into force on 25 July 2024, after Angola deposited the 14th instrument of "
        "ratification on 25 June 2024 (SADC Secretariat). `joined` is that date for the 14 States that had deposited "
        "by then (Angola, Botswana, Burundi, Egypt, Eswatini, Kenya, Lesotho, Malawi, Namibia, Rwanda, South Africa, "
        "Uganda, Zambia and Zimbabwe); the other 15 Tripartite Member/Partner States have no `joined` date. Later "
        "deposits were not found. The roster lists all 29 Tripartite Member/Partner States of COMESA, the EAC and "
        "SADC."
    )
    record["last_verified"] = DAY
    record["provenance"].append(prov("includes", "SADC Secretariat, TFTA to come into force on 25 July 2024", SADC_TFTA))
    dump(path, record, 100000)

    path = ROOT / "data/trade_agreements/TFTA.yaml"
    record = load(path)
    notes = (
        "Signed at Sharm El Sheikh on 10 June 2015; in force from 25 July 2024 for the 14 States that had deposited "
        "ratification (SADC Secretariat). Per-State dates are on the `TFTA` intblock roster."
    )
    out = {}
    for key, value in record.items():
        if key == "verification":
            out["notes"] = notes
        out[key] = value
    record = out
    record["last_verified"] = DAY
    record["provenance"].append(prov("in_force", "SADC Secretariat, TFTA to come into force on 25 July 2024", SADC_TFTA))
    dump(path, record, 120)


AGOA_NOTES = (
    "AGOA preferences lapsed after 30 September 2025. The Consolidated Appropriations Act, 2026 (Public Law 119-75, "
    "section 5019, enacted 3 February 2026) extended them through 31 December 2026, and entries made during the lapse "
    "can be reliquidated on request; Proclamation 11030 of 19 May 2026 implemented the extension. The "
    "Continuing Appropriations and Extensions Act, 2027 (Public Law 119-103, section 2008, enacted 2 September 2026) "
    "extended duty-free treatment, the regional apparel article program and the third-country fabric program "
    "through 31 December 2028."
)


def agoa() -> None:
    sources = [
        ("Consolidated Appropriations Act, 2026 (Public Law 119-75), section 5019",
         "https://www.congress.gov/119/plaws/publ75/PLAW-119publ75.htm"),
        ("Proclamation 11030 of 19 May 2026, 91 FR 30469",
         "https://www.federalregister.gov/documents/2026/05/22/2026-10398/"
         "to-implement-certain-provisions-in-the-consolidated-appropriations-act-2026-and-for-other-purposes"),
        ("Continuing Appropriations and Extensions Act, 2027 (Public Law 119-103), section 2008",
         "https://www.congress.gov/119/plaws/publ103/PLAW-119publ103.htm"),
    ]
    for rid in ("AGOA", "AGOA-APPAREL"):
        path = ROOT / f"data/trade_agreements/{rid}.yaml"
        record = load(path)
        notes = AGOA_NOTES
        if record.get("notes"):
            notes = record["notes"] + " " + AGOA_NOTES
        # Keep key order: notes before verification.
        out = {}
        for key, value in record.items():
            if key == "verification" and "notes" not in record:
                out["notes"] = notes
            out[key] = notes if key == "notes" else value
        out["last_verified"] = DAY
        out["provenance"] = record["provenance"] + [prov("status", s, u) for s, u in sources]
        dump(path, out, 120)


def mwza() -> None:
    path = ROOT / "data/trade_agreements/MWZA.yaml"
    record = load(path)
    out = {}
    for key, value in record.items():
        if key == "in_force":
            out["signed"] = "1990-06-19"
        out[key] = value
    out["provenance"].insert(0, prov(
        "signed",
        "South African Revenue Service, Trade Agreement between South Africa and Malawi (concluded 19 June 1990, "
        "Notice R.1357, GG 12546)",
        "https://www.sars.gov.za/legal-counsel/international-treaties-agreements/trade-agreements/rsa-malawi/",
    ))
    dump(path, out, 120)


def bilateral(rid: str, body: dict) -> None:
    path = ROOT / f"data/trade_agreements/{rid}.yaml"
    if path.exists():
        sys.exit(f"{path} exists")
    dump(path, {"id": rid, **body}, 120)


def tralac_prov(field: str = "notes") -> dict:
    return prov(field, "tralac, Morocco trade and tariff profile 2020 (bilateral FTAs, catalogue)",
                "https://www.tralac.org/documents/publications/trade-data-analysis/"
                "4329-morocco-trade-and-tariff-profile-2020-infographic/file.html")


def bilaterals() -> None:
    countries = lambda *ids: [{"id": i, "type": "country"} for i in ids]  # noqa: E731
    bilateral("DZMA", {
        "name": "Trade and Tariff Convention between Algeria and Morocco",
        "other_names": [{"lang": "fr", "name": "Convention commerciale et tarifaire entre l'Algérie et le Maroc"}],
        "agreement_type": "fta",
        "status": "in_force",
        "signed": "1989-03-14",
        "in_force": "1989-03-14",
        "parties": countries("DZ", "MA"),
        "links": [{"url": MCINET_PDF + "CCT%20Maroc_Algerie.pdf", "type": "treaty_text"}],
        "notes": (
            "Exempts all goods originating in and coming from the two countries from customs duties and charges of "
            "equivalent effect; one year, renewed by tacit renewal. The Moroccan Ministry of Industry and Trade gives "
            "entry into force on 14 March 1989, the date of the convention, and ratification on 28 May 1993. "
            "Morocco's 2009 WTO review lists the agreement without dates. DESTA also lists a 1973 agreement between "
            "the two countries, which is not recorded."
        ),
        "verification": "official",
        "last_verified": DAY,
        "provenance": [
            prov("in_force", "Moroccan Ministry of Industry and Trade, Conventions commerciales et tarifaires: Algérie",
                 MCINET + "conventions-commerciales-et-tarifaires-algerie"),
            prov("status", "Moroccan Ministry of Industry and Trade, Conventions commerciales et tarifaires",
                 MCINET + "autres-types-daccords-conventions"),
            tralac_prov(),
            prov("desta_id", "Design of Trade Agreements (DESTA) v2.3, list of treaties, number 19", DESTA),
        ],
    })
    bilateral("LYMA", {
        "name": "Trade and Tariff Convention between Libya and Morocco",
        "other_names": [{"lang": "fr", "name": "Convention commerciale et tarifaire entre la Libye et le Maroc"}],
        "agreement_type": "fta",
        "status": "in_force",
        "signed": "1990-06-29",
        "in_force": "1990-06-29",
        "parties": countries("LY", "MA"),
        "links": [{"url": MCINET_PDF + "CCT%20Maroc_Libye.pdf", "type": "treaty_text"}],
        "notes": (
            "Exempts all goods originating in and coming from the two countries from import duties, for an "
            "indefinite period. The Moroccan Ministry of Industry and Trade gives entry into force on 29 June 1990, "
            "the date of the convention, and ratification on 9 November 1992. Morocco's 2009 WTO review lists the "
            "agreement without dates."
        ),
        "verification": "official",
        "last_verified": DAY,
        "provenance": [
            prov("in_force", "Moroccan Ministry of Industry and Trade, Conventions commerciales et tarifaires: Libye",
                 MCINET + "libye"),
            prov("status", "Moroccan Ministry of Industry and Trade, Conventions commerciales et tarifaires",
                 MCINET + "autres-types-daccords-conventions"),
            tralac_prov(),
            prov("desta_id", "Design of Trade Agreements (DESTA) v2.3, list of treaties, number 574", DESTA),
        ],
    })
    bilateral("GNMA", {
        "name": "Trade and Tariff Convention between Guinea and Morocco",
        "other_names": [{"lang": "fr", "name": "Convention commerciale et tarifaire maroco-guinéenne"}],
        "agreement_type": "pta",
        "status": "in_force",
        "signed": "1997-04-12",
        "provisional_application": "1997-04-12",
        "in_force": "2000-09-06",
        "parties": countries("GN", "MA"),
        "links": [{"url": MCINET_PDF + "CCT%20Maroc_REP%20Guinee.pdf", "type": "treaty_text"}],
        "notes": (
            "Signed at Conakry on 12 April 1997. Exempts the goods on lists 1 and 2 annexed to the convention from "
            "customs duties and charges of equivalent effect; three years, renewed by tacit renewal. Article 17 "
            "applies it provisionally from signature and puts it definitively in force on the last notification; "
            "the Moroccan Ministry of Industry and Trade gives entry into force on 6 September 2000. It replaced "
            "the trade and tariff convention of 17 January 1979 and its additional protocol of 14 September 1990, "
            "which are not recorded."
        ),
        "verification": "official",
        "last_verified": DAY,
        "provenance": [
            prov("in_force",
                 "Moroccan Ministry of Industry and Trade, Conventions commerciales et tarifaires: République de Guinée",
                 MCINET + "republique-de-guinee"),
            prov("provisional_application", "Convention text, Article 17 (Moroccan Ministry of Industry and Trade)",
                 MCINET_PDF + "CCT%20Maroc_REP%20Guinee.pdf"),
            tralac_prov(),
            prov("desta_id", "Design of Trade Agreements (DESTA) v2.3, list of treaties, number 742", DESTA),
        ],
    })
    bilateral("MAMR", {
        "name": "Trade and Tariff Agreement between Morocco and Mauritania",
        "other_names": [{"lang": "fr", "name": "Accord commercial et tarifaire entre le Maroc et la Mauritanie"}],
        "agreement_type": "pta",
        "status": "in_force",
        "signed": "1986-08-04",
        "provisional_application": "1986-08-04",
        "parties": countries("MA", "MR"),
        "links": [{"url": MCINET_PDF + "CCT%20Maroc_Mauritanie.pdf", "type": "treaty_text"}],
        "notes": (
            "Signed at Nouakchott on 4 August 1986. Exempts the Moroccan goods on list A and the Mauritanian goods "
            "on list B from import duties; one year, renewed by tacit renewal. Article 10 applies it provisionally "
            "from signature and definitively once both parties have notified their constitutional formalities. The "
            "Moroccan Ministry of Industry and Trade gives ratification on 28 May 1993 and no date of definitive "
            "entry into force. It replaced the trade agreement signed at Rabat on 9 July 1970 and its additional "
            "arrangements of 1972 and 1974. Conflict: Mauritania's 2018 WTO review lists a 1988 agreement with "
            "Morocco whose tariff concessions are not applied."
        ),
        "verification": "official",
        "last_verified": DAY,
        "provenance": [
            prov("status", "Moroccan Ministry of Industry and Trade, Conventions commerciales et tarifaires: Mauritanie",
                 MCINET + "mauritanie"),
            prov("provisional_application", "Agreement text, Article 10 (Moroccan Ministry of Industry and Trade)",
                 MCINET_PDF + "CCT%20Maroc_Mauritanie.pdf"),
            prov("notes", "WTO, Trade Policy Review of Mauritania, WT/TPR/S/371 (2018)",
                 "https://www.wto.org/english/tratop_e/tpr_e/s371_e.pdf"),
            tralac_prov(),
            prov("desta_id", "Design of Trade Agreements (DESTA) v2.3, list of treaties, number 601", DESTA),
        ],
    })
    bilateral("MASN", {
        "name": "General Convention between Morocco and Senegal",
        "other_names": [{"lang": "fr", "name": "Convention générale maroco-sénégalaise"}],
        "agreement_type": "pta",
        "status": "in_force",
        "signed": "1966-09-06",
        "in_force": "1968-02-27",
        "parties": countries("MA", "SN"),
        "instruments": [{
            "id": "protocol-1987",
            "kind": "amending_protocol",
            "name": "Protocole d'accord between Morocco and Senegal of 13 September 1987",
            "status": "in_force",
            "signed": "1987-09-13",
            "in_force": "1987-12-03",
            "coverage": ["goods"],
            "notes": (
                "Exempts the goods on its annexed list from import duties; two years, renewed by tacit renewal. Its "
                "list complements that of the protocol of 12 April 1983."
            ),
            "provenance": [prov("instruments",
                                "Moroccan Ministry of Industry and Trade, Conventions commerciales et tarifaires: Sénégal",
                                MCINET + "senegale")],
        }],
        "links": [{"url": MCINET_PDF + "CCT%20Maroc_Senegal.pdf", "type": "treaty_text"}],
        "notes": (
            "Exempts the goods originating in the two countries on the list annexed to the convention from import "
            "duties; five years, renewed by tacit renewal. The Moroccan Ministry of Industry and Trade dates the "
            "convention 6 September 1966 and gives entry into force on 27 February 1968; DESTA dates the agreement "
            "1963. The goods lists in force are those of the protocols of 12 April 1983 and 13 September 1987."
        ),
        "verification": "official",
        "last_verified": DAY,
        "provenance": [
            prov("in_force", "Moroccan Ministry of Industry and Trade, Conventions commerciales et tarifaires: Sénégal",
                 MCINET + "senegale"),
            prov("signed", "Moroccan Ministry of Industry and Trade, Conventions commerciales et tarifaires: Sénégal",
                 MCINET + "senegale"),
            tralac_prov(),
            prov("desta_id", "Design of Trade Agreements (DESTA) v2.3, list of treaties, number 769", DESTA),
        ],
    })
    bilateral("ZAZW-1964", {
        "name": "Trade Agreement between the Government of the Republic of South Africa and the Government of Southern "
                "Rhodesia",
        "agreement_type": "pta",
        "status": "terminated",
        "signed": "1964-11-30",
        "in_force": "1964-12-01",
        "ended": "2018-11-20",
        "parties": countries("ZA", "ZW"),
        "notes": (
            "Concluded on 30 November 1964 under section 74 of the Customs Act, 1955, and in force from 1 December "
            "1964 (South African Revenue Service; Regulation Gazette 420, Notice R.1967). It gave preferential "
            "access to certain agricultural and manufactured goods, among them textiles and clothing under its own "
            "rules of origin. South Africa gave notice, and the agreement ended on 20 November 2018 in favour of the "
            "SADC Protocol on Trade (WTO Trade Policy Review of Zimbabwe, 2020); the SARS page, last updated in "
            "2021, does not mention the termination. `ZAZW` is the 1948 customs union agreement."
        ),
        "verification": "official",
        "last_verified": DAY,
        "provenance": [
            prov("in_force", "South African Revenue Service, RSA - Southern Rhodesia (Zimbabwe) trade agreement",
                 "https://www.sars.gov.za/legal-counsel/international-treaties-agreements/trade-agreements/"
                 "rsa-southern-rhodesia-zimbabwe/"),
            prov("ended", "WTO, Trade Policy Review of Zimbabwe, WT/TPR/S/398 (2020), Section 2.3.2",
                 "https://www.wto.org/english/tratop_e/tpr_e/s398_e.pdf"),
            prov("notes", "tralac, South Africa - Zimbabwe bilateral trade update (catalogue)",
                 "https://www.tralac.org/documents/publications/trade-data-analysis/"
                 "959-south-africa-zimbabwe-bilateral-trade-update-september-2017/file.html"),
            prov("desta_id", "Design of Trade Agreements (DESTA) v2.3, list of treaties, number 664", DESTA),
        ],
    })
    bilateral("DZMR", {
        "name": "Preferential Trade Agreement between Algeria and Mauritania",
        "agreement_type": "pta",
        "status": "negotiating",
        "parties": countries("DZ", "MR"),
        "notes": (
            "Negotiations on a preferential trade agreement covering 20 priority products were launched at the 10th "
            "session of the Algerian-Mauritanian Business Council in Algiers on 4 August 2026, according to the "
            "Algerian Ministry of Foreign Trade and Export Promotion. Conflict: tralac's 2022 Algeria update says "
            "Algeria already has a bilateral agreement giving its goods preferential access to Mauritania."
        ),
        "verification": "official",
        "last_verified": DAY,
        "provenance": [
            prov("status",
                 "Algerian Radio, citing the Ministry of Foreign Trade and Export Promotion (4 August 2026)",
                 "https://news.radioalgerie.dz/en/node/83271"),
            prov("notes", "tralac, Algeria trade and tariffs update 2022 (catalogue)",
                 "https://www.tralac.org/documents/publications/trade-data-analysis/"
                 "5363-algeria-trade-and-tariffs-update-2022/file.html"),
        ],
    })


def main() -> None:
    afcfta_roster()
    afcfta_record()
    tfta()
    agoa()
    mwza()
    bilaterals()


if __name__ == "__main__":
    main()
