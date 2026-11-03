# Business transactions – Loanwise Zakelijk Light

Light-versie van de Loanwise-analyse voor zakelijke kredieten, volledig gebouwd op de categorisatie en analyse van Enable Now (E1, profielen `corporate` en `retail`). Alle data in deze repo is fictief.

## Inhoud

| Pad | Wat |
| --- | --- |
| `index.html` | De pagina (Loanwise Zakelijk Light). Open hem in een browser en laad een dataset via "Dataset laden" (zip of losse JSON-bestanden). Data wordt alleen in de browser verwerkt. |
| `datasets/slager/` | Eenmanszaak, 2 zakelijke rekeningen, 460 transacties (nov 2024 – okt 2025) |
| `datasets/lender-spender/` | B.V., 625 transacties; elke indicator en elke corporate-categorie geraakt |
| `datasets/mister-x/` | Eenmanszaak met aparte zakelijke (corporate) en privérekening (retail), 616 transacties |
| `generators/` | Python-scripts waarmee de sets zijn gemaakt |

Elke dataset bevat per Enable Now-call het verzoek en het antwoord: `01` token, `02` accounts, `03` categorisatiejob, `04` transacties (pagina's van 100), `05` analyse.

## Datasets opnieuw genereren

```bash
python3 generators/lender_spender.py datasets/lender-spender
python3 generators/mister_x.py datasets/mister-x
```

`slager_export.py` exporteert de ingebouwde voorbeelddata uit de pagina en heeft Playwright nodig:
`python3 generators/slager_export.py "$PWD/index.html" datasets/slager`

## Documentatie

- Handboek (invoer, verwerking per onderdeel, schema, testen, inschatting): https://claude.ai/artifact/N8cWcRenLTGmzwyGkwAFpZ
- Enable Now API: https://docs.enablenow.nl/

## Publiceren (Netlify)

Geen build nodig. `netlify.toml` publiceert de hoofdmap; `index.html` is de pagina.
In Netlify: Base directory leeg, Build command leeg, Publish directory leeg of `.`.
