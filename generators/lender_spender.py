"""Voorbeeldset Lender Spender Zakelijke B.V. in Enable Now-formaat (fictief)."""
import json, math, random, uuid, calendar, os, sys
from collections import defaultdict

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
rnd = random.Random(20261031)
uid = lambda: str(uuid.UUID(int=rnd.getrandbits(128), version=4))

MONTHS = ['2025-11', '2025-12', '2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06', '2026-07', '2026-08', '2026-09', '2026-10']
LABELS = ['nov', 'dec', 'jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt']
CONSENT = uid()
HOLDER = 'Lender Spender Zakelijke B.V.'
ACC = [
    {'id': uid(), 'iban': 'NL27 INGB •••• ••51', 'start': 41850.00, 'kind': 'Zakelijke betaalrekening'},
    {'id': uid(), 'iban': 'NL63 INGB •••• ••08', 'start': 25000.00, 'kind': 'Zakelijke spaarrekening'},
]
MAIN, SAVE = 0, 1
TX = []

def iban_for(name):
    h = sum(ord(c) * (i + 7) for i, c in enumerate(name)) % 9973
    bank = ['INGB', 'RABO', 'ABNA', 'KNAB', 'BUNQ', 'TRIO', 'SNSB'][h % 7]
    return f'NL{h % 89 + 10} {bank} •••• ••{h % 90 + 10}'

def add(m, day, acc, amount, name, desc, cat, conf, flags=(), iban=None):
    y, mo = map(int, MONTHS[m].split('-'))
    day = min(day, calendar.monthrange(y, mo)[1])
    TX.append({
        'id': uid(), 'accountId': ACC[acc]['id'], 'accountNumber': ACC[acc]['iban'], 'description': desc,
        'bookDate': f'{MONTHS[m]}-{day:02d}', 'transactionDateTime': None, 'amount': round(amount, 2),
        'balanceAfterTransaction': None, 'currency': 'EUR', 'counterpartDescription': name,
        'counterpartAccountNumber': iban if iban is not None else (iban_for(name) if name else None),
        'normalized': {'description': desc.lower(), 'counterpartDescription': name.lower().replace('.', '').replace(',', '') if name else None},
        'category': {'e1': {'category': cat, 'confidence': round(conf, 2), 'flags': list(flags),
                            'model': {'version': 'e1-2026.10', 'profile': 'corporate', 'countryCode': 'nl'}}},
    })

BD = 'Belastingdienst'
BD_IBAN = 'NL86 INGB 0002 4455 88'

# ---------- Omzet: 16 afnemers, 1 grote, groei ~12,5% per maand ----------
growth = [1, 1.11, 1.25, 1.39, 1.57, 1.78, 1.98, 2.24, 2.49, 2.83, 3.14, 3.55]  # gem. ~12,2% per maand
BASE = 30500
BIG = ('Kredietbank Noord B.V.', 0.27)
OTHERS = [  # naam, gewicht
    ('Hypotheekhuis Zuid B.V.', 11), ('Ondernemersfinanciering Oost B.V.', 10), ('Leasepartner Holland B.V.', 9),
    ('Autofinance Direct B.V.', 8), ('Zakelijk Krediet Plus B.V.', 8), ('Bedrijfslening Online B.V.', 7),
    ('Factoring Collectief B.V.', 7), ('Groeikapitaal Partners B.V.', 6), ('Microkrediet Nederland', 6),
    ('Crowdfunding Platform MKB B.V.', 5), ('Financieringsadvies Van Dam V.O.F.', 5), ('Equipment Lease Benelux B.V.', 5),
    ('Werkkapitaal Direct B.V.', 4), ('Starterskrediet Stichting', 4), ('Vastgoedfinanciering West B.V.', 3),
]
inv = 2601
for m in range(12):
    revenue = BASE * growth[m] * rnd.uniform(0.97, 1.03)
    big = revenue * BIG[1]
    for part, day in zip((0.4, 0.35, 0.25), (8, 18, 28)):
        inv += 1
        add(m, day, MAIN, big * part, BIG[0], f'Provisie periode {inv}', 'income.other', rnd.uniform(0.9, 0.97))
    rest = revenue - big
    chosen = sorted(rnd.sample(range(len(OTHERS)), k=min(15, 11 + m // 3)))
    weights = [OTHERS[i][1] * rnd.uniform(0.7, 1.3) for i in chosen]
    for i, w in zip(chosen, weights):
        amount = rest * w / sum(weights)
        parts = 2 if amount > 6000 else 1
        for p in range(parts):
            inv += 1
            add(m, rnd.randint(2, 27), MAIN, amount / parts, OTHERS[i][0], f'Factuur 2026-{inv}', 'income.other',
                rnd.uniform(0.84, 0.97) if 'B.V.' in OTHERS[i][0] or 'V.O.F.' in OTHERS[i][0] else rnd.uniform(0.62, 0.8))

# ---------- Kosten: dalend ----------
decline = [0.955 ** m for m in range(12)]
SUPPLIERS = [('Leadpartner Nederland B.V.', 7800), ('Data Partners B.V.', 4200), ('Kredietinfo Services B.V.', 2600)]
for m in range(12):
    lab = LABELS[m]
    for name, base in SUPPLIERS:
        add(m, rnd.randint(4, 20), MAIN, -base * decline[m] * rnd.uniform(0.92, 1.08), name, f'Factuur {lab} {MONTHS[m][:4]}', 'expense.other', rnd.uniform(0.74, 0.9))
    for name, gross in (('M. de Vries', 4850), ('S. Bakker', 3120), ('R. Yilmaz', 2980), ('L. Jansen', 2760), ('T. Peters', 2540)):
        add(m, 25, MAIN, -gross, name, f'Salaris {lab}' if name != 'M. de Vries' else f'Salaris DGA {lab}', 'expense.salary', 0.94)
    add(m, 28, MAIN, -3920, BD, 'Betalingskenmerk loonheffingen', 'tax.payroll', 0.97, iban=BD_IBAN)
    add(m, 27, MAIN, -1240, 'Pensioenfonds Zakelijk', 'Premie pensioenregeling', 'expense.pension', 0.92)
    add(m, 1, MAIN, -3250, 'Kantorenpark Rotterdam B.V.', f'Huur kantoor {lab}', 'office.rent', 0.96)
    add(m, 12, MAIN, -520 * decline[m], 'Energiebedrijf Zakelijk B.V.', 'Termijn energie kantoor', 'expense.operations.utilities', 0.91)
    add(m, 20, MAIN, -214.5, 'Telecom Zakelijk B.V.', 'Zakelijk abonnement', 'expense.operations.telecom', 0.95)
    add(m, 3, MAIN, -320, 'Schoonmaakbedrijf Glans B.V.', 'Schoonmaak kantoor', 'expense.operations.other', 0.83)
    add(m, 1, MAIN, -38.9, 'ING', 'Kosten zakelijk betalen', 'expense.operations.bank_fees', 0.99, iban='NL·· INGB bank')
    add(m, 5, MAIN, -480 * decline[m], 'Cloud Hosting Nederland B.V.', 'Hosting en licenties', 'expense.it', 0.9)
    add(m, 9, MAIN, -1650 * decline[m], 'Online Advertenties B.V.', 'Campagne zoekmachine', 'expense.marketing', 0.86)
    add(m, 15, MAIN, -1200 * decline[m] * rnd.uniform(0.85, 1.15), 'Creditcard Services B.V.', 'Afschrijving zakelijke creditcard', 'loan.credit_card', 0.93)
    add(m, 30, MAIN, -2100, 'ING', 'Aflossing en rente zakelijke lening 66.21.904', 'loan.bank', 0.95, iban='NL·· INGB bank')
    add(m, 2, MAIN, -845.6, 'Autolease Zakelijk B.V.', f'Leasetermijn Tesla Model 3 {lab}', 'loan.vehicle_lease', 0.96)
    add(m, 3, MAIN, -265, 'IT Lease Nederland B.V.', 'Lease laptops contract 2291', 'loan.equipment_lease', 0.94)
    add(m, 1, MAIN, -186.4, 'Verzuimverzekeraar Nederland', 'Premie verzuimverzekering', 'insurance.other', 0.88)
    add(m, 24, MAIN, -1850, BD, f'Voorlopige aanslag vennootschapsbelasting {MONTHS[m][:4]}', 'tax.corporate', 0.96, iban=BD_IBAN)
    add(m, rnd.randint(4, 26), MAIN, -rnd.uniform(65, 95), 'Laadpunt Zakelijk B.V.', 'Laden bedrijfsauto', 'expense.transport.fuel', 0.9)
    # spaarrekening: vaste overboeking tussen eigen rekeningen
    add(m, 27, MAIN, -2500, HOLDER, 'Naar spaarrekening', 'internal.other', 1.0, iban=ACC[SAVE]['iban'])
    add(m, 27, SAVE, 2500, HOLDER, 'Van betaalrekening', 'internal.other', 1.0, iban=ACC[MAIN]['iban'])

for m in (0, 3, 6, 9):  # per kwartaal
    add(m, 15, MAIN, -1150, 'Accountantskantoor Verhoef', 'Factuur administratie kwartaal', 'expense.accounting', 0.89)
    add(m, 1, MAIN, -96.8 * 3, 'Zakelijk Verzekerd B.V.', 'Premie autoverzekering kwartaal', 'insurance.vehicle', 0.92)
    add(m, 1, MAIN, -390, 'VvE Kantorenpark Rotterdam', 'Servicekosten kwartaal', 'office.other', 0.84)
    add(m, 1, MAIN, -560, 'Hypotheekbank Zakelijk N.V.', 'Hypotheek archiefruimte kwartaal', 'office.mortgage', 0.9)
    add(m, 1, SAVE, -12.5, 'ING', 'Kosten spaarrekening', 'expense.operations.bank_fees', 0.98, iban='NL·· INGB bank')
    add(m + 2, 1, SAVE, round(25000 * 0.0045 * (1 + m / 10), 2), 'ING', 'Rente spaarrekening', 'income.interest', 0.95, iban='NL·· INGB bank')
    add(m + 1, 5, MAIN, 650, 'Studio Noord V.O.F.', 'Onderhuur werkplekken kwartaal', 'income.rent', 0.86)
    add(m + 1, 18, MAIN, -750, 'J. de Groot', 'Aflossing lening', 'loan.other', 0.66)
for m in range(0, 12, 2):
    add(m, 11, MAIN, -rnd.uniform(60, 140), 'Kantoorartikelen Direct B.V.', 'Bestelling kantoorartikelen', 'expense.operations.office_supplies', 0.88)
    add(m, 14, MAIN, -145, 'OV Zakelijk B.V.', 'Zakelijke reizen OV', 'expense.transport.public_transport', 0.9)

# btw per kwartaal, groeiend met de omzet; april deels, daarna regeling
add(2, 31, MAIN, -6840, BD, 'Omzetbelasting Q4 2025', 'tax.vat', 0.97, iban=BD_IBAN)
add(5, 30, MAIN, -4000, BD, 'Omzetbelasting Q1 2026 (deel)', 'tax.vat', 0.97, iban=BD_IBAN)
for m in (6, 7, 8, 9):
    add(m, 24, MAIN, -1550, BD, 'Betalingsregeling 2251 0937 1144', 'tax.vat', 0.79, ['payment_arrangement'], iban=BD_IBAN)
add(8, 31, MAIN, -14920, BD, 'Omzetbelasting Q2 2026', 'tax.vat', 0.97, iban=BD_IBAN)

# ---------- Eenmalige posten: elke categorie minstens 1 hit ----------
one = [
    (1, 12, MAIN, 18450, 'Factorfinance B.V.', 'Voorschot factuurfinanciering', 'income.factoring', 0.9, ()),
    (2, 4, MAIN, -18450 * 1.025, 'Factorfinance B.V.', 'Afrekening factuurfinanciering', 'income.factoring', 0.82, ()),
    (5, 20, MAIN, 7500, 'LS Deelneming B.V.', 'Dividend 2025', 'income.dividend', 0.9, ()),
    (3, 10, MAIN, 4800, 'Rijksdienst voor Ondernemend Nederland', 'WBSO-subsidie 2026', 'subsidy.other', 0.95, ()),
    (4, 16, MAIN, -1950, 'Opleidingsinstituut Financieel Advies', 'Wft-opleiding 2 medewerkers', 'expense.education', 0.88, ()),
    (8, 16, MAIN, -1950, 'Opleidingsinstituut Financieel Advies', 'PE-punten Wft', 'expense.education', 0.88, ()),
    (1, 19, MAIN, -342.5, 'Restaurant De Haven', 'Kerstlunch team', 'expense.representation', 0.85, ()),
    (7, 3, MAIN, -615, 'Evenementenbureau Maas B.V.', 'Relatie-event zomer', 'expense.representation', 0.8, ()),
    (6, 22, MAIN, -129, 'CJIB', 'Verkeersboete bedrijfsauto', 'expense.fines', 0.93, ()),
    (2, 17, MAIN, -2400, 'Advocatenkantoor Van Leeuwen', 'Juridisch advies contracten', 'expense.legal', 0.9, ()),
    (5, 8, MAIN, -850, 'Notariskantoor Smit', 'Statutenwijziging', 'expense.legal', 0.9, ()),
    (6, 30, MAIN, -25000, 'Lender Spender Holding B.V.', 'Dividenduitkering 2025', 'expense.dividend', 0.87, ()),
    (7, 15, MAIN, -3750, BD, 'Aangifte dividendbelasting 2026', 'tax.dividend', 0.95, (), BD_IBAN),
    (3, 6, MAIN, -682, 'Autobedrijf Jansen', 'Onderhoud en APK bestelbus', 'expense.transport.vehicle', 0.9, ()),
    (9, 6, MAIN, -415, 'Autobedrijf Jansen', 'Banden wisselen', 'expense.transport.vehicle', 0.88, ()),
    (1, 7, MAIN, -45, 'Parkeergarage Centrum', 'Parkeren', 'expense.transport.parking', 0.95, ()),
    (5, 21, MAIN, -38.5, 'Parkeergarage Centrum', 'Parkeren', 'expense.transport.parking', 0.95, ()),
    (8, 2, MAIN, -412, 'Vliegreizen Online B.V.', 'Vlucht congres Brussel', 'expense.transport.travel', 0.9, ()),
    (8, 3, MAIN, -298, 'Hotel Brussel Centrum', 'Overnachting congres', 'expense.transport.travel', 0.86, ()),
    (4, 9, MAIN, -64, 'Taxicentrale Rotterdam', 'Rit klantbezoek', 'expense.transport.other', 0.84, ()),
    (2, 13, MAIN, -112, 'Gemeente Rotterdam', 'Rioolheffing eigenaren', 'tax.other', 0.9, ()),
    (3, 28, MAIN, -486, 'Gemeente Rotterdam', 'Aanslag OZB en reclamebelasting', 'tax.other', 0.9, ()),
    (4, 28, MAIN, -96, 'Waterschap Hollandse Delta', 'Waterschapsbelasting', 'tax.other', 0.88, ()),
    (1, 26, MAIN, -153, BD, 'Motorrijtuigenbelasting bestelbus', 'tax.vehicle', 0.93, (), BD_IBAN),
    (7, 26, MAIN, -153, BD, 'Motorrijtuigenbelasting bestelbus', 'tax.vehicle', 0.93, (), BD_IBAN),
    (4, 30, MAIN, -1140, 'UWV', 'Correctie premie werknemersverzekeringen', 'tax.social', 0.84, ()),
    (0, 1, MAIN, -1840, 'Zakelijk Verzekerd B.V.', 'Jaarpremie bedrijfsaansprakelijkheid', 'insurance.liability', 0.91, ()),
    (2, 1, MAIN, -760, 'Zakelijk Verzekerd B.V.', 'Jaarpremie inventaris en bedrijfsschade', 'insurance.property', 0.9, ()),
    (2, 1, MAIN, -495, 'Rechtsbijstand Zakelijk N.V.', 'Jaarpremie rechtsbijstand', 'insurance.legal', 0.9, ()),
    (0, 14, MAIN, -300, 'Geldautomaat Rotterdam', 'Geldopname', 'cash.other', 0.98, (), 'NL·· geldautomaat'),
    (6, 9, MAIN, -150, 'Geldautomaat Rotterdam', 'Geldopname', 'cash.other', 0.98, (), 'NL·· geldautomaat'),
    (3, 14, MAIN, -45, 'Nederlandse Loterij', 'Loten personeelsfeest', 'gambling.lottery', 0.93, ()),
    (10, 19, MAIN, -250, 'Holland Casino', 'Betaalautomaat', 'gambling.other', 0.91, ()),
    (1, 22, MAIN, -15000, 'Depositobank Nederland N.V.', 'Inleg 12-maandsdeposito', 'investment.savings', 0.88, ()),
    (5, 3, MAIN, -38500, 'Notariskantoor Smit', 'Aankoop archiefruimte Kralingen', 'investment.real_estate', 0.71, ()),
    (8, 12, MAIN, -20000, 'Groeifonds Fintech B.V.', 'Storting aandelenkapitaal deelneming', 'investment.participations', 0.83, ()),
    (9, 23, MAIN, -2500, 'CryptoBroker NL B.V.', 'Aankoop BTC', 'investment.crypto', 0.95, ()),
    (4, 11, MAIN, -5000, 'Beleggingsfonds Duurzaam N.V.', 'Inleg beleggingsfonds', 'investment.other', 0.8, ()),
    (2, 6, MAIN, 7500, 'Snelkrediet Zakelijk B.V.', 'Uitbetaling flexkrediet', 'loan.flash', 0.86, ()),
    (3, 6, MAIN, -2690, 'Snelkrediet Zakelijk B.V.', 'Termijn flexkrediet', 'loan.flash', 0.86, ()),
    (4, 6, MAIN, -2690, 'Snelkrediet Zakelijk B.V.', 'Termijn flexkrediet', 'loan.flash', 0.86, ()),
    (5, 6, MAIN, -2690, 'Snelkrediet Zakelijk B.V.', 'Termijn flexkrediet', 'loan.flash', 0.86, ()),
    (6, 13, MAIN, -318.4, 'Achteraf Zakelijk B.V.', 'Termijn bestelling bureaustoelen', 'loan.bnpl', 0.89, ()),
    (7, 13, MAIN, -318.4, 'Achteraf Zakelijk B.V.', 'Termijn bestelling bureaustoelen', 'loan.bnpl', 0.89, ()),
    # signalen
    (9, 21, MAIN, -612.3, 'Gerechtsdeurwaarders Kok & Partners', 'Dossier 26-40817 Leadpartner', 'loan.debt_collection', 0.94, ()),
    (11, 9, MAIN, -284, 'Incassobureau Zuid B.V.', 'Vordering 55120', 'loan.debt_collection', 0.91, ()),
    (9, 6, MAIN, 845.6, 'Autolease Zakelijk B.V.', 'Terugboeking incasso: onvoldoende saldo', 'loan.vehicle_lease', 0.93, ('reversal_payment',)),
    (9, 17, MAIN, -845.6, 'Autolease Zakelijk B.V.', 'Leasetermijn Tesla Model 3 aug (herhaald)', 'loan.vehicle_lease', 0.95, ()),
    (11, 6, MAIN, 845.6, 'Autolease Zakelijk B.V.', 'Terugboeking incasso: onvoldoende saldo', 'loan.vehicle_lease', 0.93, ('reversal_payment',)),
    (10, 12, MAIN, -1880, 'Starterskrediet Stichting', 'Storno incasso klant', 'income.other', 0.78, ('reversal_payment',)),
    (6, 15, MAIN, 412.6, 'Data Partners B.V.', 'Creditnota 7781', 'expense.other', 0.84, ('refund',)),
    (8, 11, MAIN, 96, 'S. Bakker', 'Tikkie teamlunch', 'expense.representation', 0.67, ('payment_request',)),
    (7, 20, MAIN, 30000, 'Lender Spender Holding B.V.', 'Storting rekening-courant', 'other.other', 0.46, ()),
    (3, 18, MAIN, 1260, None, 'Overboeking', 'income.other', 0.41, ()),
    (5, 11, MAIN, -890, 'Online Marktplaats', 'Aankoop 4411', 'expense.other', 0.48, ()),
    (10, 4, MAIN, -2300, 'M. de Vries', 'Voorschot', 'other.other', 0.53, ()),
    (1, 29, MAIN, -480, 'Stichting Vrienden van het Erasmus', 'Bijdrage', 'other.other', 0.57, ()),
    (8, 25, MAIN, -1200, 'M. de Vries', 'Declaratie', 'other.other', 0.55, ()),
    (4, 22, MAIN, 25000, 'Lender Spender Holding B.V.', 'Rekening-courant', 'other.other', 0.51, ()),
    (10, 27, MAIN, -18500, 'M. de Vries', 'Rekening-courant DGA', 'other.other', 0.52, ()),
    (11, 14, MAIN, -9000, None, 'Overboeking 4471-K', 'other.other', 0.44, ()),
]
for row in one:
    add(*row[:8], flags=row[8], **({'iban': row[9]} if len(row) > 9 else {}))

# ---------- Volgorde, tijdstempels en saldo per rekening ----------
TX.sort(key=lambda t: (t['bookDate'], t['amount'] < 0, t['id']))
per_day = defaultdict(int)
for t in TX:
    per_day[t['bookDate']] += 1
    n = per_day[t['bookDate']]
    t['transactionDateTime'] = f"{t['bookDate']}T{7 + n // 6:02d}:{(n * 9) % 60:02d}:00Z"
for a in ACC:
    bal = a['start']
    for t in TX:
        if t['accountId'] == a['id']:
            bal = round(bal + t['amount'], 2)
            t['balanceAfterTransaction'] = bal
    a['end'] = bal

# ---------- Analyse (E1, corporate) ----------
def entry(name, rows):
    return {'name': name, 'transactionCount': len(rows), 'totalInflow': round(sum(r['amount'] for r in rows if r['amount'] > 0), 2),
            'totalOutflow': round(-sum(r['amount'] for r in rows if r['amount'] < 0), 2),
            'categories': sorted({r['category']['e1']['category'] for r in rows}), 'transactionIds': [r['id'] for r in rows]}
cat = lambda r: r['category']['e1']['category']
fl = lambda r: r['category']['e1']['flags']
cf = lambda r: r['category']['e1']['confidence']
LEASES = {'loan.debt_collection', 'loan.vehicle_lease', 'loan.equipment_lease'}
sections = {
    'clientProfile': [
        entry('Taxes', [r for r in TX if cat(r).startswith('tax.')]),
        entry('Loans', [r for r in TX if cat(r).startswith('loan.') and cat(r) not in LEASES]),
        entry('Debt collection', [r for r in TX if cat(r) == 'loan.debt_collection']),
        entry('Vehicle Lease', [r for r in TX if cat(r) == 'loan.vehicle_lease']),
        entry('Equipment Lease', [r for r in TX if cat(r) == 'loan.equipment_lease']),
        entry('Internal transactions', [r for r in TX if cat(r) == 'internal.other']),
        entry('Gambling', [r for r in TX if cat(r).startswith('gambling.')]),
        entry('Crypto', [r for r in TX if cat(r) == 'investment.crypto']),
    ],
    'flaggedTransactions': [
        entry('Reversal payments', [r for r in TX if 'reversal_payment' in fl(r)]),
        entry('Refunds', [r for r in TX if 'refund' in fl(r)]),
        entry('Payment arrangements', [r for r in TX if 'payment_arrangement' in fl(r)]),
    ],
    'lowConfidenceTransactions': [
        entry('Confidence <50%', [r for r in TX if cf(r) < 0.5]),
        entry('50% <= Confidence <60%', [r for r in TX if 0.5 <= cf(r) < 0.6]),
    ],
    'otherHighlightedTransactions': [
        entry('Round number', [r for r in TX if abs(r['amount']) >= 10000 and float(r['amount']).is_integer() and abs(r['amount']) % 10000 == 0]),
    ],
}
def top(side):
    groups = defaultdict(list)
    for r in TX:
        if (r['amount'] > 0) == (side == 'inflow'):
            groups[r['counterpartDescription'] or 'Unknown'].append(r)
    ranked = sorted(groups.items(), key=lambda kv: -abs(sum(r['amount'] for r in kv[1])))[:5]
    return {str(i): entry(name, rows) for i, (name, rows) in enumerate(ranked)}
start_bal = round(sum(a['start'] for a in ACC), 2)
analysis = {
    'generalInfo': {'startDate': '2025-11-01', 'endDate': '2026-10-31', 'startBalance': start_bal, 'endBalance': round(sum(a['end'] for a in ACC), 2),
                    'accounts': [{'iban': a['iban'], 'accountName': HOLDER, 'accountId': a['id']} for a in ACC],
                    'totalInflow': round(sum(r['amount'] for r in TX if r['amount'] > 0), 2), 'totalOutflow': round(-sum(r['amount'] for r in TX if r['amount'] < 0), 2)},
    'companyInfo': {'kvkNumber': '69012345', 'name': HOLDER, 'address': 'Weena 505, Rotterdam', 'industryCode': '66190',
                    'industryDescription': 'Overige ondersteunende activiteiten voor financiële dienstverlening', 'legalForm': 'Besloten Vennootschap',
                    'numberOfEmployees': 6, 'startDate': '2018-04-01T00:00:00', 'registrationDate': '2018-04-09T00:00:00'},
    'topCounterparties': {'inflow': top('inflow'), 'outflow': top('outflow')},
    **sections, 'creditQualityMetrics': [],
}

# ---------- Bestanden zoals de API ze levert ----------
dump = lambda name, obj: json.dump(obj, open(os.path.join(OUT, name), 'w'), indent=2, ensure_ascii=False)
dump('01-token.json', {'request': {'method': 'POST', 'path': '/connect/token', 'contentType': 'application/x-www-form-urlencoded', 'body': {'client_id': '<client_id>', 'client_secret': '<client_secret>', 'scope': 'customer-api', 'grant_type': 'client_credentials'}}, 'response_200': {'accessToken': '<jwt>', 'expiresIn': 3600, 'tokenType': 'Bearer'}, 'note': 'Responsvelden en geldigheid zijn een aanname.'})
dump('02-get-accounts.json', {'request': {'method': 'GET', 'path': '/Accounts', 'query': {'ConsentId': CONSENT}}, 'response_200': {'data': [{'id': a['id'], 'iban': a['iban'], 'providerAccountId': 'ingb-' + a['id'][:8], 'accountHolder': HOLDER, 'bban': None, 'currency': 'EUR', 'accountBalance': {'currency': 'EUR', 'date': '2026-10-31T23:59:59Z', 'amount': a['end']}} for a in ACC]}})
job = uid()
meta = {'internal_ibans': [a['iban'] for a in ACC]}
dump('03-categorization-job.json', {'request': {'method': 'POST', 'path': '/v2/categorization-jobs', 'body': {'engine': 'e1', 'profile': 'corporate', 'countryCode': 'nl', 'consentId': CONSENT, 'accountIds': [a['id'] for a in ACC], 'metaData': meta}}, 'response_202': {'data': job}, 'poll': {'method': 'GET', 'path': f'/v2/categorization-jobs/{job}', 'response_200': {'data': {'id': job, 'status': 'COMPLETED', 'engine': 'e1', 'profile': 'corporate', 'countryCode': 'nl', 'consentId': CONSENT, 'userId': None, 'externalUserId': None, 'accountIds': [a['id'] for a in ACC], 'parentId': None, 'engineVersion': 'e1-2026.10', 'metaData': meta}}}, 'note': 'Status COMPLETED is een aanname.'})
desc = sorted(TX, key=lambda t: (t['bookDate'], t['transactionDateTime'], t['id']), reverse=True)
pages = math.ceil(len(desc) / 100)
for i in range(pages):
    dump(f'04-get-transactions-page-{i + 1}.json', {'request': {'method': 'GET', 'path': '/Transactions', 'query': {'ConsentId': CONSENT, 'DateFrom': '2025-11-01T00:00:00Z', 'DateTo': '2026-10-31T23:59:59Z', 'OrderBy': 'bookDate', 'OrderDirection': 'desc', 'PageSize': 100, 'PageToken': None if i == 0 else f'pg{i + 1}'}}, 'response_200': {'data': desc[i * 100:(i + 1) * 100], 'nextPageToken': None if i == pages - 1 else f'pg{i + 2}'}})
aj = uid()
dump('05-analysis-job.json', {'request': {'method': 'POST', 'path': '/analysis-jobs', 'body': {'reference': 'Dossier LS-2026-1103', 'engine': 'e1', 'profile': 'corporate', 'countryCode': 'nl', 'input': {'consentIds': [CONSENT]}, 'metaData': {'kvk_number': '69012345', **meta}, 'dateFrom': '2025-11-01T00:00:00Z', 'dateTo': '2026-10-31T23:59:59Z'}}, 'poll': {'method': 'GET', 'path': f'/analysis-jobs/{aj}'}, 'response_200': {'id': aj, 'status': 'COMPLETED', 'engine': 'e1', 'profile': 'corporate', 'analysis': analysis}})

# ---------- Samenvatting voor controle ----------
rev = [round(sum(r['amount'] for r in TX if cat(r) == 'income.other' and r['amount'] > 0 and r['bookDate'].startswith(k))) for k in MONTHS]
costs = [round(-sum(r['amount'] for r in TX if r['amount'] < 0 and cat(r).split('.')[0] in ('expense', 'office', 'insurance') and r['bookDate'].startswith(k))) for k in MONTHS]
cust = defaultdict(float)
for r in TX:
    if cat(r) == 'income.other' and r['amount'] > 0:
        cust[r['counterpartDescription'] or 'Unknown'] += r['amount']
tot = sum(cust.values())
print('transacties', len(TX), 'paginas', pages)
print('omzet/mnd', rev, 'groei gem', round(((rev[-1] / rev[0]) ** (1 / 11) - 1) * 100, 1), '%')
print('kosten/mnd', costs)
print('afnemers', len([c for c in cust if c != 'Unknown']), 'grootste', max(cust, key=cust.get), round(max(cust.values()) / tot * 100, 1), '%')
print('top5', [(k, round(v / tot * 100, 1)) for k, v in sorted(cust.items(), key=lambda kv: -kv[1])[:5]])
print('categorieen', len({cat(r) for r in TX}))
print('buckets', [(e['name'], e['transactionCount']) for s in sections.values() for e in s])
print('eindsaldo', [a['end'] for a in ACC])
