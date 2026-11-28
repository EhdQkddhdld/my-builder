# My Builder 실행 PLAYBOOK v1.2

## 최우선 운영 전환 — COMMON STUDIO v3.2 (2026-11-29)

PROJECT_GUIDELINES.md 0절을 적용한다. 공유용 시안·명세·후보 원본·QA 근거·독립 검수·인계·배포 결과는 Google Drive COMMON STUDIO에 보관·재조회한다. GitHub 코드·버전·검사·배포 기준은 유지한다. 별도 업데이트실 대신 Chat Sol이 GitHub 쓰기부터 최종 배포까지 전담하고 Neon은 Drive에서 독립 검수한다. 승인 원본 보존·동시 수정 금지·후보 동일성·두 QA 트랙·기술 보호 계약은 유지한다. 모든 담당 전환/완료 보고 하단에 다음 담당자 메시지(복사 가능한 블록, 지원 시 실제 복사 버튼)를 제공한다. 이 절은 아래 과거 역할·GitHub-only 인계·ZIP 전달 규칙보다 우선한다.

## v3.3.0 이후 원클릭 업데이트·데이터 분리 지침 (Neon 설계, 2026-11-28)

목표: 업데이트 3~5분, 고정 CI 단일 job 30초, 체위 데이터 수정 10초, 데이터 검사 5초, Fold8 확인 1분. 실제 측정 전 달성 보장 금지. 개편 등급 L2. 이 지침 등록 자체는 구현 완료나 제품 배포 승인이 아니다.

### 1. 고정 QA와 두 트랙
- 이미 등록된 `.github/workflows/auto-qa.yml`, `tools/check_protected.cjs`를 재사용한다. Neon 원안의 release-gate.yml, check_protected.py는 동일 역할의 제안 파일명이다. 중복 생성 금지. 실제 검증 후 필요 시 기존 파일을 통합·교체하되 고정 QA는 하나만 유지. Docs check, Pages, Android 배포는 별개다.
- 모든 제품 관련 PR/브랜치 푸시에서 고정 QA를 재사용하도록 정비한다. check_index, scan_secrets, main 대비 git diff --check, 보호 블록 15종 원문/해시 비교를 단일 job에서 수행. 누락·중복·파싱 실패·기준 오류는 실패 처리.
- 보호 목록: assignTough, scanFlatGroups, validateShotRegistry, rd210ValidSlots, canAssignTough, applyFramingCascade, generate, POSE_SHOT_CONFIG, SHOT_TEMPLATES, EXTRA_SHOT_DEFS, CONFLICT_GROUPS, POSE_BY_COUNT, CORE_BED_1V1_IDS, ARCHIVED_POSE_IDS, TOUGH_ACTION_LIB.
- 검사 요약 목표: PROTECTED_CHANGED=0 (FAST_TRACK) 또는 PROTECTED_CHANGED=N (DEEP_TRACK). FAST_TRACK은 보호 블록 불변, UI/문구/디자인/아이콘 전용 변경, 공식 검사 성공 조건 모두 충족 시 적용. 엔진·체위/샷·저장소/API·데이터 로더 변경은 보호 블록 수와 무관하게 DEEP_TRACK. 검사 실패를 성공으로 위장하지 않는다.
- FAST_TRACK: 반복 4해상도 캡처·2세대 저장·60표본·IndexedDB 풀코스와 Neon ZIP 검수 생략. 사용자 배포 승인 1회(조건부 승인 포함) 후 동일 후보 즉시 main 반영→Pages 성공→Fold8 확인. PR Merge도 승인 파일만 반영하는 동등한 경로일 때 허용.
- DEEP_TRACK: Neon 독립 검수, 영향 범위 출력/저장 회귀 후 승인 배포. QA 실제 NAI 호출 금지.
- 버전별 신규 QA yml·verify 브랜치/PR·ZIP·REVIEW.md·patch 묶음·수동 SHA256 표 금지. 커밋 1~2개와 Actions 링크로 관리. 과거 QA 브랜치/PR/워크플로는 증거 보존 후 필요시 정리하며 이번 지침 등록에서는 삭제하지 않는다.

### 2. Fold8 원클릭 최신 버전 적용 (후속 구현)
- 부팅 또는 설정 진입 시 `fetch('./version.json?t=' + Date.now(), { cache: 'no-store' })`로 원격 web 버전 조회. 오프라인·조회 실패는 조용히 무시. 현재 rd-version과 다르면 상단 배너 또는 설정 상단에 '새 버전(vX.Y.Z) 바로 적용' 표시.
- 클릭 즉시 saveDraft()로 초안을 안전 저장하고 성공 확인. 생성 busy 중 재로드 차단 또는 안전 종료 후 허용, 실패 시 화면·데이터 보존. My Builder 소유 Cache Storage/Service Worker 캐시만 정리.
- `location.replace(location.pathname + '?v=' + encodeURIComponent(remoteVer) + '&t=' + Date.now())`로 캐시 우회 재로드. 새 버전·초안·프리셋·갤러리·화풍 보존 확인. localStorage/IndexedDB 전체 삭제 금지. APK 변경 없이 웹 범위에서 구현.

### 3. 체위·샷 데이터 분리 (후속 구현, DEEP_TRACK)
- 신규 docs/poses.json 데이터 스키마 1: schemaVersion, POSE_BY_COUNT, POSE_AFTER_BY_COUNT, SHOT_TEMPLATES, EXTRA_SHOT_DEFS, POSE_SHOT_CONFIG, CORE_BED_1V1_IDS, ARCHIVED_POSE_IDS. 사용자 저장 schemaVersion:2와 별개. 기존 ID·태그·순서·출력 및 Set 등 자료형 의미 보존.
- tools/check_poses.py에서 JSON·스키마·중복·참조 및 validateShotRegistry 동등 무결성 검증 후 고정 QA에 편입. 외부 데이터도 보호 블록에 대응해 기준/후보 비교하며 HTML만 비교해 FAST_TRACK으로 오분류 금지.
- 웹/Pages/WebView 부팅 시 `fetch('./poses.json?v=' + encodeURIComponent(APP_VERSION), { cache: 'no-store' })`로 로드. 검증 완료 데이터만 원자적으로 적용하고 validateShotRegistry 통과 후 초기화. 오프라인/file://·네트워크·파싱/검증 실패 시 내장 fallback 또는 검증된 호환 캐시로 안전 부팅. 무한 대기·부분 레지스트리 적용 금지.
- downloadSelfHTML()은 현재 유효한 메모리 레지스트리를 내장 fallback에 직렬화하고 클린 저장 규약 유지. 오프라인 단일 HTML 재열기·2세대 재저장·출력/복원/실제 저장소 회귀 확인. 외부 데이터는 실행 코드가 아닌 검증된 JSON으로 처리.
- 전환 승인·검수 후 태그 수정은 poses.json 중심으로 하되 필요한 version.json도 갱신해 버전 감지 및 호환성 보장. 데이터 변경은 정밀 트랙. 현재 index.html/version.json 제품 계약 유지, 승인된 전환 이후 poses.json을 배포 허용 파일에 추가.

### 4. 완료 기준과 적용 순서
1. 고정 QA 실제 실행 검증 및 두 트랙 분류 정비 (현재 파일 등록 완료, 실행 검증 미완료).
2. 원클릭 최신 버전 적용 버튼 구현·검수·승인 배포.
3. poses.json 분리·검증 도구·fallback/직렬화 연동·Neon 정밀 검수·승인 배포.
기존 엔진 동작, 저장 schemaVersion:2, 백업/복원, IndexedDB, 갤러리 200장, ba 원본 화풍/UC, Android app.mybuilder APK 보호. 신규 innerHTML/Math.random/외부 CDN 0건. 승인된 명세 밖 제품 변경 금지.


## 최신 우선 규칙 — 2026-11-28 간소화 승인

아래 규칙은 이 문서의 기존 단계별 산출물·검수·분업 지시보다 우선한다. 기술 보호 계약은 유지한다.

- Chat Sol이 기획부터 배포까지 총괄하고 Work는 필요할 때 보조한다. 앱 업데이트는 승인된 범위 안에서 시작부터 완료까지 연속 수행한다.
- 다음 버전부터 기존 main의 고정 `.github/workflows/auto-qa.yml`만 QA에 재사용한다. 버전별 QA 워크플로·verify 브랜치 금지. 기존 main Docs check·Pages·Android 배포 절차는 별개이며 유지한다.
- 고정 QA: check_index, scan_secrets, git diff --check, 기존 Neon 확정 보호 블록 15종의 원문 동일성. 실패/누락은 PASS로 간주하지 않는다. 최신 main을 기준으로 후보를 확인한다.
- UI/디자인 전용 변경에서 15종 불변 및 고정 Actions SUCCESS가 확인되면 Neon ZIP 검수 없이 승인 범위 내 배포한다. 엔진·체위/샷·저장소 변경에는 Neon 독립 검수 필요. 보호 블록의 의도된 변경은 실패/변경 사실을 숨기지 않고 명시 승인 및 해당 영역 독립 검수를 거친다. 단순 보호 블록 동일성이 모든 동작 검증을 의미하지 않는다.
- 버전별 커밋은 1~2개로 압축한다. 체크포인트별 ZIP, REVIEW.md, SHA256 표, 단계별 patch 묶음은 만들지 않는다. 필요한 후보 식별자·Actions 링크·변경 요약만 남기고 검수 요청서는 Neon이 필요한 변경에 한해 복사 가능한 블록으로 제공한다.
- v3.3.0 ATELIER는 사용자 명시 승인에 따라 기존 최종 Actions 3개 SUCCESS를 승계하고 추가 검수 없이 배포했다. 제품 배포 커밋 `d5d8796e0be199d52cf438b7bbc5fbcbc958d866`; [후보 QA](https://github.com/EhdQkddhdld/my-builder/actions/runs/46110505265), [Docs check](https://github.com/EhdQkddhdld/my-builder/actions/runs/46111848729), [Pages](https://github.com/EhdQkddhdld/my-builder/actions/runs/46111847951). 별도 실기기·서비스 HTTP·잔여 보호 계약 검사는 미확인이다.

갱신: 2026-11-28. 이 문서는 모든 작업 환경의 공통 실행 절차다. 사용자 최신 결정 및 AGENTS.md의 기술 보호 계약을 함께 적용한다. 이 문서의 목적은 검사 생략이 아니라 **같은 작업의 반복 제거**다.

## 1. 협업 및 권한

- Sol: 기획, 디자인, 명세, 구현, 자체 검수, QA 브랜치 관리. Chat 중심, Work 보조. 동일 제품 동시 수정 금지.
- Neon Task: NAI 전문 자문 및 독립 검수. 자체 검수와 구분한다.
- 기존 업데이트 챗: 최종 원격 대조, 배포 조건 확인, 승인 제품 파일만 main에 반영, Actions/Pages 확인.
- 사용자: 방향·중대 변경·배포 승인·실기기 결정. 명시적 조건부 배포 승인이 있고 제품 지문/범위/기준이 그대로라면 조건 충족 뒤 재승인 요청 없이 반영한다. 제품/범위/기준 변경 시 재검토한다.
- Codex 및 Neon 일반 Chat은 사용하지 않는다. 자동 배포 감시를 중단한 상태에서 임의로 재개하지 않는다.
- GitHub 공개 브랜치는 비공개 저장소가 아니다. 사용자 데이터/비밀값/개인 작품을 넣지 않는다.

## 2. 작업 시작: GitHub부터

1. README, PLAYBOOK, AGENTS, 최신 main HEAD, docs/version.json, 실제 대상 QA 브랜치 HEAD/README를 확인한다. 사용자 제공 기준/후보와 다르면 쓰기 전에 원인을 확인한다.
2. 새 버전은 `qa/vX.Y.Z` 또는 합의한 R번호 브랜치를 먼저 확보한다. 이미 존재하면 재사용한다. 승인 시안/명세, 제품 커밋, QA 커밋, 검수 증거를 분리해 보존한다.
3. QA README에는 기준 commit/blob/SHA-256, 후보 commit/blob/SHA-256, 최신 QA HEAD, 승인/보류, 명세 경로, 검사 run ID/결과/미검증, 다음 담당을 기록한다. 다른 환경은 README와 실제 원격 상태부터 이어받는다. 역사 기록을 최신 상태로 취급하지 않는다.
4. 위험도에 맞게 탐색: L0 문구·색·여백, L1 일반 UI·경량 수정, L2 신규 기능·복합 상태, L3 엔진·저장·API. 관련 코드/증거 위주로 읽으며 대규모 작업이나 실행 환경 부족은 Work 보조를 검토한다. 이미 확정한 결정을 반복 질문하지 않는다.
5. 시안 승인 이전 제품 수정 금지. 구현 시 AGENTS의 DOM·필터·NAI·Undo·저장·보안·Android 보호 계약 준수. 작업 범위 밖 개선은 별도 제안.

## 3. 원본 확보 및 장애 우회 (순서대로, 성공하면 중단)

- GitHub 연결이 가능하면 먼저 commit metadata와 두 파일의 blob SHA를 조회한다. 기존 승인 후보가 QA 브랜치에 있다면 blob 재사용을 우선한다. 큰 HTML을 채팅 본문으로 복사하거나 다시 작성하지 않는다.
- 실제 실행·SHA-256 계산이 필요하면 원본 Git checkout/archive 또는 정확한 ZIP을 확보한다. 환경에서 Git/DNS가 막히면 GitHub 연결의 Git blob/recursive tree, Actions artifact, 이미 보존된 저장소 스냅샷을 검토한다.
- 전체 저장소 복원은 원격 recursive tree의 모든 경로·모드·blob 지문과 비교한다. 차이 파일만 정확히 확보하고 전체 동일성 확인 뒤 검사한다. 일부 파일만 검사하면 부분 검사로 표기한다.
- 파일 전송이 불가능하면 승인된 기준본에 정확한 기계 생성 delta를 적용하는 방식을 검토한다. 적용 결과 SHA-256과 Git blob이 승인값과 완전히 일치할 때만 사용한다. 임시 전달 파일은 비밀·사용자 자료 없이 만들고 필요한 권한 범위 안에서 정리한다. 동일성을 입증할 수 없으면 배포하지 않는다.
- 직접 접속 실패와 제품 결함을 구분한다. 동일한 실패 경로를 반복하지 말고 실제 시도·오류·대체 경로를 기록한다. 대체 경로도 없으면 담당 환경으로 정확한 후보/로그/필요 작업을 인계한다.

## 4. 검수: 유효 증거 승계 및 실패만 재검사

필수 공식 검사:
```sh
python3 tools/scan_secrets.py
python3 tools/check_index.py docs/index.html
git diff --check
```

- 각 결과에 실행 대상 commit/blob/SHA-256, 환경, 명령, 종료 코드, 로그/run ID를 남긴다. 전체 저장소 보안 검사는 전체 스냅샷에서 확인한다.
- 이전 증거는 제품 지문이 동일하거나, 변경 diff와 검사 영향 관계가 명시적으로 입증된 경우에만 승계한다. QA 파일만 변경되고 제품 두 파일의 blob이 그대로라면 기존 제품 검사 중 유효한 결과를 재사용한다. 영향받은 기능, 누락된 필수 검사, 실패 경로는 재검사한다.
- 위험도에 따라 실제 HTTP origin + Chromium, 실제 IndexedDB, 상태/Undo, 출력 비교, 백업 복원, HTML 저장 2세대, Back/Escape, 476×660/839×660/840×660/933×612 등을 선택한다. 모의 테스트·표본·실기기를 구분한다.
- 필수 검사 실패는 차단 조건. 실패 위치, 전체 예외/traceback, 경과 시간, 실제 대상 상태, 기준본 재현 여부를 확인한다. 검사별 독립 브라우저 컨텍스트를 사용하되 저장 지속성/재열기 검사 내부에서는 동일 컨텍스트를 유지한다.
- 사례 v3.2.1: 기존 회귀 run 46038439375에서 12초 TimeoutError 6건. 다운로드 제한 20초보다 먼저 실패해 공통 boot 경로를 조사. 이전 단계 복원을 고려해 명시적 초기 단계 이동, 테스트 컨텍스트 격리, 진단 기록을 보완. 동일 제품 후보에서 재실행 run 46039798694 및 Auto QA 46039798753 성공. 타임아웃 연장이나 검사 삭제로 통과 처리하지 않는다.
- 제품 결함이면 Sol에 반환, QA 결함이면 QA 커밋만 보완. 제품 지문이 바뀌면 영향 검토와 필요한 검사/독립 검수를 다시 한다.
- QA는 테스트용 중립 데이터·모의 외부 요청만 사용한다. 실제 NAI API 호출, 사용자 원본 작품/백업/키 사용 금지. 최소 권한의 격리된 Actions를 사용하며 QA 워크플로는 제품 배포에서 제외한다.
- Neon의 독립 판정(PASS/조건부 PASS/FAIL/미검증)을 확보한다. 필수 실패/누락을 조건부 PASS로 우회하지 않는다. 직접 실행·로그 검토·승계·미검증을 구분한다.

## 5. 업데이트실: 승인 blob 그대로 단일 커밋

제품 배포는 다음 순서로 수행한다. 문서 관리 변경은 별도 승인 범위/별도 커밋으로 분리한다.

1. 현재 main HEAD, 대상 QA HEAD, 제품 후보 commit, 승인 두 파일 blob/SHA-256, 독립 검수 대상과 공식 검사 증거 및 사용자 승인 확인.
2. QA HEAD의 두 파일 blob과 승인 제품 커밋의 blob을 비교한다. 일치해야 한다. QA 전체 병합 금지.
3. 연결 도구의 Git Data API 또는 동일 기능을 사용한다:
   - base main의 tree에 승인 `docs/index.html` 및 필요한 `docs/version.json` blob SHA만 지정해 tree 생성.
   - 현재 main을 단일 parent로 commit 생성.
   - compare로 변경 경로가 승인 파일뿐인지, 누적 diff 규모/내용이 승인 범위인지 확인.
   - main HEAD 재조회. 기준과 같을 때만 non-force ref update (지원 시 expected SHA/lease). 변경되었으면 정지하고 새 기준 대조. 강제 덮어쓰기 금지.
4. 배포 후 main HEAD와 두 원격 blob, version.json, 변경 경로를 다시 확인. Android/서명/APK/QA 파일은 승인 없이는 변경 금지.
5. GitHub Actions REST의 `actions/runs?head_sha=배포커밋`으로 push/Pages run 확인. PR 전용 조회 결과가 비어도 실행이 없다고 단정하지 않는다. 해당 커밋의 Docs check(보안/HTML/JS)와 Pages build/deploy 완료·성공을 각각 확인한다.
6. 서비스 URL과 version.json 실제 HTTP를 확인할 수 있으면 수행한다. 제한되면 명시한다. Pages SUCCESS와 HTTP 정상, 실기기 기능 정상은 별개다. 처리 중/실패를 성공으로 표시하지 않는다. 무리한 반복 조회나 배경 작업 약속 금지.
7. 사용자가 Fold8 커버/펼침, 변경 기능, 필요한 저장/Undo 및 실제 생성 등을 확인한다. 웹 패치만이면 APK 재설치 불필요.

## 6. 작업 보고 및 인계

- 보고 순서: 변경 → 검사/근거 → 실패·미검증 → 배포 상태/다음 담당. 디자인 결정에는 실제 조작 가능한 시안 및 화면을 우선한다. 제품 화면/시연/실제 NAI 결과는 구분한다.
- 기술 원문은 QA 브랜치/Actions 링크로 남기고 사용자에게 중복 ZIP 전달을 요구하지 않는다. 필요한 경우 정확한 ZIP과 지문을 제공한다.
- 중대 결정·배포·환경 전환 시 기준, 후보, QA HEAD, 사용자 승인, 성공/실패 run ID, 미해결 및 담당을 기록한다. 단순 질문은 간단히 답한다.
- 사용자가 결정해야 할 사안만 승인/보류 버튼 또는 명확한 선택으로 제시한다. 일반 작업 단계는 승인 범위 안에서 자율 진행한다.
- 파일/권한/검사 환경 한계 및 실제 미실행은 솔직하게 기록한다. 다른 채팅방의 진행 상황과 기억이 자동 동기화된다고 가정하지 않는다.

## 7. 검증된 배포 사례 (역사 기록, 항상 최신 main 조회)

v3.2.1 R2: 기준 e6d7f85df1f7e45345d3e8dcbe4613e19bb6b236, 제품 748a82cb6ffc559332ce2b77cb834a616d607fc8, 보완 QA f594b272a88973bd40d8368befc9f36b8f03c121, 배포 205ba64810be7fc6e1bdeb0290f69317b925283e.
- HTML blob 12233467a182a9354529b3571c2bb6ea9ab12fd8, version blob 3cc74b2226730009d09703c6de9c7830ac6da30f: 원격 배포 파일 일치 확인.
- [회귀 검사 성공](https://github.com/EhdQkddhdld/my-builder/actions/runs/46039798694) · [Auto QA 성공](https://github.com/EhdQkddhdld/my-builder/actions/runs/46039798753) · [Docs check 성공](https://github.com/EhdQkddhdld/my-builder/actions/runs/46040897638) · [Pages 성공](https://github.com/EhdQkddhdld/my-builder/actions/runs/46040897719).
- 실제 공개 서비스 HTTP 및 Fold8 기능 확인은 별도이며, 이 기록이 실기기 PASS를 뜻하지 않는다.
