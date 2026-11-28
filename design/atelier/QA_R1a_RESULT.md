# R1a 실행 검사 결과 — 2026-11-28
- 제품 커밋: 4b315e557ce7b505b18558287800f57349b8ce26
- 제품 blob: f8f10bb2bb841da971a7fc35ab79bcfe53707573
- 제품 SHA-256: dc14403c944ad3439e8e860eef483b07b8c1e43bf69123d60f1dffef01ef9e0c
- QA 실행 커밋: dc7778938bf9350df4ca57b36e4033bf78bb46fa
- Actions: https://github.com/EhdQkddhdld/my-builder/actions/runs/46103858143
- Artifact ID: 15246309746, digest: sha256:97693a3d7347f2488ccf0bfdbd2fb9ed5658dd61acc4f73e52915fa7c285538b
- 다운로드한 ZIP의 navigation.json, SHA256.txt, security.txt, html.txt 직접 확인. 커버/펼침 PNG 직접 확인.
- 공식 검사: secret scan OK (533 files); check_index OK (1425223 bytes, 11 contracts, inline script syntax); diff --check는 성공한 동일 Actions step의 선행 명령.
- Chromium 실제 HTTP, 외부 네트워크 차단, 화면별 신규 컨텍스트.

| 규격 | 초기 위치 | 반전 | 결과 |
|---|---|---|---|
| 476x660 | 오른쪽 | 왼쪽 | PASS |
| 839x660 | 오른쪽 | 왼쪽 | PASS |
| 840x660 | 왼쪽 | 오른쪽 | PASS |
| 933x612 | 왼쪽 | 오른쪽 | PASS |

각 표본에서 레일 56px, 위치 버튼 44x44px, 레일 버튼 최소 크기, 가로 넘침, 위치 반전, 화면별 위치 유지, 재로드 복원, 홈 숨김, 위치 변경 전후 captureState 동일, JS 예외 없음 확인.
시각 검토: 기존 4단계와 카드 구조가 표시됨. 승인 최종 시안 전체가 구현된 것은 아니다.
원본 캡처 4개는 Actions Artifact에 보관(7일 만료), 영구 Git 바이너리 보관 미완료.
미검증: 상세 편집 흐름, 저장 HTML 2세대, 전체 상태·Undo·저장 회귀, 독립 검수, 실기기. 배포 후보 아님. main 변경 없음.
