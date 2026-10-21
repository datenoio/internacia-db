# Индивидуальные решения по 18 непромаркированным записям

> **Обновление:** шесть индивидуально утверждённых категорий применены с provenance; составы стран не менялись. Текущий статус и результаты проверки — в [отчёте о применении](reviewed-six-nonformal-scope-applied-2026-09-30.md). Ниже сохранён исходный пообъектный анализ остальных решений.

**Исходная рекомендация для шести записей:** `reference_enumeration` для `ARABW`, `BALTICSTATES`, `HISPAM`, `MIDAMERICA`, `SLAVISPHERE` и `policy_forum` для `CMA`. Ещё двум — `PALOP` и `SOUTHERNCONE` — подходит `reference_enumeration`, **но только после выбора точного состава**. Остальные десять не следует добавлять в автоматический backfill без отдельного решения об идентичности записи или её исключении. На момент первоначального анализа все 18 были предложениями; актуальное состояние шести отмечено выше.

В исходных 18 записях **202 связи `includes[].status: member`**, хотя даже для географических и культурных наборов кодовый [справочник статусов](../data/schemas/includes_status.yaml) определяет `member` как полноправного участника. Присвоение `scope_category` само по себе **не исправляет ложное членство**. Ни один из шести допустимых enum не называется `none`: ниже «нет категории» означает оставить поле незаполненным до пересмотра или вывести запись, а не записать строку `none` в YAML.

## Категория определена; отдельно проверить смысл связей

У этих шести объектов установлены собственное имя и воспроизводимая граница. Пять являются справочными наборами, а не организациями; шестой — действующим валютным режимом. Предложение о категории не утверждает, что все их `member`-связи можно без изменений использовать в запросе о формальном членстве.

Источники для культурно-географических групп чаще задают **определение и элементы набора**, а не юридический реестр участников. Поэтому для каждой записи ниже указана конвенция состава, которую надо сохранить в описании и provenance. Если потребители читают `member` буквально, сначала нужен отдельный семантический механизм для элементов справочного набора.

**`ARABW` → `reference_enumeration` (22 кода; высокая уверенность).** Это «арабский мир» в явно выбранной 22-страновой конвенции по составу Лиги арабских государств, которую также использует Library of Congress. Список совпадает с опубликованным составом ЛАГ, но государства **не состоят в организации под названием Arab World**; сама ЛАГ — другая сущность. Закрепить конвенцию в provenance, не переносить штаб-квартиру ЛАГ на географическое понятие и не трактовать совпадающий список как вторую IGO. [1] [2]

**`BALTICSTATES` → `reference_enumeration` (EE, LV, LT; высокая).** Устойчивый трёхстрановой геополитический набор; отдельные Baltic Council of Ministers и Baltic Assembly не превращают эту запись в форум или орган. Состав оставить, ссылку на первичный источник добавить. [3] [4]

**`HISPAM` → `reference_enumeration` (18 суверенных стран Америки; средняя).** RAE/ASALE определяет *Hispanoamérica* как страны Америки испанского языка; таблица Института Сервантеса позволяет проверить 18 стран. Пуэрто-Рико — территория, а Испания и Экваториальная Гвинея находятся вне Америки. Описать узкую границу явно: это геокультурный набор, **не список членов организации** и не утверждение, что испанский всюду одинаково закреплён de jure. [5] [6]

**`MIDAMERICA` → `reference_enumeration` (36 country/area-кодов; средняя).** Употребление *Middle America* охватывает Мексику, Центральную Америку и Карибский бассейн. Текущие 36 кодов воспроизводятся как восемь единиц UN M49 Central America плюс 28 Caribbean; ООН **не называет это объединение собственным реестром Middle America**. В записи нужно исправить описание состава и трактовать 36 как число охваченных территориальных кодов, а не полноправных членов. [7] [8]

**`SLAVISPHERE` → `reference_enumeration` (13 стран; средняя).** Один академический источник прямо перечисляет те же 13 *Slavic countries*, однако сам ID назван *Slavic Europe*, а текущий Wikipedia-provenance допускает ещё Приднестровье. Описать принятый критерий «13 суверенных стран» и сменить источник; наличие славянских языков/общин за их пределами не является основанием расширять `includes`. Это культурный reference set, не IGO. [9]

**`CMA` → `policy_forum` (четыре государства; средняя).** Из шести имеющихся категорий это ближайшая для устойчивого режима денежной координации без собственной правосубъектности: официальное определение связывает CMA с соглашением 1992 года между Лесото, Намибией, Эсватини и ЮАР. Сам договор **MMA** мог бы быть отдельным `treaty_body`, а **CPOC** — отдельным комитетом; ни один не является синонимом CMA. Состав четырёх оставлять, но проверить `status: de-facto`, неподтверждённую штаб-квартиру и дату `1986-07`: МВФ указывает вступление исходного трёхстороннего соглашения в силу **1 апреля 1986 года**, а Намибия присоединилась в 1992 году. [10] [11]

## Подходящая категория есть, но нынешняя граница неверна

В этих случаях сущность относится к справочному перечислению, однако действующий список нельзя подтвердить без дополнительного выбора. Назначение категории раньше исправления списка оставило бы в экспортируемых данных видимость проверенного состава.

Такой выбор лучше записать как **версию или определение набора**, а не как исключения, придуманные по одному для каждой страны. После выбора следует согласованно поправить `includes`, счётчик, описание и field-level provenance; старый снимок не следует незаметно выдавать за текущий.

**`PALOP` → условно `reference_enumeration` (6 или 5; средняя).** Нынешняя шестёрка, включая Экваториальную Гвинею, соответствует широкому употреблению Африканского банка развития. Историческая пятёрка PALOP и официальная кооперация ЕС PALOP-TL **не** включают Экваториальную Гвинею в тот же состав. Если сохранять шесть — назвать это широкой выборкой AfDB; если моделировать прежний PALOP-5 — убрать GQ из этой сущности. `partof: CPLP` не следует оставлять как организационную иерархию языкового набора без отдельного основания. [12] [13]

**`SOUTHERNCONE` → условно `reference_enumeration` (сейчас пять; средняя).** Именованный регион имеет хорошо подтверждённое ядро **AR, CL, UY**; трактовки с PY различаются. В собственном описании записи «южная Бразилия» означает штаты, а не страну `BR` целиком. Выбрать, например, документированную тройку, исправить roster и лишь затем утверждать категорию. Не выдавать границу региона за юридическое членство. [14] [15]

## Текущей записи лучше не присваивать категорию

В десяти случаях заполнение поля означало бы признать либо спорный культурный образ государственным объединением, либо страновой языковой фильтр самостоятельной сущностью. Для них предлагается **review на сохранение/вывод**, а не немедленное удаление. Если владельцы данных выберут другую чётко определённую сущность, ей может потребоваться отдельный ID и новая источниковая проверка.

Три языковых списка особенно показательны. Страновые записи уже имеют поле `languages`, но сейчас в нём **нет явно проставленных `official`-флагов ни у одного из 413 языковых элементов**; выборка по этому полю пока не заменит юридическую проверку официального языка. Это задача отдельного обогащения страновых данных в границах scope проекта, **не** причина сохранять запрещённые [политикой](../docs/intblock-inclusion-policy.md) attribute partitions как intblocks.

**`DUTCHSPHERE` — пока без категории; retirement review (7 кодов).** Официальный Taalunie и нидерландское правительство подтверждают нидерландский как официальный для заявленного узкого набора; `BQ` — объединённый код трёх особых муниципалитетов, не ещё одна суверенная страна. Но запись фактически означает фильтр стран/территорий по языковому атрибуту, а **Taalunie как учреждение** имеет другой состав. Если не будет доказана самостоятельная, не сводимая к этому атрибуту именованная join-цель, не назначать `reference_enumeration`; улучшать `countries.languages`/правовой языковой статус отдельно. [16]

**`GERMANOPHONE` — пока без категории; retirement review (6).** DAAD даёт перечень DE, AT, CH, LI, LU и BE по официальному статусу немецкого, но это не состав самостоятельной организации *German-speaking Europe*. Бельгия и Швейцария многоязычны, а запись смешивает «официальный» и «основной/большинственный» язык. Превратить её в точный country-language predicate либо доказать отличную именованную географическую сущность; простое присвоение `reference_enumeration` противоречит исключению attribute partitions. [17] [18]

**`ROMSE` — пока без категории; retirement review (13).** *Romance-speaking Europe* — языковая география, а не опубликованный единый список 13 государств. Запись смешивает официальный статус, большинство и преобладающий язык; кембриджское описание семейства языков не устанавливает такой roster. Без иного стабильного определения это страновой фильтр и ложное институциональное `member`, а не готовый intblock. [19]

**`MENA` — пока без новой категории; review на дублирование (21).** Само понятие регионально-аналитическое и допускало бы `reference_enumeration`, **но в репозитории уже есть `MEA`**: формальная World Bank enumeration из 23 экономик, включая все 21 из `MENA` плюс AF и PK. World Bank изменил классификацию с 1 июля 2025 года. Предпочтительно вывести дублирующий `MENA` с документированной миграцией потребителей к `MEA` для *текущих* данных; **не делать автоматический alias** 21→23 как будто значения эквивалентны. Если необходим исторический срез до 2025 года, оставить отдельный датированный `reference_enumeration` с версией и без претензии на актуальность. [20] [21]

**`ANGLOSPHERE` — без категории; retirement review (6).** Академические источники называют идею оспариваемой и не имеющей постоянного состава; часто упоминаемая пятёрка GB/US/CA/AU/NZ не создаёт членства, а `IE` не входит в обычное ядро. Не подменять понятие реальным и отдельным форматом Five Eyes. [22]

**`HISPANIDAD` — без категории; retirement review (21).** Определение RAE относится к языково-культурной общности **народов**, а не к закрытому списку государств. Текущий состав совпадает с языково-демографической таблицей Института Сервантеса (18 из `HISPAM` плюс ES, GQ, PR), но это **не** опубликованный состав «членов Hispanidad». Не превращать его в дубликат `HISPAM`. [23] [6]

**`MAR` — без категории; retirement review (8).** Здесь смешаны аналитическая территория OECD 2006 года (**девять мексиканских штатов** плюс семь стран Центральной Америки), широкая культурная Мезоамерика и отдельный ныне действующий Proyecto Mesoamérica с **десятью странами**. Код `MX` не описывает девять штатов; добавлять CO и DO к `MAR` для имитации другого проекта нельзя. При потребности в действующем механизме исследовать его как **отдельный** `policy_forum`. [24] [25]

**`RUSSOPHONE` — без категории; retirement review (4).** RU/BY/KZ/KG близки к узкому списку стран с официальным статусом/употреблением русского, но культурное понятие *Russophone* относится также к людям и диаспорам; четыре юридических языковых случая — country-attribute partition, а не «страны-члены русскоязычного мира». [26]

**`SINOSPHERE` — без категории; retirement review (5).** Текущие CN/TW/SG/HK/MO названы «китайскоязычным административным ядром», тогда как академические исторические определения Sinosphere включают Китай, Корею, Японию и Вьетнам; список смешивает разные критерии и не представляет опубликованный состав. Сохранять можно лишь отдельно очерченный исторический исследовательский набор с иным правилом территориального отображения, не копируя эти пять `member`. [27]

**`CHIP4` — без категории сейчас; retirement review, не объявление роспуска (4).** Подтверждены консультации US/JP/KR/TW в 2022–2023 годах, включая официально документированную встречу в декабре 2023-го. Не найдено проверенного подтверждения продолжающегося процесса после 2023 года; прежние `joined: 2022-09` не являются доказанными датами формального вступления, особенно для KR. Если появится официальный материал 2024–2026 годов о продолжении именно этой группы, её можно пересмотреть как `policy_forum` и перекодировать роли в исторических встречах как `participant`; отсутствие материала **не доказывает**, что группа распущена. [28] [29]

## Что это означает для подготовленного backfill

[Manifest 30 кандидатов](../data/schemas/scope_category_nonformal_30.yaml) — **предварительный**, а не список готовых правок. В нём 16 записей из этой проверки пока предлагаются как `reference_enumeration`, а `CHIP4` как `policy_forum`; после пообъектного анализа это нельзя одобрить массовым переводом `pending_review` в `source_reviewed`. Шесть конкретных категорий остаются предложениями для **отдельно проверенной правки**; два случая требуют выбора состава; десять должны выйти из данного cohort до решения о сохранении. Сам скрипт [backfill_nonformal_scope_category.py](../scripts/backfill_nonformal_scope_category.py) ничего не изменит, пока остаются 18 review-блокеров.

Отдельная модель нейтральной связи для элементов перечисления (например, `included_area`/`enumerated`) потребует OpenSpec-предложения: кодовый `member` означает полноправное участие. Пока такой модели нет, потребители не должны смешивать `scope_category = 'reference_enumeration'` с запросами на формальное членство. В рамках этого исследования **ни source YAML, ни manifest, ни экспорты не изменялись**.

## References

[1]: https://guides.loc.gov/arab-world-newspapers/country "Library of Congress: Arab World — Countries and Publications"
[2]: https://www.eeas.europa.eu/eeas/league-arab-states-las-and-eu_en "European External Action Service: League of Arab States and the EU"
[3]: https://vm.ee/en/baltic-cooperation "Ministry of Foreign Affairs of Estonia: Baltic Cooperation"
[4]: https://economy-finance.ec.europa.eu/eueconomyexplained/graphs-economic-topics/integration-baltic-economies_en "European Commission: Integration of the Baltic Economies"
[5]: https://www.rae.es/dpd/Hispanoam%C3%A9rica "RAE/ASALE: Hispanoamérica, Diccionario panhispánico de dudas"
[6]: https://cvc.cervantes.es/lengua/anuario/anuario_25/moreno-alvarez/cuadros.htm "Instituto Cervantes: Demografía del español en el mundo 2025 — tables"
[7]: https://www.britannica.com/place/Americas "Encyclopaedia Britannica: Americas and Middle America"
[8]: https://unstats.un.org/unsd/methodology/m49/ "United Nations Statistics Division: M49 geographic regions"
[9]: https://www.degruyterbrill.com/document/doi/10.1515/cjss-2021-2003/html "Wei Liu: International Slavic Studies, Comparative Journal of Slavic Studies"
[10]: https://www.bon.com.na/CMSTemplates/Bon/Files/bon.com.na/54/54ae6b7e-d1e6-4277-8916-55d56388b981.pdf "Namibia Government Gazette: Definition of Common Monetary Area"
[11]: https://www.elibrary.imf.org/view/journals/001/2007/158/article-A001-en.xml "IMF Working Paper WP/07/158: Common Monetary Area history"
[12]: https://www.un.org/esa/earthsummit/portu-cp.htm "United Nations: Portugal country profile and traditional PALOP five"
[13]: https://www.afdb.org/en/news-and-events/investing-portuguese-speaking-africa-moment-now-32209 "African Development Bank: Six Portuguese-speaking African countries"
[14]: https://opened.tesu.edu/umnworldgeography/chapter/6-4-the-southern-cone/ "University of Minnesota World Regional Geography: Southern Cone"
[15]: https://www.cepal.org/en/publications/36386-fifth-freedom-and-southern-cone-new-perspective "ECLAC: Context-dependent Southern Cone definition"
[16]: https://taalunie.org/english-information "Dutch Language Union: Dutch-language territories and institutional participation"
[17]: https://www.study-in-germany.com/en/germany/discover-germany/worldwide-use-of-german-language/ "DAAD: German as an official language in six countries"
[18]: https://www.belgium.be/en/about_belgium/government/federale_staat "Belgian Government: Communities and languages in federal Belgium"
[19]: https://www.cambridge.org/core/books/cambridge-history-of-the-romance-languages/geography-and-distribution-of-the-romance-languages-in-europe/EEB3410C9C6F6342D576F4AD07316C02 "Cambridge University Press: Geography of Romance languages in Europe"
[20]: https://datahelpdesk.worldbank.org/knowledgebase/articles/906519-world-bank-country-and-lending-groups "World Bank: Current country and lending groups"
[21]: https://blogs.worldbank.org/en/opendata/what-happens-when-regional-boundaries-change---and-why-it-matter "World Bank Data Blog: Regional boundary change and pre-MENAAP"
[22]: https://journals.sagepub.com/doi/10.1177/13691481231169643 "SAGE: Contested Anglosphere and varying membership"
[23]: https://dle.rae.es/hispanidad "Real Academia Española: Hispanidad dictionary definition"
[24]: https://www.oecd.org/content/dam/oecd/en/publications/reports/2006/03/oecd-territorial-reviews-the-mesoamerican-region-2006_g1gh68c7/9789264021921-en.pdf "OECD Territorial Reviews: The Mesoamerican Region 2006"
[25]: https://www.proyectomesoamerica.org/index.php/noticias/20-noticiaspm/articulos-noticias/1166-belize-takes-over-pro-tempore-presidency-of-mesoamerica-project "Proyecto Mesoamérica: Ten current countries and presidency"
[26]: https://russian.indiana.edu/about/russian-language/index.html "Indiana University: Russian language and four official-language contexts"
[27]: https://manifold.uhpress.hawaii.edu/read/confucianisms-for-a-changing-world-cultural-order/section/0b4ea328-561c-4cdd-8be8-971e4e4c2a35 "University of Hawai‘i Press: Historic East Asian Sinosphere"
[28]: https://www.congress.gov/crs_external_products/R/PDF/R47558/R47558.3.pdf "Congressional Research Service: Proposed Chip 4 working group"
[29]: https://ws.mofa.gov.tw/Download.ashx?u=LzAwMS9VcGxvYWQvNDAyL3JlbGZpbGUvMTE5LzExNzE2MC82NWZhNDE2Yi1kMjQyLTRmODQtYTM3Zi0yMTg4ZGRhMTkzMjEucGRm&n=MTEy5bm05Ye65ZyL6KiI55Wr5Z%2B36KGM5oOF5b2i5aCx5ZGK6KGoeGxzICjnmbzmlofniYgpLeS%2FruatozIucGRm&icon=.pdf "Taiwan Ministry of Foreign Affairs: 2023 official travel report, December working-group meeting"
