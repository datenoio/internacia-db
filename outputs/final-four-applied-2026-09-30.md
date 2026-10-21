# Завершение formal scope taxonomy — 30 сентября 2026 г.

**Все четыре оставшихся предупреждения закрыты** в worktree `manus/crosswalk-wb-remediation`. Это изменения в исходном YAML, коде валидации, тестах и автоматически пересобранных экспортах; коммит и релиз не создавались. Перед правками OpenSpec change [`complete-intblock-scope-taxonomy`](../openspec/changes/complete-intblock-scope-taxonomy/proposal.md) был уточнён и прошёл `--strict`.

Работа исправляет не только отсутствующие категории. Удалены связи со странами, которые были донорами, получателями, покрытием инфраструктуры или предполагаемыми акционерами, но **не** членами названных организаций. Для сети TAR сохранён старый ID; договор получил новый ID, а коммерческая компания teleSUR исключена с [документированным retirement ID](../docs/retired-intblock-ids.md), **без ложного alias**.

## Что изменилось

У AFDF исходные 82 страны были смешанным списком, а официальный состав Fund — 29 State Participants плюс Bank как отдельный не-страновой участник. По [учредительному соглашению](https://www.afdb.org/sites/default/files/documents/legal-documents/agreement_establishing_the_african_development_fund_2016_edition.pdf) Fund обладает самостоятельной правосубъектностью; по [ведомости голосов на 2025-09-30](https://www.afdb.org/sites/default/files/documents/board-documents/adf_-_statement_of_subscriptions_and_voting_powers_30_september_2025.pdf) 53 прежние country links не являются State Participants. Именно эти датированные источники использованы для roster и field-level provenance.

CIF и TAR требуют разграничения природы записи и её географии. CIF теперь описывает совместную архитектуру CTF и SCF по [официальному описанию управления](https://www.cif.org/governance), а не список 15 доноров. TAR — [платформа сети ESCAP](https://www.unescap.org/our-work/transport/regional-land-transport/trans-asian-railway-network); отдельно добавлен договор с 22 сторонами по [депозитарию ООН](https://treaties.un.org/pages/viewdetails.aspx?src=treaty&mtdsg_no=xi-c-5&chapter=11&clang=_en).

| Запись | Категория и результат |
|---|---|
| `AFDF` | `igo`; 29 State Participants вместо 82 смешанных связей; удалено неверное иерархическое `partof` |
| `CIF` | `intergovernmental_body`; 15 contributors удалены из membership, `membership_applicability: not_applicable`; World Bank trustee/host описан без `partof: WB` |
| `TAR` | `policy_forum`; охват 28 стран описан как география, а не членство; `includes` пуст, даты вступления в договор убраны из сети |
| `TARAGREEMENT` | новая самостоятельная запись `treaty_body` с 22 сторонами и датами по UNTC; Q-id сети не копировался, отсутствие отдельного Q-id задокументировано в exclusions |
| `TELESUR` | source YAML удалён вместе с семью неверными membership edges; в aliases нет фиктивного перенаправления, историю исключения фиксируют changelog и [retirement doc](../docs/retired-intblock-ids.md) |

## Проверка и границы результата

Сборка из source YAML создала согласованные JSON/Parquet/DuckDB артефакты. В итоговом DuckDB **256 countries, 1278 intblocks, 78 blocktypes и 59 569 memberships**: итоговое число intblocks неизменно только потому, что один договор добавлен и одна компания удалена. Из четырёх затронутых ID country-membership rows остались лишь у `AFDF` (29) и `TARAGREEMENT` (22). Идентификатор `TELESUR` отсутствует в intblocks и memberships, а `TAR` и `CIF` не порождают ложных country joins.

После включения строгого gate `status: formal` без `scope_category` становится **ошибкой** CLI-валидатора и **IMPORTANT**-проблемой quality analyzer; прежний directory labeler выдаёт только предложения. Проверка synthetic omission, regression suite с новым документированным SQL-рецептом, Ruff, оба валидатора, свежий quality analyzer, artifact guard, проверка счётчиков документации, внутренних Markdown-ссылок и `openspec validate ... --strict` прошли. **Сейчас 0 ошибок и 0 предупреждений в обоих валидаторах и 0 проблем в quality report.** Из 1106 formal-записей неклассифицированных не осталось.

Это не означает полной разметки всего реестра: **78 записей других статусов** ещё не имеют `scope_category`; семантический аудит прежних меток `igo` также остаётся отдельной задачей. Датированные rosters AFDF и TAR потребуется перепроверять при новых официальных публикациях. Исторический [отчёт о предыдущем cohort](scope-category-cohort-15-applied-2026-09-30.md) описывает состояние **до** этой миграции, когда четыре предупреждения ещё оставались.
