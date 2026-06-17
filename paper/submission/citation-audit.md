# Citation Audit

Audit date: 2026-06-16.

Scope: all entries in `paper/references.bib`; no Tsiokos-authored entries were present.

Method:

- DOI entries were checked against Crossref (`https://api.crossref.org/works/{doi}`) and OpenAlex (`https://api.openalex.org/works/https://doi.org/{doi}`).
- The arXiv-only Hyper-Kamiokande entry was checked against arXiv and OpenAlex; DataCite was consulted but not used as the canonical BibTeX DOI because its creator metadata shortens the collaboration name.
- The no-DOI 't Hooft--Veltman original article was checked against CERN Document Server and Numdam.

Findings applied:

- `Witten1982`: fixed DOI from `10.1016/0370-2693(82)90973-X` (unrelated quark-search paper) to `10.1016/0370-2693(82)90728-6`; added issue `5`; normalized title case.
- `tHooftVeltman1974`: confirmed as a real no-DOI original journal article; added issue `1`, report number `CERN-TH-1723`, and stable Numdam URL.
- `HyperK2025`: confirmed real arXiv preprint `arXiv:2506.16641`; added arXiv URL.

| Key | Canonical ID | Source 1 | Source 2 | Result |
| --- | --- | --- | --- | --- |
| `Weinberg1967` | DOI `10.1103/PhysRevLett.19.1264` | Crossref | OpenAlex | Verified: title, journal, volume, pages, year. |
| `Bouchiat1972` | DOI `10.1016/0370-2693(72)90532-1` | Crossref | OpenAlex | Verified: title, journal, volume, pages, year. |
| `Witten1982` | DOI `10.1016/0370-2693(82)90728-6` | Crossref | OpenAlex; Princeton profile | Corrected and verified: title, journal, volume, issue, pages, year. |
| `KobayashiMaskawa1973` | DOI `10.1143/PTP.49.652` | Crossref | OpenAlex | Verified: title, journal, volume, pages, year. |
| `GeorgiGlashow1974` | DOI `10.1103/PhysRevLett.32.438` | Crossref | OpenAlex | Verified: title, journal, volume, pages, year. |
| `PatiSalam1974` | DOI `10.1103/PhysRevD.10.275` | Crossref | OpenAlex | Verified: title, journal, volume, pages, year. |
| `FritzschMinkowski1975` | DOI `10.1016/0003-4916(75)90211-0` | Crossref | OpenAlex | Verified: title, journal, volume, pages, year. |
| `Langacker1981` | DOI `10.1016/0370-1573(81)90059-4` | Crossref | OpenAlex | Verified: title, journal, volume, pages, year. |
| `SuperK2020` | DOI `10.1103/PhysRevD.102.112011` | Crossref | OpenAlex | Verified: title, journal, volume, article number, year. |
| `HyperK2025` | arXiv `2506.16641` | arXiv | OpenAlex; DataCite | Verified as arXiv preprint in `hep-ex`; arXiv ID kept canonical. |
| `Dirac1931` | DOI `10.1098/rspa.1931.0130` | Crossref | OpenAlex | Verified: title, journal, volume, pages, year. |
| `tHooft1974monopole` | DOI `10.1016/0550-3213(74)90486-6` | Crossref | OpenAlex | Verified: title, journal, volume, pages, year. |
| `tHooftVeltman1974` | CERN `CERN-TH-1723`; Numdam `AIHPA_1974__20_1_69_0` | CERN Document Server | Numdam | Verified: real original article, journal, volume, issue, pages, year; no original DOI found. |
| `GoroffSagnotti1985` | DOI `10.1016/0370-2693(85)91470-4` | Crossref | OpenAlex | Verified: title, journal, volume, pages, year. |
| `Maldacena1998` | DOI `10.4310/ATMP.1998.v2.n2.a1` | Crossref | OpenAlex | Verified: title, journal, volume, pages, year. |
| `RyuTakayanagi2006` | DOI `10.1103/PhysRevLett.96.181602` | Crossref | OpenAlex | Verified: title, journal, volume, article number, year. |
| `FreedmanHeadrick2017` | DOI `10.1007/s00220-016-2796-3` | Crossref | OpenAlex | Verified: title, journal, volume, pages; BibTeX year follows journal issue year. |
| `HaydenHeadrickMaloney2013` | DOI `10.1103/PhysRevD.87.046003` | Crossref | OpenAlex | Verified: title, journal, volume, article number, year. |
| `Faulkner2014` | DOI `10.1007/JHEP03(2014)051` | Crossref | OpenAlex | Verified: title, journal, volume/issue, article number, year. |
| `MaldacenaSusskind2013` | DOI `10.1002/prop.201300020` | Crossref | OpenAlex | Verified: title, journal, volume, pages, year. |
| `VanRaamsdonk2010` | DOI `10.1007/s10714-010-1034-0` | Crossref | OpenAlex | Verified: title, journal, volume, pages, year. |
| `Freivogel2015` | DOI `10.1103/PhysRevD.91.086013` | Crossref | OpenAlex | Verified: title, journal, volume, article number, year. |
| `Bekenstein1973` | DOI `10.1103/PhysRevD.7.2333` | Crossref | OpenAlex | Verified: title, journal, volume, pages, year. |
| `Hawking1976` | DOI `10.1103/PhysRevD.14.2460` | Crossref | OpenAlex | Verified: title, journal, volume, pages, year. |
| `Page1993` | DOI `10.1103/PhysRevLett.71.3743` | Crossref | OpenAlex | Verified: title, journal, volume, pages, year. |
| `Weinberg1989` | DOI `10.1103/RevModPhys.61.1` | Crossref | OpenAlex | Verified: title, journal, volume, pages, year. |
| `Bose2017` | DOI `10.1103/PhysRevLett.119.240401` | Crossref | OpenAlex | Verified: title, journal, volume, article number, year. |
| `MarlettoVedral2017` | DOI `10.1103/PhysRevLett.119.240402` | Crossref | OpenAlex | Verified: title, journal, volume, article number, year. |
| `Kafri2014` | DOI `10.1088/1367-2630/16/6/065020` | Crossref | OpenAlex | Verified: title, journal, volume, article number, year. |
| `Dyson2013` | DOI `10.1142/S0217751X1330041X` | Crossref | OpenAlex | Verified: title, journal, volume, article number, year. |
| `Bell1964` | DOI `10.1103/PhysicsPhysiqueFizika.1.195` | Crossref | OpenAlex | Verified: title, journal, volume, pages, year. |
| `CHSH1969` | DOI `10.1103/PhysRevLett.23.880` | Crossref | OpenAlex | Verified: title, journal, volume, pages, year. |
| `GHZ1989` | DOI `10.1007/978-94-017-0849-4_10` | Crossref | OpenAlex | Verified: chapter title, book title, pages, year. |
| `Anderson1972` | DOI `10.1126/science.177.4047.393` | Crossref | OpenAlex | Verified: title, journal, volume, pages, year. |
| `FordFulkerson1956` | DOI `10.4153/CJM-1956-045-5` | Crossref | OpenAlex | Verified: title, journal, volume, pages, year. |

Residual notes:

- Abbreviated journal names in `references.bib` are conventional and correspond to the full journal names returned by Crossref/OpenAlex.
- Some article-number journals return empty page fields in Crossref/OpenAlex and represent article numbers through publisher metadata. The BibTeX `pages` values are retained as article identifiers.
