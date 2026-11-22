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

SGG_XLSX = BASE + '/download/sido_sggCode.xlsx'      # 2026-11-22 목록 화면 '시도시군구코드.xlsx' 단추가 가리키는 주소
OUTPUT_XLSX = BASE + '/download/OpenAPI_Output.xlsx'  # 출력값 설명
PROBE = ('11', '11110')                               # 매달 키 점검: 서울 종로구 한 곳(국립 2곳 · 사립이 있는 구)
KEEP = ('사립', '국립')


def kst_now():
    return time.gmtime(time.time() + 9 * 3600)


def now_utc():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def sgg_codes():
    """공식 코드표 파일에서 (시도 2자리, 시군구 5자리, 이름) 줄을 뽑음 — 칸 이름을 몰라도 숫자 모양으로 찾음."""
    b, _ = get(SGG_XLSX, binary=True)
    rows = load_xlsx(b)
    out, seen = [], set()
    for r in rows:
        sido = next((c for c in r if re.fullmatch(r'\d{2}', c)), '')
        sgg = next((c for c in r if re.fullmatch(r'\d{5}', c)), '')
        if sido and sgg and sgg.startswith(sido) and sgg not in seen:
            seen.add(sgg)
            names = [c for c in r if c and not re.fullmatch(r'[\d.]+', c)]
            out.append({'sido': sido, 'sgg': sgg, 'name': ' '.join(names[:2])})
    return out, rows[:3]


def num(v):
    """'553(5)' → (553, 5) · 553 → (553, None) · 없음 → (None, None)."""
    if v is None or v == '':
        return None, None
    if isinstance(v, (int, float)):
        return int(v), None
    m = re.fullmatch(r'\s*(\d+)\s*(?:\((\d+)\))?\s*', str(v))
    return (int(m.group(1)), int(m.group(2)) if m.group(2) else None) if m else (None, None)


def row_of(x, sido, sgg, year):
    cls, cls_sp = num(x.get('COL_SUM'))
    stu, stu_sp = num(x.get('COL_FGR_SUM'))
    return {'code': x.get('SCHUL_CODE'), 'name': x.get('SCHUL_NM'), 'found': x.get('FOND_SC_CODE'),
            'branch': x.get('BNHH_YN'), 'excluded': x.get('PBAN_EXCP_YN'),
            'classes': cls, 'classesSp': cls_sp, 'students': stu, 'studentsSp': stu_sp,
            'raw': {'COL_SUM': x.get('COL_SUM'), 'COL_FGR_SUM': x.get('COL_FGR_SUM'), 'SP_SUM': x.get('SP_SUM'),
                    'SP_FGR_SUM': x.get('SP_FGR_SUM'), 'AVG_FGR_SUM': x.get('AVG_FGR_SUM')},
            'classesByGrade': [x.get('COL_%d' % i) for i in range(1, 7)],
            'adrcd': x.get('ADRCD_CD'), 'adrcdName': x.get('ADRCD_NM'), 'office': x.get('JU_ORG_NM'),
            'atpt': x.get('ATPT_OFCDC_ORG_NM'), 'sido': sido, 'sgg': sgg, 'pbanYr': year}


def fetch_all(k, year, codes):
    keep, fails, empty, seen_rows = [], [], 0, 0
    for c in codes:
        j = call(k, apiType='62', pbanYr=str(year), schulKndCode='02', sidoCode=c['sido'], sggCode=c['sgg'])
        if j.get('resultCode') == 'success':
            it = items_of(j)
            seen_rows += len(it)
            keep += [row_of(x, c['sido'], c['sgg'], year) for x in it if str(x.get('FOND_SC_CODE')) in KEEP]
        elif '존재하지 않' in str(j.get('resultMsg', '')):
            empty += 1
        else:
            fails.append({'sgg': c['sgg'], 'why': hide(j.get('resultMsg') or j.get('_http') or j.get('_err') or j.get('_text'))[:120]})
        time.sleep(PAUSE)
    return keep, fails, empty, seen_rows


def save(name, obj):
    os.makedirs(OUT, exist_ok=True)
    with io.open(os.path.join(OUT, name), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write('\n')


def load(name):
    try:
        return json.load(io.open(os.path.join(OUT, name), encoding='utf-8'))
    except Exception:
        return None


def probe(k, year):
    j = call(k, apiType='62', pbanYr=str(year), schulKndCode='02', sidoCode=PROBE[0], sggCode=PROBE[1])
    it = items_of(j)
    fp = sorted((x.get('SCHUL_CODE'), str(x.get('COL_FGR_SUM'))) for x in it)
    return j.get('resultCode') == 'success', hide(j.get('resultMsg') or j.get('_http') or j.get('_err') or '')[:120], fp


def run(force=True):
    k = key()
    ok, why = robots_ok(SGG_XLSX)
    if not ok:
        sys.exit('코드표 파일을 robots가 막음 — 멈춤: ' + why)
    y = kst_now().tm_year
    st = load('run.json') or {}
    # 공시연도: 올해 자료가 있으면 올해, 없으면 지난해(학생 수 공시는 해마다 한 번 — 올해 것이 올라오기 전엔 지난해)
    year, (good, msg, fp) = y, probe(k, y)
    if not good:
        year, (good, msg, fp) = y - 1, probe(k, y - 1)
    st.update({'checkedAt': now_utc(), 'keyOk': good, 'probe': '서울 종로구', 'probeMsg': msg})
    if not good:
        st['result'] = 'fail'
        save('run.json', st)
        sys.exit('키 점검 실패: ' + msg)
    if not force and st.get('pbanYr') == year and st.get('probeFp') == fp:
        st['result'] = 'same'           # 매달 점검: 공시연도·표본이 그대로면 전체를 다시 받지 않음
        save('run.json', st)
        print('키 정상 · 바뀐 것 없음(공시연도 %s)' % year)
        return
    codes, head = sgg_codes()
    if len(codes) < 200:
        st['result'] = 'fail'
        save('run.json', st)
        sys.exit('코드표에서 시·군·구를 %d개만 찾음 — 파일 모양이 바뀐 듯(첫 줄 %s)' % (len(codes), head[:1]))
    keep, fails, empty, seen_rows = fetch_all(k, year, codes)
    prev = (load('elem_private_national.json') or {}).get('schools') or []
    if prev and len(keep) < len(prev) * 0.9:
        st['result'] = 'fail'
        save('run.json', st)
        sys.exit('사립·국립 초등학교가 %d → %d로 10%% 넘게 줄어 저장하지 않음(API 오류로 봄)' % (len(prev), len(keep)))
    keep.sort(key=lambda r: (r['sido'], r['sgg'], r['name'] or ''))
    save('sgg_codes.json', {'source': '학교알리미 시도시군구코드.xlsx(%s)' % SGG_XLSX, 'fetched': now_utc(), 'count': len(codes), 'codes': codes})
    save('elem_private_national.json', {
        'source': '학교알리미 Open API 학교 현황(apiType 62 · 초등 02) — 출처: 학교알리미(한국교육학술정보원)',
        'license': '공공누리 출처표시(영리·변경 가능)', 'pbanYr': year, 'fetched': now_utc(),
        'note': '사립·국립 초등학교만 저장(전국 모든 학교 숫자는 저장하지 않음) · students = 학생수계(COL_FGR_SUM 괄호 앞 숫자) · 괄호 안은 raw 그대로',
        'counts': {'사립': sum(r['found'] == '사립' for r in keep), '국립': sum(r['found'] == '국립' for r in keep)},
        'schools': keep})
    st.update({'result': 'ok' if not fails else 'partial', 'pbanYr': year, 'probeFp': fp, 'sgg': len(codes), 'sggEmpty': empty,
               'sggFail': len(fails), 'fails': fails[:30], 'rowsSeen': seen_rows, 'schools': len(keep), 'fullAt': now_utc()})
    save('run.json', st)
    print(json.dumps({a: st[a] for a in ('result', 'pbanYr', 'sgg', 'sggEmpty', 'sggFail', 'rowsSeen', 'schools')}, ensure_ascii=False))


def diag_files():
    for u in (SGG_XLSX, OUTPUT_XLSX):
        try:
            b, ct = get(u, binary=True)
            rows = load_xlsx(b)
            print('파일', u.rsplit('/', 1)[1], len(b), '바이트 ·', len(rows), '줄 ·', ct)
            for r in rows[:4]:
                print('   ', [c for c in r if c][:12])
            if 'Output' in u:
                for r in rows:
                    t = ' | '.join(c for c in r if c)
                    if re.search(r'COL_FGR_SUM|COL_SUM|SP_FGR_SUM|BNHH_YN|PBAN_EXCP_YN|FOND_SC_CODE|학교 ?현황', t):
                        print('    ·', t[:220])
        except Exception as e:
            print('파일 못 받음', u, type(e).__name__, str(e)[:120])
    codes, head = sgg_codes()
    print('코드표에서 찾은 시·군·구', len(codes), '· 앞 3', codes[:3])


def main():
    mode = (sys.argv[1:2] or ['diag'])[0]
    if mode == 'diag':
        diag()
        diag_files()
    elif mode == 'run':
        run(force=True)
    elif mode == 'ping':
        run(force=False)
    else:
        sys.exit(f'모르는 모드: {mode}')


if __name__ == '__main__':
    main()
