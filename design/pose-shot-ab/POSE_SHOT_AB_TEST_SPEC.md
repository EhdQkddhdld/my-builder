# My Builder · 체위·샷 타율 A/B 비교 테스트 모드 구현 명세서 (Sol 전달용)

- **작성**: Neon (전문 연구·설계 자문)
- **기준 버전**: 최신 `main` (My Builder v3.3.0+ ATELIER 기준)
- **트랙 구분**: `DEEP_TRACK` (체위/샷 프롬프트 어댑터 포함 — 단, 원본 레지스트리 및 보호 블록 15종은 불변 유지)
- **QA 기준**: 고정 `.github/workflows/auto-qa.yml` + `tools/check_protected.cjs` 재사용 (버전별 임시 `.yml` 생성 금지)
- **목적**: 전체 95종 체위 × 43개 샷 템플릿 정적 점검에서 발견된 **물리·시선·앵커·여운 충돌 항목**을 사용자가 실제 NAI V5에서 **A(점검 전 · 기존)** vs **B(점검 후 · 개선안)** 2칸으로 동일 시드 비교한 뒤, 타율이 검증된 항목만 최종 확정할 수 있도록 임시 테스트 UI와 비파괴 패치 어댑터를 추가한다.
- **작업 등급**: L2 (신규 테스트 비교 UI + 읽기 전용 프롬프트 오버레이 어댑터, 원본 엔진·레지스트리 불변)

---

## 1. 핵심 설계 원칙 (비파괴 · 철거 용이성)

1. **원본 레지스트리 100% 보존**
   - `POSE_BY_COUNT`, `POSE_AFTER_BY_COUNT`, `SHOT_TEMPLATES`, `POSE_SHOT_CONFIG`, `EXTRA_SHOT_DEFS`, `CONFLICT_GROUPS` 원본 데이터는 **1글자도 수정하지 않는다.**
   - 개선안(B)은 별도의 격리된 읽기 전용 오버레이 테이블 `POSE_SHOT_AB_PATCHES`에만 정의한다.
   - 추후 사용자가 항목별 A/B 확정을 마치면, 확정된 B 항목만 원본에 반영하고 본 테스트 UI·오버레이 블록을 깔끔하게 제거할 수 있게 단일 모듈로 격리한다.
2. **근접 프레이밍(여캐 꽉 찬 구도) 보존**
   - 사용자 실전 피드백에 따라 **기존 거리감(`cowboy shot` 및 남캐 `cropped torso, upper body out of frame`)은 절대 건드리지 않는다.** (단, 풋잡 `1v1-footjob`처럼 발 자체가 잘리는 예외 2샷만 제외)
3. **테스트 모드 OFF 시 바이트 100% 동일**
   - A/B 테스트 토글이 `OFF`이거나 현재 선택된 체위·샷이 개선 대상에 해당하지 않으면, 프롬프트·UC·좌표·복사 슬롯은 v3.2.1과 **바이트 단위 100% 동일**해야 한다.
4. **상태·저장·Undo 비오염**
   - A/B 테스트 토글 상태는 휘발성 메모리 상태로만 유지한다(`localStorage`, `schemaVersion: 2` 백업, 프리셋, `undoStack`에 기록 금지).

---

## 2. UI 설계 — "점검 전(A) · 점검 후(B)" 2칸 비교

### 2.1 진입 및 토글
- 위치: **ATELIER 생성 Dock / 빌더 최종 확인(`step-4`)** 및 **스튜디오 생성 영역 상단**에 경량 토글 배치:
  - 라벨: `체위·샷 A/B 점검 비교` (기본 `OFF`)
  - 현재 선택된 체위/샷이 `POSE_SHOT_AB_PATCHES`에 포함되면 배지 표시: `개선안 B 있음 (그룹명 · 수정 사유 1줄)`
  - 대상 외 체위/샷이면 안내 문구만 표시: `현재 체위·샷은 기존 유지 대상(A=B)입니다.`

### 2.2 2칸 비교 레이아웃 (Fold8 대응)
- 토글 `ON` + 대상 체위/샷 선택 시 비교 영역을 **2칸**으로 분할:
  - **476×660 (커버 / 839px 이하)**: 상단 `A · 점검 전(기존)` / 하단 `B · 점검 후(개선)` 세로 2단 스택.
  - **840px 이상 / 933×612 (펼침)**: 좌측 `A · 점검 전(기존)` / 우측 `B · 점검 후(개선)` 2열 병렬 배치.
- 각 칸 구성:
  1. 헤더: `A · 점검 전 (기존)` / `B · 점검 후 (개선)` + 변경 포인트 요약 배지(예: `시선·구강 충돌 제거`, `남1 위치 앵커 보강`)
  2. 변경된 슬롯 요약 표시(메인 / 여캐 / 남1 / 남2 중 실제 달라진 슬롯만 diff 강조, 텍스트는 `createElement`+`textContent`, `innerHTML` 0건)
  3. 개별 복사 버튼: `A 복사` / `B 복사` (메인 + 캐릭터 슬롯 동일 포맷)
- **스튜디오 동일 시드 A→B 순차 생성**:
  - 버튼: `동일 시드 A·B 비교 생성` (명시적 클릭 시에만 실행)
  - 기존 스튜디오의 **공통 시드 · 전역 busy 상호 배제 · 순차 실행(A 완료 후 쿨다운 뒤 B) · 429 즉시 중단(자동 재시도 금지) · 성공 결과 보존** 계약을 100% 그대로 재사용한다.
  - 생성된 결과 카드와 갤러리 메타에 `A(기존)` / `B(개선)` 구분 배지만 표시(기존 갤러리 200장·핀·저장 스키마 유지).

---

## 3. 엔진 연동 방식 (보호 규약 준수)

- 보호 함수(`assignTough`, `scanFlatGroups`, `validateShotRegistry`, `rd210ValidSlots`, `canAssignTough`, `applyFramingCascade`, `generate`) 원본 계약 및 동작을 변경하지 않는다.
- **B안 산출 어댑터**:
  - A안: 기존 `generate()` 결과를 그대로 사용.
  - B안: 현재 선택된 `pose`·`shot` 객체의 **얕은 복사본**에 `POSE_SHOT_AB_PATCHES`의 해당 필드(`girlPose`, `boy1Pose`, `boy2Pose`, `distTag`, `stripLookingAtViewerOnSide`)만 적용해 동일한 파이프라인으로 B안 프롬프트·좌표를 산출한다.
- **측면 샷 시선 규칙(`stripLookingAtViewerOnSide: true`)**:
  - 그룹 2 대상 체위에서 현재 선택된 샷의 `angleTag`에 `from side`가 포함되고, 사용자가 `group-gaze`에서 시선을 명시적으로 선택하지 않은 경우에만 B안의 `girlPose`에서 고정 `looking at viewer`를 제거한다. (정면 샷이거나 사용자가 직접 `카메라 응시`를 고른 경우는 유지)

---

## 4. 전체 A(점검 전) vs B(점검 후) 패치 테이블

### 그룹 1 · 다인원 물리·공간 충돌 (6종 · 최우선 테스트)

| 체위 ID | 변경 필드 | A · 점검 전 (v3.2.1 원문) | B · 점검 후 (개선안) | 수정 사유 |
| :--- | :--- | :--- | :--- | :--- |
| `1v5-filming-mix` | `girlPose` | `straddling, leaning back, open mouth, looking at viewer, target#vaginal, target#anal, source#fellatio` | `straddling, leaning forward, open mouth, target#vaginal, target#anal, source#fellatio` | `looking at viewer` + `leaning back` + `source#fellatio` 3중 충돌 제거 |
| `1v5-sandwich-stack` | `girlPose` | `lying on side, sandwiched, leg lift, open mouth, target#vaginal, target#anal, source#fellatio` | `on back, sandwiched, stacked, leg lift, open mouth, target#vaginal, target#anal, source#fellatio` | 남1(`beneath female`)·남2(`kneeling behind`) 상하 스택과 자세 축 일치 |
| `1v5-air-lift` | `boy1Pose` | `standing, lifting person, holding her thighs, source#vaginal` | `standing, between legs, lifting person, holding her thighs, source#vaginal` | 남1 위치 앵커 명시 및 남3(`oral_front`)·남4(`lift_support`)와 정면 겹침 완화 |
| `1v5-full-service` | `girlPose` | `straddling, leaning back, open mouth, double handjob, target#vaginal, target#anal, source#fellatio, source#handjob` | `straddling, leaning forward, open mouth, double handjob, target#vaginal, target#anal, source#fellatio, source#handjob` | `leaning back`과 전방 구강(`source#fellatio`) 상체 방향 충돌 해소 |
| `1v2-wall-dp` | `girlPose` | `standing, sandwiched between two men, against wall, hands on wall, leg lift, target#vaginal, target#anal` | `standing, sandwiched between two men, beside wall, leg lift, target#vaginal, target#anal` | 앞뒤 2명 샌드위치 + 벽 밀착(`against wall, hands on wall`) 공간 모순 해소 |
| `1v2-mating-dp` | `girlPose` | `on back, reclining, spread legs, legs up, knees to chest, grabbing own thighs, target#vaginal, target#anal` | `on back, reclining, spread legs, legs up, knees to chest, arms raised, target#vaginal, target#anal` | 여캐 `grabbing own thighs`와 남1 `pressing legs down` 손 위치 겹침 해소 |

### 그룹 2 · 샷·시선 충돌 (체위 6종 + 샷 2건)

- **측면 샷(`from side`) 시 `girlPose`의 고정 `looking at viewer` 조건부 제거 (`stripLookingAtViewerOnSide: true`)**:
  - 대상 6종: `solo-leg-lift`, `solo-sit`, `solo-wall`, `solo-foreplay-undress`, `1v1-missionary-flat`, `1v1-footjob` (※ `1v5-filming-mix`는 그룹 1에서 이미 제거)
  - A(기존): 측면 샷에서도 `girlPose`의 `looking at viewer` 유지 → 목 꺾임·측면 구도 풀림 유발
  - B(개선): `from side` 샷 + `group-gaze` 미선택 시에만 `looking at viewer` 제외
- **풋잡(`1v1-footjob`) 샷 프레이밍 보정 (2건)**:

| 샷 ID | 변경 필드 | A · 점검 전 (v3.2.1 원문) | B · 점검 후 (개선안) | 수정 사유 |
| :--- | :--- | :--- | :--- | :--- |
| `foot-front-cowboy` | `distTag` | `cowboy shot` | `full body, feet focus` | 반신 프레이밍으로 풋잡 발이 잘리는 문제 해소 |
| `foot-pov-low` | `distTag` | `cowboy shot` | `full body, feet focus` | 1인칭 풋잡 시점 발 잘림 해소 |

### 그룹 3 · 남캐 위치 앵커 누락 보강 (활성 7종 + 아카이브 6종 + 여운 1종 = 14종)

| 구분 | 체위 ID | A · `boy1Pose` (v3.2.1 원문) | B · `boy1Pose` (개선안) |
| :--- | :--- | :--- | :--- |
| 활성 1:1 | `1v1-lotus` | `sitting, cross-legged, source#vaginal, source#penetration` | `sitting, cross-legged, facing her, holding her waist, source#vaginal, source#penetration` |
| 활성 1:1 | `1v1-wall` | `standing, looming, kabedon, source#vaginal, source#penetration` | `standing, in front of her, looming, kabedon, source#vaginal, source#penetration` |
| 활성 1:1 | `1v1-suspend` | `standing, lifting person, source#vaginal, source#penetration` | `standing, in front of her, lifting person, holding her thighs, source#vaginal, source#penetration` |
| 활성 1:1 | `1v1-amazon` | `on back, on bed, source#vaginal, source#penetration` | `on back, beneath female, legs up, on bed, source#vaginal, source#penetration` |
| 활성 1:1 | `1v1-car-backseat` | `sitting, leaning back, in car, backseat, source#vaginal, source#penetration` | `sitting, beneath female, leaning back, in car, backseat, source#vaginal, source#penetration` |
| 활성 1:1 | `1v1-irrumatio` | `standing, source#oral, source#irrumatio` | `standing, in front of her face, hand on back of head, source#oral, source#irrumatio` |
| 활성 1:1 | `1v1-fellatio` | `standing, looking down, target#fellatio, target#oral` | `standing, in front of her face, looking down, target#fellatio, target#oral` |
| 아카이브 | `1v1-paizuri` | `standing, looking down, target#paizuri` | `standing, in front of her, looking down, target#paizuri` |
| 아카이브 | `1v1-handjob` | `standing, looking down, target#handjob` | `standing, in front of her, looking down, target#handjob` |
| 아카이브 | `1v1-footjob` | `standing, looking down, target#footjob` | `standing, in front of her, looking down, target#footjob` |
| 아카이브 | `1v1-foreplay-wall-pin` | `standing, looming, kabedon, hand on wall, pinning` | `standing, in front of her, looming, kabedon, hand on wall, pinning` |
| 아카이브 | `1v2-foreplay-surround` | `sitting, on left, leaning in, holding her thigh, source#groping` | `sitting, beside her, on left, leaning in, holding her thigh, source#groping` |
| 아카이브 | `multi-foreplay-surround` | `kneeling, on left, leaning in, holding her thigh, source#groping` | `kneeling, beside her, on left, leaning in, holding her thigh, source#groping` |
| 아카이브 | `1v5-foreplay-press` | `kneeling, on left, leaning in, holding her thigh, source#groping` | `kneeling, beside her, on left, leaning in, holding her thigh, source#groping` |

### 그룹 4 · 여운(`after`) 체위 진행 중 태그 정리 (5종)

| 체위 ID | 변경 필드 | A · 점검 전 (v3.2.1 원문) | B · 점검 후 (개선안) | 수정 사유 |
| :--- | :--- | :--- | :--- | :--- |
| `1v2-after-spit` | `boy2Pose` | `standing, in front, hand on back of head` | `standing, in front, resting` | 구강 진행 중 오인 유발 태그 완화 |
| `1v2-after-oral` | `boy1Pose` | `standing, in front, hand on back of head` | `standing, in front, resting` | 구강 진행 중 오인 유발 태그 완화 |
| `1v1-after-cowgirl` | `girlPose` / `boy1Pose` | `straddling, leaning forward, after vaginal` / `on back, on bed` | `lying on his chest, collapsed, after vaginal` / `on back, beneath female, on bed` | 진행 중 `straddling` 완화 + 남1 `beneath female` 앵커 보강 |
| `1v2-after-cowgirl` | `girlPose` / `boy1Pose` | `straddling, leaning forward, after vaginal` / `on back, on bed, holding her waist` | `lying on his chest, collapsed, after vaginal` / `on back, beneath female, on bed, holding her waist` | 진행 중 `straddling` 완화 + 남1 `beneath female` 앵커 보강 |
| `1v1-after-oral` | `boy1Pose` | `standing, looking down` | `standing, in front of her, looking down` | 남1 위치 앵커 보강 |

> **별도 보류 (이번 1차 A/B 패치에 섞지 않음)**: `1:1` 23종의 `source#/target#penetration` 이중 부착 제거와 DP 5중 / 구강 3~4중 중복 압축은 효과가 모델 성향에 따라 갈릴 수 있으므로, 위 4그룹 검증 완료 후 필요 시 2차 실험으로 분리한다.

---

## 5. 보호 규약 및 검수 완료 기준

1. **공식 필수 검사 3종 PASS**: `python3 tools/scan_secrets.py`, `python3 tools/check_index.py docs/index.html`, `git diff --check`.
2. **보호 블록 15종 및 원본 레지스트리 100% 동일**: `POSE_BY_COUNT`, `POSE_AFTER_BY_COUNT`, `SHOT_TEMPLATES`, `POSE_SHOT_CONFIG` 및 보호 함수 7종 원본 바이트 유지.
3. **OFF 회귀 0건**: A/B 토글 OFF 상태에서 기존 v3.2.1과 메인·캐릭터·UC·좌표·복사 슬롯 바이트 100% 일치.
4. **ON 동작 검증 (4해상도: `476×660`, `839×660`, `840×660`, `933×612`)**:
   - 대상 체위 선택 + 토글 ON 시 A/B 2칸 정상 렌더, 넘침 없음, 터치 영역 44px+.
   - 토글 전환·A/B 복사만으로 `undoStack` 및 `localStorage` 변경 0건.
   - 스튜디오 `동일 시드 A·B 비교 생성` 모의 API 검사(공통 시드, 순차 실행, 429 즉시 중단, busy 락).
5. **신규 `innerHTML` 0건**, `Math.random`·외부 CDN 0건, 클린 HTML 2세대 재저장 및 `schemaVersion: 2` 백업 복원 유지.
