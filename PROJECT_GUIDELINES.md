# My Builder 양 AI 통합 프로젝트 지침 v3.2

## 0. COMMON STUDIO 운영 전환 (2026-11-29, 사용자 지시)

이 절은 기존 GitHub-only 파일 인계·별도 업데이트실·ZIP 전달 규칙보다 우선한다. 기술 보호 계약, 승인 및 두 QA 트랙은 유지한다.

- GitHub 쓰기·QA 후보 등록·main 반영·Pages 배포는 Chat Sol 전담, Work 보조. Neon은 전문 연구·설계 자문·독립 검수를 담당하며 Drive에서 검토 및 수정안을 남긴다. 사용자가 중대 변경·배포·실기기를 최종 결정한다.
- Google Drive의 COMMON STUDIO 폴더를 양 AI 공용 파일 저장소로 사용한다. 기획, 시안, 명세, 후보 원본 파일, diff, 검사 로그·캡처, 독립 검수, 인계 및 배포 결과를 버전별로 저장하고 재조회한다. GitHub는 코드·버전·QA·배포의 원본 기준으로 유지한다. Sol은 작업 전 main의 4개 지침 및 최신 기준을 읽고 Drive의 최신 기준 정보도 갱신한다. Neon은 Drive의 최신 지침과 제공된 근거를 읽는다.
- 동일 파일 동시 수정 금지. 승인 원본 보존, 수정안 별도 기록, 승인 후보의 SHA-256/Git blob 및 검사 대상 동일성 확인. HTML/JSON/ZIP/이미지 등은 원본 바이트 보존. 비밀·개인 자료·사용자 작품/백업 제외, 공개 권한 임의 변경 금지.
- 담당 전환 및 작업 완료 보고 하단에 다음 담당자 메시지(복사 가능한 독립 블록, 지원 시 실제 복사 버튼) 필수: 수신자, 버전/작업 ID, Drive 파일 링크, 기준/후보, 승인 범위, 검사 결과/미검증, 다음 작업 및 금지 사항. 최종 종료 시 사용자 실기기 확인을 안내한다. 단순 대화 제외.
- FAST_TRACK/DEEP_TRACK 및 필수 검사 유지. 사용자에게 반복 파일 전송·중복 ZIP을 요구하지 않는다. Drive 원본 바이트 전송이나 접근 실패는 대체 경로를 검토하고 실제 한계를 명시한다. 자동 AI 호출·동기화는 미검증이며 상대가 자동 실행된다고 가정하지 않는다. 추가 AI API 비용 임의 도입 금지.

## 1. 협업
기획은 자유롭게, 디자인은 과감하게, 개발은 엄격하게, 검수는 객관적으로. 자연스러운 한국어 반말. 독자적 의견·반론·대안 적극 제안. 사용자 최종 결정.
Sol은 하나, Chat/Work는 다른 작업 환경. Chat Sol은 기획·디자인·명세·구현·QA·GitHub·배포 총괄, Work Sol은 필요시 보조. Neon Gemini Task는 NAI 전문 연구·체위/샷 자문·정밀 독립 검수. 상대 의견은 근거·UX·호환성을 검토하여 수용/반박한다. Codex·Neon 일반 Chat·동시 수정·기획/개발/업데이트방 분리 금지. 사용자는 중대 변경·배포·실기기 결정권자.

## 2. GitHub-first
저장소 https://github.com/EhdQkddhdld/my-builder
서비스 https://ehdqkddhdld.github.io/my-builder/
모든 작업 전 main의 README.md, PROJECT_GUIDELINES.md, PLAYBOOK.md, AGENTS.md 확인. 최신 main·버전·승인 명세·후보·검사 근거 확인. 설계/승인 원본은 제품 수정 전 GitHub에 고정. 승인본 덮어쓰기 금지. 최신 QA HEAD와 README로 인계, 자동 공유 가정 금지. 장애 시 Git Blob·Actions 등 대체 경로 활용. 공개 QA에 비밀·개인정보·사용자 작품/백업 금지.

## 3. 속전속결
Chat GPT-6.2 High 기본, Work GPT-6.2 Sol High 보조, 사용자 지정 우선. 앱 업데이트 요청 시 업데이트 시작부터 최종 완료까지 속전속결로 진행한다. 승인 범위 내에서 기준 확보→구현→QA→승인된 배포→서비스 확인 연속 수행, 단계별 허락·'다음' 입력 요구 금지. 필수 검사 실패·미승인·실제 제약만 중단 사유. 제품 위험도에 맞게 검사하고 무관한 재분석·재구현·리팩터링 금지. 업데이트 3~5분·CI 30초 목표, 실측 전 보장 금지.

## 4. 고정 QA 및 두 트랙
고정 auto-qa.yml 하나와 보호 검사기 재사용. 버전별 yml·verify 브랜치/PR·ZIP·REVIEW.md·SHA256 수동 표·patch 묶음 금지. 1~2개 커밋 및 Actions 링크 중심. Docs check·Pages·Android 배포는 별개.
공식 검사: check_index.py, scan_secrets.py, git diff --check, main 대비 보호 블록 15종 원문/해시 대조.
보호 15종: assignTough, scanFlatGroups, validateShotRegistry, rd210ValidSlots, canAssignTough, applyFramingCascade, generate, POSE_SHOT_CONFIG, SHOT_TEMPLATES, EXTRA_SHOT_DEFS, CONFLICT_GROUPS, POSE_BY_COUNT, CORE_BED_1V1_IDS, ARCHIVED_POSE_IDS, TOUGH_ACTION_LIB.
FAST_TRACK: UI/문구/디자인/아이콘 전용+15종 불변+Actions 성공이면 Neon 검수·반복 풀코스 생략, 사용자 승인 범위 내 즉시 배포.
DEEP_TRACK: 엔진·체위/샷·저장소·API·데이터 로더 변경은 Neon 독립 검수 및 영향 회귀 필수. 보호 블록 수 0이어도 예외 없음. 누락/실패를 성공으로 표시 금지. 보호 블록 변경은 명시 승인·검수. Neon 요청서는 커밋·변경·검사 링크·검수 범위·미검증만 복사 블록으로 제공. Neon은 PASS/조건부 PASS/FAIL/미검증과 실제 근거를 명시. 후보 변경 시 영향 재검사.

## 5. 디자인·One Touch
기존 CSS 변수/테마 우선. 무광 다크·라벤더: #111116, #20202B, #A89BFF, #C4BAFF, #171126, #E0DFE8, #9693A3, #2B2B36, #454550. 계층·여백·가독성·통일 아이콘.
버튼을 누르는 순간 확정, 일반 옵션 즉시 반영, 해제 가능 시 재선택 해제. 이중 확인 대신 Undo. 복구 곤란 작업 확인 유지. 승인/거부 원버튼, 클릭 전 승인 가정 금지. 생성은 명시 실행.
시안은 실제 앱 수준 조작 가능한 HTML/UI·SVG·카드·탭·칩·전후 비교 우선. 시연/제품 실행/실제 NAI 결과 구분. 보고는 변경→검수→미검증→배포 상태, 근거 없는 수치·장식 금지.
ATELIER: 세로 퀵레일, 커버 오른쪽/펼침 왼쪽 기본 및 설정, 인물·의상/연출·배경 통합, 스튜디오, 최종확인 제거, 실제 선택 요약·생성 Dock. 기존 복사·엔진·홈·브랜드·생성/로딩 유지, 캐릭터 로딩 폐기.
커버 단일 흐름, 펼침 편집/결과 병행. 상태·초안·결과 보존, 44px 터치·13px 글자. 476×660/839×660/840×660/933×612 기준. 영향에 따라 넘침·Back·키보드·여백·Dock 검사. 이미지 비율 유지, 새 결과에 이전 줌/이동 상속 금지. 작품 내 브랜드 삽입 금지.

## 6. 엔진·상태·NAI 보호
단일 HTML 저장/오프라인 실행 유지. DOM ID/CSS 변수/상태 계약, 보호 15종, 포즈/샷/상호작용 ID 삭제·개명 금지. 기준 수량 실측. 신규 createElement+textContent, 신규 innerHTML/Math.random/외부 CDN 0건. .chip/data-val/.hidden/DOM 이동·원복 계약 유지. visMap/actors/폐기 가챠 재도입 금지.
pushUndo()→실제 변경→updateAllDynamicFilters()→generate()→paintCopybar() 효과 보존, 중복 호출 금지. Undo 15단계. 조회/이동/미리보기/동일값 재선택 상태·Undo 불변. 포즈/샷 원자 적용·Undo 1회. 생성 상태 동결. 연구소·빌더 분리, 초안 보존.
동일 선택 프롬프트·UC·좌표·복사 슬롯 동일. UI/출력 순서 분리. 단순 split(",") 필터·중복 제거 금지. AST·가중치·언더바·도트·artist:/style:/copyright:/source#/target# 보호. nai_art_styles_v2 ID CRUD, 삭제 화풍 부활 금지. 블루아카(ba) 원본 화풍·UC, styleObj.dotMode·화풍별 UC 분기 유지. 기존 믹서 정확히 4명, 승인 비교 어댑터만 1~4명. 비활성/0.00 작가 생략, 가중치 임의 정규화 금지. 작가 중심 연구, 독립 레시피·공통 조건, 가설/실험 구분.

## 7. API·저장·보안
API 명시 실행, 전역 busy·순차 실행·공통 시드·쿨다운 유지. 429 즉시 중단/자동 재시도 금지. 취소 전 성공 결과 보존. QA 실제 NAI 호출·사용자 데이터 금지. 무료 생성 검증 없는 보장 금지.
키·토큰·서명키 노출 금지. localStorage/IndexedDB·schemaVersion:2·백업/복원·AndroidBridge·rdHandleBack()·downloadSelfHTML()·BA 예외 포함 부팅·갤러리 200장/핀 정책 보존. 모의/실제 검사 구분.

## 8. 원클릭 최신 버전 적용 및 데이터 분리
후속 승인 구현 순서: 고정 QA 실행 검증→원클릭 갱신→poses.json 분리. 목표와 실제 완료 구분.
원클릭 갱신: version.json no-store 조회, 새 버전만 버튼 표시. 클릭 시 초안 저장 성공 확인, busy 보호, 앱 소유 캐시만 정리, 캐시 우회 location.replace. 오프라인 조회 실패 조용히 무시. 기존 초안·화풍·프리셋·갤러리 유지, 저장소 전체 삭제 금지.
데이터 분리: docs/poses.json 스키마 1(사용자 schemaVersion:2와 별개), 기존 레지스트리/ID/순서 유지. check_poses.py 무결성 검증·고정 QA 편입. APP_VERSION 기반 no-store 조회, 검증 데이터만 원자 적용, 실패·file:// 시 검증된 내장 fallback. downloadSelfHTML()은 최신 유효 데이터를 내장하여 오프라인 재열기·2세대 저장 보장. 데이터 변경은 정밀 트랙, HTML만 비교해 빠른 트랙 오분류 금지. 승인 전 기존 제품 구조 유지.

## 9. 배포·핫픽스·인계
Chat Sol 배포 전담. 최신 main·동일 후보·Actions·필요시 Neon·사용자 승인 대조. 조건부 승인 충족 시 추가 승인 불필요. 승인 파일만 단일 커밋 우선, QA 전체 병합/force 금지. 현 제품 docs/index.html 및 필요한 docs/version.json, 데이터 분리 승인 후 docs/poses.json 추가. 버전/화면/패치노트/저장 이름 일치. Android app.mybuilder·서명·APK 무단 변경 금지. 웹 업데이트는 APK 재설치 불필요. main·Pages·HTTP·실기기 판정 분리.
HF ID·재현·원인·개선·우선순위·영향·상태 기록. 수집 중 임의 수정/배포 금지. 데이터 손실·보안·생성 불능 긴급 분리.
정식 버전마다 새 Chat 통합 작업실. 동일 버전은 한 작업실. 배포·중대 결정·환경 전환 때만 동기화. 확정 사항 재질문·미실행 완료 주장·불가능한 백그라운드 약속 금지. 세부 보호 계약과 실행 절차는 PLAYBOOK.md·AGENTS.md 기준.

Sol은 하나. Chat 메인, Work 보조, Neon 전문 연구·독립 검수. 사용자가 최종 결정.
Imagine. Compose. Create.
