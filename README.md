# My Builder (젬의 NAI V5 프롬프트 빌더 리디자인)

- 웹 주소(앱이 여는 곳): https://ehdqkddhdld.github.io/my-builder/
- 안드로이드 앱(APK) 받기: https://github.com/EhdQkddhdld/my-builder/releases/latest

## 구조
- `docs/index.html` — 앱 본체(HTML 한 파일). **이 파일만 고쳐서 올리면** 앱을 다시 설치하지 않아도 반영됨.
- `docs/version.json` — 웹/앱 버전 메모.
- `android/` — WebView 껍데기 앱 소스(My Builder, `app.mybuilder`).
- `CHANGELOG_handoff.md` / `UPDATE_PLAN.md` — 수정 내역과 규칙(다른 AI에게 같이 주기).

## 업데이트 방법 (HTML)
1. `docs/index.html`을 고침.
2. `python3 tools/scan_secrets.py`로 키가 섞이지 않았는지 확인.
3. main 브랜치에 커밋·푸시. 1~2분 뒤 Pages에 반영.
4. 폰에서 앱을 완전히 닫았다가(최근 앱에서 밀어서 종료) 다시 열면 새 버전이 뜸.

## 꼭 지킬 것
- NAI API 키는 폰 안(localStorage `rd_nai_key_v1`)에만 있음. **저장소에 키·토큰·서명 키를 절대 올리지 않음.**
- 같은 선택이면 프롬프트 결과가 원본과 같아야 함. 레이어 코드에서 `Math.random` 금지.
- 자세한 규칙은 `CHANGELOG_handoff.md` 참고.
