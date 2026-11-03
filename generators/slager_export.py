import json, sys, math
from playwright.sync_api import sync_playwright
path, out = sys.argv[1], sys.argv[2]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.goto('file://' + path); pg.wait_for_timeout(500)
    d = pg.evaluate('''() => {
      includeInternal = true;
      const sections = {};
      Object.entries(BUCKETS).forEach(([s, list]) => { sections[s] = list.map(e => profileEntry(e.name, TX.filter(e.test))); });
      const top = side => { const r = topCounterparties(side).top; return Object.fromEntries(r.map((e, i) => [String(i), { name: e.name, transactionCount: e.transactionCount, totalInflow: +e.totalInflow.toFixed(2), totalOutflow: +e.totalOutflow.toFixed(2), categories: e.categories, transactionIds: e.transactionIds }])); };
      return { TX, ACCOUNTS, GENERAL_INFO, COMPANY_INFO, sections, inflow: top('inflow'), outflow: top('outflow') };
    }''')
    b.close()
r2 = lambda x: round(x, 2)
for s in d['sections'].values():
    for e in s: e['totalInflow'] = r2(e['totalInflow']); e['totalOutflow'] = r2(e['totalOutflow'])
consent = 'c0a8f3d2-6b1e-4f57-9a3c-2e7d5b9f1a60'
accts = []
for a in d['ACCOUNTS']:
    end = a['startBalance'] + sum(t['amount'] for t in d['TX'] if t['accountNumber'] == a['iban'])
    accts.append({'id': a['accountId'], 'iban': a['iban'], 'providerAccountId': 'rabo-' + a['accountId'][:8], 'accountHolder': a['accountName'], 'bban': None, 'currency': 'EUR', 'accountBalance': {'currency': 'EUR', 'date': '2025-10-31T23:59:59Z', 'amount': r2(end)}})
json.dump({'data': accts}, open(f'{out}/02-get-accounts.json', 'w'), indent=2, ensure_ascii=False)
json.dump({'request': {'method': 'POST', 'path': '/v2/categorization-jobs', 'body': {'engine': 'e1', 'profile': 'corporate', 'countryCode': 'nl', 'consentId': consent, 'accountIds': [a['id'] for a in accts], 'metaData': {'internal_ibans': [a['iban'] for a in accts]}}},
           'response_202': {'data': '5d2e9b40-1c7a-4e83-b6f2-0a9d4c3e7f15'},
           'poll': {'method': 'GET', 'path': '/v2/categorization-jobs/5d2e9b40-1c7a-4e83-b6f2-0a9d4c3e7f15', 'response_200': {'data': {'id': '5d2e9b40-1c7a-4e83-b6f2-0a9d4c3e7f15', 'status': 'COMPLETED', 'engine': 'e1', 'profile': 'corporate', 'countryCode': 'nl', 'consentId': consent, 'userId': None, 'externalUserId': None, 'accountIds': [a['id'] for a in accts], 'parentId': None, 'engineVersion': 'e1-2026.10', 'metaData': {'internal_ibans': [a['iban'] for a in accts]}}}},
           'note': 'Statuswaarde COMPLETED is een aanname; de documentatie toont alleen PENDING.'}, open(f'{out}/03-categorization-job.json', 'w'), indent=2, ensure_ascii=False)
tx = sorted(d['TX'], key=lambda t: (t['bookDate'], t['id']), reverse=True)
pages = math.ceil(len(tx) / 100)
for i in range(pages):
    nxt = None if i == pages - 1 else f'eyJwYWdlIjo{i+2}fQ'
    json.dump({'request': {'method': 'GET', 'path': '/Transactions', 'query': {'ConsentId': consent, 'DateFrom': '2024-11-01T00:00:00Z', 'DateTo': '2025-10-31T23:59:59Z', 'OrderBy': 'bookDate', 'OrderDirection': 'desc', 'PageSize': 100, 'PageToken': None if i == 0 else f'eyJwYWdlIjo{i+1}fQ'}},
               'response_200': {'data': tx[i*100:(i+1)*100], 'nextPageToken': nxt}}, open(f'{out}/04-get-transactions-page-{i+1}.json', 'w'), indent=2, ensure_ascii=False)
gi = d['GENERAL_INFO']
analysis = {'generalInfo': {'startDate': gi['startDate'], 'endDate': gi['endDate'], 'startBalance': r2(gi['startBalance']), 'endBalance': r2(gi['endBalance']), 'accounts': [{'iban': a['iban'], 'accountName': a['accountHolder'], 'accountId': a['id']} for a in accts], 'totalInflow': r2(gi['totalInflow']), 'totalOutflow': r2(gi['totalOutflow'])},
            'companyInfo': d['COMPANY_INFO'], 'topCounterparties': {'inflow': d['inflow'], 'outflow': d['outflow']}, **d['sections'], 'creditQualityMetrics': []}
json.dump({'request': {'method': 'POST', 'path': '/analysis-jobs', 'body': {'reference': 'Dossier 2025-0412 Slager', 'engine': 'e1', 'profile': 'corporate', 'countryCode': 'nl', 'input': {'consentIds': [consent]}, 'metaData': {'kvk_number': '71234567', 'internal_ibans': [a['iban'] for a in accts]}, 'dateFrom': '2024-11-01T00:00:00Z', 'dateTo': '2025-10-31T23:59:59Z'}},
           'poll': {'method': 'GET', 'path': '/analysis-jobs/9a41c7e2-3f0b-4d6a-8e25-c1b7f4d93a08'},
           'response_200': {'id': '9a41c7e2-3f0b-4d6a-8e25-c1b7f4d93a08', 'status': 'COMPLETED', 'engine': 'e1', 'profile': 'corporate', 'analysis': analysis}}, open(f'{out}/05-analysis-job.json', 'w'), indent=2, ensure_ascii=False)
json.dump({'request': {'method': 'POST', 'path': '/connect/token', 'contentType': 'application/x-www-form-urlencoded', 'body': {'client_id': '<client_id>', 'client_secret': '<client_secret>', 'scope': 'customer-api', 'grant_type': 'client_credentials'}}, 'response_200': {'accessToken': '<jwt>', 'expiresIn': 3600, 'tokenType': 'Bearer'}, 'note': 'Responsvelden en geldigheid zijn een aanname; de documentatie toont expiresIn 0.'}, open(f'{out}/01-token.json', 'w'), indent=2, ensure_ascii=False)
print(len(tx), pages, json.dumps(analysis['generalInfo'])[:300])
print([ (e['name'], e['transactionCount']) for s in d['sections'].values() for e in s])
