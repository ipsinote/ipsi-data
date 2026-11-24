# 규정 점검 2026-11-25

규정 60개 · 원문 78곳 중 자동 감시 60곳, 이번에 30곳을 열었습니다 (읽음 30 · 본문 짧아 못 읽음 0 · robots로 안 엶 0 · 못 엶 0).

높음 4 · 보통 5 · 낮음 1 — 높음·보통은 월요일 04:10 자료 점검(v5.11 4i)이 원문을 열어 우리 영향을 판단하고 운영실에 올립니다.

## 높음: 우리가 기대는 사실이 바뀌었을 수 있음 (4)
- Google 검색 검색 스팸 정책(확장된 콘텐츠 악용·도어웨이) — 수정일 Last updated 2026-08-28 → Last updated 2026-11-23 · 새 부분: Some back button hijacking was caused by third-party advertising platforms. Are / Can users report sites that engage in back button hijacking? / Does this policy apply to sites in Google Discover? / Does the back button hijacking policy apply if a user arrives at a website from / Does the back button hijacking policy apply when a website opens an external app
  - 주소: https://developers.google.com/search/docs/essentials/spam-policies?hl=en
  - 관련 규정 R-G1: 구글 검색 — 확장된 콘텐츠 악용(만드는 방법 무관)·도어웨이(지역만 바꾼 비슷한 페이지) 금지
- YouTube Data API videos.insert(업로드) — 수정일 Last updated 2026-11-12 → Last updated 2026-11-23 · 바뀐 부분: Request body
  - 주소: https://developers.google.com/youtube/v3/docs/videos/insert?hl=en
  - 관련 규정 R-YT5: 유튜브 — videos.insert는 '동영상 업로드' 따로 한도 — 1번에 1단위·하루 100번(2026-06-01 분리), 그 밖 기능 하루 10,000단위, 기본 한도 안에서는 감사 불필요. 검증 안 된 프로젝트로 올린 영상도 비공개로 잠기지 않음 — 2026-11-02 개정 기록이 2020-07-28 잠금을 거둠(2026-11-06 확인). 공개 상태를 비우면 '공개'가 기본(계정 설정에 따라 비공개가 기본인 경우도 있음 — 2026-11-02 개정 기록), 예약 공개는 비공개·미공개 영상만
  - 관련 규정 R-YT19: 유튜브 — 협찬·간접광고 등 브랜드와 대가 관계가 있으면 '유료 프로모션' 표시(영상 시작에 라벨), 안 밝히면 삭제·제한·자동 라벨 가능. API 칸 paidProductPlacementDetails.hasPaidProductPlacement — 2026-11-16부터 칸을 빼면 'PPL 없음'으로 선언되지 않음(기본 false가 아님), 없다고 하려면 false를 직접 보냄. videos.insert의 part에 들어 있고 youtube.upload 범위로 넣을 수 있음(2026-11-12 문서)
- YouTube Data API 할당량·감사(업로드 하루 100번 · 감사는 한도를 늘릴 때만) — 수정일 Last updated 2026-11-12 → Last updated 2026-11-23 · 바뀐 부분: Quota and Compliance Audits Stay organized with collections Save and categorize
  - 주소: https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits?hl=en
  - 관련 규정 R-YT5: 유튜브 — videos.insert는 '동영상 업로드' 따로 한도 — 1번에 1단위·하루 100번(2026-06-01 분리), 그 밖 기능 하루 10,000단위, 기본 한도 안에서는 감사 불필요. 검증 안 된 프로젝트로 올린 영상도 비공개로 잠기지 않음 — 2026-11-02 개정 기록이 2020-07-28 잠금을 거둠(2026-11-06 확인). 공개 상태를 비우면 '공개'가 기본(계정 설정에 따라 비공개가 기본인 경우도 있음 — 2026-11-02 개정 기록), 예약 공개는 비공개·미공개 영상만
- YouTube Data API Videos 자료(공개 상태 기본값·예약 공개·아동용·AI 표시·유료 PPL 칸) — 수정일 Last updated 2026-11-17 → Last updated 2026-11-23 · 바뀐 부분: Properties
  - 주소: https://developers.google.com/youtube/v3/docs/videos?hl=en
  - 관련 규정 R-YT3: 유튜브 — 사실처럼 보이는 AI 콘텐츠는 공개 의무. 대본·자막·인포그래픽 보조와 '자기 목소리 복제 음성'은 의무 아님. 스튜디오 '속성 › AI use 예/아니요', API status.containsSyntheticMedia(2024-10-30). 유튜브가 자체 AI 도구·C2PA·내부 감지로 라벨을 붙일 수 있음. 표시만으로 노출·수익 불이익 없음. 2026-05-27부터 사실적 AI 라벨은 쇼츠 화면 위, 덜 사실적·AI 오디오는 설명 안
  - 관련 규정 R-YT5: 유튜브 — videos.insert는 '동영상 업로드' 따로 한도 — 1번에 1단위·하루 100번(2026-06-01 분리), 그 밖 기능 하루 10,000단위, 기본 한도 안에서는 감사 불필요. 검증 안 된 프로젝트로 올린 영상도 비공개로 잠기지 않음 — 2026-11-02 개정 기록이 2020-07-28 잠금을 거둠(2026-11-06 확인). 공개 상태를 비우면 '공개'가 기본(계정 설정에 따라 비공개가 기본인 경우도 있음 — 2026-11-02 개정 기록), 예약 공개는 비공개·미공개 영상만
  - 관련 규정 R-YT6: 유튜브 — 아동용 여부는 주제·의도한/실제 시청자·아이 대상 캐릭터·노래·말투 등을 함께 봄, '혼합 시청자'도 아동용, 사는 나라와 상관없이 영상마다 지정 의무, 영상 설정이 채널 설정보다 우선, 유튜브가 바꿀 수 있음(영상당 이의 1번), 아동용이면 댓글·알림 벨·카드·최종 화면 등이 꺼짐
  - 관련 규정 R-YT19: 유튜브 — 협찬·간접광고 등 브랜드와 대가 관계가 있으면 '유료 프로모션' 표시(영상 시작에 라벨), 안 밝히면 삭제·제한·자동 라벨 가능. API 칸 paidProductPlacementDetails.hasPaidProductPlacement — 2026-11-16부터 칸을 빼면 'PPL 없음'으로 선언되지 않음(기본 false가 아님), 없다고 하려면 false를 직접 보냄. videos.insert의 part에 들어 있고 youtube.upload 범위로 넣을 수 있음(2026-11-12 문서)

## 보통: 내용이 바뀐 부분이 있음 (5)
- Anthropic Claude Code 변경 기록(예약·클라우드 세션·스킬·hooks·아티팩트) — 바뀐 부분: (첫 부분)
  - 주소: https://code.claude.com/docs/en/changelog
- Anthropic 모델 은퇴 일정 — 바뀐 부분: Overview / Migrating to replacements / Model status / 2026-09-30: Claude Sonnet 4.5 model · 새 부분: 2026-11-23: Claude Opus 4.5 model
  - 주소: https://platform.claude.com/docs/en/about-claude/model-deprecations
- Anthropic claude.ai 앱 변경 기록(프로젝트·메모리·예약·아티팩트·스킬) — 새 부분: November 24, 2026
  - 주소: https://support.claude.com/en/articles/12138966-release-notes
- Anthropic 개발자 플랫폼 변경 기록(모델·스킬·도구·컨텍스트) — 새 부분: November 23, 2026 · 없어진 부분: April 23, 2026
  - 주소: https://platform.claude.com/docs/en/release-notes/overview
- Google 검색 Search Status Dashboard 순위 업데이트 이력 — 바뀐 부분: 2026
  - 주소: https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history
  - 관련 규정 R-G3: 구글 검색 — 스팸·코어 업데이트가 자주 있음(2026년 스팸 업데이트 3·6·8·9월)

## 낮음: 처음 기록·읽지 못함 (1)
- Anthropic 모델 마이그레이션 가이드 목록 — 처음 기록
  - 주소: https://platform.claude.com/docs/en/about-claude/models/migration-guide

## 자동으로 보지 않는 규정 (18) — 월요일 자료 점검이 차례(확인일 + 주기)를 보고 확인
- [대표 확인 · 분기 1회] 네이버 블로그 운영정책(자동화·대량 발행 조항) — 주소 확인 필요: 네이버 고객센터 › 블로그 › 운영정책. 대표가 한 번 열어 주소를 알려 주면 auto로 바꿈
- [AI 확인 · 월 1회] AI 기본법(2026-01-22 시행)·투명성 가이드라인·계도기간
- [AI 확인 · 월 1회] 정보통신망법 개정안(게시자 AI 생성물 표시 의무) 진행
- [AI 확인 · 분기 1회] 추천·보증 등에 관한 표시·광고 심사지침(가상인물·경제적 이해관계)
- [AI 확인 · 분기 1회] 개인정보 보호법·처리방침 작성지침·국외 이전
- [AI 확인 · 분기 1회] 광고성 정보 전송 규정(정보통신망법 제50조, 사전 동의)
- [AI 확인 · 해마다] 학원법(유료 입시 상담·교습 범위)
- [AI 확인 · 해마다] 저작권법(인용·요약, 생성형 AI 저작권 안내서)
- [AI 확인 · 분기 1회] 나이스 교육정보 개방 포털 이용약관·출처 표시
- [대표 확인 · 분기 1회] GED 영재교육종합데이터베이스 이용 정책(서면 동의 없는 DB 구축·영리 이용 금지) — 이용 조건 때문에 자동으로 열지 않음. 대표 결정 대기: 서면 문의
- [대표 확인 · 해마다] 베리타스알파·교육을 비추다 'AI 학습·이용 금지' 표시 — 자동으로 열지 않음. 대표가 기사 하단 문구를 한 번 확인
- [대표 확인 · 해마다] '어디가' 이용약관(대학 입시 결과 정리 보류 항목) — robots로 막힘. 입시 결과 정리를 다시 볼 때만
- [AI 확인 · 분기 1회] ElevenLabs 이용약관·요금제별 상업 이용
- [AI 확인 · 분기 1회] 타입캐스트 이용약관·요금제별 상업 이용
- [대표 확인 · 분기 1회] 서치어드바이저 웹마스터 가이드 › 콘텐츠 가이드라인(스팸 정책·콘텐츠 작성 원칙) — 2026-11-04 대표가 PC 크롬으로 열어 '콘텐츠 가이드라인'의 스팸 정책·콘텐츠 작성 원칙 본문을 대화에 붙여 넣어 확인(이 조사 환경·웹 가져오기 도구는 사이트가 막혀 우회하지 않음). 세부 글 주소는 확인 필요 — 다음 대표 확인 때 주소창 주소를 받으면 채움
- [대표 확인 · 분기 1회] 네이버 책임의 한계와 법적고지(자동화 접속·어뷰징·상표) — 2026-11-23 대표 인쇄본(PDF 2쪽 · 날짜 표기 없음)으로 원문 대조 — 다음 확인은 대표 인쇄 1개(약 2분) + 글자 지문 비교(본문 지문 990e2a1174246d19 · 프로젝트 문서 claude/리서치_38d_네이버_법적고지_대조_1123.md 4절). 주소 = 네이버 페이지 맨 아래 '책임의 한계와 법적고지'. Claude·GitHub 감시는 열지 않음(policy.naver.com의 robots.txt 자리에 HTML 화면이 와서 '못 읽음 = 막힘' — 2026-11-25 확인). 2026-11-04 대표가 본문을 대화에 붙여 넣어 처음 확인
- [대표 확인 · 해마다] 쿠팡 파트너스 이용 약관·활동 가이드(대가 문구·등록 채널) — robots로 자동 읽기 막힘 — 수익화를 정할 때 대표가 로그인해 가이드 확인(지금은 쓰지 않음)
- [AI 확인 · 해마다] 평생교육법 제33조(원격평생교육 신고)·학원법 교습 정의 — 유료 정보 구독 검토용
