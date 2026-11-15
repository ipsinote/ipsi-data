"""robots.txt 판정 점검(2026-11-15 법무·보안 — 실행마다 '열림'·'막힘'이 흔들리던 곳). 네트워크 없이 돈다: python scripts/test_robots.py
보는 것: ① 5xx·429·네트워크 오류는 막힘 ② 401·403 막힘 · 404 열림 ③ RFC 9309 규칙(* · $ · 같은 이름 묶음 · 가장 긴 규칙 · BOM)
④ 30일 안에 우리를 막는 규칙을 본 곳이 '없음'·HTML로 답하면 막힘 ⑤ 고친 판정이 예전 판정보다 더 열지 않음(닫히기만 함)
⑥ robots.txt 자리에 HTML 화면이 오면 기억이 없어도 막힘(11/15 저녁 독립 검토 R1 4번 — 인천 교육청·학교 7곳 77바이트 HTML)."""
import datetime, os, sys, urllib.robotparser
sys.path.insert(0, os.path.dirname(__file__))
import requests
import fetch_official as fo

fails = []


def check(name, got, want):
    print(('ok  ' if got == want else 'FAIL') + ' ' + name + (' — 받음 %r · 기대 %r' % (got, want) if got != want else ''))
    if got != want:
        fails.append(name)


class Resp:
    def __init__(self, code, text='', ctype='text/plain', url=None):
        self.status_code, self.content, self.url = code, text.encode('utf-8'), url
        self.headers = {'Content-Type': ctype}
        self.text = text


def fetcher(answer, memory=None):
    F = fo.Fetcher(robots_memory=memory or {})
    def get(url, **kw):
        if isinstance(answer, Exception):
            raise answer
        r = answer if isinstance(answer, Resp) else Resp(*answer)
        r.url = r.url or url
        return r
    F.s.get = get
    return F


def old_allowed(answer, url):
    """2026-11-15 전 판정(비교용 — 그대로 옮김)."""
    rp = urllib.robotparser.RobotFileParser()
    if isinstance(answer, Exception):
        return False
    r = answer if isinstance(answer, Resp) else Resp(*answer)
    if r.status_code in (401, 403):
        rp.disallow_all = True
    elif r.status_code >= 400:
        rp.allow_all = True
    else:
        rp.parse(r.text.splitlines())
    return rp.can_fetch(fo.UA, url)


H = 'https://gifted.example.ac.kr'
# ① 받지 못함 = 막힘
check('5xx(503) → 막힘', fetcher((503, 'busy')).allowed(H + '/a.do'), False)
check('500 → 막힘', fetcher((500, '')).allowed(H + '/a.do'), False)
check('429 → 막힘', fetcher((429, '')).allowed(H + '/a.do'), False)
check('시간 초과 → 막힘', fetcher(requests.exceptions.ConnectTimeout('t')).allowed(H + '/a.do'), False)
F = fetcher((503, '')); F.allowed(H + '/a.do')
check('5xx 까닭 = unreachable', F.robots_why(H + '/a.do'), 'unreachable')
# ② 401·403 막힘 · 404 열림(robots 없음)
check('403 → 막힘', fetcher((403, '')).allowed(H + '/a.do'), False)
check('404 → 열림', fetcher((404, 'not found')).allowed(H + '/a.do'), True)
# ③ 규칙
ALLOW_ONLY_AI = 'User-agent: ClaudeBot\nDisallow: /\n\nUser-agent: GPTBot\nDisallow: /\n\nUser-agent: *\nAllow: /\n'
check('학습용·다른 회사 봇만 이름으로 막음 → 우리 이름은 열림', fetcher((200, ALLOW_ONLY_AI)).allowed(H + '/notice?md=v&bbsidx=1'), True)
check('우리 이름 묶음이 막음 → 막힘', fetcher((200, 'User-agent: ipsi-data-bot\nDisallow: /\n\nUser-agent: *\nAllow: /\n')).allowed(H + '/a.do'), False)
check("'*' 전체 막음 → 막힘", fetcher((200, 'User-agent: *\nDisallow: /\n')).allowed(H + '/a.do'), False)
check('BOM 뒤 첫 묶음도 읽음 → 막힘', fetcher((200, '﻿User-agent: *\nDisallow: /\n')).allowed(H + '/a.do'), False)
check('* 패턴(?mode=view) → 막힘', fetcher((200, 'User-agent: *\nDisallow: /*mode=view\n')).allowed(H + '/sel.do?mode=view&articleNo=1'), False)
check('* 패턴 밖 주소 → 열림', fetcher((200, 'User-agent: *\nDisallow: /*mode=view\n')).allowed(H + '/sel.do'), True)
check('$ 끝 패턴(.pdf$) → 막힘', fetcher((200, 'User-agent: *\nDisallow: /*.pdf$\n')).allowed(H + '/files/a.pdf'), False)
check('두 번째 * 묶음도 합침 → 막힘', fetcher((200, 'User-agent: *\nDisallow: /x/\n\nUser-agent: *\nDisallow: /sub/\n')).allowed(H + '/sub/info.do'), False)
check("'Allow: /' 뒤 Disallow /sub/ → 막힘(가장 긴 규칙)", fetcher((200, 'User-agent: *\nAllow: /\nDisallow: /sub/\n')).allowed(H + '/sub/info.do'), False)
check('Disallow /upload/·Allow /boardCnts/ → /boardCnts/ 열림', fetcher((200, 'User-agent: GPTBot\nDisallow: /\n\nUser-agent: *\nAllow: /boardCnts/\nDisallow: /upload/\nDisallow: /sub/\n')).allowed(H + '/boardCnts/list.do?boardID=1'), True)
check('같은 파일 /upload/ → 막힘', fetcher((200, 'User-agent: *\nAllow: /boardCnts/\nDisallow: /upload/\n')).allowed(H + '/upload/a.pdf'), False)
# ④ 기억: 30일 안에 우리를 막는 규칙을 본 곳
today = fo.kst_now().date()
recent = {H: {'blockAt': (today - datetime.timedelta(days=3)).isoformat()}}
old = {H: {'blockAt': (today - datetime.timedelta(days=40)).isoformat()}}
check('3일 전 막는 규칙 + 오늘 404 → 막힘(애매)', fetcher((404, ''), recent).allowed(H + '/a.do'), False)
check('3일 전 막는 규칙 + 오늘 HTML 화면 → 막힘(애매)', fetcher(Resp(200, '<html><body>점검 중</body></html>', 'text/html'), recent).allowed(H + '/a.do'), False)
check('40일 전 막는 규칙 + 오늘 404 → 열림', fetcher((404, ''), old).allowed(H + '/a.do'), True)
F = fetcher((200, 'User-agent: *\nDisallow: /\n')); F.allowed(H + '/a.do')
check('막는 규칙을 보면 blockAt = 오늘', F.robots_record()[H].get('blockAt'), today.isoformat())
F = fetcher((404, ''), recent); F.allowed(H + '/a.do')
check('애매 까닭 = ambiguous', F.robots_why(H + '/a.do'), 'ambiguous')
F = fetcher((200, ALLOW_ONLY_AI)); F.allowed(H + '/a.do')
check('우리를 안 막는 파일은 blockAt 없음', F.robots_record()[H].get('blockAt'), None)
F = fetcher((404, ''), {'https://other.example.kr': recent[H]}); F.allowed(H + '/a.do')
check('이번에 안 본 곳의 기억은 다음 실행으로 넘김', F.robots_record().get('https://other.example.kr', {}).get('kept'), True)
# ⑥ robots.txt 자리에 HTML 화면(규칙 파일이 아닌 답) — 기억이 없어도 막힘
HTML77 = Resp(200, '<script type="text/javascript">location.href="/main.do";</script>', 'text/html')   # 인천 7곳 모양(77바이트 안팎)
SOFT404 = Resp(200, '<!DOCTYPE html><html><head><title>404</title></head><body>없는 페이지</body></html>', 'text/html; charset=utf-8', H + '/resources/Error/404.html')
check('HTML 화면(기억 없음) → 막힘', fetcher(HTML77).allowed(H + '/boardCnts/list.do?boardID=1'), False)
check('없는 페이지 화면을 200으로(기억 없음) → 막힘', fetcher(SOFT404).allowed(H + '/a.do'), False)
check('HTML 종류 머리 없이 HTML 본문 → 막힘', fetcher((200, '<html><body>점검 중</body></html>')).allowed(H + '/a.do'), False)
check('HTML 종류 머리 + 본문은 글자(규칙 없음) → 막힘', fetcher(Resp(200, 'Service Unavailable', 'text/html')).allowed(H + '/a.do'), False)
F = fetcher(HTML77); F.allowed(H + '/a.do')
check('HTML 까닭 = html', F.robots_why(H + '/a.do'), 'html')
check('HTML 기록 kind = html', F.robots_record()[H].get('kind'), 'html')
RULES_AS_HTML = Resp(200, 'User-agent: *\nDisallow: /sub/\n', 'text/html')   # 종류 머리만 잘못 붙인 진짜 규칙 파일
check('HTML 종류 머리로 온 진짜 규칙 — 허용 주소 열림(예전과 같음)', fetcher(RULES_AS_HTML).allowed(H + '/boardCnts/list.do'), True)
check('HTML 종류 머리로 온 진짜 규칙 — 막는 주소 막힘', fetcher(RULES_AS_HTML).allowed(H + '/sub/info.do'), False)
F = fetcher(RULES_AS_HTML); F.allowed(H + '/a.do')
check('HTML 종류 머리로 온 진짜 규칙은 rules + blockAt 기억', (F.robots_record()[H].get('kind'), F.robots_record()[H].get('blockAt')), ('rules', today.isoformat()))
check('빈 답(HTML 종류 머리) → 빈 robots = 열림(예전과 같음)', fetcher(Resp(200, '', 'text/html')).allowed(H + '/a.do'), True)
# ⑤ 고친 판정은 예전보다 더 열지 않음(닫히기만 함)
answers = [(200, t) for t in (ALLOW_ONLY_AI, 'User-agent: *\nDisallow: /\nAllow: /boardCnts/\n', 'User-agent: *\nAllow: /\nDisallow: /sub/\n',
                                 '﻿User-agent: *\nDisallow: /\n', 'User-agent: *\nDisallow: /*mode=view\n', 'User-agent: data\nDisallow: /\n',
                                 'User-agent: *\n\nDisallow: /a/\n', '', 'Disallow: /\n', 'User-agent: *\nDisallow:\n',
                                 '<html><body>점검 중</body></html>')] + [(404, ''), (403, ''), (503, ''), (429, '')] + [
           HTML77, SOFT404, RULES_AS_HTML, Resp(200, 'Service Unavailable', 'text/html'), Resp(200, '', 'text/html')]
urls = ['/', '/a/b.do', '/sub/info.do', '/boardCnts/list.do', '/sel.do?mode=view&articleNo=2', '/upload/x.png', '/robots.txt']
more = [(a, u) for a in answers for u in urls if fetcher(a).allowed(H + u) and not old_allowed(a, H + u)]
check('새로 열리는 주소 0(예전보다 넓어지지 않음)', more, [])
closed = sum(1 for a in answers for u in urls if old_allowed(a, H + u) and not fetcher(a).allowed(H + u))
print('참고: 예전엔 열고 이제 막는 경우 %d개(5xx·429·* 패턴·BOM·두 번째 묶음·긴 규칙·HTML 화면)' % closed)

print('실패 %d' % len(fails))
sys.exit(1 if fails else 0)
