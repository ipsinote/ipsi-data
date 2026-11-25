"""학교 종류를 열로 나눈 일정표에서 대상의 열만 읽기 점검(2026-11-26 — 경북 고입전형포털 일정표의 과학고 열을 못 읽던 일).
네트워크 없이 돈다: python scripts/test_table_col.py
"""
import datetime, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import fetch_official as F
T = datetime.date(2026, 11, 26)
fails = []
def check(name, got, want):
    print(('ok  ' if got == want else 'FAIL') + ' ' + name, got if got != want else '')
    if got != want: fails.append(name)

# 경북 일정표와 같은 꼴: '구분'은 세로로 합친 칸, '전기고등학교'는 가로로 합친 칸, '특성화고'는 두 열 · 예비소집 줄은 전기 열 전체를 합침
HTML = '''<html><body><table>
<tr><th rowspan="3">구분</th><th colspan="5">전기고등학교</th><th rowspan="3">후기고(평준화일반고)</th></tr>
<tr><th rowspan="2">산업수요맞춤형고</th><th colspan="2">특성화고</th><th rowspan="2">과학고</th><th rowspan="2">외고·자사고</th></tr>
<tr><th>특별전형</th><th>일반전형</th></tr>
<tr><td>1단계 합격자 발표</td><td>10. 27.(화)</td><td>11. 12.(목)</td><td>-</td><td>10. 30.(금)</td><td>12. 15.(화)</td><td>-</td></tr>
<tr><td>예비소집(학교별)</td><td colspan="5">필요 시 학교별 시행</td><td>-</td></tr>
<tr><td>합격자 발표</td><td>11. 4.(수)</td><td>11. 17.(화)</td><td>12. 1.(화)</td><td>11. 30.(월)</td><td>12. 24.(목)</td><td>’27. 1. 5.(화)</td></tr>
<tr><td>합격자 등록</td><td>11. 4.(수)~11. 5.(목)</td><td>11. 17.(화)∼11. 18.(수)</td><td>12. 1.(화)∼12. 2.(수)</td><td>11. 30.(월)∼12. 2.(수)</td><td>12. 24.(목)∼12. 29.(화)</td><td>-</td></tr>
</table></body></html>'''
NEAR = ['과학', '1단계', '합격', '발표', '면접']

soup = F.soup_of(HTML)
got = F.table_col_lines(soup, '과학고', NEAR, T, 'x')
check('① 과학고 열 줄 3개', [l['text'] for l in got], ['1단계 합격자 발표 | 과학고 | 10. 30.(금)', '합격자 발표 | 과학고 | 11. 30.(월)', '합격자 등록 | 과학고 | 11. 30.(월)∼12. 2.(수)'])
check('② 과학고 합격자 발표 날짜 = 2026-11-30', [l['dates'] for l in got if l['text'].startswith('합격자 발표')], [['2026-11-30']])
check('③ 다른 열 날짜(11. 4. · 12. 24.) 섞이지 않음', sorted({d for l in got for d in l['dates']} & {'2026-11-04', '2026-12-24'}), [])
check('④ 열 이름이 없는 표는 0줄', F.table_col_lines(F.soup_of('<table><tr><td>원서</td><td>10. 1.(목)</td></tr></table>'), '과학고', NEAR, T, 'x'), [])

# ⑤ read_post_html: col이 있으면 그 쪽 줄을 열 줄로 바꿈 · 없으면 예전 그대로
class _F:
    ocr_left = 0
    debug = []
res = {'lines': [], 'files': [], 'titles': [], 'opened': []}
F.read_post_html(_F(), HTML, 'https://example.org/x', {'id': 't', 'near': NEAR, 'col': '과학고'}, T, res, depth_files=False)
check('⑤ col 있음 → 과학고 열 줄만', [l['text'] for l in res['lines']], [l['text'] for l in got])
res2 = {'lines': [], 'files': [], 'titles': [], 'opened': []}
F.read_post_html(_F(), HTML, 'https://example.org/x', {'id': 't', 'near': NEAR}, T, res2, depth_files=False)
check('⑥ col 없음 → 예전 글 줄 읽기 그대로', [l['text'] for l in res2['lines']], [l['text'] for l in F.date_lines(F.visible_text(F.soup_of(HTML)), NEAR, T, 'https://example.org/x')])

print('FAILS', len(fails))
sys.exit(1 if fails else 0)
