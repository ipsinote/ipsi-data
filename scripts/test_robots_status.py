"""robots 판정 파일 점검 — 네트워크 없이 돈다: python scripts/test_robots_status.py
보는 것: ① 4xx 없음 = 열림 · 403·5xx·연결 실패·HTML 화면 = 막힘 ② '*'만 있으면 주 이름이 '*'를 따름
③ claude-user 이름 묶음이 있으면 웹 열기는 '*' 대신 그것(수집기는 자기 이름·*) ④ 옛 이름(anthropic-ai)·claude-searchbot은 이름 묶음이 있을 때만 막음
⑤ ClaudeBot만 막은 곳은 열림(공통 규칙 4절 — 서울대 입학본부 예) ⑥ 30일 안에 막는 규칙을 본 곳이 404로 답하면 애매(막힘)
⑦ 열지 않는 곳(언론·GED)은 목록에서 빠짐 ⑧ robots.txt 전체 글은 파일에 남지 않음."""
import datetime, json, os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import robots_status as rs

fails = []


def check(name, got, want):
    print(('ok  ' if got == want else 'FAIL') + ' ' + name + (' — 받음 %r · 기대 %r' % (got, want) if got != want else ''))
    if got != want:
        fails.append(name)


class Resp:
    def __init__(self, code, text='', ctype='text/plain', url=None):
        self.status_code, self.content, self.url = code, text.encode('utf-8'), url
        self.headers = {'Content-Type': ctype}


class Sess:
    def __init__(self, answers):
        self.answers = answers

    def get(self, url, timeout=None):
        a = self.answers[url.rsplit('/robots.txt', 1)[0]]
        if isinstance(a, Exception):
            raise a
        a.url = a.url or url
        return a


ANS = {
    'https://none.go.kr': Resp(404),
    'https://deny.go.kr': Resp(403),
    'https://down.go.kr': Resp(503),
    'https://err.go.kr': OSError('timeout'),
    'https://html.go.kr': Resp(200, '<html><body>점검 중</body></html>', 'text/html'),
    'https://star.go.kr': Resp(200, 'User-agent: *\nDisallow: /admin/\nAllow: /\n'),
    'https://named.go.kr': Resp(200, 'User-agent: *\nDisallow: /\n\nUser-agent: Claude-User\nAllow: /board/\nDisallow: /\n'),
    'https://old.go.kr': Resp(200, 'User-agent: *\nAllow: /\n\nUser-agent: anthropic-ai\nDisallow: /notice/\n'),
    'https://bot.go.kr': Resp(200, 'User-agent: ClaudeBot\nDisallow: /\n\nUser-agent: *\nAllow: /\n'),
    'https://search.go.kr': Resp(200, 'User-agent: Claude-SearchBot\nDisallow: /\n'),
    'https://mem.go.kr': Resp(404),
}

d = tempfile.mkdtemp()
w = os.path.join(d, 'watch'); os.makedirs(w)
json.dump({'hosts': [k for k in ANS] + ['https://www.newsis.com', 'https://ged.kedi.re.kr']}, open(os.path.join(w, 'robots_hosts.json'), 'w'))
json.dump([{'id': 'x', 'pages': [{'url': 'https://star.go.kr/notice/1'}]}], open(os.path.join(w, 'targets.json'), 'w'))
out = os.path.join(d, 'robots_status.json')
today = rs.kst_now().date().isoformat()
json.dump({'hosts': {'https://mem.go.kr': {'kind': 'rules', 'blockAt': today}}}, open(out, 'w'))
doc = rs.main(out, w, session=Sess(ANS), pause=0)
H = doc['hosts']
V = lambda o, path, who='web': rs.verdict(H[o], o + path, who)[0]

check('① 404 = 열림', V('https://none.go.kr', '/a'), True)
check('① 403 = 막힘', V('https://deny.go.kr', '/a'), False)
check('① 503 = 막힘', V('https://down.go.kr', '/a'), False)
check('① 연결 실패 = 막힘', V('https://err.go.kr', '/a'), False)
check('① HTML 화면 = 막힘', H['https://html.go.kr']['kind'], 'html')
check('② * 규칙 — /admin/ 막힘', V('https://star.go.kr', '/admin/x'), False)
check('② * 규칙 — /notice/ 열림', V('https://star.go.kr', '/notice/1'), True)
check('③ claude-user 이름 묶음 — /board/ 열림(* 는 다 막아도)', V('https://named.go.kr', '/board/3'), True)
check('③ claude-user 이름 묶음 — /etc 막힘', V('https://named.go.kr', '/etc'), False)
check('③ 수집기(bot)는 * 를 따라 /board/ 막힘', V('https://named.go.kr', '/board/3', 'bot'), False)
check('④ 옛 이름은 수집기 판정에 안 들어감', V('https://old.go.kr', '/notice/9', 'bot'), True)
check('④ anthropic-ai 이름 묶음이 막은 /notice/ = 막힘', V('https://old.go.kr', '/notice/9'), False)
check('④ anthropic-ai 이름 묶음 밖 = 열림', V('https://old.go.kr', '/main'), True)
check('④ Claude-SearchBot이 다 막음 = 막힘', V('https://search.go.kr', '/a'), False)
check('⑤ ClaudeBot만 막은 곳 = 열림', V('https://bot.go.kr', '/a'), True)
check('⑥ 30일 안 막은 기억 + 404 = 애매(막힘)', H['https://mem.go.kr']['kind'], 'ambiguous')
check('⑦ 언론·GED 빠짐', [o for o in H if 'newsis' in o or 'ged.kedi' in o], [])
check('⑦ 공식 공고 읽기 대상도 들어감', 'targets' in H['https://star.go.kr']['from'], True)
raw = open(out, encoding='utf-8').read()
check('⑧ robots 글 통째로 없음(주석·sitemap 없음)', ('User-agent' in raw, 'Sitemap' in raw), (False, False))
check('요약 수 = 곳 수', doc['summary']['hosts'], len(H))

print('실패 %d' % len(fails) if fails else '모두 통과')
sys.exit(1 if fails else 0)
