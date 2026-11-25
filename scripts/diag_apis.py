"""공공데이터포털 API 응답 모양 살펴보기(키는 찍지 않음) — 2026-11-14 대학 기본정보(getSchoolInfo)·공휴일(특일 정보) 수집기 만들기 전."""
import os, re, urllib.parse, urllib.request
key = os.environ.get('DATA_GO_KR_KEY', '').strip()
T = [
    ('대학 기본정보 getSchoolInfo 2025', 'https://apis.data.go.kr/B340014/SchoolInfoService/getSchoolInfo', {'pageNo': 1, 'numOfRows': 3, 'svyYr': 2025}),
    ('대학 기본정보 getSchoolInfo 2026', 'https://apis.data.go.kr/B340014/SchoolInfoService/getSchoolInfo', {'pageNo': 1, 'numOfRows': 3, 'svyYr': 2026}),
    ('학교별 학과 getUniversityMajorCode 2025 가천대', 'https://apis.data.go.kr/B340014/BasicInformationService_1/getUniversityMajorCode', {'pageNo': 1, 'numOfRows': 3, 'svyYr': 2025, 'schlId': '0000063'}),
    ('공휴일 getRestDeInfo 2027', 'https://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo', {'pageNo': 1, 'numOfRows': 50, 'solYear': 2027}),
    ('국경일 getHoliDeInfo 2027', 'https://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getHoliDeInfo', {'pageNo': 1, 'numOfRows': 50, 'solYear': 2027}),
    # (2026-11-25 실행 1 창 — 입시노트 운영실 카드 '대학 기본 정보 API' · 대표 11/24 활용신청) 대학알리미 대학 기본 정보_GW(15158963):
    # 같은 키(DATA_GO_KR_KEY)가 이 API에 맞는지 + 주요지표 코드 목록(cdid·cdnm·rmk)에 등록금·충원율·취업률이 있는지만 봄 — 이 API는 값은 주지 않음
    ('대학 기본 정보 주요지표 코드 getKeyIndicatorCode', 'https://apis.data.go.kr/B340014/BasicInformationService_2/getKeyIndicatorCode', {'pageNo': 1, 'numOfRows': 500}),
    ('대학 기본 정보 비교 대학 목록 getComparisonUniversitySearchList 2025 서울대', 'https://apis.data.go.kr/B340014/BasicInformationService_2/getComparisonUniversitySearchList', {'pageNo': 1, 'numOfRows': 3, 'svyYr': 2025, 'schlKrnNm': '서울대학교'}),
    ('대학 기본 정보 공시 대학 목록 getNoticeUniversitySearchList 2025 서울대', 'https://apis.data.go.kr/B340014/BasicInformationService_2/getNoticeUniversitySearchList', {'pageNo': 1, 'numOfRows': 3, 'svyYr': 2025, 'schlKrnNm': '서울대학교'}),
    ('대학 기본 정보 공시년도 getNoticeSvyYear', 'https://apis.data.go.kr/B340014/BasicInformationService_2/getNoticeSvyYear', {'pageNo': 1, 'numOfRows': 20}),
]
# (2026-11-25 12시 실행 1 창 — 운영실 카드 '등록금 받는 길' ②) 이번 실행은 아래 파일 받기 길만 봄(API 줄은 건너뜀 — 다시 보려면 FILE_ONLY = False)
FILE_ONLY = True
if FILE_ONLY:
    T = []
for name, url, q in T:
    q = dict(q, serviceKey=key)
    try:
        with urllib.request.urlopen(url + '?' + urllib.parse.urlencode(q), timeout=60) as r:
            x = r.read().decode('utf-8', 'replace')
    except Exception as e:
        x = 'ERROR %s %s %s' % (type(e).__name__, getattr(e, 'code', ''), (getattr(e, 'read', lambda: b'')() or b'')[:300].decode('utf-8', 'replace'))
    if key:   # 키는 어떤 모양으로도 남기지 않음(그대로·URL 인코딩 두 가지)
        for k in {key, urllib.parse.quote(key, safe=''), urllib.parse.quote_plus(key)}:
            x = x.replace(k, '***')
    tags = sorted(set(re.findall(r'<([A-Za-z0-9_]+)>', x)))
    print('==', name, '| 길이', len(x), '| 태그:', ','.join(tags)[:600])
    print(x[:80000] if 'getKeyIndicatorCode' in url else x[:1500])


# ── 한국장학재단_대학별 평균등록금(공공데이터포털 3071171 · CSV · 이용허락범위 제한 없음 · 로그인 없이 내려받기) — 파일 받는 길 찾기 ──
# robots: data.go.kr는 Googlebot 묶음만 있고 '*' 규칙이 없음(2026-11-24 판정) → 우리 이름(ipsi-data-bot)에 걸리는 규칙 없음 = 열어도 됨. 한 번 실행에 3~4번만 엶.
if FILE_ONLY:
    import http.cookiejar, json, time, csv, io
    UA = 'ipsi-data-bot/1.0 (+https://github.com/ipsinote/ipsi-data; public admission notice dates)'
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    def get(url, data=None, ref=None):
        h = {'User-Agent': UA, 'Accept-Language': 'ko-KR,ko;q=0.9'}
        if ref: h['Referer'] = ref
        if data is not None:
            data = urllib.parse.urlencode(data).encode(); h['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'; h['X-Requested-With'] = 'XMLHttpRequest'
        rq = urllib.request.Request(url, data=data, headers=h)
        with op.open(rq, timeout=60) as r:
            return r.status, dict(r.headers), r.read()
    PAGE = 'https://www.data.go.kr/data/3071171/fileData.do'
    try:
        st, hd, body = get(PAGE)
        html = body.decode('utf-8', 'replace')
        print('== 파일 쪽', st, len(html), '자')
        pat = re.compile(r'(fileDetailSn|atchFileId|publicDataDetailPk|publicDataPk|fileDataDown|fn_[A-Za-z]*[Dd]own[A-Za-z]*|Download\.do|download\.do|uddi:[0-9a-f-]+)')
        seen = set()
        for m in pat.finditer(html):
            a0 = max(0, m.start() - 160); snip = html[a0:m.end() + 220].replace('\n', ' ')
            k = snip[:120]
            if k in seen: continue
            seen.add(k); print('  …', snip)
            if len(seen) >= 40: break
        pk = (re.search(r'publicDataPk["\']?\s*[:=]\s*["\']?(\d+)', html) or [None, '3071171'])[1]
        dpk = re.search(r'(uddi:[0-9a-f-]{20,})', html)
        dpk = dpk.group(1) if dpk else ''
        print('== 찾은 값 publicDataPk', pk, '| publicDataDetailPk', dpk or '없음')
        time.sleep(1.5)
        if dpk:
            for sn in ('1',):
                st, hd, b2 = get('https://www.data.go.kr/tcs/dss/selectFileDataDownload.do',
                                 {'publicDataPk': pk, 'publicDataDetailPk': dpk, 'fileDetailSn': sn}, ref=PAGE)
                t2 = b2.decode('utf-8', 'replace'); print('== selectFileDataDownload', st, hd.get('Content-Type'), t2[:800])
                try:
                    j = json.loads(t2)
                except Exception:
                    j = {}
                fid = j.get('atchFileId') or (j.get('fileDataRegistVO') or {}).get('atchFileId') if isinstance(j, dict) else None
                fsn = (j.get('fileDetailSn') if isinstance(j, dict) else None) or sn
                if fid:
                    time.sleep(1.5)
                    st, hd, b3 = get('https://www.data.go.kr/cmm/cmm/fileDownload.do?' + urllib.parse.urlencode({'atchFileId': fid, 'fileDetailSn': fsn, 'insertDataPrcus': 'N'}), ref=PAGE)
                    print('== fileDownload', st, hd.get('Content-Type'), hd.get('Content-Disposition'), len(b3), '바이트')
                    for enc in ('utf-8-sig', 'cp949'):
                        try:
                            txt = b3.decode(enc); break
                        except Exception:
                            txt = None
                    if txt:
                        rows = list(csv.reader(io.StringIO(txt)))
                        print('   인코딩', enc, '| 줄', len(rows), '| 머리', rows[0] if rows else None)
                        for r in rows[1:4]: print('   ', r)
                        for r in rows:
                            if r and any('서울대학교' == c.strip() for c in r): print('   서울대 줄', r)
    except Exception as e:
        print('== 파일 받기 길 오류', type(e).__name__, getattr(e, 'code', ''), str(e)[:300])
