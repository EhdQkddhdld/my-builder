# R1a: 세로 단계 레일 구현 체크포인트

- 제품 커밋: 4b315e557ce7b505b18558287800f57349b8ce26
- 제품 blob: f8f10bb2bb841da971a7fc35ab79bcfe53707573
- 기준 blob: 12233467a182a9354529b3571c2bb6ea9ab12fd8
- 기존 HTML에 UI CSS/JS 두 블록만 삽입. 제거 시 기준 문자열 완전 일치, 원격 blob 재조회 일치.
- 기존 단계 버튼, 이벤트 및 상세 편집 구조 유지. 기본 커버 우측/펼침 좌측, 화면별 위치 독립 저장. 폭 56px, 이동 버튼 44px. 전용 표시 설정 rd_atelier_rail_v1. 홈/스튜디오/상세 화면에는 레일 미표시. 기존 편집 데이터와 백업 스키마 무변경.
- 최종 ATELIER 퀵레일의 전체 카테고리/실제 선택 개수, 카드·요약·생성 Dock, 독립 검수는 미완료. 이 체크포인트는 배포 후보가 아니므로 버전 표시는 기준 v3.2.1 유지.
- 로컬 실제 HTTP 및 file URL: Chromium ERR_BLOCKED_BY_ADMINISTRATOR. 로컬 제품 실행 PASS 주장 금지. GitHub Actions에서 공식 검사 및 격리 HTTP 브라우저 검사 시작. 결과는 실행 완료 후 별도로 확인.
- main, Pages, Android, APK 변경 금지. 실제 NAI 요청 금지.
