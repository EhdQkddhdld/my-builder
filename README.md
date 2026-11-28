# My Builder (젬의 NAI V5 프롬프트 빌더 리디자인)

## COMMON STUDIO (v3.2, 2026-11-29)

Google Drive의 COMMON STUDIO 폴더는 양 AI 공용 산출물·검수·인계 저장소다. GitHub 제품 코드·버전·QA·배포 기준은 유지하며 Chat Sol이 GitHub 쓰기 및 배포를 전담한다. Neon은 Drive에서 연구·자문·독립 검수와 수정안을 기록한다. 다음 담당자 메시지는 복사 가능한 블록(지원 시 복사 버튼)으로 필수 제공한다. 세부 운영은 PROJECT_GUIDELINES.md의 0절이 우선한다.

- 웹 앱: https://ehdqkddhdld.github.io/my-builder/
- Android APK: https://github.com/EhdQkddhdld/my-builder/releases/latest
- 현재 버전은 [docs/version.json](docs/version.json)과 실제 main/Pages를 조회해 판단한다.

## AI 작업 시작 — 필수

1. [PROJECT_GUIDELINES.md](PROJECT_GUIDELINES.md): ChatGPT와 Neon 양 AI 공통 최신 통합 지침.
2. [PLAYBOOK.md](PLAYBOOK.md): 최신 협업 체계, GitHub-first 실행 절차, QA 증거 승계, 장애 우회, 원자적 배포.
3. [AGENTS.md](AGENTS.md): 보호 계약 및 기술 규약.
4. 최신 main과 대상 QA 브랜치 README, 승인 시안/명세, 제품 후보 커밋과 검사 증거를 확인한다.

Chat Sol은 기획부터 배포까지 총괄하고 Work는 보조한다. Neon Task는 전문 연구·자문·정밀 트랙 독립 검수를 담당한다. 사용자가 중대 변경·배포를 승인한다. 다른 챗의 상태나 권한이 자동 공유된다고 가정하지 않는다. 과거 인수인계 문서의 역할과 버전은 역사 기록이다.

## 제품 구조

- `docs/index.html`: 단일 HTML 앱 본체
- `docs/version.json`: 웹/앱 버전
- `android/`: WebView 앱 (패키지 app.mybuilder)
- `CHANGELOG_handoff.md`, `docs/CHANGELOG_handoff.md`: 기술·변경 이력

## 웹 배포

고정 Auto QA를 사용한다. UI/디자인 전용·보호 블록 15종 불변·Actions 성공 시 빠른 트랙, 엔진·체위/샷·저장소/API 변경은 Neon 정밀 검수 트랙이다. 사용자 승인 후 Chat Sol이 최신 main을 기준으로 승인된 제품 파일만 단일 커밋에 반영한다. QA 브랜치 전체 병합 금지. 웹 배포는 Android 수정이나 APK 재설치를 요구하지 않는다.

원클릭 버전 갱신 및 poses.json 데이터 분리는 후속 구현 과제다. 세부 절차와 상태는 PLAYBOOK을 확인한다.

공식 검사: `python3 tools/scan_secrets.py`, `python3 tools/check_index.py docs/index.html`, `git diff --check`. 실패/미완료 시 배포 금지. NAI 키·토큰·서명키·개인 작품/백업은 공개 QA 브랜치에도 올리지 않는다. 동일 선택의 기존 프롬프트 출력과 보호 계약을 보존한다.

GitHub Actions와 Pages 배포 성공, 실제 서비스 HTTP, Fold8 실기기 확인은 서로 별개의 판정이다.
