"""공식 누리집 robots 판정 파일 — 매일 깃허브가 robots.txt를 읽어 '우리 이름'에 걸리는 규칙만 파일로 남긴다.

    python scripts/robots_status.py data/robots_status.json

까닭(2026-11-23 대표 대화 버튼 'A 깃허브가 읽고 예약은 결과 파일만' — 운영실 asks/ask-dec-permwait-1123):
  예약(무인) 실행의 웹 열기(WebFetch)는 robots.txt 주소를 열 때 허락을 기다리다 멈췄다(11/17~11/20 낮 작업 4번).
  그래서 깃허브가 대신 읽고, 예약·대화 창은 이 파일(공개 주소 raw.githubusercontent.com)만 받아 판정한다
  — 판정 도구는 ipsi-site tools/robots_allow.py(같은 규칙).

읽는 곳(누리집 origin = scheme://host):
  watch/robots_hosts.json(손으로 더한 곳 — ipsi-site 허락 목록 등) + watch/targets.json·targets_auto.json(공식 공고 읽기 대상)
  + watch/sources.json(출처 대장). 열지 않는 곳(공통 규칙 4절 — GED·대학어디가·언론·학원)은 뺀다.
남기는 것: 곳마다 받은 때·http 코드·종류·지문(sha 앞 8자)·우리 이름에 걸리는 규칙(star = '*' 묶음 · named = 이름 묶음).
  robots.txt 전체 글은 남기지 않는다.
판정 규칙(공통 규칙 4절 '자동 읽기 막힘·AI 봇 이름으로 막은 공식 기관' · fetch_official.py robots 판정과 같음):
  ① 종류 none(4xx — robots 없음) = 열림 · denied(401·403)·unreachable(5xx·429·연결 실패)·html(규칙 파일이 아닌 화면)·
     ambiguous(30일 안에 우리를 막는 규칙을 본 곳이 이번에 없음·화면으로 답함) = 막힘
  ② 종류 rules — 누가 여나에 따라 둘로 판정한다:
     web(대화 창·예약의 웹 열기 — Claude-User): claude-user 이름 묶음(없으면 '*')이 허용하고, 옛 이름(claude-web·anthropic-ai)·
       claude-searchbot은 이름 묶음이 있을 때만 그 묶음도 허용해야 열림
     bot(수집기 ipsi-data-bot): ipsi-data-bot 이름 묶음(없으면 '*')이 허용해야 열림
  ③ 규칙 해석은 RFC 9309(* · $ · 같은 이름 묶음 합치기 · 가장 긴 규칙 · 길이가 같으면 막힘)
"""
import datetime
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_official as fo  # noqa: E402

TOKENS_MAIN = ['claude-user', 'ipsi-data-bot']                    # 이름 묶음이 없으면 '*'를 따름
TOKENS_OLD = ['claude-web', 'anthropic-ai', 'claude-searchbot']   # 이름 묶음이 있을 때만 봄
TOKENS = TOKENS_MAIN + TOKENS_OLD
SKIP = ['ged.kedi', 'adiga', 'ipsinote.com', 'veritas-a', 'kyobit', 'newsis', 'hankyung', 'mt.co.kr', 'asiae', 'nocutnews',
        'gnnews', 'khan.co.kr', 'etoday', 'kyosu', 'dhnews', 'thesegye', 'kbmaeil', 'kyeonggi', 'kukinews', 'dailypharm',
        'heraldk', 'supple.kr', 'negagea', 'sanedu']
MEMORY_DAYS = 30
TIMEOUT = 10
PAUSE = 0.3
WORKERS = 8   # 누리집마다 한 번만 받으니 여러 곳을 함께(같은 곳을 두 번 부르지 않음) — 11/23 첫 실행이 한 줄로 12분 넘게 걸림


def kst_now():
    return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)


def origin(u):
    p = urllib.parse.urlsplit(str(u or '').strip())
    if p.scheme not in ('http', 'https') or not p.netloc:
        return ''
    return p.scheme + '://' + p.netloc.lower()


def skipped(o):
    return any(s in o for s in SKIP)


def _pages(t):
    for x in (t if isinstance(t, list) else (t or {}).get('targets', [])):
        for pg in x.get('pages', []) or []:
            yield pg.get('url', '')


def load_hosts(watch_dir='watch'):
    """(origin 목록, 어디서 왔나 {origin: [출처 이름]})"""
    got = {}

    def add(u, why):
        o = origin(u)
        if o and not skipped(o):
            got.setdefault(o, set()).add(why)

    def jload(name):
        try:
            return json.load(open(os.path.join(watch_dir, name), encoding='utf-8'))
        except (OSError, ValueError):
            return None

    hx = jload('robots_hosts.json') or {}
    for u in (hx.get('hosts') if isinstance(hx, dict) else hx) or []:
        add(u, 'hosts')
    for name in ('targets.json', 'targets_auto.json'):
        for u in _pages(jload(name)):
            add(u, 'targets')
    src = jload('sources.json') or {}
    for it in (src.get('sources') if isinstance(src, dict) else src) or []:
        add(it.get('url', ''), 'sources')
    return sorted(got), {k: sorted(v) for k, v in got.items()}


def named_groups(groups, token):
    """이름 묶음만(같은 이름 묶음은 합침) — 없으면 None. 이름 견주기는 fetch_official.robots_rules_for와 같음(이름 일부도 걸림 · 안전한 쪽)."""
    def mine(a):
        return a != '*' and a and (a.split('/')[0] == token or a in token)
    pick = [g for g in groups if any(mine(a) for a in g[0])]
    if not pick:
        return None
    return [r for g in pick for r in g[1]]


def star_rules(groups):
    return [r for g in groups if '*' in g[0] for r in g[1]]


def pack(rules):
    return [[1 if a else 0, p] for a, p in rules]


def rules_of(entry, token):
    """판정에 쓸 규칙 — 이름 묶음이 있으면 그것, 없으면 주 이름은 '*' · 옛 이름은 None(보지 않음)."""
    named = (entry.get('named') or {}).get(token)
    if named is not None:
        return [(bool(a), p) for a, p in named]
    if token in TOKENS_MAIN:
        return [(bool(a), p) for a, p in entry.get('star') or []]
    return None


WHO = {'web': ['claude-user'] + TOKENS_OLD, 'bot': ['ipsi-data-bot']}


def verdict(entry, url, who='web'):
    """(열림 True/False, 까닭) — who: web(웹 열기 Claude-User) · bot(수집기). 까닭: none · rules · rules-blocked:<이름> · denied · unreachable · html · ambiguous"""
    kind = entry.get('kind')
    if kind == 'none':
        return True, 'none'
    if kind != 'rules':
        return False, kind or 'unknown'
    for t in WHO[who]:
        rl = rules_of(entry, t)
        if rl is not None and not fo.robots_rfc_allowed(rl, url):
            return False, 'rules-blocked:' + t
    return True, 'rules'


def blocks_us(entry):
    """우리 이름에 걸리는 규칙에 Disallow가 하나라도 있나(30일 기억용)."""
    for t in TOKENS:
        rl = rules_of(entry, t)
        if rl and any(not a for a, _ in rl):
            return True
    return False


def read_one(session, o):
    """robots.txt 하나 → 기록(dict). 네트워크는 session.get 하나만."""
    at = kst_now().isoformat(timespec='minutes')
    try:
        r = session.get(o + '/robots.txt', timeout=TIMEOUT)
    except Exception as e:  # requests 오류 모두
        return {'at': at, 'http': 'error', 'kind': 'unreachable', 'error': str(e)[:100]}
    e = {'at': at, 'http': r.status_code}
    if getattr(r, 'url', None) and r.url != o + '/robots.txt':
        e['final'] = r.url[:160]
    if r.status_code in (401, 403):
        e['kind'] = 'denied'; return e
    if r.status_code == 429 or r.status_code >= 500:
        e['kind'] = 'unreachable'; return e
    if r.status_code >= 400:
        e['kind'] = 'none'; return e
    raw = r.content[:fo.ROBOTS_MAX]
    text = raw.decode('utf-8', 'replace').lstrip('﻿')
    groups = fo.robots_groups(text)
    head = text.lstrip()[:2048]
    looks_html = head[:1] == '<' or bool(re.search(r'<\s*(!doctype|html|head|body|script|meta)\b', head, re.I))
    ctype = (r.headers or {}).get('Content-Type', '').lower()
    html = looks_html or ('html' in ctype and not groups and bool(text.strip()))
    e['sha'] = hashlib.sha1(r.content).hexdigest()[:8]
    e['bytes'] = len(r.content)
    if html:
        e['kind'] = 'html'; return e
    e['kind'] = 'rules'
    e['star'] = pack(star_rules(groups))
    named = {}
    for t in TOKENS:
        n = named_groups(groups, t)
        if n is not None:
            named[t] = pack(n)
    if named:
        e['named'] = named
    return e


def apply_memory(e, prev, today):
    """30일 기억 — 우리를 막는 규칙을 본 날(blockAt)을 이어 적고, 그 뒤 '없음'·화면 답은 애매(막힘)로."""
    block_at = (prev or {}).get('blockAt')
    if e.get('kind') == 'rules' and blocks_us(e):
        block_at = today.isoformat()
    if e.get('kind') in ('none', 'html') and block_at:
        try:
            if (today - datetime.date.fromisoformat(block_at)).days <= MEMORY_DAYS:
                e['kind'] = 'ambiguous'
        except ValueError:
            pass
    if block_at:
        try:
            if (today - datetime.date.fromisoformat(block_at)).days <= MEMORY_DAYS:
                e['blockAt'] = block_at
        except ValueError:
            pass
    return e


def main(out_path, watch_dir='watch', session=None, pause=PAUSE, workers=WORKERS):
    try:
        old = json.load(open(out_path, encoding='utf-8'))
    except (OSError, ValueError):
        old = {}
    prev = old.get('hosts') or {}
    hosts, why = load_hosts(watch_dir)
    if session is None:
        import requests
        session = requests.Session()
        session.headers.update({'User-Agent': fo.UA})
        session.mount('https://', requests.adapters.HTTPAdapter(pool_connections=WORKERS * 2, pool_maxsize=WORKERS * 2))
        session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=WORKERS * 2, pool_maxsize=WORKERS * 2))
    today = kst_now().date()
    out, count = {}, {}

    def one(o):
        e = read_one(session, o)
        if pause:
            time.sleep(pause)
        return o, e

    if workers > 1:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=workers) as ex:
            got = dict(ex.map(one, hosts))
    else:
        got = dict(one(o) for o in hosts)
    for o in hosts:
        e = apply_memory(got[o], prev.get(o), today)
        e['from'] = why.get(o, [])
        out[o] = e
        count[e['kind']] = count.get(e['kind'], 0) + 1
    doc = {'checkedAt': kst_now().isoformat(timespec='minutes'),
           'ua': fo.UA, 'tokens': {'main': TOKENS_MAIN, 'old': TOKENS_OLD},
           'note': '공식 누리집 robots 판정(우리 이름·* 규칙만) — 판정 도구 ipsi-site tools/robots_allow.py · 규칙 scripts/robots_status.py 머리말',
           'summary': dict(sorted(count.items()), hosts=len(out)),
           'hosts': out}
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    json.dump(doc, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=False)
    print('robots 판정', json.dumps(doc['summary'], ensure_ascii=False))
    return doc


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'data/robots_status.json')
