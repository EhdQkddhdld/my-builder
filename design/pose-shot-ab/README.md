# My Builder v3.3.10 · 체위·샷 A/B 비교

- 기준 main: `e359c5d3011c9f813c46f7464662fc07a302186d` (v3.3.9 UI 통합판)
- 선행 후보: `998548d54fdde7e47bd1d0ff4eacc2c07549a48d`
- [첨부 명세](POSE_SHOT_AB_TEST_SPEC.md) · [오버레이 표](POSE_SHOT_AB_PATCHES.json)
- 후보 HTML blob: `0ccc5df6a7703c9c5e831dd81402ddaddd61abd0`
- A 프롬프트는 `p=pair.a`로 읽고 `[p,pair.b]` 순으로 요청한다.
- 로컬 필수 검사 및 보호 코드 15종 원문 대조 PASS.
- [고정 Auto QA](https://github.com/EhdQkddhdld/my-builder/actions/workflows/auto-qa.yml?query=branch%3Aqa%2Fv3.3.10-pose-shot-ab)
- DEEP_TRACK. Neon 독립 판정 후 배포. 제품 반영 대상은 `docs/index.html`과 `docs/version.json`.
