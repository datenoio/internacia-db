# Проверка 18 записей официального статуса

По состоянию на 30 сентября 2026 года проверены все 18 записей второй когорты. Для **14** найдена обоснованная категория из существующих четырёх значений; они получили `scope_category` и отдельную запись `provenance`. Четыре записи оставлены без категории, потому что официальные источники опровергли исходное предположение либо выявили смешанный roster.

После применения валидатор и quality analyzer одинаково показывают **0 ошибок и 19 предупреждений** `MISSING_SCOPE_CATEGORY`: исходные 33 уменьшились на 14. Экспорт содержит 1278 intblocks и 59 816 membership rows. `--check` повторного запуска сообщает 14 already-set, 0 pending и 0 conflicts; полный pytest, Ruff, проверка экспортов и `openspec validate --strict` прошли.

## Какие решения внесены

Две записи получили `igo`. Учредительное соглашение Global Crop Diversity Trust наделяет фонд собственной международной правосубъектностью, поэтому `CROPTRUST` — самостоятельный институт, а не название договора. Однако существующие 66 `includes` не совпадают с 28 участниками соглашения; это отдельная задача проверки состава, а не основание подменять категорию. [1] [2] Governing Instrument Green Climate Fund прямо предоставляет фонду юридическую личность, поэтому `GCF` также размечен `igo`; его 21 `includes` описывают вкладчиков, а не формальных членов фонда. [3]

Четыре записи получили `treaty_body`. Для `CACM` официальный договор создаёт общий рынок между государствами и учреждает отдельно правоспособный секретариат SIECA; правосубъектность SIECA нельзя переносить на сам CACM. [4] `TRACECA` действует в рамках Basic Multilateral Agreement; официальный регламент отдельно указывает, что межправительственная комиссия не является юридическим лицом. В записи есть также наблюдатели — их статус не следует считать сторонами договора. [5] [6] Petrocaribe учреждён соглашением об энергетическом сотрудничестве государств, а не самостоятельной IGO или неформальным форумом. [7] `ISS` размечен по представленному в записи межправительственному соглашению 1998 года, стороны которого образуют договорную рамку станции; сама физическая станция не является IGO. [8]

Четыре записи получили `policy_forum`. Учредительный договор AMERIPOL 2023 года предполагает будущую договорную организацию, но официальная публикация 2026 года сообщает лишь о второй ратификации при требуемых пяти; на проверенную дату это действующий механизм полицейского сотрудничества. [9] Для `CELSE` официальные материалы описывают коридор и транспортную услугу COSCO, не отдельную организацию. [10] `CKURAILWAY` — совместный инфраструктурный проект трёх государств; отдельное предприятие-исполнитель не тождественно проекту. [11] `IPSOS` — международная инициатива стандартов; официальный реестр внедрений не является членским реестром государств. [12]

Четыре записи получили `reference_enumeration`. `CFACENTRAL` и `CFAWEST` обозначают страны обращения соответствующего CFA franc, но не юридические лица BEAC/BCEAO или валютные союзы как самостоятельные институты. [13] [14] ECCB учреждён как юридическое лицо отдельным соглашением; `ECCU` в имеющейся записи означает восемь юрисдикций общей валюты. [15] Договоры ЕС закрепляют таможенный союз как часть Союза и наделяют правосубъектностью ЕС, не EUCU. При этом состав `EUCU` смешивает государства-члены и территории/страны с отдельными таможенными соглашениями; его roster нужно уточнять отдельно. [16]

## Какие четыре решения отложены

`ACIL` не следует помечать `igo`: UNESCO относит Arabic Language International Council к партнёрским NGO, а официальный список его членов состоит из организаций и учреждений, не стран. Нынешний список 22 стран в `includes` не подтверждён как членство ACIL. После расширения taxonomy следует рассмотреть `non_state_organization` и отдельно исправить состав. [17] [18]

`RDR` — постоянный межгосударственный совет, но официальный статут не устанавливает самостоятельную IGO-правосубъектность. Представители некоторых территорий участвуют через соответствующие органы, а Люксембург имеет иной статус. Ближе всего будущая категория `intergovernmental_body`; применять `igo` или трактовать страны как договорные стороны было бы неверно. [19]

`GCCPO` — патентное ведомство внутри Генерального секретариата GCC. Самостоятельного членства шести стран у ведомства нет: это государства материнского GCC и территория действия патентов. После обновления enum следует проверить `intergovernmental_body` и семантику `includes`. [20] [21]

`TAR` — сеть и платформа железнодорожного сотрудничества, которую поддерживает межправительственный договор. Официальный депозитарий перечисляет **22 стороны**, тогда как текущие `includes` содержат **28 стран** сети, включая подписантов без депонированных документов и страны покрытия. Поэтому `treaty_body` нельзя проставлять до решения, разделять ли запись о сети и запись о договоре либо как иначе моделировать их разные списки. [22] [23]

После нового OpenSpec-решения потребуется разобрать **19** оставшихся formal-записей: 15 первоначальных model-gap и эти четыре отсрочки. До этого предупреждение останется неблокирующим. Категории в текущем экспортированном наборе: 735 `igo`, 309 `treaty_body`, 61 `policy_forum`, 76 `reference_enumeration`; у 97 записей поле отсутствует, из них 19 formal и 78 других статусов.

## References

[1]: https://www.fao.org/fileadmin/user_upload/legal/docs/034t-e.pdf "FAO — Agreement for the Establishment of the Global Crop Diversity Trust"
[2]: https://www.fao.org/treaties/results/details/en/c/TRE-000073/ "FAO Treaties Database — Crop Diversity Trust"
[3]: https://www.greenclimate.fund/sites/default/files/document/governing-instrument.pdf "Green Climate Fund — Governing Instrument"
[4]: https://www.sica.int/download/?449 "SICA — Tratado General de Integración Económica Centroamericana"
[5]: https://traceca-org.org/tj/home/basic-documents/traceca-agreements/basic-multilateral-agreement-mla/ "TRACECA — Basic Multilateral Agreement"
[6]: https://traceca-org.org/fileadmin/fm-dam/pdfs/til_igc/en/2022/Rule3.pdf "TRACECA — Rules of Procedure, Rule 3"
[7]: https://jis.gov.jm/pm-says-petrocaribe-agreement-will-deepen-regional-ties/ "Jamaica Information Service — PetroCaribe Agreement"
[8]: https://www.state.gov/wp-content/uploads/2019/02/12927-Multilateral-Space-Space-Station-1.29.1998.pdf "U.S. Department of State — TIAS 12927 ISS Agreement"
[9]: https://ameripol.org/noticias/chile-deposita-el-instrumento-de-ratificacion-del-tratado-constitutivo-de-ameripol-y-fortalece-la-cooperacion-policial-en-las-americas/ "AMERIPOL — Chile deposits second ratification"
[10]: http://en.sasac.gov.cn/2024/05/23/c_17219.htm "SASAC — China-Europe Land-Sea Express Line logistics corridor"
[11]: https://english.www.gov.cn/news/202412/27/content_WS676eabb1c6d0868f4e8ee51f.html "State Council of China — CKU railway project"
[12]: https://international-patient-summary.net/cross-sdo-ips-collaboration/ "International Patient Summary — JIC IPS Coordination Committee"
[13]: https://www.beac.int/billets-pieces/mission-de-beac/ "BEAC — Rôle de la BEAC"
[14]: https://www.bceao.int/sites/default/files/inline-files/TraiteUMOA2010.pdf "BCEAO — UMOA Treaty"
[15]: https://www.eccb-centralbank.org/currency "Eastern Caribbean Central Bank — Currency"
[16]: https://eur-lex.europa.eu/LexUriServ/LexUriServ.do?uri=CELEX%3A12008E028%3AEN%3AHTML "EUR-Lex — TFEU Article 28"
[17]: https://www.unesco.org/sites/default/files/medias/fichiers/2026/09/List%20NGOs%20official%20partnership%20-%20Liste%20ONG%20partenariat%20officiel_September%202026.pdf "UNESCO — NGOs in official partnership, September 2026"
[18]: https://alarabiah.org/members/ "Arabic Language International Council — Members"
[19]: https://www.rechtschreibrat.com/DOX/statut.pdf "Rat für deutsche Rechtschreibung — Statut"
[20]: https://www.gcc-sg.org/en/AboutUs/Pages/OrganizationalStructure.aspx "GCC — Organizational Structure"
[21]: https://www.gcc-sg.org/en/MediaCenter/DigitalLibrary/Documents/7161447306380.pdf "GCC — The GCC Process and Achievements"
[22]: https://treaties.un.org/pages/viewdetails.aspx?src=treaty&mtdsg_no=xi-c-5&chapter=11&clang=_en "UN Treaty Collection — Trans-Asian Railway Network Agreement status"
[23]: https://www.unescap.org/our-work/transport/regional-land-transport/trans-asian-railway-network "UN ESCAP — Trans-Asian Railway Network"
