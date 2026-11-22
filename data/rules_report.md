# 규정 점검 2026-11-22

규정 60개 · 원문 71곳 중 자동 감시 53곳, 이번에 46곳을 열었습니다 (읽음 44 · 본문 짧아 못 읽음 1 · robots로 안 엶 1 · 못 엶 0).

높음 4 · 보통 5 · 낮음 3 — 높음·보통은 월요일 04:10 자료 점검(v5.11 4i)이 원문을 열어 우리 영향을 판단하고 운영실에 올립니다.

## 높음: 우리가 기대는 사실이 바뀌었을 수 있음 (4)
- Cloudflare Cloudflare Pages 한도 — 수정일 Last updated Sep 5, 2026 → Last updated Nov 19, 2026 · 바뀐 부분: Preview deployments · 새 부분: Deployments
  - 주소: https://developers.cloudflare.com/pages/platform/limits/
  - 관련 규정 R-T3: Cloudflare Pages — 정적 요청 무료·무제한, 빌드 월 500회, 파일 2만 개·25MiB(상업 이용 문구는 확인 필요)
- Vercel Fair use guidelines(Hobby 비상업) — 감시 낱말이 사라짐: commercial · 바뀐 부분: (첫 부분)
  - 주소: https://vercel.com/docs/limits/fair-use-guidelines
  - 관련 규정 R-T1: Vercel — Hobby(무료)는 비상업 전용
- YouTube Data API 개정 이력 — 수정일 Last updated 2026-11-12 → Last updated 2026-11-17 · 새 부분: November 16, 2026 · 없어진 부분: March 16, 2016
  - 주소: https://developers.google.com/youtube/v3/revision_history?hl=en
  - 관련 규정 R-YT5: 유튜브 — videos.insert는 '동영상 업로드' 따로 한도 — 1번에 1단위·하루 100번(2026-06-01 분리), 그 밖 기능 하루 10,000단위, 기본 한도 안에서는 감사 불필요. 검증 안 된 프로젝트로 올린 영상도 비공개로 잠기지 않음 — 2026-11-02 개정 기록이 2020-07-28 잠금을 거둠(2026-11-06 확인). 공개 상태를 비우면 '공개'가 기본, 예약 공개는 비공개·미공개 영상만
- YouTube Data API Videos 자료(공개 상태 기본값·예약 공개·아동용·AI 표시 칸) — 수정일 Last updated 2026-11-12 → Last updated 2026-11-17 · 바뀐 부분: Properties
  - 주소: https://developers.google.com/youtube/v3/docs/videos?hl=en
  - 관련 규정 R-YT3: 유튜브 — 사실처럼 보이는 AI 콘텐츠는 공개 의무. 대본·자막·인포그래픽 보조와 '자기 목소리 복제 음성'은 의무 아님. 스튜디오 '속성 › AI use 예/아니요', API status.containsSyntheticMedia(2024-10-30). 유튜브가 자체 AI 도구·C2PA·내부 감지로 라벨을 붙일 수 있음. 표시만으로 노출·수익 불이익 없음. 2026-05-27부터 사실적 AI 라벨은 쇼츠 화면 위, 덜 사실적·AI 오디오는 설명 안
  - 관련 규정 R-YT5: 유튜브 — videos.insert는 '동영상 업로드' 따로 한도 — 1번에 1단위·하루 100번(2026-06-01 분리), 그 밖 기능 하루 10,000단위, 기본 한도 안에서는 감사 불필요. 검증 안 된 프로젝트로 올린 영상도 비공개로 잠기지 않음 — 2026-11-02 개정 기록이 2020-07-28 잠금을 거둠(2026-11-06 확인). 공개 상태를 비우면 '공개'가 기본, 예약 공개는 비공개·미공개 영상만
  - 관련 규정 R-YT6: 유튜브 — 아동용 여부는 주제·의도한/실제 시청자·아이 대상 캐릭터·노래·말투 등을 함께 봄, '혼합 시청자'도 아동용, 사는 나라와 상관없이 영상마다 지정 의무, 영상 설정이 채널 설정보다 우선, 유튜브가 바꿀 수 있음(영상당 이의 1번), 아동용이면 댓글·알림 벨·카드·최종 화면 등이 꺼짐

## 보통: 내용이 바뀐 부분이 있음 (5)
- Google 검색 Search Status Dashboard 순위 업데이트 이력 — 바뀐 부분: 2021
  - 주소: https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history
  - 관련 규정 R-G3: 구글 검색 — 스팸·코어 업데이트가 자주 있음(2026년 스팸 업데이트 3·6·8·9월)
- Meta Threads API Posts — 바뀐 부분: (첫 부분)
  - 주소: https://developers.facebook.com/docs/threads/posts
  - 관련 규정 R-TH1: 스레드 — API 게시 24시간 250개, 고급 권한 전엔 테스터 계정만, 링크 5개 넘으면 오류
- AWS CloudFront 정액제 문서 — 바뀐 부분: CloudFront flat-rate pricing plans / Pricing plan features / What happens when usage exceeds the allowance / Subscribe an existing distribution to a pricing plan / Cancel a pricing plan / Deleting a distribution with a pricing plan · 새 부분: Topics
  - 주소: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/flat-rate-pricing-plan.html
  - 관련 규정 R-T4: AWS CloudFront — 정액제 Free: 월 요청 100만·전송 100GB, 초과 요금 없음
- GitHub GitHub Actions 과금(비공개 저장소 무료 한도) — 바뀐 부분: GitHub Actions billing / How use of GitHub Actions is measured / Examples of how usage is measured / Paying for additional GitHub Actions use / Baseline minute costs · 새 부분: Copilot code review and GitHub Actions usage / Included compute usage and storage / Using more than your included compute usage / Example additional runner cost calculation · 없어진 부분: Copilot code review and GitHub Actions minutes / Free use of GitHub Actions / Using more than your included quota / Example minutes cost calculation for GitHub-hosted runners
  - 주소: https://docs.github.com/en/billing/concepts/product-billing/github-actions
  - 관련 규정 R-T5: GitHub Actions — 공개 저장소 무료, 비공개는 월 2,000분 무료 안
- X X API 요금 — 새 부분: Credit consumption details / Read operations / Write operations / Webhook events / Owned Reads / Deduplication · 없어진 부분: ​ Credit consumption details / ​ Read operations / ​ Write operations / ​ Webhook events / ​ Owned Reads / ​ Deduplication
  - 주소: https://docs.x.com/x-api/getting-started/pricing
  - 관련 규정 R-X1: X — X API는 유료(글·링크 글 요금)

## 낮음: 처음 기록·읽지 못함 (3)
- 네이버 네이버 클립 등록 예약·비공개 예약 안내(클립 고객센터) — 본문이 짧아 자동으로 읽지 못함(직접 확인·월요일 자료 점검이 원문 확인)
  - 주소: https://help.naver.com/service/30048/contents/25177
  - 관련 규정 R-NV4: 네이버 클립 — 업로드 API 없음(PC 웹 예약), 낭독형·반복 업로드·AI 미표기가 경고 사유로 거론
- 네이버 네이버 이용약관 — robots.txt가 막아 열지 않음 → 직접 확인으로 다룸
  - 주소: https://policy.naver.com/rules/service.html
  - 관련 규정 R-NV1: 네이버 블로그 — 글쓰기 API 2020-05-06 종료, 기계적 대량 발행은 운영정책 위반
  - 관련 규정 R-NV2: 네이버 — 'AI 활용' 표시는 블로그·클립 권장(쇼핑라이브만 의무)
  - 관련 규정 R-NV6: 네이버 — 책임의 한계와 법적고지: 매크로·봇·크롤러·스크래퍼 같은 자동 수단으로 접속·수집 금지(명시 허락·공식 API·robots 허용 범위만 예외 — 어기면 정보통신망법상 무단 접근·업무방해가 될 수 있다고 밝힘), 보상을 걸고 클릭·검색·구독을 끌어오는 행위 금지, 네이버 이름·로고는 허락 없이 상표로 쓰지 않음
- YouTube 쇼츠에 관련 동영상 추가(쇼츠 → 내 채널 영상 링크) — 처음 기록
  - 주소: https://support.google.com/youtube/answer/14075157?hl=en
  - 관련 규정 R-YT8: 유튜브 — 쇼츠에 '관련 동영상'을 걸면 채널 이름 아래 눌리는 링크가 생김 — 내 채널의 공개·일부 공개 영상만, YouTube Studio 웹에서 설정, 고급 기능 사용 설정 필요

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
- [대표 확인 · 분기 1회] 네이버 책임의 한계와 법적고지(자동화 접속·어뷰징·상표) — 2026-11-04 대표가 본문을 대화에 붙여 넣어 확인. 주소 확인 필요 — 네이버 페이지 맨 아래 '책임한계와 법적고지' 링크
- [대표 확인 · 해마다] 쿠팡 파트너스 이용 약관·활동 가이드(대가 문구·등록 채널) — robots로 자동 읽기 막힘 — 수익화를 정할 때 대표가 로그인해 가이드 확인(지금은 쓰지 않음)
- [AI 확인 · 해마다] 평생교육법 제33조(원격평생교육 신고)·학원법 교습 정의 — 유료 정보 구독 검토용
