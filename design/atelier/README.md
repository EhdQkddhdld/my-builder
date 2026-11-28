# Project ATELIER · v3.3.0 작업실

상태: R2/R3 선택 요약 및 Dock 보완 후보와 QA 코드 보관. 최신 후보 실행 검사 미확인. 종합 QA·독립 검수 미완료. main/Pages/APK 변경 금지.

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
- 제품 커밋: 810fae3e5a93f6fa2e6d2d6452b53e0018fc5c89
- 제품 blob: 3e83b1cab6de330f09d964e6c47c34dd2f6b9ff9
- 제품 SHA-256: 08e2d45e46bb34c1e7585bc2af540d1c06afb0151c74e51f6f0f13b3c510bd2c
- 제품 UTF-8 bytes: 1431644
- QA 코드 커밋: 1837702e631f128f1f84f135077fb84adbc66a95
- 최신 디자인 결정: 1d4fcb6319196dbf85264b4f67d850dcfbcbe51e (DESIGN.md)
- 레일: 화풍·인물(의상 통합)·구도·연출(배경 통합)·스튜디오. 최종 확인 레일 제거, 더보기의 완성 프롬프트 보기 및 기존 출력 계약 보존. 하단 단계 이동은 R3까지 유지. 스튜디오 이동은 API 생성 실행이 아님.
- QA: 기존 R1a 및 갱신된 qa/r1b.py. 해당 후보의 새 Actions 실행 결과 미확인; 이전 R1a PASS는 이전 blob에만 해당. 새 제품의 공식 검사 및 브라우저 회귀 확인 필요.
- 미완료: R2/R3, 전체 상태·출력·저장·폴더블 회귀, Neon 독립 검수, 배포 승인. main/Pages/APK 변경 없음.

## R2/R3 선택 요약 최신 체크포인트
- 사용자 승인: acccb0cd8886cc10aed21f9cae31f37ef0a29c78 (DESIGN.md).
- 제품 커밋: 44ac8586a316c32b1ebbd5977b3aae8d4b87ecf7
- 제품 blob: 3b4d01640127faaeeb9900590eb0aba4e586468e
- SHA-256: a70bdccfb925f8f35c579ea067623d2c7ec1911d731313dd1baac6374429f85 (1441262 bytes)
- QA 코드 커밋: bf392af4a75923d24386f6c5aa63191c97100c00 (qa/r1b.py 확장, 기존 workflow 재사용).
- 구현: 활성 칩 이름/개수 통일, 슬라이더 현재값 별도 표시, 커버 주요 3개+나머지 개수/전체 보기, 펼침 우측 요약, 상세 편집 진입, 프롬프트/스튜디오 Dock. 기존 footer는 Dock 노출 시 숨김.
- 정적 확인: 원격 blob/SHA-256, version.json 불변. 이전 후보 대비 innerHTML/Math.random/schemaVersion:2 문자열 수 증가 0. 비칩 토글/텍스트 필드 전체의 요약 범위, 보호 계약 및 실행 동작 추가 검수 필요.
- Actions 실행 결과 미확인(PR 전용 조회 빈 결과, 공개 API 접근 실패). 공식 검사 및 4개 뷰포트/선택/Undo/복원/출력/저장/생성 회귀 확인 필요. 이전 R1a PASS는 자동 승계하지 않는다.
- R2/R3 전체 완료 아님: 나머지 카드 표현, 생성 설정/복사 상세 UX, 종합 회귀, Neon 독립 검수, 버전 일치, 배포 승인 남음. main/Pages/APK 변경 금지.

## R2/R3 추가 보완 체크포인트
- 제품 커밋: a513fc4405f23de9e835bbb55b77c5d0a2527578
- 제품 blob: ecada16cc5b675934b638d24c6cff92702ecd3eb
- SHA-256: dc43e47daa950f5f8a2f721140017045553b6173ccd7b41ac59998001fbeeadb (1443984 bytes)
- QA 코드 커밋: 4d2e80ea20e81f81b0c4982bc2dabd3a20bd2724
- 기존 생성 폼에서 이미지 크기/Steps/CFG 읽기, 기존 메인 복사 버튼 호출, 선택 카드 강조와 키보드 포커스, 도트/배경 보강/가중치 안정화 및 사용자 입력 슬롯 개수 표시 보완. 생성 요청 경로와 원래 설정 화면 그대로 유지.
- 사용자 입력값은 슬롯 수만 표시. 입력 원문 및 모든 비칩 필드의 완전한 표시 여부는 별도 확인 필요.
- 이전/현재 원격 blob 및 SHA-256 확인, version.json 유지 (3cc74b2226730009d09703c6de9c7830ac6da30f), 신규 innerHTML/Math.random 문자열 증가 없음. 로컬 git ls-remote 실패: Could not resolve host: github.com. 공식 검사/Chromium/Actions 결과 미확인. 배포 금지. 다음: 실제 실행 환경에서 기존 검사 및 전체 회귀, 필요한 보완, 독립 검수, 버전 확정 및 배포 승인.
