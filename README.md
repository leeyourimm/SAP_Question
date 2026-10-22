# RAP 실습 문제집 (BTP ABAP Cloud)

정리일: 2026-10-17. RAP 실습 문제만 남기고 전면 개편했습니다. BAPI는 쓰지 않고, SAP 공식 샘플(RAP100/110/400/610, ABAP Flight Reference Scenario, ABAP cheat sheets)에 나오는 RAP 기능을 18개 큰 문제로 모두 직접 만들어 보게 했습니다.

**웹페이지:** https://leeyourimm.github.io/SAP_Question/ (원본 HTML: [index.html](index.html))
- 탭 두 개: **RAP 실습**, **어노테이션 설명**
- 문제마다 단계(섹션)를 나눠 한 문제 안에서 처음부터 끝까지 만들 수 있습니다. 단계마다 요구사항, 직접 추가할 어노테이션(이름과 목적만), 확인 방법, 정답·해설이 있습니다.
- 정답 코드 안의 어노테이션을 누르면 어노테이션 설명 탭으로 이동합니다. 단계별 "끝냄" 표시와 메모는 브라우저에만 저장됩니다.

## 문제 구성 (22문제 · 233단계)

| 파일 | 단원 | 문제 |
|---|---|---|
| [rap/R01_managed_model.md](rap/R01_managed_model.md) | 1. 관리형 BO와 Draft | R-01 테이블부터 Fiori 미리보기까지 (데이터 모델, 프로젝션, 값 도움말, MDE, 가상 요소, 서비스) |
| [rap/R02_managed_behavior.md](rap/R02_managed_behavior.md) | 〃 | R-02 결정·검증·액션(인스턴스/팩토리/static default factory/반복/파라미터+기본값 함수)·함수·사이드 이펙트·Draft |
| [rap/R03_R04_managed_control_save.md](rap/R03_R04_managed_control_save.md) | 〃 | R-03 ETag·잠금·기능 제어(인스턴스/글로벌)·권한·precheck·DCL·인터페이스 계층·privileged mode / R-04 저장 시퀀스, late numbering, 추가 저장, 비즈니스 이벤트, unmanaged save |
| [rap/R05_R07_unmanaged.md](rap/R05_R07_unmanaged.md) | 2. 비관리형 BO | R-05 레거시 주문 앱(Z 클래스+버퍼, BAPI 없음) / R-06 핸들러·세이버 전 메서드 구현 / R-07 Unmanaged + Draft, 단위 테스트 |
| [rap/R08_R09_query_singleton.md](rap/R08_R09_query_singleton.md) | 3. 특수 BO 패턴 | R-08 Custom Entity·Unmanaged Query / R-09 Singleton 설정 앱 |
| [rap/R10_R11_extensibility_xbo.md](rap/R10_R11_extensibility_xbo.md) | 〃 | R-10 확장 가능한 BO와 BDEF 확장 / R-11 Cross-BO 연관·협업 Draft·계층(Tree)·추천값 |
| [rap/R12_R13_eml_test.md](rap/R12_R13_eml_test.md) | 4. EML과 테스트 | R-12 EML 전부 / R-13 ABAP Unit·테스트 더블·OData 수준 테스트 |
| [rap/R14_signatures.md](rap/R14_signatures.md) | 5. 고급·특수 기능 보충 | R-14 BDEF 고급 문법: deep 파라미터/결과, selective 결과, 추상 BDEF(hierarchy·control·mandatory:execute), 팩토리 [0..*], static 액션, save action, 삭제 시 검증·결정, always, notrigger, suppress, internal 연산, 대체 키·key function, 매핑 |
| [rap/R15_lock_auth_save_adv.md](rap/R15_lock_auth_save_adv.md) | 〃 | R-15 lock master unmanaged, 액션별 권한, 자식 권한 마스터, auxiliary class, BDEF friends, RAP 변경 문서, CL_ABAP_BEHAVIOR_SAVER_FAILED, CDS 테이블 엔티티, preserve_changes |
| [rap/R16_events_sideeffects_adv.md](rap/R16_events_sideeffects_adv.md) | 〃 | R-16 자식·deep·파생 이벤트, 로컬 소비자 재시도, 이벤트 기반·전역·$self·entity·permissions 사이드 이펙트, use event, 이벤트 바인딩 |
| [rap/R17_projection_eml_adv.md](rap/R17_projection_eml_adv.md) | 〃 | R-17 다중 프로젝션, 프로젝션 전용 액션·함수, augment·precheck, managed instance filter, FORWARDING PRIVILEGED, WITH CHANGES, get_current_phase, 파생 타입(RTTS), 계약 검사 |
| [rap/R18_tools_integration.md](rap/R18_tools_integration.md) | 〃 | R-18 ADT 생성기, Service Consumption Model + Custom Entity, 애플리케이션 로그, bgPF, 애플리케이션 잡, BAS 배포·FLP |
| [rap/R19_R22_sql_challenge.md](rap/R19_R22_sql_challenge.md) | 6. SQL 고난도 (결과 자동 채점) ★★★★ | R-19 구매(EKKO/EKPO 모양) 조인·집계·CTE·FOR ALL ENTRIES 함정 / R-20 판매 윈도 함수(순번·누적·LAG·Top-N 동점·ABC·연속 구간·이동평균) / R-21 회계(차대 검증·GROUPING SETS·기준일 연령 분석·반제 매칭·대사·중복 송장) / R-22 같은 문제를 CDS·파라미터 CDS·AMDP 테이블 함수·custom entity로 |
| [rap/annotations.md](rap/annotations.md) | 어노테이션 설명 탭 | 97개 항목, 하고 싶은 일 → 어노테이션 표 |

> 실제 SAP 시스템에서 실행해 검증하지는 못했습니다. 정답 안에 "(실제 시스템에서 확인 필요)"라고 적힌 곳은 공식 샘플에서 문법을 확인하지 못한 부분이니 활성화하면서 확인하세요.

## 2026-10-22 고난도 업그레이드 (쿼리포터 sql.10xflow.kr 참고)

- **새 단원 6 (R-19~R-22, 20문항 Q01~Q20)**: SAP 모양 Z 테이블 9개(`ZSQ_EKKO_###` 등)에 고정 데이터를 넣고, 문항마다 기대 결과 표와 ABAP Unit 채점 메서드(`cl_osql_test_environment`)를 줍니다. 결과가 한 줄이라도 다르면 실패합니다. 기대 결과는 같은 데이터를 다른 DB 엔진으로 실행해 계산한 값입니다.
- **기존 문제 도전 단계(★★★★) 추가**: R-01 12단계(데이터 품질 SQL), R-02 13단계(기간 겹침 집합 검증), R-04 11단계(번호 감사 SQL), R-08 11단계(계산·페이징 DB push-down), R-13 12단계(RTTS 차이 리포트 채점기).

## 보관한 이전 문제

- 서면 시험 185문제(01~04)와 개념 정리: [_archive/2026-10-17_written_set/](_archive/2026-10-17_written_set/)

## 파일 형식 (문제 추가 시)

```
## 단원
### R-14. 제목 [작성] ★★★   (난이도 ★1~4개)
<!-- covers: 기능1, 기능2 -->
**목표** / **전제** / **만들 객체**
#### 1단계. 제목
요구사항, 직접 추가할 어노테이션, 확인
<details><summary>정답·해설</summary>

코드와 해설

</details>
```
어노테이션 항목은 `rap/annotations.md`에 `## 그룹` / `### @이름` 형식으로 씁니다. 페이지는 `LC_ALL=C.UTF-8 python3 _web/gen.py`(pip markdown, pygments 필요)로 다시 만듭니다.
