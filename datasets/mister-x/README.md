# Voorbeeldset Enable Now – Mister X (fictief)

Eenmanszaak met twee rekeningen in één consent, elk met een eigen rekeningnummer en E1-profiel:

| Rekening | IBAN | Houder | E1-profiel |
| --- | --- | --- | --- |
| Zakelijk | NL45 RABO •••• ••17 | Mister X Consultancy | corporate |
| Privé | NL72 INGB •••• ••63 | Mister X | retail |

Periode nov 2025 – okt 2026, 616 transacties (235 zakelijk, 381 privé) in 7 pagina's.

## Bestanden
- 01 token · 02 accounts (beide rekeningen)
- 03a/03b categorisatiejob per rekening: corporate voor zakelijk, retail voor privé
- 04 transacties pagina 1–7: elke transactie draagt `category.e1.model.profile`
- 05a/05b analyse per profiel; 05a met `companyInfo` (KvK), 05b zonder
- `internal_ibans` bevat beide rekeningen: privé-opnamen staan op beide kanten als `internal.other`

## Leningen (voor het blok Actieve leningen)
| Rekening | Kredietverstrekker | Categorie | Maandlast | Status |
| --- | --- | --- | --- | --- |
| Privé | Hypotheekbank Nederland N.V. | housing.mortgage | € 1.385 | actief |
| Zakelijk | Rabobank | loan.bank | € 640 | actief |
| Zakelijk | Autolease Zakelijk B.V. | loan.vehicle_lease | € 590 | actief, 1× teruggeboekt (aug) |
| Privé | Creditcard Services B.V. | loan.credit_card | wisselend | actief |
| Privé | Persoonlijke Lening Direct B.V. | loan.other | € 245 | actief, 1× teruggeboekt (jun) |
| Privé | DUO | loan.student | € 112 | actief |
| Privé | Achteraf Betalen B.V. | loan.bnpl | € 80 | actief (aug–okt) |
| Zakelijk | Snelkrediet Zakelijk B.V. | loan.flash | — | afgelost (laatste termijn apr) |
| Privé | B. Jansen | loan.private | — | eenmalig, geen patroon |

## Overige hits
Privé: deurwaarder/incasso (sep), boete CJIB, 2× loterij, IB-betalingsregeling (jun–okt), ronde bedrag € 10.000 nalatenschap, kinderopvang + kinderbijslag, partnersalaris.
Zakelijk: btw per kwartaal, privéstorting (feb), extra privé-opname (jul), lage zekerheid op 2 posten.

Aanname: één categorisatie- en analysejob per rekening met een eigen profiel; nog te bevestigen door Enable Now.
