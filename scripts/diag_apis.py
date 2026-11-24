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
    ('대학 기본 정보 공시년도 getNoticeSvyYear', 'https://apis.data.go.kr/B340014/BasicInformationService_2/getNoticeSvyYear', {'pageNo': 1, 'numOfRows': 20}),
]
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
