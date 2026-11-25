"""한국장학재단 대학별 평균등록금 받기 — 공공데이터포털 파일데이터(로그인 없이 내려받기).

출처: 한국장학재단, 「한국장학재단_대학별 평균등록금」, 공공데이터포털 데이터 번호 3071171
      (이용허락범위 제한 없음 · 연간 · 매년 4월 대학정보공시 기준 · 분교·캠퍼스는 본교에 합산 · 평균등록금은 연간 기준 · 학부 입학금은 2023년부터 폐지).
      2026-11-25 실행 1 창 — 입시노트 운영실 카드 '등록금 받는 길' ②(자료 저장소 작업이 파일로 연 1번 받기 · 대표 0분).

받는 길(2026-11-25 응답 살펴보기로 확인 — 가지 diag-out 37e47ce):
  ① 파일 쪽 https://www.data.go.kr/data/3071171/fileData.do 의 숨은 칸 publicDataDetailPk(uddi:…)·updtDt(고친 때)를 읽음
  ② POST /tcs/dss/selectFileDataDownload.do (publicDataPk·publicDataDetailPk·fileDetailSn=1) → JSON 안의 atchFileId·fileDetailSn
  ③ GET /cmm/cmm/fileDownload.do?atchFileId=…&fileDetailSn=…&insertDataPrcus=N → CSV(cp949 · 382줄 + 머리줄 · 24,270바이트, 2026-05-19 판)
robots: data.go.kr robots.txt는 Googlebot 묶음만 있고 '*'·우리 이름 규칙이 없음(2026-11-24 판정) — 열기 전에 다시 받아 우리 이름(ipsi-data-bot)이나
        '*' 묶음이 이 주소들을 막으면 열지 않고 끝냄(RFC 9309 · fetch_official.py와 같은 기준 — robots를 못 받으면 막힘으로 봄).
점검: 머리줄 7칸이 정해진 이름과 같음 · 줄 수가 쪽에 적힌 '전체 행'과 같음 · 평균등록금이 숫자이고 50만~2,000만 원 안 — 하나라도 어긋나면 저장하지 않음.
저장: data/univ_tuition/latest.json(고친 때가 그대로면 파일도 그대로) · data/univ_tuition/run.json(실행 기록). 원본 CSV는 저장하지 않음(칸을 그대로 옮긴 JSON만).
쓰는 법: python scripts/fetch_tuition.py [--dry]
"""
import csv
import datetime
import hashlib
import http.cookiejar
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

PK = '3071171'
PAGE = f'https://www.data.go.kr/data/{PK}/fileData.do'
SEL = 'https://www.data.go.kr/tcs/dss/selectFileDataDownload.do'
DOWN = 'https://www.data.go.kr/cmm/cmm/fileDownload.do'
UA_NAME = 'ipsi-data-bot'
UA = 'ipsi-data-bot/1.0 (+https://github.com/ipsinote/ipsi-data; public admission notice dates)'
OUT = 'data/univ_tuition'
HEAD = ['학제별', '설립별', '대학명', '지역별', '입학정원', '평균입학금', '평균등록금(원)']
SOURCE = {'org': '한국장학재단', 'name': '한국장학재단_대학별 평균등록금', 'portal': '공공데이터포털', 'id': PK, 'url': PAGE,
          'license': '이용허락범위 제한 없음', 'basis': '매년 4월 대학정보공시 기준 · 분교·캠퍼스는 본교에 합산 · 평균등록금은 연간(학기 아님)'}


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


class Net:
    def __init__(self):
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def get(self, url, data=None, ref=None):
        h = {'User-Agent': UA, 'Accept-Language': 'ko-KR,ko;q=0.9'}
        if ref:
            h['Referer'] = ref
        if data is not None:
            data = urllib.parse.urlencode(data).encode()
            h['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
            h['X-Requested-With'] = 'XMLHttpRequest'
        with self.op.open(urllib.request.Request(url, data=data, headers=h), timeout=90) as r:
            return r.status, dict(r.headers), r.read()


def robots_ok(net):
    """우리 이름·'*' 묶음이 세 주소를 막는지 — 못 받으면(5xx·연결 실패) 막힘, 4xx(파일 없음)는 규칙 없음."""
    try:
        st, _, b = net.get('https://www.data.go.kr/robots.txt')
    except urllib.error.HTTPError as e:
        if 400 <= e.code < 500 and e.code not in (401, 403):
            return True, f'robots.txt {e.code} — 규칙 없음'
        return False, f'robots.txt {e.code} — 막힘으로 봄'
    except Exception as e:
        return False, f'robots.txt 못 받음({type(e).__name__}) — 막힘으로 봄'
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(b.decode('utf-8', 'replace').splitlines())
    bad = [u for u in (PAGE, SEL, DOWN) if not rp.can_fetch(UA_NAME, u)]
    return (not bad), ('막힌 주소: ' + ', '.join(bad)) if bad else 'robots 허용(우리 이름·* 묶음에 막는 규칙 없음)'


def num(x):
    x = (x or '').replace(',', '').strip()
    return float(x) if re.fullmatch(r'-?\d+(\.\d+)?', x) else None


def main():
    dry = '--dry' in sys.argv
    t0 = time.time()
    net = Net()
    run = {'at': now_utc(), 'ok': False}
    ok, why = robots_ok(net)
    run['robots'] = why
    if not ok:
        return finish(run, f'열지 않음 — {why}', dry)
    time.sleep(1.5)
    st, _, b = net.get(PAGE)
    html = b.decode('utf-8', 'replace')
    m = re.search(r'id="publicDataDetailPk"[^>]*value="(uddi:[0-9a-f-]+)"', html)
    u = re.search(r'id="updtDt"[^>]*value="([^"]+)"', html)
    rows_n = re.search(r'전체 행</strong>\s*<[^>]+>\s*([\d,]+)', html)
    if not m:
        return finish(run, '파일 쪽에서 publicDataDetailPk를 못 찾음 — 쪽 모양이 바뀜', dry)
    dpk, updt = m.group(1), (u.group(1) if u else '')
    run.update({'detailPk': dpk, 'updtDt': updt, 'pageRows': int(rows_n.group(1).replace(',', '')) if rows_n else None})
    old = json.load(open(os.path.join(OUT, 'latest.json'), encoding='utf-8')) if os.path.exists(os.path.join(OUT, 'latest.json')) else {}
    if old and old.get('source', {}).get('updtDt') == updt and not dry:
        run['ok'] = True
        return finish(run, f'고친 때 그대로({updt}) — 받지 않음', dry)
    time.sleep(1.5)
    st, _, b = net.get(SEL, {'publicDataPk': PK, 'publicDataDetailPk': dpk, 'fileDetailSn': '1'}, ref=PAGE)
    t = b.decode('utf-8', 'replace')
    fid = re.search(r'"atchFileId"\s*:\s*"([^"]+)"', t)
    fsn = re.search(r'"fileDetailSn"\s*:\s*"?(\d+)', t)
    if not fid:
        return finish(run, '내려받기 값(atchFileId)을 못 찾음 — 받는 길이 바뀜', dry)
    time.sleep(1.5)
    st, hd, raw = net.get(DOWN + '?' + urllib.parse.urlencode({'atchFileId': fid.group(1), 'fileDetailSn': fsn.group(1) if fsn else '1', 'insertDataPrcus': 'N'}), ref=PAGE)
    txt = enc = None
    for e in ('utf-8-sig', 'cp949'):
        try:
            txt, enc = raw.decode(e), e
            break
        except UnicodeDecodeError:
            pass
    if txt is None:
        return finish(run, '파일 글자를 못 읽음(utf-8·cp949 아님)', dry)
    rows = [r for r in csv.reader(io.StringIO(txt)) if any(c.strip() for c in r)]
    head, body = [c.strip() for c in rows[0]], rows[1:]
    run.update({'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'encoding': enc, 'rows': len(body)})
    prob = []
    if head != HEAD:
        prob.append(f'머리줄 다름: {head}')
    if run['pageRows'] is not None and run['pageRows'] != len(body):
        prob.append(f"줄 수 {len(body)} ≠ 쪽에 적힌 전체 행 {run['pageRows']}")
    out = []
    for r in body:
        r = (r + [''] * 7)[:7]
        v = num(r[6])
        if v is None or not (500000 <= v <= 20000000):
            prob.append(f'평균등록금 칸 이상: {r[2]} {r[6]!r}')
            continue
        out.append({'type': r[0].strip(), 'found': r[1].strip(), 'name': r[2].strip(), 'region': r[3].strip(),
                    'quota': int(num(r[4]) or 0), 'admFee': num(r[5]), 'tuition': round(v)})
    if prob:
        run['problems'] = prob[:20]
        return finish(run, f'점검 어긋남 {len(prob)} — 저장하지 않음', dry)
    names = {}
    for o in out:
        names.setdefault(o['name'], 0)
        names[o['name']] += 1
    dup = sorted(k for k, n in names.items() if n > 1)
    year = int(updt[:4]) if re.match(r'\d{4}', updt) else None
    res = {'made': now_utc(), 'by': 'scripts/fetch_tuition.py',
           'source': dict(SOURCE, updtDt=updt, sha256=run['sha256'], rows=len(out), fetched=now_utc()[:10]),
           'year': year, 'yearNote': f'{year}년 4월 대학정보공시 기준(파일 등록 {updt[:10]}) · 연간 평균' if year else '',
           'unit': '원(연간 평균 · 소수점 반올림)', 'dupNames': dup, 'rows': out}
    run['ok'] = True
    if not dry:
        os.makedirs(OUT, exist_ok=True)
        json.dump(res, open(os.path.join(OUT, 'latest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    run['sec'] = round(time.time() - t0, 1)
    return finish(run, f"받음 {len(out)}줄 · 고친 때 {updt} · 같은 이름 {len(dup)}", dry)


def finish(run, msg, dry):
    run['msg'] = msg
    print(msg)
    if not dry:
        os.makedirs(OUT, exist_ok=True)
        json.dump(run, open(os.path.join(OUT, 'run.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return 0 if run.get('ok') else 1


if __name__ == '__main__':
    sys.exit(main())
