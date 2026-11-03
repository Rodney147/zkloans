"""Voorbeeldset Mister X: eenmanszaak met zakelijke (corporate) en privérekening (retail). Fictief."""
import json, math, random, uuid, calendar, os, sys
from collections import defaultdict

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
rnd = random.Random(20261103)
uid = lambda: str(uuid.UUID(int=rnd.getrandbits(128), version=4))

MONTHS = ['2025-11', '2025-12', '2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06', '2026-07', '2026-08', '2026-09', '2026-10']
LABELS = ['nov', 'dec', 'jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt']
CONSENT = uid()
ACC = {
    'zakelijk': {'id': uid(), 'iban': 'NL45 RABO •••• ••17', 'holder': 'Mister X Consultancy', 'start': 18400.00, 'profile': 'corporate', 'bank': 'Rabobank'},
    'prive': {'id': uid(), 'iban': 'NL72 INGB •••• ••63', 'holder': 'Mister X', 'start': 4250.00, 'profile': 'retail', 'bank': 'ING'},
}
TX = []
BD, BD_IBAN = 'Belastingdienst', 'NL86 INGB 0002 4455 88'

def iban_for(name):
    h = sum(ord(c) * (i + 11) for i, c in enumerate(name)) % 9973
    bank = ['INGB', 'RABO', 'ABNA', 'KNAB', 'BUNQ', 'TRIO', 'SNSB'][h % 7]
    return f'NL{h % 89 + 10} {bank} •••• ••{h % 90 + 10}'

def add(m, day, acc, amount, name, desc, cat, conf, flags=(), iban=None):
    y, mo = map(int, MONTHS[m].split('-'))
    day = min(day, calendar.monthrange(y, mo)[1])
    a = ACC[acc]
    TX.append({
        'id': uid(), 'accountId': a['id'], 'accountNumber': a['iban'], 'description': desc,
        'bookDate': f'{MONTHS[m]}-{day:02d}', 'transactionDateTime': None, 'amount': round(amount, 2),
        'balanceAfterTransaction': None, 'currency': 'EUR', 'counterpartDescription': name,
        'counterpartAccountNumber': iban if iban is not None else (iban_for(name) if name else None),
        'normalized': {'description': desc.lower(), 'counterpartDescription': name.lower().replace('.', '').replace(',', '') if name else None},
        'category': {'e1': {'category': cat, 'confidence': round(conf, 2), 'flags': list(flags),
                            'model': {'version': 'e1-2026.10', 'profile': a['profile'], 'countryCode': 'nl'}}},
    })

Z, P = 'zakelijk', 'prive'

# ================= Zakelijk (eenmanszaak, E1 corporate) =================
CLIENTS = [('Gemeente Amersfoort', 4200), ('Zorggroep Utrecht B.V.', 3600), ('Logistiek Centrum Midden B.V.', 2900), ('Bouwfonds Regio B.V.', 2400),
           ('Onderwijsstichting Eemland', 1800), ('Retail Partners Nederland B.V.', 1500), ('Adviesbureau Kroon V.O.F.', 950), ('Techniek Holland B.V.', 1200)]
season = [1.0, 0.85, 0.9, 1.0, 1.05, 1.0, 1.05, 1.1, 0.7, 0.8, 1.1, 1.05]
inv = 1100
for m in range(12):
    for name, base in CLIENTS:
        if rnd.random() < 0.88:
            inv += 1
            add(m, rnd.randint(3, 27), Z, base * 0.8 * season[m] * rnd.uniform(0.8, 1.2), name, f'Factuur {MONTHS[m][:4]}-{inv}', 'income.other', rnd.uniform(0.82, 0.97))
    lab = LABELS[m]
    add(m, 1, Z, -475, 'Coworking De Werkplaats B.V.', f'Flexplek {lab}', 'office.rent', 0.94)
    add(m, 4, Z, -89, 'Software Abonnementen B.V.', 'Licenties', 'expense.it', 0.9)
    add(m, 18, Z, -62.5, 'Telecom Zakelijk B.V.', 'Mobiel abonnement', 'expense.operations.telecom', 0.95)
    add(m, 1, Z, -16.5, 'Rabobank', 'Kosten Rabo Zakelijk', 'expense.operations.bank_fees', 0.99, iban='NL·· RABO bank')
    add(m, 1, Z, -265, 'AOV Verzekeraar N.V.', 'Premie arbeidsongeschiktheid', 'insurance.other', 0.86)
    add(m, 28, Z, -640, 'Rabobank', 'Aflossing en rente bedrijfskrediet 31.07.552', 'loan.bank', 0.95, iban='NL·· RABO bank')
    add(m, 2, Z, -590.4, 'Autolease Zakelijk B.V.', f'Leasetermijn Skoda Enyaq {lab}', 'loan.vehicle_lease', 0.96)
    for _ in range(2):
        add(m, rnd.randint(3, 26), Z, -rnd.uniform(45, 85), 'Laadpunt Zakelijk B.V.', 'Laden leaseauto', 'expense.transport.fuel', 0.9)
    add(m, 25, Z, -5800, 'Mister X', 'Privé-opname', 'internal.other', 1.0, iban=ACC[P]['iban'])
    add(m, 25, P, 5800, 'Mister X Consultancy', 'Van zakelijke rekening', 'internal.other', 1.0, iban=ACC[Z]['iban'])
    if m % 2 == 0:
        add(m, 10, Z, -150, 'Online Advertenties B.V.', 'Campagne LinkedIn', 'expense.marketing', 0.84)
for m in (0, 3, 6, 9):
    add(m, 15, Z, -425, 'Administratiekantoor Visser', 'Administratie kwartaal', 'expense.accounting', 0.89)
for m, amount, q in ((2, -4820, 'Q4 2025'), (5, -4310, 'Q1 2026'), (8, -4590, 'Q2 2026'), (11, -4975, 'Q3 2026')):
    add(m, 30, Z, amount, BD, f'Omzetbelasting {q}', 'tax.vat', 0.97, iban=BD_IBAN)
zak_one = [
    (1, 9, Z, 6000, 'Snelkrediet Zakelijk B.V.', 'Uitbetaling flexkrediet', 'loan.flash', 0.86, ()),
    (2, 9, Z, -1575, 'Snelkrediet Zakelijk B.V.', 'Termijn flexkrediet', 'loan.flash', 0.86, ()),
    (3, 9, Z, -1575, 'Snelkrediet Zakelijk B.V.', 'Termijn flexkrediet', 'loan.flash', 0.86, ()),
    (4, 9, Z, -1575, 'Snelkrediet Zakelijk B.V.', 'Termijn flexkrediet', 'loan.flash', 0.86, ()),
    (5, 9, Z, -1575, 'Snelkrediet Zakelijk B.V.', 'Termijn flexkrediet, laatste', 'loan.flash', 0.86, ()),
    (0, 3, Z, -980, 'Zakelijk Verzekerd B.V.', 'Jaarpremie beroepsaansprakelijkheid', 'insurance.liability', 0.9, ()),
    (4, 20, Z, -312, 'Drukkerij Snel B.V.', 'Visitekaartjes en flyers', 'expense.marketing', 0.85, ()),
    (6, 14, Z, -1249, 'Laptop Shop B.V.', 'MacBook Pro', 'expense.it', 0.77, ()),
    (3, 12, Z, -38, 'Parkeergarage Centrum', 'Parkeren klant', 'expense.transport.parking', 0.95, ()),
    (8, 5, Z, -52, 'Parkeergarage Centrum', 'Parkeren klant', 'expense.transport.parking', 0.95, ()),
    (7, 11, Z, -186, 'Treinreizen NL', 'Zakelijke reis', 'expense.transport.public_transport', 0.88, ()),
    (9, 3, Z, 590.4, 'Autolease Zakelijk B.V.', 'Terugboeking incasso: onvoldoende saldo', 'loan.vehicle_lease', 0.93, ('reversal_payment',)),
    (9, 16, Z, -590.4, 'Autolease Zakelijk B.V.', 'Leasetermijn Skoda Enyaq sep (herhaald)', 'loan.vehicle_lease', 0.95, ()),
    (8, 24, Z, -1500, 'Mister X', 'Privé-opname vakantie', 'internal.other', 1.0, (), ACC[P]['iban']),
    (8, 24, P, 1500, 'Mister X Consultancy', 'Van zakelijke rekening', 'internal.other', 1.0, (), ACC[Z]['iban']),
    (3, 6, P, -2000, 'Mister X Consultancy', 'Storting in de zaak', 'internal.other', 1.0, (), ACC[Z]['iban']),
    (3, 6, Z, 2000, 'Mister X', 'Privéstorting', 'internal.other', 1.0, (), ACC[P]['iban']),
    (5, 17, Z, 1850, None, 'Overboeking', 'income.other', 0.47, ()),
    (10, 21, Z, -640, 'Coaching & Co', 'Training', 'other.other', 0.52, ()),
]

# ================= Privé (E1 retail) =================
for m in range(12):
    lab = LABELS[m]
    add(m, 24, P, 2780 + (40 if m >= 2 else 0), 'Zorggroep Noord', f'Salaris {lab} (partner)', 'income.salary', 0.95)
    add(m, 1, P, -1385.4, 'Hypotheekbank Nederland N.V.', 'Hypotheek leningdeel 1 en 2', 'housing.mortgage', 0.97)
    add(m, 1, P, -145, 'VvE Lindenhof', 'Servicekosten', 'housing.other', 0.9)
    add(m, 27, P, -245, 'Persoonlijke Lening Direct B.V.', 'Termijn persoonlijke lening 88120', 'loan.other', 0.93)
    add(m, 20, P, -round(rnd.uniform(180, 650), 2), 'Creditcard Services B.V.', 'Afschrijving creditcard', 'loan.credit_card', 0.94)
    add(m, 28, P, -112.4, 'DUO', 'Aflossing studieschuld', 'loan.student', 0.97)
    add(m, 22, P, -540, BD, 'Voorlopige aanslag inkomstenbelasting 2026' if m >= 2 else 'Voorlopige aanslag inkomstenbelasting 2025', 'tax.income', 0.95, iban=BD_IBAN)
    add(m, 1, P, -298.6, 'Zorgverzekeraar Midden', 'Premie zorgverzekering 2 personen', 'insurance.health', 0.97)
    add(m, 1, P, -64.2, 'Autoverzekeraar Direct N.V.', 'Premie autoverzekering', 'insurance.vehicle', 0.95)
    add(m, 1, P, -38.9, 'Woonverzekering Online', 'Premie inboedel en opstal', 'insurance.other', 0.9)
    add(m, 14, P, -195, 'Energie Huishouden B.V.', 'Termijnbedrag energie', 'expense.essential.utilities.energy', 0.95)
    add(m, 19, P, -92.5, 'Telecom Thuis B.V.', 'Internet en mobiel', 'expense.essential.telecom', 0.95)
    add(m, 2, P, -720, 'Kinderopvang Zonnetje B.V.', f'Opvang {lab}', 'expense.essential.childcare', 0.94)
    add(m, rnd.randint(5, 25), P, -rnd.uniform(18, 55), 'Drogisterij Midden', 'Betaalautomaat', 'expense.essential.personal_care', 0.88)
    add(m, 6, P, -13.99, 'Streamingdienst Films', 'Abonnement', 'expense.lifestyle.streaming', 0.97)
    add(m, 6, P, -10.99, 'Muziekstreaming', 'Abonnement', 'expense.lifestyle.streaming', 0.97)
    add(m, 3, P, -39, 'Sportschool FitPlus', 'Lidmaatschap', 'expense.lifestyle.sports', 0.93)
    add(m, 26, P, -600, 'Spaarrekening Oranje', 'Maandelijkse inleg', 'investment.savings', 0.88)
    for w in range(4):
        add(m, 3 + w * 7, P, -rnd.uniform(70, 165), rnd.choice(['Supermarkt Plus', 'Supermarkt Groen', 'Buurtsuper De Hoek']), 'Betaalautomaat', 'expense.essential.groceries', rnd.uniform(0.9, 0.98))
    for _ in range(2):
        add(m, rnd.randint(4, 27), P, -rnd.uniform(22, 85), rnd.choice(['Restaurant De Linde', 'Pizzeria Roma', 'Café Het Plein']), 'Betaalautomaat', 'expense.lifestyle.restaurants_bars', 0.9)
        add(m, rnd.randint(4, 27), P, -rnd.uniform(50, 80), 'Tankstation Utrechtseweg', 'Tanken', 'expense.transport.fuel', 0.93)
    if m % 2 == 1:
        add(m, 16, P, -rnd.uniform(60, 180), 'Kledingwinkel Stad', 'Betaalautomaat', 'expense.essential.clothing', 0.86)
    if m >= 3:
        add(m, 28, P, -98, 'Gemeente Utrecht', 'Termijn gemeentelijke belastingen 2026', 'expense.essential.municipal', 0.92)
for m in (2, 5, 8, 11):
    add(m, 1, P, 285.6, 'Sociale Verzekeringsbank', 'Kinderbijslag kwartaal', 'subsidy.family', 0.98)
    add(m, 12, P, -58.4, 'Waterbedrijf Midden', 'Drinkwater kwartaal', 'expense.essential.utilities.water', 0.94)
for m in (1, 4, 7, 10):
    add(m, 20, P, -186, BD, 'Motorrijtuigenbelasting', 'tax.vehicle', 0.94, iban=BD_IBAN)
for m in (9, 10, 11):
    add(m, 12, P, -79.95, 'Achteraf Betalen B.V.', 'Termijn bestelling tuinset', 'loan.bnpl', 0.9)
for m in (7, 8, 9, 10, 11):
    add(m, 23, P, -300, BD, 'Betalingsregeling aanslag IB 2024', 'tax.income', 0.81, ['payment_arrangement'], iban=BD_IBAN)
prive_one = [
    (7, 30, P, 245, 'Persoonlijke Lening Direct B.V.', 'Terugboeking incasso: onvoldoende saldo', 'loan.other', 0.92, ('reversal_payment',)),
    (8, 8, P, -245, 'Persoonlijke Lening Direct B.V.', 'Termijn juli (herhaald)', 'loan.other', 0.93, ()),
    (10, 15, P, -186.5, 'Incassobureau West B.V.', 'Vordering 30981 energie oud adres', 'loan.debt_collection', 0.92, ()),
    (5, 9, P, -95, 'CJIB', 'Verkeersboete', 'other.fines', 0.95, ()),
    (1, 28, P, -15, 'Nederlandse Loterij', 'Staatsloterij oudejaars', 'gambling.lottery', 0.93, ()),
    (6, 2, P, -12.5, 'Nederlandse Loterij', 'Postcodeloterij', 'gambling.lottery', 0.9, ()),
    (8, 1, P, -2390, 'Vakantieparken Europa B.V.', 'Vakantie Frankrijk', 'expense.lifestyle.travel', 0.92, ()),
    (4, 18, P, -145, 'Tandartspraktijk Wilhelminapark', 'Behandeling eigen bijdrage', 'expense.essential.medical', 0.89, ()),
    (3, 9, P, -11, 'Parkeren Utrecht', 'Parkeren', 'expense.transport.parking', 0.94, ()),
    (6, 21, P, -24.6, 'Treinreizen NL', 'Dagretour', 'expense.transport.public_transport', 0.9, ()),
    (9, 7, P, -410, 'Garage Van Rijn', 'Onderhoud auto', 'expense.transport.vehicle', 0.9, ()),
    (1, 15, P, -50, 'Stichting Voedselbank', 'Donatie', 'expense.lifestyle.donations', 0.9, ()),
    (0, 12, P, -200, 'Geldautomaat Utrecht', 'Geldopname', 'cash.other', 0.98, (), 'NL·· geldautomaat'),
    (6, 12, P, -100, 'Geldautomaat Utrecht', 'Geldopname', 'cash.other', 0.98, (), 'NL·· geldautomaat'),
    (3, 22, P, 35, 'J. Smit', 'Tikkie etentje', 'other.private_transfer', 0.74, ('payment_request',)),
    (7, 13, P, 42.5, 'L. de Wit', 'Tikkie uitje', 'other.private_transfer', 0.72, ('payment_request',)),
    (9, 4, P, 10000, 'Notariskantoor Bergsma', 'Uitkering nalatenschap', 'other.other', 0.48, ()),
    (4, 3, P, -350, None, 'Overboeking', 'other.other', 0.44, ()),
    (10, 27, P, -275, 'B. Jansen', 'Lening terug', 'loan.private', 0.58, ()),
    (2, 11, P, -42, 'Dierenkliniek Oost', 'Consult kat', 'expense.lifestyle.pets', 0.88, ()),
]
for row in zak_one + prive_one:
    add(*row[:8], flags=row[8], **({'iban': row[9]} if len(row) > 9 else {}))

# ---------- volgorde, tijdstempels, saldo ----------
TX.sort(key=lambda t: (t['bookDate'], t['amount'] < 0, t['id']))
per_day = defaultdict(int)
for t in TX:
    per_day[t['bookDate']] += 1
    n = per_day[t['bookDate']]
    t['transactionDateTime'] = f"{t['bookDate']}T{7 + n // 6:02d}:{(n * 9) % 60:02d}:00Z"
for a in ACC.values():
    bal = a['start']
    for t in TX:
        if t['accountId'] == a['id']:
            bal = round(bal + t['amount'], 2)
            t['balanceAfterTransaction'] = bal
    a['end'] = bal

# ---------- analyses per profiel ----------
cat = lambda r: r['category']['e1']['category']
fl = lambda r: r['category']['e1']['flags']
cf = lambda r: r['category']['e1']['confidence']
def entry(name, rows):
    return {'name': name, 'transactionCount': len(rows), 'totalInflow': round(sum(r['amount'] for r in rows if r['amount'] > 0), 2),
            'totalOutflow': round(-sum(r['amount'] for r in rows if r['amount'] < 0), 2),
            'categories': sorted({cat(r) for r in rows}), 'transactionIds': [r['id'] for r in rows]}
LEASES = {'loan.debt_collection', 'loan.vehicle_lease', 'loan.equipment_lease'}
CORPORATE = [('Taxes', lambda r: cat(r).startswith('tax.')), ('Loans', lambda r: cat(r).startswith('loan.') and cat(r) not in LEASES),
             ('Debt collection', lambda r: cat(r) == 'loan.debt_collection'), ('Vehicle Lease', lambda r: cat(r) == 'loan.vehicle_lease'),
             ('Equipment Lease', lambda r: cat(r) == 'loan.equipment_lease'), ('Internal transactions', lambda r: cat(r) == 'internal.other'),
             ('Gambling', lambda r: cat(r).startswith('gambling.')), ('Crypto', lambda r: cat(r) == 'investment.crypto')]
RETAIL = [('Internal transactions', lambda r: cat(r) == 'internal.other'),
          ('Car', lambda r: cat(r) in ('tax.vehicle', 'expense.transport.vehicle', 'insurance.vehicle', 'expense.transport.fuel', 'expense.transport.parking')),
          ('Child', lambda r: cat(r) in ('expense.essential.childcare', 'subsidy.family')), ('Divorced', lambda r: cat(r).startswith('alimony.')),
          ('Pension', lambda r: cat(r).startswith('income.pension.')), ('Unemployed', lambda r: cat(r) == 'subsidy.unemployment'),
          ('Loans', lambda r: cat(r).startswith('loan.') and cat(r) != 'loan.debt_collection'), ('Debt collection', lambda r: cat(r) == 'loan.debt_collection'),
          ('Salary', lambda r: cat(r) == 'income.salary'), ('Housing', lambda r: cat(r).startswith('housing.')),
          ('Other benefits', lambda r: cat(r).startswith('subsidy.') and cat(r) not in ('subsidy.unemployment', 'subsidy.family', 'subsidy.family.income')),
          ('Fines', lambda r: cat(r) == 'other.fines'), ('Gambling', lambda r: cat(r).startswith('gambling.')), ('Crypto', lambda r: cat(r) == 'investment.crypto')]
def analysis_for(key, buckets, company):
    a = ACC[key]
    rows = [r for r in TX if r['accountId'] == a['id']]
    def top(side):
        groups = defaultdict(list)
        for r in rows:
            if (r['amount'] > 0) == (side == 'inflow'):
                groups[r['counterpartDescription'] or 'Unknown'].append(r)
        ranked = sorted(groups.items(), key=lambda kv: -abs(sum(r['amount'] for r in kv[1])))[:5]
        return {str(i): entry(n, rs) for i, (n, rs) in enumerate(ranked)}
    return {
        'generalInfo': {'startDate': '2025-11-01', 'endDate': '2026-10-31', 'startBalance': a['start'], 'endBalance': a['end'],
                        'accounts': [{'iban': a['iban'], 'accountName': a['holder'], 'accountId': a['id']}],
                        'totalInflow': round(sum(r['amount'] for r in rows if r['amount'] > 0), 2), 'totalOutflow': round(-sum(r['amount'] for r in rows if r['amount'] < 0), 2)},
        'companyInfo': company,
        'topCounterparties': {'inflow': top('inflow'), 'outflow': top('outflow')},
        'clientProfile': [entry(n, [r for r in rows if t(r)]) for n, t in buckets],
        'flaggedTransactions': [entry('Reversal payments', [r for r in rows if 'reversal_payment' in fl(r)]), entry('Refunds', [r for r in rows if 'refund' in fl(r)]),
                                entry('Payment arrangements', [r for r in rows if 'payment_arrangement' in fl(r)])],
        'lowConfidenceTransactions': [entry('Confidence <50%', [r for r in rows if cf(r) < 0.5]), entry('50% <= Confidence <60%', [r for r in rows if 0.5 <= cf(r) < 0.6])],
        'otherHighlightedTransactions': [entry('Round number', [r for r in rows if abs(r['amount']) >= 10000 and float(r['amount']).is_integer() and abs(r['amount']) % 10000 == 0])],
        'creditQualityMetrics': [],
    }
company = {'kvkNumber': '74561230', 'name': 'Mister X Consultancy', 'address': 'Maliebaan 12, Utrecht', 'industryCode': '70221',
           'industryDescription': 'Organisatie-adviesbureaus', 'legalForm': 'Eenmanszaak', 'numberOfEmployees': 1,
           'startDate': '2019-09-01T00:00:00', 'registrationDate': '2019-09-04T00:00:00'}
ANALYSES = {'corporate': analysis_for(Z, CORPORATE, company), 'retail': analysis_for(P, RETAIL, None)}

# ---------- bestanden ----------
dump = lambda name, obj: json.dump(obj, open(os.path.join(OUT, name), 'w'), indent=2, ensure_ascii=False)
ibans = [a['iban'] for a in ACC.values()]
dump('01-token.json', {'request': {'method': 'POST', 'path': '/connect/token', 'contentType': 'application/x-www-form-urlencoded', 'body': {'client_id': '<client_id>', 'client_secret': '<client_secret>', 'scope': 'customer-api', 'grant_type': 'client_credentials'}}, 'response_200': {'accessToken': '<jwt>', 'expiresIn': 3600, 'tokenType': 'Bearer'}, 'note': 'Responsvelden en geldigheid zijn een aanname.'})
dump('02-get-accounts.json', {'request': {'method': 'GET', 'path': '/Accounts', 'query': {'ConsentId': CONSENT}}, 'response_200': {'data': [{'id': a['id'], 'iban': a['iban'], 'providerAccountId': a['bank'].lower()[:4] + '-' + a['id'][:8], 'accountHolder': a['holder'], 'bban': None, 'currency': 'EUR', 'accountBalance': {'currency': 'EUR', 'date': '2026-10-31T23:59:59Z', 'amount': a['end']}} for a in ACC.values()]}})
for suffix, key in (('a-corporate', Z), ('b-retail', P)):
    a, job = ACC[key], uid()
    meta = {'internal_ibans': ibans}
    dump(f'03{suffix}-categorization-job.json', {'request': {'method': 'POST', 'path': '/v2/categorization-jobs', 'body': {'engine': 'e1', 'profile': a['profile'], 'countryCode': 'nl', 'consentId': CONSENT, 'accountIds': [a['id']], 'metaData': meta}}, 'response_202': {'data': job}, 'poll': {'method': 'GET', 'path': f'/v2/categorization-jobs/{job}', 'response_200': {'data': {'id': job, 'status': 'COMPLETED', 'engine': 'e1', 'profile': a['profile'], 'countryCode': 'nl', 'consentId': CONSENT, 'userId': None, 'externalUserId': None, 'accountIds': [a['id']], 'parentId': None, 'engineVersion': 'e1-2026.10', 'metaData': meta}}}, 'note': 'Eén job per rekening met een eigen profiel is een aanname; navragen bij Enable Now.'})
desc = sorted(TX, key=lambda t: (t['bookDate'], t['transactionDateTime'], t['id']), reverse=True)
pages = math.ceil(len(desc) / 100)
for i in range(pages):
    dump(f'04-get-transactions-page-{i + 1}.json', {'request': {'method': 'GET', 'path': '/Transactions', 'query': {'ConsentId': CONSENT, 'DateFrom': '2025-11-01T00:00:00Z', 'DateTo': '2026-10-31T23:59:59Z', 'OrderBy': 'bookDate', 'OrderDirection': 'desc', 'PageSize': 100, 'PageToken': None if i == 0 else f'pg{i + 1}'}}, 'response_200': {'data': desc[i * 100:(i + 1) * 100], 'nextPageToken': None if i == pages - 1 else f'pg{i + 2}'}})
for suffix, key, profile in (('a-corporate', Z, 'corporate'), ('b-retail', P, 'retail')):
    a, job = ACC[key], uid()
    body = {'reference': f'Dossier Mister X {profile}', 'engine': 'e1', 'profile': profile, 'countryCode': 'nl', 'input': {'accountIds': [a['id']]}, 'metaData': {'internal_ibans': ibans, **({'kvk_number': '74561230'} if profile == 'corporate' else {})}, 'dateFrom': '2025-11-01T00:00:00Z', 'dateTo': '2026-10-31T23:59:59Z'}
    dump(f'05{suffix}-analysis-job.json', {'request': {'method': 'POST', 'path': '/analysis-jobs', 'body': body}, 'poll': {'method': 'GET', 'path': f'/analysis-jobs/{job}'}, 'response_200': {'id': job, 'status': 'COMPLETED', 'engine': 'e1', 'profile': profile, 'analysis': ANALYSES[profile]}})

# ---------- samenvatting ----------
for key in (Z, P):
    rows = [r for r in TX if r['accountId'] == ACC[key]['id']]
    print(key, len(rows), 'tx · categorieën', len({cat(r) for r in rows}), '· eindsaldo', ACC[key]['end'])
print('totaal', len(TX), 'pagina\'s', pages)
for p, an in ANALYSES.items():
    print(p, [(e['name'], e['transactionCount']) for e in an['clientProfile']])
    print('  ', [(e['name'], e['transactionCount']) for s in ('flaggedTransactions', 'lowConfidenceTransactions', 'otherHighlightedTransactions') for e in an[s]])
