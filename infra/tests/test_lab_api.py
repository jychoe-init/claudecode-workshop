"""API 계약·데이터·시간·페이지 검증: python3 infra/tests/test_lab_api.py"""
import datetime as dt
import importlib.util
import json
import os
import re
import subprocess
import sys
import types
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch
from urllib.parse import quote, urlencode

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'infra/lambda'))
import lab_api as api
import lab_company as c

T1, T2 = 'lab-a1b2c3d4', 'lab-zz99yy88'
NOW = dt.datetime(2026, 10, 6, 10, tzinfo=c.KST)


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.store = api.MemoryStore(tokens={T1, T2})

    def call(self, path, body=None, now=NOW, token=T1, method=None, **headers):
        return api.handle(method or ('POST' if body is not None else 'GET'), path,
                          {'Authorization': 'Bearer ' + token, **headers},
                          json.dumps(body) if body is not None else None, self.store, now)

    def get(self, path, **kw):
        status, data = self.call(path, **kw)
        self.assertEqual(status, 200, data)
        return data

    def post(self, **kw):
        body = {'employee': '김민준', 'date': '2026-10-13', 'days': 1, **kw}
        return self.call('/v1/leave/requests', body)

    def test_auth_methods_rate(self):
        self.assertEqual(api.handle('GET', '/v1/me', {}, None, self.store, NOW)[0], 401)
        self.assertEqual(self.call('/v1/me', token='lab-SHORT')[0], 401)
        self.assertEqual(self.call('/v1/me', token='lab-00000000')[0], 403)
        self.assertEqual(self.call('/docs')[0], 404)
        self.assertEqual(self.call('/v1/me', method='DELETE')[0], 405)
        for path in ('/v1/notify', '/v1/slack/link'):
            self.assertEqual(self.call(path, {}, method='POST')[0], 404)
        key = NOW.strftime('%Y%m%d%H%M')
        self.store.rate[T1 + '#' + key] = api.RATE_LIMIT_PER_MIN - 1
        self.assertEqual(self.call('/v1/company')[0], 200)
        self.assertEqual(self.call('/v1/company')[0], 429)
        self.assertEqual(self.call('/v1/company', now=NOW + dt.timedelta(minutes=1))[0], 200)

    def test_company_determinism_identity(self):
        first = self.get('/v1/me')
        self.assertEqual(first, self.get('/v1/me', token=T2))
        self.assertEqual(first['team'], 'growth')
        self.assertEqual(first['token_hint'], 'lab-…')
        self.assertEqual(first['me']['name'], '김민준')
        self.assertEqual(first['me']['position'], '팀장')
        self.assertEqual(len(first['members']), 8)
        es = self.get('/v1/employees?limit=all')['employees']
        self.assertEqual(len(es), 120)
        self.assertEqual(len({e['id'] for e in es}), 120)
        self.assertEqual(len({e['email'] for e in es}), 120)
        required = set('id name name_en email extension division division_name team team_name title position role role_label employment_type joined_on contract_end last_day manager_id manager office home_area work_type status leave_balance'.split())
        for e in es:
            self.assertTrue(required <= e.keys())
            self.assertRegex(e['id'], r'^SL\d{5}$')
            self.assertEqual(e['id'][2:4], e['joined_on'][2:4])
            self.assertTrue(e['email'].endswith('@superlab.example'))
            self.assertEqual(set(e['office']), {'code', 'name', 'address', 'zip'})
        code = "import sys,json,hashlib;sys.path.insert(0,'infra/lambda');import lab_company as c;print(hashlib.sha256(json.dumps(c.company_employees(),ensure_ascii=False,sort_keys=True).encode()).hexdigest())"
        outputs = [subprocess.check_output([sys.executable, '-B', '-c', code], cwd=ROOT,
                   env={**os.environ, 'PYTHONHASHSEED': seed}) for seed in ('1', '1729')]
        self.assertEqual(*outputs)

    def test_org_and_special_employees(self):
        org = self.get('/v1/org')
        self.assertEqual(sum(d['headcount'] for d in org['divisions']), 120)
        teams = {t['code']: t for d in org['divisions'] for t in d['teams']}
        self.assertTrue(teams['legal']['leader_vacant'])
        self.assertIsNone(teams['legal']['leader'])
        for code, _, _, count in c.TEAMS:
            self.assertEqual(teams[code]['headcount'], count)
        es = self.get('/v1/employees?limit=all')['employees']
        self.assertEqual(sum(e['position'] == '부문장' and e['team'] is None for e in es), 3)
        self.assertEqual(sum(e['name'] == '김지훈' for e in es), 2)
        self.assertTrue(any(e['name'] == '알렉산드라 페트로바' for e in es))
        self.assertTrue(any(e['name'] == '남궁하늘' and e['employment_type'] == 'intern' for e in es))
        self.assertTrue(any(e['team'] == 'hr' and e['employment_type'] == 'contract' for e in es))
        self.assertTrue(any(e['team'] == 'data' and e['status'] == 'on_leave' for e in es))
        self.assertTrue(any(e['team'] == 'cs' and e['status'] == 'leaving' for e in es))
        self.assertTrue(any(e['team'] == 'sales2' and e['office']['code'] == 'busan' for e in es))

    def test_lookup_and_filters(self):
        e = self.get('/v1/me')['me']
        for key in (e['id'], e['name'], e['name_en'], e['email'], e['email'].split('@')[0]):
            self.assertEqual(self.get('/v1/employees/' + quote(key, safe=''))['id'], e['id'])
            self.assertEqual(self.get('/v1/leave/' + quote(key, safe=''))['employee_id'], e['id'])
        status, ambiguous = self.call('/v1/employees/' + quote('김지훈'))
        self.assertEqual(status, 409)
        self.assertEqual(ambiguous['error'], 'ambiguous_employee')
        self.assertEqual(len(ambiguous['candidates']), 2)
        self.assertEqual(self.call('/v1/employees/nobody')[0], 404)
        self.assertEqual(self.get('/v1/employees?team=' + quote('그로스팀'))['total'], 8)
        self.assertEqual(self.get('/v1/employees?division=product&limit=all')['total'], 47)
        for query, field, expected in [('status=on_leave', 'status', 'on_leave'), ('role=frontend', 'role', 'frontend')]:
            self.assertTrue(all(e[field] == expected for e in self.get('/v1/employees?' + query)['employees']))
        self.assertEqual(self.get('/v1/employees?q=' + quote('김지훈'))['total'], 2)
        self.assertEqual(self.get('/v1/employees?q=no-such-employee')['employees'], [])
        for query in ('team=nope', 'division=nope', 'status=nope', 'role=nope'):
            self.assertEqual(self.call('/v1/employees?' + query)[0], 400)

    def test_pagination_all_collections(self):
        cases = [('/v1/me', 'members'), ('/v1/org', 'divisions'), ('/v1/employees', 'employees'),
                 ('/v1/holidays', 'holidays'), ('/v1/leave?team=all', 'balances'),
                 ('/v1/leave/history', 'history'), ('/v1/leave/calendar?month=2026-10', 'days'),
                 ('/v1/leave/stats', 'by_team'), ('/v1/deploys', 'deploys'),
                 ('/v1/mail/planning/sent', 'value'), ('/v1/calendar/sales', 'value')]
        for path, key in cases:
            with self.subTest(path=path):
                sep = '&' if '?' in path else '?'
                full = self.get(path + sep + 'limit=all')
                default = self.get(path)
                self.assertEqual(default['limit'], 100 if key == 'history' else 20)
                self.assertEqual(default[key], full[key][:default['limit']])
                page = self.get(path + sep + 'limit=2&offset=1')
                self.assertEqual(page[key], full[key][1:3])
                self.assertEqual(page['total'], len(full[key]))
                self.assertEqual(page['next_offset'], 3 if full['total'] > 3 else None)
                self.assertEqual(self.get(path + sep + 'limit=all&offset=2')[key], full[key][2:])
                empty = self.get(path + sep + 'offset=100000')
                self.assertEqual(empty[key], [])
                self.assertIsNone(empty['next_offset'])
                cap = 1000 if key == 'history' else 100
                self.assertEqual(self.get(path + sep + f'limit={cap}')['limit'], cap)
                for query in ('limit=0', 'limit=-1', 'limit=x', 'limit=1.5', 'limit=', 'limit=ALL',
                              f'limit={cap+1}', 'offset=-1', 'offset=x'):
                    self.assertEqual(self.call(path + sep + query)[0], 400, (path, query))
        all_ids = self.get('/v1/employees?limit=all')['employees']
        paged = []
        offset = 0
        while offset is not None:
            data = self.get(f'/v1/employees?limit=17&offset={offset}')
            paged.extend(data['employees'])
            offset = data['next_offset']
        self.assertEqual(paged, all_ids)
        self.assertEqual(self.get('/v1/employees?team=growth&limit=all')['total'], 8)

    def test_balances_and_history_sums(self):
        for year in c.YEARS:
            now = NOW if year == 2026 else dt.datetime(2025, 12, 31, 23, 59, tzinfo=c.KST)
            for e in c.company_employees():
                with self.subTest(year=year, employee=e['id']):
                    b = c.balance(e, now, year)
                    self.assertEqual(b['total'], b['annual'] + b['carried_over'])
                    self.assertEqual(b['remaining'], b['total'] - b['used'] - b['scheduled'] - b['pending'])
                    self.assertGreaterEqual(b['remaining'], 0)
                    self.assertEqual(b['expiring'], max(0, b['remaining'] - 3))
                    used = sum(amount for raw in c.employee_records(e['id'], year)
                               for v in [c.record_view(raw, now)] if v and v['status'] == 'approved' and v['deducted']
                               for day, amount in c.units(v) if day.year == year and day <= c.today_at(now))
                    self.assertEqual(b['used'], used)
                    if year == 2026:
                        last = c.balance(e, dt.datetime(2025, 12, 31, 23, 59, tzinfo=c.KST), 2025)
                        self.assertEqual(b['carried_over'], min(3, last['remaining']))
        data = self.get('/v1/leave/history?team=growth&limit=all')
        self.assertTrue(data['history'])
        self.assertTrue(all(r['team'] == 'growth' for r in data['history']))
        for query, key, expected in [('type=half_pm', 'type', 'half_pm'), ('status=rejected', 'status', 'rejected')]:
            filtered = self.get('/v1/leave/history?' + query)['history']
            self.assertTrue(filtered)
            self.assertTrue(all(r[key] == expected for r in filtered))
        filtered = self.get('/v1/leave/history?' + urlencode({'employee': '김민준', 'from': '2026-03-01', 'to': '2026-10-01'}))['history']
        self.assertTrue(all(r['employee'] == '김민준' and r['start'] <= '2026-10-01' and r['end'] >= '2026-03-01' for r in filtered))
        for query in ('year=2024', 'year=2027', 'from=2026-11-01&to=2026-01-01', 'from=bad', 'type=bad', 'status=bad'):
            self.assertEqual(self.call('/v1/leave/history?' + query)[0], 400)

    def test_event_boundaries_never_overbooked(self):
        for e in c.company_employees():
            for year in c.YEARS:
                for raw in c.employee_records(e['id'], year):
                    self.assertGreaterEqual(raw['start'], e['joined_on'])
                    self.assertEqual(sum(a for _, a in c.units(raw)), raw['days'])
                    for day, _ in c.units(raw):
                        self.assertLess(day.weekday(), 5)
                        self.assertNotIn(day.strftime('%m-%d'), c.HOLIDAY_DATA.get(day.year, {}))
                    for field in ('requested_at', 'decided_at', 'cancelled_at'):
                        if not raw[field]:
                            continue
                        instant = dt.datetime.fromisoformat(raw[field])
                        for at in (instant - dt.timedelta(seconds=1), instant):
                            self.assertGreaterEqual(c.balance(e, at)['remaining'], 0, (e['id'], field, at))
                    requested = dt.datetime.fromisoformat(raw['requested_at'])
                    self.assertIsNone(c.record_view(raw, requested - dt.timedelta(seconds=1)))
                    self.assertEqual(c.record_view(raw, requested)['status'], 'pending')

    def test_annual_calendar_scenarios(self):
        e = {'joined_on': '2026-08-03'}
        self.assertEqual(c.annual_at(e, dt.date(2026, 9, 2)), (0, 'monthly'))
        self.assertEqual(c.annual_at(e, dt.date(2026, 9, 3)), (1, 'monthly'))
        self.assertEqual(c.annual_at(e, dt.date(2027, 8, 3)), (15, 'yearly'))
        self.assertEqual(c.annual_at({'joined_on': '2023-10-06'}, dt.date(2026, 10, 6)), (16, 'yearly'))
        self.assertEqual(c.annual_at({'joined_on': '1990-01-01'}, dt.date(2026, 10, 6))[0], 25)
        self.assertFalse(c.business_day('2026-07-17'))
        self.assertFalse(c.business_day('2026-05-01'))
        self.assertTrue(c.business_day('2026-09-28'))
        self.assertTrue(c.business_day('2026-06-08'))
        self.assertEqual(c.end_for('2026-10-02', 4), '2026-10-08')
        bs = {b['employee']: b for b in self.get('/v1/leave')['balances']}
        self.assertEqual(bs['이지은']['remaining'], 0)
        self.assertEqual(bs['최수빈']['pending'], 3)
        self.assertGreaterEqual(bs['강도윤']['expiring'], 5)
        self.assertEqual(bs['윤서아']['accrual'], 'monthly')
        self.assertEqual(bs['윤서아']['used'], .5)
        self.assertTrue(any(h['start'] == '2026-10-14' and h['status'] == 'rejected' for h in bs['정하린']['history']))
        approved = self.get('/v1/leave/' + quote('최수빈'), now=dt.datetime(2026, 10, 23, 15, tzinfo=c.KST))
        self.assertTrue(any(h['start'] == '2026-10-26' and h['status'] == 'approved' for h in approved['history']))
        cal = self.get('/v1/leave/calendar?month=2026-05&team=platform&limit=all')
        may4 = next(d for d in cal['days'] if d['date'] == '2026-05-04')
        self.assertGreaterEqual(len(may4['absentees']), 6)
        self.assertTrue(any(a['date'] == '2026-05-04' for a in cal['alerts']))
        page = self.get('/v1/leave/calendar?month=2026-05&limit=2')
        self.assertTrue(all(a['date'] in {d['date'] for d in page['days']} for a in page['alerts']))
        octcal = self.get('/v1/leave/calendar?month=2026-10&team=growth&limit=all')
        for day in ('2026-10-06', '2026-10-07', '2026-10-08'):
            self.assertTrue(any(a['employee'] == '박서준' for d in octcal['days'] if d['date'] == day for a in d['absentees']))
        self.assertEqual(self.call('/v1/leave/calendar?month=2026-13')[0], 400)

    def test_stats_consistency(self):
        data = self.get('/v1/leave/stats?team=growth')
        self.assertEqual(data['summary']['used'], sum(m['used'] for m in data['by_month']))
        self.assertEqual(data['summary']['used'], sum(t['used'] for t in data['by_type'] if t['deducted']))
        self.assertEqual(data['summary']['headcount'], 8)
        all_stats = self.get('/v1/leave/stats?limit=all')
        self.assertEqual(all_stats['summary'], all_stats['company_average'])
        self.assertEqual(all_stats['summary']['used'], sum(t['used'] for t in all_stats['by_team']))
        self.assertEqual(self.get('/v1/leave/stats?limit=1')['summary'], all_stats['summary'])

    def test_post_validation_warnings_and_balance(self):
        before = self.get('/v1/leave/' + quote('김민준'))
        for days, kind in [(1, 'annual'), (.5, 'half_pm'), (.25, 'quarter'), (.5, 'annual')]:
            status, request = self.post(days=days, type=kind)
            self.assertEqual(status, 201, request)
            self.assertEqual(request['status'], 'pending')
            self.assertRegex(request['request_id'], r'^REQ-[A-Z0-9]{6}$')
            self.assertEqual(request['team'], 'growth')
            self.assertTrue(request['approver'])
        self.assertEqual(self.get('/v1/leave/' + quote('김민준')), before)
        self.assertEqual(self.post(days=before['remaining'])[0], 201)
        for body in ({'days': before['remaining'] + 1}, {'employee': '이지은'}):
            status, error = self.post(**body)
            self.assertEqual((status, error['error']), (409, 'insufficient_balance'))
        self.assertEqual(self.post(employee='nobody')[0], 404)
        resigned = self.get('/v1/employees?status=resigned')['employees'][0]
        self.assertEqual(self.post(employee=resigned['id'])[1]['error'], 'employee_resigned')
        for changes in ({'date': '10/30'}, {'date': '2026-02-30'}, {'date': '2027-01-01'},
                        {'days': 0}, {'days': -1}, {'days': True}, {'days': .3}, {'days': float('nan')},
                        {'days': float('inf')}, {'days': '1'}, {'days': 367}, {'employee': None},
                        {'type': 'unknown'}, {'type': []}, {'type': 'half_am', 'days': 1},
                        {'type': 'quarter', 'days': .5}, {'type': 'sick', 'days': .5},
                        {'reason': 'a' * 101}, {'requested_by': 'a' * 31}):
            self.assertEqual(self.post(**changes)[0], 400, changes)
        for raw in ('{', '[]', 'null'):
            self.assertEqual(api.handle('POST', '/v1/leave/requests', {'Authorization': 'Bearer ' + T1}, raw, self.store, NOW)[0], 400)
        self.assertEqual(self.post(type='parental', days=366, date='2026-12-31')[0], 400)
        for date, expected in [('2026-10-03', {'weekend', 'holiday', 'past_date'}), ('2026-10-13', {'overlap'})]:
            status, result = self.post(date=date)
            self.assertEqual(status, 201)
            self.assertTrue(expected <= {w['code'] for w in result['warnings']})

    def test_requests_filters_paging_approval(self):
        for i in range(25):
            self.post(requested_by='participant-a' if i % 2 else 'participant-b', days=.5, type='half_pm')
        first = self.get('/v1/leave/requests')
        self.assertEqual(len(first['requests']), 20)
        self.assertEqual(first['total'], 25)
        self.assertEqual(first['next_offset'], 20)
        self.assertEqual(len(self.get('/v1/leave/requests?offset=20')['requests']), 5)
        self.assertEqual(len(self.get('/v1/leave/requests?limit=all')['requests']), 25)
        self.assertEqual(self.get('/v1/leave/requests', token=T2)['requests'], [])
        filtered = self.get('/v1/leave/requests?requested_by=participant-a&team=growth&status=pending&limit=all')
        self.assertEqual(filtered['total'], 12)
        self.assertTrue(all(r['requested_by'] == 'participant-a' for r in filtered['requests']))
        self.assertEqual(self.get('/v1/leave/requests?status=approved')['total'], 0)
        self.assertEqual(self.get('/v1/leave/requests?status=approved', now=NOW + dt.timedelta(minutes=2))['total'], 25)
        self.assertEqual(self.get('/v1/leave/requests', now=NOW - dt.timedelta(seconds=1))['total'], 0)
        status, long = self.post(days=3, requested_by='long')
        self.assertEqual(status, 201)
        self.assertEqual(self.get('/v1/leave/requests?requested_by=long', now=NOW + dt.timedelta(minutes=9))['requests'][0]['status'], 'pending')
        self.assertEqual(self.get('/v1/leave/requests?requested_by=long', now=NOW + dt.timedelta(minutes=10))['requests'][0]['status'], 'approved')
        status, header = self.call('/v1/leave/requests', {'employee': '김민준', 'date': '2026-10-13', 'days': 1}, **{'X-Lab-User': 'header-user'})
        self.assertEqual(header['requested_by'], 'header-user')
        ids = {r['request_id'] for r in self.get('/v1/leave/requests?limit=all')['requests']}
        self.assertEqual(len(ids), 27)
        for query in ('limit=101', 'limit=0', 'offset=-1', 'status=rejected'):
            self.assertEqual(self.call('/v1/leave/requests?' + query)[0], 400)
        self.store.requests[T1] = [{**header, 'request_id': f'REQ-{i:06}', 'requested_at': (NOW - dt.timedelta(seconds=600-i)).isoformat()} for i in range(501)]
        self.assertEqual(self.get('/v1/leave/requests?limit=all')['total'], 500)
        self.assertEqual(self.get('/v1/leave/requests?limit=all')['window_limit'], 500)

    def test_mail_calendar_deploys_regression(self):
        now = dt.datetime(2026, 10, 20, 9, tzinfo=dt.timezone.utc)
        self.assertEqual(api.report_monday(dt.date(2026, 10, 20)), dt.date(2026, 10, 12))
        self.assertEqual(api.report_monday(dt.date(2026, 10, 23)), dt.date(2026, 10, 19))
        self.assertEqual(self.get('/v1/mail/sent', now=now), self.get('/v1/mail/planning/sent', now=now))
        for box, team in [('planning', 'planning'), ('sales', 'sales2'), ('cs', 'cs'), ('hr', 'hr')]:
            messages = self.get(f'/v1/mail/{box}/sent', now=now)['value']
            events = self.get(f'/v1/calendar/{box}', now=now)['value']
            self.assertEqual(len(messages), 7)
            self.assertEqual(len(events), 7)
            members = c.team_members(team)
            emails = {e['email'] for e in members}
            for m in messages:
                self.assertEqual(m['from']['emailAddress']['address'], members[0]['email'])
                self.assertTrue(all(a['emailAddress']['address'] in emails for a in m['toRecipients']))
                self.assertNotIn('{', m['bodyPreview'])
                self.assertTrue({'id', 'subject', 'sentDateTime', 'from', 'toRecipients', 'bodyPreview', 'importance'} <= m.keys())
            for marker in ('하려면', '다음 주 수요일까지', 'AI 비서는'):
                self.assertTrue(any(marker in m['bodyPreview'] for m in messages))
            self.assertTrue(any(e['subject'] == '치과 예약' and not e['attendees'] for e in events))
            self.assertEqual([e['start']['dateTime'][:10] for e in events[5:]], ['2026-10-21', '2026-10-22'])
            self.assertTrue(all(e['start']['timeZone'] == 'Asia/Seoul' and e['end']['dateTime'] > e['start']['dateTime'] for e in events))
        self.assertEqual(self.call('/v1/mail/nope/sent')[0], 404)
        deploys = self.get('/v1/deploys')['deploys']
        product_names = {e['name'] for e in c.company_employees() if e['division'] == 'product'}
        self.assertTrue(4 <= len(deploys) <= 6)
        self.assertTrue(all(set(d) == {'service', 'version', 'status', 'deployed_at', 'deployed_by'} and d['deployed_by'] in product_names for d in deploys))

    def test_dynamo_serialization_pagination_handler(self):
        # AWS를 호출하지 않고 실제 핸들러의 직렬화·이벤트 전달·Query 페이지를 검증한다.
        fake = types.SimpleNamespace(resource=lambda *args: types.SimpleNamespace(Table=lambda name: object()))
        spec = importlib.util.spec_from_file_location('tested_handler', ROOT / 'infra/lambda/handler.py')
        handler = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'boto3': fake}), patch.dict(os.environ, {'TABLE_NAME': 'test', 'ORIGIN_SECRET': 'test-origin'}):
            spec.loader.exec_module(handler)
        item = {'days': .5, 'nested': [1, .25, {'x': 2.0}]}
        converted = handler.to_dynamo(item)
        self.assertIsInstance(converted['days'], Decimal)
        self.assertEqual(handler.from_dynamo(converted), item)
        calls, puts = [], []
        def query(**kwargs):
            calls.append(kwargs)
            if len(calls) == 1:
                return {'Items': [{'days': Decimal('.5'), 'pk': 'hidden'}], 'LastEvaluatedKey': {'pk': 'cursor'}}
            return {'Items': [{'days': Decimal('1'), 'sk': 'hidden'}]}
        handler._ddb = types.SimpleNamespace(query=query, put_item=lambda **kw: puts.append(kw))
        ds = handler.DynamoStore()
        self.assertEqual(ds.list_requests(T1, 2), [{'days': .5}, {'days': 1}])
        self.assertEqual(calls[1]['ExclusiveStartKey'], {'pk': 'cursor'})
        ds.put_request(T1, {'requested_at': NOW.isoformat(), 'request_id': 'REQ-ABC123', 'days': .5})
        ds.put_request(T1, {'requested_at': NOW.isoformat(), 'request_id': 'REQ-ABC124', 'days': .5})
        self.assertNotEqual(puts[0]['Item']['sk'], puts[1]['Item']['sk'])
        self.assertEqual(puts[0]['Item']['days'], Decimal('.5'))
        with patch.object(handler.lab_api, 'handle', return_value=(200, {'ok': True})) as routed, patch('builtins.print'):
            response = handler.handler({'rawPath': '/v1/employees', 'rawQueryString': 'limit=1&offset=3',
                'requestContext': {'http': {'method': 'GET'}}, 'headers': {'x-lab-origin': 'test-origin'}}, None)
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(routed.call_args.args[1], '/v1/employees?limit=1&offset=3')

    def test_shared_sources(self):
        for name in ('lab_api.py', 'lab_company.py'):
            self.assertEqual((ROOT / 'infra/lambda' / name).read_bytes(), (ROOT / 'superlab/tools' / name).read_bytes())


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ApiTests))
    failures = len(result.failures) + len(result.errors)
    print(f'\nTESTS {result.testsRun}, FAIL {failures}')
    sys.exit(bool(failures))
