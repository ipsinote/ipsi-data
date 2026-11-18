"""출처 점검 판정 시험(2026-11-18 대표 결정 '링크 오류 대응 B안'). 네트워크 없이 돈다: python scripts/test_verdicts.py

보는 것
① 시험 세트(watch/verdict_cases.json — 사례집 주소 '주소 → 기대 판정'): 사례마다 가짜 답(runs)을 차례로 두 주 돌린 뒤의 verdict·why
② 낱개: 첫 실패는 caution(아직 broken 아님) · 긴 정상 쪽의 '권한이 없습니다'는 소프트 404가 아님 · 짧은 쪽의 알림창 글은 소프트 404 ·
   열리는 내려받기 주소는 caution · 잠깐 못 찾음(이름은 있음)은 dns가 아님 · 403 두 번은 연속 실패로 안 셈 · 규칙 파일이 없으면 예전처럼
③ 지난 실제 결과(data/sources_status.json)를 새 판정으로 다시 셈 — 숫자만 보여 줌(오류 없이 도는지)

python scripts/test_verdicts.py --live : 시험 세트 주소를 진짜로 한 번씩 열어 판정을 보여 줌(GitHub Actions에서만 — robots 지킴 · 맞고 틀림은 세지 않음)
"""
import contextlib, datetime, io, json, os, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import check_sources as cs

cs.RETRY_WAIT = 0
fails = []
KST = datetime.timezone(datetime.timedelta(hours=9))
BASE = datetime.datetime(2026, 11, 22, 15, 37, tzinfo=KST)


def check(name, got, want):
    ok = got == want
    print(('ok  ' if ok else 'FAIL') + ' ' + name + ('' if ok else ' — 받음 %r · 기대 %r' % (got, want)))
    if not ok:
        fails.append(name)


class FakeF:
    """check_sources가 쓰는 Fetcher 자리(get · robots_why)에 정해 둔 답을 돌려줌."""
    def __init__(self, run):
        self.run = run

    def get(self, url, binary=False, referer=None):
        r = self.run
        st = r['st']
        if st == 'ok':
            return 'ok', r.get('html', '<html><head><title></title></head><body></body></html>'), r.get('final', url), 'text/html'
        return st, None, url, ''

    def robots_why(self, url):
        return self.run.get('robots', '') if self.run['st'] == 'robots' else ''


def run_case(url, name, runs, rules, kind='공식'):
    """runs를 한 주씩(7일 간격) 돌리고 마지막 상태(item)와 보고서 글을 돌려줌."""
    d = tempfile.mkdtemp()
    reg_p, out_p, rep_p = os.path.join(d, 'reg.json'), os.path.join(d, 'st.json'), os.path.join(d, 'rep.md')
    json.dump({'ver': 'test', 'generated': '2026-11-18', 'count': 1,
               'sources': [{'id': 'x', 'url': url, 'host': cs.host(url), 'name': name, 'kind': kind, 'cat': '시험', 'used': ['t'], 'cycle': 'w'}]},
              open(reg_p, 'w', encoding='utf-8'), ensure_ascii=False)
    for i, r in enumerate(runs):
        res = r.get('resolve') or {}
        with contextlib.redirect_stdout(io.StringIO()):   # 점검의 한 줄 요약은 시험 화면에 찍지 않음
            cs.main(reg_p, out_p, rep_p, F=FakeF(r), now=BASE + datetime.timedelta(days=7 * i), resolve=lambda h, res=res: res.get(h, True), rules=rules)
    st = json.load(open(out_p, encoding='utf-8'))
    return st['items']['x'], open(rep_p, encoding='utf-8').read(), st


def main_offline():
    rules = cs.load_rules()
    check('판정 규칙 파일 읽힘', bool(rules.get('soft404') and rules.get('dns') and rules.get('fileUrl') and rules.get('year')), True)
    cases = json.load(open(os.path.join(ROOT, 'watch', 'verdict_cases.json'), encoding='utf-8'))['cases']
    print('\n① 시험 세트 %d개' % len(cases))
    hit = 0
    for c in cases:
        it, rep, _ = run_case(c['url'], c['name'], c['runs'], rules)
        got = it.get('verdict')
        miss = [w for w in c.get('whyHas', []) if w not in it.get('why', [])]
        good = got == c['expect'] and not miss and (not c.get('alt') or it.get('alt') == c['alt'])
        hit += good
        check('%s → %s(why %s)' % (c['id'], c['expect'], ','.join(c.get('whyHas', [])) or '-'),
              (got, miss, it.get('alt') if c.get('alt') else None), (c['expect'], [], c.get('alt')))
    print('시험 세트 기대 판정대로: %d / %d' % (hit, len(cases)))

    print('\n② 낱개')
    it, _, _ = run_case('https://example.go.kr/a', '시험', [{'st': 'http-404'}], rules)
    check('첫 실패 한 번은 caution(아직 broken 아님)', (it['verdict'], it['failStreak']), ('caution', 1))
    it, rep, _ = run_case('https://example.go.kr/a', '시험', [{'st': 'http-404'}, {'st': 'http-404'}], rules)
    check('두 번 연속 실패는 broken · 보고서 끊김 칸', (it['verdict'], '## 끊김: 두 번 연속 못 엶 (1)' in rep), ('broken', True))
    longpage = '<html><head><title>공지 글</title></head><body><main>' + ('입학 전형 안내 본문입니다. ' * 300) + '권한이 없습니다</main></body></html>'
    it, _, _ = run_case('https://example.go.kr/b', '시험', [{'st': 'ok', 'html': longpage}], rules)
    check('긴 정상 쪽에 섞인 \'권한이 없습니다\'는 소프트 404가 아님', (it['status'], it['verdict']), ('ok', 'ok'))
    alertpage = "<html><head><title>학교</title><script>alert('존재하지 않는 게시물입니다.'); history.back();</script></head><body></body></html>"
    it, _, _ = run_case('https://example.go.kr/c', '시험', [{'st': 'ok', 'html': alertpage}], rules)
    check('짧은 쪽의 알림창 글(존재하지 않는 게시물)은 소프트 404', (it['status'], it.get('soft404')), ('soft404', '존재하지 않는 게시물'))
    it, _, _ = run_case('https://example.ac.kr/notice?md=down&bbsidx=1&fileidx=2', '시험', [{'st': 'ok', 'html': '<html><head><title>x</title></head><body>파일</body></html>'}], rules)
    check('열리는 내려받기 주소는 caution(알림만)', (it['verdict'], 'file-url' in it['why']), ('caution', True))
    it, _, _ = run_case('https://www.example.go.kr', '시험', [{'st': 'robots', 'robots': 'unreachable', 'resolve': {'www.example.go.kr': True}}] * 2, rules)
    check('robots.txt를 못 받았어도 이름이 있으면 dns가 아님(restricted)', (it['status'], it['verdict']), ('robots', 'restricted'))
    it, _, _ = run_case('https://www.example.go.kr', '시험', [{'st': 'robots', 'robots': 'rules', 'resolve': {'www.example.go.kr': False}}], rules)
    check('robots 규칙이 막은 곳은 dns를 보지 않음', it['status'], 'robots')
    it, _, _ = run_case('https://journal.example.org/a', '시험', [{'st': 'http-403'}] * 3, rules, kind='기타')
    check('403 세 번도 연속 실패로 안 셈(restricted)', (it['verdict'], it.get('failStreak')), ('restricted', 0))
    it, _, _ = run_case('https://wjgift.gwe.go.kr/boardCnts/view.do?boardID=1&boardSeq=2', '2027학년도 원주 영재교육원 요강',
                        [{'st': 'ok', 'html': '<html><head><title>2027학년도 요강</title></head><body><main>요강</main></body></html>'}], rules)
    check('교육부가 아닌 boardCnts/view.do는 옛 주소 꼴이 아님', (it['status'], it['verdict']), ('ok', 'ok'))
    it, _, _ = run_case('https://example.hs.kr/y', '○○고 2027학년도 요강', [{'st': 'ok', 'html': '<html><head><title>○○고 2027학년도 신입생 요강</title></head><body>x</body></html>'}], rules)
    check('학년도가 같으면 알림 없음', (it['verdict'], 'year' in it['why']), ('ok', False))
    it, _, _ = run_case('https://example.hs.kr/y', '○○고 입학 안내', [{'st': 'ok', 'html': '<html><head><title>○○고 2026학년도 요강</title></head><body>x</body></html>'}], rules)
    check('출처 이름에 학년도가 없으면 학년도는 보지 않음', 'year' in it['why'], False)
    it, rep, _ = run_case('https://example.go.kr/a', '시험', [{'st': 'http-404'}, {'st': 'http-404'}], {})
    check('규칙 파일이 없으면 예전처럼(verdict 없음 · failStreak 2 = 끊김)', ('verdict' in it, '## 끊김: 두 번 연속 못 엶 (1)' in rep, '## 주의' in rep), (False, True, False))
    it, _, _ = run_case('https://example.go.kr/a', '시험', [{'st': 'http-404'}, {'st': 'ok', 'html': '<html><head><title>새 글</title></head><body><main>' + '본문 ' * 800 + '</main></body></html>'}], rules)
    check('다시 열리면 failStreak 0 · ok', (it['failStreak'], it['verdict']), (0, 'ok'))

    print('\n③ 지난 실제 결과(data/sources_status.json)를 새 판정으로 다시 셈 — 이번에 다시 열지 않은 상태 그대로')
    sp, rp = os.path.join(ROOT, 'data', 'sources_status.json'), os.path.join(ROOT, 'watch', 'sources.json')
    if os.path.exists(sp) and os.path.exists(rp):
        items = json.load(open(sp, encoding='utf-8')).get('items') or {}
        reg = {x['id']: x for x in json.load(open(rp, encoding='utf-8'))['sources']}
        vc, wc = {}, {}
        for k, v in items.items():
            vd, why = cs.judge(v, reg.get(k, {'url': v.get('url')}), rules)
            vc[vd] = vc.get(vd, 0) + 1
            for w in why:
                wc[w] = wc.get(w, 0) + 1
        print('  판정: ' + ' · '.join('%s %d' % kv for kv in sorted(vc.items())))
        print('  이유: ' + ' · '.join('%s %d' % kv for kv in sorted(wc.items())))
    print('\n' + ('모두 통과' if not fails else '실패 %d: %s' % (len(fails), ', '.join(fails))))
    return 1 if fails else 0


def main_live():
    """시험 세트 주소를 진짜로 한 번씩 연다(robots 지킴) — 첫 주라서 실패는 caution으로 나오는 것이 정상. 맞고 틀림은 세지 않는다."""
    import fetch_official as fo
    rules = cs.load_rules()
    cases = json.load(open(os.path.join(ROOT, 'watch', 'verdict_cases.json'), encoding='utf-8'))['cases']
    F = fo.Fetcher()
    for c in cases:
        d = tempfile.mkdtemp()
        reg_p, out_p, rep_p = os.path.join(d, 'reg.json'), os.path.join(d, 'st.json'), os.path.join(d, 'rep.md')
        json.dump({'ver': 'live', 'count': 1, 'sources': [{'id': 'x', 'url': c['url'], 'host': cs.host(c['url']), 'name': c['name'], 'kind': '공식', 'cat': '시험', 'used': ['t'], 'cycle': 'w'}]},
                  open(reg_p, 'w', encoding='utf-8'), ensure_ascii=False)
        cs.main(reg_p, out_p, rep_p, F=F, rules=rules)
        it = json.load(open(out_p, encoding='utf-8'))['items']['x']
        print('%-18s 기대 %-10s 이번 %-10s status %-10s why %s %s' % (c['id'], c['expect'], it.get('verdict'), it.get('status'), ','.join(it.get('why', [])), it.get('alt', '')))
    return 0


if __name__ == '__main__':
    sys.exit(main_live() if '--live' in sys.argv else main_offline())
