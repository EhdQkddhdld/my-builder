# Project ATELIER · v3.3.0 작업실

상태: R1b 통합 레일 제품 후보 및 QA 코드 보관. R1a 기존 후보의 한정 실행 검사 통과. R1b 실행 결과 미확인. 최종 구현·전체 QA·독립 검수 미완료. main/Pages/APK 변경 금지.

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
- [Actions 실행 기록](https://github.com/EhdQkddhdld/my-builder/actions?query=branch%3Aqa%2Fv3.3.0-atelier). R1a 한정 검사 완료. [검사 결과](QA_R1a_RESULT.md) 참고.
- 다음 단계: 승인 시안과 나머지 일반 UI 연결 및 영향 경로 검수. 승인 시안 전체와 R1a 검사 범위를 구분한다. 제품 후보와 QA 기록을 구분하고 배포 승인 전 main을 변경하지 않는다.

## R1b 최신 체크포인트
- 제품 커밋: 64bab79980652633bd4ffa44e4cca9d11d7dcaa4
- 제품 blob: 05af3b7a7a7a9dc1cdfd6b275392835317029fcc
- 제품 SHA-256: 2e2856d473d257bdf9ff747416ccfcb658a62ca7f40595bc13680bad178d4c28
- 제품 UTF-8 bytes: 1431575
- QA 코드 커밋: 92fd66879388517f67488af32d8cab01e7b84295
- 최신 디자인 결정: 310b5bef5cb4e8feb59bb099a10fa6e7cf2f2381 (DESIGN.md)
- 레일: 화풍·인물(의상 통합)·구도·연출(배경 통합)·스튜디오. 최종 확인 유지. 스튜디오 이동은 API 생성 실행이 아님.
- QA: 기존 R1a 및 갱신된 qa/r1b.py. 해당 후보의 새 Actions 실행 결과 미확인; 이전 R1a PASS는 이전 blob에만 해당. 새 제품의 공식 검사 및 브라우저 회귀 확인 필요.
- 미완료: R2/R3, 전체 상태·출력·저장·폴더블 회귀, Neon 독립 검수, 배포 승인. main/Pages/APK 변경 없음.
