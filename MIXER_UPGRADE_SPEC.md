# 믹스기 강화 구현 지시서 (v2.9 기준)

아스트라/GPT용. **기준 파일은 배포된 `docs/index.html` v2.9 전체본**입니다. 산출물도 **전체 `docs/index.html` 하나**로 주세요. 패치 조각만 주지 마세요. 원본 HTML과 `android/`는 건드리지 마세요.

이 작업은 네온 로드맵의 LAB(가중치·비교)·도감(수동 썸네일)과 맞닿아 있지만, 버전 번호는 태준님이 정하면 됩니다. 제안: `docs/version.json`의 `web`을 2.9 다음으로.

관련 규칙: `AI_HANDOFF_RULES.md`, 배포: `UPDATE_GUIDE.md`.

## 목표 (6가지, 모두 필수)

4슬롯 믹스기는 **항상 작가 4명**입니다. 2~3명 믹스는 만들지 마세요.

1. **랜덤 믹스** — 풀에서 4명을 뽑고 가중치도 랜덤.
2. **가중치 슬라이더** — 슬롯마다 슬라이더, 합계, 과가중치 경고 색 바.
3. **고정 + 리롤** — 슬롯 잠그고, 잠기지 않은 슬롯만 다시 뽑기.
4. **믹스 비교** — 같은 시드로 믹스 2~3개를 나란히 생성.
5. **믹스 레시피 저장** — 이름 붙인 4명+가중치 목록. 불러오기/이름 변경/삭제. 백업에 포함.
6. **벨 번들 썸네일 제거 + 사용자 썸네일** — `docs/artists/*`와 그 참조를 지우고, 폰에서 고른 이미지를 작가마다 넣기.

## 지금 v2.9에 이미 있는 것 (이름을 유지하고 확장)

코드는 코어 스크립트와 레이어로 나뉘어 있습니다. 부팅: `migrateArtistVaultV29()` → `bootArtistVault()` → `bootArtistMixer()` (약 13176행). 믹스 UI는 `#artist-vault-fold` 뒤에 런타임으로 만듭니다. `downloadSelfHTML`은 `#artist-mixer-fold`를 저장본에서 제거하므로, 부팅 때 다시 만들어야 합니다.

| 이름 | 역할 |
|---|---|
| `artistMixerSlots` | 길이 4 배열. `{tag, weight, locked}`. 기본 가중치 1, `locked:false` |
| `artistMixerPreviewText()` | 태그가 있는 슬롯을 `1::artist:name::, …` 로 이어 붙임. **지금은 2명 이상이면 문자열을 만듦** → 이번엔 레시피/비교/화풍 저장은 **4명 채워졌을 때만** 되게 바꾸세요. |
| `paintArtistMixerPreview()` | `#artist-mixer-preview`, `#artist-mixer-save` 활성 |
| `refreshArtistMixerOptions()` | `#artist-mixer-slots`에 행을 다시 그림. 즐겨찾기(`pinned`)가 목록 위 |
| `#artist-mixer-slot-0`…`3` | 작가 `<select>` |
| `#artist-mixer-weight-0`…`3` | 지금은 `type="number"` 0.5–2.0, step 0.05 |
| `#artist-mixer-lock-0`…`3` | 잠금 버튼. `aria-pressed`, 🔒/🔓 |
| `.rd-mix-thumb` | 슬롯 썸네일 `<img>` |
| `paintArtistMixerThumb(img, item)` | **지금은 `item.no`로 `artists/NNN.webp`를 넣음. 이 경로를 없애고 사용자 썸네일로 교체** |
| `rollArtistMixer(recipe)` | 잠긴 슬롯은 유지, 가중치는 항상 1로 리셋. 잠기지 않은 칸에 중복 없이 배정 |
| `ARTIST_MIXER_RECIPES_V29` | 지금: `fav`, `fav_semi`, `semi_gen`, `all`. **요청 풀 4개에 맞게 재구성** |
| `saveArtistMixerStyle()` | `#artist-mixer-name`으로 **커스텀 화풍**(`mix_…`, `readArtStyles()` / `ART_STYLES_KEY`)에 저장 후 선택. 이 버튼은 유지해도 됩니다. **믹스 레시피는 이와 별도 목록** |
| `pasteArtistMixerPool()` / `#artist-mixer-paste` / `#artist-mixer-add` | 작가 풀에 붙여넣기 추가. 유지 |
| `#artist-mixer-status` | 상태 문구 |
| `normArtistKey(raw)` / `readArtistVault()` / `writeArtistVault()` / `makeVaultArtist()` | 저장소. 키 `nai_artist_vault_v1`. 항목: `{id, tag, category, weight, pinned, memo, no?}` |
| `paintArtistVault()` | `#vault-list`에 `.vault-chip` (`dataset.val`, 있으면 `dataset.no`) |
| `filterVaultArtists()` | `__fav` / `__mine` / 카테고리 / 이름·번호 검색 |
| `editVault(card)` | 작가 시트(`rdUx`). 지금 벨 샘플 `#` 큰 그림 |
| `decorateVault()` / `decorateMixer()` | `#rd-shell-js` 레이어. 카드 썸네일 `.rd-av.rd-av-img`, `+ 슬롯`(`quickAdd`), 가중치 ±(`.rd-wstep`)와 `.rd-wbar` |
| `tagMixer()` / `tagVault()` | `#rd-addon`. `data-cat` (`gen`/`semi` 등) |
| `pushUndo` / `writeStorageWithUndo` | 슬롯·저장소 변경은 기존 되돌리기에 타야 함 |
| `window.exportSettings` / `importSettings` | 백업 JSON. 지금은 `artistVault`를 포함. **키(`rd_nai_key_v1`)는 넣지 않음** |
| `window.rdNai` | `readPrompt`, `buildBody`, `isFree`, `unzipFirstImage`, `galList`/`galOpen`, `_ENDPOINT`, `_KEY_LS` |
| `FREE_PIXELS=1048576`, `FREE_STEPS=28` | `isFree(o)` = `width*height<=1048576` 이고 `steps<=28`. `buildBody`의 `n_samples`는 이미 1 |
| `busy` / `#rd-nai-cancel` / 429 처리 | 스튜디오 `generate()`, `previewGen()`, 체위 썸네일 만들기는 **자동 재시도 없음**. 비교도 같은 규칙을 따르세요. 전역 `busy`가 켜져 있으면 새 생성을 시작하지 마세요. |
| `shuffle()` | `rollArtistMixer`가 이미 사용. **코어 `generate()` 경로에 `Math.random`을 넣지 마세요.** |

랜덤 풀 판별: 즐겨찾기 = `item.pinned`, 반실사 = `item.category==="반실사"`, 일반 = 반실사가 아닌 항목, 전체 = 저장소 전부. `VAULT_CATS = ["일반", "반실사"]`.

## 1. 랜덤 믹스

버튼 행을 다음 4개 풀로 맞추세요. (기존 `semi_gen` 배합은 빼도 됩니다.)

- ★ 즐겨찾기
- 반실사
- 전체
- ★ 즐겨찾기 + 반실사 (예: 즐겨찾기에서 2, 반실사에서 2. 한쪽이 부족하면 다른 쪽에서 채워 4명을 맞추고, 그래도 부족하면 상태 문구로 알리기)

동작:

- 잠기지 않은 슬롯만 다시 채웁니다. 잠긴 슬롯의 `tag`와 `weight`는 그대로.
- **4명 고정:** 잠기지 않은 칸을 가능한 한 다 채우고, 서로 다른 작가여야 합니다. 이미 잠긴 태그와도 중복 금지.
- **가중치도 랜덤.** 범위는 기존과 같이 0.5–2.0, 0.05 단위. 한 명은 메인이 되도록 1.2–2.0, 나머지는 0.5–1.15처럼 나눠도 됩니다. 전부 1.00으로 두지 마세요.
- 마지막에 쓴 풀을 기억해 두고, 「리롤」은 그 풀(없으면 전체)로 `rollArtistMixer`를 다시 호출하면 됩니다.
- 후보가 없거나 전부 잠겼으면 지금처럼 `#artist-mixer-status`에만 알리고, 슬롯을 비우지 마세요.

## 2. 가중치 슬라이더 + 합계 + 경고 바

- `#artist-mixer-weight-0`…`3`을 슬라이더(`type="range"`)로 바꾸거나, 슬라이더+숫자 표시를 함께 두세요. 범위 0.5–2.0, step 0.05. 값 변경 시 `artistMixerSlots[i].weight`를 갱신하고 `paintArtistMixerPreview()`, `pushUndo`는 기존과 같이.
- 레이어 `decorateMixer()`의 ± 버튼(`.rd-wstep`)·`.rd-wbar`와 충돌하지 않게, 한 가지 UI로 정리하세요. 터치 영역은 44px 이상, 글자 13px 이상.
- **네 슬롯 가중치 합계**를 믹스기 안에 항상 보여 주세요.
- **과가중치 경고 바:** 합계가 4.5를 넘거나 한 슬롯이 1.6을 넘으면 주황/빨강으로 바를 바꾸고 짧은 경고 문구. 합계가 낮으면 평소 색. 생성은 막지 마세요(경고만).
- `stabilizeWeights`(⚖️ 가중치 안정화)는 장면 프롬프트용입니다. 믹스 미리보기 `N::artist:…::` 문자열을 자동으로 깎지 마세요.

## 3. 고정과 리롤

- 기존 슬롯 잠금(`#artist-mixer-lock-*`, `slot.locked`)을 유지하세요.
- **리롤** 버튼을 명확히 두세요. 잠기지 않은 슬롯만 작가+가중치를 다시 뽑고, 잠긴 슬롯은 작가와 가중치를 유지합니다. `rollArtistMixer`를 확장하면 됩니다.
- 작가 카드의 `+ 슬롯`(`quickAdd`)도 잠긴/찬 슬롯 규칙을 지금처럼 지키세요.

## 4. 믹스 비교

같은 시드로 믹스 **2장 또는 3장**을 나란히 보여 줍니다. (A/B 또는 A/B/C)

- **사용자가 시작 버튼을 눌렀을 때만** 생성합니다. 칩 변경·앱 시작·미리보기로 자동 호출 금지.
- 시작 전에 요청 수(2 또는 3)를 보여 주세요.
- **한 장씩 순서대로.** 장 사이에 약 **1.5초** 간격을 둡니다.
- **중지** 버튼을 두고, 누르면 다음 장을 시작하지 않습니다. 진행 중인 fetch는 기존처럼 `AbortController`로 취소해도 됩니다(`#rd-nai-cancel` 패턴).
- **HTTP 429면 즉시 중단, 재시도 없음.** 이미 나온 장은 남기고, 토스트/상태로 알리세요. (체위 썸네일·미리보기와 동일한 정책, 약 399–400행, 14533행)
- **유료 Anlas 가드:** `rdNai.isFree(opts)`가 거짓이면 생성하지 않습니다. Opus 무료 기준은 이미 코드에 있습니다: 픽셀 면적 ≤ 1024×1024(`FREE_PIXELS=1048576`), steps ≤ 28, `n_samples` 1. 크기·스텝이 유료면 막고, 필요하면 확인창 뒤에만 진행하게 할 수 있습니다. 확인 없이 유료 요청을 보내지 마세요.
- 시드는 비교 세션 동안 고정. 스튜디오의 시드 잠금(`rd_nai_opts_v1` / `#rd-nai-seedlock`)이 꺼져 있어도, 비교 첫 장에서 정한 시드를 나머지에 재사용하세요.
- 구현 힌트: 코어 `generate()`를 고쳐 섞지 마세요. `rdNai.readPrompt()`(또는 스튜디오 `readStudioPrompt`) 결과를 복사하고, **그 요청의 그림체 작가 태그만** 각 믹스의 `artistMixerPreviewText()` 형식 문자열로 바꿔 `rdNai.buildBody(p, o, seed)` → `fetch(rdNai._ENDPOINT)` → `unzipFirstImage` → `galAdd` 순으로 보내세요. 블루아카 등 **현재 선택된 그림체(`selectedArtId` / `getSelectedArtStyle()`)는 비교가 끝난 뒤에도 그대로**여야 합니다.
- 스튜디오·미리보기·체위 썸네일과 **동시에** 돌리지 마세요. 기존 `busy`를 재사용하세요.
- 결과는 비교 패널에 나란히 표시하고, 기록(갤러리 IDB)에도 지금 생성과 같이 쌓이면 됩니다. 마음에 든 믹스는 레시피로 저장할 수 있게 해 주세요.
- 커버 476×660에서 가로로 넘치지 않게, 비교 이미지는 세로 나열 또는 가로 스크롤로 맞추세요. 펼침 933×612에서는 나란히 보여도 됩니다.

## 5. 믹스 레시피 저장

작가 4명 + 가중치를 **이름 붙여 따로** 저장합니다. `saveArtistMixerStyle()`의 커스텀 화풍 목록과 섞지 마세요.

- 새 localStorage 키를 쓰세요. 제안: `nai_mix_recipes_v1`.
- 항목 예: `{id, name, slots:[{tag, weight}, {tag, weight}, {tag, weight}, {tag, weight}]}`. `tag`는 `normArtistKey` 결과.
- 목록 · 불러오기(슬롯 4개에 반영, 잠금 상태는 유지하거나 모두 해제 — 불러오기 후 상태 문구로 안내) · 이름 변경 · 삭제. 삭제·덮어쓰기는 확인.
- 4명이 다 채워지지 않으면 저장하지 말고 알려 주세요.
- **`exportSettings` / `importSettings`에 `mixRecipes` 필드로 포함.** 옛 백업에 이 필드가 없으면 무시하고 나머지(작가 저장소 등)는 지금처럼 복구. 백업에 `rd_*` 키나 API 키를 넣지 마세요.
- 슬롯 변경과 같이 되돌리기(`pushUndo`)에 넣으면 좋습니다.

## 6. 번들 썸네일 제거 + 사용자 썸네일

태준님이 직접 넣을 수 있게, **추가 기능만** 넣습니다. 번들 벨 샘플은 빼세요.

제거할 것:

- 저장소 폴더 `docs/artists/` 전체 (`NNN.webp`, `l/NNN.webp` 포함)
- `artistThumbSrc(no, large)`의 `"artists/" + … + ".webp"` 경로와 그 호출
- `decorateVault()`의 벨 샘플 자동 부착, `editVault()`의 `rd-sh-artist` 벨 큰 이미지, `paintArtistMixerThumb`의 번호 기반 파일 로딩
- 주석·패치 노트의 “벨 샘플 썸네일” 설명. `item.no`(목록 번호)와 검색·필터는 유지

넣을 것:

- 작가마다 이미지를 **폰에서 고르기**. `<input type="file" accept="image/*">`를 쓰세요. 앱 WebView는 이미 `onShowFileChooser`가 있어 사진 선택이 됩니다. (`#import-file`과 같은 방식, 이미지용으로 따로)
- **클라이언트에서만** 리사이즈(긴 변 약 160px, JPEG/WebP, 적당한 품질). 원본 파일을 그대로 IDB에 넣지 마세요.
- **IndexedDB에 저장.** 기존 `rd-nai-gallery` / `rd-nai-history` / `rd-pose-thumbs`의 버전·스토어를 바꾸지 마세요. **새 DB**를 만드세요. 제안: DB `rd-artist-thumbs`, store `thumbs`, keyPath는 `normArtistKey(tag)` (또는 `key`).
- 썸네일이 있는 작가는 **저장소 카드(`.vault-chip`)**, **작가 시트(`editVault`)**, **믹스 슬롯(`.rd-mix-thumb`)**에 같은 그림이 보여야 합니다. 없으면 지금처럼 이니셜(`.rd-av`)만.
- 카드/시트에서 넣기 · 바꾸기 · 삭제(확인). 터치 44px 이상.
- **백업에 포함.** `exportSettings` JSON에 예: `artistThumbs: [{key, mime, data(base64)}]` . import 때 IDB에 다시 넣기. API 키는 넣지 않음. 용량이 커질 수 있으니 리사이즈를 꼭 지키세요. localStorage에 이진/data URL을 넣지 마세요(할당량).
- HTML 저장 파일이나 GitHub에 사용자 이미지가 들어가면 안 됩니다. (`data-rd-ephemeral`, 런타임 위젯 제거와 같은 주의)

## 제약 (깨면 실패)

- 믹스기를 **쓰지 않은** 상태(슬롯이 비었거나, 커스텀 믹스 화풍을 선택하지 않음)에서 **블루아카 프롬프트는 v2.9와 바이트 단위로 같아야** 합니다. 코어 `generate()`에 믹스 문자열을 항상 넣지 마세요. 지금처럼 화풍으로 저장해 선택하거나, 비교 요청에만 임시로 넣으세요.
- 저장 호환: `rd_nai_key_v1`, 기존 IndexedDB 스토어 이름, `rdHandleBack`, `AndroidBridge.saveBase64`. 옛 백업·작가 저장소·장면 슬롯이 그대로 열려야 합니다.
- **자동 API 호출 금지.** 비교·생성은 버튼으로만.
- 폴드8: 폰트 ≥13px, 터치 ≥44px, 커버 476×660 / 펼침 933×612에서 가로 넘침 없음. 슬롯 한 줄(썸네일+선택+슬라이더+잠금)이 커버에서 깨지면 두 줄로 접으세요.
- 외부 요청은 NAI 이미지 생성만.
- 앱 안 패치 노트와 `CHANGELOG_handoff.md`를 같은 내용으로 갱신하고, `docs/version.json`의 `web` / `web_updated`를 올리세요.

## 산출 · 검사

1. 전체 `docs/index.html`
2. `docs/version.json` 버전  bump
3. 앱 안 패치 노트 + `CHANGELOG_handoff.md`
4. `docs/artists/` 삭제 (번들 썸네일 제거의 일부)
5. 푸시 전:

```
python3 tools/scan_secrets.py
python3 tools/check_index.py docs/index.html
```

가능하면 기존 테스트도 블루아카 기준으로 돌려 주세요 (`functest2` 바이트 동일, `naitest` 키가 백업/HTML에 없음, `galtest`, `uxtest`, `previewtest`, `apptest`). 비교 기능이 유료 설정을 막는지, 429에서 멈추는지만 수동으로라도 확인하세요.

PR로 올린 뒤 `docs-check`가 초록인지 확인하고 합칩니다. (`UPDATE_GUIDE.md`)
