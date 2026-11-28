# My Builder — AI 개발 운영 규약

**2026-11-28 운영 갱신 (v3.1):** 먼저 [양 AI 통합 지침](PROJECT_GUIDELINES.md)과 PLAYBOOK v1.2의 최신 원클릭/두 트랙 규칙을 적용한다. 이 규칙은 아래의 기존 별도 업데이트실·전 버전 독립 검수·ZIP/수동 산출물·반복 전체 회귀 지시보다 우선한다. 원클릭 갱신 및 poses.json 분리는 후속 승인 구현 사항이며 기존 보호 계약을 유지한다.

**기존 운영 갱신:** 모든 작업 환경은 먼저 [PLAYBOOK.md](PLAYBOOK.md)를 읽는다. 최신 사용자 승인 및 PLAYBOOK의 협업·검수·배포 절차가 과거 역할/경로 설명보다 우선한다. 아래 기술 보호 계약은 그대로 유지한다. 한국어로 소통하며 다른 환경의 실제 기억·권한을 공유한다고 가정하지 않는다.

## 1. 작업 시작 계약
- 저장소: https://github.com/EhdQkddhdld/my-builder, 기준 브랜치 main. 웹: https://ehdqkddhdld.github.io/my-builder/.
- GitHub-first: `README.md`, `PLAYBOOK.md`, 최신 `main` HEAD와 `docs/version.json`, 대상 QA 브랜치의 README/승인 명세/후보 지문/실행 증거 및 관련 AGENTS 계층을 먼저 확인한다. `ASTRA_HANDOFF.md`, `AI_HANDOFF_RULES.md`, `docs/CHANGELOG_handoff.md`, 루트 `CHANGELOG_handoff.md`는 관련 보호 계약 및 역사 확인에 활용한다. 과거 상태·역할을 현재로 간주하지 않는다. 단순 작업에 전체 저장소 재분석을 강제하지 않는다.
- Sol(기획·디자인·구현·자체 검수·QA 브랜치 관리; Chat 중심, Work 보조) → Neon Task(독립 검수) → 기존 업데이트 챗(최종 대조·배포) → 사용자 실기기 확인. 사용자는 방향·중대 변경·배포 승인권자다. Codex 및 Neon 일반 Chat을 사용하지 않는다. 동일 기능 동시 수정 금지. 개발실은 main을 배포하지 않고, 업데이트실은 제품을 임의 수정하지 않는다.
- 최신 명세의 범위만 변경한다. 명세 미수신 상태에서는 읽기 전용 확인만 한다. 동시에 같은 기능을 수정하지 않는다. 현재 작업 트리의 사용자 변경을 보존한다. 범위 충돌, 누락, 위험은 명시한다. 승인 없이 main 푸시·병합·배포·APK 제작·릴리스 발행 금지. 필요한 경우 작업 브랜치/PR로 준비한다. 제품 수정은 승인 범위 내에서만 수행하고, QA 및 제품 커밋을 분리한다.

## 2. 파일과 버전 계약
- 웹 본체는 단일 `docs/index.html`, 버전 정보는 `docs/version.json`. 웹 수정 시 두 파일의 버전과 필요한 화면/제목/패치노트/HTML 저장 파일명을 일치시킨다. 웹 전용 패치에서는 apk, apk_version_code와 android/를 수정하지 않는다. 인수인계 문서 변경은 해당 명세나 사용자 승인 범위에 따른다.
- 원본 Core v3.67.0, 기존 버전 스냅샷, 검사 도구, 워크플로를 임의로 덮어쓰지 않는다. 외부 라이브러리/CDN을 신규 추가하지 않는다. 기존 의존성의 임의 제거 역시 금지. 명세 승인 없이 리팩터링/압축/데이터 삭제/ID 이름 변경 금지.
- 코드 제공 시 수정된 함수 전체 또는 완전한 HTML을 제공한다. 생략 표기 금지. 수정 위치는 고유한 함수명/주석으로 지정한다. 기존 CSS 변수, DOM ID, 이벤트 계약 유지.

## 3. 코어 불변 조건
- 동일 선택/동일 난수 조건에서 메인·캐릭터·공통 UC·개별 UC·복사 슬롯의 출력은 바이트 동일해야 한다. 기능 변경이 명세상 출력 변경을 요구하면 허용된 차이를 별도로 명시하고 나머지를 회귀 검사한다.
- `generate()`, `scanFlatGroups()`, `assignTough()`, `validateShotRegistry()`, `rd210ValidSlots()` 및 복잡한 필터링·연쇄 처리(`CONFLICT_GROUPS`, `canAssignTough`, `applyFramingCascade`) 보존. 최신 소스에 존재하는 95 포즈 ID, 42+2 샷 ID, 기존 18종 상호작용 레지스트리와 두 계층 구조를 보존한다. 과거 75 포즈 지침은 구 버전 기록이며 최신 레지스트리 실측이 우선이다. 폐기된 visMap/actors를 재도입하지 않는다.
- 태그 처리: 단순 comma split 기반 필터·중복 제거 금지. 기존 AST 처리, 사용자 가중치 수치, 언더바, 도트 닫기 `, ::`, artist:/style:/copyright:/source#/target# 보호. 도트 모드 판정은 styleObj.dotMode. 도트 모드의 기존 UC 처리 보존.
- 그림체는 ID 기반 CRUD `nai_art_styles_v2` 유지, 0개일 때 삭제한 화풍 자동 부활 금지. Blue Archive(`ba`)의 기존 화풍/UC 및 4슬롯 고정은 명시 승인 없이는 변경하지 않는다. 원본 제로 액티브 규약과 웹 셸의 승인된 BA 기본 선택 예외를 구분하고 최신 부팅 정책을 회귀 검사한다. 기본값을 임의로 주입하지 않는다.
- 실제 사용자 상태 변경 전 `pushUndo()` 1회. Undo 15단계. 화면 이동·복사·단순 표시 변경·같은 값 재선택 등 상태 비변경 시 Undo 오염 금지. 기존 상태 변경 경로의 `updateAllDynamicFilters()` → `generate()` → `paintCopybar()` 효과를 보존하되 기존 내부 호출을 중복 실행하지 않는다.
- 칩은 `.chip`과 `data-val`, 조건부 기능 숨김은 기존 `.hidden` 사용. 단, `isShown()`이 생성에 관여하므로 화면 목차용 숨김은 논리적 필터 상태와 분리한다. 기존 DOM을 복제하지 말고 이동/원복한다. 신규·수정 UI는 createElement/textContent; 신규 innerHTML 0건. 레이어와 코어 generate 내 신규 Math.random 0건.

## 4. 저장·보안·Android
- schemaVersion 2 및 구 프리셋/백업 하위 호환. 기존 localStorage/IndexedDB 키·스키마/마이그레이션을 보존. `rd_v30_prefs_v1`, `rd_v30_draft_v1`, 기존 작가·화풍·캐릭터·즐겨찾기·시퀀스·히스토리 및 갤러리/썸네일 DB 계약 유지. 세부 키는 기존 AI_HANDOFF_RULES 및 실제 코드 확인.
- NAI API 키는 기존 `rd_nai_key_v1` 로컬 저장 경로에서만 관리. 키 값, GitHub 토큰, 개인키, 서명키, 사용자 백업 및 보관함 사진을 소스/보고서/커밋/ZIP에 포함하지 않는다. 기존 키 지우기 유지. 승인 없는 외부 요청 및 실제 유료 NAI 호출 금지. 429 재시도 금지.
- `window.rdHandleBack()`의 기존 우선순위·true/false 반환, Escape, `AndroidBridge.saveBase64`, copyText, shareText, haptic, hapticKind 및 기존 앱 폴백 유지. Android 1.1 패키지 `app.mybuilder`, versionCode 2, 신규 영구 서명 체계 보존. 키 재생성·교체 금지.
- `downloadSelfHTML()`의 기존 원복 체인과 런타임 위젯 정리, API 키 제거 및 클린 재부팅을 보존. 상세 페이지/시트가 열린 상태 포함 2세대 재저장 검사.

## 5. 필수 검수
- `python3 tools/scan_secrets.py`, `python3 tools/check_index.py docs/index.html`, `git diff --check` 실제 실행 증거 필수. 정확한 후보와 영향 범위가 일치하는 유효 증거는 PLAYBOOK 기준으로 승계한다. 필수 실패/누락 시 배포 금지. 검사 자체를 약화하지 않는다. Git diff/변경 경로/버전/해시를 확인한다.
- 최신 명세 기준 대표 22개 이상 출력 비교(메인·캐릭터·공통/개별 UC와 슬롯). 해당 기능의 실제 변경 이벤트, Undo 및 자동 연동, 백업/프리셋 복구, 네 가지 부팅/복원 조합, HTML 2세대, Back/Escape, Android 브리지 호환 검사. 선택값 및 난수 조건은 기준본과 동일하게 설정.
- Galaxy 폴더블 기준 476×660, 933×612, 경계 839×660/840×660. 44px 이상 터치 영역, 일반 글자 13px 이상, 가로 넘침/겹침/중복 ID 0건, 보관함 이미지/핀 중첩 0건. 모션은 transform/opacity, reduced-motion, 입력 잠금 및 레이아웃 밀림 여부 확인. 해당 명세에 없는 UI 개편은 금지.
- PASS/FAIL/부분 PASS/미실행을 분리. 모의 브리지나 대체 localStorage를 실기기/실제 IndexedDB 결과로 보고하지 않는다. 실험한 표본을 전수 검증으로 부풀리지 않는다. 실패 및 기준본 자체의 오류도 기록한다. 검사 로그·명령·비교 해시를 근거로 남긴다.

## 6. 보고·배포·한도 운영
- 사용자에게 쉬운 한국어로 변경 내용, 현재 상태, 남은 확인, 올릴 파일 및 경로, APK 재설치 필요 여부를 전달. 함수/DOM/키/기술 전문 용어는 별도의 Neon 검수 블록에만 기재한다. 과장·근거 없는 승인 선언 금지.
- 배포 패키지: 수정 파일 전체본을 저장소 경로 그대로 ZIP에 담고 `검수보고서.md` 동봉. 보고서는 기본적으로 GitHub 업로드 제외(명시 승인 시 예외). 개별 다운로드, GitHub 대상 폴더 바로가기, 적용 순서, 실기기 체크를 같이 제공한다. 파일을 생성하지 못하면 경로/PR과 한계를 명시하고 가짜 링크 금지.
- 웹 대상: https://github.com/EhdQkddhdld/my-builder/tree/main/docs ; 루트: https://github.com/EhdQkddhdld/my-builder ; Actions: https://github.com/EhdQkddhdld/my-builder/actions. 배포는 사용자 승인 후 docs-check 및 Pages 성공 확인. 웹만 변경 시 APK 재설치 불필요. 네이티브 수정은 별도 명세/승인 및 동일 서명, versionCode 증가 필요.
- Chat 기본, Work 보조. 사용자가 선택한 모델/추론 설정을 유지한다. 관련 영역만 탐색하고 정확한 후보의 유효 테스트 증거를 재사용하되 필수 검증을 생략하지 않는다. 승인 없는 반복 작업이나 모델 전환은 하지 않는다. 환경 장애 시 PLAYBOOK의 대체 경로를 사용한다.
- 배포·중대 결정·대화 전환·외부 인계 시 다음 5개 항목을 최신 사실로 갱신한다. 일상 답변에는 생략한다.

[동기화 갱신 블록]
- 현재 배포 버전:
- 목표 버전:
- 완료 사항:
- 미확정 항목:
- 다음 담당 AI:
