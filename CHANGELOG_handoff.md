# 젬의 NAI V5 프롬프트 빌더 — 리디자인 수정 내역 (인수인계용)

대상: 네온 · 그록 · 아스트라 등 이 파일을 이어서 만질 AI
기준 원본: `src_original.html` (v3.67.0). **원본은 절대 수정 금지.** 모든 버전은 원본 + 레이어를 빌드 스크립트로 합친 결과물임.
기기 기준: 갤럭시 Z 폴드8 일반형. 커버 476×660, 메인(펼침) 933×612, DPR 2.625. PC는 깨지지만 않으면 됨.

---

## 1. 파일 구조와 빌드

```
ui-mockup/
  src_original.html          원본 v3.67.0 (읽기 전용)
  patch_v24.py → src_v24.html  v2.4 원본 로직 패치 (assert 치환, 실패 시 빌드 중단)
  parts/                     레이어 원본 (사람이 읽기 쉬운 형태)
    theme.css  addon.js                      v1~
    shell.css  shell.js / shell_v21.js       v2 / v2.1
    wrapfix.css                              v2.1
    nai.css  nai.js                          v2.2
    shell_v23.css wrapfix_v23.css nai_v23.css nai_v23.js v23.css shell_v23.js   v2.3
    shell_v24.js ux_v24.js v24.css           v2.4
    ux_v25.js v25.css nai_v25.js thumbs_v25.js  v2.5
    app_v26.js                               v2.6 (앱 대응: 뒤로가기 훅, 저장 브리지)
  build.py / build_v2.py / build_v21.py / build_v22.py / build_v23.py / build_v24.py / build_v25.py
  mixer_redesign*.html       빌드 결과 (버전별로 그대로 보존)
  *_v2x.py                   테스트 (아래 7절)
  shots*/                    스크린샷 · 측정 결과
```

빌드: v2.6은 `python3 build_v26.py` (build_v25.py를 먼저 돌린 뒤 v2.5 결과물에 `rd-app-js`와 `<meta name="rd-version">`만 더해 `mixer_redesign_v2.6.html` 생성. v2.5 파일은 바뀌지 않음). v2.5 빌드는 `python3 build_v25.py` (patch_v24.py 자동 실행 후 v2.4 레이어 + v2.5 레이어 → `mixer_redesign_v2.5.html`). v2.4는 `build_v24.py`로 그대로 재현 가능하며 파일을 덮어쓰지 않음.
주입 순서: `</head>` 앞에 Pretendard 폰트 링크 + `<style id=rd-theme | rd-shell-css | rd-wrapfix-css | rd-nai-css | rd-v23-css | rd-v24-css | rd-v25-css>`. `</body>` 앞에 `<script id=rd-addon | rd-shell-js | rd-nai-js | rd-ux-js | rd-thumbs-js>`.
v2.4 빌드에서 CSS 레이어는 죽은 규칙 제거와 공백 압축을 거침. JS는 압축하지 않음 (편집 가능 유지).

## 2. 아키텍처

- **원본 로직**: 프롬프트 생성은 전부 원본 함수(`generate`, `captureState`, `copySlots`, `getEffectiveMainUC` 등 전역)를 씀. 레이어는 읽기만 하거나 원본 버튼을 `.click()`으로 대신 누름.
- **셸(`shell_v2x.js`)**: 기존 노드를 ID와 핸들러 그대로 옮김. header/nav/dock → `#rd-left`, `.section` 4개 → `#rd-main`, 복사바/기록 → `#rd-right`. `setStep`이 `.rd-active`를 토글함. 멱등이라 원본의 'HTML 저장' 결과를 다시 열어도 중복이 생기지 않음.
  - v2.4: MutationObserver를 `#rd-main`과 `#rd-left`로만 한정함 (복사바 갱신은 무시). 추가 꾸밈 함수는 `window.__rdDecorators`에 등록.
- **HTML 저장**: 원본 `downloadSelfHTML`가 documentElement를 복제함. 래퍼가 두 겹 있음.
  - `nai` 래퍼: `[data-nai-ephemeral]` 노드를 잠시 떼고 키 입력값을 비움.
  - `ux` 래퍼 (v2.4): 저장 전에 시트를 닫아 옮긴 폼을 원위치로 돌려놓음.
- **NAI 모듈(`nai_v23.js`)**: `POST https://image.novelai.net/ai/generate-image`, Bearer 토큰, 응답 zip은 자체 unzip으로 처리.
  - V5 바디: `params_version 4`, `v4_prompt`/`v4_negative_prompt`, `ucPreset 3`, `qualityToggle false`, `cfg_rescale`, `noise_schedule`. 기본값이면 v2.2와 바디가 동일함.
  - 외부에서 쓰는 API: `window.rdNai = {readPrompt, buildBody, unzipFirstImage, isFree, galList, galOpen, galSetPinned, openModal, _ENDPOINT}` (v2.5에서 `galSetPinned`/`openModal` 추가).
- **갤러리/기록 IDB**: DB `rd-nai-gallery`. v2.5에서 v2로 올림.
  - `meta` 저장소 (keyPath id): `{id, ts, thumb(webp ~360px), bytes, pinned, meta{...}}`.
  - `full` 저장소: `{id, blob}`.
  - v1(v2.4) 항목은 업그레이드 커서가 `pinned=false`로 채워 **기록에만** 남김. 갤러리는 핀 찍은 것만.
  - 기록 상한 200장. 넘치면 핀 안 된 것 중 가장 오래된 것부터 삭제. 전부 핀이면 삭제하지 않음.
  - IDB를 못 쓰면 메모리로 대체. v2.2의 `rd-nai-history`는 1회 이전함 (`rd_nai_gal_migrated_v1`).
- **v2.4 시트(`ux_v24.js`)**: `#rd-sheet`(ephemeral)가 기존 폼(`#art-fold`, `#char-fold`, 저장소 입력줄, `#preset-name`, `#sequence-actions`)을 주석 자리표시자와 함께 잠시 옮겨 담고, 닫으면 원위치로 돌려놓음. 폼 안의 저장/삭제 버튼은 하단 액션 버튼이 원본 버튼을 대신 눌러 줌.
  - 외부에서 쓰는 API: `window.rdSheet{open, close, isOpen}`, `window.rdUx{editArt, newArt, editChar, newChar, editVault, vaultAdd, editPreset, editCut}`.

## 3. 저장 키와 호환

| 키 | 종류 | 비고 |
|---|---|---|
| `nai_art_styles_v2`(+v1), `nai_custom_art_v1`, `nai_v366_styles_seeded` | LS | 그림체 |
| `nai_artist_vault_v1`, `nai_v367_artist_pool_seeded` | LS | 작가 저장소 |
| `nai_char_custom_v1` | LS | 커스텀 캐릭터 |
| `nai_favorites_v1` `{chars:[],poses:[]}` | LS | v2.4: **chars는 더 이상 읽지 않지만 지우지도 않음**. 백업에 그대로 포함, 예전 백업 복구 가능 |
| `nai_v5_gem_presets_v310`(+`_preset_v31`) | LS | 장면 슬롯 |
| `nai_sequence_v1`, `nai_history` | LS | 시퀀스 · 기록 |
| `rd_nai_key_v1` | LS | **API 키. 이 브라우저에만 저장. HTML 저장·백업·갤러리에 절대 들어가면 안 됨** |
| `rd_nai_opts_v1` | LS | 생성 설정. `seedLock`이 없던 예전 값은 `seed!==""`로 보정 |
| `rd_nai_gal_migrated_v1` | LS | 갤러리 이전 완료 표시 |
| IDB `rd-nai-gallery` / (구) `rd-nai-history` | IDB | 위 2절 참고 |

백업(`exportSettings`)은 원본의 화이트리스트 그대로라서 `rd_*` 키가 들어가지 않음.

## 4. 불변 조건 (깨면 안 됨)

1. **같은 선택이면 프롬프트가 같아야 함.** functest2가 원본과 체크포인트 md5를 비교함. 카오스는 `Math.random`을 시드로 고정해 비교하므로 **레이어 코드에서 `Math.random`을 쓰면 안 됨** (v2.4에서 실제로 걸렸던 문제).
2. **API 키는 HTML 저장, 백업, 갤러리 메타 어디에도 들어가면 안 됨.** naitest와 galtest로 확인. '키 지우기' 버튼은 유지.
3. **HTML 저장 후 다시 열었을 때 DOM이 중복되면 안 됨.** dltest2가 2세대까지 개수 1을 확인하고, 시트를 연 채 저장해도 깨끗해야 함.
4. 기존 localStorage와 백업은 그대로 열려야 함.
5. 외부 전송은 NAI 생성 요청뿐임.

## 5. 버전별 내역

### v1 — 테마 레이어 (`mixer_redesign.html`)
- 추가: Pretendard 폰트, 다크 테마 카드·칩·버튼 스타일(`theme.css`), 작가 카테고리 색상 보조(`addon.js`, `#vault-filter`만 조작).
- 원칙: 원본 CSS와 JS는 그대로 두고 뒤에 덧씌우기만 함.

### v2 — 앱 셸 (`mixer_redesign_v2.html`)
- 추가: 3단 레이아웃(좌측 내비·본문·우측 복사 패널), 모바일 하단 탭바, 작가 카드 아바타(`.rd-av`)와 믹스 슬롯 꾸밈, ☰ 메뉴, 토스트, 🎲 FAB.
- 변경: 단계 4개를 탭으로 전환(`.rd-active`).

### v2.1 — 줄바꿈 수정
- 수정: 한글이 단어 중간에서 끊기던 문제를 `keep-all`과 strict로 고침. 프롬프트·태그 영역만 어디서든 끊김 허용(`wrapfix.css`).
- 변경: 탭 라벨을 '번호 배지 + 라벨'로 바꾸고 `·` 양옆에 word-joiner를 넣음(`shell_v21.js`).

### v2.2 — NAI 이미지 생성 (`nai.js`)
- 추가: 복사바 🎨 생성 버튼, 키 설정(localStorage 전용, 지우기 포함), 생성 모달, 최근 기록(IDB `rd-nai-history`).
- 보안: ephemeral UI는 HTML 저장 시 떼어 냄. 키 입력값은 비우고 백업에서 제외.

### v2.3 — 가독성 · 생성 창 재설계 · 갤러리
- 가독성(`v23.css`): 본문 16px, 최소 13px. 흐린 글자는 #8a8a98, 대비 4.5 이상. 터치 영역 44px 이상. 제목 체계 통일(섹션 20, 행 17+보라 막대, 카테고리 15), 괄호 설명은 제목 아래로.
- 선택 칩: 테두리 하이라이트 대신 **내부를 색으로 채움**(진한 글자). 잠금/흐림 칩은 빗금, 점선, 🔒 표시.
- 모바일 복사바를 한 줄로 접고 ▴로 펼치게 함(`#rd-cb-toggle`). 탭바 56px. 저장소 내부 스크롤 제거. 커버 화면 믹스기는 1열. 메인 화면은 2/3열(840~1023: 184/1fr/260).
- 제거: 🎲 FAB. 사유: 중복이라 사용자 요청으로 뺌. 카오스는 ☰ 메뉴에 남아 있음.
- NAI 생성 창 전면 재설계(NovelAI 공홈 방식):
  - 이미지가 창 밖으로 넘치던 문제를 고침(`object-fit: contain`).
  - 크기 선택기: 비율 상자, 라벨, px, ✓무료/Anlas 배지. 기본값 832×1216.
  - 설정: 모델, steps, CFG, CFG rescale, 샘플러, 노이즈 스케줄, 시드(🎲 랜덤 · 🔒 고정).
  - 화면 구성: 커버는 전체 화면(이미지 위, 생성 버튼 고정, 고급 설정 접기). 메인은 설정 왼쪽, 이미지 오른쪽.
  - 동작: 진행 표시, 취소(AbortController), 오류 배너(401/402/429/500/압축 오류), 다운로드·다시 생성·갤러리 담기, 최근 결과 줄.
  - 노출하지 않은 것: qualityToggle/UC 프리셋(앱이 품질·UC를 직접 붙이고, V5 형식이 검증되지 않음), SMEA(V4 이상에서 무효), Variety+(V5 값이 검증되지 않음).
- 갤러리(IDB `rd-nai-gallery`): 5번째 탭, 썸네일 지연 로딩, 3:4 타일(커버 3열, 메인 5열 이상), 뷰어(스와이프/화살표), 메타 정보, 프롬프트/시드 복사, '설정 재사용'(프롬프트는 건드리지 않음), 개별·여러 장·전체 삭제(확인 있음). v2.2 기록은 1회 이전.
- 빌드: 브레이크포인트를 840/839로 정리.

### v2.4 — 추가/수정/삭제 통일 · 정리 · 최적화
- 추가/수정/삭제를 한 가지 방식으로 통일함:
  - 그룹 맨 끝의 **＋ 칩**을 누르면 추가 시트가 열림.
  - 칩을 **길게 누르거나(0.5초)** 선택된 칩 옆의 **⋯**를 누르면 하단 시트에서 수정·삭제.
  - 삭제는 항상 확인을 거침.
  - 적용 대상: 그림체, 캐릭터, 작가 저장소, 장면 슬롯, 연속 컷.
- 제거 (흩어져 있던 폼과 버튼, 모두 시트로 대체):
  - 그림체 편집 접기, 캐릭터 편집 접기.
  - 저장소 입력줄과 카드의 ×.
  - 헤더의 장면 이름 입력, 삭제·저장 버튼.
  - 연속 컷의 동기화/이동/삭제/종료 줄.
  - 컷이 있을 때의 '현재 장면 담기' 버튼 (탭 줄 끝 ＋로 대체).
- 원본 로직 변경(`patch_v24.py`):
  - **1-3 캐릭터의 검색칸, 작품/진영 필터, 즐겨찾기(☆/★ 즐겨찾기만)를 UI와 로직 모두 제거**하고 게임별 폴더만 남김. 사유: 사용자 요청.
    - 예전 즐겨찾기 데이터는 조용히 무시함 (지우지 않고 백업에도 유지).
    - 체위 즐겨찾기는 유지.
  - **'＋ 캐릭터' 칩 제거.** 사유: 아래 편집과 중복.
    - 이 칩은 '커스텀 캐릭터 새로 만들기'로 가는 유일한 입구였음. 그래서 `startNewCharacter()`를 새로 만들고, 캐릭터 시트의 **[＋ 새 캐릭터]** 버튼으로 같은 기능을 남김.
  - 원본에도 확인창이 없던 저장소 작가 삭제와 컷 삭제에 확인 추가(레이어).
- 라벨 정리: 긴 라벨을 짧게 줄이고 괄호 설명은 **ⓘ**로 접음 (탭하면 펼쳐짐). 바뀐 목록은 아래 표 참고.
- 최적화:
  - 폰트 CSS를 렌더링을 막지 않게 로드(`media=print` → `onload`).
  - MutationObserver 범위 축소.
  - 저장소가 닫혀 있으면 카드를 꾸미지 않음(지연 처리).
  - 죽은 CSS 16개 규칙 제거(구 NAI 모달, FAB). CSS 레이어 압축.
  - 원본의 죽은 코드 제거(캐릭터 필터 관련 함수와 변수, `.char-add-row`).
  - 측정값은 아래 표 참고.

### 측정 (폴드8, headless Chrome, CPU 4배 감속, 5회 중앙값 · 커버 476×660)

| 지표 | 원본 v3.67.0 | v2.3 | v2.4 |
|---|---|---|---|
| 파일 크기 | 773 KB | 895 KB | 906 KB |
| DOMContentLoaded | 421 ms | 1026 ms | **626 ms** |
| 첫 화면 표시(FCP) | 220 ms | 356 ms | **248 ms** |
| DOM 노드(초기) | 2553 | 3416 | **2799** |
| addEventListener 호출 | 530 | 553 | 565 |
| 칩 탭 동기 처리 | 27 ms | 23 ms | **20 ms** |
| 캐릭터 칩 탭~2프레임 | 50 ms | 46 ms | **34 ms** |

가독성 (`measure_v23.py`, 커버): 13px 미만 글자 1544/1842(v2.2) → 5/1839(v2.4, 글자 크기 0인 탭 라벨 측정 오류). AA 대비 미달 502 → 11(범위 슬라이더 숫자·그라데이션 버튼 등 측정 오류성). 44px 미만 터치 영역 1016/1223 → 3/980(NAI 범위 슬라이더 3개). 하단 고정 영역 202px(31%) → 116px(18%), 메인 화면은 0(우측 패널).

| 이전 라벨 | 새 라벨 |
|---|---|
| 1-3. 여캐릭터 (공식 가슴 볼륨 자동 연동 · 검색 가능) | 1-3. 캐릭터 ⓘ |
| 그림체 추가 · 이름/내용 수정 · 삭제 · 외부 추출 ▾ (접기) | 시트 제목 '그림체 편집 · 이름' / '새 그림체' |
| 캐릭터 추가 · 태그 수정 · 삭제 ▾ (접기) | 시트 제목 '캐릭터 편집 · 이름' / '새 캐릭터' |
| 작가태그 저장소 · 그림체 가챠 | 작가 저장소 · 가챠 |
| + 추가/추출 | 추가 (＋ 작가 시트 안) |
| ✨ 3대 공식 화풍 추가/최신화 | ✨ 공식 화풍 갱신 |
| 연속 컷 시퀀스 (2~4컷) | 연속 컷 (2~4컷) |
| + 현재 장면 담기 | ＋ 지금 장면을 컷으로 (컷이 있으면 탭 끝 ＋) |
| 🔗 공통 설정 전 컷 동기화 / 현재 컷 삭제 / ✕ 시퀀스 종료 | 🔗 전 컷 동기화 / 🗑 컷 삭제 / ✕ 끝내기 (컷 시트) |
| 자유 추가 태그 · 원클릭 퀵 태그 | 추가 태그 · 퀵 태그 |
| 도트 모드 (장면 가중치 생략 · 화풍 태그 후미 결합) | 도트 모드 ⓘ |
| 모든 '(…설명…)' 꼬리 | ⓘ 토글 (`.rd-info` → `.rd-tip.open`) |


### v2.5 — ＋칩 · 여백 · 생성 창 · 기록/갤러리 · 접힘 화살표 · 미리보기 (`mixer_redesign_v2.5.html`)

v2.4 파일은 그대로 두고 `src_v24.html` + 새 레이어(`v25.css`, `nai_v25.js`, `ux_v25.js`, `thumbs_v25.js`)로 빌드함.

- **캐릭터 ＋ 칩 복구**: `#group-char` 맨 끝에 `＋ 캐릭터` 칩(`.rd-char-add`). 선택과 무관하게 누르면 `startNewCharacter()`로 「새 캐릭터」 시트가 바로 열림. 예전 `data-add` ＋캐릭터 칩과는 다름(검색/즐겨찾기 없음).
- **여백 정리** (`--rd-gap-chip:8px`, `--rd-gap-block:14px`, `--rd-gap-section:22px`). 폴드8 커버·메인 전체 훑어서 고친 자리:
  - 체위 탭: `#insert-state-bar`(삽입 중 / 방금 뽑음)가 고정 복사바에 가려지던 여백, 프리셋 칩 줄과 다음 블록 간격.
  - 카메라 탭: `#cam-effective-badge`(기준 샷 요약)와 `2-2. 샷` 헤더 사이 간격. 커버에서 헤더 버튼(풀밀착 바로가기, 여캐 중심 크롭)이 제목과 겹치지 않게 줄바꿈.
  - **2-4b 시네마틱 카메라 · 프레임 연출**: wrapfix의 `.cat-title > :first-child { flex: 1 1 10em }` + 세로 `space-between` 때문에 제목/설명이 카드를 400px 넘게 키우던 문제. 제목 줄은 `flex: 0 0 auto`, 카드 높이 정상화.
  - 섹션 헤더 앞 여백, 칩 그룹 간격, 커버에서 마지막 칩이 하단바에 덜 가리도록 패딩.
- **생성 창을 이미지 없이 열 수 있음**: 복사바 `#rd-nai-gen` 라벨을 「생성 창」으로 바꾸고, 누르면 생성 요청 없이 스튜디오만 염. 키 없으면 설정 `<details>`만 열고 요청은 안 보냄. 실제 생성은 스튜디오 안의 「생성」(`#rd-nai-go`)만. 메뉴의 `#rd-nai-open`은 원래부터 열기만 했음.
- **기록과 갤러리 분리**:
  - 하단 탭이 6칸(화풍·캐릭터 / 체위·접촉 / 수위·환경 / 완성 프롬프트 / 기록 / 갤러리). 메뉴와 스튜디오 안에도 기록|갤러리 전환이 있음.
  - **기록**: 생성한 그림이 전부 자동 저장(최신순, 상한 200). 「기록 비우기」는 핀 안 된 것만 삭제.
  - **갤러리**: 📌 핀 찍은 것만. 스튜디오 결과와 기록 뷰어에서 핀/해제. 「핀 모두 해제」는 갤러리에서만 빼고 기록에는 남김. 뷰어에서 삭제는 둘 다에서 제거.
  - 기존 v2.4 갤러리 항목은 업그레이드 시 기록(핀 안 됨)으로 이전.
- **접힌 탭 글자 회전 제거**: `.art-fold` 등을 열 때 배지/건수(`기본`, `0건`)가 180도 뒤집히던 문제. 글자(`span`, `#history-count` 등)는 회전하지 않음. CSS `::after` 화살표 또는 캐릭터 폴더의 `aria-hidden` ▾만 회전. `#history-count`/`#helpless-fold-count` 끝의 ▾ 문자는 `stripFoldArrows()`가 지워서 화살표가 두 개가 되지 않음. 복사바 `#rd-cb-toggle`은 원래 화살표만 들어 있어 그대로 회전.
- **샷 거리/앵글 칩 SVG 실루엣 아이콘** (`thumbs_v25.js`, `.rd-shot-ico`).
- **「썸네일 만들기」**: 체위 칩 샘플을 사용자 키로 Opus 무료 크기(512×768, 28스텝, 시드 42424242)로 일괄 생성해 IDB `rd-pose-thumbs`에 저장. 이미 있는 칩은 건너뜀. 429면 재시도 없이 중단. 생성 전후 프롬프트 상태를 `captureState`/`loadStandaloneState`로 복구. HTML 저장 때 `[data-rd-ephemeral]`(아이콘·썸네일 버튼)은 떼어 냄. **이 환경에서는 실제 키로 일괄 생성을 돌리지 않음** (테스트는 엔드포인트 목업).
- **미리보기 생성**: 복사바 바로 위 `#rd-prev-bar`. 그림체+캐릭터+샷이 채워져야 버튼이 켜지고, 꺼져 있으면 부족한 항목을 힌트로 보여 줌. 누르면 현재 프롬프트로 작은 그림 한 장(512×768, 23스텝, Opus 무료)만 요청. 칩을 눌러도 자동 생성하지 않음. 429는 재시도 없음. 결과 카드의 「이 시드로 본 생성」은 같은 시드를 고정하고 생성 창을 큰 크기(기본 832×1216)로 열기만 함. 미리보기 그림은 기록에만 자동 저장(핀해야 갤러리). 옵션(`rd_nai_opts_v1`)에 미리보기 크기/스텝을 저장하지 않음.
- **크기 선택기 그룹 라벨**: `.rd-sz-g`의 `writing-mode: vertical-rl`을 없애 커버에서도 「일반/작게/크게/배경화면」이 가로로 한 줄에 붙음.
- 빌드: `python3 build_v25.py` → `mixer_redesign_v2.5.html`. 테스트: `functest2_v25.py`, `v2features_v25.py`, `dltest2_v25.py`, `naitest_v25.py`, `galtest_v25.py`, `uxtest_v25.py`, `previewtest_v25.py`. 스크린샷: `shots6/` (전후 `before_*` / `after_*`).


### v2.6 — 앱 대응 레이어 · GitHub Pages · 안드로이드 앱 (`mixer_redesign_v2.6.html` = 저장소 `docs/index.html`)
- 추가(`app_v26.js`, `<script id="rd-app-js">`, `</body>` 바로 앞 마지막 스크립트):
  - `window.rdHandleBack()` — 안드로이드 뒤로가기용. 열린 것 하나만 닫고 `true`. 우선순위: 갤러리 뷰어 > 갤러리/기록 > NAI 생성 창 > 하단 시트(`rdSheet`) > ☰ 메뉴 > 펼친 복사바 > 이전 스텝(`jumpToStep`). 1단계에서 닫을 게 없으면 `false` → 앱 종료. 각 창은 자기 닫기 버튼(`[data-gv-close]`, `[data-gal-close]`, `[data-nai-close]`)을 눌러 닫으므로 기존 정리 로직(URL 해제 등)을 그대로 탐.
  - 앱 안에서만(`window.AndroidBridge`가 있을 때): `<a download>`의 blob:/data: 저장을 가로채 `AndroidBridge.saveBase64(b64, 파일명, mime)`로 넘김 → 그림은 `Pictures/MyBuilder`, 백업 JSON·HTML 저장은 `Download/MyBuilder`. 원본의 1초 뒤 `revokeObjectURL`에 대비해 `URL.createObjectURL`이 만든 Blob을 클릭 순간 잡아 둠. 복사는 `AndroidBridge.copyText`, 길게 누르기 진동(`navigator.vibrate`)은 `AndroidBridge.haptic`으로. `window.rdShare.text(t)`로 공유 시트 호출 가능(아직 UI 버튼은 없음).
  - 브라우저/`file://`에서는 `rdHandleBack`만 생기고 다른 동작은 그대로(일반 `<a download>`). `Math.random`·`innerHTML` 안 씀. `__rdApp` 가드로 HTML 저장본을 다시 열어도 한 번만 동작.
- 원본·v2.5 레이어 코드는 손대지 않음. 같은 선택이면 프롬프트 동일(functest2 확인).

### v2.7 — M3 다크 앱 UI · 캐릭터별 프롬프트 · 통합 보관함 (`mixer_redesign_v2.7.html` = 저장소 `docs/index.html`)
- **M3 다크 셸 (`#rd-v27-prepatch-css`, `#rd-v27-css`, `#rd-v27-ui-js`)**:
  - 슬림 상단 앱 바(`#rd-v27-appbar`): 현재 선택 요약, 되돌리기, 카오스, ☰ 메뉴.
  - ☰ 메뉴: `완성 프롬프트 보기`(4단계 이동), `전체 초기화`(확인 후 `resetAllSelections()`), `도움말 · 패치 노트`, HTML 저장, 백업/복구, 장면 슬롯, NAI 생성 창.
  - 4탭 내비게이션(화풍 / 체위 / 환경 / 보관함): 커버에서는 하단 내비게이션 바, 펼침 화면에서는 좌측 레일. 4단계(완성 프롬프트)는 ☰ 메뉴로 이동.
  - 하단 복사바(`#copybar`) UI는 숨기고 우측/PIP 옆 플로팅 `복사` 버튼(`#rd-v27-copy`) 제공(프롬프트 생성 엔진·DOM·체크포인트 출력은 원본 v3.67.0과 동일).
  - 단계(1~3) 간 좌우 스와이프 전환(`input`, 슬라이더, 칩, 가로 스크롤 영역 제외). 시트 손잡이 드래그 닫기 지원.
- **미리보기 상시 패널 / 모바일 PIP**:
  - 펼침 화면은 우측 캔버스 상시 표시, 커버는 우측 하단 작은 PIP + `확대`/`닫기` 토글.
  - 칩 탭 시 자동 생성하지 않으며, `미리보기 생성` 버튼 클릭 시에만 512×768·23스텝 요청(429 재시도 없음).
- **통합 보관함 (`#rd-library-tab`)**: 기록(전체)과 갤러리(📌 핀)를 탭 하나로 통합하고 상단에 `전체` / `핀` 필터 배치. 뷰어에서 프롬프트(`메인 프롬프트`, `메인 UC`, 캐릭터별 긍정/UC/위치) 상시 표시 및 원탭 복사. 기존 IDB(`rd-nai-history`, `rd-nai-gallery`, `rd-pose-thumbs`) 호환 유지.
- **스튜디오 캐릭터별 프롬프트 칸 (`#rd-v27-prompts`)**: 메인 긍정/UC + 활성 캐릭터별 긍정/UC/위치(`AI's choice` or `A1`~`E5`) 입력 칸 제공. 빌더 값으로 자동 채워지며, 스튜디오에서 수정한 내용은 해당 생성 요청(`v4_prompt`/`v4_negative_prompt` `char_captions`)에만 반영되고 빌더 상태는 변경하지 않음.
- **테스트 모드 제거 & 기타 수정**: `#copybar-test-mode` / 파이프 테스트 복사 제거(기본값 꺼짐과 출력 동일), 스튜디오 크기 선택기 그룹 라벨(`.rd-sz-g`) 겹침 수정, `rdHandleBack` 우선순위에 PIP 닫기(`rdV27ClosePip`) 추가.
- **최종 검수 수정 반영**:
  - `.m3-ripple-host`가 `position:relative`를 덮어써 뷰어 화살표(`.rd-gv-nav`) 위치가 밀리던 문제를 `.m3-ripple-rel` 분리로 해결.
  - `galOpen()` 시작 시 열린 스튜디오 모달을 닫아(`closeModal()`) `#rd-gal`이 가려지지 않게 수정.

### v2.8 — 모션 · M3 확인창 · 스낵바 실행 취소 · 스크롤 기억 (`mixer_redesign_v2.8.html` = 저장소 `docs/index.html`)
- **M3 대화상자 (`#rd-v28-dialog`, `rdConfirm` / `rdAlert`)**: 남아 있던 브라우저 기본 `alert`/`confirm`/`prompt` 21곳을 모두 M3 모달 다이얼로그로 교체(배경 `inert`, 포커스 트랩, `Escape`/백드롭/뒤로가기 닫기, `rdHandleBack` 최우선 순위).
- **모션 및 스와이프 (`#rd-v28-css`, `#rd-v28-js`)**:
  - `transform`/`opacity`만 쓰는 단계 전환 애니메이션(좌/우/상승, `cubic-bezier(.05,.7,.1,1)`·`cubic-bezier(.22,1.12,.36,1)`).
  - 손가락을 따라가는 실시간 스와이프(`--rd-v28-dx`, 가장자리 저항, 놓으면 탄성 복귀 또는 단계 전환; `input`/슬라이더/칩/가로 스크롤 영역 제외).
  - 모바일 PIP ↔ 확대 카드 전환(`rdV28PipMotion`), 보관함 진입/닫기 전환(`rdV28GalleryMotion`), 칩 눌림 마이크로 인터랙션, 이미지/생성 중 콤포지트 쉬머 스켈레톤(`.rd-v28-skeleton`, `.rd-v28-generating`), 생성 완료 펄스(`.rd-v28-pulse`).
  - `@media(prefers-reduced-motion: reduce)` CSS/JS 대응.
- **스낵바 실행 취소(`rdV28OfferUndo`) · 복구 액션 · 스크롤 기억**:
  - 카오스·전체 초기화·섹션 초기화·프리셋 불러오기 시 스낵바 `실행 취소` 버튼 제공(새 편집 스냅샷 발생 시 자동 비활성).
  - API 키 미설정/401 시 `키 설정` 바로가기, 429 시 `제한 안내` M3 안내창(자동 재시도 없음). 보관함 빈 화면 행동 유도 버튼 추가.
  - 단계(1~3) 및 보관함 그리드 스크롤 위치 탭별 기억(`positions` Map, 저장/백업에 포함되지 않음).
- **정리**: 중복 `<meta name="theme-color">` 1개로 통합, HTML 저장 전 드래그/종료/다이얼로그 임시 상태 정리(`rdV28CancelDialog`, `rdV28BeforeSave`). `innerHTML` 증가 없음(17곳 유지). 공유 기능 UI 없음(안드로이드 앱 수정 없음).

## 6. 디자인 토큰

- 글자: 본문 16 / 보조 15·14 / 최소 13px. 섹션 제목 20, 행 제목 17(왼쪽 4px 보라 막대), 카테고리 15, 시트 제목 17. 탭 라벨 13 (요청은 12였으나 가독성 때문에 13 유지).
- 색: 배경 테마는 `theme.css` 변수 사용. 흐린 글자 #8a8a98(대비 4.5 이상). 선택 칩은 `--accent` 바탕에 글자 #0e0b1f, 영문 #17123a. 위험 버튼 #ff9b8a.
- 터치: 최소 44×44px(⋯, ＋, 시트 버튼 포함). 체크박스 22px. 탭바 56px.
- 레이아웃: 커버 ≤839px는 1열, 하단 탭바와 한 줄 복사바. 메인 ≥840px는 좌/본문/우 3열(840~1023: 184px/1fr/260px). 시트는 커버에서 전체 폭 하단, 메인에서 가운데 560px.

## 7. 테스트 실행

Playwright(python) + `/usr/bin/google-chrome --no-sandbox`. 오래 걸리는 것은 `nohup … &`로 돌릴 것.

| 스크립트 | 내용 |
|---|---|
| `functest2_v24.py` | 원본과 v2.4 프롬프트 체크포인트 비교(커버/메인/데스크톱), 카오스(시드 고정), 클립보드, 저장소 해시. `TOTAL DIFFS: 0`이면 통과 |
| `v2features_v24.py` | 셸 기능(메뉴로 카오스, FAB 0개 등) |
| `dltest2_v24.py` | HTML 저장 2세대 다시 열기 시 DOM 중복 없음(시트 연 채 저장 포함), 백업 왕복 |
| `naitest_v24.py` | 생성 창 모의 테스트 162개: 넘침 없음, 키 유출 없음, 취소·오류, 파라미터, 저장 청결 |
| `galtest_v24.py` | 갤러리 54개 |
| `uxtest_v24.py` | (92개) v2.4 시트·길게 누르기·⋯·＋, 캐릭터 검색/즐겨찾기/＋캐릭터 제거, 예전 즐겨찾기 데이터·백업 호환, 카오스 |
| `perf_v24.py a.html b.html` | 크기, 로드(CPU 4배 감속), DOM 노드, 리스너, 칩 탭 비용 → `shots4/perf_results.json` |
| `shots4/measure_v23.py VER` | 가독성 지표(13px 미만 글자, 대비, 44px 미만 터치 영역) |
| `apptest_v26.py` | v2.6 앱 레이어 68개: rdHandleBack 우선순위, 가짜 AndroidBridge로 그림/백업/HTML 저장 가로채기, 저장본 키 없음, 브라우저에선 기존 다운로드 유지 |
| `*_v26.py` | v2.5 테스트를 v2.6 파일로 돌리는 사본 (스크린샷은 shots7/) |

## 8. 최종 테스트 결과

### v2.4
functest2 프롬프트 체크포인트 원본과 전부 동일(커버/메인/데스크톱, 남은 DIFF 5개는 `xx_used_*` 경로 표시뿐) · v2features OK · dltest2 2세대 중복 0 · naitest 162/162 · galtest 54/54 · uxtest 92/92.

### v2.5
- functest2: 프롬프트 체크포인트는 원본과 전부 동일(커버/메인/데스크톱). DIFF 5개는 UI 경로 플래그뿐(`xx_cb_expanded`, `xx_used_menu`, `xx_used_sheet`). `xx_storage` 해시는 동일. 저장소 DIFF는 `nai_history` 시각 문자열과 `rd_nai_gal_migrated_v1` 플래그(원본에는 없음).
- v2features: 오류 없음 (커버·데스크톱).
- dltest2: 2세대 HTML 저장 뒤 셸/탭/모듈 개수 1 유지(`#rd-v25-css`, `#rd-thumbs-js`, `#rd-hist-tab` 포함). 백업 왕복 DIFF는 원본과 동일(원본 동작).
- naitest: 174/174.
- galtest: 74/74 (기록/갤러리 분리, 핀, v1→기록 이전, 생성 창만 열기).
- uxtest: 100/100 (＋ 캐릭터 칩, 접힘 글자 비회전, 예전 즐겨찾기 호환).
- previewtest: 42/42 (버튼 활성 조건, 칩 탭 시 요청 없음, 512×768·23스텝, 기록만 저장, 시드 고정 후 스튜디오 열기, 429 재시도 없음).

### v2.6
- functest2: 프롬프트 체크포인트 원본과 전부 동일(커버/메인/데스크톱). DIFF 5개는 v2.5와 같은 UI 경로 플래그뿐.
- v2features 오류 없음 · dltest2 2세대 중복 0 · naitest 174/174 · galtest 74/74 · uxtest 100/100 · previewtest 42/42 · apptest 68/68.
- APK: `aapt dump badging` 확인(app.mybuilder, 1.0, minSdk 26, targetSdk 35, 라벨 My Builder), apksigner v2/v3 서명 확인. 패키지에서 개인 이름을 뺐음. 실제 폰·에뮬레이터 실행 확인은 아직 못 함(작업 박스의 에뮬레이터가 부팅되지 않음). 첫 설치 때 폰에서 확인 필요.

### v2.7
- functest2: 프롬프트·슬롯·블록·클립보드·히스토리 체크포인트 원본과 전부 동일(커버/메인/데스크톱). 남은 DIFF 3개는 `xx_used_sheet` 경로 플래그뿐.
- naitest 174/174 · galtest 74/74 · uxtest 100/100 · previewtest 42/42 · apptest 70/70 · dltest2 2세대 중복 0 (`navOK: true`) · v2features 오류 0 · v27_audit 50/50 (스펙 1~10, 스와이프 예외, 429 무재시도, 폴드8 레이아웃·터치 44px·폰트 13px·가로 넘침 없음).

### v2.8
- functest2: 프롬프트·슬롯·블록·클립보드·히스토리 체크포인트 원본과 전부 동일(커버/메인/데스크톱). 남은 DIFF 3개는 `xx_used_sheet` 경로 플래그뿐.
- naitest 174/174 · galtest 76/76 · uxtest 102/102 · previewtest 42/42 · apptest 70/70 · dltest2 2세대 중복 0 (`navOK: true`) · v2features 오류 0 · v28_audit 48/48 (기본 `alert`/`confirm`/`prompt` 0건, 실시간 스와이프 `--rd-v28-dx` 및 예외, 스낵바 `실행 취소`·만료, 401/429 복구 액션, 탭별 스크롤 기억, `prefers-reduced-motion` 규칙, 폴드8 폰트 `>=13px`·터치 `>=44px`·가로 넘침 없음).

## 9. 알려진 문제와 TODO

- NAI 파라미터 중 기본값이 아닌 값(noise, rescale 등)은 실제 키로 확인하지 못함 (키 없이는 401이 먼저 옴). 기본 바디는 사용자의 실제 키로 확인됨.
- 원본의 백업 왕복(초기화 → 복구) 후 프롬프트 차이는 원본과 똑같이 재현됨(원본 동작).
- 카오스는 예전 캐릭터 즐겨찾기가 있으면 원본(즐겨찾기를 앞으로 정렬)과 후보 순서가 달라서 같은 시드에서도 다른 캐릭터를 뽑을 수 있음. 선택이 같으면 결과 프롬프트는 같음.
- `v23.css`의 메인 화면 하단 grid 규칙 일부는 뒤의 flex 규칙에 덮여 쓸모없음(정리 후보).
- 원본 JS(678KB) 압축은 편집성 때문에 보류함. v2.5 파일은 v2.4보다 약 21KB 큼(기록/갤러리 · 썸네일 · 여백 레이어).
- 기록 상한 200장. 기존 v2.4 갤러리 그림은 처음엔 핀이 안 되어 기록에만 보임 — 남기고 싶은 것만 핀.
- 「썸네일 만들기」는 사용자 키가 필요하고, 429가 나면 나머지 칩은 다음에 이어서 만들 수 있음(있는 칩은 건너뜀).
- 커버 하단 6칸 탭 라벨은 13px 근처(12px 미만은 안 씀). 조금 촘촘함.
- 커버 크기 선택기에서 스크롤하면 그룹 라벨이 스튜디오 헤더 아래로 살짝 들어갈 수 있음(가로 쌓임은 해소됨).

- (v2.6) 공유 버튼 UI, 스텝 좌우 스와이프, 폴드 접힘 전용 처리는 아직 없음(브리지 `shareText`는 준비됨).

## 10. GitHub 저장소 · 웹 주소 · 안드로이드 앱 (v2.6~)

- 저장소: https://github.com/EhdQkddhdld/my-builder (공개, 브랜치 main)
- 웹 주소(GitHub Pages, main 브랜치 `/docs`): https://ehdqkddhdld.github.io/my-builder/
- APK: https://github.com/EhdQkddhdld/my-builder/releases (태그 `apk-v1.0`, 파일 `my-builder-1.0.apk`)
- 저장소 이름을 `-`에서 `my-builder`로 바꿈. 웹 주소는 `https://ehdqkddhdld.github.io/my-builder/`. APK 파일 이름은 `my-builder-1.0.apk`. 앱 표시 이름은 'My Builder'. 패키지는 `app.mybuilder`로 바꿨음(개인 이름 제거). 예전에 받으신 패키지(개인 이름이 들어 있던 ID)와는 다른 앱으로 취급되므로, 그 APK를 설치했다면 지우고 이 파일을 새로 설치하면 됨. versionCode는 1.
- 저장소 구조: `docs/index.html`(앱 본체 = `mixer_redesign_v2.6.html`), `docs/version.json`, `android/`(WebView 앱), `tools/scan_secrets.py`, `.github/workflows/android.yml`, 이 문서와 `UPDATE_PLAN.md`.
- **v2.6부터 기준 파일은 `docs/index.html`.** 다른 AI가 고칠 때는 이 파일을 고쳐 main에 푸시하면 됨. (`ui-mockup/`의 레이어 빌드는 v2.6까지의 기록. 레이어 방식으로 계속 만들면 결과물을 `docs/index.html`로 복사.)

### HTML 업데이트 방법
1. `docs/index.html` 수정 (지킬 규칙은 4절 그대로).
2. `python3 tools/scan_secrets.py` — `pst-…`, `github_pat_…`, 값이 붙은 `Bearer …`, 개인키, 키스토어 파일이 있으면 중단.
3. main에 커밋·푸시 → 1~2분 뒤 Pages 반영. `docs/version.json`의 `web`도 올려 두면 좋음.
4. 폰: 앱을 완전히 닫았다가 다시 열면 새 HTML. 재설치 필요 없음.

### 앱(WebView 껍데기) 동작
- 패키지 `app.mybuilder`, 이름 'My Builder', minSdk 26, targetSdk 35. 소스는 `android/app/src/main/java/.../MainActivity.java` 한 파일.
- 열 때마다 `index.html?rdv=<시각>`으로 캐시를 건너뛰고 새 HTML을 받아 보여 주고, 앱 안(`files/offline/index.html`)에 사본 저장. 인터넷이 없거나 실패하면 마지막 사본으로 열림. 처음 한 번은 인터넷 필요.
- 주소(origin)가 `https://ehdqkddhdld.github.io`로 고정이라 localStorage·IndexedDB(작가 목록, 기록/갤러리, API 키)가 앱 저장공간에 남고, 같은 키로 서명한 새 APK를 덮어 설치해도 유지됨. **앱 삭제나 '저장공간 지우기'를 하면 사라짐** → 메뉴의 백업을 가끔 받아 두기.
- `allowBackup=false`: API 키가 든 앱 데이터가 구글 클라우드 백업으로 나가지 않음.
- 뒤로가기 → `window.rdHandleBack()`; `true`가 아니면 앱 종료. 파일 선택(백업 불러오기), 확인/알림 창, 외부 링크(브라우저로 열기) 처리. 글꼴 크기 설정 무시(textZoom 100). 폴드 접기/펴기에 화면을 다시 만들지 않음(configChanges).
- 안드로이드 15+ 화면 끝까지 그리기 대응: 상태바·내비바·키보드만큼 안쪽 여백. 상태바는 보이고(시계·배터리), 주소창·브라우저 버튼은 없음.
- 브리지(`AndroidBridge`): `saveBase64(b64,name,mime)→boolean`, `copyText(t)`, `haptic()`, `shareText(t)`, `appVersion()`.
- `debug` 빌드(`app.mybuilder.dev`)는 에뮬레이터 확인용으로 `http://10.0.2.2:8765/my-builder/`를 염. 폰에는 release만.

### APK 다시 만들기 (HTML만 바꿀 때는 필요 없음)
- 앱 껍데기(`android/`)를 바꿀 때만. `android/app/build.gradle`의 `versionCode`를 1 올리고 `versionName`도 올림.
- 서명 키는 **하나만** 씀: `artistmixer-release.jks` (별칭 `artistmixer`, SHA-256 9D:D0:BC:8D:…:CE:5B:DE:3B). 저장소에 절대 올리지 않음. 다른 키로 서명하면 폰에서 덮어 설치가 안 되고, 지우고 다시 깔면 앱 안 데이터(키·기록·갤러리)가 사라짐.
- 로컬 빌드: `RD_KEYSTORE`, `RD_KEYSTORE_PASSWORD`, `RD_KEY_ALIAS`, `RD_KEY_PASSWORD` 환경변수를 준 뒤 `cd android && ./gradlew assembleRelease`.
- GitHub Actions(`.github/workflows/android.yml`): `android/**`가 바뀌면 빌드. 저장소 Secrets(`RD_KEYSTORE_B64`, `RD_KEYSTORE_PASSWORD`, `RD_KEY_ALIAS`, `RD_KEY_PASSWORD`)가 있으면 서명하고, `apk-v*` 태그를 푸시하면 Release에 APK를 붙임. Secrets가 없으면 서명 안 된 확인용 APK만 아티팩트로 남김.

## 11. 다른 AI(네온 · 아스트라 · 그록 등)에게

이 저장소만 보면 이어서 수정할 수 있음. 토큰·NAI 키·서명 키는 절대 공유하거나 커밋하지 말 것.

- 저장소: https://github.com/EhdQkddhdld/my-builder (공개, 브랜치 main)
- 웹 주소(앱이 여는 곳): https://ehdqkddhdld.github.io/my-builder/
- APK: https://github.com/EhdQkddhdld/my-builder/releases/latest
- **고칠 파일은 `docs/index.html`만.** 원본 HTML과 `android/`(앱 껍데기)는 건드리지 말 것. 레이어 방식으로 다시 빌드했다면 결과물을 `docs/index.html`로 복사.
- 같은 선택이면 프롬프트 결과가 원본과 같아야 함. 레이어 코드에서 `Math.random`을 쓰면 안 됨.
- NAI API 키(`rd_nai_key_v1`), GitHub 토큰, 서명 키(.jks)는 커밋하지 말 것. 푸시 전에 `python3 tools/scan_secrets.py`로 검사.
- main에 푸시하면 1~2분 뒤 웹 주소에 반영됨. 앱을 완전히 닫았다가 다시 열면 재설치 없이 새 HTML이 뜸. 자세한 규칙은 위 4절·10절.
