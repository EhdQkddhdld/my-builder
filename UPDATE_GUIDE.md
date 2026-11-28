# My Builder — 혼자 업데이트하는 법

> **2026-11-28 운영 갱신:** AI 협업·QA·배포는 [PLAYBOOK.md](PLAYBOOK.md)가 최신 절차다. 아래 과거 역할/수동 배포 설명보다 우선한다. 사용자 승인, 필수 검사 및 Neon 독립 검수 없이 main 반영 금지. QA 브랜치 전체 병합 금지. 기술 보호 계약은 그대로 유효하다.

앱은 GitHub Pages 주소(`https://ehdqkddhdld.github.io/my-builder/`)만 엽니다. 저장소의 `docs/index.html`을 바꾸면, **앱을 완전히 종료했다가 다시 열 때** 새 버전이 적용됩니다. APK를 다시 설치할 필요는 없습니다.

**추천 방법:** 새 가지(브랜치)에 올리고 검사(PR)가 초록색인지 확인한 뒤 합치기. `main`에 바로 올리면, 검사가 실패해도 이미 앱 주소에 반영될 수 있습니다.

아래 버튼 이름은 화면·앱 버전에 따라 조금 다를 수 있습니다. 모바일 웹(Chrome / 삼성 인터넷)으로 [저장소](https://github.com/EhdQkddhdld/my-builder)를 여는 편이 좋아요. GitHub 앱은 파일 올리기가 불편할 수 있습니다.

## 1. 준비

1. 아스트라/GPT가 만든 **전체** `index.html`을 폰에 받아 둡니다. 이름이 정확히 `index.html`이어야 합니다.
2. 버전 번호를 정합니다. (예: 지금 2.9 → 다음 2.10)

## 2. 새 가지에 파일 올리기 (추천)

1. 저장소에서 `docs` 폴더로 들어갑니다.
2. `Add file` → `Upload files`(파일 올리기)를 누릅니다.
3. 새 `index.html`을 올립니다. `docs` 안에서 올리면 기존 파일을 덮습니다.
4. 아래 커밋 상자에서 **main에 바로 커밋하지 말고** `Create a new branch` / 새 브랜치 만들기를 고릅니다. 이름 예: `update-2.10`
5. `Commit` / `Propose changes`를 누릅니다.
6. `Create pull request` 또는 `Compare & pull request`가 뜨면 눌러 main으로 요청을 만듭니다. 제목은 `v2.10`처럼 적어도 됩니다.

## 3. 버전 파일도 같이 올리기

`docs/version.json`은 작은 파일이라 브라우저에서 바로 고치면 됩니다.

1. 방금 만든 가지가 선택된 상태에서 `docs/version.json`을 엽니다.
2. 연필(Edit) 아이콘을 누릅니다.
3. `web`을 새 버전으로, `web_updated`를 오늘 날짜(`YYYY-MM-DD`)로 바꿉니다. 다른 줄은 그대로 둡니다.
4. 같은 가지에 커밋합니다. PR에 자동으로 붙습니다.

## 4. 초록 검사 확인 후 합치기

1. PR 화면의 검사(`Docs check` / `docs-check`)가 초록색이 될 때까지 기다립니다. 보통 1~2분입니다.
2. 빨간색이면 **합치지 마세요.** 로그를 만든 AI에게 보여 주세요. 흔한 원인: 파일이 잘림, JS 괄호 오류, API 키·토큰이 파일에 들어감, 앱 계약 문자열 삭제.
3. 초록이면 `Merge pull request` → `Confirm merge`.
4. 1~2분 기다립니다. 웹 주소에도 반영됩니다.

## 5. 폰에서 확인

1. 최근 앱 화면을 열고 My Builder를 **위로 밀어 완전히 종료**합니다. 홈으로만 나가면 예전 화면이 남을 수 있습니다.
2. 앱을 다시 엽니다.
3. 제목이나 메뉴의 패치 노트가 새 버전인지 확인합니다.

## 6. 되돌리기

PR로 합친 경우:

1. GitHub에서 방금 합친 Pull request를 엽니다.
2. `Revert`를 누릅니다. (합쳐진 PR 본문 위쪽이나 대화 탭 근처. 위치가 다를 수 있습니다.)
3. 생기는 되돌리기 PR을 다시 합칩니다.
4. 1~2분 뒤 앱을 완전히 종료하고 다시 엽니다.

`Revert`가 안 보이거나 충돌이 나면, 저장소 `Commits` 또는 `docs/index.html`의 `History`에서 이전 파일을 열어 받은 뒤, 2~4절처럼 새 가지에 다시 올리고 합칩니다. 그 이후에 다른 커밋이 더 있으면 다른 AI에게 도움을 요청하세요.

## 다른 방법: main에 바로 올리기

급하면 `docs`에서 파일을 올린 뒤 `Commit directly to the main branch`를 고를 수 있습니다. 검사는 **올린 뒤에** 돌아가므로, 실패해도 잠시 앱에 잘못된 버전이 보일 수 있습니다. 가능하면 PR 방법을 쓰세요.

## 한 번만 해 두면 좋은 설정

- 저장소 `Settings` → `Actions`가 켜져 있는지 확인합니다. 공개 저장소는 보통 기본으로 켜져 있습니다. 검사가 아예 안 뜨면 여기부터 보세요.
- 더 안전하게: `Settings` → `Branches`에서 `main` 보호 규칙을 넣고, `docs-check` 검사가 통과해야 합쳐지게 할 수 있습니다. 없어도 사용은 가능합니다.

로컬/AI 검사용 명령: `python3 tools/scan_secrets.py`, `python3 tools/check_index.py docs/index.html`
