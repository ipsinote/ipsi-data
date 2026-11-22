"""
학교알리미 Open API '학교 현황'(apiType 62) → 사립·국립 초등학교의 학급 수·학생 수만 저장합니다.

- 2026-11-22 대표가 키를 받아 GitHub 비밀 값 SCHOOLINFO_KEY에 넣음(일반인 · 운영계정 · 사업에 활용).
  키는 환경 변수에서만 읽고, 로그에서는 가립니다(::add-mask:: · 오류 글의 apiKey=***).
- 2026년 1월 1일 뒤 받은 키는 시·군·구 값(sggCode)이 필수 → 시·군·구마다 한 번씩 부릅니다(요청 제한 없음 · 1.2초 쉼).
- 저장하는 것: 사립·국립 초등학교만(예비 초1 학교 목록에 쓰는 것). 전국 모든 학교 숫자는 저장하지 않습니다(넣는 정보 원칙).
- 화면에 쓸 때 출처 '학교알리미(한국교육학술정보원) · 공시연도'를 함께 적습니다(키 신청 때 약속 · 이용허락 공공누리 출처표시).

쓰는 법
  python scripts/fetch_schoolinfo.py diag   # 응답 모양만 살펴보기(저장 안 함) — 코드표·요청 변수·출력 칸 이름 확인
  python scripts/fetch_schoolinfo.py run    # 받아서 data/schoolinfo/ 에 저장
  python scripts/fetch_schoolinfo.py ping   # 매달 키 점검 — 시·군·구 하나만 부름

결과 파일(run)
  data/schoolinfo/elem_private_national.json : 사립·국립 초등학교 {공시연도, 학교코드, 학교명, 설립구분, 분교, 공시 제외, 학급수계, 학생수계}
  data/schoolinfo/sgg_codes.json             : 시도·시군구 코드표(공식 코드표 파일에서 읽은 것)
  data/schoolinfo/run.json                   : 마지막 실행(시각 · 시·군·구 수 · 실패 수 · 학교 수)
"""
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser

BASE = 'https://www.schoolinfo.go.kr'
API = BASE + '/openApi.do'
LIST_PAGE = BASE + '/ng/go/pnnggo_a01_l0.do'
UA = 'ipsi-data-bot/1.0 (+https://github.com/ipsinote/ipsi-data; public school disclosure counts)'
OUT = os.path.join(os.environ.get('OUT_DIR', 'data'), 'schoolinfo')
PAUSE = 1.2


def key():
    k = os.environ.get('SCHOOLINFO_KEY', '').strip()
    if not k:
        sys.exit('비밀 값 SCHOOLINFO_KEY가 없습니다(저장소 Settings → Secrets and variables → Actions)')
    if os.environ.get('GITHUB_ACTIONS'):
        print('::add-mask::' + k)
    return k


def hide(s):
    return re.sub(r'(apiKey=)[^&\s"\']+', r'\1***', str(s))


def get(url, binary=False, timeout=40):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        b = r.read()
        if binary:
            return b, r.headers.get('Content-Type', '')
        ct = r.headers.get('Content-Type', '')
        m = re.search(r'charset=([\w-]+)', ct, re.I)
        enc = (m.group(1) if m else '').lower()
        for e in ([enc] if enc else []) + ['utf-8', 'euc-kr', 'cp949']:
            try:
                return b.decode(e)
            except Exception:
                continue
        return b.decode('utf-8', 'replace')


def robots_ok(url):
    rp = urllib.robotparser.RobotFileParser()
    try:
        txt = get(BASE + '/robots.txt', timeout=20)
    except urllib.error.HTTPError as e:
        if 400 <= e.code < 500:
            return True, f'robots.txt {e.code} — 규칙 없음(RFC 9309)'
        return False, f'robots.txt {e.code}'
    except Exception as e:
        return False, f'robots.txt 못 받음 {type(e).__name__}'
    rp.parse(txt.splitlines())
    ok = rp.can_fetch('ipsi-data-bot', url)
    return ok, 'robots 허용' if ok else 'robots가 막음'


def call(k, **params):
    q = {'apiKey': k}
    q.update({a: b for a, b in params.items() if b not in (None, '')})
    url = API + '?' + urllib.parse.urlencode(q)
    try:
        txt = get(url)
    except urllib.error.HTTPError as e:
        return {'_http': e.code}
    except Exception as e:
        return {'_err': hide(type(e).__name__ + ' ' + str(e))[:200]}
    try:
        return json.loads(txt)
    except Exception:
        return {'_text': hide(txt[:300])}


def items_of(j):
    """응답에서 학교 줄 목록을 찾음(키 이름을 모를 때 — 리스트인 값 중 가장 긴 것)."""
    if isinstance(j, list):
        return j
    best = []
    if isinstance(j, dict):
        for v in j.values():
            if isinstance(v, list) and len(v) > len(best) and all(isinstance(x, dict) for x in v[:3]):
                best = v
            elif isinstance(v, dict):
                w = items_of(v)
                if len(w) > len(best):
                    best = w
    return best


def shape(j):
    if not isinstance(j, dict):
        return {'type': type(j).__name__}
    out = {}
    for a, b in j.items():
        if isinstance(b, list):
            out[a] = f'list[{len(b)}]'
        elif isinstance(b, dict):
            out[a] = 'dict(' + ','.join(list(b)[:12]) + ')'
        else:
            out[a] = hide(str(b))[:120]
    return out


# ── 코드표 ─────────────────────────────────────────────

def find_links(html):
    links = []
    for m in re.finditer(r'''(?:href|onclick)\s*=\s*["']([^"']+)["']''', html, re.I):
        v = m.group(1)
        s = max(0, m.start() - 160)
        ctx = re.sub(r'<[^>]+>', ' ', html[s:m.end() + 160])
        ctx = re.sub(r'\s+', ' ', ctx).strip()
        if re.search(r'xlsx|pdf|down|file', v, re.I) or re.search(r'코드|가이드|출력값', ctx):
            links.append((v, ctx[:220]))
    return links


def load_xlsx(b):
    import openpyxl  # 작업 안에서 pip로 설치
    wb = openpyxl.load_workbook(io.BytesIO(b), read_only=True, data_only=True)
    rows = []
    for ws in wb.worksheets:
        for r in ws.iter_rows(values_only=True):
            rows.append([('' if c is None else str(c).strip()) for c in r])
    return rows


def diag():
    k = key()
    ok, why = robots_ok(LIST_PAGE)
    print('① robots(목록 화면):', why)
    html = ''
    if ok:
        try:
            html = get(LIST_PAGE)
            print('   목록 화면 글자 수', len(html))
        except Exception as e:
            print('   목록 화면 못 받음', type(e).__name__, str(e)[:120])
    links = find_links(html) if html else []
    print('② 파일 링크 후보', len(links))
    for v, ctx in links[:40]:
        print('   -', v[:160], '|', ctx[:160])
    # 공시연도·학교급만 바꿔 sggCode 없이 한 번(오류 글로 필수 칸 확인)
    print('③ 요청 모양 시험(키는 가림)')
    tries = [
        dict(apiType='62', pbanYr='2026', schulKndCode='02'),
        dict(apiType='62', pbanYr='2026', schulKndCode='02', sidoCode='11'),
        dict(apiType='62', pbanYr='2026', schulKndCode='02', sidoCode='1100000000'),
        dict(apiType='62', pbanYr='2026', schulKndCode='02', sidoCode='11', sggCode='11110'),
        dict(apiType='62', pbanYr='2026', schulKndCode='02', sidoCode='1100000000', sggCode='1111000000'),
        dict(apiType='62', pbanYr='2025', schulKndCode='02', sidoCode='1100000000', sggCode='1111000000'),
        dict(apiType='0', sidoCode='1100000000', sggCode='1111000000', schulKndCode='02'),
    ]
    for t in tries:
        j = call(k, **t)
        it = items_of(j)
        print('   ', t, '→', json.dumps(shape(j), ensure_ascii=False)[:400], '| 줄', len(it))
        if it:
            print('      첫 줄 칸:', json.dumps(it[0], ensure_ascii=False)[:700])
        time.sleep(PAUSE)


# ── 받기 ───────────────────────────────────────────────

def main():
    mode = (sys.argv[1:2] or ['diag'])[0]
    if mode == 'diag':
        diag()
    else:
        sys.exit(f'아직 없는 모드: {mode} — diag로 응답 모양을 먼저 봅니다')


if __name__ == '__main__':
    main()
