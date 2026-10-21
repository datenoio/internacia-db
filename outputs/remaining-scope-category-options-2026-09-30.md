# Оставшиеся 19 предупреждений: статус и варианты разрешения

**Срез на 30 сентября 2026 года.** Валидатор и quality analyzer согласованно показывают **0 ошибок и 19 предупреждений `MISSING_SCOPE_CATEGORY`**. Все 19 записей имеют `status: formal`. В экспортированных 1278 intblocks поле не заполнено ещё у 78 записей других статусов; они в этот gate не входят. Присвоить 19 произвольных категорий технически просто, но это скроет проблемы правового статуса и состава участников. В этой проверке YAML, схема и экспорты **не изменялись**.

Оставшиеся записи делятся на восемь комиссий FAO, четыре фонда, три негосударственных объединения (`MSF`, `CANTO`, `ACIL`), два межгосударственных органа без самостоятельной IGO-личности (`RDR`, `GCCPO`), одну сеть (`TAR`) и одну коммерческую медиакомпанию (`TELESUR`). Это **19** отдельных случаев; не все решаются добавлением двух значений enum. Приведённые ниже категории — предложения, а не уже применённые метки.

## Восемь комиссий FAO: новая категория, но не единый тип договора

Для **CECAF, CIFAA, COPESCAALC, EIFAAC, SWIOFC и WECAFC** официальный FAO-реестр и учредительные акты подтверждают постоянные органы по **Article VI**, учреждённые решениями FAO. Их `includes` — формальные члены органов, а не стороны отдельного международного договора; независимую правосубъектность этих комиссий нельзя приписывать по одной лишь постоянной структуре. Рекомендация — сохранить записи и после утверждения новой категории присвоить `intergovernmental_body`, не `igo` и не `treaty_body`. [1] [2] [3] [4] [5] [6]

**APFIC** отличается от предыдущих: её Commission учреждена **Agreement по Article XIV**, но официальный текст помещает комиссию *within the framework* FAO. Запись именует именно комиссию, не Agreement; его стороны и членство комиссии связаны, но это не повод присвоить самой комиссии `treaty_body`. Рекомендуемая категория также `intergovernmental_body`; отдельную treaty-запись имеет смысл создавать только при реальной потребности в договорных запросах, не заменяя APFIC. Официальный текущий список из 21 члена совпадает с записью. [7] [8]

**CODEX** — совместный подчинённый орган FAO/WHO по Article VI, а не самостоятельная организация или конвенция. Для него также подходит `intergovernmental_body`, но одной метки недостаточно: в `includes` есть только **EU**, тогда как официальный состав — **188 государств и EU**. Вариант с полным roster предпочтителен; иначе надо явно представлять перечень как частичный, а не выдавать единственный элемент за весь состав. [9] [10]

У **COPESCAALC** отдельный долговой вопрос: официальный действующий акт использует **COPPESAALC** и изменённое полное имя; специализированный список FAO показывает **21** участника, включая Nicaragua, при 20 в YAML. Другая страница FAO всё ещё показывает 20, поэтому правка имени и roster должна сохранить ссылки и дату среза, не переименовывая стабильный ID без миграции aliases. Для **SWIOFC** официальное написание — *South West*, а не *Southwest*. Составы CECAF, CIFAA, EIFAAC, SWIOFC и WECAFC по проверенным реестрам в целом совпадают с YAML; для WECAFC в официальных страницах FAO есть расхождение 34/33, поэтому Nicaragua не следует удалять автоматически. [3] [5] [6] [11]

**Альтернатива без расширения enum** — временно оставить комиссии неклассифицированными с источниками и review-статусом. Искусственное `igo` завышает их независимость, а `policy_forum` стирает статутный характер. Удаление этих восьми записей не рекомендуется: их юридическая основа и большая часть roster проверяемы. В новом OpenSpec определение `intergovernmental_body` должно включать как Article VI, так и подчинённые Article XIV органы, но не любой договор автоматически. [1] [7]

## Четыре фонда: один самостоятельный IGO, два зависимых фонда и спорная архитектура

**AFDF (African Development Fund) — исключение из предварительного плана.** Его учредительный договор прямо делает фонд юридически отдельным от African Development Bank и наделяет полной правосубъектностью. Поэтому для самой записи подходит уже существующее `igo`, **не** будущее `intergovernmental_body`. При этом `includes: 82` — ошибочная смесь **29 государств-участников ADF** и государств-членов/получателей/доноров AfDB. Официальный voting statement перечисляет 29 State Participants; Bank — отдельный, не-country участник. Рекомендуется исправить roster и `membership_count` до присвоения метки либо в той же атомарной правке. Более дорогой вариант — отдельные типизированные связи для участников, доноров и получателей. [12] [13]

**ADF (Asian Development Fund)** — Special Fund, созданный и администрируемый ADB; правосубъектность и членство по Уставу принадлежат Bank, не Fund. Его 26 `includes` нельзя считать членами ADF: официальные donor и recipient rosters имеют разные роли и меняются по циклам финансирования. **AF (Adaptation Fund)** учреждён решением COP; его Board, а не список 24 стран-вкладчиков, осуществляет управление. Предложение для обоих — `intergovernmental_body` после изменения schema **и** удаление ложного `membership_count`/country-member roster. Если полезны вкладчики и получатели, хранить их отдельно с ролью, периодом и источником. Без ролевой модели допустимо оставить фонд как справочную запись без странового членства; подменять его `igo` нельзя. [14] [15] [16] [17]

**CIF (Climate Investment Funds)** — объединяющая архитектура двух отдельных трастов CTF и SCF, а не одна договорная IGO. Его 15 `includes` точно соответствуют официальному датированному списку **contributors**, однако `membership_count: 15` не означает число членов. Тут есть три корректных направления: (1) сохранить CIF как зонтичную институциональную запись и, после уточнения определения, обсудить `intergovernmental_body` **без** member roster; (2) выделить отдельную запись *«страны-вкладчики CIF на дату X»* с `reference_enumeration`, а сам CIF описывать отдельно; (3) отложить классификацию, если каталог не поддерживает эту пару сущностей. Просто присвоить текущей записи `reference_enumeration` **без переопределения её объекта** означало бы путать тип финансовой архитектуры с типом списка стран. `partof: WB` также требует проверки: роль trustee/host не обязательно означает организационную иерархию. [18] [19]

## Негосударственные организации и два зависимых органа

**MSF** и **CANTO** — подходящие кандидаты для предлагаемой категории `non_state_organization`, но их country `includes` не являются государствами-членами. У MSF официальное членство — ассоциации и отдельные лица, у CANTO — компании и учреждения, для которых country служит географическим атрибутом. Для обеих записей лучший вариант — оставить сущность, после утверждения enum присвоить новую категорию и убрать ложное country membership; если нужны членские данные, вводить roster организаций. Альтернатива — исключить записи именно из membership-экспорта, а не объявлять присутствие в стране межгосударственным членством. MSF дополнительно требует отличить движение 1971 года от отдельной швейцарской ассоциации MSF International. [20] [21] [22]

**ACIL** уже проверен ранее: UNESCO относит его к NGO, а официальный список членов состоит из организаций/учреждений, не 22 стран YAML. `non_state_organization` выглядит допустимо лишь вместе с решением об удалении или переосмыслении country roster и исправлением утверждения о межправительственном статусе. Более консервативно оставить предупреждение до такой правки; `igo` и фиктивное `policy_forum` ради тишины валидатора не рекомендованы. [23] [24]

**RDR** — устойчивый межгосударственный совет с индивидуальными представителями, без подтверждённой собственной международной правосубъектности. **GCCPO** — патентное ведомство внутри секретариата GCC, а шесть стран в записи — страны GCC и территория действия патента, не члены отдельной GCCPO-организации. Для обоих правдоподобна `intergovernmental_body` после уточнения критериев и описания значения country `includes`. Альтернативное `policy_forum` для RDR возможно лишь при **явном расширении** политики на постоянные нормативные органы; для GCCPO оно не подходит, потому что ведомство не форум. [25] [26]

## TAR и TELESUR требуют решения о границе самого реестра

**TAR:** официальный договор Trans-Asian Railway имеет **22 стороны**, но запись охватывает **28 стран** железнодорожной сети. Шесть дополнительных позиций не превращаются в стороны договора от того, что сеть действует в рамках Agreement. Предпочтителен **разделённый объект**: запись о договоре с подтверждёнными сторонами (`treaty_body`) и запись о сети/коридоре со своей географией и ясно названным смыслом `includes`. Если поддержка двух сущностей не нужна, выбрать одну: либо превратить нынешнюю TAR в договор и пересобрать roster по депозитарию, либо оставить сеть как кооперационную платформу и не приписывать странам party status. Категория для сети (`policy_forum` либо географическая enumeration) должна следовать из того, какую сущность проект фактически сохраняет. [27] [28]

**TELESUR:** официальные судебные документы называют юридического оператора **La Nueva Televisión del Sur (T.V. SUR) C.A.**, венесуэльской коммерческой компанией; при учреждении её капитал принадлежал Венесуэле. Текущие семь «стран-членов», даты присоединения и `intergovernmental` в YAML не подтверждают IGO, договор или межгосударственный орган. Предпочтительно **исключить запись из intblocks** после проверки downstream-зависимостей и сохранить при необходимости в отдельном реестре медиакомпаний. Второй вариант — отдельная будущая модель корпоративных государств-акционеров с удостоверенным и датированным shareholder roster. Маркировать её `intergovernmental_body` или `non_state_organization` нельзя только ради снятия предупреждения. [29]

## Рекомендуемая последовательность и варианты объёма

**Вариант A — семантически строгий (рекомендуется).** В OpenSpec сначала зафиксировать две новые категории и правило, что `scope_category` классифицирует **сущность**, а не тип её `includes`. Явно исключить AFDF из класса зависимых фондов. Затем отдельным data-этапом исправить roster и имена, где они недостоверны: прежде всего AFDF, CODEX, ADF, AF, MSF, CANTO, ACIL, COPESCAALC, GCCPO, TAR и TELESUR. Только после этого применять manifest с field-level provenance. Для CIF решить entity boundary; для TAR — split или одну семантику; для TELESUR — исключение либо отдельную корпоративную модель. Наконец, когда все formal-записи действительно классифицированы либо обоснованно выведены из scope, повышать отсутствие категории из warning в error. Издержка — новый enum и переносы в данных; выгода — проверяемые joins, а не только ноль предупреждений.

**Вариант B — поэтапное снижение предупреждений.** Сначала исправить AFDF roster и присвоить существующее `igo`: тогда **19 → 18**. После утверждения enum следующие **12** записей могут получить `intergovernmental_body` (восемь комиссий, ADF, AF, RDR, GCCPO), а **три** — `non_state_organization` (MSF, CANTO, ACIL), **но только вместе с устранением ложных country-member связей**: условно **18 → 3**. Останутся CIF, TAR, TELESUR — три разных решения об объекте записи/включении. Эти числа — сценарий при успешной правке roster, **не** достигнутый результат.

**Вариант C — сохранить нынешний enum.** Ограничиться точным `igo` для AFDF после исправления roster, а для CIF/TAR принимать решения об изменении предмета записи. Большинство предупреждений придётся оставить неблокирующими или исключить полезные записи. Этот путь не решает исходную проблему и лучше ложного массового `igo`, но хуже варианта A.

Не следует обещать неизменность числа intblocks/memberships в будущей миграции: исправление CODEX добавит страны, AFDF/NGO/фонды удалят ложные связи, а разделение TAR или исключение TELESUR изменят объём реестра. Для каждого изменения потребуются сверка manifest, поле-level provenance, тесты схемы/валидатора, пересборка экспортов и проверка downstream-интерфейсов. **Пока фактический статус остаётся 0 ошибок и 19 предупреждений.**

## References

[1]: https://www.fao.org/4/k8024e/k8024e.pdf "FAO Basic Texts — Constitution, Articles VI and XIV"
[2]: https://www.fao.org/cecaf/overview/en/ "FAO — CECAF Overview"
[3]: https://www.fao.org/unfao/govbodies/gsb-subject-matter/statutory-bodies-details/en/c/187/?no_cache=1 "FAO — CIFAA statutory-body record"
[4]: https://www.fao.org/eifaac/about/membership/en "FAO — EIFAAC membership"
[5]: https://www.fao.org/unfao/govbodies/gsb-subject-matter/statutory-bodies-details/en/c/661/ "FAO — SWIOFC statutory-body record"
[6]: https://www.fao.org/unfao/govbodies/gsb-subject-matter/statutory-bodies-details/en/c/179/?no_cache=1 "FAO — WECAFC statutory-body record"
[7]: https://www.fao.org/apfic/about/text-of-the--apfic-agreement/en "FAO — Text of APFIC Agreement"
[8]: https://www.fao.org/apfic/about/membership/en "FAO — APFIC membership"
[9]: https://www.fao.org/unfao/govbodies/gsb-subject-matter/statutory-bodies-details/en/c/211/?no_cache=1 "FAO — Codex Alimentarius Commission statutory-body record"
[10]: https://www.fao.org/fao-who-codexalimentarius/about-codex/members/en/ "FAO/WHO — Codex Members"
[11]: https://www.fao.org/fishery/organization/coppesaalc/en "FAO — COPPESAALC current fishery-body record"
[12]: https://www.afdb.org/fileadmin/uploads/afdb/Documents/Legal-Documents/Agreement_establishing_the_African_development_fund_2016_edition.pdf "AfDB — Agreement Establishing the African Development Fund"
[13]: https://www.afdb.org/sites/default/files/documents/board-documents/adf_-_statement_of_subscriptions_and_voting_powers_as_at_30_june_2025.pdf "African Development Fund — Statement of subscriptions and voting powers, 30 June 2025"
[14]: https://www.adb.org/sites/default/files/institutional-document/32120/amended-adb-charter-1mar2026.pdf "ADB — Amended Charter, Articles 19 and 49"
[15]: https://www.adb.org/what-we-do/funds/adf/overview "ADB — Asian Development Fund overview and donor/recipient roles"
[16]: https://unfccc.int/resource/docs/cop7/13a01.pdf "UNFCCC — Decision 10/CP.7 on Adaptation Fund"
[17]: https://www.adaptation-fund.org/about/governance/ "Adaptation Fund — Governance"
[18]: https://documents.worldbank.org/en/publication/documents-reports/documentdetail/784701476432289160 "World Bank Board — Climate Investment Funds CTF/SCF report"
[19]: https://www.cif.org/cif-contributors "Climate Investment Funds — Contributors"
[20]: https://www.msf.org/sites/default/files/2022-06/msf-international-statutes.pdf "Médecins Sans Frontières International — Statutes"
[21]: https://www.msf.org/how-we-are-run "MSF — How we are run"
[22]: https://canto.org/membership/listing "CANTO — Meet our Members"
[23]: https://www.unesco.org/sites/default/files/medias/fichiers/2026/09/List%20NGOs%20official%20partnership%20-%20Liste%20ONG%20partenariat%20officiel_September%202026.pdf "UNESCO — NGOs in official partnership, September 2026"
[24]: https://alarabiah.org/members/ "Arabic Language International Council — Members"
[25]: https://www.rechtschreibrat.com/DOX/statut.pdf "Rat für deutsche Rechtschreibung — Statut"
[26]: https://www.gcc-sg.org/en/AboutUs/Pages/OrganizationalStructure.aspx "GCC — Organizational Structure"
[27]: https://treaties.un.org/pages/viewdetails.aspx?src=treaty&mtdsg_no=xi-c-5&chapter=11&clang=_en "UN Treaty Collection — Trans-Asian Railway Agreement status"
[28]: https://www.unescap.org/our-work/transport/regional-land-transport/trans-asian-railway-network "UN ESCAP — Trans-Asian Railway Network"
[29]: https://caracas.tsj.gob.ve/DECISIONES/2014/JUNIO/2258-12-2564-14-164-14.HTML "TSJ Venezuela — Decision 2564-14 on T.V. SUR C.A."
