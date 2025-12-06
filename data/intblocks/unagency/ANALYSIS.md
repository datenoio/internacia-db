# Analysis of Missing UN Agency Records

## Current Status

The `data/intblocks/unagency` directory contains **34 files** (27 original + 7 newly created).

## UN System Structure

The UN system consists of:
1. **15 UN Specialized Agencies** (autonomous organizations)
2. **UN Funds and Programmes** (established by General Assembly)
3. **Other UN Entities** (various statuses)

## Existing Records in `unagency` Directory (27)

### UN Specialized Agencies (14/15)
1. ✅ **FAO** - Food and Agriculture Organization
2. ✅ **ICAO** - International Civil Aviation Organization
3. ✅ **IFAD** - International Fund for Agricultural Development
4. ✅ **ILO** - International Labour Organization
5. ✅ **IMO** - International Maritime Organization
6. ✅ **ITU** - International Telecommunication Union
7. ✅ **UNESCO** - United Nations Educational, Scientific and Cultural Organization
8. ✅ **UNIDO** - United Nations Industrial Development Organization
9. ✅ **UPU** - Universal Postal Union
10. ✅ **WHO** - World Health Organization
11. ✅ **WIPO** - World Intellectual Property Organization
12. ✅ **WMO** - World Meteorological Organization
13. ✅ **UNWTO** - United Nations World Tourism Organization
14. ✅ **IMF** - International Monetary Fund

**Note:** World Bank Group components (IBRD, IDA, IFC) exist in `bank/` directory. IBRD and IDA are specialized agencies, but the World Bank Group as a unified entity is not in `unagency/`.

### Other UN Entities (14)
15. ✅ **ECOSOC** - Economic and Social Council (UN principal organ)
16. ✅ **IAEA** - International Atomic Energy Agency (autonomous, not specialized agency)
17. ✅ **ICJ** - International Court of Justice (UN principal organ)
18. ✅ **UNDP** - United Nations Development Programme
19. ✅ **UNEP** - United Nations Environment Programme
20. ✅ **UNFPA** - United Nations Population Fund
21. ✅ **UNHABITAT** - United Nations Human Settlements Programme
22. ✅ **UNODC** - United Nations Office on Drugs and Crime
23. ✅ **UNOHRLLS** - Office of the High Representative for the Least Developed Countries
24. ✅ **UNOOSA** - United Nations Office for Outer Space Affairs
25. ✅ **UNRWA** - United Nations Relief and Works Agency for Palestine Refugees
26. ✅ **UNWOMEN** - United Nations Entity for Gender Equality
27. ✅ **WFP** - World Food Programme

## Missing Records (All Created ✅)

### UN Specialized Agencies (0 missing - 1 optional)
1. ⚠️ **World Bank Group (WBG)** - IBRD and IDA are specialized agencies (exist in `bank/` directory). The World Bank Group as a unified entity could be added to `unagency/` for completeness, though it's technically a group of institutions rather than a single specialized agency. **Status: Optional, not created**

### UN Funds and Programmes (2 created ✅)
2. ✅ **UNICEF** - United Nations Children's Fund - **CREATED**
3. ✅ **UNHCR** - United Nations High Commissioner for Refugees - **CREATED**

### Other UN Entities (5 created ✅)
4. ✅ **UNAIDS** - Joint United Nations Programme on HIV/AIDS - **CREATED**
5. ✅ **UNCTAD** - United Nations Conference on Trade and Development - **CREATED**
6. ✅ **UNOPS** - United Nations Office for Project Services - **CREATED**
7. ✅ **OHCHR** - Office of the High Commissioner for Human Rights - **CREATED**
8. ✅ **ITC** - International Trade Centre - **CREATED**

## Summary

**Total Created: 7 records**

- 2 UN Funds/Programmes (UNICEF, UNHCR)
- 5 Other UN Entities (UNAIDS, UNCTAD, UNOPS, OHCHR, ITC)

All missing records have been created in the `unagency/` directory following the same structure and format as existing files.

## Notes

- **UNICEF** and **UNHCR** exist in `data/intblocks/intorg/` with `blocktype: unagency` but should also have files in `unagency/` directory for consistency
- **World Bank Group** components (IBRD, IDA, IFC, MIGA, ICSID) exist in `data/intblocks/bank/` directory
- **IAEA** and **ICJ** are correctly placed in `unagency/` even though they are not technically specialized agencies
