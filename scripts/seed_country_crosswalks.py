#!/usr/bin/env python3
"""Seed optional country crosswalk codes (IOC/FIFA/FIPS/GeoNames) from a static map.

Uses curated seed data for official ISO records. Does not overwrite existing values.
"""

from __future__ import annotations

import csv
import io
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
COUNTRIES = ROOT / "data" / "countries"
SEED = ROOT / "data" / "schemas" / "country_crosswalk_seed.csv"

# Minimal seed: alpha-2, geonames_id, ioc_code, fifa_code, fips_code
# FIFA/IOC often match ISO3; exceptions handled explicitly.
DEFAULT_SEED = """code,geonames_id,ioc_code,fifa_code,fips_code
AD,3041565,AND,AND,AN
AE,290557,UAE,UAE,AE
AF,1149361,AFG,AFG,AF
AL,783754,ALB,ALB,AL
AM,174982,ARM,ARM,AM
AO,3351879,ANG,ANG,AO
AR,3865483,ARG,ARG,AR
AT,2782113,AUT,AUT,AU
AU,2077456,AUS,AUS,AS
AZ,587116,AZE,AZE,AJ
BA,3277605,BIH,BIH,BK
BD,1210997,BAN,BAN,BG
BE,2802361,BEL,BEL,BE
BG,732800,BUL,BUL,BU
BH,290340,BRN,BHR,BA
BR,3469034,BRA,BRA,BR
CA,6251999,CAN,CAN,CA
CH,2658434,SUI,SUI,SZ
CL,3895114,CHI,CHI,CI
CN,1814991,CHN,CHN,CH
CO,3686110,COL,COL,CO
CR,3624060,CRC,CRC,CS
CU,3562981,CUB,CUB,CU
CY,146669,CYP,CYP,CY
CZ,3077311,CZE,CZE,EZ
DE,2921044,GER,GER,GM
DK,2623032,DEN,DEN,DA
DZ,2589581,ALG,ALG,AG
EC,3658394,ECU,ECU,EC
EE,453733,EST,EST,EN
EG,357994,EGY,EGY,EG
ES,2510769,ESP,ESP,SP
ET,337996,ETH,ETH,ET
FI,660013,FIN,FIN,FI
FR,3017382,FRA,FRA,FR
GB,2635167,GBR,,UK
GE,614540,GEO,GEO,GG
GH,2300660,GHA,GHA,GH
GR,390903,GRE,GRE,GR
HR,3202326,CRO,CRO,HR
HU,719819,HUN,HUN,HU
ID,1643084,INA,IDN,ID
IE,2963597,IRL,IRL,EI
IL,294640,ISR,ISR,IS
IN,1269750,IND,IND,IN
IQ,99237,IRQ,IRQ,IZ
IR,130758,IRI,IRN,IR
IS,2629691,ISL,ISL,IC
IT,3175395,ITA,ITA,IT
JP,1861060,JPN,JPN,JA
KE,192950,KEN,KEN,KE
KG,1527747,KGZ,KGZ,KG
KH,1831722,CAM,CAM,CB
KP,1873107,PRK,PRK,KN
KR,1835841,KOR,KOR,KS
KW,285570,KUW,KUW,KU
KZ,1522867,KAZ,KAZ,KZ
LA,1655842,LAO,LAO,LA
LB,272103,LBN,LBN,LE
LK,1227603,SRI,SRI,CE
LT,597427,LTU,LTU,LH
LU,2960313,LUX,LUX,LU
LV,458258,LAT,LAT,LG
LY,2215636,LBA,LBY,LY
MA,2542007,MAR,MAR,MO
MD,617790,MDA,MDA,MD
ME,3194884,MNE,MNE,MJ
MG,1062947,MAD,MAD,MA
MK,718075,MKD,MKD,MK
ML,2453866,MLI,MLI,ML
MM,1327865,MYA,MYA,BM
MN,2029969,MGL,MNG,MG
MX,3996063,MEX,MEX,MX
MY,1733045,MAS,MAS,MY
NG,2328926,NGR,NGA,NI
NL,2750405,NED,NED,NL
NO,3144096,NOR,NOR,NO
NP,1282988,NEP,NEP,NP
NZ,2186224,NZL,NZL,NZ
OM,286963,OMA,OMA,MU
PA,3703430,PAN,PAN,PM
PE,3932488,PER,PER,PE
PH,1694008,PHI,PHI,RP
PK,1168579,PAK,PAK,PK
PL,798544,POL,POL,PL
PT,2264397,POR,POR,PO
PY,3437598,PAR,PAR,PA
QA,289688,QAT,QAT,QA
RO,798549,ROU,ROU,RO
RS,6290252,SRB,SRB,RI
RU,2017370,RUS,RUS,RS
SA,102358,KSA,KSA,SA
SE,2661886,SWE,SWE,SW
SG,1880251,SGP,SIN,SN
SI,3190538,SLO,SVN,SI
SK,3057568,SVK,SVK,LO
SN,2245662,SEN,SEN,SG
SO,51537,SOM,SOM,SO
SV,3585968,ESA,SLV,ES
SY,163843,SYR,SYR,SY
TH,1605651,THA,THA,TH
TJ,1220409,TJK,TJK,TI
TM,1218197,TKM,TKM,TX
TN,2464461,TUN,TUN,TS
TR,298795,TUR,TUR,TU
TW,1668284,TPE,TPE,TW
TZ,149590,TAN,TAN,TZ
UA,690791,UKR,UKR,UP
UG,226074,UGA,UGA,UG
US,6252001,USA,USA,US
UY,3439705,URU,URU,UY
UZ,1512440,UZB,UZB,UZ
VE,3625428,VEN,VEN,VE
VN,1562822,VIE,VIE,VM
XK,831053,KOS,KVX,KV
ZA,953987,RSA,RSA,SF
ZM,895949,ZAM,ZAM,ZA
ZW,878675,ZIM,ZIM,ZI
"""


def load_seed() -> dict[str, dict[str, str]]:
    raw = SEED.read_text(encoding="utf-8") if SEED.exists() else DEFAULT_SEED
    rows = {}
    for row in csv.DictReader(io.StringIO(raw)):
        code = (row.get("code") or "").strip().upper()
        if code:
            rows[code] = {k: (row.get(k) or "").strip() for k in ("geonames_id", "ioc_code", "fifa_code", "fips_code")}
    return rows


def apply_to_file(path: Path, seed: dict[str, str]) -> bool:
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        return False
    changed_fields: list[str] = []
    for field in ("geonames_id", "ioc_code", "fifa_code", "fips_code"):
        val = seed.get(field) or ""
        if not val or data.get(field):
            continue
        data[field] = val
        changed_fields.append(field)
        # Surgical insert after wikidata_id if present, else after iso3code
        if re.search(rf"^{field}:", text, re.M):
            continue
        anchor = None
        for cand in ("wikidata_id:", "iso3code:", "numeric_code:"):
            if re.search(rf"^{cand}", text, re.M):
                anchor = cand
                break
        if anchor:
            quoted = f"'{val}'"
            text = re.sub(
                rf"^({re.escape(anchor)}.*)$",
                rf"\1\n{field}: {quoted}",
                text,
                count=1,
                flags=re.M,
            )
        else:
            text = f"{field}: {val}\n" + text
    if not changed_fields:
        return False
    # Prefer surgical text we built; fall back to dump if anchors failed partially
    if all(re.search(rf"^{f}:", text, re.M) for f in changed_fields):
        path.write_text(text, encoding="utf-8")
    else:
        path.write_text(yaml.dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False), encoding="utf-8")
    return True


def main() -> None:
    if not SEED.exists():
        SEED.write_text(DEFAULT_SEED.lstrip(), encoding="utf-8")
        print(f"Wrote seed {SEED.relative_to(ROOT)}")
    seed_map = load_seed()
    updated = 0
    for path in sorted(COUNTRIES.glob("*.yaml")):
        code = path.stem
        if code not in seed_map:
            continue
        if apply_to_file(path, seed_map[code]):
            updated += 1
            print(f"  {code}")
    print(f"Updated crosswalk fields on {updated} country file(s)")


if __name__ == "__main__":
    main()
