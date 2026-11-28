# My Builder (젬의 NAI V5 프롬프트 빌더 리디자인)

- 웹 앱: https://ehdqkddhdld.github.io/my-builder/
- Android APK: https://github.com/EhdQkddhdld/my-builder/releases/latest
- 현재 버전은 [docs/version.json](docs/version.json)과 실제 main/Pages를 조회해 판단한다.

## AI 작업 시작 — 필수

1. [PLAYBOOK.md](PLAYBOOK.md): 최신 협업 체계, GitHub-first 실행 절차, QA 증거 승계, 장애 우회, 원자적 배포.
2. [AGENTS.md](AGENTS.md): 보호 계약 및 기술 규약.
3. 최신 main과 대상 QA 브랜치 README, 승인 시안/명세, 제품 후보 커밋과 검사 증거를 확인한다.

Sol(Chat 중심, Work 보조)은 기획·디자인·구현·자체 검수·QA 브랜치 관리, Neon Task는 독립 검수, 기존 업데이트 챗은 최종 대조·배포를 담당한다. 사용자가 중대 변경·배포를 승인한다. 다른 챗의 상태나 권한이 자동 공유된다고 가정하지 않는다. 과거 인수인계 문서의 역할과 버전은 역사 기록이다.

## 제품 구조

- `docs/index.html`: 단일 HTML 앱 본체
- `docs/version.json`: 웹/앱 버전
- `android/`: WebView 앱 (패키지 app.mybuilder)
- `CHANGELOG_handoff.md`, `docs/CHANGELOG_handoff.md`: 기술·변경 이력

## 웹 배포

QA 브랜치에서 승인 후보를 확정하고 공식 검사 및 독립 검수를 완료한다. 사용자 승인 후 업데이트실이 최신 main을 기준으로 승인된 제품 파일만 단일 커밋에 반영한다. QA 브랜치 전체 병합 금지. 웹 배포는 Android 수정이나 APK 재설치를 요구하지 않는다.

공식 검사: `python3 tools/scan_secrets.py`, `python3 tools/check_index.py docs/index.html`, `git diff --check`. 실패/미완료 시 배포 금지. NAI 키·토큰·서명키·개인 작품/백업은 공개 QA 브랜치에도 올리지 않는다. 동일 선택의 기존 프롬프트 출력과 보호 계약을 보존한다.

GitHub Actions와 Pages 배포 성공, 실제 서비스 HTTP, Fold8 실기기 확인은 서로 별개의 판정이다.
