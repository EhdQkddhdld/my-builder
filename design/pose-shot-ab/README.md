# My Builder v3.3.9 · 체위·샷 A/B 비교

- 기준 main: `918d3eb3e45b97171d40ca3cfc625618f86d4589` (v3.3.8)
- [첨부 명세](POSE_SHOT_AB_TEST_SPEC.md) · [오버레이 표](POSE_SHOT_AB_PATCHES.json)
- 후보 HTML blob: `0d5ac80bfa7246142deaf7f064bf70defec5038d`
- 로컬 필수 검사 및 보호 코드 15종 원문 대조 PASS
- Chromium에서 최신 main 대비 122개 체위·샷 조합 출력/복사 일치 및 비교 중 상태 불변 확인. 네 해상도에서 두 진입점의 레이아웃과 복사 동작 확인.
- [고정 Auto QA](https://github.com/EhdQkddhdld/my-builder/actions/workflows/auto-qa.yml?query=branch%3Aqa%2Fv3.3.9-pose-shot-ab)
- DEEP_TRACK. Neon 독립 판정 후 배포. 제품 반영 대상은 `docs/index.html`과 `docs/version.json`.
