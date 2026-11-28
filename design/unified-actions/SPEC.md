# My Builder · 동작·반응 통합 단일 선택(자동 기본) 개편 명세서 (Sol 전달용)

- **작성**: Neon (NAI 연구 · 설계 자문)
- **목적**: 타율 저하와 태그 충돌을 유발하는 다중 선택·크롭 충돌 동작을 정리하여, **① 남성 추가 손길 · ② 여캐 능동 손동작 · ③ 말단 신체 반응** 3개 영역을 모두 **"기본 자동(추가 태그 없음) + 현재 체위·구도에서 호환되는 항목만 최대 1종 단일 선택"** 구조로 통일한다.
- **트랙 구분**: `DEEP_TRACK` (UI 단일 선택·가시성 필터 확장 포함 — 단, 보호 블록 15종·레지스트리 ID·저장 스키마 불변)

---

## 1. 공통 UX & 보호 계약

1. **기본 상태 = 자동 (무선택)**
   - 3개 영역 모두 초기값은 무선택(`자동`, 추가 태그 0건)이다.
   - 재선택 시 즉시 해제(One Touch)되어 `자동`으로 복귀한다.
2. **최대 1종 단일 선택 (라디오 계약)**
   - 각 그룹 안에서 동시에 1개만 선택 가능하며, 다른 항목을 누르면 기존 항목이 즉시 교체된다(Undo 1회).
3. **체위·구도 호환 필터 (불가능한 항목 숨김)**
   - 현재 선택된 `인원 · 체위 · 샷(가시 부위) · 복장 · 구속 · 남캐 크롭` 조건에서 물리적으로 불가능하거나 크롭과 충돌하는 항목은 UI에서 숨긴다(`.hidden` 논리 필터 계약 유지).
   - 가능한 항목이 0개이면 섹션에 안내 문구만 표시(`현재 체위·구도에서 선택 가능한 항목이 없어요`).
4. **레지스트리 및 기존 프리셋 100% 보존**
   - UI에서 숨기는 항목의 ID를 코드(`TOUGH_ACTION_LIB`, `FEMALE_ACTIVE_HANDS`, `EXTREMITY_CHIPS`)에서 **삭제·개명하지 않는다.**
   - 기존 저장 프리셋이나 `schemaVersion: 2` 백업에 구 다중 선택 또는 숨김 항목이 들어 있어도 **자동 삭제·정규화하지 않고 원본을 유지**한다(사용자가 새로 클릭할 때만 단일 선택 정책 적용).

---

## 2. 영역별 노출 항목 및 체위·구도 호환 규칙

### 2.1 남성 추가 손길 (`group-tough`) — 확정안 반영
- **UI 노출 (최대 1종 · 기본 자동)**: 가슴 3종만 노출 (기존 Soft/Medium/Hard 분류 폐기, 나머지 15키는 코드 보존·UI 숨김)

| 항목 | 내부 키 / 태그 | 노출 조건 (체위·구도 필터) |
| :--- | :--- | :--- |
| **가슴 주무르기** | `breast squeezing` (`squeezing breasts` / `groping breasts` 통합 UI) | 파트너 있음(`1:1`~`1:5`) · 가슴 가시 샷(`!hideChest`) · 가용 남캐 손 있음 |
| **유두 꼬집기** | `nipple tweak` (`tweaking nipples`) | 위 조건 + 상체 노출(`requiresBare: true`) |
| **가슴 빨기** | `breast sucking` (`breast sucking`) | 위 조건 + 상체 노출(`requiresBare: true`) + 구강 비점유(`!boyOralBlocked`) |

### 2.2 여캐 능동 · 셀프 손동작 (`group-female-hand`)
- **UI 숨김 (타율 저하 · 크롭 충돌 · 코드 보존)**:
  - `hands_on_chest` (`상대 가슴에 손`): 남캐 `cropped torso / upper body out of frame`과 정면 충돌
  - `bite_clothes` (`옷자락 물기`): 입 표정·구강·상의 탈의와 충돌 및 의상 기형 유발
  - `arms_around_neck` (`목 감싸 안기`): 남캐 두부 크롭(`head out of frame`) 시 팔 붕 뜸 유발
- **UI 노출 (최대 1종 · 기본 자동)**: 핵심 5종

| 항목 | ID / 태그 | 노출 조건 (체위·구도 필터) |
| :--- | :--- | :--- |
| **가슴 들어올리기** | `lift_breasts` (`lifting own breasts`) | 양손 자유(`!handsBusy && !restrained`) · 가슴 가시(`!hideChest`) |
| **가슴 가리기** | `cover_breasts` (`covering breasts`) | 양손 자유 · 가슴 가시(`!hideChest`) |
| **입술에 손가락** | `finger_to_mouth` (`finger to mouth`) | 한 손 이상 자유 · 얼굴 가시(`!hideFace`) · 구강 비점유(`!hasOral`) |
| **더블 브이** | `double_peace` (`double peace`) | 양손 자유 · 상반신/반신/전신(`!upperCrop`) · 정면/측면 시야(배면/얼굴 비가시 제외) |
| **직접 벌리기** | `spread_pussy` (`spread pussy, spreading own pussy`) | **단독(`solo`) 전용** · 양손 자유 · 하의 노출(`requiresLowerBare`) · 하체 가시 |

### 2.3 말단 신체 반응 (`group-extremity`)
- **변경 핵심**: 기존 다중 선택 → **최대 1종 단일 선택(기본 자동)**으로 전환.
- **UI 숨김 (해부학 과장 · 코드 보존)**: `stomach bulge` (`아랫배 볼록·깊은 압박`) — 일반 체위 구도 왜곡 빈도가 높아 UI 기본 숨김(기존 프리셋 로드 시에만 유지).
- **UI 노출 (최대 1종 · 기본 자동)**: 핵심 4종

| 항목 | 태그 | 노출 조건 (체위·구도 필터) |
| :--- | :--- | :--- |
| **전신 홍조** | `body blush` | 상시 허용 (포즈 간섭 0%) |
| **등·허리 휨** | `arched back` | 이미 체위 `girlPose`에 `arched back`이 들어있지 않고, 상체/전신이 보이는 샷(`!faceCrop && !crotchCrop`) |
| **주먹 꽉 쥠** | `clenched hands` | 손이 바닥/벽을 지지하거나 구속되지 않은 체위(`!handsBusy && !restrained`) · 손 가시 샷 |
| **발가락 오므림** | `curled toes` | 발이 실제로 프레임에 들어오는 샷(`showFeet !== false && (full body || wide || feet focus)`)에만 노출 (`cowboy shot`/`upper body`에서는 숨김) |

---

## 3. 기존 충돌·보호 규약 점검

1. **기존 `CONFLICT_GROUPS` · `evaluateFemaleHandRules()` · `canAssignTough()` 원형 보존**:
   - 기존 필터 함수를 단순화하거나 삭제하지 않고, UI 노출 목록(Allowlist) 및 단일 선택 라디오 제어 레이어만 얹는다.
2. **프롬프트 출력 계약**:
   - 모두 `자동(무선택)` 상태일 때 기존 무선택 상태와 프롬프트·UC·좌표·복사 슬롯 바이트 100% 동일.
   - `clenched hands`와 `group-female-hand` 간 기존 배타 규칙(`FEMALE_HAND_PEERS`) 유지.
3. **공식 필수 검사 & QA**:
   - 고정 `.github/workflows/auto-qa.yml` + `tools/check_protected.cjs` 통과.
   - 신규 `innerHTML` · `Math.random` 0건, `schemaVersion: 2` 백업 복원 및 기존 다중 선택 프리셋 비파괴 확인.
