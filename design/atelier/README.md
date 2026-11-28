# Project ATELIER · v3.3.0 작업실

상태: R1a 단계 레일 제품 체크포인트 등록. 최종 구현·필수 QA·독립 검수 미완료. main/Pages/APK 변경 금지.

- 기준 main: 205ba64810be7fc6e1bdeb0290f69317b925283e
- 웹 기준: v3.2.1, APK 1.1 (versionCode 2)
- 기준 index.html Git blob: 12233467a182a9354529b3571c2bb6ea9ab12fd8
- 기준 SHA-256: ff72dc7cb1bf9fa55f5b206ff490e56bcab90d277c6844714c32a5c6277da76b
- 원본 전달 워크플로 커밋: be3f2759a26ced905c223a756f49e6b8f7983f9b
- 원본 전달 Actions: https://github.com/EhdQkddhdld/my-builder/actions/runs/46102652988

## 읽는 순서
1. ../PROJECT_GUIDELINES.md: 공통 작업 지침 v2.9.1
2. DESIGN.md: 승인된 방향과 보존 범위
3. DESIGN.html: 최종 독립 시안
4. IMPLEMENT.md: 제품 연결 요구사항 (실물 코드 대조 전)
5. REVIEW.md: 증거와 미검증 상태
6. BLOBS.txt: HTML 원본 Git blob
7. history/: 이전 독립 시안

폐기: 캐릭터 로딩/엠블럼 애니메이션. 기존 생성 화면 및 대기 애니메이션 보존.
시안의 로고는 기존 공개 화면에서 추출한 임시 자산. 제품 구현 시 기존 자산 재사용.
Neon 별도 연구 명세는 이 디자인 보관 범위에 포함하지 않았다. 디자인과 연구 기능의 구현 상태를 혼동하지 않는다.

## 구현 재개 지점
- R1a 제품 커밋: 4b315e557ce7b505b18558287800f57349b8ce26
- R1a 제품 blob: f8f10bb2bb841da971a7fc35ab79bcfe53707573
- QA 코드 커밋: dc7778938bf9350df4ca57b36e4033bf78bb46fa
- [체크포인트](CHECKPOINT_R1a.md), [검사 코드](qa/r1a.py).
- [Actions 실행 기록](https://github.com/EhdQkddhdld/my-builder/actions?query=branch%3Aqa%2Fv3.3.0-atelier). 필수 검사 완료 여부 및 결과를 확인한 뒤 이어서 작업한다.
- 다음 단계: R1a 실행 검사 및 실패 원인 보완 → 승인 시안과 나머지 일반 UI 연결. 제품 후보와 QA 기록을 구분하고 배포 승인 전 main을 변경하지 않는다.
