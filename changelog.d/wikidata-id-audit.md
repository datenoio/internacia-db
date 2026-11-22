### Fixed

- Wikidata id audit (22 November 2026): every intblock `wikidata_id` was fetched from
  Wikidata and checked against the record's name and type. 54 records pointed to the wrong
  item, a missing item or a redirect. Each corrected record also gets the matching
  `type: wikidata` link and a `wikidata_id` provenance entry for the new item.
  Old id, new id, and what the old id was:
  - `ARTEMISACCORDS` (Artemis Accords): Q96341450 to Q94568413; Q96341450 is a 2020 article
    on diesel engine emissions.
  - `BANGKOK` (Treaty of Bangkok): Q7707000 to Q1395235; Q7707000 is a Ukrainian tennis
    player.
  - `BARCELONA` (Barcelona Convention): Q808430 to Q2118997; Q808430 is a crater on Mars.
  - `CTBT` (Comprehensive Nuclear-Test-Ban Treaty): Q192088 to Q521306; Q192088 is Eton
    College.
  - `EIB` (European Investment Bank): Q152096 to Q192247; Q152096 is Sainsbury's.
  - `ESM` (European Stability Mechanism): Q2040462 to Q1130098; Q2040462 is the Meath West
    Dáil constituency.
  - `FOCONLINE` (Freedom Online Coalition): Q5504594 to Q17024071; Q5504594 is fringe
    benefits tax.
  - `GGGI` (Global Green Growth Institute): Q5533568 to Q12586353; Q5533568 is a ward in
    Hastings.
  - `LIC` (Low income): Q28035133 to Q25450947 (World Bank low income countries);
    Q28035133 is a Romanian politician.
  - `MSF` (Médecins Sans Frontières): Q37685 to Q49330; Q37685 is Jurong Falls.
  - `NAIROBI` (Nairobi Convention): Q6960080 to Q2996268; Q6960080 is a Wikimedia category.
  - `OFID` (OPEC Fund for International Development): Q7074800 to Q392787; Q7074800 is a
    Canadian publisher.
  - `PEPFAR`: Q1191982 to Q3402412; Q1191982 is mariculture.
  - `RAROTONGA` (Treaty of Rarotonga): Q7835003 to Q1760687; Q7835003 is transport in
    Jersey.
  - `TPNW` (Treaty on the Prohibition of Nuclear Weapons): Q27961877 to Q28130514;
    Q27961877 is a football club.
  - `UNAIDS`: Q781014 to Q588982; Q781014 is Aubusson tapestry.
  - `UNCLOS`: Q19989 to Q216996; Q19989 is a Linkin Park single.
  - `UNHCR`: Q15768 to Q132551; Q15768 is sodium bromide.
  - `ASEANPLUS3` (ASEAN Plus Three): Q483654 to Q1323760; Q483654 is Sunni Islam.
  - `BUDCONV` (Budapest Convention on Cybercrime): Q223800 to Q1093069; Q223800 is the
    Houston disambiguation page.
  - `CILSS`: Q1419931 to Q1114955; Q1419931 is Niemann-Pick disease.
  - `CISG`: Q202027 to Q1196344; Q202027 is the cornet.
  - `COVAX`: Q101437219 to Q99360983; Q101437219 is a street in Eberswalde.
  - `EASTASIASUMMIT` (East Asia Summit): Q618666 to Q542549; Q618666 is a Swiss glacier.
  - `G24` (Group of 24): Q18048978 to Q1589222; Q18048978 is the human gene LACTB.
  - `GATT`: Q192713 to Q194284; Q192713 is a commune in Lozère.
  - `GHSA` (Global Health Security Agenda): Q22022249 to Q104846388; Q22022249 is a 1928
    college football season.
  - `IPBES`: Q3156270 to Q1666088; Q3156270 is a place in Madagascar.
  - `ITC` (International Trade Centre): Q315306 to Q1184878; Q315306 is the German
    Schutzpolizei.
  - `NDPHS` (Northern Dimension Partnership in Public Health and Social Well-being):
    Q17021727 to Q7058307; Q17021727 is a fictional TV character.
  - `REFUGEECONVENTION` (1951 Refugee Convention): Q193430 to Q60433; Q193430 is
    heterocyclic compound.
  - `REFUGEEPROTOCOL` (1967 Refugee Protocol): Q392278 to Q60468; Q392278 is a lake in
    France.
  - `UNCTAD`: Q192710 to Q182000; Q192710 is the Malayan tapir.
  - `UNICEF`: Q142489 to Q740308; Q142489 is the gigabit interface converter.
  - `UNIDROIT`: Q376658 to Q1192641; Q376658 is a Chicago skyscraper.
  - `UNODC`: Q188307 to Q636107; Q188307 is The Salvation Army.
  - `VISTA`: Q924241 to Q1136157; Q924241 is Vista, California.
  - `ICPE` (International Center for Promotion of Enterprises): Q85787929 to Q6049045;
    Q85787929 is an Indian institute for small enterprises.
  - `BBNJ` (High Seas Treaty): Q120432689 to Q48780688; Q120432689 redirects to an
    American economist.
  - `STATELESS1954` (1954 Statelessness Convention): Q1783482 to Q5166243; Q1783482 is a
    mathematical theorem.
  - `STATELESS1961` (1961 Statelessness Convention): Q1783494 to Q5166303; Q1783494 is a
    disambiguation page.
  - `V20` (Vulnerable Twenty Group): Q30943971 to Q141737207; Q30943971 is a Chinese
    person.
  - `WESTERNBLOC` (Western Bloc): Q153045 to Q1507074; Q153045 is an asteroid.
  - `GPAI` (Global Partnership on Artificial Intelligence): Q97185282 to Q105730365;
    Q97185282 is a 1988 animated film.
  - `IAPH` (International Association of Ports and Harbors): Q6048000 to Q17081446;
    Q6048000 is a legal concept.
  - `DEPA` (Digital Economy Partnership Agreement): Q104830867 to Q104880620; Q104830867
    does not exist.
  - `PELINDABA` (Treaty of Pelindaba): Q4691025 to Q1468283; Q4691025 does not exist.
  - `GFCE` (Global Forum on Cyber Expertise): Q30337375 to Q142168082; Q30337375 does not
    exist.
  - `AUUK` (Australia–United Kingdom Free Trade Agreement): Q107271797 to Q97356844;
    Q107271797 does not exist.
  - `CCAMLR`: Q97382426 to Q16184543; Q97382426 redirects to Q16184543.
- No Wikidata item exists for 4 records, so their wrong ids are removed and the records are
  listed in `data/schemas/wikidata_exclusions.yaml`: `TIMBI` (Q22702079, a river in the
  Central African Republic), `ECTEL` (Q5329555, a railway workshop in New Zealand), `ALLPI`
  (Q106518178, a Polish rapper) and `ABIDJAN` (Q4666000, which does not exist).
- 105 names copied from the wrong items are removed from `other_names` and `acronyms` in 23
  records, for example "The Salvation Army" from `UNODC`, "Sunni Islam" from `ASEANPLUS3`
  and "Houston" from `BUDCONV`.
- Descriptions copied from the wrong items are rewritten for `UNAIDS`, `UNHCR`, `G24`,
  `ITC`, `UNCTAD`, `UNICEF` and `UNODC` (for example, `UNHCR` was described as a chemical
  compound).
- Wikipedia links: `BBNJ` now links to High Seas Treaty and `CILSS` to the existing article
  title. Links to articles that do not exist are removed from `V20`, `GFCE`, `ECTEL` and
  `ALLPI`.
