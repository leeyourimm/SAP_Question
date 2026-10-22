## 6. SQL 고난도 (결과 자동 채점)

### R-19. 구매 데이터 SQL 챌린지: 조인·집계·서브쿼리·CTE, 그리고 채점기 만들기 [작성] ★★★★
<!-- covers: SQL 채점기, cl_osql_test_environment, insert_test_data, 고정 시드 데이터, LEFT OUTER JOIN, ON 조건 vs WHERE 조건, COUNT DISTINCT, COALESCE, SUM 식, CAST, AVG AS DEC, 상관 조건, WITH 공통 테이블 식(CTE), HAVING, DIVISION, DATS_DAYS_BETWEEN, CASE, 조건부 집계(피벗), NULL과 초기값, FOR ALL ENTRIES 함정, SELECT FROM @itab -->

**이 단원은 무엇이 다른가요**
- 쿼리포터(sql.10xflow.kr)처럼 **SAP 모양 테이블(EKKO/EKPO, VBAK/VBAP, BKPF/BSEG)**에 쿼리를 쓰고, **실행 결과가 기대 결과와 한 줄도 틀리지 않아야 정답**입니다. 다만 브라우저 대신 여러분의 BTP 트라이얼에서 ABAP SQL로 풀고, 채점은 ABAP Unit이 합니다.
- 트라이얼(ABAP Cloud)에서는 표준 `EKKO`·`VBAK`·`BKPF`를 읽을 수 없어서(릴리스되지 않은 객체), 같은 필드 이름을 가진 **작은 Z 테이블 9개**를 만들고 **고정 데이터**를 넣습니다. 데이터가 고정이라 기대 결과를 미리 적어 둘 수 있습니다.
- 각 문항은 "요구 결과 열과 정렬 → 기대 결과 표 → 채점 테스트 메서드" 순서로 주어집니다. 정답·해설에는 모범 쿼리, 왜 그렇게 쓰는지, **오답이 나오는 전형적인 실수**가 있습니다.
- 데이터에는 일부러 함정이 들어 있습니다: 삭제 표시(`loekz = 'L'`) 품목, 주문이 하나도 없는 공급업체, 입고되지 않은 품목, 반품 주문, 차대가 안 맞는 전표, 금액이 다른 대사 건, 중복 의심 송장.

**목표**
- 결과 집합을 머릿속으로 먼저 그리고(행의 단위가 무엇인지), 그에 맞는 조인·집계·정렬을 고를 수 있습니다.
- LEFT OUTER JOIN에서 조건을 `ON`에 둘 때와 `WHERE`에 둘 때 결과가 어떻게 달라지는지 설명할 수 있습니다.
- `WITH`(CTE)로 단계별 결과를 만들고, 집계 결과를 다시 조인할 수 있습니다.
- `DIVISION`, `DATS_DAYS_BETWEEN`, `CASE`, `COALESCE`로 업무 지표(정시 납품률, 단가 편차, 증감률)를 계산할 수 있습니다.
- `FOR ALL ENTRIES`가 중복 행을 지우고, 드라이버 테이블이 비면 전체를 읽는다는 함정을 테스트로 잡을 수 있습니다.
- `cl_osql_test_environment`로 DB 내용과 관계없이 항상 같은 결과를 내는 채점 테스트를 만들 수 있습니다.

**전제**
- 패키지 `ZRAP_###`(또는 새 패키지 `ZSQ_###`). `###`는 본인 이니셜 3자리입니다.
- R-01~R-18을 끝내지 않아도 풀 수 있습니다. R-13의 ABAP Unit 기본(테스트 클래스, `cl_abap_unit_assert`)만 알면 됩니다.
- 통화는 모두 EUR 하나로 고정했습니다(환산 없음). 기준일(key date)은 따로 말이 없으면 **2026-06-30**입니다.
- 정답 SQL은 공식 문법 문서 기준으로 썼지만 실제 시스템에서 실행해 검증하지는 못했습니다. 문법이 확실하지 않은 곳에는 "(실제 시스템에서 확인 필요)"를 붙였습니다. 채점 기대값은 같은 데이터를 다른 DB 엔진에서 실행해 계산한 값입니다.

**만들 객체**

| 순서 | 객체 유형 | 이름 | 역할 |
|---|---|---|---|
| 1 | 데이터베이스 테이블 | `ZSQ_LFA1_###`, `ZSQ_MARA_###` | 공급업체, 자재 |
| 2 | 데이터베이스 테이블 | `ZSQ_EKKO_###`, `ZSQ_EKPO_###` | 구매 오더 헤더·품목 |
| 3 | 데이터베이스 테이블 | `ZSQ_KNA1_###`, `ZSQ_VBAK_###`, `ZSQ_VBAP_###` | 고객, 판매 오더 헤더·품목 (R-20) |
| 4 | 데이터베이스 테이블 | `ZSQ_BKPF_###`, `ZSQ_BSEG_###` | 회계 전표 헤더·라인 (R-21) |
| 5 | ABAP 클래스 | `ZCL_SQ_SEED_###` | 고정 데이터 제공 + 콘솔에서 DB에 적재 |
| 6 | ABAP 클래스 | `ZCL_SQ_QUERIES_###` | 문항 Q01~Q20 풀이 메서드 + 결과 타입 |
| 7 | 테스트 클래스(같은 클래스의 Test Classes 탭) | `LTC_GRADE` | 채점기: SQL 테스트 더블에 시드를 넣고 기대 결과와 비교 |

**데이터 한눈에 보기 (R-19~R-21 공통)**

| 테이블 | 건수 | 일부러 넣은 특징 |
|---|---|---|
| 공급업체 | 6 | `V600 Idle Vendor`는 구매 오더가 하나도 없음 |
| 자재 | 8 | `M08 근접 센서`는 한 번도 구매하지 않음 |
| 구매 오더 | 12 (품목 28) | `4500000003/30`(M07) 삭제 표시 `L`, 입고일 없는 품목 7개, 납기 2026-07-05인 미래 품목 1개 |
| 고객 | 7 | `C002`와 `C007`의 순매출이 같음(동점) |
| 판매 오더 | 19 (품목 25) | `0010000010`은 반품(`auart = 'RE'`) — 금액을 빼야 함 |
| 회계 전표 | 22 (라인 44) | 차대 불일치 2건, 판매와 금액 다른 송장 2건, 판매 오더 없는 송장 1건, 덜 받은 반제 1건, 중복 의심 송장 1쌍 |

#### 1단계. SAP 모양 테이블 9개 만들기

요구사항
1. **New > Other ABAP Repository Object > Database Table**로 아래 9개 테이블을 만드세요. 모든 테이블의 첫 키는 `client`(`abap.clnt`)입니다.
2. 데이터 엘리먼트는 쓰지 않고 내장 타입(`abap.char(10)` 등)을 씁니다. 표준 `EBELN`·`LIFNR` 같은 데이터 엘리먼트는 ABAP Cloud에서 릴리스되지 않아 쓸 수 없습니다.
3. 금액 필드는 통화 필드를, 수량 필드는 단위 필드를 참조해야 활성화됩니다(표의 "참조" 열).
4. 테이블 헤더: 확장 불가, 투명 테이블, 전달 클래스 A, 데이터 유지 관리 제한.

`ZSQ_LFA1_###` (공급업체)

| 필드 | 키 | 데이터 엘리먼트 | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | ✓ | (내장) abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| lifnr | ✓ | (내장) abap.char | CHAR | 10 | 0 | 공급업체 번호 |
| name1 | | (내장) abap.char | CHAR | 35 | 0 | 이름 |
| land1 | | (내장) abap.char | CHAR | 3 | 0 | 국가 |

`ZSQ_MARA_###` (자재)

| 필드 | 키 | 데이터 엘리먼트 | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | ✓ | (내장) abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| matnr | ✓ | (내장) abap.char | CHAR | 18 | 0 | 자재 번호 |
| maktx | | (내장) abap.char | CHAR | 40 | 0 | 자재 내역 |
| matkl | | (내장) abap.char | CHAR | 9 | 0 | 자재 그룹 |
| meins | | (내장) abap.unit | UNIT | 3 | 0 | 기본 단위 |

`ZSQ_EKKO_###` (구매 오더 헤더)

| 필드 | 키 | 데이터 엘리먼트 | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | ✓ | (내장) abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| ebeln | ✓ | (내장) abap.char | CHAR | 10 | 0 | 구매 오더 번호 |
| lifnr | | (내장) abap.char | CHAR | 10 | 0 | 공급업체 |
| bedat | | (내장) abap.dats | DATS | 8 | 0 | 오더일 |
| ekgrp | | (내장) abap.char | CHAR | 3 | 0 | 구매 그룹 |
| waers | | (내장) abap.cuky | CUKY | 5 | 0 | 통화 |

`ZSQ_EKPO_###` (구매 오더 품목)

| 필드 | 키 | 데이터 엘리먼트 | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | ✓ | (내장) abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| ebeln | ✓ | (내장) abap.char | CHAR | 10 | 0 | 구매 오더 번호 |
| ebelp | ✓ | (내장) abap.numc | NUMC | 5 | 0 | 품목 번호 |
| matnr | | (내장) abap.char | CHAR | 18 | 0 | 자재 |
| menge | | (내장) abap.quan | QUAN | 13 | 3 | 수량 (참조: meins) |
| meins | | (내장) abap.unit | UNIT | 3 | 0 | 단위 |
| netpr | | (내장) abap.curr | CURR | 11 | 2 | 단가 (참조: waers) |
| waers | | (내장) abap.cuky | CUKY | 5 | 0 | 통화 |
| eindt | | (내장) abap.dats | DATS | 8 | 0 | 납기일 |
| wedat | | (내장) abap.dats | DATS | 8 | 0 | 입고일 (미입고면 초기값 00000000) |
| loekz | | (내장) abap.char | CHAR | 1 | 0 | 삭제 표시 (`L` = 삭제) |

`ZSQ_KNA1_###` (고객)

| 필드 | 키 | 데이터 엘리먼트 | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | ✓ | (내장) abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| kunnr | ✓ | (내장) abap.char | CHAR | 10 | 0 | 고객 번호 |
| name1 | | (내장) abap.char | CHAR | 35 | 0 | 이름 |
| land1 | | (내장) abap.char | CHAR | 3 | 0 | 국가 |

`ZSQ_VBAK_###` (판매 오더 헤더)

| 필드 | 키 | 데이터 엘리먼트 | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | ✓ | (내장) abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| vbeln | ✓ | (내장) abap.char | CHAR | 10 | 0 | 판매 오더 번호 |
| kunnr | | (내장) abap.char | CHAR | 10 | 0 | 고객 |
| audat | | (내장) abap.dats | DATS | 8 | 0 | 오더일 |
| auart | | (내장) abap.char | CHAR | 4 | 0 | 오더 유형 (`OR` 일반, `RE` 반품) |
| waerk | | (내장) abap.cuky | CUKY | 5 | 0 | 통화 |

`ZSQ_VBAP_###` (판매 오더 품목)

| 필드 | 키 | 데이터 엘리먼트 | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | ✓ | (내장) abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| vbeln | ✓ | (내장) abap.char | CHAR | 10 | 0 | 판매 오더 번호 |
| posnr | ✓ | (내장) abap.numc | NUMC | 6 | 0 | 품목 번호 |
| matnr | | (내장) abap.char | CHAR | 18 | 0 | 자재 |
| kwmeng | | (내장) abap.quan | QUAN | 15 | 3 | 오더 수량 (참조: vrkme) |
| vrkme | | (내장) abap.unit | UNIT | 3 | 0 | 판매 단위 |
| netwr | | (내장) abap.curr | CURR | 15 | 2 | 품목 순금액 (참조: waerk) |
| waerk | | (내장) abap.cuky | CUKY | 5 | 0 | 통화 |

`ZSQ_BKPF_###` (회계 전표 헤더)

| 필드 | 키 | 데이터 엘리먼트 | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | ✓ | (내장) abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| bukrs | ✓ | (내장) abap.char | CHAR | 4 | 0 | 회사 코드 |
| belnr | ✓ | (내장) abap.char | CHAR | 10 | 0 | 전표 번호 |
| gjahr | ✓ | (내장) abap.numc | NUMC | 4 | 0 | 회계 연도 |
| blart | | (내장) abap.char | CHAR | 2 | 0 | 전표 유형 (DR 고객 송장, DZ 입금, KR 공급업체 송장, SA 일반) |
| budat | | (내장) abap.dats | DATS | 8 | 0 | 전기일 |
| xblnr | | (내장) abap.char | CHAR | 16 | 0 | 참조 번호 (DR은 판매 오더 번호) |
| waers | | (내장) abap.cuky | CUKY | 5 | 0 | 통화 |

`ZSQ_BSEG_###` (회계 전표 라인)

| 필드 | 키 | 데이터 엘리먼트 | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | ✓ | (내장) abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| bukrs | ✓ | (내장) abap.char | CHAR | 4 | 0 | 회사 코드 |
| belnr | ✓ | (내장) abap.char | CHAR | 10 | 0 | 전표 번호 |
| gjahr | ✓ | (내장) abap.numc | NUMC | 4 | 0 | 회계 연도 |
| buzei | ✓ | (내장) abap.numc | NUMC | 3 | 0 | 라인 번호 |
| koart | | (내장) abap.char | CHAR | 1 | 0 | 계정 유형 (D 고객, K 공급업체, S 총계정) |
| kunnr | | (내장) abap.char | CHAR | 10 | 0 | 고객 (D 라인) |
| lifnr | | (내장) abap.char | CHAR | 10 | 0 | 공급업체 (K 라인) |
| hkont | | (내장) abap.char | CHAR | 10 | 0 | 총계정 (120000 매출채권, 400000 매출, 113100 은행, 210000 매입채무, 500000 비용, 600000 기타) |
| shkzg | | (내장) abap.char | CHAR | 1 | 0 | 차대 (S 차변, H 대변) |
| dmbtr | | (내장) abap.curr | CURR | 13 | 2 | 금액 (참조: waers) |
| waers | | (내장) abap.cuky | CUKY | 5 | 0 | 통화 |
| augbl | | (내장) abap.char | CHAR | 10 | 0 | 반제 전표 번호 (미결이면 공백) |
| augdt | | (내장) abap.dats | DATS | 8 | 0 | 반제일 |

**직접 추가할 어노테이션**
- `@EndUserText.label` — 테이블 설명.
- `@AbapCatalog.enhancement.category` — append 확장 가능 여부.
- `@AbapCatalog.tableCategory` — 투명 테이블.
- `@AbapCatalog.deliveryClass` — 애플리케이션 데이터(A).
- `@AbapCatalog.dataMaintenance` — 직접 유지 관리 제한.
- `@Semantics.amount.currencyCode` — 금액 필드 → 통화 필드.
- `@Semantics.quantity.unitOfMeasure` — 수량 필드 → 단위 필드.

**확인**
- 9개 테이블이 모두 활성화됩니다. 금액·수량 참조를 빼면 "reference field missing" 류의 오류로 활성화가 안 됩니다.

<details><summary>정답·해설</summary>

대표로 금액·수량 참조가 있는 `ZSQ_EKPO_###`와 `ZSQ_BSEG_###`만 전체를 보이고, 나머지는 필드 부분만 보입니다. 헤더 어노테이션 다섯 줄은 모든 테이블에 똑같이 붙입니다.

```cds
@EndUserText.label : 'SQL drill: purchase order item (EKPO-like)'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zsq_ekpo_### {
  key client : abap.clnt not null;
  key ebeln  : abap.char(10) not null;
  key ebelp  : abap.numc(5) not null;
  matnr      : abap.char(18);
  @Semantics.quantity.unitOfMeasure : 'zsq_ekpo_###.meins'
  menge      : abap.quan(13,3);
  meins      : abap.unit(3);
  @Semantics.amount.currencyCode : 'zsq_ekpo_###.waers'
  netpr      : abap.curr(11,2);
  waers      : abap.cuky;
  eindt      : abap.dats;
  wedat      : abap.dats;
  loekz      : abap.char(1);
}
```

```cds
@EndUserText.label : 'SQL drill: accounting line (BSEG-like)'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zsq_bseg_### {
  key client : abap.clnt not null;
  key bukrs  : abap.char(4) not null;
  key belnr  : abap.char(10) not null;
  key gjahr  : abap.numc(4) not null;
  key buzei  : abap.numc(3) not null;
  koart      : abap.char(1);
  kunnr      : abap.char(10);
  lifnr      : abap.char(10);
  hkont      : abap.char(10);
  shkzg      : abap.char(1);
  @Semantics.amount.currencyCode : 'zsq_bseg_###.waers'
  dmbtr      : abap.curr(13,2);
  waers      : abap.cuky;
  augbl      : abap.char(10);
  augdt      : abap.dats;
}
```

나머지 테이블의 필드 부분:

```cds
// zsq_lfa1_###
  key client : abap.clnt not null;
  key lifnr  : abap.char(10) not null;
  name1      : abap.char(35);
  land1      : abap.char(3);

// zsq_mara_###
  key client : abap.clnt not null;
  key matnr  : abap.char(18) not null;
  maktx      : abap.char(40);
  matkl      : abap.char(9);
  meins      : abap.unit(3);

// zsq_ekko_###
  key client : abap.clnt not null;
  key ebeln  : abap.char(10) not null;
  lifnr      : abap.char(10);
  bedat      : abap.dats;
  ekgrp      : abap.char(3);
  waers      : abap.cuky;

// zsq_kna1_###
  key client : abap.clnt not null;
  key kunnr  : abap.char(10) not null;
  name1      : abap.char(35);
  land1      : abap.char(3);

// zsq_vbak_###
  key client : abap.clnt not null;
  key vbeln  : abap.char(10) not null;
  kunnr      : abap.char(10);
  audat      : abap.dats;
  auart      : abap.char(4);
  waerk      : abap.cuky;

// zsq_vbap_###
  key client : abap.clnt not null;
  key vbeln  : abap.char(10) not null;
  key posnr  : abap.numc(6) not null;
  matnr      : abap.char(18);
  @Semantics.quantity.unitOfMeasure : 'zsq_vbap_###.vrkme'
  kwmeng     : abap.quan(15,3);
  vrkme      : abap.unit(3);
  @Semantics.amount.currencyCode : 'zsq_vbap_###.waerk'
  netwr      : abap.curr(15,2);
  waerk      : abap.cuky;

// zsq_bkpf_###
  key client : abap.clnt not null;
  key bukrs  : abap.char(4) not null;
  key belnr  : abap.char(10) not null;
  key gjahr  : abap.numc(4) not null;
  blart      : abap.char(2);
  budat      : abap.dats;
  xblnr      : abap.char(16);
  waers      : abap.cuky;
```

왜 이렇게 쓰나
- 필드 이름을 SAP 표준과 똑같이(`ebeln`, `lifnr`, `shkzg`, `augbl` …) 지었습니다. 실무 쿼리와 쿼리포터 문제를 그대로 옮겨 연습할 수 있게 하려는 것입니다. 실제 S/4HANA에서는 `BSEG` 대신 `ACDOCA`(Universal Journal)와 `I_JournalEntryItem` 같은 릴리스된 CDS 뷰를 읽는 것이 맞습니다.
- `wedat`(입고일)와 `augdt`(반제일)는 "아직 없음"을 **초기값 `00000000`**으로 표현합니다. DB의 NULL이 아닙니다. 이 차이가 Q04·Q17에서 결과를 가릅니다.
- `kunnr`·`lifnr`를 `C001`, `V100`처럼 짧게 넣었습니다. 실제 SAP는 ALPHA 변환으로 앞에 0을 채운 `0000000001` 형태라서 문자열 비교·정렬 결과가 달라질 수 있다는 점만 기억하세요.

자주 나는 오류와 해결
- `@Semantics.amount.currencyCode : 'zsq_ekpo_###.waers'`에서 테이블 이름 부분을 빠뜨리거나 대소문자를 바꾸면 참조를 찾지 못합니다. 퀵 픽스(Ctrl+1)로 넣으면 정확합니다.
- 테이블 이름은 16자까지입니다. `ZSQ_EKPO_###`는 12자라서 문제없습니다.

</details>

#### 2단계. 고정 데이터 클래스 `ZCL_SQ_SEED_###`

요구사항
1. 클래스 `ZCL_SQ_SEED_###`(PUBLIC FINAL CREATE PUBLIC)를 만들고 `if_oo_adt_classrun`을 구현하세요.
2. 테이블마다 **데이터를 돌려주는 공개 메서드**를 하나씩 만듭니다: `lfa1`, `mara`, `ekko`, `ekpo`, `kna1`, `vbak`, `vbap`, `bkpf`, `bseg`. 반환 타입은 해당 테이블의 내부 테이블입니다. 이 메서드는 3단계 채점기가 SQL 테스트 더블에 같은 데이터를 넣을 때 다시 씁니다(데이터를 한 곳에만 둠).
3. `main`은 9개 테이블을 모두 지운 뒤(`DELETE FROM`) 메서드 결과를 `INSERT`하고, 테이블마다 건수를 출력합니다.
4. 데이터는 아래 정답의 값을 **그대로** 쓰세요. 값이 하나라도 다르면 채점 기대 결과와 맞지 않습니다.

**확인**
- F9 → 콘솔에 `lfa1 6`, `mara 8`, `ekko 12`, `ekpo 28`, `kna1 7`, `vbak 19`, `vbap 25`, `bkpf 22`, `bseg 44`가 나옵니다.
- 두 번 실행해도 건수가 같아야 합니다(먼저 지우므로 중복 키 오류가 나지 않음).

<details><summary>정답·해설</summary>

```abap
CLASS zcl_sq_seed_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.

    TYPES tt_lfa1 TYPE STANDARD TABLE OF zsq_lfa1_### WITH EMPTY KEY.
    TYPES tt_mara TYPE STANDARD TABLE OF zsq_mara_### WITH EMPTY KEY.
    TYPES tt_ekko TYPE STANDARD TABLE OF zsq_ekko_### WITH EMPTY KEY.
    TYPES tt_ekpo TYPE STANDARD TABLE OF zsq_ekpo_### WITH EMPTY KEY.
    TYPES tt_kna1 TYPE STANDARD TABLE OF zsq_kna1_### WITH EMPTY KEY.
    TYPES tt_vbak TYPE STANDARD TABLE OF zsq_vbak_### WITH EMPTY KEY.
    TYPES tt_vbap TYPE STANDARD TABLE OF zsq_vbap_### WITH EMPTY KEY.
    TYPES tt_bkpf TYPE STANDARD TABLE OF zsq_bkpf_### WITH EMPTY KEY.
    TYPES tt_bseg TYPE STANDARD TABLE OF zsq_bseg_### WITH EMPTY KEY.

    METHODS lfa1 RETURNING VALUE(result) TYPE tt_lfa1.
    METHODS mara RETURNING VALUE(result) TYPE tt_mara.
    METHODS ekko RETURNING VALUE(result) TYPE tt_ekko.
    METHODS ekpo RETURNING VALUE(result) TYPE tt_ekpo.
    METHODS kna1 RETURNING VALUE(result) TYPE tt_kna1.
    METHODS vbak RETURNING VALUE(result) TYPE tt_vbak.
    METHODS vbap RETURNING VALUE(result) TYPE tt_vbap.
    METHODS bkpf RETURNING VALUE(result) TYPE tt_bkpf.
    METHODS bseg RETURNING VALUE(result) TYPE tt_bseg.

  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.


CLASS zcl_sq_seed_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.
    DELETE FROM zsq_lfa1_###.
    DELETE FROM zsq_mara_###.
    DELETE FROM zsq_ekko_###.
    DELETE FROM zsq_ekpo_###.
    DELETE FROM zsq_kna1_###.
    DELETE FROM zsq_vbak_###.
    DELETE FROM zsq_vbap_###.
    DELETE FROM zsq_bkpf_###.
    DELETE FROM zsq_bseg_###.

    DATA(lt_lfa1) = lfa1( ).  INSERT zsq_lfa1_### FROM TABLE @lt_lfa1.
    DATA(lt_mara) = mara( ).  INSERT zsq_mara_### FROM TABLE @lt_mara.
    DATA(lt_ekko) = ekko( ).  INSERT zsq_ekko_### FROM TABLE @lt_ekko.
    DATA(lt_ekpo) = ekpo( ).  INSERT zsq_ekpo_### FROM TABLE @lt_ekpo.
    DATA(lt_kna1) = kna1( ).  INSERT zsq_kna1_### FROM TABLE @lt_kna1.
    DATA(lt_vbak) = vbak( ).  INSERT zsq_vbak_### FROM TABLE @lt_vbak.
    DATA(lt_vbap) = vbap( ).  INSERT zsq_vbap_### FROM TABLE @lt_vbap.
    DATA(lt_bkpf) = bkpf( ).  INSERT zsq_bkpf_### FROM TABLE @lt_bkpf.
    DATA(lt_bseg) = bseg( ).  INSERT zsq_bseg_### FROM TABLE @lt_bseg.

    SELECT COUNT( * ) FROM zsq_lfa1_### INTO @DATA(n). out->write( |lfa1 { n }| ).
    SELECT COUNT( * ) FROM zsq_mara_### INTO @n.        out->write( |mara { n }| ).
    SELECT COUNT( * ) FROM zsq_ekko_### INTO @n.        out->write( |ekko { n }| ).
    SELECT COUNT( * ) FROM zsq_ekpo_### INTO @n.        out->write( |ekpo { n }| ).
    SELECT COUNT( * ) FROM zsq_kna1_### INTO @n.        out->write( |kna1 { n }| ).
    SELECT COUNT( * ) FROM zsq_vbak_### INTO @n.        out->write( |vbak { n }| ).
    SELECT COUNT( * ) FROM zsq_vbap_### INTO @n.        out->write( |vbap { n }| ).
    SELECT COUNT( * ) FROM zsq_bkpf_### INTO @n.        out->write( |bkpf { n }| ).
    SELECT COUNT( * ) FROM zsq_bseg_### INTO @n.        out->write( |bseg { n }| ).
  ENDMETHOD.


  METHOD lfa1.
    result = VALUE #(
      ( lifnr = 'V100' name1 = '한빛상사' land1 = 'KR' )
      ( lifnr = 'V200' name1 = 'Nord Supply' land1 = 'DE' )
      ( lifnr = 'V300' name1 = 'Pacific Parts' land1 = 'US' )
      ( lifnr = 'V400' name1 = '대성기계' land1 = 'KR' )
      ( lifnr = 'V500' name1 = 'Alpen Tech' land1 = 'DE' )
      ( lifnr = 'V600' name1 = 'Idle Vendor' land1 = 'US' ) ).
  ENDMETHOD.


  METHOD mara.
    result = VALUE #(
      ( matnr = 'M01' maktx = '볼트 M8' matkl = 'FAST' meins = 'EA' )
      ( matnr = 'M02' maktx = '너트 M8' matkl = 'FAST' meins = 'EA' )
      ( matnr = 'M03' maktx = '베어링 6204' matkl = 'BEAR' meins = 'EA' )
      ( matnr = 'M04' maktx = '모터 1kW' matkl = 'ELEC' meins = 'EA' )
      ( matnr = 'M05' maktx = '케이블 2m' matkl = 'ELEC' meins = 'EA' )
      ( matnr = 'M06' maktx = '윤활유 1L' matkl = 'CHEM' meins = 'L' )
      ( matnr = 'M07' maktx = '기어박스' matkl = 'MECH' meins = 'EA' )
      ( matnr = 'M08' maktx = '근접 센서' matkl = 'ELEC' meins = 'EA' ) ).
  ENDMETHOD.


  METHOD ekko.
    result = VALUE #(
      ( ebeln = '4500000001' lifnr = 'V100' bedat = '20260105' ekgrp = 'A01' waers = 'EUR' )
      ( ebeln = '4500000002' lifnr = 'V200' bedat = '20260112' ekgrp = 'A01' waers = 'EUR' )
      ( ebeln = '4500000003' lifnr = 'V100' bedat = '20260203' ekgrp = 'A02' waers = 'EUR' )
      ( ebeln = '4500000004' lifnr = 'V300' bedat = '20260210' ekgrp = 'A02' waers = 'EUR' )
      ( ebeln = '4500000005' lifnr = 'V400' bedat = '20260215' ekgrp = 'A01' waers = 'EUR' )
      ( ebeln = '4500000006' lifnr = 'V200' bedat = '20260302' ekgrp = 'A03' waers = 'EUR' )
      ( ebeln = '4500000007' lifnr = 'V500' bedat = '20260318' ekgrp = 'A03' waers = 'EUR' )
      ( ebeln = '4500000008' lifnr = 'V100' bedat = '20260405' ekgrp = 'A01' waers = 'EUR' )
      ( ebeln = '4500000009' lifnr = 'V300' bedat = '20260420' ekgrp = 'A02' waers = 'EUR' )
      ( ebeln = '4500000010' lifnr = 'V400' bedat = '20260502' ekgrp = 'A03' waers = 'EUR' )
      ( ebeln = '4500000011' lifnr = 'V500' bedat = '20260515' ekgrp = 'A01' waers = 'EUR' )
      ( ebeln = '4500000012' lifnr = 'V200' bedat = '20260603' ekgrp = 'A02' waers = 'EUR' ) ).
  ENDMETHOD.


  METHOD ekpo.
    result = VALUE #(
      ( ebeln = '4500000001' ebelp = '00010' matnr = 'M01' menge = 1000 meins = 'EA' netpr = '0.12' waers = 'EUR' eindt = '20260115' wedat = '20260114' )
      ( ebeln = '4500000001' ebelp = '00020' matnr = 'M02' menge = 1000 meins = 'EA' netpr = '0.08' waers = 'EUR' eindt = '20260115' wedat = '20260118' )
      ( ebeln = '4500000001' ebelp = '00030' matnr = 'M06' menge = 50 meins = 'L' netpr = '4.50' waers = 'EUR' eindt = '20260120' wedat = '20260120' )
      ( ebeln = '4500000002' ebelp = '00010' matnr = 'M03' menge = 200 meins = 'EA' netpr = '3.20' waers = 'EUR' eindt = '20260125' wedat = '20260130' )
      ( ebeln = '4500000002' ebelp = '00020' matnr = 'M04' menge = 10 meins = 'EA' netpr = '185.00' waers = 'EUR' eindt = '20260131' wedat = '20260205' )
      ( ebeln = '4500000003' ebelp = '00010' matnr = 'M01' menge = 2000 meins = 'EA' netpr = '0.11' waers = 'EUR' eindt = '20260215' wedat = '20260215' )
      ( ebeln = '4500000003' ebelp = '00020' matnr = 'M05' menge = 300 meins = 'EA' netpr = '2.40' waers = 'EUR' eindt = '20260215' wedat = '20260214' )
      ( ebeln = '4500000003' ebelp = '00030' matnr = 'M07' menge = 2 meins = 'EA' netpr = '950.00' waers = 'EUR' eindt = '20260228' loekz = 'L' )
      ( ebeln = '4500000004' ebelp = '00010' matnr = 'M04' menge = 15 meins = 'EA' netpr = '179.50' waers = 'EUR' eindt = '20260225' wedat = '20260301' )
      ( ebeln = '4500000004' ebelp = '00020' matnr = 'M03' menge = 150 meins = 'EA' netpr = '3.45' waers = 'EUR' eindt = '20260225' wedat = '20260224' )
      ( ebeln = '4500000005' ebelp = '00010' matnr = 'M07' menge = 3 meins = 'EA' netpr = '920.00' waers = 'EUR' eindt = '20260310' wedat = '20260322' )
      ( ebeln = '4500000005' ebelp = '00020' matnr = 'M06' menge = 80 meins = 'L' netpr = '4.20' waers = 'EUR' eindt = '20260305' wedat = '20260305' )
      ( ebeln = '4500000006' ebelp = '00010' matnr = 'M02' menge = 1500 meins = 'EA' netpr = '0.09' waers = 'EUR' eindt = '20260315' wedat = '20260316' )
      ( ebeln = '4500000006' ebelp = '00020' matnr = 'M05' menge = 200 meins = 'EA' netpr = '2.55' waers = 'EUR' eindt = '20260315' wedat = '20260320' )
      ( ebeln = '4500000006' ebelp = '00030' matnr = 'M03' menge = 100 meins = 'EA' netpr = '3.10' waers = 'EUR' eindt = '20260320' wedat = '20260319' )
      ( ebeln = '4500000007' ebelp = '00010' matnr = 'M04' menge = 8 meins = 'EA' netpr = '192.00' waers = 'EUR' eindt = '20260401' wedat = '20260410' )
      ( ebeln = '4500000007' ebelp = '00020' matnr = 'M07' menge = 1 meins = 'EA' netpr = '990.00' waers = 'EUR' eindt = '20260405' wedat = '20260405' )
      ( ebeln = '4500000008' ebelp = '00010' matnr = 'M01' menge = 1500 meins = 'EA' netpr = '0.12' waers = 'EUR' eindt = '20260415' wedat = '20260415' )
      ( ebeln = '4500000008' ebelp = '00020' matnr = 'M06' menge = 60 meins = 'L' netpr = '4.50' waers = 'EUR' eindt = '20260420' )
      ( ebeln = '4500000009' ebelp = '00010' matnr = 'M05' menge = 400 meins = 'EA' netpr = '2.35' waers = 'EUR' eindt = '20260505' wedat = '20260504' )
      ( ebeln = '4500000009' ebelp = '00020' matnr = 'M04' menge = 12 meins = 'EA' netpr = '182.00' waers = 'EUR' eindt = '20260510' wedat = '20260520' )
      ( ebeln = '4500000010' ebelp = '00010' matnr = 'M07' menge = 2 meins = 'EA' netpr = '940.00' waers = 'EUR' eindt = '20260520' )
      ( ebeln = '4500000010' ebelp = '00020' matnr = 'M03' menge = 250 meins = 'EA' netpr = '3.05' waers = 'EUR' eindt = '20260515' wedat = '20260515' )
      ( ebeln = '4500000011' ebelp = '00010' matnr = 'M04' menge = 5 meins = 'EA' netpr = '189.00' waers = 'EUR' eindt = '20260601' wedat = '20260603' )
      ( ebeln = '4500000011' ebelp = '00020' matnr = 'M02' menge = 800 meins = 'EA' netpr = '0.10' waers = 'EUR' eindt = '20260601' )
      ( ebeln = '4500000012' ebelp = '00010' matnr = 'M01' menge = 3000 meins = 'EA' netpr = '0.10' waers = 'EUR' eindt = '20260620' )
      ( ebeln = '4500000012' ebelp = '00020' matnr = 'M03' menge = 120 meins = 'EA' netpr = '3.30' waers = 'EUR' eindt = '20260625' )
      ( ebeln = '4500000012' ebelp = '00030' matnr = 'M05' menge = 100 meins = 'EA' netpr = '2.60' waers = 'EUR' eindt = '20260705' ) ).
  ENDMETHOD.


  METHOD kna1.
    result = VALUE #(
      ( kunnr = 'C001' name1 = '서울정밀' land1 = 'KR' )
      ( kunnr = 'C002' name1 = '부산중공업' land1 = 'KR' )
      ( kunnr = 'C003' name1 = 'Berlin Motoren' land1 = 'DE' )
      ( kunnr = 'C004' name1 = 'München Anlagen' land1 = 'DE' )
      ( kunnr = 'C005' name1 = 'Texas Drives' land1 = 'US' )
      ( kunnr = 'C006' name1 = 'Ohio Robotics' land1 = 'US' )
      ( kunnr = 'C007' name1 = 'Seoul Robotics' land1 = 'KR' ) ).
  ENDMETHOD.


  METHOD vbak.
    result = VALUE #(
      ( vbeln = '0010000001' kunnr = 'C001' audat = '20260108' auart = 'OR' waerk = 'EUR' )
      ( vbeln = '0010000002' kunnr = 'C003' audat = '20260115' auart = 'OR' waerk = 'EUR' )
      ( vbeln = '0010000003' kunnr = 'C002' audat = '20260122' auart = 'OR' waerk = 'EUR' )
      ( vbeln = '0010000004' kunnr = 'C001' audat = '20260205' auart = 'OR' waerk = 'EUR' )
      ( vbeln = '0010000005' kunnr = 'C005' audat = '20260211' auart = 'OR' waerk = 'EUR' )
      ( vbeln = '0010000006' kunnr = 'C004' audat = '20260226' auart = 'OR' waerk = 'EUR' )
      ( vbeln = '0010000007' kunnr = 'C003' audat = '20260304' auart = 'OR' waerk = 'EUR' )
      ( vbeln = '0010000008' kunnr = 'C001' audat = '20260312' auart = 'OR' waerk = 'EUR' )
      ( vbeln = '0010000009' kunnr = 'C006' audat = '20260318' auart = 'OR' waerk = 'EUR' )
      ( vbeln = '0010000010' kunnr = 'C002' audat = '20260325' auart = 'RE' waerk = 'EUR' )
      ( vbeln = '0010000011' kunnr = 'C005' audat = '20260409' auart = 'OR' waerk = 'EUR' )
      ( vbeln = '0010000012' kunnr = 'C003' audat = '20260416' auart = 'OR' waerk = 'EUR' )
      ( vbeln = '0010000013' kunnr = 'C004' audat = '20260428' auart = 'OR' waerk = 'EUR' )
      ( vbeln = '0010000014' kunnr = 'C001' audat = '20260507' auart = 'OR' waerk = 'EUR' )
      ( vbeln = '0010000015' kunnr = 'C006' audat = '20260514' auart = 'OR' waerk = 'EUR' )
      ( vbeln = '0010000016' kunnr = 'C002' audat = '20260521' auart = 'OR' waerk = 'EUR' )
      ( vbeln = '0010000017' kunnr = 'C003' audat = '20260611' auart = 'OR' waerk = 'EUR' )
      ( vbeln = '0010000018' kunnr = 'C005' audat = '20260618' auart = 'OR' waerk = 'EUR' )
      ( vbeln = '0010000019' kunnr = 'C007' audat = '20260625' auart = 'OR' waerk = 'EUR' ) ).
  ENDMETHOD.


  METHOD vbap.
    result = VALUE #(
      ( vbeln = '0010000001' posnr = '000010' matnr = 'M04' kwmeng = 2 vrkme = 'EA' netwr = '370.00' waerk = 'EUR' )
      ( vbeln = '0010000001' posnr = '000020' matnr = 'M05' kwmeng = 50 vrkme = 'EA' netwr = '150.00' waerk = 'EUR' )
      ( vbeln = '0010000002' posnr = '000010' matnr = 'M07' kwmeng = 1 vrkme = 'EA' netwr = '1450.00' waerk = 'EUR' )
      ( vbeln = '0010000003' posnr = '000010' matnr = 'M04' kwmeng = 5 vrkme = 'EA' netwr = '950.00' waerk = 'EUR' )
      ( vbeln = '0010000003' posnr = '000020' matnr = 'M03' kwmeng = 100 vrkme = 'EA' netwr = '520.00' waerk = 'EUR' )
      ( vbeln = '0010000004' posnr = '000010' matnr = 'M01' kwmeng = 5000 vrkme = 'EA' netwr = '900.00' waerk = 'EUR' )
      ( vbeln = '0010000005' posnr = '000010' matnr = 'M07' kwmeng = 2 vrkme = 'EA' netwr = '2800.00' waerk = 'EUR' )
      ( vbeln = '0010000005' posnr = '000020' matnr = 'M06' kwmeng = 30 vrkme = 'L' netwr = '240.00' waerk = 'EUR' )
      ( vbeln = '0010000006' posnr = '000010' matnr = 'M04' kwmeng = 3 vrkme = 'EA' netwr = '570.00' waerk = 'EUR' )
      ( vbeln = '0010000007' posnr = '000010' matnr = 'M03' kwmeng = 200 vrkme = 'EA' netwr = '1000.00' waerk = 'EUR' )
      ( vbeln = '0010000007' posnr = '000020' matnr = 'M05' kwmeng = 100 vrkme = 'EA' netwr = '310.00' waerk = 'EUR' )
      ( vbeln = '0010000008' posnr = '000010' matnr = 'M07' kwmeng = 1 vrkme = 'EA' netwr = '1500.00' waerk = 'EUR' )
      ( vbeln = '0010000009' posnr = '000010' matnr = 'M04' kwmeng = 4 vrkme = 'EA' netwr = '780.00' waerk = 'EUR' )
      ( vbeln = '0010000010' posnr = '000010' matnr = 'M04' kwmeng = 1 vrkme = 'EA' netwr = '190.00' waerk = 'EUR' )
      ( vbeln = '0010000011' posnr = '000010' matnr = 'M03' kwmeng = 150 vrkme = 'EA' netwr = '780.00' waerk = 'EUR' )
      ( vbeln = '0010000012' posnr = '000010' matnr = 'M07' kwmeng = 1 vrkme = 'EA' netwr = '1480.00' waerk = 'EUR' )
      ( vbeln = '0010000012' posnr = '000020' matnr = 'M06' kwmeng = 20 vrkme = 'L' netwr = '170.00' waerk = 'EUR' )
      ( vbeln = '0010000013' posnr = '000010' matnr = 'M01' kwmeng = 3000 vrkme = 'EA' netwr = '560.00' waerk = 'EUR' )
      ( vbeln = '0010000014' posnr = '000010' matnr = 'M05' kwmeng = 200 vrkme = 'EA' netwr = '640.00' waerk = 'EUR' )
      ( vbeln = '0010000015' posnr = '000010' matnr = 'M07' kwmeng = 2 vrkme = 'EA' netwr = '2900.00' waerk = 'EUR' )
      ( vbeln = '0010000016' posnr = '000010' matnr = 'M04' kwmeng = 6 vrkme = 'EA' netwr = '1140.00' waerk = 'EUR' )
      ( vbeln = '0010000017' posnr = '000010' matnr = 'M04' kwmeng = 2 vrkme = 'EA' netwr = '400.00' waerk = 'EUR' )
      ( vbeln = '0010000018' posnr = '000010' matnr = 'M05' kwmeng = 150 vrkme = 'EA' netwr = '480.00' waerk = 'EUR' )
      ( vbeln = '0010000018' posnr = '000020' matnr = 'M06' kwmeng = 40 vrkme = 'L' netwr = '330.00' waerk = 'EUR' )
      ( vbeln = '0010000019' posnr = '000010' matnr = 'M07' kwmeng = 2 vrkme = 'EA' netwr = '2420.00' waerk = 'EUR' ) ).
  ENDMETHOD.


  METHOD bkpf.
    result = VALUE #(
      ( bukrs = '1000' belnr = '0100000001' gjahr = '2026' blart = 'DR' budat = '20260110' xblnr = '0010000001' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000002' gjahr = '2026' blart = 'DR' budat = '20260116' xblnr = '0010000002' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000003' gjahr = '2026' blart = 'DR' budat = '20260124' xblnr = '0010000003' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000004' gjahr = '2026' blart = 'DR' budat = '20260206' xblnr = '0010000004' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000005' gjahr = '2026' blart = 'DR' budat = '20260212' xblnr = '0010000005' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000006' gjahr = '2026' blart = 'DR' budat = '20260305' xblnr = '0010000007' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000007' gjahr = '2026' blart = 'DR' budat = '20260313' xblnr = '0010000008' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000008' gjahr = '2026' blart = 'DR' budat = '20260410' xblnr = '0010000011' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000009' gjahr = '2026' blart = 'DR' budat = '20260417' xblnr = '0010000012' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000010' gjahr = '2026' blart = 'DR' budat = '20260508' xblnr = '0010000014' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000011' gjahr = '2026' blart = 'DR' budat = '20260515' xblnr = '0010000099' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000012' gjahr = '2026' blart = 'DR' budat = '20260612' xblnr = '0010000017' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1400000001' gjahr = '2026' blart = 'DZ' budat = '20260209' xblnr = '0100000001' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1400000002' gjahr = '2026' blart = 'DZ' budat = '20260310' xblnr = '0100000003' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1400000003' gjahr = '2026' blart = 'DZ' budat = '20260420' xblnr = '0100000006' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1500000001' gjahr = '2026' blart = 'SA' budat = '20260331' xblnr = 'ACCRUAL-03' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1900000001' gjahr = '2026' blart = 'KR' budat = '20260301' xblnr = 'INV-A77' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1900000002' gjahr = '2026' blart = 'KR' budat = '20260303' xblnr = 'INV-A77B' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1900000003' gjahr = '2026' blart = 'KR' budat = '20260320' xblnr = 'P-881' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1900000004' gjahr = '2026' blart = 'KR' budat = '20260402' xblnr = 'P-990' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1900000005' gjahr = '2026' blart = 'KR' budat = '20260405' xblnr = 'X-1' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1900000006' gjahr = '2026' blart = 'KR' budat = '20260406' xblnr = 'X-2' waers = 'EUR' ) ).
  ENDMETHOD.


  METHOD bseg.
    result = VALUE #(
      ( bukrs = '1000' belnr = '0100000001' gjahr = '2026' buzei = '001' koart = 'D' kunnr = 'C001' hkont = '120000' shkzg = 'S' dmbtr = '520.00' waers = 'EUR' augbl = '1400000001' augdt = '20260209' )
      ( bukrs = '1000' belnr = '0100000001' gjahr = '2026' buzei = '002' koart = 'S' hkont = '400000' shkzg = 'H' dmbtr = '520.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000002' gjahr = '2026' buzei = '001' koart = 'D' kunnr = 'C003' hkont = '120000' shkzg = 'S' dmbtr = '1450.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000002' gjahr = '2026' buzei = '002' koart = 'S' hkont = '400000' shkzg = 'H' dmbtr = '1450.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000003' gjahr = '2026' buzei = '001' koart = 'D' kunnr = 'C002' hkont = '120000' shkzg = 'S' dmbtr = '1470.00' waers = 'EUR' augbl = '1400000002' augdt = '20260310' )
      ( bukrs = '1000' belnr = '0100000003' gjahr = '2026' buzei = '002' koart = 'S' hkont = '400000' shkzg = 'H' dmbtr = '1470.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000004' gjahr = '2026' buzei = '001' koart = 'D' kunnr = 'C001' hkont = '120000' shkzg = 'S' dmbtr = '900.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000004' gjahr = '2026' buzei = '002' koart = 'S' hkont = '400000' shkzg = 'H' dmbtr = '900.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000005' gjahr = '2026' buzei = '001' koart = 'D' kunnr = 'C005' hkont = '120000' shkzg = 'S' dmbtr = '3040.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000005' gjahr = '2026' buzei = '002' koart = 'S' hkont = '400000' shkzg = 'H' dmbtr = '3000.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000006' gjahr = '2026' buzei = '001' koart = 'D' kunnr = 'C003' hkont = '120000' shkzg = 'S' dmbtr = '1310.00' waers = 'EUR' augbl = '1400000003' augdt = '20260420' )
      ( bukrs = '1000' belnr = '0100000006' gjahr = '2026' buzei = '002' koart = 'S' hkont = '400000' shkzg = 'H' dmbtr = '1310.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000007' gjahr = '2026' buzei = '001' koart = 'D' kunnr = 'C001' hkont = '120000' shkzg = 'S' dmbtr = '1500.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000007' gjahr = '2026' buzei = '002' koart = 'S' hkont = '400000' shkzg = 'H' dmbtr = '1500.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000008' gjahr = '2026' buzei = '001' koart = 'D' kunnr = 'C005' hkont = '120000' shkzg = 'S' dmbtr = '780.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000008' gjahr = '2026' buzei = '002' koart = 'S' hkont = '400000' shkzg = 'H' dmbtr = '780.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000009' gjahr = '2026' buzei = '001' koart = 'D' kunnr = 'C003' hkont = '120000' shkzg = 'S' dmbtr = '1600.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000009' gjahr = '2026' buzei = '002' koart = 'S' hkont = '400000' shkzg = 'H' dmbtr = '1600.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000010' gjahr = '2026' buzei = '001' koart = 'D' kunnr = 'C001' hkont = '120000' shkzg = 'S' dmbtr = '640.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000010' gjahr = '2026' buzei = '002' koart = 'S' hkont = '400000' shkzg = 'H' dmbtr = '640.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000011' gjahr = '2026' buzei = '001' koart = 'D' kunnr = 'C006' hkont = '120000' shkzg = 'S' dmbtr = '300.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000011' gjahr = '2026' buzei = '002' koart = 'S' hkont = '400000' shkzg = 'H' dmbtr = '300.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000012' gjahr = '2026' buzei = '001' koart = 'D' kunnr = 'C003' hkont = '120000' shkzg = 'S' dmbtr = '400.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '0100000012' gjahr = '2026' buzei = '002' koart = 'S' hkont = '400000' shkzg = 'H' dmbtr = '400.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1400000001' gjahr = '2026' buzei = '001' koart = 'S' hkont = '113100' shkzg = 'S' dmbtr = '520.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1400000001' gjahr = '2026' buzei = '002' koart = 'D' kunnr = 'C001' hkont = '120000' shkzg = 'H' dmbtr = '520.00' waers = 'EUR' augbl = '1400000001' augdt = '20260209' )
      ( bukrs = '1000' belnr = '1400000002' gjahr = '2026' buzei = '001' koart = 'S' hkont = '113100' shkzg = 'S' dmbtr = '1470.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1400000002' gjahr = '2026' buzei = '002' koart = 'D' kunnr = 'C002' hkont = '120000' shkzg = 'H' dmbtr = '1470.00' waers = 'EUR' augbl = '1400000002' augdt = '20260310' )
      ( bukrs = '1000' belnr = '1400000003' gjahr = '2026' buzei = '001' koart = 'S' hkont = '113100' shkzg = 'S' dmbtr = '1300.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1400000003' gjahr = '2026' buzei = '002' koart = 'D' kunnr = 'C003' hkont = '120000' shkzg = 'H' dmbtr = '1300.00' waers = 'EUR' augbl = '1400000003' augdt = '20260420' )
      ( bukrs = '1000' belnr = '1500000001' gjahr = '2026' buzei = '001' koart = 'S' hkont = '600000' shkzg = 'S' dmbtr = '250.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1500000001' gjahr = '2026' buzei = '002' koart = 'S' hkont = '113100' shkzg = 'H' dmbtr = '200.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1900000001' gjahr = '2026' buzei = '001' koart = 'S' hkont = '500000' shkzg = 'S' dmbtr = '1200.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1900000001' gjahr = '2026' buzei = '002' koart = 'K' lifnr = 'V200' hkont = '210000' shkzg = 'H' dmbtr = '1200.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1900000002' gjahr = '2026' buzei = '001' koart = 'S' hkont = '500000' shkzg = 'S' dmbtr = '1200.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1900000002' gjahr = '2026' buzei = '002' koart = 'K' lifnr = 'V200' hkont = '210000' shkzg = 'H' dmbtr = '1200.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1900000003' gjahr = '2026' buzei = '001' koart = 'S' hkont = '500000' shkzg = 'S' dmbtr = '760.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1900000003' gjahr = '2026' buzei = '002' koart = 'K' lifnr = 'V500' hkont = '210000' shkzg = 'H' dmbtr = '760.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1900000004' gjahr = '2026' buzei = '001' koart = 'S' hkont = '500000' shkzg = 'S' dmbtr = '760.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1900000004' gjahr = '2026' buzei = '002' koart = 'K' lifnr = 'V500' hkont = '210000' shkzg = 'H' dmbtr = '760.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1900000005' gjahr = '2026' buzei = '001' koart = 'S' hkont = '500000' shkzg = 'S' dmbtr = '300.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1900000005' gjahr = '2026' buzei = '002' koart = 'K' lifnr = 'V100' hkont = '210000' shkzg = 'H' dmbtr = '300.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1900000006' gjahr = '2026' buzei = '001' koart = 'S' hkont = '500000' shkzg = 'S' dmbtr = '300.00' waers = 'EUR' )
      ( bukrs = '1000' belnr = '1900000006' gjahr = '2026' buzei = '002' koart = 'K' lifnr = 'V300' hkont = '210000' shkzg = 'H' dmbtr = '300.00' waers = 'EUR' ) ).
  ENDMETHOD.
ENDCLASS.
```

왜 이렇게 쓰나
- `client`를 VALUE에 적지 않았습니다. ABAP SQL `INSERT`는 클라이언트 필드를 현재 클라이언트로 자동으로 채웁니다(ABAP Cloud에서는 클라이언트를 직접 다룰 수 없습니다).
- 입고일 `wedat`와 반제 필드 `augbl`·`augdt`를 적지 않은 행은 초기값으로 들어갑니다. "미입고", "미결"을 이렇게 표현합니다.
- 데이터를 메서드로 돌려주게 한 것이 핵심입니다. DB 적재(`main`)와 채점용 테스트 더블(3단계)이 **같은 원본**을 쓰므로, 데이터를 고칠 때 한 곳만 고치면 됩니다.
- `INSERT ... FROM TABLE`에는 내부 테이블 변수를 넘깁니다. 메서드 결과를 바로 넘기는 호스트 식(`@( lfa1( ) )`)도 문법상 가능해 보이지만 릴리스에 따라 막힐 수 있어 변수에 담았습니다.

자주 나는 오류와 해결
- `DUPLICATE_KEY` 덤프: `DELETE FROM`을 빼고 두 번 실행한 경우입니다.
- 금액 문자열 `'0.12'`를 따옴표 없이 `0.12`로 쓰면 ABAP에서는 숫자 리터럴에 소수점을 쓸 수 없어 구문 오류가 납니다. 소수는 문자 리터럴로 넣으세요.

</details>

#### 3단계. 풀이 클래스 뼈대와 채점기 `LTC_GRADE`

요구사항
1. 클래스 `ZCL_SQ_QUERIES_###`(PUBLIC FINAL CREATE PUBLIC)를 만들고, 아래 정답의 **공개 타입과 메서드 선언을 그대로** 넣으세요. 결과 타입(`tt_q01`~`tt_q20`)이 곧 "요구 결과 열"입니다. 메서드 본문은 비워 둡니다(빈 결과를 돌려줌).
2. `if_oo_adt_classrun~main`에서 메서드를 하나 불러 결과를 출력할 수 있게 해 두세요(풀면서 눈으로 확인하는 용도).
3. 같은 클래스의 **Test Classes** 탭에 채점기 `ltc_grade`를 만듭니다.
   - `class_setup`: `cl_osql_test_environment=>create`로 9개 테이블을 SQL 테스트 더블로 바꾸고, `ZCL_SQ_SEED_###`의 데이터를 `insert_test_data`로 넣습니다.
   - `class_teardown`: `destroy`.
   - 문항별 테스트 메서드 `q01`~`q20`은 각 문항 단계에서 하나씩 붙여 넣습니다. 이 단계에서는 `q01` 하나만 넣어 **빨간 결과(실패)**를 확인하세요.
4. 정렬 순서도 채점 대상입니다. 기대 결과와 같은 순서로 `ORDER BY`를 써야 통과합니다.

**확인**
- Ctrl+Shift+F10(ABAP Unit 실행) → `q01`이 실패하고, 실패 메시지에 기대 결과 6행과 실제 결과 0행의 차이가 보입니다.
- DB 테이블을 비우거나 바꿔도 채점 결과가 달라지지 않아야 합니다(테스트 더블을 쓰기 때문).

<details><summary>정답·해설</summary>

```abap
CLASS zcl_sq_queries_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.

    TYPES ty_amount TYPE p LENGTH 15 DECIMALS 2.
    TYPES ty_avg4   TYPE p LENGTH 15 DECIMALS 4.
    TYPES ty_pct1   TYPE p LENGTH 8 DECIMALS 1.
    TYPES ty_pct2   TYPE p LENGTH 8 DECIMALS 2.
    TYPES ty_period TYPE c LENGTH 6.
    TYPES tt_lifnr  TYPE STANDARD TABLE OF zsq_lfa1_###-lifnr WITH EMPTY KEY.

    " ---- R-19 구매 ----
    TYPES: BEGIN OF ty_q01,
             lifnr      TYPE zsq_lfa1_###-lifnr,
             name1      TYPE zsq_lfa1_###-name1,
             po_count   TYPE i,
             item_count TYPE i,
             net_value  TYPE ty_amount,
           END OF ty_q01,
           tt_q01 TYPE STANDARD TABLE OF ty_q01 WITH EMPTY KEY.
    TYPES: BEGIN OF ty_q02,
             ebeln     TYPE zsq_ekpo_###-ebeln,
             ebelp     TYPE zsq_ekpo_###-ebelp,
             matnr     TYPE zsq_ekpo_###-matnr,
             lifnr     TYPE zsq_ekko_###-lifnr,
             netpr     TYPE ty_amount,
             avg_netpr TYPE ty_avg4,
             diff_pct  TYPE ty_pct2,
           END OF ty_q02,
           tt_q02 TYPE STANDARD TABLE OF ty_q02 WITH EMPTY KEY.
    TYPES: BEGIN OF ty_q03,
             matnr      TYPE zsq_mara_###-matnr,
             maktx      TYPE zsq_mara_###-maktx,
             vendor_cnt TYPE i,
             min_netpr  TYPE ty_amount,
             max_netpr  TYPE ty_amount,
             spread_pct TYPE ty_pct2,
           END OF ty_q03,
           tt_q03 TYPE STANDARD TABLE OF ty_q03 WITH EMPTY KEY.
    TYPES: BEGIN OF ty_q04,
             lifnr           TYPE zsq_ekko_###-lifnr,
             due_items       TYPE i,
             late_items      TYPE i,
             open_late_items TYPE i,
             max_delay_days  TYPE i,
             ontime_pct      TYPE ty_pct1,
           END OF ty_q04,
           tt_q04 TYPE STANDARD TABLE OF ty_q04 WITH EMPTY KEY.
    TYPES: BEGIN OF ty_q05,
             matnr        TYPE zsq_mara_###-matnr,
             maktx        TYPE zsq_mara_###-maktx,
             last_po_date TYPE d,
             days_since   TYPE i,
             status       TYPE c LENGTH 5,
           END OF ty_q05,
           tt_q05 TYPE STANDARD TABLE OF ty_q05 WITH EMPTY KEY.
    TYPES: BEGIN OF ty_q06,
             ekgrp       TYPE zsq_ekko_###-ekgrp,
             q1_value    TYPE ty_amount,
             q2_value    TYPE ty_amount,
             total_value TYPE ty_amount,
             growth_pct  TYPE ty_pct1,
           END OF ty_q06,
           tt_q06 TYPE STANDARD TABLE OF ty_q06 WITH EMPTY KEY.
    TYPES: BEGIN OF ty_q07,
             lifnr     TYPE zsq_ekko_###-lifnr,
             item_cnt  TYPE i,
             avg_netpr TYPE ty_avg4,
           END OF ty_q07,
           tt_q07 TYPE STANDARD TABLE OF ty_q07 WITH EMPTY KEY.

    " ---- R-20 판매 ----
    TYPES: BEGIN OF ty_q08,
             kunnr        TYPE zsq_vbak_###-kunnr,
             first_vbeln  TYPE zsq_vbak_###-vbeln,
             first_date   TYPE d,
             second_vbeln TYPE zsq_vbak_###-vbeln,
             second_date  TYPE d,
             days_between TYPE i,
           END OF ty_q08,
           tt_q08 TYPE STANDARD TABLE OF ty_q08 WITH EMPTY KEY.
    TYPES: BEGIN OF ty_q09,
             period     TYPE ty_period,
             net_value  TYPE ty_amount,
             cum_value  TYPE ty_amount,
             prev_value TYPE ty_amount,
             mom_pct    TYPE ty_pct1,
           END OF ty_q09,
           tt_q09 TYPE STANDARD TABLE OF ty_q09 WITH EMPTY KEY.
    TYPES: BEGIN OF ty_q10,
             land1     TYPE zsq_kna1_###-land1,
             rank_no   TYPE i,
             kunnr     TYPE zsq_kna1_###-kunnr,
             name1     TYPE zsq_kna1_###-name1,
             net_value TYPE ty_amount,
             share_pct TYPE ty_pct1,
           END OF ty_q10,
           tt_q10 TYPE STANDARD TABLE OF ty_q10 WITH EMPTY KEY.
    TYPES: BEGIN OF ty_q11,
             kunnr        TYPE zsq_vbak_###-kunnr,
             order_cnt    TYPE i,
             avg_gap_days TYPE ty_pct1,
             max_gap_days TYPE i,
           END OF ty_q11,
           tt_q11 TYPE STANDARD TABLE OF ty_q11 WITH EMPTY KEY.
    TYPES: BEGIN OF ty_q12,
             matnr     TYPE zsq_vbap_###-matnr,
             net_value TYPE ty_amount,
             share_pct TYPE ty_pct2,
             cum_pct   TYPE ty_pct2,
             abc_class TYPE c LENGTH 1,
           END OF ty_q12,
           tt_q12 TYPE STANDARD TABLE OF ty_q12 WITH EMPTY KEY.
    TYPES: BEGIN OF ty_q13,
             kunnr        TYPE zsq_vbak_###-kunnr,
             start_period TYPE ty_period,
             end_period   TYPE ty_period,
             months       TYPE i,
           END OF ty_q13,
           tt_q13 TYPE STANDARD TABLE OF ty_q13 WITH EMPTY KEY.
    TYPES: BEGIN OF ty_q14,
             period    TYPE ty_period,
             net_value TYPE ty_amount,
             mov_sum3  TYPE ty_amount,
             mov_cnt   TYPE i,
             mov_avg3  TYPE ty_amount,
           END OF ty_q14,
           tt_q14 TYPE STANDARD TABLE OF ty_q14 WITH EMPTY KEY.

    " ---- R-21 회계 ----
    TYPES: BEGIN OF ty_q15,
             belnr  TYPE zsq_bkpf_###-belnr,
             blart  TYPE zsq_bkpf_###-blart,
             debit  TYPE ty_amount,
             credit TYPE ty_amount,
             diff   TYPE ty_amount,
           END OF ty_q15,
           tt_q15 TYPE STANDARD TABLE OF ty_q15 WITH EMPTY KEY.
    TYPES: BEGIN OF ty_q16,
             row_level TYPE i,
             hkont     TYPE zsq_bseg_###-hkont,
             period    TYPE ty_period,
             amount    TYPE ty_amount,
           END OF ty_q16,
           tt_q16 TYPE STANDARD TABLE OF ty_q16 WITH EMPTY KEY.
    TYPES: BEGIN OF ty_q17,
             kunnr          TYPE zsq_kna1_###-kunnr,
             name1          TYPE zsq_kna1_###-name1,
             bucket_0_30    TYPE ty_amount,
             bucket_31_60   TYPE ty_amount,
             bucket_61_90   TYPE ty_amount,
             bucket_91_plus TYPE ty_amount,
             total_open     TYPE ty_amount,
             oldest_days    TYPE i,
           END OF ty_q17,
           tt_q17 TYPE STANDARD TABLE OF ty_q17 WITH EMPTY KEY.
    TYPES: BEGIN OF ty_q18,
             invoice_no     TYPE zsq_bseg_###-belnr,
             kunnr          TYPE zsq_bseg_###-kunnr,
             invoice_amount TYPE ty_amount,
             clearing_doc   TYPE zsq_bseg_###-augbl,
             clearing_date  TYPE d,
             paid_amount    TYPE ty_amount,
             difference     TYPE ty_amount,
           END OF ty_q18,
           tt_q18 TYPE STANDARD TABLE OF ty_q18 WITH EMPTY KEY.
    TYPES: BEGIN OF ty_q19,
             doc_ref  TYPE c LENGTH 16,
             kunnr    TYPE zsq_vbak_###-kunnr,
             so_value TYPE ty_amount,
             fi_value TYPE ty_amount,
             status   TYPE c LENGTH 14,
           END OF ty_q19,
           tt_q19 TYPE STANDARD TABLE OF ty_q19 WITH EMPTY KEY.
    TYPES: BEGIN OF ty_q20,
             lifnr      TYPE zsq_bseg_###-lifnr,
             belnr_1    TYPE zsq_bkpf_###-belnr,
             xblnr_1    TYPE zsq_bkpf_###-xblnr,
             belnr_2    TYPE zsq_bkpf_###-belnr,
             xblnr_2    TYPE zsq_bkpf_###-xblnr,
             amount     TYPE ty_amount,
             days_apart TYPE i,
           END OF ty_q20,
           tt_q20 TYPE STANDARD TABLE OF ty_q20 WITH EMPTY KEY.

    CONSTANTS c_key_date TYPE d VALUE '20260630'.

    METHODS q01 RETURNING VALUE(result) TYPE tt_q01.
    METHODS q02 RETURNING VALUE(result) TYPE tt_q02.
    METHODS q03 RETURNING VALUE(result) TYPE tt_q03.
    METHODS q04 IMPORTING iv_key_date TYPE d DEFAULT c_key_date
                RETURNING VALUE(result) TYPE tt_q04.
    METHODS q05 IMPORTING iv_key_date TYPE d DEFAULT c_key_date
                RETURNING VALUE(result) TYPE tt_q05.
    METHODS q06 RETURNING VALUE(result) TYPE tt_q06.
    METHODS q07 IMPORTING it_vendors TYPE tt_lifnr
                RETURNING VALUE(result) TYPE tt_q07.
    METHODS q08 RETURNING VALUE(result) TYPE tt_q08.
    METHODS q09 RETURNING VALUE(result) TYPE tt_q09.
    METHODS q10 RETURNING VALUE(result) TYPE tt_q10.
    METHODS q11 RETURNING VALUE(result) TYPE tt_q11.
    METHODS q12 RETURNING VALUE(result) TYPE tt_q12.
    METHODS q13 RETURNING VALUE(result) TYPE tt_q13.
    METHODS q14 RETURNING VALUE(result) TYPE tt_q14.
    METHODS q15 RETURNING VALUE(result) TYPE tt_q15.
    METHODS q16 RETURNING VALUE(result) TYPE tt_q16.
    METHODS q17 IMPORTING iv_key_date TYPE d DEFAULT c_key_date
                RETURNING VALUE(result) TYPE tt_q17.
    METHODS q18 RETURNING VALUE(result) TYPE tt_q18.
    METHODS q19 RETURNING VALUE(result) TYPE tt_q19.
    METHODS q20 RETURNING VALUE(result) TYPE tt_q20.

  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.


CLASS zcl_sq_queries_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.
    " 풀고 있는 문항으로 바꿔 가며 결과를 눈으로 확인
    out->write( q01( ) ).
  ENDMETHOD.

  METHOD q01.
  ENDMETHOD.

  " ... q02 ~ q20 도 같은 모양으로 빈 본문
ENDCLASS.
```

Test Classes 탭:

```abap
CLASS ltc_grade DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    CLASS-DATA env TYPE REF TO if_osql_test_environment.
    DATA cut TYPE REF TO zcl_sq_queries_###.

    CLASS-METHODS class_setup.
    CLASS-METHODS class_teardown.
    METHODS setup.

    METHODS q01 FOR TESTING.
    " 각 문항 단계에서 q02 ~ q20 을 여기에 추가
ENDCLASS.


CLASS ltc_grade IMPLEMENTATION.

  METHOD class_setup.
    env = cl_osql_test_environment=>create( i_dependency_list = VALUE #(
            ( 'ZSQ_LFA1_###' ) ( 'ZSQ_MARA_###' ) ( 'ZSQ_EKKO_###' ) ( 'ZSQ_EKPO_###' )
            ( 'ZSQ_KNA1_###' ) ( 'ZSQ_VBAK_###' ) ( 'ZSQ_VBAP_###' )
            ( 'ZSQ_BKPF_###' ) ( 'ZSQ_BSEG_###' ) ) ).

    DATA(seed) = NEW zcl_sq_seed_###( ).
    DATA(lt_lfa1) = seed->lfa1( ).  env->insert_test_data( lt_lfa1 ).
    DATA(lt_mara) = seed->mara( ).  env->insert_test_data( lt_mara ).
    DATA(lt_ekko) = seed->ekko( ).  env->insert_test_data( lt_ekko ).
    DATA(lt_ekpo) = seed->ekpo( ).  env->insert_test_data( lt_ekpo ).
    DATA(lt_kna1) = seed->kna1( ).  env->insert_test_data( lt_kna1 ).
    DATA(lt_vbak) = seed->vbak( ).  env->insert_test_data( lt_vbak ).
    DATA(lt_vbap) = seed->vbap( ).  env->insert_test_data( lt_vbap ).
    DATA(lt_bkpf) = seed->bkpf( ).  env->insert_test_data( lt_bkpf ).
    DATA(lt_bseg) = seed->bseg( ).  env->insert_test_data( lt_bseg ).
  ENDMETHOD.

  METHOD class_teardown.
    env->destroy( ).
  ENDMETHOD.

  METHOD setup.
    cut = NEW #( ).
  ENDMETHOD.

  METHOD q01.
    " 4단계의 채점 메서드를 여기에 붙여 넣습니다
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나
- **결과 타입을 먼저 고정**하는 것이 쿼리포터식 채점의 핵심입니다. 열 이름·타입·순서가 정해져 있으니 `cl_abap_unit_assert=>assert_equals`가 내부 테이블 두 개를 행 단위로 비교할 수 있습니다. 실패하면 ADT가 어느 행·어느 열이 다른지 표로 보여 줍니다.
- 금액 결과는 `p LENGTH 15 DECIMALS 2`로 받습니다. SQL 식 결과의 소수 자릿수가 더 길면(예: 수량 × 단가 = 소수 5자리) 할당하면서 반올림됩니다. 비율은 문항마다 소수 1자리(`ty_pct1`) 또는 2자리(`ty_pct2`)로 정했습니다.
- `cl_osql_test_environment`는 테스트가 도는 동안 9개 테이블에 대한 ABAP SQL 접근을 **테스트 더블 테이블**로 돌립니다. 그래서 여러분이 DB에서 데이터를 바꿔도 채점 결과는 항상 같습니다. CTE, 윈도 함수, `FROM @itab`이 들어간 SQL도 그대로 리다이렉트됩니다(실제 시스템에서 확인 필요).
- 테스트 더블은 `class_setup`에서 한 번만 만듭니다. 문항 테스트가 모두 읽기만 하므로 테스트마다 다시 넣을 필요가 없습니다.

자주 나는 오류와 해결
- `insert_test_data( seed->lfa1( ) )`처럼 메서드 호출을 바로 넘기면 일반(generic) 파라미터라서 오류가 날 수 있습니다. 변수에 담아 넘기세요.
- 테이블 이름을 소문자로 넣어도 되지만, 목록에 빠진 테이블이 있으면 그 테이블은 **실제 DB를 읽습니다**. 채점 결과가 DB 내용에 따라 바뀌면 의존 목록부터 확인하세요.

</details>

#### 4단계. Q01 공급업체별 구매 실적 — LEFT JOIN의 ON과 WHERE

요구사항
1. `q01`을 구현하세요. **모든 공급업체**(구매 오더가 없어도)를 한 행씩 돌려줍니다.
   - `po_count`: 그 공급업체의 구매 오더 수(서로 다른 `ebeln` 수).
   - `item_count`: 삭제 표시가 없는(`loekz`가 공백) 품목 수.
   - `net_value`: 삭제 표시가 없는 품목의 `menge × netpr` 합계. 품목이 없으면 0.
2. 정렬: `net_value` 내림차순, 같으면 `lifnr` 오름차순.
3. **SELECT 한 번**으로 끝내세요(루프 안 SELECT, ABAP 쪽 합산 금지).

기대 결과

| lifnr | name1 | po_count | item_count | net_value |
|---|---|---|---|---|
| V300 | Pacific Parts | 2 | 4 | 6334.00 |
| V400 | 대성기계 | 2 | 4 | 5738.50 |
| V200 | Nord Supply | 3 | 8 | 4401.00 |
| V500 | Alpen Tech | 2 | 4 | 3551.00 |
| V100 | 한빛상사 | 3 | 7 | 1815.00 |
| V600 | Idle Vendor | 0 | 0 | 0.00 |

채점 메서드 (`ltc_grade`에 추가)

```abap
  METHOD q01.
    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q01(
      ( lifnr = 'V300' name1 = 'Pacific Parts' po_count = 2 item_count = 4 net_value = '6334.00' )
      ( lifnr = 'V400' name1 = '대성기계' po_count = 2 item_count = 4 net_value = '5738.50' )
      ( lifnr = 'V200' name1 = 'Nord Supply' po_count = 3 item_count = 8 net_value = '4401.00' )
      ( lifnr = 'V500' name1 = 'Alpen Tech' po_count = 2 item_count = 4 net_value = '3551.00' )
      ( lifnr = 'V100' name1 = '한빛상사' po_count = 3 item_count = 7 net_value = '1815.00' )
      ( lifnr = 'V600' name1 = 'Idle Vendor' po_count = 0 item_count = 0 net_value = '0.00' ) ).
    cl_abap_unit_assert=>assert_equals( act = cut->q01( ) exp = exp msg = 'Q01' ).
  ENDMETHOD.
```

(정의 부분에 `METHODS q01 FOR TESTING.`을 추가하세요.)

<details><summary>정답·해설</summary>

```abap
  METHOD q01.
    SELECT FROM zsq_lfa1_### AS v
           LEFT OUTER JOIN zsq_ekko_### AS k
             ON k~lifnr = v~lifnr
           LEFT OUTER JOIN zsq_ekpo_### AS p
             ON  p~ebeln = k~ebeln
             AND p~loekz = @space                       " ← 삭제 품목 제외는 ON에서
      FIELDS v~lifnr,
             v~name1,
             COUNT( DISTINCT k~ebeln )                  AS po_count,
             COUNT( p~ebelp )                           AS item_count,
             COALESCE( SUM( CAST( p~menge AS DEC( 13, 3 ) ) * CAST( p~netpr AS DEC( 11, 2 ) ) ), 0 )
                                                        AS net_value
      GROUP BY v~lifnr, v~name1
      ORDER BY net_value DESCENDING, v~lifnr
      INTO CORRESPONDING FIELDS OF TABLE @result.
  ENDMETHOD.
```

왜 이렇게 쓰나
- **행의 단위**는 "공급업체 1명"입니다. 공급업체 테이블을 왼쪽에 두고 LEFT OUTER JOIN으로 붙여야 오더가 없는 `V600`도 남습니다.
- 삭제 표시 조건을 `WHERE p~loekz = @space`에 두면, 오른쪽이 없는 행(`V600`의 `p~loekz`는 NULL)이 `NULL = ' '` 비교에서 거짓이 되어 **잘려 나갑니다**. LEFT JOIN이 사실상 INNER JOIN이 되는 것입니다. 오른쪽 테이블을 거르는 조건은 `ON`에 두세요.
- `COUNT( * )`가 아니라 `COUNT( p~ebelp )`를 써야 품목이 없는 행이 0으로 셉니다(`COUNT( 열 )`은 NULL을 세지 않음). `COUNT( DISTINCT k~ebeln )`은 품목 조인으로 오더가 여러 번 복제돼도 한 번만 셉니다.
- `SUM`이 NULL(합할 행 없음)을 돌려주므로 `COALESCE( ..., 0 )`으로 0을 만듭니다. 사실 ABAP으로 받을 때 NULL은 초기값(0)이 되므로 COALESCE 없이도 이 문항은 통과합니다. 하지만 이 값을 다른 식에 쓰거나 CDS로 옮기면 NULL이 계산 전체를 NULL로 만들므로 습관적으로 처리하세요.
- `CAST`로 QUAN·CURR를 DEC로 바꾼 뒤 곱했습니다. 통화·수량 타입끼리의 산술은 시스템 버전에 따라 막힐 수 있어 DEC로 바꾸는 쪽이 안전합니다(실제 시스템에서 확인 필요).

오답이 나오는 전형적인 실수
- `V100`의 `item_count`가 8 → 삭제 품목(`4500000003/30`)을 뺀다는 조건을 잊음.
- `V600`이 없음 → 조건을 `WHERE`에 둠, 또는 INNER JOIN 사용.
- `po_count`가 품목 수와 같게 나옴 → `DISTINCT`를 빠뜨림.
- 순서만 다름 → `ORDER BY`에서 동점 처리용 두 번째 키(`lifnr`)를 빠뜨림. 채점은 순서까지 봅니다.

</details>

#### 5단계. Q02 자재 평균 단가보다 비싸게 산 품목 — CTE로 집계 결과 다시 조인

요구사항
1. 삭제되지 않은 품목만 대상으로, **같은 자재의 평균 단가**보다 `netpr`가 높은 품목을 찾으세요.
2. 결과 열: `ebeln`, `ebelp`, `matnr`, `lifnr`(오더 헤더의 공급업체), `netpr`, `avg_netpr`(그 자재의 평균 단가, 소수 4자리), `diff_pct` = (`netpr` − 평균) × 100 ÷ 평균, 소수 2자리 반올림.
3. 정렬: `matnr`, `ebeln`, `ebelp`.
4. 평균을 구할 때도 삭제 품목은 빼야 합니다(`M07`의 삭제 품목 단가 950.00이 평균에 들어가면 결과가 달라집니다).

기대 결과

| ebeln | ebelp | matnr | lifnr | netpr | avg_netpr | diff_pct |
|---|---|---|---|---|---|---|
| 4500000001 | 10 | M01 | V100 | 0.12 | 0.1125 | 6.67 |
| 4500000008 | 10 | M01 | V100 | 0.12 | 0.1125 | 6.67 |
| 4500000011 | 20 | M02 | V500 | 0.10 | 0.0900 | 11.11 |
| 4500000004 | 20 | M03 | V300 | 3.45 | 3.2200 | 7.14 |
| 4500000012 | 20 | M03 | V200 | 3.30 | 3.2200 | 2.48 |
| 4500000007 | 10 | M04 | V500 | 192.00 | 185.5000 | 3.50 |
| 4500000011 | 10 | M04 | V500 | 189.00 | 185.5000 | 1.89 |
| 4500000006 | 20 | M05 | V200 | 2.55 | 2.4750 | 3.03 |
| 4500000012 | 30 | M05 | V200 | 2.60 | 2.4750 | 5.05 |
| 4500000001 | 30 | M06 | V100 | 4.50 | 4.4000 | 2.27 |
| 4500000008 | 20 | M06 | V100 | 4.50 | 4.4000 | 2.27 |
| 4500000007 | 20 | M07 | V500 | 990.00 | 950.0000 | 4.21 |

채점 메서드

```abap
  METHOD q02.
    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q02(
      ( ebeln = '4500000001' ebelp = '00010' matnr = 'M01' lifnr = 'V100' netpr = '0.12' avg_netpr = '0.1125' diff_pct = '6.67' )
      ( ebeln = '4500000008' ebelp = '00010' matnr = 'M01' lifnr = 'V100' netpr = '0.12' avg_netpr = '0.1125' diff_pct = '6.67' )
      ( ebeln = '4500000011' ebelp = '00020' matnr = 'M02' lifnr = 'V500' netpr = '0.10' avg_netpr = '0.0900' diff_pct = '11.11' )
      ( ebeln = '4500000004' ebelp = '00020' matnr = 'M03' lifnr = 'V300' netpr = '3.45' avg_netpr = '3.2200' diff_pct = '7.14' )
      ( ebeln = '4500000012' ebelp = '00020' matnr = 'M03' lifnr = 'V200' netpr = '3.30' avg_netpr = '3.2200' diff_pct = '2.48' )
      ( ebeln = '4500000007' ebelp = '00010' matnr = 'M04' lifnr = 'V500' netpr = '192.00' avg_netpr = '185.5000' diff_pct = '3.50' )
      ( ebeln = '4500000011' ebelp = '00010' matnr = 'M04' lifnr = 'V500' netpr = '189.00' avg_netpr = '185.5000' diff_pct = '1.89' )
      ( ebeln = '4500000006' ebelp = '00020' matnr = 'M05' lifnr = 'V200' netpr = '2.55' avg_netpr = '2.4750' diff_pct = '3.03' )
      ( ebeln = '4500000012' ebelp = '00030' matnr = 'M05' lifnr = 'V200' netpr = '2.60' avg_netpr = '2.4750' diff_pct = '5.05' )
      ( ebeln = '4500000001' ebelp = '00030' matnr = 'M06' lifnr = 'V100' netpr = '4.50' avg_netpr = '4.4000' diff_pct = '2.27' )
      ( ebeln = '4500000008' ebelp = '00020' matnr = 'M06' lifnr = 'V100' netpr = '4.50' avg_netpr = '4.4000' diff_pct = '2.27' )
      ( ebeln = '4500000007' ebelp = '00020' matnr = 'M07' lifnr = 'V500' netpr = '990.00' avg_netpr = '950.0000' diff_pct = '4.21' ) ).
    cl_abap_unit_assert=>assert_equals( act = cut->q02( ) exp = exp msg = 'Q02' ).
  ENDMETHOD.
```

(정의 부분에 `METHODS q02 FOR TESTING.`을 추가하세요.)

<details><summary>정답·해설</summary>

```abap
  METHOD q02.
    WITH
      +avg AS ( SELECT FROM zsq_ekpo_###
                  FIELDS matnr,
                         AVG( netpr AS DEC( 15, 4 ) ) AS avg_netpr
                  WHERE loekz = @space
                  GROUP BY matnr )
      SELECT FROM zsq_ekpo_### AS p
             INNER JOIN zsq_ekko_### AS k ON k~ebeln = p~ebeln
             INNER JOIN +avg         AS a ON a~matnr = p~matnr
        FIELDS p~ebeln,
               p~ebelp,
               p~matnr,
               k~lifnr,
               p~netpr,
               a~avg_netpr,
               DIVISION( ( CAST( p~netpr AS DEC( 15, 4 ) ) - a~avg_netpr ) * 100, a~avg_netpr, 2 ) AS diff_pct
        WHERE p~loekz = @space
          AND CAST( p~netpr AS DEC( 15, 4 ) ) > a~avg_netpr
        ORDER BY p~matnr, p~ebeln, p~ebelp
        INTO CORRESPONDING FIELDS OF TABLE @result.
  ENDMETHOD.
```

왜 이렇게 쓰나
- 결과에 **평균값을 열로 보여 줘야** 하므로, `WHERE netpr > ( SELECT AVG(...) ... )` 같은 서브쿼리만으로는 부족합니다(ABAP SQL은 SELECT 목록에 스칼라 서브쿼리를 쓸 수 없습니다). 그래서 자재별 평균을 CTE `+avg`로 한 번 만들고 원래 품목에 다시 조인합니다.
- CTE 이름은 `+`로 시작합니다. `WITH` 뒤의 CTE들은 위에서 아래로 차례로 정의되고, 아래 CTE와 본 쿼리가 위의 CTE를 테이블처럼 씁니다.
- `AVG( 열 AS DEC( 15, 4 ) )`는 평균의 결과 타입을 정하는 ABAP SQL 문법입니다. 이걸 빼면 평균이 FLTP(부동소수)로 나와 `0.1125`가 `0.11249999…`처럼 될 수 있고, 그러면 비교·채점이 흔들립니다.
- `DIVISION( 피제수, 제수, 소수자릿수 )`는 지정한 자릿수로 **반올림**한 나눗셈입니다. `/` 연산자는 정수끼리면 정수 나눗셈, DEC면 결과 자릿수가 정해지지 않아 채점이 어려워집니다.

오답이 나오는 전형적인 실수
- `M07` 행이 없음 → 평균에 삭제 품목 950.00이 들어가 평균이 950.00 → 990.00만 남아야 하는데, 반대로 940.00 같은 값이 섞이거나 평균이 달라짐. CTE 안에도 `loekz` 조건이 필요합니다.
- `diff_pct`가 0.01씩 다름 → `ROUND`가 아닌 버림이 되는 식을 썼거나, 평균을 소수 2자리로 먼저 반올림한 뒤 나눔.

</details>

#### 6단계. Q03 공급처가 3곳 이상인 자재와 단가 편차 — HAVING과 집계 식

요구사항
1. 삭제되지 않은 품목 기준으로 **서로 다른 공급업체 3곳 이상**에서 산 자재를 찾으세요.
2. 결과 열: `matnr`, `maktx`, `vendor_cnt`, `min_netpr`, `max_netpr`, `spread_pct` = (최고 − 최저) × 100 ÷ 최저, 소수 2자리.
3. 정렬: `spread_pct` 내림차순, 같으면 `matnr`.

기대 결과

| matnr | maktx | vendor_cnt | min_netpr | max_netpr | spread_pct |
|---|---|---|---|---|---|
| M02 | 너트 M8 | 3 | 0.08 | 0.10 | 25.00 |
| M03 | 베어링 6204 | 3 | 3.05 | 3.45 | 13.11 |
| M05 | 케이블 2m | 3 | 2.35 | 2.60 | 10.64 |
| M04 | 모터 1kW | 3 | 179.50 | 192.00 | 6.96 |

채점 메서드

```abap
  METHOD q03.
    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q03(
      ( matnr = 'M02' maktx = '너트 M8' vendor_cnt = 3 min_netpr = '0.08' max_netpr = '0.10' spread_pct = '25.00' )
      ( matnr = 'M03' maktx = '베어링 6204' vendor_cnt = 3 min_netpr = '3.05' max_netpr = '3.45' spread_pct = '13.11' )
      ( matnr = 'M05' maktx = '케이블 2m' vendor_cnt = 3 min_netpr = '2.35' max_netpr = '2.60' spread_pct = '10.64' )
      ( matnr = 'M04' maktx = '모터 1kW' vendor_cnt = 3 min_netpr = '179.50' max_netpr = '192.00' spread_pct = '6.96' ) ).
    cl_abap_unit_assert=>assert_equals( act = cut->q03( ) exp = exp msg = 'Q03' ).
  ENDMETHOD.
```

(정의 부분에 `METHODS q03 FOR TESTING.`을 추가하세요.)

<details><summary>정답·해설</summary>

```abap
  METHOD q03.
    SELECT FROM zsq_ekpo_### AS p
           INNER JOIN zsq_ekko_### AS k ON k~ebeln = p~ebeln
           INNER JOIN zsq_mara_### AS m ON m~matnr = p~matnr
      FIELDS p~matnr,
             m~maktx,
             COUNT( DISTINCT k~lifnr ) AS vendor_cnt,
             MIN( p~netpr )            AS min_netpr,
             MAX( p~netpr )            AS max_netpr,
             DIVISION( ( MAX( CAST( p~netpr AS DEC( 11, 2 ) ) ) - MIN( CAST( p~netpr AS DEC( 11, 2 ) ) ) ) * 100,
                       MIN( CAST( p~netpr AS DEC( 11, 2 ) ) ), 2 ) AS spread_pct
      WHERE p~loekz = @space
      GROUP BY p~matnr, m~maktx
      HAVING COUNT( DISTINCT k~lifnr ) >= 3
      ORDER BY spread_pct DESCENDING, p~matnr
      INTO CORRESPONDING FIELDS OF TABLE @result.
  ENDMETHOD.
```

왜 이렇게 쓰나
- `WHERE`는 **묶기 전 행**을, `HAVING`은 **묶은 뒤 그룹**을 거릅니다. "공급업체 3곳 이상"은 그룹에 대한 조건이라 `HAVING`에만 쓸 수 있습니다.
- 집계 함수끼리의 산술(`MAX(...) - MIN(...)`)을 `DIVISION`에 넣을 수 있습니다. 집계 함수 안에 식(`MAX( CAST(...) )`)을 넣는 것도 됩니다.
- 자재 내역 `maktx`를 SELECT 목록에 쓰려면 `GROUP BY`에도 넣어야 합니다. 집계되지 않는 모든 열은 GROUP BY에 있어야 합니다.

오답이 나오는 전형적인 실수
- `M07`이 결과에 나옴 → 삭제 품목의 공급업체 `V100`이 세어져 3곳이 됨. `WHERE p~loekz = @space`를 빠뜨림.
- `vendor_cnt`가 품목 수로 나옴 → `COUNT( DISTINCT ... )`가 아닌 `COUNT( * )`.

</details>

#### 7단계. Q04 공급업체 납기 준수율 — 날짜 함수, CASE, 초기값 날짜

요구사항
1. 기준일 `iv_key_date`(기본 2026-06-30)까지 **납기가 지난**(`eindt <= 기준일`) 삭제되지 않은 품목만 봅니다.
2. 품목별 지연일수 = 입고했으면 `eindt`→`wedat` 일수, 아직 입고 안 했으면(`wedat` 초기값) `eindt`→기준일 일수. 0 이하이면 정시.
3. 공급업체별로 `due_items`(대상 품목 수), `late_items`(지연일수 > 0), `open_late_items`(그중 미입고), `max_delay_days`(지연 품목의 최대 지연일수, 없으면 0), `ontime_pct`(정시 품목 비율 %, 소수 1자리).
4. 정렬: `ontime_pct` 오름차순, 같으면 `lifnr`.
5. 납기가 기준일 이후인 품목(`4500000012/30`, 납기 2026-07-05)은 아직 판단할 수 없으므로 빼야 합니다.

기대 결과

| lifnr | due_items | late_items | open_late_items | max_delay_days | ontime_pct |
|---|---|---|---|---|---|
| V200 | 7 | 6 | 2 | 10 | 14.3 |
| V500 | 4 | 3 | 1 | 29 | 25.0 |
| V300 | 4 | 2 | 0 | 10 | 50.0 |
| V400 | 4 | 2 | 1 | 41 | 50.0 |
| V100 | 7 | 2 | 1 | 71 | 71.4 |

채점 메서드

```abap
  METHOD q04.
    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q04(
      ( lifnr = 'V200' due_items = 7 late_items = 6 open_late_items = 2 max_delay_days = 10 ontime_pct = '14.3' )
      ( lifnr = 'V500' due_items = 4 late_items = 3 open_late_items = 1 max_delay_days = 29 ontime_pct = '25.0' )
      ( lifnr = 'V300' due_items = 4 late_items = 2 open_late_items = 0 max_delay_days = 10 ontime_pct = '50.0' )
      ( lifnr = 'V400' due_items = 4 late_items = 2 open_late_items = 1 max_delay_days = 41 ontime_pct = '50.0' )
      ( lifnr = 'V100' due_items = 7 late_items = 2 open_late_items = 1 max_delay_days = 71 ontime_pct = '71.4' ) ).
    cl_abap_unit_assert=>assert_equals( act = cut->q04( ) exp = exp msg = 'Q04' ).
  ENDMETHOD.
```

(정의 부분에 `METHODS q04 FOR TESTING.`을 추가하세요.)

<details><summary>정답·해설</summary>

```abap
  METHOD q04.
    WITH
      +due AS ( SELECT FROM zsq_ekpo_### AS p
                  INNER JOIN zsq_ekko_### AS k ON k~ebeln = p~ebeln
                  FIELDS k~lifnr,
                         CASE WHEN p~wedat = '00000000' THEN 'X' ELSE ' ' END AS is_open,
                         CASE WHEN p~wedat = '00000000'
                              THEN DATS_DAYS_BETWEEN( p~eindt, @iv_key_date )
                              ELSE DATS_DAYS_BETWEEN( p~eindt, p~wedat )
                         END AS delay_days
                  WHERE p~loekz = @space
                    AND p~eindt <= @iv_key_date )
      SELECT FROM +due
        FIELDS lifnr,
               COUNT( * )                                                   AS due_items,
               SUM( CASE WHEN delay_days > 0 THEN 1 ELSE 0 END )            AS late_items,
               SUM( CASE WHEN delay_days > 0 AND is_open = 'X' THEN 1 ELSE 0 END ) AS open_late_items,
               MAX( CASE WHEN delay_days > 0 THEN delay_days ELSE 0 END )   AS max_delay_days,
               DIVISION( SUM( CASE WHEN delay_days <= 0 THEN 1 ELSE 0 END ) * 100, COUNT( * ), 1 )
                                                                            AS ontime_pct
        GROUP BY lifnr
        ORDER BY ontime_pct, lifnr
        INTO CORRESPONDING FIELDS OF TABLE @result.
  ENDMETHOD.
```

왜 이렇게 쓰나
- 품목 단위 계산(지연일수)과 공급업체 단위 집계를 **두 층으로 나눈** 전형적인 CTE 패턴입니다. 한 SELECT에 몰아 쓰면 같은 CASE 식을 네 번 반복해야 합니다.
- ABAP 날짜 필드의 "빈 값"은 NULL이 아니라 `'00000000'`입니다. `IS NULL`로 검사하면 아무것도 걸리지 않습니다. `DATS_DAYS_BETWEEN( '00000000', ... )`처럼 초기값 날짜를 그대로 넣으면 오류나 엉뚱한 값이 나오므로 CASE로 갈라야 합니다.
- `DATS_DAYS_BETWEEN( 시작, 끝 )`은 끝 − 시작 일수입니다. 순서를 바꾸면 부호가 반대가 됩니다.
- 비율은 "정시 건수 × 100 ÷ 전체 건수"를 `DIVISION(…, 1)`로 반올림합니다. 정수끼리 `/`로 나누면 소수가 사라집니다.

오답이 나오는 전형적인 실수
- `V200`의 `due_items`가 8 → 미래 납기 품목을 넣음.
- `V100`의 `max_delay_days`가 0 → 미입고 품목(`4500000008/20`, 납기 4/20)의 지연을 기준일까지로 계산하지 않음.
- `V300`·`V400` 순서가 바뀜 → 동점 정렬 키 누락.

</details>

#### 8단계. Q05 오래 구매하지 않은 자재 — LEFT JOIN 집계와 NULL → 초기값

요구사항
1. 자재마다 삭제되지 않은 품목의 **마지막 오더일**(`ekko.bedat`의 최댓값)을 구하세요.
2. 한 번도 산 적이 없으면 `status = 'NEVER'`, 마지막 오더일이 기준일보다 **60일 넘게** 지났으면 `'STALE'`. 이 두 경우만 결과에 남깁니다.
3. 결과 열: `matnr`, `maktx`, `last_po_date`(없으면 `00000000`), `days_since`(없으면 0), `status`. 정렬: `matnr`.
4. 경계값 주의: `M07`의 마지막 오더일 2026-05-02는 기준일까지 **59일**이라 결과에 없어야 합니다.

기대 결과

| matnr | maktx | last_po_date | days_since | status |
|---|---|---|---|---|
| M06 | 윤활유 1L | 20260405 | 86 | STALE |
| M08 | 근접 센서 | 00000000 | 0 | NEVER |

채점 메서드

```abap
  METHOD q05.
    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q05(
      ( matnr = 'M06' maktx = '윤활유 1L' last_po_date = '20260405' days_since = 86 status = 'STALE' )
      ( matnr = 'M08' maktx = '근접 센서' last_po_date = '00000000' days_since = 0 status = 'NEVER' ) ).
    cl_abap_unit_assert=>assert_equals( act = cut->q05( ) exp = exp msg = 'Q05' ).
  ENDMETHOD.
```

(정의 부분에 `METHODS q05 FOR TESTING.`을 추가하세요.)

<details><summary>정답·해설</summary>

```abap
  METHOD q05.
    WITH
      +last AS ( SELECT FROM zsq_mara_### AS m
                   LEFT OUTER JOIN zsq_ekpo_### AS p
                     ON  p~matnr = m~matnr
                     AND p~loekz = @space
                   LEFT OUTER JOIN zsq_ekko_### AS k
                     ON k~ebeln = p~ebeln
                   FIELDS m~matnr,
                          m~maktx,
                          MAX( k~bedat ) AS last_po_date
                   GROUP BY m~matnr, m~maktx )
      SELECT FROM +last
        FIELDS matnr,
               maktx,
               last_po_date,
               CASE WHEN last_po_date IS NULL THEN 0
                    ELSE DATS_DAYS_BETWEEN( last_po_date, @iv_key_date ) END AS days_since,
               CASE WHEN last_po_date IS NULL THEN 'NEVER' ELSE 'STALE' END AS status
        WHERE last_po_date IS NULL
           OR DATS_DAYS_BETWEEN( last_po_date, @iv_key_date ) > 60
        ORDER BY matnr
        INTO CORRESPONDING FIELDS OF TABLE @result.
  ENDMETHOD.
```

왜 이렇게 쓰나
- 이번에는 날짜가 **진짜 NULL**입니다. `M08`은 오른쪽 조인 상대가 없어서 `MAX( k~bedat )`가 NULL이 됩니다. 테이블에 저장된 초기값(`00000000`, Q04)과 조인·집계가 만든 NULL은 다른 것이라 검사 방법도 다릅니다(`IS NULL`).
- NULL은 ABAP 변수로 받는 순간 **초기값**이 됩니다. 그래서 `last_po_date`를 COALESCE하지 않아도 결과에는 `00000000`이 들어갑니다. 반대로 ABAP 결과만 보고 "DB 값이 00000000이었다"고 판단하면 안 됩니다. 구분이 필요하면 `IS NULL`로 표시 열을 따로 만드세요.
- 첫 번째 LEFT JOIN의 `ON`에 `loekz` 조건을 둔 이유는 Q01과 같습니다.

오답이 나오는 전형적인 실수
- `M08`이 없음 → INNER JOIN, 또는 `WHERE p~loekz = @space`.
- `M07`이 나옴 → `>= 60`으로 씀(59일이라 원래도 안 나와야 하지만, 기준일을 하루 잘못 넣으면 나옴). 경계값을 표로 직접 계산해 보세요.

</details>

#### 9단계. Q06 구매 그룹 × 분기 피벗 — 조건부 집계

요구사항
1. 구매 그룹(`ekgrp`)별로 1분기(2026-01-01~03-31)와 2분기(04-01~06-30) 구매 금액(삭제 품목 제외, `menge × netpr`)을 **열로 펼치세요**.
2. 결과 열: `ekgrp`, `q1_value`, `q2_value`, `total_value`, `growth_pct` = (Q2 − Q1) × 100 ÷ Q1, 소수 1자리. 정렬: `ekgrp`.
3. 분기 경계는 하드코딩하지 말고 호스트 변수로 넘기세요.

기대 결과

| ekgrp | q1_value | q2_value | total_value | growth_pct |
|---|---|---|---|---|
| A01 | 6011.00 | 1475.00 | 7486.00 | -75.5 |
| A02 | 4150.00 | 4080.00 | 8230.00 | -1.7 |
| A03 | 3481.00 | 2642.50 | 6123.50 | -24.1 |

채점 메서드

```abap
  METHOD q06.
    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q06(
      ( ekgrp = 'A01' q1_value = '6011.00' q2_value = '1475.00' total_value = '7486.00' growth_pct = '-75.5' )
      ( ekgrp = 'A02' q1_value = '4150.00' q2_value = '4080.00' total_value = '8230.00' growth_pct = '-1.7' )
      ( ekgrp = 'A03' q1_value = '3481.00' q2_value = '2642.50' total_value = '6123.50' growth_pct = '-24.1' ) ).
    cl_abap_unit_assert=>assert_equals( act = cut->q06( ) exp = exp msg = 'Q06' ).
  ENDMETHOD.
```

(정의 부분에 `METHODS q06 FOR TESTING.`을 추가하세요.)

<details><summary>정답·해설</summary>

```abap
  METHOD q06.
    DATA(lv_q1_from) = CONV d( '20260101' ).
    DATA(lv_q1_to)   = CONV d( '20260331' ).
    DATA(lv_q2_from) = CONV d( '20260401' ).
    DATA(lv_q2_to)   = CONV d( '20260630' ).

    WITH
      +items AS ( SELECT FROM zsq_ekko_### AS k
                    INNER JOIN zsq_ekpo_### AS p ON p~ebeln = k~ebeln
                    FIELDS k~ekgrp,
                           k~bedat,
                           CAST( p~menge AS DEC( 13, 3 ) ) * CAST( p~netpr AS DEC( 11, 2 ) ) AS net_value
                    WHERE p~loekz = @space ),
      +pivot AS ( SELECT FROM +items
                    FIELDS ekgrp,
                           SUM( CASE WHEN bedat BETWEEN @lv_q1_from AND @lv_q1_to THEN net_value ELSE 0 END ) AS q1_value,
                           SUM( CASE WHEN bedat BETWEEN @lv_q2_from AND @lv_q2_to THEN net_value ELSE 0 END ) AS q2_value,
                           SUM( net_value ) AS total_value
                    GROUP BY ekgrp )
      SELECT FROM +pivot
        FIELDS ekgrp,
               q1_value,
               q2_value,
               total_value,
               DIVISION( ( q2_value - q1_value ) * 100, q1_value, 1 ) AS growth_pct
        ORDER BY ekgrp
        INTO CORRESPONDING FIELDS OF TABLE @result.
  ENDMETHOD.
```

왜 이렇게 쓰나
- ABAP SQL에는 `PIVOT` 문법이 없습니다. "SUM( CASE WHEN 조건 THEN 값 ELSE 0 END )"를 열마다 쓰는 **조건부 집계**가 표준 방법입니다. 쿼리포터·실무 리포트에서 가장 자주 나오는 모양입니다.
- 증감률은 집계가 끝난 값으로 계산해야 하므로 CTE를 한 층 더 둡니다. 같은 SELECT 안에서 별칭(`q1_value`)을 다른 열의 식에 쓸 수는 없습니다.
- `CASE ... THEN net_value ELSE 0 END`처럼 DEC와 정수를 섞으면 결과 타입이 DEC로 맞춰집니다. 활성화에서 타입 오류가 나면 `ELSE CAST( 0 AS DEC( 24, 5 ) )`처럼 맞추세요(실제 시스템에서 확인 필요).

오답이 나오는 전형적인 실수
- `A02`의 `q1_value`가 6050.00 → 삭제 품목(2 × 950.00 = 1900.00)이 들어감. `loekz` 조건 확인.
- `growth_pct` 부호가 반대 → (Q1 − Q2)로 계산.

</details>

#### 10단계. Q07 FOR ALL ENTRIES 함정 잡기 — 중복 제거와 빈 드라이버 테이블

요구사항
1. `q07( it_vendors )`는 공급업체 번호 목록을 받아, 그 공급업체들의 **삭제되지 않은 품목 수와 평균 단가**(소수 4자리)를 공급업체별로 돌려줍니다(품목이 없는 공급업체는 결과에 없음). 정렬: `lifnr`.
2. 이 문항은 일부러 **`FOR ALL ENTRIES IN @it_vendors`를 써서** 품목을 읽게 합니다. 다음 네 개의 채점 테스트를 모두 통과해야 합니다.
   - V100 하나 → 품목 7개, 평균 1.6900
   - V200, V600 → V200 한 행(품목 8개, 평균 25.1175)
   - 같은 V100이 두 번 들어 있음 → 품목 7개(중복 공급업체 때문에 품목이 두 번 세어지면 안 됨)
   - 빈 목록 → 빈 결과(전체 공급업체가 나오면 안 됨)
3. 평균은 ABAP 루프가 아닌 **SQL로**(`SELECT ... FROM @itab`) 구하세요.

채점 메서드 (네 개)

```abap
  METHOD q07_single.
    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q07( ( lifnr = 'V100' item_cnt = 7 avg_netpr = '1.6900' ) ).
    cl_abap_unit_assert=>assert_equals( act = cut->q07( VALUE #( ( 'V100' ) ) ) exp = exp msg = 'Q07 V100' ).
  ENDMETHOD.

  METHOD q07_no_items.
    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q07( ( lifnr = 'V200' item_cnt = 8 avg_netpr = '25.1175' ) ).
    cl_abap_unit_assert=>assert_equals( act = cut->q07( VALUE #( ( 'V200' ) ( 'V600' ) ) ) exp = exp msg = 'Q07 V200+V600' ).
  ENDMETHOD.

  METHOD q07_duplicates.
    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q07( ( lifnr = 'V100' item_cnt = 7 avg_netpr = '1.6900' ) ).
    cl_abap_unit_assert=>assert_equals( act = cut->q07( VALUE #( ( 'V100' ) ( 'V100' ) ) ) exp = exp msg = 'Q07 dup' ).
  ENDMETHOD.

  METHOD q07_empty.
    cl_abap_unit_assert=>assert_initial( act = cut->q07( VALUE #( ) ) msg = 'Q07 empty must return nothing' ).
  ENDMETHOD.
```

(정의 부분에 `METHODS q07_single FOR TESTING.` 등 네 줄을 추가하세요.)

<details><summary>정답·해설</summary>

```abap
  METHOD q07.
    " 함정 1: 빈 드라이버 테이블이면 FOR ALL ENTRIES의 WHERE가 통째로 무시되어 전체를 읽는다
    IF it_vendors IS INITIAL.
      RETURN.
    ENDIF.

    " 함정 2: FOR ALL ENTRIES는 결과에서 '완전히 같은 행'을 지운다
    "        → 품목 키(ebeln, ebelp)를 반드시 SELECT 목록에 넣는다
    SELECT FROM zsq_ekko_### AS k
           INNER JOIN zsq_ekpo_### AS p ON p~ebeln = k~ebeln
      FIELDS k~lifnr, p~ebeln, p~ebelp, p~netpr
      FOR ALL ENTRIES IN @it_vendors
      WHERE k~lifnr = @it_vendors-table_line
        AND p~loekz = @space
      INTO TABLE @DATA(lt_items).

    " 내부 테이블을 데이터 소스로 다시 SQL 집계
    SELECT FROM @lt_items AS i
      FIELDS lifnr,
             COUNT( * )                  AS item_cnt,
             AVG( netpr AS DEC( 15, 4 ) ) AS avg_netpr
      GROUP BY lifnr
      ORDER BY lifnr
      INTO CORRESPONDING FIELDS OF TABLE @result.
  ENDMETHOD.
```

왜 이렇게 쓰나
- **중복 제거 함정**: FOR ALL ENTRIES는 드라이버 행마다 쿼리를 나눠 보낸 뒤 결과를 합치면서 `SELECT DISTINCT`처럼 같은 행을 지웁니다. 키 없이 `lifnr, netpr`만 읽으면 V100의 단가 0.12(두 품목)와 4.50(두 품목)이 하나씩 사라져 품목 5개, 평균 1.4420이 나옵니다. 키를 넣으면 모든 행이 서로 달라 지워지지 않습니다.
- **드라이버 중복**: 같은 V100이 두 번 있어도 결과 행이 같으므로 위 중복 제거 덕분에 두 번 세어지지 않습니다. 같은 일을 JOIN이나 `IN`으로 직접 짜면 중복 드라이버가 품목을 두 배로 만들 수 있으니 주의하세요.
- **빈 테이블 함정**: `it_vendors`가 비면 `WHERE k~lifnr = @it_vendors-table_line` 조건 전체가 무시되어 **모든 공급업체**를 읽습니다. FOR ALL ENTRIES 앞의 `IS INITIAL` 검사는 습관이 아니라 필수입니다.
- FOR ALL ENTRIES와 함께 집계 함수·`ORDER BY`를 쓸 수 없어서(쿼리가 쪼개져 실행되기 때문) 먼저 행을 읽고, `SELECT FROM @lt_items`로 다시 집계했습니다. 내부 테이블 데이터 소스 쿼리는 필요하면 DB로 보내져 실행됩니다(실제 시스템에서 확인 필요).
- 요즘은 FOR ALL ENTRIES 대신 `SELECT ... FROM @it_vendors AS v INNER JOIN ...`(내부 테이블 조인)이나 `WHERE lifnr IN @range`를 더 권장합니다. 그래도 레거시 코드에서 이 두 함정은 여전히 자주 버그가 됩니다.

오답이 나오는 전형적인 실수
- `q07_single`에서 품목 5개 → 키 열 누락.
- `q07_empty`에서 5개 공급업체 결과 → `IS INITIAL` 검사 누락.

</details>

### R-20. 판매 데이터 윈도 함수 챌린지: 순번·누적·이동평균·Top-N·연속 구간 [작성] ★★★★
<!-- covers: 윈도 함수, OVER, PARTITION BY, ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD, SUM OVER, COUNT OVER, ROWS BETWEEN, UNBOUNDED PRECEDING, 누적 합계, 이동 평균, Top-N per group, 동점 처리, 파레토 ABC 분석, gaps and islands, EXTRACT_YEAR, EXTRACT_MONTH, 반품 부호 처리, 다단 CTE -->

**목표**
- 윈도 함수가 **행을 줄이지 않고** 옆 행·그룹 전체 값을 붙인다는 점(집계 함수와의 차이)을 결과 표로 설명할 수 있습니다.
- `PARTITION BY`·`ORDER BY`·프레임(`ROWS BETWEEN …`)을 조합해 순번, 누적 합계, 전월 값, 이동 평균을 만들 수 있습니다.
- 윈도 함수 결과로는 `WHERE`를 걸 수 없으므로 CTE로 한 층 감싸서 거르는 패턴(Top-N, 첫 주문)을 쓸 수 있습니다.
- `ROW_NUMBER`·`RANK`·`DENSE_RANK`의 동점 처리 차이를 알고 요구사항에 맞는 것을 고를 수 있습니다.
- "연속된 달" 같은 구간 찾기(gaps and islands)를 SQL 한 번으로 풀 수 있습니다.

**전제**
- R-19 1~3단계(테이블, 시드 데이터, 채점기)를 끝냈습니다. 문항 번호는 Q08~Q14입니다.
- **반품 규칙**: `auart = 'RE'` 오더의 금액은 음수로 계산합니다. 반품까지 포함한 "순매출"을 쓰는 문항과 일반 오더(`OR`)만 보는 문항이 섞여 있으니 요구사항을 꼼꼼히 읽으세요.
- ABAP SQL 윈도 함수 중 `LAG`/`LEAD`, 프레임 지정(`ROWS BETWEEN`)은 비교적 최근 릴리스에 들어왔습니다. BTP ABAP 환경은 최신 릴리스라 쓸 수 있지만, 온프레미스 구버전에서는 안 될 수 있습니다.
- 여러 문항이 아래 공통 CTE를 씁니다. 오더 한 건의 순금액(반품은 음수)입니다.

```abap
      +so AS ( SELECT FROM zsq_vbak_### AS h
                 INNER JOIN zsq_vbap_### AS i ON i~vbeln = h~vbeln
                 FIELDS h~vbeln, h~kunnr, h~audat, h~auart,
                        SUM( CASE h~auart WHEN 'RE' THEN CAST( i~netwr AS DEC( 15, 2 ) ) * -1
                                          ELSE CAST( i~netwr AS DEC( 15, 2 ) ) END ) AS order_value
                 GROUP BY h~vbeln, h~kunnr, h~audat, h~auart )
```

**만들 객체**

| 순서 | 객체 유형 | 이름 | 역할 |
|---|---|---|---|
| 1 | 기존 클래스 | `ZCL_SQ_QUERIES_###` | `q08`~`q14` 구현 |
| 2 | 기존 테스트 클래스 | `LTC_GRADE` | 채점 메서드 `q08`~`q14` 추가 |

#### 1단계. Q08 고객별 첫 주문과 두 번째 주문 — ROW_NUMBER와 자기 조인

요구사항
1. 일반 오더(`OR`)만 보고, 고객마다 **첫 번째와 두 번째 주문**의 오더 번호·오더일, 그리고 두 주문 사이 일수를 구하세요.
2. 주문 순서는 `audat`, 같은 날이면 `vbeln` 순입니다. 일반 오더가 2건 이상인 고객만 결과에 나옵니다(`C007`은 1건이라 없음).
3. 결과 열: `kunnr`, `first_vbeln`, `first_date`, `second_vbeln`, `second_date`, `days_between`. 정렬: `kunnr`.

기대 결과

| kunnr | first_vbeln | first_date | second_vbeln | second_date | days_between |
|---|---|---|---|---|---|
| C001 | 0010000001 | 20260108 | 0010000004 | 20260205 | 28 |
| C002 | 0010000003 | 20260122 | 0010000016 | 20260521 | 119 |
| C003 | 0010000002 | 20260115 | 0010000007 | 20260304 | 48 |
| C004 | 0010000006 | 20260226 | 0010000013 | 20260428 | 61 |
| C005 | 0010000005 | 20260211 | 0010000011 | 20260409 | 57 |
| C006 | 0010000009 | 20260318 | 0010000015 | 20260514 | 57 |

채점 메서드

```abap
  METHOD q08.
    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q08(
      ( kunnr = 'C001' first_vbeln = '0010000001' first_date = '20260108' second_vbeln = '0010000004' second_date = '20260205' days_between = 28 )
      ( kunnr = 'C002' first_vbeln = '0010000003' first_date = '20260122' second_vbeln = '0010000016' second_date = '20260521' days_between = 119 )
      ( kunnr = 'C003' first_vbeln = '0010000002' first_date = '20260115' second_vbeln = '0010000007' second_date = '20260304' days_between = 48 )
      ( kunnr = 'C004' first_vbeln = '0010000006' first_date = '20260226' second_vbeln = '0010000013' second_date = '20260428' days_between = 61 )
      ( kunnr = 'C005' first_vbeln = '0010000005' first_date = '20260211' second_vbeln = '0010000011' second_date = '20260409' days_between = 57 )
      ( kunnr = 'C006' first_vbeln = '0010000009' first_date = '20260318' second_vbeln = '0010000015' second_date = '20260514' days_between = 57 ) ).
    cl_abap_unit_assert=>assert_equals( act = cut->q08( ) exp = exp msg = 'Q08' ).
  ENDMETHOD.
```

(정의 부분에 `METHODS q08 FOR TESTING.`을 추가하세요.)

<details><summary>정답·해설</summary>

```abap
  METHOD q08.
    WITH
      +seq AS ( SELECT FROM zsq_vbak_###
                  FIELDS kunnr, vbeln, audat,
                         ROW_NUMBER( ) OVER( PARTITION BY kunnr ORDER BY audat, vbeln ) AS rn
                  WHERE auart = 'OR' )
      SELECT FROM +seq AS a
             INNER JOIN +seq AS b
               ON  b~kunnr = a~kunnr
               AND b~rn    = 2
        FIELDS a~kunnr,
               a~vbeln AS first_vbeln,
               a~audat AS first_date,
               b~vbeln AS second_vbeln,
               b~audat AS second_date,
               DATS_DAYS_BETWEEN( a~audat, b~audat ) AS days_between
        WHERE a~rn = 1
        ORDER BY a~kunnr
        INTO CORRESPONDING FIELDS OF TABLE @result.
  ENDMETHOD.
```

왜 이렇게 쓰나
- `ROW_NUMBER( ) OVER( PARTITION BY kunnr ORDER BY audat, vbeln )`는 고객마다 1부터 번호를 다시 매깁니다. 집계와 달리 **행 수가 그대로**입니다.
- 윈도 함수는 `WHERE` 다음에 계산되므로 같은 SELECT의 `WHERE rn = 1`은 쓸 수 없습니다. CTE로 감싼 뒤 바깥에서 거릅니다. 여기서는 같은 CTE를 두 번(`a`, `b`) 써서 1번과 2번 주문을 한 행으로 붙였습니다.
- CTE 안의 `WHERE auart = 'OR'`는 번호를 매기기 **전에** 반품을 지웁니다. 반품을 바깥에서 지우면 반품이 2번 자리를 차지해 `C002`의 두 번째 주문이 반품(`0010000010`)이 됩니다.
- `ORDER BY audat, vbeln`처럼 순서를 **유일하게** 정하세요. 같은 날 주문이 둘이면 `ROW_NUMBER`는 DB 마음대로 번호를 줍니다(비결정적).
- 다른 풀이: `LEAD( vbeln ) OVER( PARTITION BY kunnr ORDER BY audat, vbeln )`로 다음 주문을 옆 열에 붙이고 `rn = 1`만 남겨도 됩니다(자기 조인이 필요 없음).

오답이 나오는 전형적인 실수
- `C002` 두 번째 주문이 `0010000010` → 반품을 번호 매긴 뒤에 지움.
- `C007`이 나옴 → INNER JOIN 대신 LEFT JOIN.

</details>

#### 2단계. Q09 월별 순매출·누적·전월 대비 — SUM OVER와 LAG

요구사항
1. 월(`audat`의 `YYYYMM`)별 **순매출**(반품 차감)을 구하세요.
2. 같은 행에 `cum_value`(1월부터 그 달까지 누적), `prev_value`(전월 순매출, 첫 달은 0), `mom_pct`(전월 대비 증감률 %, 소수 1자리, 첫 달은 0)를 붙입니다.
3. 결과 열: `period`, `net_value`, `cum_value`, `prev_value`, `mom_pct`. 정렬: `period`.

기대 결과

| period | net_value | cum_value | prev_value | mom_pct |
|---|---|---|---|---|
| 202601 | 3440.00 | 3440.00 | 0.00 | 0.0 |
| 202602 | 4510.00 | 7950.00 | 3440.00 | 31.1 |
| 202603 | 3400.00 | 11350.00 | 4510.00 | -24.6 |
| 202604 | 2990.00 | 14340.00 | 3400.00 | -12.1 |
| 202605 | 4680.00 | 19020.00 | 2990.00 | 56.5 |
| 202606 | 3630.00 | 22650.00 | 4680.00 | -22.4 |

채점 메서드

```abap
  METHOD q09.
    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q09(
      ( period = '202601' net_value = '3440.00' cum_value = '3440.00' prev_value = '0.00' mom_pct = '0.0' )
      ( period = '202602' net_value = '4510.00' cum_value = '7950.00' prev_value = '3440.00' mom_pct = '31.1' )
      ( period = '202603' net_value = '3400.00' cum_value = '11350.00' prev_value = '4510.00' mom_pct = '-24.6' )
      ( period = '202604' net_value = '2990.00' cum_value = '14340.00' prev_value = '3400.00' mom_pct = '-12.1' )
      ( period = '202605' net_value = '4680.00' cum_value = '19020.00' prev_value = '2990.00' mom_pct = '56.5' )
      ( period = '202606' net_value = '3630.00' cum_value = '22650.00' prev_value = '4680.00' mom_pct = '-22.4' ) ).
    cl_abap_unit_assert=>assert_equals( act = cut->q09( ) exp = exp msg = 'Q09' ).
  ENDMETHOD.
```

(정의 부분에 `METHODS q09 FOR TESTING.`을 추가하세요.)

<details><summary>정답·해설</summary>

```abap
  METHOD q09.
    WITH
      +so AS ( SELECT FROM zsq_vbak_### AS h
                 INNER JOIN zsq_vbap_### AS i ON i~vbeln = h~vbeln
                 FIELDS h~vbeln, h~kunnr, h~audat, h~auart,
                        SUM( CASE h~auart WHEN 'RE' THEN CAST( i~netwr AS DEC( 15, 2 ) ) * -1
                                          ELSE CAST( i~netwr AS DEC( 15, 2 ) ) END ) AS order_value
                 GROUP BY h~vbeln, h~kunnr, h~audat, h~auart ),
      +m  AS ( SELECT FROM +so
                 FIELDS LEFT( audat, 6 ) AS period,
                        SUM( order_value ) AS net_value
                 GROUP BY LEFT( audat, 6 ) ),
      +w  AS ( SELECT FROM +m
                 FIELDS period,
                        net_value,
                        SUM( net_value ) OVER( ORDER BY period
                                               ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW ) AS cum_value,
                        LAG( net_value ) OVER( ORDER BY period ) AS prev_value )
      SELECT FROM +w
        FIELDS period,
               net_value,
               cum_value,
               prev_value,
               DIVISION( ( net_value - prev_value ) * 100, prev_value, 1 ) AS mom_pct
        ORDER BY period
        INTO CORRESPONDING FIELDS OF TABLE @result.
  ENDMETHOD.
```

왜 이렇게 쓰나
- **3층 CTE**: 오더 금액(`+so`) → 월 합계(`+m`) → 윈도 계산(`+w`) → 비율. 집계 결과 위에 윈도 함수를 쓰려면 집계를 먼저 끝내야 합니다.
- `SUM( … ) OVER( ORDER BY period ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW )`는 처음부터 현재 행까지의 합, 곧 누적입니다. 프레임을 생략해도 기본값이 비슷하게 동작하지만, 기본 프레임은 `RANGE`라서 같은 `period` 값이 여러 행이면 결과가 달라집니다. 누적은 프레임을 명시하는 습관을 들이세요.
- 첫 달의 `LAG`는 NULL입니다. NULL이 들어간 산술·`DIVISION`도 NULL이고, ABAP으로 받으면 0이 됩니다. 그래서 0으로 나누는 오류 없이 "첫 달 0"이 저절로 맞습니다. 다만 이것은 **NULL → 초기값 변환에 기댄 것**이니, 결과를 CDS나 다른 SQL에서 다시 쓸 때는 `COALESCE`로 명시하세요.
- `LEFT( audat, 6 )`로 날짜 앞 6자리를 잘랐습니다. `GROUP BY`에 같은 식을 그대로 쓰는 것이 핵심입니다(별칭 `period`로는 묶을 수 없음).

오답이 나오는 전형적인 실수
- 3월 `net_value`가 3590.00 → 반품 190.00을 빼지 않고 더함.
- `cum_value`가 월 값과 같음 → `OVER( )` 안의 `ORDER BY` 누락(그러면 전체 합이 모든 행에 붙거나 누적이 안 됨).

</details>

#### 3단계. Q10 국가별 매출 Top-2 고객 (동점 포함) — DENSE_RANK와 그룹 합계

요구사항
1. 고객별 순매출(반품 차감)을 구하고, 국가(`kna1.land1`) 안에서 순위를 매겨 **2위까지** 남기세요.
2. **동점은 같은 순위**이고 다음 순위를 건너뛰지 않습니다. 한국(KR)은 `C002`와 `C007`이 2420.00으로 공동 2위라 세 행이 나와야 합니다.
3. `share_pct` = 고객 순매출 × 100 ÷ 그 국가 전체 순매출(2위 밖 고객 포함), 소수 1자리.
4. 결과 열: `land1`, `rank_no`, `kunnr`, `name1`, `net_value`, `share_pct`. 정렬: `land1`, `rank_no`, `kunnr`.

기대 결과

| land1 | rank_no | kunnr | name1 | net_value | share_pct |
|---|---|---|---|---|---|
| DE | 1 | C003 | Berlin Motoren | 4810.00 | 81.0 |
| DE | 2 | C004 | München Anlagen | 1130.00 | 19.0 |
| KR | 1 | C001 | 서울정밀 | 3560.00 | 42.4 |
| KR | 2 | C002 | 부산중공업 | 2420.00 | 28.8 |
| KR | 2 | C007 | Seoul Robotics | 2420.00 | 28.8 |
| US | 1 | C005 | Texas Drives | 4630.00 | 55.7 |
| US | 2 | C006 | Ohio Robotics | 3680.00 | 44.3 |

채점 메서드

```abap
  METHOD q10.
    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q10(
      ( land1 = 'DE' rank_no = 1 kunnr = 'C003' name1 = 'Berlin Motoren' net_value = '4810.00' share_pct = '81.0' )
      ( land1 = 'DE' rank_no = 2 kunnr = 'C004' name1 = 'München Anlagen' net_value = '1130.00' share_pct = '19.0' )
      ( land1 = 'KR' rank_no = 1 kunnr = 'C001' name1 = '서울정밀' net_value = '3560.00' share_pct = '42.4' )
      ( land1 = 'KR' rank_no = 2 kunnr = 'C002' name1 = '부산중공업' net_value = '2420.00' share_pct = '28.8' )
      ( land1 = 'KR' rank_no = 2 kunnr = 'C007' name1 = 'Seoul Robotics' net_value = '2420.00' share_pct = '28.8' )
      ( land1 = 'US' rank_no = 1 kunnr = 'C005' name1 = 'Texas Drives' net_value = '4630.00' share_pct = '55.7' )
      ( land1 = 'US' rank_no = 2 kunnr = 'C006' name1 = 'Ohio Robotics' net_value = '3680.00' share_pct = '44.3' ) ).
    cl_abap_unit_assert=>assert_equals( act = cut->q10( ) exp = exp msg = 'Q10' ).
  ENDMETHOD.
```

(정의 부분에 `METHODS q10 FOR TESTING.`을 추가하세요.)

<details><summary>정답·해설</summary>

```abap
  METHOD q10.
    WITH
      +so   AS ( SELECT FROM zsq_vbak_### AS h
                   INNER JOIN zsq_vbap_### AS i ON i~vbeln = h~vbeln
                   FIELDS h~vbeln, h~kunnr, h~audat, h~auart,
                          SUM( CASE h~auart WHEN 'RE' THEN CAST( i~netwr AS DEC( 15, 2 ) ) * -1
                                            ELSE CAST( i~netwr AS DEC( 15, 2 ) ) END ) AS order_value
                   GROUP BY h~vbeln, h~kunnr, h~audat, h~auart ),
      +cust AS ( SELECT FROM +so AS o
                   INNER JOIN zsq_kna1_### AS c ON c~kunnr = o~kunnr
                   FIELDS c~land1, o~kunnr, c~name1,
                          SUM( o~order_value ) AS net_value
                   GROUP BY c~land1, o~kunnr, c~name1 ),
      +rk   AS ( SELECT FROM +cust
                   FIELDS land1, kunnr, name1, net_value,
                          DENSE_RANK( ) OVER( PARTITION BY land1 ORDER BY net_value DESCENDING ) AS rank_no,
                          SUM( net_value ) OVER( PARTITION BY land1 ) AS country_total )
      SELECT FROM +rk
        FIELDS land1, rank_no, kunnr, name1, net_value,
               DIVISION( net_value * 100, country_total, 1 ) AS share_pct
        WHERE rank_no <= 2
        ORDER BY land1, rank_no, kunnr
        INTO CORRESPONDING FIELDS OF TABLE @result.
  ENDMETHOD.
```

왜 이렇게 쓰나
- 세 순위 함수의 차이(KR 예):

| kunnr | net | ROW_NUMBER | RANK | DENSE_RANK |
|---|---|---|---|---|
| C001 | 3560 | 1 | 1 | 1 |
| C002 | 2420 | 2 | 2 | 2 |
| C007 | 2420 | 3 (또는 2) | 2 | 2 |
| (가상) C008 | 1000 | 4 | **4** | **3** |

  "동점은 같은 순위, 다음 순위를 건너뛰지 않음"은 `DENSE_RANK`입니다. `ROW_NUMBER`는 동점에도 다른 번호를 주고 어느 쪽이 2가 될지 정해지지 않으므로 Top-N 문제에서 결과가 매번 바뀔 수 있습니다.
- `SUM( net_value ) OVER( PARTITION BY land1 )`는 `ORDER BY` 없는 윈도라 **그 국가 전체 합계**가 모든 행에 붙습니다. 비중을 구하려고 별도 집계 쿼리를 조인할 필요가 없습니다. 이 합계는 `WHERE rank_no <= 2`로 거르기 **전**에 계산되므로 2위 밖 고객도 분모에 들어갑니다.

오답이 나오는 전형적인 실수
- KR이 두 행 → `ROW_NUMBER`.
- `share_pct` 합이 국가마다 100 → 분모를 2위 안 고객만으로 계산(거른 뒤 합계).
- `C002` 금액이 2610.00 → 반품 미차감.

</details>

#### 4단계. Q11 고객 재주문 간격 — LAG로 이전 행과 비교한 뒤 집계

요구사항
1. 일반 오더(`OR`)만 보고, 고객마다 **바로 이전 주문과의 간격(일)**을 구한 뒤 고객 단위로 집계하세요.
2. 결과 열: `kunnr`, `order_cnt`(일반 오더 수), `avg_gap_days`(간격 평균, 소수 1자리), `max_gap_days`. 주문이 2건 이상인 고객만.
3. 정렬: `avg_gap_days` 내림차순, 같으면 `kunnr`.

기대 결과

| kunnr | order_cnt | avg_gap_days | max_gap_days |
|---|---|---|---|
| C002 | 2 | 119.0 | 119 |
| C005 | 3 | 63.5 | 70 |
| C004 | 2 | 61.0 | 61 |
| C006 | 2 | 57.0 | 57 |
| C003 | 4 | 49.0 | 56 |
| C001 | 4 | 39.7 | 56 |

채점 메서드

```abap
  METHOD q11.
    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q11(
      ( kunnr = 'C002' order_cnt = 2 avg_gap_days = '119.0' max_gap_days = 119 )
      ( kunnr = 'C005' order_cnt = 3 avg_gap_days = '63.5' max_gap_days = 70 )
      ( kunnr = 'C004' order_cnt = 2 avg_gap_days = '61.0' max_gap_days = 61 )
      ( kunnr = 'C006' order_cnt = 2 avg_gap_days = '57.0' max_gap_days = 57 )
      ( kunnr = 'C003' order_cnt = 4 avg_gap_days = '49.0' max_gap_days = 56 )
      ( kunnr = 'C001' order_cnt = 4 avg_gap_days = '39.7' max_gap_days = 56 ) ).
    cl_abap_unit_assert=>assert_equals( act = cut->q11( ) exp = exp msg = 'Q11' ).
  ENDMETHOD.
```

(정의 부분에 `METHODS q11 FOR TESTING.`을 추가하세요.)

<details><summary>정답·해설</summary>

```abap
  METHOD q11.
    WITH
      +gap AS ( SELECT FROM zsq_vbak_###
                  FIELDS kunnr,
                         audat,
                         LAG( audat ) OVER( PARTITION BY kunnr ORDER BY audat, vbeln ) AS prev_date
                  WHERE auart = 'OR' ),
      +d   AS ( SELECT FROM +gap
                  FIELDS kunnr,
                         CASE WHEN prev_date IS NULL THEN NULL
                              ELSE DATS_DAYS_BETWEEN( prev_date, audat ) END AS gap_days )
      SELECT FROM +d
        FIELDS kunnr,
               COUNT( * )                                        AS order_cnt,
               DIVISION( SUM( gap_days ), COUNT( gap_days ), 1 ) AS avg_gap_days,
               MAX( gap_days )                                   AS max_gap_days
        GROUP BY kunnr
        HAVING COUNT( * ) >= 2
        ORDER BY avg_gap_days DESCENDING, kunnr
        INTO CORRESPONDING FIELDS OF TABLE @result.
  ENDMETHOD.
```

왜 이렇게 쓰나
- 고객의 첫 주문에는 이전 주문이 없어 `prev_date`가 NULL입니다. 간격도 NULL로 두면 `SUM`·`MAX`·`COUNT( gap_days )`가 그 행을 **자동으로 건너뜁니다**. 그래서 평균의 분모가 "주문 수 − 1"이 됩니다.
- `COUNT( * )`(주문 수)와 `COUNT( gap_days )`(간격 수)의 차이를 한 쿼리에서 같이 쓰는 것이 이 문항의 핵심입니다.
- `CASE … THEN NULL`이 문법상 막히면(실제 시스템에서 확인 필요) `DATS_DAYS_BETWEEN( prev_date, audat )`를 바로 쓰세요. NULL이 들어간 함수 결과도 NULL입니다.
- `AVG( gap_days AS DEC( 10, 1 ) )`로도 구할 수 있지만, AVG 결과를 소수 1자리 타입으로 바꿀 때 반올림인지 버림인지가 명확하지 않아 `DIVISION`(반올림)을 썼습니다. `C001`은 119 ÷ 3 = 39.666…이라 반올림이면 39.7, 버림이면 39.6입니다.

오답이 나오는 전형적인 실수
- `C001` 평균이 29.8 → 분모를 주문 수 4로 나눔(첫 주문의 NULL 간격을 0으로 셈).
- `C002` 간격이 62 → 반품(3/25)을 포함함.

</details>

#### 5단계. Q12 자재 ABC 분석(파레토) — 누적 비중과 등급

요구사항
1. 자재별 순매출(반품 차감)을 구해 **큰 순서**로 줄 세우고, 비중(`share_pct`)과 누적 비중(`cum_pct`)을 소수 2자리로 붙이세요.
2. 등급: 누적 비중이 70% 이하이면 `A`, 90% 이하이면 `B`, 나머지는 `C`. 등급 판단은 **반올림하기 전 값**으로 합니다.
3. 결과 열: `matnr`, `net_value`, `share_pct`, `cum_pct`, `abc_class`. 정렬: `net_value` 내림차순, 같으면 `matnr`.

기대 결과

| matnr | net_value | share_pct | cum_pct | abc_class |
|---|---|---|---|---|
| M07 | 12550.00 | 55.41 | 55.41 | A |
| M04 | 4020.00 | 17.75 | 73.16 | B |
| M03 | 2300.00 | 10.15 | 83.31 | B |
| M05 | 1580.00 | 6.98 | 90.29 | C |
| M01 | 1460.00 | 6.45 | 96.73 | C |
| M06 | 740.00 | 3.27 | 100.00 | C |

채점 메서드

```abap
  METHOD q12.
    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q12(
      ( matnr = 'M07' net_value = '12550.00' share_pct = '55.41' cum_pct = '55.41' abc_class = 'A' )
      ( matnr = 'M04' net_value = '4020.00' share_pct = '17.75' cum_pct = '73.16' abc_class = 'B' )
      ( matnr = 'M03' net_value = '2300.00' share_pct = '10.15' cum_pct = '83.31' abc_class = 'B' )
      ( matnr = 'M05' net_value = '1580.00' share_pct = '6.98' cum_pct = '90.29' abc_class = 'C' )
      ( matnr = 'M01' net_value = '1460.00' share_pct = '6.45' cum_pct = '96.73' abc_class = 'C' )
      ( matnr = 'M06' net_value = '740.00' share_pct = '3.27' cum_pct = '100.00' abc_class = 'C' ) ).
    cl_abap_unit_assert=>assert_equals( act = cut->q12( ) exp = exp msg = 'Q12' ).
  ENDMETHOD.
```

(정의 부분에 `METHODS q12 FOR TESTING.`을 추가하세요.)

<details><summary>정답·해설</summary>

```abap
  METHOD q12.
    WITH
      +mat AS ( SELECT FROM zsq_vbak_### AS h
                  INNER JOIN zsq_vbap_### AS i ON i~vbeln = h~vbeln
                  FIELDS i~matnr,
                         SUM( CASE h~auart WHEN 'RE' THEN CAST( i~netwr AS DEC( 15, 2 ) ) * -1
                                           ELSE CAST( i~netwr AS DEC( 15, 2 ) ) END ) AS net_value
                  GROUP BY i~matnr ),
      +cum AS ( SELECT FROM +mat
                  FIELDS matnr,
                         net_value,
                         SUM( net_value ) OVER( ) AS total_value,
                         SUM( net_value ) OVER( ORDER BY net_value DESCENDING, matnr
                                                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW ) AS cum_value )
      SELECT FROM +cum
        FIELDS matnr,
               net_value,
               DIVISION( net_value * 100, total_value, 2 ) AS share_pct,
               DIVISION( cum_value * 100, total_value, 2 ) AS cum_pct,
               CASE WHEN cum_value * 100 <= total_value * 70 THEN 'A'
                    WHEN cum_value * 100 <= total_value * 90 THEN 'B'
                    ELSE 'C' END                             AS abc_class
        ORDER BY net_value DESCENDING, matnr
        INTO CORRESPONDING FIELDS OF TABLE @result.
  ENDMETHOD.
```

왜 이렇게 쓰나
- `OVER( )`(빈 괄호)는 결과 전체가 하나의 윈도입니다. 총합을 모든 행에 붙일 때 씁니다.
- 누적 합계의 `ORDER BY`에 `matnr`까지 넣어 **순서를 유일하게** 만들었습니다. 금액이 같은 자재가 있으면 누적값이 어느 쪽을 먼저 더하느냐에 따라 달라지기 때문입니다.
- 등급 판단을 `DIVISION` 결과(반올림된 %)로 하면 69.996%가 70.00이 되어 등급이 바뀔 수 있습니다. 그래서 곱셈으로 바꿔 **정확한 값끼리 비교**했습니다(`cum × 100 <= total × 70`). 나눗셈을 비교에서 없애는 것은 금액 비교의 기본 기술입니다.
- `M04`는 누적 73.16%로 70%를 넘었으므로 B입니다. "70%를 처음 넘기는 자재까지 A"로 정의하는 회사도 있는데, 그러면 `LAG( cum_value )`(이전 누적)로 판단해야 합니다. 요구사항의 정의를 먼저 확인하세요.

오답이 나오는 전형적인 실수
- `M04` 순매출이 4210.00 → 반품 미차감.
- `cum_pct`가 모두 100.00 → `OVER( ORDER BY … )` 대신 `OVER( )`를 누적에도 씀.

</details>

#### 6단계. Q13 연속 주문 월 구간 찾기 (gaps and islands)

요구사항
1. 일반 오더(`OR`)만 보고, 고객별로 주문이 있었던 달을 모은 뒤 **연속된 달끼리 한 구간**으로 묶으세요. 예: `C001`은 1·2·3월, 5월에 주문 → 202601~202603(3개월), 202605~202605(1개월) 두 구간.
2. 결과 열: `kunnr`, `start_period`, `end_period`, `months`. 정렬: `kunnr`, `start_period`.
3. 한 달에 주문이 여러 건이어도 그 달은 한 번만 셉니다. 연도가 바뀌는 경우(12월 → 1월)도 연속으로 처리할 수 있는 방식이어야 합니다.

기대 결과

| kunnr | start_period | end_period | months |
|---|---|---|---|
| C001 | 202601 | 202603 | 3 |
| C001 | 202605 | 202605 | 1 |
| C002 | 202601 | 202601 | 1 |
| C002 | 202605 | 202605 | 1 |
| C003 | 202601 | 202601 | 1 |
| C003 | 202603 | 202604 | 2 |
| C003 | 202606 | 202606 | 1 |
| C004 | 202602 | 202602 | 1 |
| C004 | 202604 | 202604 | 1 |
| C005 | 202602 | 202602 | 1 |
| C005 | 202604 | 202604 | 1 |
| C005 | 202606 | 202606 | 1 |
| C006 | 202603 | 202603 | 1 |
| C006 | 202605 | 202605 | 1 |
| C007 | 202606 | 202606 | 1 |

채점 메서드

```abap
  METHOD q13.
    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q13(
      ( kunnr = 'C001' start_period = '202601' end_period = '202603' months = 3 )
      ( kunnr = 'C001' start_period = '202605' end_period = '202605' months = 1 )
      ( kunnr = 'C002' start_period = '202601' end_period = '202601' months = 1 )
      ( kunnr = 'C002' start_period = '202605' end_period = '202605' months = 1 )
      ( kunnr = 'C003' start_period = '202601' end_period = '202601' months = 1 )
      ( kunnr = 'C003' start_period = '202603' end_period = '202604' months = 2 )
      ( kunnr = 'C003' start_period = '202606' end_period = '202606' months = 1 )
      ( kunnr = 'C004' start_period = '202602' end_period = '202602' months = 1 )
      ( kunnr = 'C004' start_period = '202604' end_period = '202604' months = 1 )
      ( kunnr = 'C005' start_period = '202602' end_period = '202602' months = 1 )
      ( kunnr = 'C005' start_period = '202604' end_period = '202604' months = 1 )
      ( kunnr = 'C005' start_period = '202606' end_period = '202606' months = 1 )
      ( kunnr = 'C006' start_period = '202603' end_period = '202603' months = 1 )
      ( kunnr = 'C006' start_period = '202605' end_period = '202605' months = 1 )
      ( kunnr = 'C007' start_period = '202606' end_period = '202606' months = 1 ) ).
    cl_abap_unit_assert=>assert_equals( act = cut->q13( ) exp = exp msg = 'Q13' ).
  ENDMETHOD.
```

(정의 부분에 `METHODS q13 FOR TESTING.`을 추가하세요.)

<details><summary>정답·해설</summary>

```abap
  METHOD q13.
    WITH
      +mon AS ( SELECT FROM zsq_vbak_###
                  FIELDS DISTINCT
                         kunnr,
                         LEFT( audat, 6 ) AS period,
                         EXTRACT_YEAR( audat ) * 12 + EXTRACT_MONTH( audat ) AS month_no
                  WHERE auart = 'OR' ),
      +rn  AS ( SELECT FROM +mon
                  FIELDS kunnr, period, month_no,
                         ROW_NUMBER( ) OVER( PARTITION BY kunnr ORDER BY month_no ) AS rn ),
      +isl AS ( SELECT FROM +rn
                  FIELDS kunnr, period,
                         month_no - rn AS island_key )
      SELECT FROM +isl
        FIELDS kunnr,
               MIN( period ) AS start_period,
               MAX( period ) AS end_period,
               COUNT( * )    AS months
        GROUP BY kunnr, island_key
        ORDER BY kunnr, start_period
        INTO CORRESPONDING FIELDS OF TABLE @result.
  ENDMETHOD.
```

왜 이렇게 쓰나
- **핵심 아이디어**: 연속된 달의 "달 번호"와 "순번"은 둘 다 1씩 커지므로 그 차이가 일정합니다. 끊기면 차이가 바뀝니다.

| kunnr | period | month_no | rn | month_no − rn |
|---|---|---|---|---|
| C001 | 202601 | 24313 | 1 | 24312 |
| C001 | 202602 | 24314 | 2 | 24312 |
| C001 | 202603 | 24315 | 3 | 24312 |
| C001 | 202605 | 24317 | 4 | **24313** |

  차이가 같은 행끼리 `GROUP BY`하면 구간이 됩니다.
- 달 번호를 `연도 × 12 + 월`로 만들어야 12월(2025×12+12 = 24312)과 다음 해 1월(2026×12+1 = 24313)이 연속이 됩니다. `period` 문자열(`202512` → `202601`)을 숫자로 바꿔 빼면 89가 차이 나서 끊긴 것으로 보입니다.
- `EXTRACT_YEAR`/`EXTRACT_MONTH`는 ABAP SQL 날짜 함수입니다(정수 반환). 시스템에서 지원하지 않으면 `CAST( LEFT( audat, 4 ) AS NUMC( 4 ) )`를 거쳐 `INT4`로 바꾸는 방법을 시도하세요(실제 시스템에서 확인 필요).
- 같은 달 주문이 여러 건이면 `rn`이 같은 달에 여러 번 올라가 섬이 깨집니다. 그래서 처음에 `DISTINCT`로 고객·달을 한 행으로 줄였습니다(`FIELDS DISTINCT`).
- 윈도 함수 결과(`rn`)를 산술에 쓰는 것은 한 층 더 감싼 CTE(`+isl`)에서 했습니다. 같은 SELECT 안에서 `month_no - ROW_NUMBER( ) OVER(…)`를 쓰는 것은 막힐 수 있습니다(실제 시스템에서 확인 필요).

오답이 나오는 전형적인 실수
- `C003`의 3·4월이 두 구간 → `DISTINCT` 누락이 아니라면, `PARTITION BY kunnr` 누락으로 전체 고객에 번호를 매김.
- `C002`의 3월이 나옴 → 반품 오더 포함.

</details>

#### 7단계. Q14 3개월 이동 합계·이동 평균 — 프레임 지정

요구사항
1. Q09의 월별 순매출에 **현재 달 포함 최근 3개월** 이동 합계(`mov_sum3`), 그 창에 들어간 달 수(`mov_cnt`), 이동 평균(`mov_avg3` = 합계 ÷ 달 수, 소수 2자리)을 붙이세요.
2. 1월은 1개월, 2월은 2개월만 있으므로 그 개수로 나눕니다.
3. 결과 열: `period`, `net_value`, `mov_sum3`, `mov_cnt`, `mov_avg3`. 정렬: `period`.

기대 결과

| period | net_value | mov_sum3 | mov_cnt | mov_avg3 |
|---|---|---|---|---|
| 202601 | 3440.00 | 3440.00 | 1 | 3440.00 |
| 202602 | 4510.00 | 7950.00 | 2 | 3975.00 |
| 202603 | 3400.00 | 11350.00 | 3 | 3783.33 |
| 202604 | 2990.00 | 10900.00 | 3 | 3633.33 |
| 202605 | 4680.00 | 11070.00 | 3 | 3690.00 |
| 202606 | 3630.00 | 11300.00 | 3 | 3766.67 |

채점 메서드

```abap
  METHOD q14.
    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q14(
      ( period = '202601' net_value = '3440.00' mov_sum3 = '3440.00' mov_cnt = 1 mov_avg3 = '3440.00' )
      ( period = '202602' net_value = '4510.00' mov_sum3 = '7950.00' mov_cnt = 2 mov_avg3 = '3975.00' )
      ( period = '202603' net_value = '3400.00' mov_sum3 = '11350.00' mov_cnt = 3 mov_avg3 = '3783.33' )
      ( period = '202604' net_value = '2990.00' mov_sum3 = '10900.00' mov_cnt = 3 mov_avg3 = '3633.33' )
      ( period = '202605' net_value = '4680.00' mov_sum3 = '11070.00' mov_cnt = 3 mov_avg3 = '3690.00' )
      ( period = '202606' net_value = '3630.00' mov_sum3 = '11300.00' mov_cnt = 3 mov_avg3 = '3766.67' ) ).
    cl_abap_unit_assert=>assert_equals( act = cut->q14( ) exp = exp msg = 'Q14' ).
  ENDMETHOD.
```

(정의 부분에 `METHODS q14 FOR TESTING.`을 추가하세요.)

<details><summary>정답·해설</summary>

```abap
  METHOD q14.
    WITH
      +so AS ( SELECT FROM zsq_vbak_### AS h
                 INNER JOIN zsq_vbap_### AS i ON i~vbeln = h~vbeln
                 FIELDS h~vbeln, h~audat,
                        SUM( CASE h~auart WHEN 'RE' THEN CAST( i~netwr AS DEC( 15, 2 ) ) * -1
                                          ELSE CAST( i~netwr AS DEC( 15, 2 ) ) END ) AS order_value
                 GROUP BY h~vbeln, h~audat ),
      +m  AS ( SELECT FROM +so
                 FIELDS LEFT( audat, 6 ) AS period, SUM( order_value ) AS net_value
                 GROUP BY LEFT( audat, 6 ) ),
      +mv AS ( SELECT FROM +m
                 FIELDS period,
                        net_value,
                        SUM( net_value ) OVER( ORDER BY period ROWS BETWEEN 2 PRECEDING AND CURRENT ROW ) AS mov_sum3,
                        COUNT( * )       OVER( ORDER BY period ROWS BETWEEN 2 PRECEDING AND CURRENT ROW ) AS mov_cnt )
      SELECT FROM +mv
        FIELDS period, net_value, mov_sum3, mov_cnt,
               DIVISION( mov_sum3, mov_cnt, 2 ) AS mov_avg3
        ORDER BY period
        INTO CORRESPONDING FIELDS OF TABLE @result.
  ENDMETHOD.
```

왜 이렇게 쓰나
- `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW`는 "앞 두 행 + 현재 행"입니다. **행** 기준이라, 주문이 없는 달이 있으면(행이 빠지면) 3개월이 아니라 "3개 행"이 됩니다. 이 데이터는 6개월 모두 주문이 있어 문제없지만, 실무에서는 달력 CTE를 먼저 LEFT JOIN해 빈 달을 0으로 채운 뒤 이동 평균을 냅니다.
- `AVG( … ) OVER( … )`로 바로 평균을 내도 되지만, 결과 자릿수와 반올림을 통제하려고 합계와 개수를 따로 구해 `DIVISION`으로 나눴습니다. 3783.333… → 3783.33, 3766.666… → 3766.67.

오답이 나오는 전형적인 실수
- 1월 `mov_avg3`가 1146.67 → 앞 행이 없는데 3으로 나눔.
- 4월 `mov_sum3`가 14340.00 → `UNBOUNDED PRECEDING`(누적)으로 씀.

</details>

### R-21. 회계 데이터 SQL 챌린지: 차대 검증·소계·연령 분석·반제·대사·중복 탐지 [작성] ★★★★
<!-- covers: 차변/대변 부호 처리, HAVING으로 불균형 찾기, GROUPING SETS, GROUPING 함수, 소계·총계 행, 미결 항목 연령 분석(aging), 기준일 시점 미결 판단, 자기 조인(self join), 반제 전표 매칭, 대사(reconciliation), UNION ALL, NOT EXISTS, CAST로 UNION 열 맞추기, 중복 송장 탐지, ABS -->

**목표**
- 차변(`S`)/대변(`H`) 표시로 금액 부호를 바꿔 합계를 내고, 전표가 균형인지 SQL로 검증할 수 있습니다.
- `GROUPING SETS`로 상세·소계·총계를 한 번에 만들고, `GROUPING( )`으로 어떤 행이 소계인지 구분할 수 있습니다.
- "기준일 시점"으로 미결 여부를 판단하는(나중에 반제된 것은 그 시점엔 미결) 연령 분석을 쓸 수 있습니다.
- 같은 테이블을 두 번 조인해 전표끼리 짝을 맞추고(반제, 중복), 서로 다른 출처를 대사해 **세 종류의 불일치**를 한 결과로 낼 수 있습니다.

**전제**
- R-19 1~3단계를 끝냈습니다. 문항 번호는 Q15~Q20입니다.
- 회사 코드는 `1000`, 회계 연도는 `2026` 하나뿐입니다. 그래도 정답 SQL은 전표 키 세 개(`bukrs`, `belnr`, `gjahr`)로 조인하세요. 실무 데이터에서는 연도가 다르면 같은 번호가 다시 나옵니다.
- 금액 부호: 차변 `S`는 +, 대변 `H`는 −.
- 전표 유형: `DR` 고객 송장(차변 고객 120000 / 대변 매출 400000), `DZ` 입금(차변 은행 113100 / 대변 고객), `KR` 공급업체 송장(차변 비용 500000 / 대변 공급업체), `SA` 일반 전표.

**만들 객체**

| 순서 | 객체 유형 | 이름 | 역할 |
|---|---|---|---|
| 1 | 기존 클래스 | `ZCL_SQ_QUERIES_###` | `q15`~`q20` 구현 |
| 2 | 기존 테스트 클래스 | `LTC_GRADE` | 채점 메서드 `q15`~`q20`, `q17_feb` 추가 |

#### 1단계. Q15 차대가 맞지 않는 전표 찾기

요구사항
1. 전표마다 차변 합계(`debit`), 대변 합계(`credit`), 차이(`diff` = 차변 − 대변)를 구하고 **차이가 0이 아닌 전표만** 돌려주세요.
2. 결과 열: `belnr`, `blart`, `debit`, `credit`, `diff`. 정렬: `belnr`.

기대 결과

| belnr | blart | debit | credit | diff |
|---|---|---|---|---|
| 0100000005 | DR | 3040.00 | 3000.00 | 40.00 |
| 1500000001 | SA | 250.00 | 200.00 | 50.00 |

채점 메서드

```abap
  METHOD q15.
    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q15(
      ( belnr = '0100000005' blart = 'DR' debit = '3040.00' credit = '3000.00' diff = '40.00' )
      ( belnr = '1500000001' blart = 'SA' debit = '250.00' credit = '200.00' diff = '50.00' ) ).
    cl_abap_unit_assert=>assert_equals( act = cut->q15( ) exp = exp msg = 'Q15' ).
  ENDMETHOD.
```

(정의 부분에 `METHODS q15 FOR TESTING.`을 추가하세요.)

<details><summary>정답·해설</summary>

```abap
  METHOD q15.
    WITH
      +l AS ( SELECT FROM zsq_bseg_### AS s
                INNER JOIN zsq_bkpf_### AS h
                  ON  h~bukrs = s~bukrs
                  AND h~belnr = s~belnr
                  AND h~gjahr = s~gjahr
                FIELDS s~bukrs, s~belnr, s~gjahr, h~blart,
                       CASE s~shkzg WHEN 'S' THEN CAST( s~dmbtr AS DEC( 15, 2 ) ) ELSE 0 END AS debit_amt,
                       CASE s~shkzg WHEN 'H' THEN CAST( s~dmbtr AS DEC( 15, 2 ) ) ELSE 0 END AS credit_amt )
      SELECT FROM +l
        FIELDS belnr, blart,
               SUM( debit_amt )                    AS debit,
               SUM( credit_amt )                   AS credit,
               SUM( debit_amt ) - SUM( credit_amt ) AS diff
        GROUP BY bukrs, belnr, gjahr, blart
        HAVING SUM( debit_amt ) <> SUM( credit_amt )
        ORDER BY belnr
        INTO CORRESPONDING FIELDS OF TABLE @result.
  ENDMETHOD.
```

왜 이렇게 쓰나
- 라인 단위로 차변·대변 금액 열을 먼저 나누고(CASE), 전표 단위로 합칩니다. 실제 회계 시스템은 이런 전표의 전기를 막지만, 인터페이스로 들어온 데이터나 마이그레이션 데이터 검증에 이 쿼리를 그대로 씁니다.
- `HAVING`에 별칭(`debit`)은 쓸 수 없어 집계 식을 다시 씁니다.

오답이 나오는 전형적인 실수
- 모든 전표가 나옴 → 부호 없이 `SUM( dmbtr )`만 보고 0과 비교.
- `0100000005`가 없음 → `blart = 'SA'`처럼 유형으로 미리 거름. 불균형은 어떤 유형에서도 생길 수 있습니다.

</details>

#### 2단계. Q16 총계정별·월별 잔액과 소계·총계 — GROUPING SETS

요구사항
1. 총계정 라인(`koart = 'S'`)만 보고, 부호를 붙인 금액(`S` +, `H` −)을 **계정·월별**로 합하세요.
2. 같은 결과 안에 **계정별 소계**(월 없음)와 **전체 총계**(계정·월 없음)도 넣습니다.
3. `row_level`: 상세 0, 계정 소계 1, 총계 2. 소계·총계 행의 빈 열은 공백(초기값)입니다.
4. 정렬: `row_level`, `hkont`, `period`.
5. SELECT **한 번**으로 만드세요(UNION 세 번 금지).

기대 결과

| row_level | hkont | period | amount |
|---|---|---|---|
| 0 | 113100 | 202602 | 520.00 |
| 0 | 113100 | 202603 | 1270.00 |
| 0 | 113100 | 202604 | 1300.00 |
| 0 | 400000 | 202601 | -3440.00 |
| 0 | 400000 | 202602 | -3900.00 |
| 0 | 400000 | 202603 | -2810.00 |
| 0 | 400000 | 202604 | -2380.00 |
| 0 | 400000 | 202605 | -940.00 |
| 0 | 400000 | 202606 | -400.00 |
| 0 | 500000 | 202603 | 3160.00 |
| 0 | 500000 | 202604 | 1360.00 |
| 0 | 600000 | 202603 | 250.00 |
| 1 | 113100 | (빈 값) | 3090.00 |
| 1 | 400000 | (빈 값) | -13870.00 |
| 1 | 500000 | (빈 값) | 4520.00 |
| 1 | 600000 | (빈 값) | 250.00 |
| 2 | (빈 값) | (빈 값) | -6010.00 |

채점 메서드

```abap
  METHOD q16.
    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q16(
      ( row_level = 0 hkont = '113100' period = '202602' amount = '520.00' )
      ( row_level = 0 hkont = '113100' period = '202603' amount = '1270.00' )
      ( row_level = 0 hkont = '113100' period = '202604' amount = '1300.00' )
      ( row_level = 0 hkont = '400000' period = '202601' amount = '-3440.00' )
      ( row_level = 0 hkont = '400000' period = '202602' amount = '-3900.00' )
      ( row_level = 0 hkont = '400000' period = '202603' amount = '-2810.00' )
      ( row_level = 0 hkont = '400000' period = '202604' amount = '-2380.00' )
      ( row_level = 0 hkont = '400000' period = '202605' amount = '-940.00' )
      ( row_level = 0 hkont = '400000' period = '202606' amount = '-400.00' )
      ( row_level = 0 hkont = '500000' period = '202603' amount = '3160.00' )
      ( row_level = 0 hkont = '500000' period = '202604' amount = '1360.00' )
      ( row_level = 0 hkont = '600000' period = '202603' amount = '250.00' )
      ( row_level = 1 hkont = '113100' amount = '3090.00' )
      ( row_level = 1 hkont = '400000' amount = '-13870.00' )
      ( row_level = 1 hkont = '500000' amount = '4520.00' )
      ( row_level = 1 hkont = '600000' amount = '250.00' )
      ( row_level = 2 amount = '-6010.00' ) ).
    cl_abap_unit_assert=>assert_equals( act = cut->q16( ) exp = exp msg = 'Q16' ).
  ENDMETHOD.
```

(정의 부분에 `METHODS q16 FOR TESTING.`을 추가하세요.)

<details><summary>정답·해설</summary>

```abap
  METHOD q16.
    WITH
      +gl AS ( SELECT FROM zsq_bseg_### AS s
                 INNER JOIN zsq_bkpf_### AS h
                   ON  h~bukrs = s~bukrs
                   AND h~belnr = s~belnr
                   AND h~gjahr = s~gjahr
                 FIELDS s~hkont,
                        LEFT( h~budat, 6 ) AS period,
                        CASE s~shkzg WHEN 'S' THEN CAST( s~dmbtr AS DEC( 15, 2 ) )
                                     ELSE CAST( s~dmbtr AS DEC( 15, 2 ) ) * -1 END AS amount
                 WHERE s~koart = 'S' )
      SELECT FROM +gl
        FIELDS CASE WHEN GROUPING( hkont )  = 1 THEN 2
                    WHEN GROUPING( period ) = 1 THEN 1
                    ELSE 0 END      AS row_level,
               hkont,
               period,
               SUM( amount )        AS amount
        GROUP BY GROUPING SETS ( ( hkont, period ), ( hkont ), ( ) )
        ORDER BY row_level, hkont, period
        INTO CORRESPONDING FIELDS OF TABLE @result.
  ENDMETHOD.
```

왜 이렇게 쓰나
- `GROUPING SETS ( ( hkont, period ), ( hkont ), ( ) )`는 세 가지 `GROUP BY`를 한 번에 실행해 결과를 이어 붙인 것과 같습니다. `( )`는 "아무것으로도 묶지 않음", 곧 총계입니다.
- 소계·총계 행에서 묶이지 않은 열은 **NULL**입니다. 그런데 실제 값이 NULL인 행과 구별이 안 되므로 `GROUPING( 열 )`(그 열이 이번 집합에서 빠졌으면 1)로 행 종류를 판별합니다.
- 정렬 키로 `row_level`을 먼저 썼습니다. NULL의 정렬 위치는 DB마다 달라서(HANA는 오름차순에서 NULL이 앞) `hkont`만으로 정렬하면 총계 행이 맨 위로 올 수 있습니다. 행 종류를 숫자로 만들어 정렬하면 어디서나 같은 순서가 됩니다.
- 총계 −6010.00은 0이 아닙니다. 고객(120000)·공급업체(210000) 라인을 뺐고, 불균형 전표 두 건도 있기 때문입니다. 모든 라인을 넣고 불균형 전표가 없으면 총계는 0이어야 합니다. 결과를 이렇게 **검산하는 습관**을 들이세요.
- `GROUPING`을 `CASE` 조건 안에 쓰는 것이 막히면(실제 시스템에서 확인 필요) `GROUPING( hkont ) AS g1, GROUPING( period ) AS g2`를 결과에 그대로 내고 ABAP에서 `row_level`을 계산하세요.

오답이 나오는 전형적인 실수
- 소계가 없음 → `GROUP BY hkont, period`만 씀.
- 113100 소계가 3490.00 → `SA` 전표의 대변 200.00을 + 로 더함(부호 누락).

</details>

#### 3단계. Q17 매출채권 연령 분석 — 기준일 시점의 미결

요구사항
1. 고객 라인(`koart = 'D'`)의 **송장 쪽**(차변 `S`) 중 기준일 시점에 **미결**인 항목을 고객별로 나이(일) 구간에 나눠 합하세요.
   - 기준일 시점 미결 = 전기일 ≤ 기준일 **그리고** (반제 전표가 없거나, 반제일이 기준일보다 뒤).
   - 나이 = 전기일 → 기준일 일수. 구간: 0~30, 31~60, 61~90, 91 이상.
2. 결과 열: `kunnr`, `name1`, `bucket_0_30`, `bucket_31_60`, `bucket_61_90`, `bucket_91_plus`, `total_open`, `oldest_days`. 정렬: `total_open` 내림차순, 같으면 `kunnr`.
3. 기준일 두 개로 채점합니다. 2026-02-28 기준에서는 3월 10일에 반제된 `C002` 송장이 **아직 미결**이어야 합니다.

기대 결과 (기준일 2026-06-30)

| kunnr | name1 | bucket_0_30 | bucket_31_60 | bucket_61_90 | bucket_91_plus | total_open | oldest_days |
|---|---|---|---|---|---|---|---|
| C005 | Texas Drives | 0.00 | 0.00 | 780.00 | 3040.00 | 3820.00 | 138 |
| C003 | Berlin Motoren | 400.00 | 0.00 | 1600.00 | 1450.00 | 3450.00 | 165 |
| C001 | 서울정밀 | 0.00 | 640.00 | 0.00 | 2400.00 | 3040.00 | 144 |
| C006 | Ohio Robotics | 0.00 | 300.00 | 0.00 | 0.00 | 300.00 | 46 |

기대 결과 (기준일 2026-02-28)

| kunnr | name1 | bucket_0_30 | bucket_31_60 | bucket_61_90 | bucket_91_plus | total_open | oldest_days |
|---|---|---|---|---|---|---|---|
| C005 | Texas Drives | 3040.00 | 0.00 | 0.00 | 0.00 | 3040.00 | 16 |
| C002 | 부산중공업 | 0.00 | 1470.00 | 0.00 | 0.00 | 1470.00 | 35 |
| C003 | Berlin Motoren | 0.00 | 1450.00 | 0.00 | 0.00 | 1450.00 | 43 |
| C001 | 서울정밀 | 900.00 | 0.00 | 0.00 | 0.00 | 900.00 | 22 |

채점 메서드 (두 개)

```abap
  METHOD q17.
    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q17(
      ( kunnr = 'C005' name1 = 'Texas Drives' bucket_0_30 = '0.00' bucket_31_60 = '0.00' bucket_61_90 = '780.00' bucket_91_plus = '3040.00' total_open = '3820.00' oldest_days = 138 )
      ( kunnr = 'C003' name1 = 'Berlin Motoren' bucket_0_30 = '400.00' bucket_31_60 = '0.00' bucket_61_90 = '1600.00' bucket_91_plus = '1450.00' total_open = '3450.00' oldest_days = 165 )
      ( kunnr = 'C001' name1 = '서울정밀' bucket_0_30 = '0.00' bucket_31_60 = '640.00' bucket_61_90 = '0.00' bucket_91_plus = '2400.00' total_open = '3040.00' oldest_days = 144 )
      ( kunnr = 'C006' name1 = 'Ohio Robotics' bucket_0_30 = '0.00' bucket_31_60 = '300.00' bucket_61_90 = '0.00' bucket_91_plus = '0.00' total_open = '300.00' oldest_days = 46 ) ).
    cl_abap_unit_assert=>assert_equals( act = cut->q17( iv_key_date = '20260630' ) exp = exp msg = 'Q17' ).
  ENDMETHOD.
```

(정의 부분에 `METHODS q17 FOR TESTING.`을 추가하세요.)

```abap
  METHOD q17_feb.
    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q17(
      ( kunnr = 'C005' name1 = 'Texas Drives' bucket_0_30 = '3040.00' bucket_31_60 = '0.00' bucket_61_90 = '0.00' bucket_91_plus = '0.00' total_open = '3040.00' oldest_days = 16 )
      ( kunnr = 'C002' name1 = '부산중공업' bucket_0_30 = '0.00' bucket_31_60 = '1470.00' bucket_61_90 = '0.00' bucket_91_plus = '0.00' total_open = '1470.00' oldest_days = 35 )
      ( kunnr = 'C003' name1 = 'Berlin Motoren' bucket_0_30 = '0.00' bucket_31_60 = '1450.00' bucket_61_90 = '0.00' bucket_91_plus = '0.00' total_open = '1450.00' oldest_days = 43 )
      ( kunnr = 'C001' name1 = '서울정밀' bucket_0_30 = '900.00' bucket_31_60 = '0.00' bucket_61_90 = '0.00' bucket_91_plus = '0.00' total_open = '900.00' oldest_days = 22 ) ).
    cl_abap_unit_assert=>assert_equals( act = cut->q17( iv_key_date = '20260228' ) exp = exp msg = 'Q17b' ).
  ENDMETHOD.
```

(정의 부분에 `METHODS q17_feb FOR TESTING.`을 추가하세요.)

<details><summary>정답·해설</summary>

```abap
  METHOD q17.
    WITH
      +open AS ( SELECT FROM zsq_bseg_### AS s
                   INNER JOIN zsq_bkpf_### AS h
                     ON  h~bukrs = s~bukrs
                     AND h~belnr = s~belnr
                     AND h~gjahr = s~gjahr
                   FIELDS s~kunnr,
                          CAST( s~dmbtr AS DEC( 15, 2 ) )          AS amount,
                          DATS_DAYS_BETWEEN( h~budat, @iv_key_date ) AS age_days
                   WHERE s~koart = 'D'
                     AND s~shkzg = 'S'
                     AND h~budat <= @iv_key_date
                     AND ( s~augbl = @space OR s~augdt > @iv_key_date ) )
      SELECT FROM +open AS o
             INNER JOIN zsq_kna1_### AS c ON c~kunnr = o~kunnr
        FIELDS o~kunnr,
               c~name1,
               SUM( CASE WHEN o~age_days <= 30                  THEN o~amount ELSE 0 END ) AS bucket_0_30,
               SUM( CASE WHEN o~age_days BETWEEN 31 AND 60      THEN o~amount ELSE 0 END ) AS bucket_31_60,
               SUM( CASE WHEN o~age_days BETWEEN 61 AND 90      THEN o~amount ELSE 0 END ) AS bucket_61_90,
               SUM( CASE WHEN o~age_days > 90                   THEN o~amount ELSE 0 END ) AS bucket_91_plus,
               SUM( o~amount )                                                             AS total_open,
               MAX( o~age_days )                                                           AS oldest_days
        GROUP BY o~kunnr, c~name1
        ORDER BY total_open DESCENDING, o~kunnr
        INTO CORRESPONDING FIELDS OF TABLE @result.
  ENDMETHOD.
```

왜 이렇게 쓰나
- 연령 분석은 **"지금 미결인가"가 아니라 "기준일에 미결이었나"**를 묻습니다. 월말 결산 보고서를 나중에 다시 뽑아도 같은 숫자가 나와야 하기 때문입니다. 그래서 `augbl = 공백`만 보면 안 되고, 반제일이 기준일 뒤인 항목도 미결로 넣습니다. 기준일 이후에 전기된 송장(`budat > 기준일`)은 빼야 합니다.
- 입금 전표의 고객 라인(대변 `H`)은 송장이 아니라 결제이므로 `shkzg = 'S'`로 뺐습니다. 실무에서는 미결 대변(선수금)도 연령에 넣는 경우가 있으니 요구사항을 확인하세요.
- 구간 경계: `BETWEEN 31 AND 60`은 양 끝을 포함합니다. 30일은 첫 구간, 31일은 둘째 구간입니다.
- 2026-02-28 기준에서 `C001`은 2/9에 반제된 1월 송장이 빠지고 2/6 송장(900.00, 22일)만 남습니다.

오답이 나오는 전형적인 실수
- 2월 기준에 `C002`가 없음 → `augbl = @space`만 검사.
- 2월 기준에 `C003`이 1450.00이 아님 → 3월 이후 전기된 송장을 포함(`budat <= 기준일` 누락).
- `C003`(6월 기준) 합계가 4760.00 → 반제된 3월 송장 1310.00을 넣음.

</details>

#### 4단계. Q18 반제 전표 매칭 — 같은 테이블 자기 조인

요구사항
1. 반제된 고객 송장 라인(`koart = 'D'`, `shkzg = 'S'`, `augbl`이 있음)마다, 반제 전표(`augbl`) 안의 **고객 대변 라인** 금액을 찾아 나란히 보여 주세요.
2. 결과 열: `invoice_no`, `kunnr`, `invoice_amount`, `clearing_doc`, `clearing_date`, `paid_amount`, `difference`(= 받은 금액 − 송장 금액). 정렬: `invoice_no`.

기대 결과

| invoice_no | kunnr | invoice_amount | clearing_doc | clearing_date | paid_amount | difference |
|---|---|---|---|---|---|---|
| 0100000001 | C001 | 520.00 | 1400000001 | 20260209 | 520.00 | 0.00 |
| 0100000003 | C002 | 1470.00 | 1400000002 | 20260310 | 1470.00 | 0.00 |
| 0100000006 | C003 | 1310.00 | 1400000003 | 20260420 | 1300.00 | -10.00 |

채점 메서드

```abap
  METHOD q18.
    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q18(
      ( invoice_no = '0100000001' kunnr = 'C001' invoice_amount = '520.00' clearing_doc = '1400000001' clearing_date = '20260209' paid_amount = '520.00' difference = '0.00' )
      ( invoice_no = '0100000003' kunnr = 'C002' invoice_amount = '1470.00' clearing_doc = '1400000002' clearing_date = '20260310' paid_amount = '1470.00' difference = '0.00' )
      ( invoice_no = '0100000006' kunnr = 'C003' invoice_amount = '1310.00' clearing_doc = '1400000003' clearing_date = '20260420' paid_amount = '1300.00' difference = '-10.00' ) ).
    cl_abap_unit_assert=>assert_equals( act = cut->q18( ) exp = exp msg = 'Q18' ).
  ENDMETHOD.
```

(정의 부분에 `METHODS q18 FOR TESTING.`을 추가하세요.)

<details><summary>정답·해설</summary>

```abap
  METHOD q18.
    SELECT FROM zsq_bseg_### AS i
           INNER JOIN zsq_bseg_### AS p
             ON  p~bukrs = i~bukrs
             AND p~gjahr = i~gjahr
             AND p~belnr = i~augbl
             AND p~koart = 'D'
             AND p~shkzg = 'H'
      FIELDS i~belnr AS invoice_no,
             i~kunnr,
             i~dmbtr AS invoice_amount,
             i~augbl AS clearing_doc,
             i~augdt AS clearing_date,
             p~dmbtr AS paid_amount,
             CAST( p~dmbtr AS DEC( 15, 2 ) ) - CAST( i~dmbtr AS DEC( 15, 2 ) ) AS difference
      WHERE i~koart = 'D'
        AND i~shkzg = 'S'
        AND i~augbl <> @space
      ORDER BY i~belnr
      INTO CORRESPONDING FIELDS OF TABLE @result.
  ENDMETHOD.
```

왜 이렇게 쓰나
- 같은 테이블을 별칭 두 개(`i` 송장, `p` 결제)로 조인했습니다. `i~augbl = p~belnr`가 "이 송장을 정리한 전표"를 찾는 연결입니다.
- 반제 전표 안에는 은행 라인(113100)도 있으므로 `p~koart = 'D' AND p~shkzg = 'H'`로 고객 라인 하나만 고릅니다. 이 조건을 빼면 송장 하나에 두 행이 나와 결과가 부풀어 오릅니다(조인 팬아웃).
- 실제 SAP에서 반제 전표의 연도(`auggj`)는 송장 연도와 다를 수 있습니다. 이 연습 테이블에는 `auggj`가 없어 `gjahr`를 같게 두었습니다.
- `0100000006`은 10.00을 덜 받고 반제됐습니다. 실무에서는 차액이 할인·손실 계정으로 처리됐는지 확인하는 단서가 됩니다.

오답이 나오는 전형적인 실수
- 행이 6개 → 반제 전표의 은행 라인까지 조인됨.
- 입금 전표 자체의 고객 라인(`augbl`이 자기 자신)이 송장처럼 나옴 → `i~shkzg = 'S'` 누락.

</details>

#### 5단계. Q19 판매 ↔ 회계 대사 — 세 종류의 불일치를 한 결과로

요구사항
1. 일반 판매 오더(`OR`)의 순금액과, 고객 송장 전표(`blart = 'DR'`)의 매출 라인(400000, 대변) 금액을 **참조 번호(`bkpf.xblnr` = 오더 번호)**로 대사하세요.
2. 불일치만 돌려줍니다. `status`:
   - `AMOUNT_DIFF`: 둘 다 있는데 금액이 다름
   - `NOT_INVOICED`: 판매 오더는 있는데 송장이 없음
   - `NO_SALES_ORDER`: 송장은 있는데 그 번호의 판매 오더가 없음
3. 결과 열: `doc_ref`(오더 번호 또는 송장의 참조 번호), `kunnr`(판매 오더의 고객, 판매 오더가 없으면 공백), `so_value`, `fi_value`, `status`. 정렬: `status`, `doc_ref`.
4. SELECT 한 번(`UNION ALL` 사용 가능)으로 만드세요.

기대 결과

| doc_ref | kunnr | so_value | fi_value | status |
|---|---|---|---|---|
| 0010000005 | C005 | 3040.00 | 3000.00 | AMOUNT_DIFF |
| 0010000012 | C003 | 1650.00 | 1600.00 | AMOUNT_DIFF |
| 0010000006 | C004 | 570.00 | 0.00 | NOT_INVOICED |
| 0010000009 | C006 | 780.00 | 0.00 | NOT_INVOICED |
| 0010000013 | C004 | 560.00 | 0.00 | NOT_INVOICED |
| 0010000015 | C006 | 2900.00 | 0.00 | NOT_INVOICED |
| 0010000016 | C002 | 1140.00 | 0.00 | NOT_INVOICED |
| 0010000018 | C005 | 810.00 | 0.00 | NOT_INVOICED |
| 0010000019 | C007 | 2420.00 | 0.00 | NOT_INVOICED |
| 0010000099 | (빈 값) | 0.00 | 300.00 | NO_SALES_ORDER |

채점 메서드

```abap
  METHOD q19.
    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q19(
      ( doc_ref = '0010000005' kunnr = 'C005' so_value = '3040.00' fi_value = '3000.00' status = 'AMOUNT_DIFF' )
      ( doc_ref = '0010000012' kunnr = 'C003' so_value = '1650.00' fi_value = '1600.00' status = 'AMOUNT_DIFF' )
      ( doc_ref = '0010000006' kunnr = 'C004' so_value = '570.00' fi_value = '0.00' status = 'NOT_INVOICED' )
      ( doc_ref = '0010000009' kunnr = 'C006' so_value = '780.00' fi_value = '0.00' status = 'NOT_INVOICED' )
      ( doc_ref = '0010000013' kunnr = 'C004' so_value = '560.00' fi_value = '0.00' status = 'NOT_INVOICED' )
      ( doc_ref = '0010000015' kunnr = 'C006' so_value = '2900.00' fi_value = '0.00' status = 'NOT_INVOICED' )
      ( doc_ref = '0010000016' kunnr = 'C002' so_value = '1140.00' fi_value = '0.00' status = 'NOT_INVOICED' )
      ( doc_ref = '0010000018' kunnr = 'C005' so_value = '810.00' fi_value = '0.00' status = 'NOT_INVOICED' )
      ( doc_ref = '0010000019' kunnr = 'C007' so_value = '2420.00' fi_value = '0.00' status = 'NOT_INVOICED' )
      ( doc_ref = '0010000099' so_value = '0.00' fi_value = '300.00' status = 'NO_SALES_ORDER' ) ).
    cl_abap_unit_assert=>assert_equals( act = cut->q19( ) exp = exp msg = 'Q19' ).
  ENDMETHOD.
```

(정의 부분에 `METHODS q19 FOR TESTING.`을 추가하세요.)

<details><summary>정답·해설</summary>

```abap
  METHOD q19.
    WITH
      +so AS ( SELECT FROM zsq_vbak_### AS h
                 INNER JOIN zsq_vbap_### AS i ON i~vbeln = h~vbeln
                 FIELDS h~vbeln, h~kunnr,
                        SUM( CAST( i~netwr AS DEC( 15, 2 ) ) ) AS so_value
                 WHERE h~auart = 'OR'
                 GROUP BY h~vbeln, h~kunnr ),
      +fi AS ( SELECT FROM zsq_bkpf_### AS h
                 INNER JOIN zsq_bseg_### AS s
                   ON  s~bukrs = h~bukrs
                   AND s~belnr = h~belnr
                   AND s~gjahr = h~gjahr
                 FIELDS h~xblnr,
                        SUM( CAST( s~dmbtr AS DEC( 15, 2 ) ) ) AS fi_value
                 WHERE h~blart = 'DR'
                   AND s~hkont = '400000'
                   AND s~shkzg = 'H'
                 GROUP BY h~xblnr )
      SELECT FROM +so AS o
             LEFT OUTER JOIN +fi AS f ON f~xblnr = o~vbeln
        FIELDS CAST( o~vbeln AS CHAR( 16 ) )             AS doc_ref,
               o~kunnr                                   AS kunnr,
               o~so_value                                AS so_value,
               COALESCE( f~fi_value, CAST( 0 AS DEC( 15, 2 ) ) ) AS fi_value,
               CAST( CASE WHEN f~xblnr IS NULL THEN 'NOT_INVOICED'
                          ELSE 'AMOUNT_DIFF' END AS CHAR( 14 ) ) AS status
        WHERE f~xblnr IS NULL
           OR f~fi_value <> o~so_value
      UNION ALL
      SELECT FROM +fi AS f
        FIELDS f~xblnr                                   AS doc_ref,
               CAST( ' ' AS CHAR( 10 ) )                 AS kunnr,
               CAST( 0 AS DEC( 15, 2 ) )                 AS so_value,
               f~fi_value                                AS fi_value,
               CAST( 'NO_SALES_ORDER' AS CHAR( 14 ) )    AS status
        WHERE NOT EXISTS ( SELECT vbeln FROM zsq_vbak_### WHERE vbeln = f~xblnr )
      ORDER BY status, doc_ref
      INTO CORRESPONDING FIELDS OF TABLE @result.
  ENDMETHOD.
```

왜 이렇게 쓰나
- 양쪽에서 빠진 것을 모두 찾는 대사는 원래 `FULL OUTER JOIN` 자리입니다. ABAP SQL에는 FULL OUTER JOIN이 없으므로 **LEFT JOIN(왼쪽 기준 불일치) + UNION ALL + NOT EXISTS(오른쪽에만 있는 것)**로 만듭니다. 실무 대사 쿼리의 기본 뼈대입니다.
- 대사는 **같은 단위로 먼저 집계한 뒤** 비교해야 합니다. 판매는 오더 단위, 회계는 참조 번호 단위로 각각 CTE에서 합계를 낸 뒤 조인했습니다. 품목·라인 단위로 바로 조인하면 금액이 곱해집니다.
- `UNION`의 두 SELECT는 열 개수·순서·타입이 맞아야 합니다. `vbeln`(10자)과 `xblnr`(16자), 길이가 다른 상태 문자열을 `CAST`로 맞췄습니다. 타입 오류가 나면 이 부분부터 보세요(실제 시스템에서 확인 필요).
- `ORDER BY`는 UNION 전체 결과에 한 번만, 열 별칭으로 씁니다.
- `NOT_INVOICED` < `NO_SALES_ORDER` 순서는 문자 코드 순입니다(`T`가 `_`보다 앞).
- 반품 오더 `0010000010`은 `OR`이 아니라서 처음부터 빠집니다. 실무라면 반품은 대변 메모(credit memo)와 따로 대사합니다.

오답이 나오는 전형적인 실수
- `0010000099`가 없음 → 오른쪽에만 있는 송장을 찾는 두 번째 SELECT 누락.
- 일치하는 오더(`MATCH`)까지 나옴 → 불일치 조건(`WHERE`) 누락.
- `0010000005`의 `fi_value`가 6040.00 → 매출 라인만 고르지 않고 고객 라인(차변 3040.00)까지 더함.

</details>

#### 6단계. Q20 중복 의심 공급업체 송장 — 자기 조인 + 날짜 창

요구사항
1. 공급업체 송장(`blart = 'KR'`)의 공급업체 라인(`koart = 'K'`)끼리 비교해, **같은 공급업체·같은 금액·전기일 차이 3일 이내**인 쌍을 찾으세요.
2. 한 쌍은 한 번만(앞 전표 번호 < 뒤 전표 번호) 나옵니다.
3. 결과 열: `lifnr`, `belnr_1`, `xblnr_1`, `belnr_2`, `xblnr_2`, `amount`, `days_apart`(뒤 − 앞). 정렬: `lifnr`, `belnr_1`.
4. 데이터 함정: `V500`의 760.00 두 건은 13일 차이라 아니고, 300.00 두 건은 공급업체가 달라 아닙니다.

기대 결과

| lifnr | belnr_1 | xblnr_1 | belnr_2 | xblnr_2 | amount | days_apart |
|---|---|---|---|---|---|---|
| V200 | 1900000001 | INV-A77 | 1900000002 | INV-A77B | 1200.00 | 2 |

채점 메서드

```abap
  METHOD q20.
    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q20(
      ( lifnr = 'V200' belnr_1 = '1900000001' xblnr_1 = 'INV-A77' belnr_2 = '1900000002' xblnr_2 = 'INV-A77B' amount = '1200.00' days_apart = 2 ) ).
    cl_abap_unit_assert=>assert_equals( act = cut->q20( ) exp = exp msg = 'Q20' ).
  ENDMETHOD.
```

(정의 부분에 `METHODS q20 FOR TESTING.`을 추가하세요.)

<details><summary>정답·해설</summary>

```abap
  METHOD q20.
    WITH
      +kr AS ( SELECT FROM zsq_bkpf_### AS h
                 INNER JOIN zsq_bseg_### AS s
                   ON  s~bukrs = h~bukrs
                   AND s~belnr = h~belnr
                   AND s~gjahr = h~gjahr
                 FIELDS s~lifnr, h~belnr, h~xblnr, h~budat, s~dmbtr
                 WHERE h~blart = 'KR'
                   AND s~koart = 'K' )
      SELECT FROM +kr AS a
             INNER JOIN +kr AS b
               ON  b~lifnr = a~lifnr
               AND b~dmbtr = a~dmbtr
               AND b~belnr > a~belnr
        FIELDS a~lifnr,
               a~belnr AS belnr_1,
               a~xblnr AS xblnr_1,
               b~belnr AS belnr_2,
               b~xblnr AS xblnr_2,
               a~dmbtr AS amount,
               DATS_DAYS_BETWEEN( a~budat, b~budat ) AS days_apart
        WHERE ABS( DATS_DAYS_BETWEEN( a~budat, b~budat ) ) <= 3
        ORDER BY a~lifnr, a~belnr
        INTO CORRESPONDING FIELDS OF TABLE @result.
  ENDMETHOD.
```

왜 이렇게 쓰나
- `b~belnr > a~belnr`가 두 가지 일을 합니다. 자기 자신과의 짝(`=`)을 없애고, (A,B)와 (B,A)가 두 번 나오는 것도 막습니다. `<>`를 쓰면 같은 쌍이 두 번 나옵니다.
- 전표 번호 순서와 날짜 순서가 다를 수 있어 `ABS`로 날짜 차이의 절댓값을 봤습니다.
- 같은 CTE를 두 번 쓰는 것은 CTE의 장점입니다. 같은 서브쿼리를 두 번 쓰는 것보다 읽기 쉽고, DB가 한 번만 계산할 수도 있습니다.
- 실무 확장: 참조 번호가 비슷한지(`INV-A77`과 `INV-A77B`)도 보려면 `LEFT( a~xblnr, 7 ) = LEFT( b~xblnr, 7 )` 같은 조건이나 HANA 퍼지 검색을 씁니다. 금액이 정확히 같지 않고 1% 이내인 경우까지 잡으려면 `ABS( a - b ) <= a * 0.01`로 바꿉니다.

오답이 나오는 전형적인 실수
- 같은 쌍이 두 번 → `<>` 사용.
- 행이 0개 → 송장 라인 대신 비용 라인(`koart = 'S'`)으로 비교했는데 `lifnr`가 비어 있어 조인 실패.

</details>

### R-22. 같은 문제를 CDS·AMDP·Custom Entity로: SQL을 모델로 옮기고 Fiori까지 [작성] ★★★★
<!-- covers: CDS view entity 집계, left outer to many join, 계층 CDS(기본 뷰 + 집계 뷰), 파라미터 CDS, $parameters, dats_days_between, CDS case, cl_cds_test_environment, i_select_base_dependencies, CDS table function, AMDP, if_amdp_marker_hdb, BY DATABASE FUNCTION, SQLScript 윈도 함수, SESSION_CONTEXT CDS_CLIENT, @ClientHandling, 교차 검증(두 구현 비교), custom entity, unmanaged query, 동적 ORDER BY, OFFSET, 페이징, 건수 요청 -->

**목표**
- ABAP SQL로 푼 문항을 **재사용 가능한 모델**(CDS 뷰, 테이블 함수, custom entity)로 옮길 수 있습니다.
- 각 기술의 한계를 알고 고를 수 있습니다: CDS 뷰 엔터티에는 윈도 함수가 없고, 테이블 함수(AMDP)는 SQLScript로 무엇이든 할 수 있지만 ABAP SQL 테스트 더블이 통하지 않으며, custom entity는 ABAP 코드로 무엇이든 만들 수 있지만 필터·정렬·페이징을 직접 처리해야 합니다.
- 같은 결과를 두 방식으로 만들고 **서로 비교하는 테스트**로 정답을 확인할 수 있습니다(기대값을 손으로 적을 수 없는 실무 데이터에서 쓰는 방법).

**전제**
- R-19~R-21의 Q01, Q10, Q13, Q17을 통과했습니다. R-08(custom entity)을 해 봤다면 4단계가 쉽습니다.
- 4단계 Fiori 확인 전에 `ZCL_SQ_SEED_###`를 F9로 실행해 DB에 데이터를 넣어 두세요(테이블 함수와 Fiori는 실제 DB를 읽습니다).

**만들 객체**

| 순서 | 객체 유형 | 이름 | 역할 |
|---|---|---|---|
| 1 | CDS 뷰 엔터티 | `ZSQ_I_POITEM_###` | 삭제 안 된 품목 + 공급업체 + 품목 금액 |
| 2 | CDS 뷰 엔터티 | `ZSQ_I_VENDORSPEND_###` | Q01을 CDS로 (집계) |
| 3 | CDS 뷰 엔터티(파라미터) | `ZSQ_I_ARAGING_###` | Q17을 CDS로 (기준일 파라미터) |
| 4 | CDS 테이블 함수 | `ZSQ_TF_ISLANDS_###` | Q13을 SQLScript로 |
| 5 | ABAP 클래스(AMDP) | `ZCL_SQ_AMDP_###` | 테이블 함수 구현 |
| 6 | 테스트 클래스 | `ZCL_SQ_QUERIES_###` 안 `LTC_MODEL` | CDS 테스트 더블 채점 |
| 7 | Custom entity + 쿼리 클래스 | `ZSQ_CE_TOPCUST_###`, `ZCL_SQ_CE_TOPCUST_###` | Q10을 OData로 (필터·정렬·페이징) |
| 8 | 서비스 정의·바인딩 | `ZSQ_UI_TOPCUST_###`, `ZSQ_UI_TOPCUST_O4_###` | Fiori 미리보기 |

#### 1단계. Q01을 CDS 두 층으로: 품목 뷰 + 공급업체 집계 뷰

요구사항
1. `ZSQ_I_POITEM_###`: `zsq_ekpo_###` ⋈ `zsq_ekko_###`에서 **삭제되지 않은 품목**만, 요소 `PurchaseOrder`(키), `PurchaseOrderItem`(키), `Supplier`, `Material`, `NetPrice`, `NetValue`(수량 × 단가, `abap.dec(24,5)`), `ItemCount`(항상 1, `abap.int4`).
2. `ZSQ_I_VENDORSPEND_###`: `zsq_lfa1_###`을 왼쪽에 두고 `zsq_ekko_###`, `ZSQ_I_POITEM_###`을 LEFT OUTER JOIN 해서 Q01과 같은 열(`Supplier`, `SupplierName`, `PoCount`, `ItemCount`, `NetValue`)을 돌려줍니다.
3. Q01 결과와 같은지 3단계 테스트에서 확인합니다(정렬은 CDS가 아니라 소비하는 SELECT가 정합니다).

**직접 추가할 어노테이션**
- `@AccessControl.authorizationCheck` — DCL 없이 읽을 수 있게(연습용).
- `@EndUserText.label` — 뷰 설명.
- `@Semantics.amount.currencyCode` — `NetPrice`가 통화 금액임을 표시(통화 요소 필요).

**확인**
- 두 뷰가 활성화되고, F8 데이터 미리보기에서 `ZSQ_I_VENDORSPEND_###`가 6행(`V600` 포함)을 보여 줍니다. `V600`의 `ItemCount`·`NetValue`는 빈 칸(NULL)으로 보입니다.

<details><summary>정답·해설</summary>

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'SQL drill: PO items (not deleted)'
define view entity ZSQ_I_POITEM_###
  as select from zsq_ekpo_### as p
    inner join   zsq_ekko_### as k on k.ebeln = p.ebeln
{
  key p.ebeln                                                   as PurchaseOrder,
  key p.ebelp                                                   as PurchaseOrderItem,
      k.lifnr                                                   as Supplier,
      p.matnr                                                   as Material,
      @Semantics.amount.currencyCode: 'Currency'
      p.netpr                                                   as NetPrice,
      p.waers                                                   as Currency,
      cast( p.menge as abap.dec(13,3) ) * cast( p.netpr as abap.dec(11,2) )
                                                                as NetValue,
      cast( 1 as abap.int4 )                                    as ItemCount
}
where p.loekz = ''
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'SQL drill: spend per supplier (Q01)'
define view entity ZSQ_I_VENDORSPEND_###
  as select from    zsq_lfa1_###     as v
    left outer to many join zsq_ekko_###     as k on k.lifnr = v.lifnr
    left outer to many join ZSQ_I_POITEM_### as p on p.PurchaseOrder = k.ebeln
{
  key v.lifnr                       as Supplier,
      v.name1                       as SupplierName,
      count( distinct k.ebeln )     as PoCount,
      sum( p.ItemCount )            as ItemCount,
      sum( p.NetValue )             as NetValue
}
group by v.lifnr, v.name1
```

왜 이렇게 쓰나
- CDS에서는 ON 조건에 상수 비교(`p.loekz = ''`)를 넣는 것이 제한적이라, **삭제 조건을 아래층 뷰의 WHERE로 내리고** 그 뷰를 LEFT JOIN 했습니다. Q01의 "오른쪽 조건은 ON에"와 같은 효과입니다. 계층을 나누면 품목 뷰를 다른 분석에서도 재사용할 수 있습니다.
- CDS 뷰 엔터티의 `count`는 `count(*)`와 `count(distinct …)`만 됩니다. NULL을 빼고 세는 `COUNT( 열 )`이 없으므로 "항상 1인 열"을 만들어 `sum`했습니다. 품목이 없으면 `sum`이 NULL → ABAP에서 0.
- `left outer to many join`의 `to many`는 카디널리티 표시입니다. 집계 뷰에서는 결과에 영향이 없지만, 표시해 두면 최적화와 경고 처리에 쓰입니다.
- `cast( … as abap.dec )`로 QUAN·CURR를 바꿔 곱했습니다. 뷰 엔터티에서 통화 금액끼리의 산술이 막히면 이 방식이나 `curr_to_decfloat_amount( )`를 씁니다(실제 시스템에서 확인 필요).
- `PoCount`는 품목 뷰가 아니라 `zsq_ekko_###`의 `ebeln`을 셉니다. 품목이 모두 삭제된 오더도 오더 수에는 들어가야 하기 때문입니다(Q01 정의).

</details>

#### 2단계. Q17을 파라미터 CDS로: 기준일 연령 분석

요구사항
1. `ZSQ_I_ARAGING_###`를 파라미터 `P_KeyDate : abap.dats`를 받는 뷰 엔터티로 만드세요. Q17과 같은 열을 고객별로 돌려줍니다(정렬 제외).
2. 아래층 뷰 없이 한 뷰에서 만들되, 구간 금액은 `sum( case … end )`로 계산합니다. 막히면 라인 단위 뷰와 집계 뷰 두 층으로 나누세요.

**직접 추가할 어노테이션**
- `@AccessControl.authorizationCheck`, `@EndUserText.label` — 1단계와 같음.
- `@EndUserText.label` (파라미터) — 파라미터 설명.

**확인**
- F8 미리보기에서 파라미터에 `20260228`을 넣으면 4행, 첫 행 `C005 3040.00`이 나옵니다.

<details><summary>정답·해설</summary>

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'SQL drill: AR aging at key date (Q17)'
define view entity ZSQ_I_ARAGING_###
  with parameters
    @EndUserText.label: 'Key date'
    P_KeyDate : abap.dats
  as select from zsq_bseg_### as s
    inner join   zsq_bkpf_### as h on  h.bukrs = s.bukrs
                                   and h.belnr = s.belnr
                                   and h.gjahr = s.gjahr
    inner join   zsq_kna1_### as c on  c.kunnr = s.kunnr
{
  key s.kunnr as Customer,
      c.name1 as CustomerName,
      sum( case when dats_days_between( h.budat, $parameters.P_KeyDate ) <= 30
                then cast( s.dmbtr as abap.dec(15,2) ) else cast( 0 as abap.dec(15,2) ) end ) as Bucket0to30,
      sum( case when dats_days_between( h.budat, $parameters.P_KeyDate ) between 31 and 60
                then cast( s.dmbtr as abap.dec(15,2) ) else cast( 0 as abap.dec(15,2) ) end ) as Bucket31to60,
      sum( case when dats_days_between( h.budat, $parameters.P_KeyDate ) between 61 and 90
                then cast( s.dmbtr as abap.dec(15,2) ) else cast( 0 as abap.dec(15,2) ) end ) as Bucket61to90,
      sum( case when dats_days_between( h.budat, $parameters.P_KeyDate ) > 90
                then cast( s.dmbtr as abap.dec(15,2) ) else cast( 0 as abap.dec(15,2) ) end ) as Bucket91Plus,
      sum( cast( s.dmbtr as abap.dec(15,2) ) )                                               as TotalOpen,
      max( dats_days_between( h.budat, $parameters.P_KeyDate ) )                             as OldestDays
}
where s.koart  = 'D'
  and s.shkzg  = 'S'
  and h.budat <= $parameters.P_KeyDate
  and ( s.augbl = '' or s.augdt > $parameters.P_KeyDate )
group by s.kunnr, c.name1
```

왜 이렇게 쓰나
- 파라미터는 "기준일처럼 **조회할 때마다 바뀌는 값**이 계산 안쪽(WHERE·CASE)에 들어가야 할 때" 씁니다. 결과를 거르는 값이면 파라미터 대신 소비자가 WHERE를 걸면 됩니다. 기준일 연령 분석은 계산 자체가 기준일에 달려 있어 파라미터가 필요합니다.
- 소비할 때: `SELECT FROM zsq_i_araging_###( p_keydate = @lv_key ) FIELDS …`. OData로 내보내면 파라미터가 URL 경로에 들어가는 특이한 모양이 됩니다(`…/ZSQ_I_ARAGING(P_KeyDate=2026-06-30)/Set`).
- `sum( case … )`가 활성화에서 막히면(실제 시스템에서 확인 필요) 라인 단위 뷰에 `Bucket0to30` 등 금액 열을 만들고 위층에서 `sum( Bucket0to30 )`만 하세요.

</details>

#### 3단계. CDS 테스트 더블로 채점: Q01·Q17과 같은 결과인지

요구사항
1. `ZCL_SQ_QUERIES_###`의 Test Classes 탭에 두 번째 테스트 클래스 `ltc_model`을 추가하세요.
2. `cl_cds_test_environment=>create_for_multiple_cds`로 `ZSQ_I_VENDORSPEND_###`와 `ZSQ_I_ARAGING_###`의 테스트 환경을 만들고, 아래 테이블까지 대역으로 바꾸게(`select_base_dependencies`) 하세요. 시드 데이터를 넣습니다.
3. 테스트 두 개:
   - `spend_equals_q01`: 뷰를 `ORDER BY NetValue DESCENDING, Supplier`로 읽어 Q01 기대 결과와 비교.
   - `aging_feb_equals_q17`: 뷰를 `p_keydate = '20260228'`로 읽어 Q17(2월 기준) 기대 결과와 비교.

**확인**
- 두 테스트가 초록입니다. `ZSQ_I_POITEM_###`의 WHERE를 지우면 `spend_equals_q01`이 실패해야 합니다(테스트가 진짜로 뷰 로직을 검사하는지 확인).

<details><summary>정답·해설</summary>

```abap
CLASS ltc_model DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    CLASS-DATA env TYPE REF TO if_cds_test_environment.
    CLASS-METHODS class_setup.
    CLASS-METHODS class_teardown.
    METHODS spend_equals_q01 FOR TESTING.
    METHODS aging_feb_equals_q17 FOR TESTING.
ENDCLASS.


CLASS ltc_model IMPLEMENTATION.

  METHOD class_setup.
    env = cl_cds_test_environment=>create_for_multiple_cds(
            i_for_entities = VALUE #(
              ( i_for_entity = 'ZSQ_I_VENDORSPEND_###' i_select_base_dependencies = abap_true )
              ( i_for_entity = 'ZSQ_I_ARAGING_###'     i_select_base_dependencies = abap_true ) ) ).

    DATA(seed) = NEW zcl_sq_seed_###( ).
    DATA(lt_lfa1) = seed->lfa1( ).  env->insert_test_data( lt_lfa1 ).
    DATA(lt_ekko) = seed->ekko( ).  env->insert_test_data( lt_ekko ).
    DATA(lt_ekpo) = seed->ekpo( ).  env->insert_test_data( lt_ekpo ).
    DATA(lt_kna1) = seed->kna1( ).  env->insert_test_data( lt_kna1 ).
    DATA(lt_bkpf) = seed->bkpf( ).  env->insert_test_data( lt_bkpf ).
    DATA(lt_bseg) = seed->bseg( ).  env->insert_test_data( lt_bseg ).
  ENDMETHOD.

  METHOD class_teardown.
    env->destroy( ).
  ENDMETHOD.

  METHOD spend_equals_q01.
    SELECT FROM zsq_i_vendorspend_###
      FIELDS supplier     AS lifnr,
             suppliername AS name1,
             poCount      AS po_count,
             itemcount    AS item_count,
             netvalue     AS net_value
      ORDER BY netvalue DESCENDING, supplier
      INTO TABLE @DATA(act).
    DATA lt_act TYPE zcl_sq_queries_###=>tt_q01.
    lt_act = CORRESPONDING #( act ).

    " Q01 기대 결과 그대로
    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q01(
      ( lifnr = 'V300' name1 = 'Pacific Parts' po_count = 2 item_count = 4 net_value = '6334.00' )
      ( lifnr = 'V400' name1 = '대성기계' po_count = 2 item_count = 4 net_value = '5738.50' )
      ( lifnr = 'V200' name1 = 'Nord Supply' po_count = 3 item_count = 8 net_value = '4401.00' )
      ( lifnr = 'V500' name1 = 'Alpen Tech' po_count = 2 item_count = 4 net_value = '3551.00' )
      ( lifnr = 'V100' name1 = '한빛상사' po_count = 3 item_count = 7 net_value = '1815.00' )
      ( lifnr = 'V600' name1 = 'Idle Vendor' po_count = 0 item_count = 0 net_value = '0.00' ) ).
    cl_abap_unit_assert=>assert_equals( act = lt_act exp = exp msg = 'CDS spend = Q01' ).
  ENDMETHOD.

  METHOD aging_feb_equals_q17.
    SELECT FROM zsq_i_araging_###( p_keydate = '20260228' )
      FIELDS customer     AS kunnr,
             customername AS name1,
             bucket0to30  AS bucket_0_30,
             bucket31to60 AS bucket_31_60,
             bucket61to90 AS bucket_61_90,
             bucket91plus AS bucket_91_plus,
             totalopen    AS total_open,
             oldestdays   AS oldest_days
      ORDER BY totalopen DESCENDING, customer
      INTO TABLE @DATA(act).
    DATA lt_act TYPE zcl_sq_queries_###=>tt_q17.
    lt_act = CORRESPONDING #( act ).

    DATA(exp) = VALUE zcl_sq_queries_###=>tt_q17(
      ( kunnr = 'C005' name1 = 'Texas Drives' bucket_0_30 = '3040.00' bucket_31_60 = '0.00' bucket_61_90 = '0.00' bucket_91_plus = '0.00' total_open = '3040.00' oldest_days = 16 )
      ( kunnr = 'C002' name1 = '부산중공업' bucket_0_30 = '0.00' bucket_31_60 = '1470.00' bucket_61_90 = '0.00' bucket_91_plus = '0.00' total_open = '1470.00' oldest_days = 35 )
      ( kunnr = 'C003' name1 = 'Berlin Motoren' bucket_0_30 = '0.00' bucket_31_60 = '1450.00' bucket_61_90 = '0.00' bucket_91_plus = '0.00' total_open = '1450.00' oldest_days = 43 )
      ( kunnr = 'C001' name1 = '서울정밀' bucket_0_30 = '900.00' bucket_31_60 = '0.00' bucket_61_90 = '0.00' bucket_91_plus = '0.00' total_open = '900.00' oldest_days = 22 ) ).
    cl_abap_unit_assert=>assert_equals( act = lt_act exp = exp msg = 'CDS aging = Q17 (Feb)' ).
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나
- `cl_osql_test_environment`(R-19)는 **ABAP SQL이 읽는 테이블**을 바꿔치기하고, `cl_cds_test_environment`는 **CDS 뷰가 읽는 의존 객체**를 바꿔치기합니다. 뷰의 로직(조인·집계·CASE)을 검증하려면 후자를 써야 합니다.
- `i_select_base_dependencies = abap_true`는 바로 아래 의존(`ZSQ_I_POITEM_###`)이 아니라 **맨 아래 DB 테이블까지** 대역으로 바꿉니다. 그래야 품목 뷰의 WHERE까지 함께 검증됩니다. `abap_false`면 품목 뷰 자체가 대역이 되어 그 안의 로직은 검사되지 않습니다.
- 뷰의 요소 이름(`Supplier`)과 채점 타입의 열 이름(`lifnr`)이 다르므로, SELECT에서 별칭으로 이름을 맞춘 뒤 인라인 테이블로 받고 `CORRESPONDING #( )`으로 채점 타입에 옮겼습니다. 열 순서·타입이 달라도 이름만 맞으면 옮겨집니다.
- 같은 기대 결과를 SQL 풀이와 CDS 모델이 함께 통과하면, 두 구현이 같은 업무 규칙을 따른다는 증거가 됩니다.

</details>

#### 4단계. Q13을 CDS 테이블 함수 + AMDP(SQLScript)로, 그리고 교차 검증

요구사항
1. CDS 테이블 함수 `ZSQ_TF_ISLANDS_###`를 만드세요. 반환 요소: `client`(키), `kunnr`(키), `start_period`(키, `abap.char(6)`), `end_period`, `months`(`abap.int4`). 클라이언트는 세션 변수로 처리합니다.
2. AMDP 클래스 `ZCL_SQ_AMDP_###`에 구현 메서드 `get_islands`를 SQLScript로 쓰세요. 로직은 Q13과 같습니다(일반 오더만, 고객·월 중복 제거, 달 번호 − 순번).
3. `ZCL_SQ_QUERIES_###`의 `main`(콘솔)에 **교차 검증**을 추가하세요: 실제 DB에서 `q13( )` 결과와 `SELECT FROM zsq_tf_islands_###` 결과(같은 정렬)를 비교해 같으면 `Q13 = TF : OK`, 다르면 다른 행을 출력합니다.

**직접 추가할 어노테이션**
- `@EndUserText.label` — 테이블 함수 설명.
- `@ClientHandling.type` — 클라이언트 종속 여부.
- `@ClientHandling.algorithm` — 클라이언트를 세션 변수로 넘길지.

**확인**
- 시드를 DB에 넣은 뒤 F9 → `Q13 = TF : OK`.
- F8 미리보기로 테이블 함수를 직접 열어 15행이 나오는지 봅니다.

<details><summary>정답·해설</summary>

```cds
@EndUserText.label: 'SQL drill: order month islands (Q13)'
@ClientHandling.type: #CLIENT_DEPENDENT
@ClientHandling.algorithm: #SESSION_VARIABLE
define table function ZSQ_TF_ISLANDS_###
returns
{
  key client       : abap.clnt;
  key kunnr        : abap.char(10);
  key start_period : abap.char(6);
      end_period   : abap.char(6);
      months       : abap.int4;
}
implemented by method zcl_sq_amdp_###=>get_islands;
```

```abap
CLASS zcl_sq_amdp_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_amdp_marker_hdb.
    CLASS-METHODS get_islands FOR TABLE FUNCTION zsq_tf_islands_###.

  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.


CLASS zcl_sq_amdp_### IMPLEMENTATION.

  METHOD get_islands
    BY DATABASE FUNCTION FOR HDB
    LANGUAGE SQLSCRIPT
    OPTIONS READ-ONLY
    USING zsq_vbak_###.

    mon = SELECT DISTINCT
                 client,
                 kunnr,
                 LEFT( audat, 6 )                                     AS period,
                 YEAR( TO_DATE( audat, 'YYYYMMDD' ) ) * 12
                   + MONTH( TO_DATE( audat, 'YYYYMMDD' ) )            AS month_no
            FROM zsq_vbak_###
           WHERE client = SESSION_CONTEXT( 'CDS_CLIENT' )
             AND auart  = 'OR';

    isl = SELECT client,
                 kunnr,
                 period,
                 month_no - ROW_NUMBER( ) OVER ( PARTITION BY client, kunnr ORDER BY month_no ) AS island_key
            FROM :mon;

    RETURN SELECT client,
                  kunnr,
                  MIN( period )       AS start_period,
                  MAX( period )       AS end_period,
                  TO_INT( COUNT(*) )  AS months
             FROM :isl
            GROUP BY client, kunnr, island_key;
  ENDMETHOD.

ENDCLASS.
```

`main`에 추가할 교차 검증:

```abap
    DATA(lt_sql) = q13( ).

    SELECT FROM zsq_tf_islands_###
      FIELDS kunnr, start_period, end_period, months
      ORDER BY kunnr, start_period
      INTO CORRESPONDING FIELDS OF TABLE @DATA(lt_tf_raw).
    DATA lt_tf TYPE tt_q13.
    lt_tf = CORRESPONDING #( lt_tf_raw ).

    IF lt_sql = lt_tf.
      out->write( |Q13 = TF : OK ({ lines( lt_sql ) } rows)| ).
    ELSE.
      out->write( 'Q13 <> TF' ).
      out->write( name = 'ABAP SQL'       data = lt_sql ).
      out->write( name = 'Table function' data = lt_tf ).
    ENDIF.
```

왜 이렇게 쓰나
- **왜 테이블 함수인가**: CDS 뷰 엔터티에는 윈도 함수(`ROW_NUMBER`, `LAG` …)가 없습니다. 섬 찾기처럼 윈도 함수가 꼭 필요한 로직을 **CDS 모델로** 내보내려면 테이블 함수가 답입니다. 테이블 함수는 다른 CDS 뷰의 데이터 소스, 연관 대상, OData 노출 대상이 될 수 있습니다.
- AMDP 본문은 ABAP SQL이 아니라 **HANA SQLScript**입니다. 그래서 `~` 대신 `.`, 호스트 변수 대신 `:변수`, 날짜 함수도 HANA 것(`TO_DATE`, `YEAR`, `MONTH`)을 씁니다. 읽는 테이블은 모두 `USING`에 적어야 합니다.
- 클라이언트: ABAP SQL은 클라이언트를 자동으로 거르지만 SQLScript는 그러지 않습니다. `@ClientHandling.algorithm: #SESSION_VARIABLE` + `SESSION_CONTEXT( 'CDS_CLIENT' )`로 직접 걸러야 다른 클라이언트 데이터가 섞이지 않습니다. 반환 구조의 첫 요소가 클라이언트 필드여야 합니다.
- `COUNT(*)`는 HANA에서 BIGINT라 `abap.int4` 요소와 맞추려고 `TO_INT`로 바꿨습니다.
- **교차 검증**: AMDP는 `cl_osql_test_environment`로 테이블을 바꿔치기할 수 없습니다(ABAP SQL이 아니라서). 그래서 실제 DB에서 이미 검증된 Q13 결과와 비교했습니다. 실무 데이터처럼 기대값을 손으로 적을 수 없을 때 "독립된 두 구현이 같은 답을 내는지"가 강력한 테스트가 됩니다.
- BTP ABAP 환경에서 AMDP는 쓸 수 있지만 언어 버전·릴리스 상태 검사가 있습니다. 활성화 오류가 나면 패키지의 ABAP 언어 버전과 `USING` 목록을 먼저 보세요(실제 시스템에서 확인 필요).

</details>

#### 5단계. Q10을 custom entity로: 필터·정렬·페이징을 직접 처리하는 Top-N 앱

요구사항
1. custom entity `ZSQ_CE_TOPCUST_###`: 요소 `Country`(키), `Customer`(키), `RankNo`, `CustomerName`, `NetValue`(통화 금액), `Currency`, `SharePct`(`abap.dec(5,1)`). 쿼리 클래스 `ZCL_SQ_CE_TOPCUST_###`를 연결합니다.
2. 쿼리 클래스 `select`에서 다음을 모두 처리하세요.
   - 필터: `Country`, `RankNo`(예: `RankNo le 2`)를 range로 받아 **윈도 계산이 끝난 뒤** 거릅니다. 기본(필터 없음)은 전체 순위.
   - 정렬: 요청된 정렬을 동적 `ORDER BY`로. 요청이 없으면 `Country, RankNo, Customer`.
   - 페이징: `OFFSET`과 `UP TO n ROWS`를 **DB에서** 적용.
   - 건수: 같은 필터로 `COUNT(*)`.
3. 서비스 정의·바인딩(OData V4 UI)을 만들고 Fiori 미리보기에서 `RankNo`에 "2 이하" 필터를 걸어 KR이 세 행인지 봅니다.

**직접 추가할 어노테이션**
- `@ObjectModel.query.implementedBy` — 쿼리 클래스 연결.
- `@Semantics.amount.currencyCode` — 금액 요소.
- `@UI.lineItem`, `@UI.selectionField` — 목록 열과 필터 칸.
- `@UI.headerInfo` — 목록 제목.

**확인**
- Fiori 미리보기: 필터 없이 Go → 7명 전체(순위 3인 고객은 없음). `RankNo ≤ 1` → 3행.
- 목록 맨 위 건수 표시가 필터와 맞게 바뀝니다(건수 요청 처리).
- 열 머리글을 눌러 `NetValue` 내림차순 정렬이 됩니다(동적 ORDER BY).

<details><summary>정답·해설</summary>

```cds
@EndUserText.label: 'Top customers per country (Q10)'
@ObjectModel.query.implementedBy: 'ABAP:ZCL_SQ_CE_TOPCUST_###'
@UI.headerInfo: { typeName: 'Customer', typeNamePlural: 'Top Customers' }
define custom entity ZSQ_CE_TOPCUST_###
{
      @UI.lineItem: [{ position: 10 }]
      @UI.selectionField: [{ position: 10 }]
  key Country      : abap.char(3);
      @UI.lineItem: [{ position: 30 }]
  key Customer     : abap.char(10);
      @UI.lineItem: [{ position: 20 }]
      @UI.selectionField: [{ position: 20 }]
      RankNo       : abap.int4;
      @UI.lineItem: [{ position: 40 }]
      CustomerName : abap.char(35);
      @UI.lineItem: [{ position: 50 }]
      @Semantics.amount.currencyCode: 'Currency'
      NetValue     : abap.curr(15,2);
      Currency     : abap.cuky;
      @UI.lineItem: [{ position: 60 }]
      SharePct     : abap.dec(5,1);
}
```

```abap
CLASS zcl_sq_ce_topcust_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_rap_query_provider.
  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.


CLASS zcl_sq_ce_topcust_### IMPLEMENTATION.

  METHOD if_rap_query_provider~select.
    DATA lt_data TYPE STANDARD TABLE OF zsq_ce_topcust_### WITH EMPTY KEY.
    DATA lr_country TYPE RANGE OF zsq_kna1_###-land1.
    DATA lr_rank    TYPE RANGE OF i.

    " 1) 필터 → range (지원하지 않는 필터는 오류로 알림)
    TRY.
        DATA(lt_ranges) = io_request->get_filter( )->get_as_ranges( ).
      CATCH cx_rap_query_filter_no_range INTO DATA(lx_range).
        RAISE EXCEPTION TYPE cx_rap_query_provider EXPORTING previous = lx_range.
    ENDTRY.
    LOOP AT lt_ranges INTO DATA(ls_range).
      CASE ls_range-name.
        WHEN 'COUNTRY'. lr_country = CORRESPONDING #( ls_range-range ).
        WHEN 'RANKNO'.  lr_rank    = CORRESPONDING #( ls_range-range ).
      ENDCASE.
    ENDLOOP.

    " 2) 정렬 → 동적 ORDER BY 문자열 (엔터티 요소 이름만 허용)
    DATA(lt_sort) = io_request->get_sort_elements( ).
    DATA(lv_order) = COND string(
      WHEN lt_sort IS INITIAL THEN `country, rankno, customer`
      ELSE REDUCE string( INIT s = ``
                          FOR ls IN lt_sort
                          NEXT s = s && COND #( WHEN s IS NOT INITIAL THEN `, ` )
                                     && to_lower( ls-element_name )
                                     && COND #( WHEN ls-descending = abap_true THEN ` DESCENDING` ) ) ).

    " 3) 페이징
    DATA(lv_offset) = io_request->get_paging( )->get_offset( ).
    DATA(lv_size)   = io_request->get_paging( )->get_page_size( ).
    DATA(lv_max)    = COND i( WHEN lv_size = if_rap_query_paging=>page_size_unlimited THEN 0 ELSE lv_size ).

    " 4) Q10 로직 (Top-N 고정 없이 전체 순위) + 바깥에서 필터·정렬·페이징
    IF io_request->is_data_requested( ).
      WITH
        +so   AS ( SELECT FROM zsq_vbak_### AS h
                     INNER JOIN zsq_vbap_### AS i ON i~vbeln = h~vbeln
                     FIELDS h~kunnr, h~waerk,
                            SUM( CASE h~auart WHEN 'RE' THEN CAST( i~netwr AS DEC( 15, 2 ) ) * -1
                                              ELSE CAST( i~netwr AS DEC( 15, 2 ) ) END ) AS order_value
                     GROUP BY h~vbeln, h~kunnr, h~waerk ),
        +cust AS ( SELECT FROM +so AS o
                     INNER JOIN zsq_kna1_### AS c ON c~kunnr = o~kunnr
                     FIELDS c~land1, o~kunnr, c~name1, o~waerk,
                            SUM( o~order_value ) AS net_value
                     GROUP BY c~land1, o~kunnr, c~name1, o~waerk ),
        +rk   AS ( SELECT FROM +cust
                     FIELDS land1 AS country, kunnr AS customer, name1 AS customername,
                            waerk AS currency, net_value AS netvalue,
                            DENSE_RANK( ) OVER( PARTITION BY land1 ORDER BY net_value DESCENDING ) AS rankno,
                            SUM( net_value ) OVER( PARTITION BY land1 ) AS country_total )
        SELECT FROM +rk
          FIELDS country, customer, rankno, customername, netvalue, currency,
                 DIVISION( netvalue * 100, country_total, 1 ) AS sharepct
          WHERE country IN @lr_country
            AND rankno  IN @lr_rank
          ORDER BY (lv_order)
          INTO CORRESPONDING FIELDS OF TABLE @lt_data
          OFFSET @lv_offset
          UP TO @lv_max ROWS.
      io_response->set_data( lt_data ).
    ENDIF.

    " 5) 건수 (같은 필터, 정렬·페이징 없이)
    IF io_request->is_total_numb_of_rec_requested( ).
      WITH
        +so   AS ( SELECT FROM zsq_vbak_### AS h
                     INNER JOIN zsq_vbap_### AS i ON i~vbeln = h~vbeln
                     FIELDS h~kunnr,
                            SUM( CASE h~auart WHEN 'RE' THEN CAST( i~netwr AS DEC( 15, 2 ) ) * -1
                                              ELSE CAST( i~netwr AS DEC( 15, 2 ) ) END ) AS order_value
                     GROUP BY h~vbeln, h~kunnr ),
        +cust AS ( SELECT FROM +so AS o
                     INNER JOIN zsq_kna1_### AS c ON c~kunnr = o~kunnr
                     FIELDS c~land1, o~kunnr, SUM( o~order_value ) AS net_value
                     GROUP BY c~land1, o~kunnr ),
        +rk   AS ( SELECT FROM +cust
                     FIELDS land1 AS country,
                            DENSE_RANK( ) OVER( PARTITION BY land1 ORDER BY net_value DESCENDING ) AS rankno )
        SELECT FROM +rk
          FIELDS COUNT( * )
          WHERE country IN @lr_country
            AND rankno  IN @lr_rank
          INTO @DATA(lv_count).
      io_response->set_total_number_of_records( lv_count ).
    ENDIF.
  ENDMETHOD.

ENDCLASS.
```

서비스 정의와 바인딩:

```cds
@EndUserText.label: 'Top customers (SQL drill)'
define service ZSQ_UI_TOPCUST_### {
  expose ZSQ_CE_TOPCUST_### as TopCustomer;
}
```

바인딩 `ZSQ_UI_TOPCUST_O4_###`: Binding Type **OData V4 - UI**, Publish → `TopCustomer` 선택 → Preview.

왜 이렇게 쓰나
- **필터를 거는 위치가 결과를 바꿉니다.** `RankNo ≤ 2`는 순위를 매긴 **뒤에** 걸어야 합니다. 국가 필터는 순위 전에 걸어도 같은 결과지만(순위가 국가별이라), 만약 "2026년 4월 이후 주문만" 같은 필터를 순위 전에 걸면 순위 자체가 달라집니다. 요소별로 "윈도 앞에서 거르는 필터인가, 뒤에서 거르는 필터인가"를 정해야 합니다. 이 클래스는 모든 필터를 윈도 뒤에서 겁니다.
- 페이징은 `ORDER BY` + `OFFSET` + `UP TO n ROWS`로 **DB에서** 자릅니다. 전체를 읽어 ABAP에서 자르면 결과가 많을 때 느립니다. `UP TO 0 ROWS`는 "제한 없음"이라 무제한 요청에 0을 넘겼습니다.
- 동적 `ORDER BY (lv_order)`에는 **엔터티 요소 이름만** 들어갑니다(`get_sort_elements`가 주는 이름). 사용자 입력 문자열을 그대로 SQL에 넣지 않으므로 인젝션 위험이 없습니다. CTE에서 열 별칭을 엔터티 요소 이름과 같게(소문자) 지어 둔 이유입니다.
- 건수 쿼리를 데이터 쿼리와 따로 둔 것은 R-08과 같은 이유입니다. 같은 CTE를 두 번 쓰는 중복이 싫으면, 데이터 쿼리를 `UP TO`/`OFFSET` 없이 한 번 읽어 ABAP에서 건수와 페이지를 만드는 방식도 있지만 데이터가 많으면 비효율입니다.
- 이 단계가 RAP와 SQL을 잇는 지점입니다. R-08이 "조회 엔진을 ABAP 루프로 계산"했다면, 여기서는 **계산 전체를 DB(윈도 함수)로 밀어 넣고** RAP 쿼리 계약(필터·정렬·페이징·건수)만 ABAP에서 처리했습니다.

자주 나는 오류와 해결
- `ORDER BY (lv_order)`와 CTE를 같이 쓸 때 활성화 오류가 나면, `+rk` 결과를 `INTO TABLE`로 받은 뒤 `SELECT FROM @lt_rk … ORDER BY (lv_order) OFFSET … UP TO …`로 두 번에 나누세요(실제 시스템에서 확인 필요).
- 목록이 스크롤할 때마다 같은 행 → `OFFSET`을 빠뜨림.

</details>

## 출처

- 쿼리포터(sql.10xflow.kr) — SAP 테이블(EKKO/EKPO, VBAK/VBAP, BKPF/BSEG)로 SQL을 풀고 실행 결과로 채점하는 방식을 참고해 R-19~R-22 단원을 구성(문항과 데이터는 이 문제집용으로 새로 작성).
