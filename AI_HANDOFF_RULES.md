# My Builder — 다른 AI 인수인계 규칙

> **2026-11-28 운영 갱신 v3.1:** [양 AI 통합 지침](PROJECT_GUIDELINES.md)과 [PLAYBOOK.md](PLAYBOOK.md)가 최신 절차다. Chat Sol 통합 운영, 고정 Auto QA, 빠른/정밀 트랙을 적용한다. UI 전용·보호 15종 불변·Actions 성공이면 Neon 검수 생략, 엔진·체위/샷·저장소/API 변경만 정밀 검수. 버전별 ZIP/검수 보고서/patch 묶음 금지. 아래 과거 역할·수동 배포·산출물 설명보다 최신 지침 우선. 기술 보호 계약은 유지한다.

대상: 네온 · 아스트라 · GPT · 그록 등. 이 저장소만 보고 이어서 수정할 수 있어야 합니다.
저장소: https://github.com/EhdQkddhdld/my-builder (공개, 브랜치 main)
웹 주소(앱이 여는 곳): https://ehdqkddhdld.github.io/my-builder/
코어: Gem's NAI V5 Prompt Builder v3.67.0. 기기: Galaxy Z Fold8.

배포 방법은 `UPDATE_GUIDE.md`를 따릅니다. 토큰·NAI 키·서명 키는 절대 공유하거나 커밋하지 마세요.

## 산출물

- **고칠 파일은 `docs/index.html` 전체본 하나.** 패치 조각, diff, 부분 파일만 주지 마세요.
- 원본 HTML, 이전 버전 HTML, `android/` 앱 껍데기는 요청 없이 수정하지 마세요.
- 믹스기 강화는 `MIXER_UPGRADE_SPEC.md`를 따릅니다.

## 절대 바꾸면 안 되는 계약

1. **같은 선택이면 프롬프트 결과가 같아야 합니다.** 레이어/추가 코드에서 `Math.random`을 쓰면 카오스 비교가 깨집니다. 믹스기를 쓰지 않은 상태에서 블루아카 프롬프트는 바이트 단위로 같아야 합니다.
2. **NAI API 키는 기기 localStorage `rd_nai_key_v1`에만.** HTML, 백업 JSON, 갤러리 메타, GitHub에 넣지 마세요. `pst-…` 키, GitHub 토큰, 서명 키(`.jks`) 커밋 금지. '키 지우기' 버튼은 유지.
3. **앱 브리지·뒤로가기**
   - `window.rdHandleBack()` — 열린 창을 하나 닫고, 닫을 게 없으면 `false`(앱 종료)
   - `AndroidBridge.saveBase64(b64, name, mime)`, `copyText`, `haptic`, `shareText`
4. **저장소 이름 유지**
   - localStorage: `rd_nai_key_v1`, `rd_nai_opts_v1`, `rd_nai_gal_migrated_v1`, `nai_artist_vault_v1`, `nai_v29_arca_artists_seeded`, `nai_art_styles_v2`(+v1), `nai_custom_art_v1`, `nai_char_custom_v1`, `nai_favorites_v1`, `nai_v5_gem_presets_v310`(+`_preset_v31`), `nai_sequence_v1`, `nai_history`
   - IndexedDB: `rd-nai-gallery` (`meta`, `full`), 이전용 `rd-nai-history` (`img`), `rd-pose-thumbs` (`thumbs`). 기존 DB 스키마를 깨지 마세요. 새 데이터가 필요하면 **새 DB/새 키**를 추가하세요.
5. 외부 요청은 NAI 이미지 생성만. 자동으로 API를 호출하지 마세요. 429면 즉시 중단하고 재시도하지 마세요.
6. 폴드8: 글자 최소 13px, 터치 영역 최소 44px. 커버 476×660, 펼침 933×612에서 가로로 넘치면 안 됩니다.
7. HTML 저장(`downloadSelfHTML`) 후 다시 열어도 DOM이 중복되면 안 됩니다. 런타임 위젯(`#artist-mixer-fold` 등)은 저장본에서 빼고 부팅 때 다시 만듭니다.

## 버전과 변경 기록

1. `docs/version.json`의 `web`을 올리고 `web_updated`를 오늘 날짜(`YYYY-MM-DD`)로 바꿉니다. 웹만 바꾸면 `apk` / `apk_version_code`는 그대로입니다.
2. HTML의 `<title>`, 화면 버전 표기, 앱 안 패치 노트(패치 접힌 칸)를 같은 버전으로 맞춥니다.
3. `CHANGELOG_handoff.md`에도 같은 내용을 남깁니다.

## 배포 전 검사

```
python3 tools/scan_secrets.py
python3 tools/check_index.py docs/index.html
```

사용자는 새 가지에 올린 뒤 PR 검사(`docs-check`)가 초록색이면 합칩니다. 실패하면 합치지 않습니다. 자세한 탭 순서는 `UPDATE_GUIDE.md`.
