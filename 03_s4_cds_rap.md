# 03. S/4HANA · CDS · ABAP Cloud · RAP

ABAP on HANA·코드 푸시다운에서 출발해 CDS 뷰 엔티티, ABAP Cloud(clean core), RAP(BDEF·EML·Draft·트랜잭션), OData·Fiori Elements 연결, 테스트까지 한 흐름으로 묶은 통합 문제집이다. 문제 하나에 여러 소문항을 넣어, 예전에 잘게 나뉘어 있던 문제들이 묻던 내용을 빠짐없이 다시 묻는다. 손으로 답안을 쓰는 서면 시험을 기준으로 했다.

## ABAP on HANA·코드 푸시다운·S/4HANA 전환

### C-001. HANA의 특성과 코드 푸시다운 수단 고르기 [개념] ★★
<!-- src: RB-001, RB-002, RB-003, RB-006, IS-037, RB-005, MX-051, RB-009, RB-010 -->
팀장이 "ECC 시절 리포트를 S/4HANA에 맞게 다시 짜라"고 했다. 아래 물음에 답하시오.

(1) SAP HANA의 기술적 특징을 3가지 이상 쓰고, 각 특징이 ABAP 개발 방식에 준 영향을 쓰시오. 이 변화를 한 단어로 무엇이라 부르는지, "데이터를 코드로" 방식과 비교해 그 의미와 목적을 쓰시오.

(2) 클래식 DB 접근 성능 5원칙(① 결과 집합을 작게 ② 전송량을 작게 ③ 왕복 횟수를 적게 ④ 검색 부하를 작게 ⑤ DB 부하를 줄인다)이 HANA에서 각각 유지되는지, 더 중요해지는지, 반대로 바뀌는지 이유와 함께 쓰시오.

(3) 옳지 **않은** 것을 고르시오.
① 컬럼 스토어 테이블은 딕셔너리 인코딩 같은 압축으로 저장 공간을 줄인다.
② ORDER BY 없이 읽은 SELECT 결과는 기본 키 순서로 반환되는 것이 보장된다.
③ 별도의 합계 테이블 없이 원천 데이터에서 실시간으로 집계할 수 있다.
④ 한 행의 모든 컬럼을 읽는 `SELECT *`는 컬럼 스토어에서 상대적으로 비싸다.
⑤ 컬럼 스토어에서는 많은 2차 인덱스가 더 이상 필요 없다.

(4) 다음 중 코드 푸시다운이 **아닌** 것을 고르고 이유를 쓰시오.
① CDS 뷰 엔티티의 `sum( )`·`group by` ② ABAP SQL의 `CASE` 식과 `GROUP BY` ③ AMDP 프로시저의 SQLScript 계산 ④ `SELECT ... ENDSELECT` 루프 안에서 ABAP 변수에 합계 누적 ⑤ CDS 테이블 함수

(5) 표를 채우시오.

| 방법 | 위치 | 재사용 범위 | 권한·클라이언트 처리 | DB 독립성 | 고르는 경우 |
|---|---|---|---|---|---|
| ABAP SQL | | | | | |
| CDS 뷰 엔티티 | | | | | |
| CDS 테이블 함수 | | | | | |
| AMDP 프로시저 | | | | | |

그리고 SAP가 권장하는 선택 순서를 한 문장으로 쓰시오.

(6) DB 고유 SQL을 실행하는 Native SQL(`EXEC SQL`), ADBC, AMDP를 ABAP SQL과 비교하시오(문법 검사 시점, 클라이언트 처리, ABAP Cloud 사용 가능 여부).

(7) 운영 시스템에서 느린 리포트·SQL을 찾고 원인을 분석하는 도구를 4가지 이상 쓰고 용도를 쓰시오. 그리고 성능 개선 작업의 순서를 한 문장으로 쓰시오.

<details><summary>정답·해설</summary>

**(1)**

| HANA 특징 | ABAP 개발에 미친 영향 |
|---|---|
| 인메모리(주 메모리에서 처리) | 디스크 I/O보다 "애플리케이션 서버로 옮기는 데이터 양"이 병목이 된다 |
| 컬럼 스토어(컬럼 단위 저장, 딕셔너리 인코딩 등 압축) | 집계·필터·대량 스캔이 빠르다. 한 행의 모든 컬럼을 다시 조립하는 `SELECT *`는 상대적으로 비싸다 |
| 병렬 처리(컬럼·파티션 단위로 여러 코어) | 큰 데이터를 ABAP 루프로 처리하기보다 SQL 한 문장으로 DB에 맡기는 편이 낫다 |
| OLTP와 OLAP을 한 DB에서 | 합계·인덱스 테이블 없이 원천에서 바로 집계(S/4HANA 데이터 모델 단순화) |

- 이름: **코드 푸시다운(Code-to-Data)**. "데이터를 코드로 가져오지 말고 코드를 데이터로 보낸다". 필터·조인·집계·변환 같은 데이터 집약적 계산을 애플리케이션 서버의 ABAP이 아니라 DB(HANA)에서 수행한다.
- 목적: DB와 앱 서버 사이 전송량·왕복 횟수 감소, HANA의 인메모리·컬럼 저장·병렬 처리 활용.
- 행 스토어는 한 행 전체를 빨리 읽고, 컬럼 스토어는 특정 컬럼을 대량 집계할 때 빠르다는 대비를 답에 넣으면 좋다.

**(2)**

| 원칙 | HANA에서 | 이유 |
|---|---|---|
| ① 결과 집합을 작게(WHERE) | 유지, 여전히 중요 | 필요 없는 행을 옮기는 비용은 그대로 |
| ② 전송량을 작게(필요한 컬럼만) | 더 중요 | 컬럼 스토어에서 `SELECT *`는 행을 다시 조립해야 함 |
| ③ 왕복 횟수를 적게 | 유지, 더 중요 | LOOP 안 SELECT 대신 JOIN·서브쿼리·한 번의 집계 SQL |
| ④ 검색 부하를 작게(인덱스) | 비중 줄어듦 | 컬럼마다 인덱스처럼 동작해 2차 인덱스가 대부분 불필요(매우 선택적인 조회에는 여전히 사용) |
| ⑤ DB 부하를 줄인다(계산은 ABAP에서) | **반대로 바뀜** | 계산·집계는 DB로 내리는 것이 원칙. 단, 자주 읽는 작은 설정 테이블의 테이블 버퍼링은 여전히 유효 |

"HANA니까 규칙이 다 필요 없다"가 아니라 ⑤만 방향이 바뀌고 ①②③은 더 중요해졌다는 것이 핵심이다.

**(3)** ② — ORDER BY가 없으면 어떤 DB에서도 순서는 정해져 있지 않다. 예전 DB는 기본 키 인덱스를 타며 우연히 키 순서였지만 HANA는 병렬 처리로 순서가 달라져 `BINARY SEARCH`, `AT NEW`에 기대던 코드가 깨진다. ① 같은 값이 많아 딕셔너리·run-length 압축이 잘 된다. ③ S/4HANA는 GLT0, BSIS 같은 합계·인덱스 테이블을 없애고 ACDOCA에서 집계한다. ⑤ 매우 선택적인 조회나 유일성 보장에는 여전히 인덱스를 쓴다.

**(4)** ④ — `SELECT ... ENDSELECT`는 행을 하나씩 앱 서버로 가져와 ABAP에서 계산하는 Data-to-Code 방식이다. 나머지는 DB에서 계산하고 결과만 가져온다.

**(5)**

| 방법 | 위치 | 재사용 범위 | 권한·클라이언트 처리 | DB 독립성 | 고르는 경우 |
|---|---|---|---|---|---|
| ABAP SQL | ABAP 프로그램 안 | 그 프로그램에서만 | 클라이언트 자동, 권한은 `AUTHORITY-CHECK` 직접(CDS를 읽으면 DCL 자동) | 있음 | 한 곳에서만 쓰는 단순 조회·집계 |
| CDS 뷰 엔티티 | DDL 소스(저장소 객체) | 여러 프로그램, 다른 CDS, OData·RAP·분석 | 클라이언트 자동, DCL로 행 권한 자동, 어노테이션·association | 있음 | **기본 선택**. 재사용 데이터 모델, Fiori/RAP 노출 |
| CDS 테이블 함수 | CDS 정의 + AMDP 함수 구현 | CDS처럼 SELECT, 다른 CDS에서 조인 | 클라이언트 직접 처리(`@ClientHandling`), DCL 정의 가능 | HANA 전용 | CDS 문법으로 안 되는 SQLScript 로직인데 결과를 CDS 모델에 넣어야 할 때 |
| AMDP 프로시저 | ABAP 클래스 메서드 안 SQLScript | ABAP 코드에서만 호출 | 자동 권한·클라이언트 처리 없음 | HANA 전용(`FOR HDB`) | 여러 결과 테이블·여러 단계 절차 로직, 대량 계산 배치, AMDP BAdI |

선택 순서: "ABAP SQL 또는 CDS로 되면 그것을 쓰고, 안 될 때만 AMDP(CDS에서 써야 하면 테이블 함수 + AMDP)". AMDP는 DB 종속, 클라이언트·권한 직접 처리, 디버깅 부담이 단점이고, ABAP Cloud에서는 읽기 전용(`OPTIONS READ-ONLY`)만 허용된다.

**(6)**

| 방법 | 특징 |
|---|---|
| ABAP SQL | DB 독립. 활성화 때 문법 검사, 자동 클라이언트 처리, 테이블 버퍼 사용 |
| `EXEC SQL ... ENDEXEC` | DB 고유 SQL을 정적으로. 검사는 실행 시점, 자동 클라이언트 처리 없음. 구식 |
| ADBC(`CL_SQL_STATEMENT` 등) | 클래스 기반으로 Native SQL을 동적으로 실행. 실행 시점에만 검사, 클라이언트 처리 없음 |
| AMDP | SQLScript를 ABAP 메서드에. ABAP 저장소 객체라 이송·버전 관리가 ABAP과 같고 활성화 때 HANA 프로시저 생성·문법 검사. HANA 전용 |

ABAP Cloud에서는 `EXEC SQL`과 ADBC를 쓸 수 없고 AMDP는 읽기 전용으로만 쓴다. Native SQL·ADBC·AMDP는 클라이언트 조건을 직접 넣어야 한다(AMDP는 `CDS SESSION CLIENT DEPENDENT` 옵션으로 해결 가능).

**(7)**

| 도구 | 용도 |
|---|---|
| ST05(SQL Trace) | 실행된 SQL·횟수·시간·중복 SELECT, 실행 계획(Explain) |
| SAT / ADT ABAP Profiler | ABAP 실행 시간 분석(어느 메서드·문장에서 시간이 드는지) |
| SQLM(SQL Monitor) | 운영 시스템에서 오랜 기간 SQL 사용량·비용을 낮은 부하로 수집 |
| SWLT(SQL Performance Tuning Worklist) | SQLM 실행 데이터 + ATC 정적 점검을 합쳐 개선 우선순위 결정 |
| ATC/SCI 성능 점검 | LOOP 안 SELECT, 인덱스 없는 조회 같은 정적 패턴 탐지 |
| ST12, STAD | 단일 트랜잭션 추적, 통계 레코드 |

순서: 먼저 측정(SQLM/ST05/SAT)으로 병목을 찾고, ATC·SWLT로 대상을 정하고, ABAP 수준의 낭비(불필요한 행·컬럼, 루프 안 SELECT)를 없앤 뒤 계산을 DB로 내리고, 다시 측정한다.

</details>

---

### C-002. HANA 전환 후 틀린 결과·느린 코드를 SQL로 고치기 [코드] ★★
<!-- src: RB-004, IB-145, RB-007, RB-011, MX-041 -->
ECC(행 스토어 DB)에서 잘 돌던 코드들이다.

```abap
" (A)
SELECT carrid, connid, fldate, price FROM sflight
  WHERE carrid = 'LH'
  INTO TABLE @DATA(lt_flight).
READ TABLE lt_flight INTO DATA(ls_hit)
     WITH KEY carrid = 'LH' connid = '0400' BINARY SEARCH.   " 0400편 찾기
READ TABLE lt_flight INTO DATA(ls_first) INDEX 1.          " 가장 이른 항공편

" (B) 항공사별 결제 합계와 항공편 수
TYPES: BEGIN OF ty_sum,
         carrid   TYPE s_carr_id,
         currency TYPE s_currcode,
         total    TYPE s_sum,
         cnt      TYPE i,
       END OF ty_sum.
DATA lt_sum TYPE STANDARD TABLE OF ty_sum WITH EMPTY KEY.
SELECT carrid, connid, fldate, paymentsum, currency FROM sflight
  INTO TABLE @DATA(lt_all).
LOOP AT lt_all INTO DATA(ls_all).
  READ TABLE lt_sum ASSIGNING FIELD-SYMBOL(<ls_sum>) WITH KEY carrid = ls_all-carrid.
  IF sy-subrc <> 0.
    APPEND VALUE #( carrid = ls_all-carrid currency = ls_all-currency )
           TO lt_sum ASSIGNING <ls_sum>.
  ENDIF.
  <ls_sum>-total = <ls_sum>-total + ls_all-paymentsum.
  <ls_sum>-cnt   = <ls_sum>-cnt + 1.
ENDLOOP.
```

(1) (A)를 HANA로 옮긴 뒤 데이터가 있는데도 가끔 `sy-subrc = 4`가 나오고, `ls_first`가 가장 이른 항공편이 아닐 때가 있다. 원인을 쓰시오.

(2) (A)를 고치는 방법을 세 가지 쓰고, "가장 이른 항공편 한 건만" 필요할 때의 SELECT를 쓰시오. 이런 패턴을 전환 프로젝트에서 자동으로 찾는 도구와, 같은 이유로 점검 대상이 되는 다른 코드 패턴을 쓰시오.

(3) (B)의 성능 문제와 논리 오류를 하나씩 쓰고, SELECT 한 문장으로 다시 쓰시오.

(4) 항공사별 노선 수를 먼저 구하고 그 결과를 SCARR와 조인해 한 번의 DB 접근으로 읽는 공통 테이블 식(CTE)이다. 빈칸을 채우시오.

```abap
____(가)____ ____(나)____ AS (
       SELECT carrid, COUNT(*) AS conn_cnt
         FROM spfli
         ____(다)____ carrid )
  SELECT c~carrid, c~carrname, n~conn_cnt
    FROM scarr AS c
    ____(라)____ +conn AS n ON c~carrid = n~carrid
    INTO TABLE @DATA(lt_result).
```

(5) 기간 안의 항공편을 항공사별로 집계해 운항 2편 이상인 항공사만 점유 좌석 수 내림차순으로 10개 읽는다. 빈칸을 채우고, 신규 ABAP SQL 문법의 규칙 세 가지를 쓰시오.

```abap
SELECT FROM sflight AS f
       ____(1)____ scarr AS c ON c~carrid = f~carrid
  FIELDS f~carrid, c~carrname,
         COUNT(*)          AS flights,
         SUM( f~seatsocc ) AS occ
  WHERE f~fldate BETWEEN @p_from AND @p_to
    AND f~carrid IN @____(2)____
  ____(3)____ f~carrid, c~carrname
  ____(4)____ COUNT(*) >= 2
  ORDER BY occ ____(5)____
  INTO TABLE @____(6)____(lt_stat)
  UP TO 10 ROWS.
```

<details><summary>정답·해설</summary>

**(1)** SELECT에 ORDER BY가 없으면 결과 순서는 정해지지 않는다. 예전 DB는 기본 키 인덱스 순서로 나오는 경우가 많아 우연히 동작했지만, HANA(컬럼 스토어, 병렬 처리)에서는 매번 다를 수 있다. 그래서 정렬되지 않은 테이블에 `BINARY SEARCH`를 해 엉뚱한 위치를 보고 못 찾으며, `INDEX 1`이 가장 이른 날짜라는 가정도 깨진다.

**(2)**
1. SELECT에 `ORDER BY carrid, connid, fldate`(또는 `ORDER BY PRIMARY KEY`)
2. READ 전에 `SORT lt_flight BY carrid connid fldate.`
3. `SORTED TABLE ... WITH NON-UNIQUE KEY carrid connid`로 받고 `WITH TABLE KEY`나 테이블 식으로 읽기

```abap
SELECT carrid, connid, fldate, price FROM sflight
  WHERE carrid = 'LH'
  ORDER BY fldate
  INTO TABLE @DATA(lt_first)
  UP TO 1 ROWS.
```

- 도구: S/4HANA 전환 때 ATC의 HANA 준비 점검("ORDER BY 없는 SELECT/OPEN CURSOR 결과에 의존하는 문장 찾기").
- 같은 이유로 점검 대상: `DELETE ADJACENT DUPLICATES`, `AT NEW/AT END OF`(컨트롤 레벨), 키 일부로만 쓰는 `SELECT SINGLE`, 풀·클러스터 테이블이 투명 테이블로 바뀐 경우(예: BSEG).

**(3)**
- 성능: SFLIGHT 전체 행과 쓰지 않는 컬럼(connid, fldate)을 앱 서버로 옮긴 뒤 ABAP에서 집계한다. 표준 테이블 `READ ... WITH KEY`도 선형 검색이다.
- 논리: carrid로만 묶으면서 currency는 첫 행 값만 남긴다. 한 항공사에 통화가 여럿이면 서로 다른 통화 금액이 더해진다. 통화도 묶음 기준이어야 한다.

```abap
SELECT carrid, currency,
       SUM( paymentsum ) AS total,
       COUNT(*)          AS cnt
  FROM sflight
  GROUP BY carrid, currency
  INTO TABLE @DATA(lt_sum).
```

금액 합계는 반드시 통화 키와 함께 묶는다. CDS에서 금액을 `sum( )`할 때 `@Semantics.amount.currencyCode`가 필요한 것도 같은 이유다.

**(4)** (가) `WITH` (나) `+conn` (다) `GROUP BY` (라) `INNER JOIN`. CTE 이름은 `+`로 시작하고, 뒤따르는 메인 쿼리에서 테이블처럼 쓴다. 중간 결과를 내부 테이블로 받았다가 다시 SELECT하는 두 번의 왕복을 한 번으로 줄인다.

**(5)** (1) `INNER JOIN` (2) `s_carr`(선택 화면 SELECT-OPTIONS) (3) `GROUP BY` (4) `HAVING` (5) `DESCENDING` (6) `DATA`
- 호스트 변수 앞에 `@`, 필드 목록은 쉼표로 구분, `FIELDS`를 쓰면 `FROM`을 먼저 써서 ADT 코드 완성이 잘 된다.
- 집계 함수가 아닌 열(carrid, carrname)은 모두 `GROUP BY`에. 그룹 조건은 `WHERE`가 아니라 `HAVING`.
- `ORDER BY`에 별칭(occ) 사용 가능, `UP TO n ROWS`는 `INTO` 뒤에 둔다.

</details>

---

### C-003. S/4HANA 데이터 모델 단순화와 커스텀 코드 전환 [개념] ★★
<!-- src: IB-142, IB-143, IB-144, RB-008, IB-146, MX-042, IB-147, IB-151, IB-152 -->
ECC의 Z 코드 수천 개를 S/4HANA로 옮기는 프로젝트에 투입되었다.

(1) ABAP 개발자 관점에서 ECC와 S/4HANA의 차이를 다섯 가지 이상 쓰시오. "HANA에서 계산은 어디서 하나?"라는 꼬리 질문에 한 문장으로 답하시오.

(2) 데이터 모델 단순화에 대한 설명으로 옳지 **않은** 것을 고르시오.
① FI·CO·자산·자재원장 라인 아이템이 Universal Journal(ACDOCA)로 통합되었다.
② 자재 문서는 MATDOC으로 통합되었고 MKPF/MSEG 읽기는 호환성 뷰로 계속 동작한다.
③ 고객·공급업체 마스터는 Business Partner로 관리하며 CVI로 KNA1/LFA1과 동기화된다.
④ VBUK/VBUP가 없어지고 상태 필드는 VBAK/VBAP 등 문서 테이블로 옮겨졌다.
⑤ MATNR 필드 길이가 18자에서 10자로 줄었다.

(3) ECC에서 BSIS를 SELECT하던 Z 리포트를 옮겼더니 동작은 하지만 느려졌다. 이유를 "대체 객체"라는 말을 써서 설명하고, BSIS에 INSERT하던 프로그램은 어떻게 되는지, 권장 수정 방향을 쓰시오. 같은 원리가 적용되는 재고 쪽 예도 쓰시오.

(4) 데이터 모델 변화가 커스텀 코드에 주는 영향을 다음 표로 정리하시오.

| 변화 | 커스텀 코드 영향 |
|---|---|
| 재무 ACDOCA 통합 | |
| 재고 MATDOC 통합 | |
| Business Partner 통합 | |
| MATNR 40자 | |
| 풀·클러스터 → 투명 테이블 + HANA 순서 미보장 | |

(5) Z 코드 전환에 쓰는 분석·수정 도구를 다섯 가지 이상 쓰고 각각의 역할을 쓰시오. 그리고 전환 작업의 첫 단계와 전체 순서를 쓰시오.

(6) ABAP CDS와 HANA CDS(Calculation View 포함)를 정의 위치, 라이프사이클, DB 독립성, ABAP 연동 관점으로 비교하고, "어느 쪽이 빠른가", "ABAP 리포트에서 HANA 뷰를 쓰려면?"에 답하시오.

(7) S/4HANA Migration Cockpit의 두 이관 방식을 설명하고, 이관 객체를 수정·생성하는 도구와 실행 앱 이름을 쓰시오.

(8) SAP Gateway 배포 방식에 대해 옳지 **않은** 것을 고르고 바르게 고치시오.
① Embedded: Gateway 구성 요소가 백엔드 안에 함께 있다.
② Hub: 별도 프런트엔드 서버(FES)에 Gateway·UI 구성 요소를 두고 신뢰 RFC로 백엔드와 연결한다.
③ SAP은 S/4HANA에 Embedded 배포를 권장한다.
④ Hub 배포에서는 서비스 등록(/IWFND/MAINT_SERVICE)을 백엔드에서만 하면 된다.

<details><summary>정답·해설</summary>

**(1)**
1. DB: ECC는 여러 DB(Oracle, DB2 등), S/4HANA는 SAP HANA 전용(인메모리, 컬럼 스토어).
2. 데이터 모델 단순화: 집계·인덱스 테이블 제거(BSIS/BSAS, 재고 집계), ACDOCA, MATDOC, VBUK/VBUP 제거, 고객·공급업체 → Business Partner.
3. 코드 푸시다운: CDS 뷰, AMDP로 계산을 DB로.
4. 개발 모델: CDS + RAP + Fiori(OData V4)가 표준, ADT 중심. 클래식 Dynpro·리포트는 유지보수 위주.
5. 확장 원칙: Clean Core, 릴리스된 API와 확장 지점만(ABAP Cloud), 수정 금지.
6. 필드·기능 변경: MATNR 40자, 신용 관리·출력 관리(BRF+) 등 → Simplification List 확인.
7. 기존 Z 코드는 Custom Code Migration(ATC)으로 점검 후 수정.

꼬리 질문: "가능한 한 DB(HANA)에서 계산하고 결과만 전송한다."

**(2)** ⑤ — MATNR은 18자에서 **40자**로 확장되었다. MATNR을 CHAR 18 변수에 넣거나 오프셋으로 자르는 Z 코드는 점검 대상이다. 변경은 Simplification List와 Simplification Database(SYCM)로 확인한다.

**(3)**
- S/4HANA에서 BSIS 같은 인덱스·집계 테이블은 실제 데이터를 저장하지 않는다. DDIC 테이블 정의에 **대체 객체(Replacement/Proxy Object)로 CDS 호환성 뷰**가 연결되어 `SELECT FROM bsis`가 ACDOCA 등에서 그때그때 계산하는 뷰로 리디렉션된다. 코드는 깨지지 않지만 매번 계산·조인이 일어나 느릴 수 있다.
- 쓰기(INSERT/UPDATE/DELETE): 호환성 뷰는 읽기 전용이라 동작하지 않는다(ATC 단순화 검사에서 오류). 표준 전기(BAPI 등)를 통해서만 데이터가 생겨야 한다.
- 수정 방향: 새 모델(ACDOCA 또는 릴리스된 CDS 뷰 `I_JournalEntryItem` 등)을 직접 읽고 필요한 필드만, 집계는 DB에서.
- 재고: MSEG(MATDOC 기반), MARD 등 재고 집계 테이블의 수량 필드도 실행 시 계산되는 호환 뷰(NSDM_*)로 바뀌어 직접 UPDATE하던 코드가 깨진다. "테이블이 없어진 것이 아니라 뷰로 바뀌었다"가 핵심이다.

**(4)**

| 변화 | 커스텀 코드 영향 |
|---|---|
| 재무 ACDOCA 통합 | BSIS/BSAS/BSID·GLT0 등이 호환 뷰. 읽기는 동작(느릴 수 있음), 쓰기는 불가 |
| 재고 MATDOC 통합 | MKPF/MSEG 읽기는 호환 뷰, 집계 테이블 직접 UPDATE 코드는 깨짐 |
| Business Partner 통합 | 고객·공급업체는 BP(CVI). XD01·XK01 기반 BDC는 쓸 수 없음 |
| MATNR 40자 | 길이를 가정한 변수 선언·오프셋 처리가 잘림 |
| 풀·클러스터 → 투명 + 순서 미보장 | "SELECT 결과가 키 순서"를 가정한 BINARY SEARCH, 컨트롤 레벨, 첫 행 읽기가 틀어짐 |

**(5)**
1. **SAP Readiness Check**: 전환 전 시스템 전체 분석(단순화 항목 영향, 애드온, 커스텀 코드 개요).
2. **Simplification Database / SYCM**: 없어지거나 바뀐 객체 목록, 사용 중인 객체와 대조.
3. **ATC S/4HANA readiness 점검 변형**(예: S4HANA_READINESS, 원격 ATC): 단순화 항목 사용, ORDER BY 누락, 필드 길이 확장 문제 탐지.
4. **Custom Code Migration 앱(Fiori)**: 검사 결과 관리, 사용 로그(SCMON/SUSG/UPL) 기반으로 안 쓰는 코드 정리 범위 결정.
5. **ADT Quick Fix**: ATC 결과에 자동 수정 제안 적용.
6. **SPDD/SPAU**: 전환 중 수정 객체 조정.
7. **SQL Monitor(SQLM)**: 전환 후 SQL 성능 확인.

순서: 첫 단계는 **사용하지 않는 코드 삭제**(실행 기록 없는 Z 객체는 전환하지 않음) → 필수 수정(문법·데이터 모델) → ATC 재검증 → HANA 성능 최적화 → 가능하면 clean core(ABAP Cloud 규칙) 방향 개선.

**(6)**

| 항목 | ABAP CDS | HANA CDS / Calculation View |
|---|---|---|
| 정의 위치 | ABAP Dictionary(ADT), ABAP 패키지 | HANA 리포지토리(XS Classic) 또는 HDI 컨테이너 |
| 라이프사이클 | ABAP 전송(CTS) | HANA 전송(HALM, HDI 배포) |
| DB 독립성 | DB 독립 문법(ABAP 서버가 DB 뷰 생성) | HANA 전용 |
| ABAP 연동 | ABAP SQL에서 바로 SELECT, DCL, OData·UI 어노테이션, RAP 기반 | ABAP에서 직접 SELECT 불가 |

- 성능: 둘 다 결국 HANA에서 실행되는 SQL 뷰라 본질적 우열보다 모델링 품질이 좌우한다. ABAP 애플리케이션에서는 ABAP CDS가 SAP 권장.
- HANA 뷰 사용: DDIC **External View**(HANA 뷰를 가리키는 프록시 뷰)를 만들어 ABAP SQL로 읽거나 ADBC/AMDP로 호출.

**(7)**
- **스테이징 테이블 방식**: 이관 객체마다 HANA에 스테이징 테이블이 생기고, 파일(XML/CSV 템플릿) 업로드나 ETL 도구(SAP Data Services 등)로 채운다. Cockpit이 검증 → 값 매핑 → 시뮬레이션 → 실제 이관(내부적으로 표준 API/BAPI)을 수행. 파일 전용 방식도 스테이징으로 통합되었다. 데이터 정제·대량 적재에 유리하고 시뮬레이션으로 오류를 미리 본다.
- **직접 전송(Direct Transfer)**: 원본이 SAP 시스템(ECC 등)일 때 RFC로 직접 읽어 이관.
- 도구: **Migration Object Modeler**(예전 LTMOM, 최근 Fiori/ADT 기반)로 필드 추가·규칙 수정·사용자 정의 객체 생성. 실행 앱은 "Migrate Your Data"(예전 LTMC는 폐기). 결과는 메시지 로그와 표준 리포트로 대사한다.

**(8)** ④ — /IWFND/MAINT_SERVICE는 Gateway **허브**(프런트엔드, IWFND)에서 실행하고 시스템 별칭(System Alias)으로 백엔드(IWBEP, 서비스 구현)를 지정한다. Embedded는 같은 시스템이라 별칭이 LOCAL이다. 오류 로그도 허브(/IWFND/ERROR_LOG)와 백엔드(/IWBEP/ERROR_LOG)로 나뉜다.

</details>

---

## AMDP·CDS 테이블 함수

### C-004. AMDP 프로시저: 선언·구현·오류·제약 [코드] ★★★
<!-- src: RB-047, MX-049, RB-048, MX-050, RB-049, RB-050, MX-052 -->
항공사·통화별 가격 합계가 기준 금액 이상인 것만 돌려주는 AMDP(ABAP for Cloud Development)다.

```abap
CLASS zcl_flight_amdp DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES ____(a)____.
    TYPES: BEGIN OF ty_result,
             carrier_id    TYPE /dmo/carrier_id,
             currency_code TYPE /dmo/currency_code,
             total         TYPE /dmo/flight_price,
           END OF ty_result,
           tt_result TYPE STANDARD TABLE OF ty_result WITH EMPTY KEY.
    METHODS get_carrier_totals
      AMDP OPTIONS ____(b)____ CDS SESSION CLIENT DEPENDENT
      IMPORTING ____(c)____(iv_min) TYPE /dmo/flight_price
      EXPORTING VALUE(et_result)   TYPE tt_result.
ENDCLASS.

CLASS zcl_flight_amdp IMPLEMENTATION.
  METHOD get_carrier_totals
    ____(d)____ DATABASE ____(e)____ FOR ____(f)____
    LANGUAGE ____(g)____
    OPTIONS READ-ONLY
    ____(h)____ /dmo/flight.
    et_result = SELECT carrier_id, currency_code, SUM( price ) AS total
                  FROM "/DMO/FLIGHT"
                  GROUP BY carrier_id, currency_code
                  HAVING SUM( price ) >= ____(i)____;
  ENDMETHOD.
ENDCLASS.
```

(1) 빈칸 (a)~(i)를 채우시오.

(2) `/DMO/FLIGHT`를 큰따옴표로 감싼 이유와, `CDS SESSION CLIENT DEPENDENT`가 하는 일을 쓰시오. 이 옵션이 없는 Standard ABAP AMDP라면 클라이언트를 어떻게 걸러야 하는지 쓰시오.

(3) 다음 AMDP(Standard ABAP)에서 활성화 오류나 잘못된 동작을 일으키는 곳을 모두 찾아 고치시오.

```abap
CLASS zcl_mx_amdp2 DEFINITION PUBLIC.
  PUBLIC SECTION.
    TYPES tt_fl TYPE STANDARD TABLE OF /dmo/flight WITH EMPTY KEY.
    METHODS get_full
      IMPORTING iv_carrier TYPE /dmo/carrier_id
      RETURNING VALUE(rt_fl) TYPE tt_fl
      RAISING   cx_static_check.
ENDCLASS.

CLASS zcl_mx_amdp2 IMPLEMENTATION.
  METHOD get_full BY DATABASE PROCEDURE FOR HDB LANGUAGE SQLSCRIPT
                  OPTIONS READ-ONLY.
    rt_fl = SELECT * FROM "/DMO/FLIGHT"
             WHERE carrier_id = iv_carrier
               AND seats_occupied >= seats_max;
  ENDMETHOD.
ENDCLASS.
```

(4) AMDP의 단점·제약을 다섯 가지 이상 쓰고, AMDP를 디버깅하는 방법과 호출부의 오류 처리 방법을 쓰시오.

(5) AMDP에 대한 설명으로 옳지 **않은** 것을 **모두** 고르시오.
① AMDP 프로시저는 ABAP에서 일반 메서드처럼 호출하며, 처음 호출할 때 DB에 프로시저가 만들어진다.
② CDS 테이블 함수를 구현하는 메서드는 `CLASS-METHODS ... FOR TABLE FUNCTION`으로 선언하고 파라미터 목록을 직접 쓰지 않는다.
③ AMDP 메서드용 테이블 함수(`BY DATABASE FUNCTION`, RETURNING 테이블)는 ABAP에서 일반 메서드처럼 직접 호출할 수 있다.
④ AMDP 스칼라 함수는 ABAP에서 일반 메서드처럼 호출할 수 있다.
⑤ AMDP 안에서 `LOOP AT`, `CALL FUNCTION` 같은 ABAP 문을 SQLScript와 섞어 쓸 수 있다.
⑥ `OPTIONS READ-ONLY`를 주면 프로시저 안에서 DB를 바꾸는 문장을 쓸 수 없다.
⑦ AMDP 메서드의 파라미터는 값 전달이며 기본 타입이나 (평면 행) 테이블 타입이어야 한다.

<details><summary>정답·해설</summary>

**(1)** (a) `if_amdp_marker_hdb` (b) `READ-ONLY` (c) `VALUE` (d) `BY` (e) `PROCEDURE` (f) `HDB` (g) `SQLSCRIPT` (h) `USING` (i) `:iv_min`
- 마커 인터페이스 `IF_AMDP_MARKER_HDB` 필수, 파라미터는 값 전달만, 프로시저에는 `RETURNING` 없음.
- `USING`에 프로시저에서 읽는 DDIC 테이블·뷰·다른 AMDP를 모두 적는다(빠지면 문법 오류).
- SQLScript 안에서 ABAP 파라미터는 `:이름`. 결과 열의 순서·타입은 `et_result` 구조와 맞아야 한다.

**(2)** SQLScript에서 `/`가 들어간 이름은 큰따옴표(대문자)로 감싸야 한다. `CDS SESSION CLIENT DEPENDENT`를 쓰면 USING의 테이블을 감싸는 뷰가 암묵적으로 쓰여 HANA 세션 변수 `CDS_CLIENT`의 클라이언트 데이터만 읽는다(client-safe). ABAP Cloud에서는 `READ-ONLY`와 클라이언트 처리 옵션(`CDS SESSION CLIENT DEPENDENT` 또는 `CLIENT INDEPENDENT`)이 필수다. 옵션이 없으면 `WHERE mandt = SESSION_CONTEXT('CLIENT')`(테이블에 따라 `client = ...`)로 직접 거르거나 클라이언트를 파라미터로 받는다. ABAP SQL과 달리 Native SQL이라 자동 처리가 없다.

**(3)**
0. 클래스에 마커 인터페이스가 없다 → PUBLIC SECTION에 `INTERFACES if_amdp_marker_hdb.` 추가.
1. `IMPORTING iv_carrier` → `IMPORTING VALUE(iv_carrier)`(모든 파라미터 값 전달).
2. `RETURNING`은 프로시저에서 불가 → `EXPORTING VALUE(et_fl) TYPE tt_fl`, 본문도 `et_fl = ...`.
3. `RAISING cx_static_check` → 삭제(임의 예외 선언 불가, `cx_amdp_error` 하위 예외만 가능).
4. `USING /dmo/flight` 누락 → `OPTIONS READ-ONLY USING /dmo/flight.`
5. `carrier_id = iv_carrier` → `carrier_id = :iv_carrier`(콜론이 없으면 같은 이름의 열을 찾다가 오류).
6. 클라이언트 조건 없음(논리 오류, 모든 클라이언트 데이터가 섞임) → `client = SESSION_CONTEXT('CLIENT')` 추가 또는 클라이언트 처리 옵션.
(참고: 클래스 정의에 `FINAL CREATE PUBLIC`이 없는 것은 오류가 아니다. 테이블 파라미터 행 타입은 평면 구조여야 하며 `/dmo/flight` 행은 평면이라 문제없다.)

**(4)**
- 단점·제약: ① HANA 전용(`FOR HDB`) ② 자동 클라이언트 처리 없음 ③ CDS DCL 같은 자동 권한 검사 없음 ④ 파라미터는 값 전달만, 프로시저는 RETURNING 불가, 타입은 기본 타입·평면 행 테이블만 ⑤ ABAP 테이블 버퍼 미사용 ⑥ ABAP Cloud에서는 읽기 전용이고 released 데이터 소스만 USING 가능 ⑦ 본문에 ABAP 문 불가 ⑧ SQLScript를 아는 사람만 유지보수.
- 디버깅: ADT에서 SQLScript 줄에 중단점을 걸면 AMDP 디버거가 HANA 프로시저 실행을 멈추고 테이블 변수까지 보여 준다.
- 오류 처리: 오류는 `CX_AMDP_*` 예외로 ABAP에 전달되므로 호출부에서 `TRY ... CATCH cx_amdp_error INTO DATA(lx)`.

**(5)** ③, ⑤
- ③ AMDP 메서드용 테이블 함수는 다른 AMDP의 SQLScript에서만 쓸 수 있고 ABAP에서 직접 호출할 수 없다.
- ⑤ 본문은 전부 SQLScript이며 DB에서 실행된다. ABAP 처리는 호출 전후에 두고, 다른 AMDP는 `USING`에 적어 부른다.
- ② CDS 테이블 함수용 메서드는 CDS 정의에서 파라미터·결과 구조를 가져오고, 그 CDS 엔티티를 ABAP SQL로 SELECT해서 쓴다. ⑤의 함수 구현은 `BY DATABASE FUNCTION`이다.

</details>

---

### C-005. CDS 테이블 함수와 AMDP 프로시저 비교 [코드] ★★★
<!-- src: IS-036, RB-051, RB-052 -->
SQLScript로 구현하는 CDS 테이블 함수다.

```cds
@EndUserText.label: 'Revenue per carrier'
define table function ZTF_Revenue
  with parameters
    @Environment.systemField: #CLIENT
    p_clnt : abap.clnt
  returns {
    mandt   : abap.clnt;
    carrid  : s_carr_id;
    revenue : abap.dec( 17, 2 );
  }
  ____(1)____ zcl_tf_revenue=>get_revenue;
```

```abap
CLASS zcl_tf_revenue DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES ____(2)____.
    CLASS-METHODS get_revenue ____(3)____ ztf_revenue.
ENDCLASS.

CLASS zcl_tf_revenue IMPLEMENTATION.
  METHOD get_revenue ____(4)____ FOR HDB
                     LANGUAGE SQLSCRIPT
                     OPTIONS READ-ONLY
                     ____(5)____ sbook.
    RETURN SELECT mandt, carrid, SUM( loccuram ) AS revenue
             FROM sbook
            WHERE mandt = :p_clnt
            GROUP BY mandt, carrid;
  ENDMETHOD.
ENDCLASS.
```

(1) 빈칸 (1)~(5)를 채우시오.

(2) 이 테이블 함수를 ABAP에서 읽는 방법을 쓰고, 예시 SQLScript에 숨어 있는 업무 논리상의 문제를 쓰시오.

(3) AMDP·CDS 테이블 함수에서 클라이언트 처리가 문제가 되는 이유를 쓰고, 클래식 방식(AMDP와 테이블 함수 각각)과 ABAP Cloud 방식의 해결 방법을 쓰시오.

(4) AMDP 프로시저를 ABAP에서 직접 호출하는 방식과 CDS 테이블 함수를 쓰는 방식을 호출, 결과 개수, 재사용, 추가 SQL, 권한, 선언 관점으로 비교하는 표를 쓰시오.

(5) 다음 두 상황에 각각 어느 쪽이 알맞은지 쓰시오.
(가) 한 배치 프로그램에서 매출표와 오류표 두 결과를 한 번에 계산한다.
(나) 계산 결과를 다른 CDS 뷰에서 조인하고 OData로도 노출한다.

<details><summary>정답·해설</summary>

**(1)** (1) `implemented by method` (2) `if_amdp_marker_hdb` (3) `FOR TABLE FUNCTION` (4) `BY DATABASE FUNCTION` (5) `USING`
- 테이블 함수 = CDS 정의(시그니처) + AMDP 함수 구현(SQLScript). 메서드는 정적·PUBLIC(`CLASS-METHODS`)이고 파라미터를 직접 쓰지 않는다. 결과는 `RETURN SELECT ...`.

**(2)** ABAP SQL에서 일반 CDS 엔티티처럼 `SELECT FROM ztf_revenue( ... )`로 읽는다(`#CLIENT` 파라미터는 생략하면 현재 클라이언트가 들어감). 문제: 통화가 섞인 금액(`loccuram`)을 통화 키 없이 더한다. 실제로는 통화(`loccurkey`)도 결과·GROUP BY에 넣어야 한다. 실무 원칙: ABAP SQL이나 CDS 뷰로 표현할 수 없는 로직일 때만 테이블 함수/AMDP를 쓴다.

**(3)**
- 이유: ABAP SQL은 현재 클라이언트 조건을 자동으로 붙이지만 SQLScript는 Native SQL이라 자동 처리가 없다. 빠뜨리면 다른 클라이언트 데이터까지 읽는다.
- 클래식
  - AMDP: 클라이언트를 파라미터로 받거나 `SESSION_CONTEXT('CLIENT')`로 조건.
  - 테이블 함수: 위 예처럼 `#CLIENT` 파라미터를 받거나, `@ClientHandling.type: #CLIENT_DEPENDENT` + `@ClientHandling.algorithm: #SESSION_VARIABLE`을 지정하고 SQLScript에서 `SESSION_CONTEXT('CDS_CLIENT')`로 거른다. 결과 구조의 첫 필드를 클라이언트로 둔다.
- ABAP Cloud: AMDP 선언에 `AMDP OPTIONS READ-ONLY CDS SESSION CLIENT DEPENDENT`(또는 `CLIENT INDEPENDENT`)를 반드시 지정. `DEPENDENT`이면 `CDS_CLIENT` 세션 변수 기준으로 자동으로 거른다(client-safe). 테이블 함수도 `#CLIENT_DEPENDENT` + `#SESSION_VARIABLE`. ABAP Cloud는 `USING CLIENT` 같은 다른 클라이언트 접근을 아예 허용하지 않는다.

**(4)**

| 항목 | AMDP 프로시저 | CDS 테이블 함수 |
|---|---|---|
| 호출 | ABAP 메서드 호출 | ABAP SQL `SELECT FROM`, 다른 CDS의 데이터 소스 |
| 결과 | EXPORTING 여러 개 가능 | 결과 테이블 하나 |
| 재사용 | ABAP 코드에서만 | 다른 CDS에서 조인·association, OData 노출 |
| 추가 SQL | 결과를 받은 뒤 ABAP에서 처리 | 결과에 ABAP SQL WHERE·JOIN·집계를 더 걸 수 있음 |
| 권한 | 없음 | DCL 롤 정의 가능 |
| 선언 | 인스턴스·정적, 임의 가시성 | `CLASS-METHODS ... FOR TABLE FUNCTION`(정적, PUBLIC) |

**(5)** (가) AMDP 프로시저(여러 결과를 한 번에). (나) CDS 테이블 함수(데이터 모델의 일부로 재사용).

</details>

---

## CDS 뷰 엔티티·association·식·어노테이션

### C-006. CDS 뷰 엔티티의 기본 구조와 DDIC 기반 뷰·SE11 뷰 비교 [코드] ★★
<!-- src: IS-029, IS-030, RB-012, RB-045 -->
SFLIGHT 기반 인터페이스 뷰다. (`ZI_Carrier`는 CarrierId를 키로 갖는 항공사 뷰로 이미 있다.)

```cds
@AccessControl.authorizationCheck: #____(a)____
@EndUserText.label: 'Flight'
define ____(b)____ ZI_Flight
  as select from sflight
  association ____(c)____ to ZI_Carrier as _Carrier
    on ____(d)____.CarrierId = _Carrier.CarrierId
{
  key carrid   as CarrierId,
  key connid   as ConnectionId,
  key fldate   as FlightDate,
      @Semantics.amount.currencyCode: 'CurrencyCode'
      price    as Price,
      currency as CurrencyCode,
      seatsmax as SeatsMax,
      seatsocc as SeatsOccupied,

      ____(e)____
}
```

(1) 빈칸을 채우시오. (a) DCL 권한 검사를 수행 (c) 항공편마다 항공사는 정확히 1개(숫자 표기와 신규 자연어 표기 둘 다) (e) 소비자가 연관을 쓸 수 있게 공개

(2) `#CHECK`, `#NOT_REQUIRED`, `#MANDATORY`의 차이를 쓰고, cardinality `[1]`이 "정확히 1개"인지, 카디널리티를 생략한 `association to`의 기본값이 무엇인지 쓰시오.

(3) 이 뷰에서 `@Semantics.amount.currencyCode`를 지우면 어떻게 되는지, 공개한 연관의 ON 조건 필드에 대한 규칙, 연관 이름 관례를 쓰시오. ABAP SQL에서 이 뷰를 읽는 문장도 쓰시오.

(4) `define view entity`와 예전의 `define view`(DDIC 기반, `@AbapCatalog.sqlViewName`)의 차이를 4가지 쓰시오.

(5) CDS 뷰 엔티티에 대해 옳은 것을 고르시오.
① 뷰 엔티티도 `@AbapCatalog.sqlViewName`을 반드시 지정해야 한다.
② 입력 파라미터는 `$parameters.파라미터명`으로 참조한다.
③ 활성화하면 SE11에서 볼 수 있는 DDIC DB 뷰가 추가로 만들어진다.
④ 클라이언트 처리는 `@ClientHandling.type`으로 직접 지정해야 한다.
⑤ 신규 개발에는 DDIC 기반 CDS 뷰가 권장된다.

(6) CDS 뷰를 ABAP SQL로 테이블을 직접 읽는 것보다 선호하는 이유를 쓰고, SE11 데이터베이스 뷰(및 유지보수 뷰)와 CDS 뷰 엔티티를 조인, 식, 파라미터, 의미 정보, 권한, 재사용, 도구 관점으로 비교하시오.

<details><summary>정답·해설</summary>

**(1)** (a) `CHECK` (b) `view entity` (c) `[1..1]`(신규 문법 `association of many to exact one`) (d) `$projection` (e) `_Carrier`

**(2)** `#CHECK`: DCL 롤이 있으면 검사하고 없으면 문법 경고. `#NOT_REQUIRED`: 검사가 필요 없다는 표시(롤이 있으면 그래도 적용됨, C-012 참고). `#MANDATORY`: 롤이 반드시 있어야 함(없으면 실행 시 오류). 숫자 표기에서 최소값을 생략하면 0이라 `[1]`은 `[0..1]`과 같다(정확히 1개가 아님). 카디널리티를 생략하면 기본값도 `[0..1]`.

**(3)**
- 금액 필드(CURR)에 통화 참조가 없으면 뷰 엔티티는 활성화되지 않는다(DDIC 기반 뷰보다 엄격).
- 공개한 연관의 ON 조건에 쓰인 필드(CarrierId)는 요소 목록에 있어야 한다.
- 연관 이름은 관례상 `_`로 시작. 요소 목록에 쓰면 공개(expose)되어 다른 뷰·ABAP SQL 경로 식·OData 내비게이션에서 쓸 수 있다.
- `SELECT FROM zi_flight FIELDS * INTO TABLE @DATA(lt_flight).` — CDS 뷰도 ABAP SQL에서 일반 테이블처럼 읽는다.

**(4)**
1. 뷰 엔티티는 별도 DDIC SQL 뷰를 만들지 않는다(`sqlViewName` 불필요). 객체가 하나라 활성화가 빠르고 관리가 단순하다.
2. 클라이언트 처리가 자동이다(`@ClientHandling` 불필요).
3. 문법 검사가 더 엄격하다(금액·수량의 통화·단위 참조 필수, 키 요소는 맨 앞에 연속, 파라미터는 `$parameters`만).
4. 신규 기능(새 cardinality 문법, 확장된 식·함수 등)은 뷰 엔티티에만 추가된다. DDIC 기반 뷰는 obsolete이며 마이그레이션 도구로 뷰 엔티티로 바꿀 수 있다.

**(5)** ② — ① sqlViewName은 DDIC 기반 뷰에서만 ③ 별도 DDIC 뷰를 만들지 않음 ④ 자동이라 `@ClientHandling`을 쓰지 않음 ⑤ DDIC 기반 뷰는 obsolete. 뷰 엔티티에서는 DDIC 기반 뷰의 `:p_param` 형식을 쓸 수 없다.

**(6)**
- 선호 이유: 조인·계산·집계를 DB에 정의해 재사용(코드 푸시다운), association·어노테이션으로 의미 표현, DCL로 권한 검사를 선언적으로, RAP·Fiori Elements·OData의 기반 모델. ABAP Cloud에서는 SAP 표준 테이블 대신 릴리스된 CDS 뷰(예: `I_Customer`)로만 읽는다.

| 항목 | SE11 DB 뷰 | CDS 뷰 엔티티 |
|---|---|---|
| 조인 | 내부 조인만 | inner/left/right outer/cross join, association |
| 식 | 거의 없음 | CASE, CAST, 산술, 문자열·날짜 함수, 집계, UNION |
| 파라미터 | 없음 | `with parameters` |
| 의미 정보 | 없음 | 어노테이션(@Semantics, @UI, @Analytics 등) |
| 권한 | 없음 | DCL 행 단위 권한 |
| 재사용·노출 | 제한적 | 뷰 위에 뷰, OData/RAP/분석의 기반 |
| 도구 | SE11 | ADT(Eclipse) |

유지보수 뷰(SM30)는 여러 테이블을 묶어 데이터를 입력하는 화면용이고, CDS는 읽기 모델과 RAP BO의 기반이라 용도가 다르다. "SE11 뷰의 고급판"만으로는 부족하고 코드 푸시다운·의미 모델·권한·서비스 노출까지 언급해야 한다.

</details>

---

### C-007. association과 경로 식: 조인 종류와 결과 행 수 [코드] ★★★
<!-- src: IS-031, IS-032, IS-038, RB-021, RB-022, RB-023 -->
데이터: `zcarr`(항공사) = AA, LH, SQ 3행. `zconn`(노선) = (AA, 0017), (LH, 0400), (LH, 0402), (ZZ, 0001) 4행. ZZ는 `zcarr`에 없고, SQ는 노선이 없다.

```cds
define view entity ZI_Carrier as select from zcarr
  association [0..*] to ZI_Connection as _Connection
    on $projection.CarrierId = _Connection.CarrierId
{ key carrid as CarrierId, carrname as CarrierName, _Connection }

define view entity ZC_CarrConnA as select from ZI_Carrier
{ key CarrierId, _Connection.ConnectionId as ConnectionId }

define view entity ZC_CarrConnB as select from ZI_Carrier
{ key CarrierId, _Connection[inner].ConnectionId as ConnectionId }

define view entity ZI_ConnA as select from zconn as c
  inner join zcarr as r on c.carrid = r.carrid
{ key c.carrid, key c.connid, r.carrname as CarrierName }

define view entity ZI_ConnB as select from zconn
  association [0..1] to zcarr as _Carrier on $projection.carrid = _Carrier.carrid
{ key carrid, key connid, _Carrier.carrname as CarrierName }

define view entity ZI_ConnC as select from zconn
  association [0..1] to zcarr as _Carrier on $projection.carrid = _Carrier.carrid
{ key carrid, key connid, _Carrier[inner].carrname as CarrierName }
```

(`ZI_Connection`은 `zconn`을 CarrierId, ConnectionId로 노출하는 뷰다.)

(1) 다섯 뷰(`ZC_CarrConnA`, `ZC_CarrConnB`, `ZI_ConnA`, `ZI_ConnB`, `ZI_ConnC`)를 각각 `SELECT *`로 읽었을 때 결과 행 수를 쓰고, `ZC_CarrConnA`의 SQ 행 ConnectionId, `ZI_ConnB`의 ZZ 행 CarrierName 값(ABAP으로 받았을 때)을 쓰시오.

(2) `ZC_CarrConnA`에서 CarrierId가 키인데 LH가 두 행 나오는 이유와, CDS `key`에 대해 기억할 점을 쓰시오.

(3) association과 join의 차이를 "언제 조인되는가", "재사용", "기본 조인 종류" 관점에서 쓰시오. 생성된 SQL을 ADT에서 확인하는 방법도 쓰시오.

(4) 옳지 **않은** 것을 고르시오.
① association은 경로 식으로 사용될 때만 SQL 조인으로 변환된다.
② `[0..*]`는 원본 한 행에 대상이 0개 이상 여러 개일 수 있다는 뜻이다.
③ 공개한 association의 ON 조건에 쓰인 원본 필드는 요소 목록에도 있어야 한다.
④ `[0..1]`로 선언했는데 실제 대상 행이 2개 있으면 DB가 오류를 낸다.
⑤ `association of many to one ...` 같은 자연어 표기도 쓸 수 있다.

(5) `ZI_Connection`이 `_Carrier`(scarr, `[1..1]`)를 노출만 하고 대상 필드는 넣지 않았다. ABAP SQL에서 항공사 이름을 함께 읽도록 빈칸을 채우고, 이때 조인이 언제 실행되는지, ABAP SQL과 CDS 안에서 경로 식 표기가 어떻게 다른지 쓰시오.

```abap
SELECT FROM zi_connection
  FIELDS carrid, connid, ____(가)____ AS carrier_name
  WHERE carrid = 'LH'
  INTO TABLE @DATA(lt_conn).
```

(6) 노선 뷰에서 to-many association `_Flight`(sflight, `[0..*]`)로 오늘 출발 항공편(노선당 하루 1편)의 가격을 가져오면서 "결과 집합의 카디널리티가 바뀔 수 있다"는 경고를 없애려 한다. 빈칸을 채우고, 조인 종류까지 지정할 때의 문법과 사용자 시간대 날짜가 필요할 때의 변수를 쓰시오.

```cds
_Flight[ ____(나)____ fldate = $session.____(다)____ ].price as TodayPrice
```

<details><summary>정답·해설</summary>

**(1)**

| 뷰 | 행 수 | 비고 |
|---|---|---|
| ZC_CarrConnA | 4 | AA 1 + LH 2 + SQ 1(짝 없음). SQ의 ConnectionId는 NULL → ABAP에서 초기값(`0000`) |
| ZC_CarrConnB | 3 | `[inner]`라 짝 없는 SQ가 빠짐 |
| ZI_ConnA | 3 | INNER JOIN이라 ZZ 빠짐 |
| ZI_ConnB | 4 | 경로 식은 LEFT OUTER JOIN. ZZ의 CarrierName은 NULL → 초기값(공백) |
| ZI_ConnC | 3 | `[inner]` → ZZ 빠짐 |

**(2)** to-many 경로를 요소 목록에 쓰면 원본 행이 대상 수만큼 늘어난다. CDS의 `key`는 DB가 유일성을 강제하지 않는 선언일 뿐이다. 그래서 to-many 경로는 집계나 필터와 함께 쓴다.

**(3)**
- join은 뷰가 실행될 때마다 항상 수행된다. association은 관계를 정의만 하고, 경로 식(`_Carrier.CarrierName`)으로 실제로 쓸 때만 조인이 생긴다(join on demand). 쓰지 않으면 비용이 없다.
- association은 공개해 소비자 뷰, ABAP SQL(`\_Carrier-carrname`), OData 내비게이션(`$expand`)에서 재사용한다. join은 그 뷰 안에서만.
- 요소 목록의 경로 식은 기본 **LEFT OUTER JOIN**, `[inner]`면 INNER JOIN. 경로에 필터(`_Text[Language = $session.system_language]`)도 붙일 수 있다.
- cardinality는 대상 행 수에 대한 선언으로 DB가 강제하지 않으며, 최적화와 문법 검사(to-many 경고)에 쓰인다.
- ADT의 "Show SQL CREATE Statement"로 생성된 SQL을 본다.

**(4)** ④ — cardinality는 선언일 뿐 DB가 검사하지 않는다. 실제와 다르면 오류 없이 행이 늘거나 최적화 결과가 틀어질 수 있으므로 정확히 선언한다.

**(5)** (가) `\_Carrier-carrname`. 노출만 한 association은 뷰 자체를 읽을 때는 조인하지 않고, 이 SELECT처럼 소비자가 association 필드를 요청할 때만 조인된다. ABAP SQL 경로 식은 `\`로 시작하고 association과 필드 사이에 `-`, CDS 안에서는 `_Carrier.carrname`처럼 점. 노출하지 않은 association은 바깥에서 쓸 수 없다.

**(6)** (나) `1:` (다) `system_date`. `[1: 조건]`은 "이 필터를 걸면 대상이 최대 한 건"이라는 선언이다. 조인 종류도 쓰면 `[1: left outer where fldate = ...]`처럼 `where`가 필요하다. 사용자 시간대 기준은 `$session.user_date`.

</details>

---

### C-008. CDS 식·내장 함수·CAST·리터럴 결과 [코드] ★★
<!-- src: RB-015, RB-016, RB-017, RB-018, RB-019, RB-020, MX-046 -->
`/dmo/flight`에 아래 세 행만 있다(carrier_id는 CHAR 3).

| carrier_id | connection_id | flight_date | seats_max | seats_occupied | currency_code | plane_type_id |
|---|---|---|---|---|---|---|
| AA | 0017 | 20261101 | 200 | 190 | USD | B747 |
| LH | 0400 | 20261102 | 300 | 0 | EUR | A380 |
| UA | 0058 | 20261103 | 100 | 60 | USD | A320 |

```cds
define view entity ZMX_I_Load as select from /dmo/flight
{
  key carrier_id    as Carrier,
  key connection_id as Connection,
  key flight_date   as FlightDate,
      seats_max - seats_occupied as FreeSeats,
      case
        when seats_occupied = 0                     then 'EMPTY'
        when seats_occupied * 100 >= seats_max * 90 then 'FULL'
        when seats_occupied * 100 >= seats_max * 50 then 'HALF'
        else 'LOW'
      end as LoadClass,
      case
        when seats_max <= 150 then 'S'
        when seats_max <  300 then 'M'
      end as SizeCat,
      concat( carrier_id, connection_id )        as FlightCode,
      division( seats_occupied * 100, seats_max, 1 ) as LoadPct
}
```

(1) 행마다 FreeSeats, LoadClass, SizeCat(ABAP으로 받았을 때), FlightCode, LoadPct를 쓰시오. CASE에 `ELSE`가 없을 때의 결과와 그것을 다른 값으로 바꾸는 방법 두 가지를 쓰시오.

(2) LH 행(`carrid = 'LH'`, `currency = 'EUR'`, `planetype = 'A380'`)에 다음 문자열 함수를 적용한 값을 쓰시오.

```cds
concat( carrid, currency )               as f1,
concat_with_space( carrid, currency, 2 ) as f2,
left( currency, 2 ) as f3,  right( currency, 1 ) as f4,
lpad( carrid, 5, '0' ) as f5,  substring( planetype, 2, 2 ) as f6,
length( planetype ) as f7,  instr( planetype, '8' ) as f8,
replace( currency, 'E', 'X' ) as f9,  ltrim( planetype, 'A' ) as f10,
lower( carrid ) as f11
```

(3) 숫자·날짜 함수 값을 쓰시오.

```cds
div( 25, 4 ) as n1,  mod( 25, 4 ) as n2,  division( 10, 4, 2 ) as n3,
round( abap.dec'1.345', 2 ) as n4,  ceil( abap.dec'3.2' ) as n5,
floor( abap.dec'-3.2' ) as n6,  abs( abap.int4'-7' ) as n7,
dats_days_between( abap.dats'20240201', abap.dats'20240301' ) as d1,
dats_add_days( abap.dats'20241230', 5, 'INITIAL' )           as d2,
dats_add_months( abap.dats'20240115', 2, 'INITIAL' )         as d3,
dats_is_valid( abap.dats'20230229' )                          as d4
```

(4) 정수끼리 `/`를 쓰지 않고 `division`을 쓴 이유, `concat`이 CHAR 3의 끝 공백을 어떻게 다루는지, 날짜 함수의 세 번째 인자 `'INITIAL'`의 의미를 쓰시오.

(5) CDS 리터럴에 대해 옳은 것을 고르고 나머지가 틀린 이유를 쓰시오.
① 정수 리터럴은 값과 상관없이 항상 INT4다.
② 숫자로만 된 문자 리터럴(`'123'`)은 CDS에서 NUMC로 취급된다.
③ `1.5` 같은 소수 리터럴은 DEC다.
④ `abap.dec'1.5'` 같은 타입 지정 리터럴은 쓸 수 없다.

(6) CDS 뷰 엔티티에서 `cast`를 쓸 때의 규칙을 4가지 이상 쓰시오.

<details><summary>정답·해설</summary>

**(1)**

| Carrier | FreeSeats | LoadClass | SizeCat | FlightCode | LoadPct |
|---|---|---|---|---|---|
| AA | 10 | FULL | M | AA0017 | 95.0 |
| LH | 300 | EMPTY | 초기값(공백), DB에서는 NULL | LH0400 | 0.0 |
| UA | 40 | HALF | S | UA0058 | 60.0 |

- AA: 19000 ≥ 18000 → FULL. 200 ≤ 150 거짓, 200 < 300 참 → M. 19000/200 = 95.0.
- LH: 첫 WHEN(점유 0)이 먼저 맞아 EMPTY(CASE는 위에서부터 처음 맞는 WHEN 하나만). 300은 `<= 150`도 `< 300`도 거짓 → ELSE가 없어 NULL.
- UA: 6000 ≥ 9000 거짓, 6000 ≥ 5000 참 → HALF.
- ELSE가 없으면 결과는 NULL이고, ABAP SQL로 받으면 그 타입의 초기값이 된다. 바꾸려면 `else 'L'`을 쓰거나 `coalesce( 식, 'L' )`.

**(2)**

| f1 | f2 | f3 | f4 | f5 | f6 | f7 | f8 | f9 | f10 | f11 |
|---|---|---|---|---|---|---|---|---|---|---|
| `LHEUR` | `LH  EUR`(공백 2) | `EU` | `R` | `000LH` | `38` | `4` | `3` | `XUR` | `380` | `lh` |

`concat_with_space`의 세 번째 인자는 공백 수, `lpad(arg, len, src)`는 길이 len이 되도록 왼쪽을 src로 채움, `substring(arg, pos, len)`은 1부터, `instr`는 처음 위치(없으면 0), `ltrim(arg, char)`은 앞쪽의 해당 문자를 모두 지움.

**(3)** n1 = 6, n2 = 1, n3 = 2.50, n4 = 1.35, n5 = 4, n6 = -4, n7 = 7, d1 = 29, d2 = 20250104, d3 = 20240315, d4 = 0
- `div`는 정수 몫, `mod`는 나머지, `division(a,b,d)`는 소수 d자리로 반올림한 나눗셈.
- `round(1.345, 2)`: DEC는 정확한 십진수라 셋째 자리 5에서 올림 → 1.35. `ceil`은 그 값 이상 최소 정수, `floor`는 이하 최대 정수(-3.2 → -4).
- 2024년은 윤년이라 2/1~3/1은 29일. 12/30 + 5일 = 2025-01-04. 1/15 + 2개월 = 3/15. 2023-02-29는 없는 날짜라 `dats_is_valid` = 0(유효하면 1).

**(4)** CDS에서 정수끼리 나눗셈 결과의 정밀도를 정하기 위해 `division`(또는 CAST)을 쓴다. `concat`은 인자의 끝 공백을 무시해 `AA␣`+`0017` → `AA0017`(공백을 넣으려면 `concat_with_space`). `'INITIAL'`은 오류 시 처리 방식(on_error) 인자이며 그 위치에는 리터럴만 쓸 수 있다.

**(5)** ② — ① CDS는 값이 들어가는 가장 짧은 정수 타입을 고른다(255는 INT1, 256은 INT2). ABAP SQL은 정수 리터럴을 모두 I(INT4)로 본다. ② ABAP SQL에서는 C지만 CDS에서는 숫자만 있으면 NUMC. ③ 소수점 리터럴은 FLTP(ABAP SQL에는 소수 리터럴 자체가 없음). ④ `abap.int4'12345'`, `abap.dats'20240101'`, `abap.dec'0.9'` 같은 타입 리터럴을 쓸 수 있고 타입이 모호할 때 권장된다.

**(6)**
1. 내장 타입은 `abap.` 접두어: `cast( price as abap.dec(15,2) )`, `cast( x as abap.char(10) )`.
2. 데이터 엘리먼트로 바꾸면 필드 라벨 같은 의미 정보도 따라온다: `cast( carrid as /dmo/carrier_id )`.
3. 기술 타입이 안 바뀌는 CAST는 경고 → 의도적이면 `preserving type`.
4. 모든 조합이 되지는 않는다. FLTP → DEC는 `fltp_to_dec( ... as abap.dec(10,2) )` 같은 전용 함수.
5. 같은 뷰에서 앞서 정의한 요소를 다시 쓰려면 `$projection.요소명`. CURR/QUAN으로 바꾸면 통화·단위 참조 어노테이션이 필요.
CASE 분기, UNION branch의 타입 맞추기, 나눗셈 정밀도 지정에 CAST를 쓴다.

</details>

---

### C-009. 집계·UNION 뷰: 결과 쓰기, 활성화 오류, 직접 작성 [코드] ★★★
<!-- src: RB-027, RB-028, IS-040, IS-039, RB-029 -->
`zflight` 데이터와 집계 뷰다.

| carrid | connid | planetype | seatsocc |
|---|---|---|---|
| LH | 0400 | A340 | 300 |
| LH | 0400 | A340 | 250 |
| LH | 0402 | A380 | 400 |
| AA | 0017 | B747 | 200 |
| AA | 0017 | B747 | 100 |

```cds
define view entity ZI_FlightStat as select from zflight
{
  key carrid,
      count(*)                    as cnt,
      count( distinct connid )    as conn_cnt,
      count( distinct planetype ) as type_cnt,
      sum( seatsocc )             as occ_sum,
      max( seatsocc )             as occ_max,
      min( seatsocc )             as occ_min
}
group by carrid
```

(1) 뷰를 조회한 결과를 표로 쓰시오. 결과 행 순서에 대해서도 한 줄 쓰시오.

(2) 다음 뷰는 활성화되지 않는다. 잘못된 곳을 모두 찾아 고치시오(최소 5곳).

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Flights per carrier'
define view entity ZI_FlightAgg
  as select from sflight
{
      carrid,
  key connid,
      currency,
      sum( paymentsum ),
      sum( price ) as TotalPrice,
      count( * )   as FlightCount
}
group by carrid
order by carrid
```

(3) (2)에서 통화 요소를 group by에 넣지 않으면 생기는 논리 문제를 쓰시오.

(4) SBOOK에서 취소되지 않은(cancelled가 `'X'`가 아닌) 예약을 항공사·노선·통화별로 집계하는 뷰 `ZI_BookingSummary`를 작성하시오. 요소: CarrierId, ConnectionId, CurrencyCode(키 3개), 예약 건수 BookingCount, 현지 통화 금액 합계 TotalAmount(`loccuram`, 통화 `loccurkey`). 권한 검사는 필요 없다고 표시한다.

(5) `zfav_web`(LH, AA)과 `zfav_app`(AA, SQ)이 있다. 두 뷰의 결과 행 수와 값을 쓰고, CDS UNION 규칙 두 가지와 성능상 고려점을 쓰시오.

```cds
define view entity ZI_FavU as
  select from zfav_web { key carrid } union     select from zfav_app { key carrid }
define view entity ZI_FavUA as
  select from zfav_web { key carrid } union all select from zfav_app { key carrid }
```

<details><summary>정답·해설</summary>

**(1)**

| carrid | cnt | conn_cnt | type_cnt | occ_sum | occ_max | occ_min |
|---|---|---|---|---|---|---|
| AA | 2 | 1 | 1 | 300 | 200 | 100 |
| LH | 3 | 2 | 2 | 950 | 400 | 250 |

`count(*)`는 행 수, `count( distinct x )`는 서로 다른 값의 수. 집계식에는 별칭이 반드시 있고, 집계하지 않은 요소는 모두 `group by`에. ORDER BY가 없으므로 행 순서는 정해져 있지 않다.

**(2)**
1. 키 요소는 맨 앞에 연속 → `key carrid, key connid, key currency` 순서.
2. `connid`가 집계되지 않는데 `group by`에 없음 → `group by carrid, connid, currency`(또는 connid를 뺀다).
3. `sum( paymentsum )`에 별칭 없음 → `as TotalPayment`.
4. 금액(CURR) 합계에 통화 참조 없음 → 각 `sum` 위에 `@Semantics.amount.currencyCode: 'currency'`(currency는 요소 목록과 group by에).
5. CDS 뷰에는 `order by`를 쓸 수 없음 → 삭제, 정렬은 소비 측 ABAP SQL `ORDER BY`나 UI에서.

```cds
define view entity ZI_FlightAgg
  as select from sflight
{
  key carrid,
  key connid,
  key currency,
      @Semantics.amount.currencyCode: 'currency'
      sum( paymentsum ) as TotalPayment,
      @Semantics.amount.currencyCode: 'currency'
      sum( price )      as TotalPrice,
      count( * )        as FlightCount
}
group by carrid, connid, currency
```

**(3)** 서로 다른 통화 금액이 한 합계로 더해지고, 통화 참조도 할 수 없어 활성화 오류가 난다. 키 순서, group by 완전성, 금액·수량의 통화·단위 참조는 시험에 자주 나오는 활성화 오류다.

**(4)**

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Booking summary'
define view entity ZI_BookingSummary
  as select from sbook
{
  key carrid    as CarrierId,
  key connid    as ConnectionId,
  key loccurkey as CurrencyCode,
      count( * ) as BookingCount,
      @Semantics.amount.currencyCode: 'CurrencyCode'
      sum( loccuram ) as TotalAmount
}
where cancelled <> 'X'
group by carrid, connid, loccurkey
```

채점 포인트: `define view entity`, 키 요소 맨 앞, 집계하지 않는 요소 모두 `group by`, 금액 합계에 통화 참조, `where`는 요소 목록 `}` 뒤(group by 앞).

**(5)** ZI_FavU: 3행(LH, AA, SQ — 중복 AA 제거), ZI_FavUA: 4행(LH, AA, AA, SQ). 규칙: 각 SELECT의 요소 수가 같고, 같은 위치 요소의 타입이 맞아야 하며(필요하면 CAST), 키 요소도 각 branch에서 같은 위치·같은 방식. `union`은 중복 제거를 위해 정렬·비교를 하므로 중복이 없다고 확신하면 `union all`이 빠르다. 행 순서는 보장되지 않고, 뷰 엔티티에서는 `intersect`, `except`도 쓸 수 있다.

</details>

---

### C-010. CDS 어노테이션 체계·메타데이터 확장·전파·VDM [개념] ★★
<!-- src: IS-034, RB-013, RB-042, RB-043, RB-044, MX-044, RB-014, MX-043 -->
(1) 요구사항에 맞는 어노테이션을 쓰시오.

| 번호 | 요구사항 | 어노테이션 |
|---|---|---|
| 1 | 엔티티·요소에 번역 가능한 라벨 | |
| 2 | DCL 롤이 없으면 문법 경고 | `@AccessControl.authorizationCheck: ___` |
| 3 | 금액 요소를 통화 키 요소와 연결 | |
| 4 | DDLX에서 어노테이션 추가 허용 | |
| 5 | 키 요소의 설명 텍스트 요소 지정 | `@ObjectModel.___: ['CarrierName']` |
| 6 | 검색창 자유 검색 대상 요소(엔티티에 필요한 것도) | |
| 7 | 입력 필드에 값 도움말 | `@Consumption.___` |
| 8 | 분석 측정값의 기본 집계 | `@Aggregation.default: ___` |
| 9 | VDM 기본(basic) 뷰 표시 | `@VDM.viewType: ___` |
| 10 | 파라미터 기본값을 시스템 날짜로 | `@Environment.systemField: ___` |
| 11 | 데이터 양 범주(성능 특성) | `@ObjectModel.usageType.___: #L` |

(2) 어노테이션을 ABAP 런타임·사전이 해석하는 것(코어)과 프레임워크(UI, OData, 분석 등)가 해석하는 것으로 나누어 대표 예를 각각 4개 이상 쓰고, 이름공간 `@AbapCatalog`, `@ObjectModel`, `@Semantics`, `@Consumption`, `@Metadata`, `@VDM`의 역할을 한 줄씩 쓰시오. `usageType`의 세 속성도 쓰시오.

(3) 항공사 코드 옆에 이름을 표시하고 검색창에서 이름 일부(오타 허용)로 찾을 수 있게 하려 한다. 빈칸을 채우고, 언어별 텍스트가 별도 뷰에 있을 때의 다른 방법을 쓰시오.

```cds
@Search.____(가)____: true
define view entity ZI_Carrier as select from /dmo/carrier
{
      @ObjectModel.____(나)____: ['CarrierName']
      @Search.defaultSearchElement: true
  key carrier_id as CarrierID,
      @Semantics.____(다)____: true
      @Search.defaultSearchElement: true
      @Search.____(라)____: 0.8
      name       as CarrierName
}
// 다국어 텍스트 뷰에서 로그온 언어의 설명
_StatusText[1: Language = $session.____(마)____].Description as StatusText
```

(4) 메타데이터 확장(`annotate entity ... with`)을 쓰는 이유 3가지와 전제 조건을 쓰시오. `ZC_Travel`의 같은 요소에 `@UI.lineItem.position`을 `#CORE` DDLX는 10, `#CUSTOMER` DDLX는 50, 뷰 자체는 30으로 정의했다면 화면에 적용되는 값과 전체 우선순위를 쓰시오.

(5) 어노테이션 전파(propagation) 방식(데이터 엘리먼트 라벨, 요소 어노테이션, 엔티티 어노테이션)을 설명하고, 전파를 막는 방법과 최종 값을 확인하는 방법을 쓰시오.

(6) 옳지 **않은** 것을 고르시오.
① `@Semantics.amount.currencyCode`는 뷰 엔티티의 CURR 요소에 필수다.
② `@ObjectModel.text.element`는 키 요소의 설명 텍스트 요소를 지정한다.
③ `@Consumption.valueHelpDefinition`은 값 도움말을 정의한다.
④ `@AccessControl.authorizationCheck: #NOT_REQUIRED`면 DCL 롤이 있어도 접근 제어가 항상 꺼진다.
⑤ `@UI.lineItem: [{ position: 10 }]`은 리스트 테이블 열을 정의한다.

(7) VDM의 basic, composite, consumption 뷰와 RAP용 `R_` 뷰의 역할·이름 접두어를 쓰고(그 밖의 `P_`, `E_`, `A_`도), 계층 간 참조 규칙, 커스텀 개발에서 VDM 뷰를 재사용할 때 확인할 점을 쓰시오. "CDS 뷰 종류"를 물으면 무엇과 무엇을 구분해 답해야 하는지도 쓰시오.

<details><summary>정답·해설</summary>

**(1)** 1 `@EndUserText.label: 'Travel'` 2 `#CHECK` 3 `@Semantics.amount.currencyCode: 'CurrencyCode'` 4 `@Metadata.allowExtensions: true` 5 `text.element` 6 요소에 `@Search.defaultSearchElement: true`, 엔티티에 `@Search.searchable: true` 7 `valueHelpDefinition` 8 `#SUM` 9 `#BASIC` 10 `#SYSTEM_DATE` 11 `sizeCategory`

**(2)**
- 코어: `@AccessControl.authorizationCheck`, `@EndUserText.label`, `@AbapCatalog.*`(확장성, 버퍼링, DDIC 기반 뷰의 SQL 뷰 이름), `@Semantics.amount.currencyCode`/`@Semantics.quantity.unitOfMeasure`, `@Metadata.allowExtensions`, `@Environment.systemField`.
- 프레임워크: `@UI.lineItem/selectionField/facet/headerInfo`(Fiori Elements 배치), `@ObjectModel.*`(텍스트, 값 도움말, 데이터 카테고리), `@Search.searchable`, `@Consumption.valueHelpDefinition`, `@Analytics.*`, `@OData.*`.

| 이름공간 | 역할 |
|---|---|
| `@AbapCatalog` | 사전 기술 설정(DDIC 뷰 이름, 확장 범주, 버퍼링) |
| `@ObjectModel` | 모델 의미(텍스트, 외래 키 association, 사용 유형, 쿼리 구현 클래스, 가상 요소) |
| `@Semantics` | 요소 의미(금액, 수량, 텍스트, 사용자·시간 스탬프) |
| `@Consumption` | 소비 측 동작(값 도움말, 필터, 숨김) |
| `@Metadata` | 메타데이터 확장 허용, 계층(layer), 전파 무시 |
| `@VDM` | 가상 데이터 모델 계층 |

그 밖에 `@AccessControl`(DCL), `@EndUserText`(라벨), `@Analytics`/`@Aggregation`(분석), `@UI`(화면), `@Search`(검색). `usageType`: `serviceQuality`(#A~#D, #X, #P), `sizeCategory`(#S~#XXL), `dataClass`(#MASTER, #TRANSACTIONAL 등).

**(3)** (가) `searchable` (나) `text.element` (다) `text` (라) `fuzzinessThreshold` (마) `system_language`. `fuzzinessThreshold`(0~1)는 1에 가까울수록 정확히 일치해야 한다. 텍스트 요소를 지정하면 Fiori Elements가 "코드 (이름)"처럼 표시한다. 텍스트가 언어 의존 뷰에 있으면 `@ObjectModel.text.association: '_Text'`와 텍스트 뷰의 `@ObjectModel.dataCategory: #TEXT`를 쓴다.

**(4)**
- 이유: 양이 많고 자주 바뀌는 `@UI` 어노테이션을 데이터 모델과 분리해 뷰를 깔끔하게 유지, 데이터 모델을 다시 활성화하지 않고 UI만 변경, `@Metadata.layer`(#CORE, #LOCALIZATION, #INDUSTRY, #PARTNER, #CUSTOMER)로 계층별 덮어쓰기.
- 전제: 원본 뷰에 `@Metadata.allowExtensions: true`, DDLX에는 `@Metadata.layer` 필수.
- 적용 값: **50**. 우선순위: DDLX(#CUSTOMER > #PARTNER > #INDUSTRY > #LOCALIZATION > #CORE) > 뷰 자체 어노테이션 > 아래 뷰·데이터 엘리먼트에서 전파된 어노테이션.

**(5)** 데이터 엘리먼트의 필드 라벨은 그 요소를 쓰는 CDS 요소 라벨로 쓰인다. 요소 어노테이션(`@Semantics`, `@ObjectModel.text.element`, `@Consumption.valueHelpDefinition` 등)은 그 요소를 그대로 가져다 쓰는 위 뷰(프로젝션 등)로 전파되고, 엔티티(헤더) 어노테이션은 전파되지 않는다. 위 뷰에서 다시 쓰면 덮어쓴다. 막으려면 `@Metadata.ignorePropagatedAnnotations: true`. 최종 값은 ADT "Active Annotations" 보기로 확인한다. 프로젝션에서 값 도움말을 다시 정의하지 않아도 동작하거나, 원치 않는 어노테이션이 따라오는 현상의 원인이다.

**(6)** ④ — `#NOT_REQUIRED`는 "롤이 없어도 경고하지 않는다"일 뿐 롤이 있으면 적용된다. 롤이 있어도 끄는 값은 `#NOT_ALLOWED`, 코드에서 건너뛰려면 `WITH PRIVILEGED ACCESS`.

**(7)**

| 계층 | 이름 예 | 역할 |
|---|---|---|
| Basic(interface) `#BASIC` | `I_Product`, `I_Customer`, `I_Currency` | DB 테이블 바로 위. 필드명을 의미 있는 CamelCase로, association으로 관계 정의, 중복 없는 기본 데이터 |
| Composite(interface) `#COMPOSITE` | `I_...` | 여러 basic 뷰를 조합·계산한 재사용 모델(예: 분석 큐브) |
| Consumption `#CONSUMPTION` | `C_...` | 특정 앱·분석·API용. UI·검색·값 도움말 어노테이션, 파라미터 |
| RAP 트랜잭션 | `R_...` | RAP BO의 기반 재사용 뷰(restricted reuse) |

그 밖에 `P_`(내부 private), `E_`(확장 include), `A_`(원격 API). 아래 계층은 위 계층을 참조하지 않는다. 재사용 시 확인: **released 여부(C1 계약, Use System-Internally / Use in Cloud Development)** — 공개되지 않은 뷰는 업그레이드 때 바뀔 수 있고 ABAP Cloud에서는 쓸 수 없다. DCL 유무, 필요한 association·텍스트·통화 어노테이션, 확장성도 확인한다. 공개된 basic/composite 위에 커스텀 뷰를 쌓으면 업그레이드에 안전하다. "CDS 뷰 종류"는 VDM 계층(basic/composite/consumption)과 기술적 종류(뷰 엔티티, 프로젝션, 추상·커스텀 엔티티, 테이블 함수 등, C-013)를 구분해 답한다.

</details>

---

## CDS 고급: 파라미터·DCL·특수 엔티티·계층·분석·확장

### C-011. 파라미터 뷰·세션 변수·$projection [코드] ★★
<!-- src: IS-033, RB-025, RB-026, MX-045, MX-047 -->
기준일 이후 항공편을 항공사 이름과 함께 보여 주는 파라미터 뷰와 그것을 읽는 코드다.

```cds
@AccessControl.authorizationCheck: #CHECK
@EndUserText.label: 'Flights from date'
define view entity ZI_FlightsFrom
  ____(1)____
    ____(2)____
    p_date : abap.dats
  as select from /dmo/flight as f
  association [1..1] to /DMO/I_Carrier as _Carrier
    on $projection.CarrierId = _Carrier.AirlineID
{
  key f.carrier_id    as CarrierId,
  key f.connection_id as ConnectionId,
  key f.flight_date   as FlightDate,
      @Semantics.amount.currencyCode: 'CurrencyCode'
      f.price         as Price,
      f.currency_code as CurrencyCode,
      _Carrier.Name   as CarrierName,
      _Carrier
}
where f.flight_date >= ____(3)____.p_date
```

```abap
" Standard ABAP
SELECT * FROM zi_flightsfrom( ____(4)____ ) INTO TABLE @DATA(lt_a).   " 변수 lv_date 전달
SELECT * FROM zi_flightsfrom INTO TABLE @DATA(lt_b).                    " 파라미터 생략
" ABAP Cloud
DATA(lv_today) = ____(5)____=>get_system_date( ).
SELECT FROM zi_flightsfrom( p_date = @lv_today ) FIELDS * INTO TABLE @DATA(lt_c).
```

(1) 빈칸 (1)~(5)를 채우시오. (2)는 파라미터를 생략하면 시스템 날짜가 들어가게 하는 어노테이션이다.

(2) `lt_b`의 SELECT가 문법상 가능한 이유를 쓰고, (2)의 어노테이션에 쓸 수 있는 다른 값 세 가지를 쓰시오. 이 파라미터 뷰를 다른 CDS 뷰에서 데이터 소스로 쓸 때의 규칙도 쓰시오.

(3) 뷰 엔티티에서 파라미터를 참조하는 문법과 DDIC 기반 뷰 문법의 차이를 쓰고, 파라미터를 쓸 수 있는 위치를 쓰시오. ON 조건의 `$projection.CarrierId`가 가리키는 것도 쓰시오.

(4) `_Carrier.Name`을 요소로 꺼낸 것과 `_Carrier`를 요소 목록에 넣은 것은 각각 어떤 효과가 있는지 쓰시오.

(5) 뷰 엔티티에서 쓸 수 있는 `$session` 변수를 5가지 이상 쓰고, `system_date`와 `user_date`의 차이를 쓰시오. 세션 변수의 대표적인 사용 예 두 가지도 쓰시오.

(6) `where created_by = $session.user`로 사용자 데이터를 거르는 것이 권한 검사를 대신할 수 없는 이유를 쓰시오.

(7) 옳지 **않은** 것을 고르시오.
① `$session.system_date`는 ABAP 시스템 날짜에 해당한다.
② `$session.client`는 현재 클라이언트를 돌려준다.
③ `$parameters.p_x`는 select 목록·WHERE·ON 조건 등에서 쓸 수 있다.
④ `$projection.Alias`는 같은 뷰 select 목록의 별칭 요소를 참조한다.
⑤ `$session.user`는 사용자의 로그온 언어를 돌려준다.

<details><summary>정답·해설</summary>

**(1)** (1) `with parameters` (2) `@Environment.systemField: #SYSTEM_DATE` (3) `$parameters` (4) `p_date = @lv_date` (5) `cl_abap_context_info`

**(2)** `@Environment.systemField`가 붙은 파라미터는 ABAP SQL에서 생략할 수 있고 시스템 값이 자동으로 넘어간다(어노테이션이 없으면 모든 파라미터를 넘겨야 한다). 다른 값: `#SYSTEM_LANGUAGE`, `#USER`, `#CLIENT`(그 밖에 `#SYSTEM_TIME`). 다른 CDS에서 쓸 때는 파라미터를 명시적으로 넘겨야 한다(자동 전달 없음). ABAP for Cloud Development에서는 `sy-datum`을 쓸 수 없어 `cl_abap_context_info=>get_system_date( )`를 쓴다. ABAP SQL에서 여러 파라미터는 `엔티티( p1 = ..., p2 = ... )`처럼 쉼표로 구분한다.

**(3)** 뷰 엔티티는 `$parameters.이름`만 쓴다. DDIC 기반 뷰의 `:이름` 형식은 뷰 엔티티에서 쓸 수 없다. 파라미터는 select 목록, WHERE, ON 조건, 경로 필터 등에서 쓸 수 있다. `$projection.CarrierId`는 이 뷰의 select 목록에서 정의한 별칭 요소를 가리킨다(원본 필드 `f.carrier_id`를 직접 써도 된다).

**(4)** `_Carrier.Name`처럼 경로로 필드를 꺼내면 to-one association이 LEFT OUTER JOIN이 된다. association 이름 자체를 넣으면 노출되어 이 뷰를 쓰는 쪽(다른 CDS, ABAP SQL `\_Carrier-...`, OData `$expand`)이 따라갈 수 있다.

**(5)** `$session.user`(사용자명), `$session.client`, `$session.system_language`(로그온 언어), `$session.system_date`(서버 날짜), `$session.user_timezone`, `$session.user_date`(사용자 시간대 기준 날짜). `system_date`는 서버 시스템 시간대, `user_date`는 사용자 시간대 기준이라 자정 전후로 다를 수 있다. 사용 예: 텍스트 association 언어 필터(`_Text[1: Language = $session.system_language]`), 날짜 필터, DCL 조건.

**(6)** 그 조건은 그 뷰를 쓸 때의 데이터 범위 제한일 뿐이다. 다른 뷰나 ABAP SQL로 같은 테이블을 읽으면 다 보인다. 행 단위 권한은 DCL(`define role`)로 정의해야 하고, DCL은 그 엔티티를 직접 읽는 모든 ABAP SQL에 자동 적용된다.

**(7)** ⑤ — `$session.user`는 사용자 이름(sy-uname에 해당). 로그온 언어는 `$session.system_language`.

</details>

---

### C-012. DCL 접근 제어: 롤 작성과 보이는 행 추적 [코드] ★★★
<!-- src: IS-035, RB-037, RB-038, RB-039, MX-048 -->
`ZI_Travel`(`@AccessControl.authorizationCheck: #CHECK`)에 다음 데이터와 두 롤이 있다. 사용자 USERB는 권한 객체 `ZAGENCY`에서 `ZAGENCY = 070001, ACTVT = 03` 한 세트와 `ZAGENCY = 070002, ACTVT = 02` 한 세트를 가지고 있다.

| TravelID | AgencyID | Status | CreatedBy | Price |
|---|---|---|---|---|
| T1 | 070001 | O | USERA | 500 |
| T2 | 070002 | A | USERB | 80 |
| T3 | 070003 | O | USERB | 300 |
| T4 | 070001 | X | USERC | 900 |
| T5 | 070004 | A | USERD | 50 |

```cds
@EndUserText.label: 'Travel by agency'
@MappingRole: true
____(1)____ ZI_Travel_Agency {
  ____(2)____ ZI_Travel
    where ( AgencyID ) = ____(3)____( ZAGENCY, ZAGENCY, ACTVT = '03' )
       or Price < 60;
}

define role ZI_Travel_Own {
  grant select on ZI_Travel
    where CreatedBy = aspect user and Status = 'O';
}
```

(1) 빈칸 (1)~(3)을 채우시오.

(2) USERB가 다음 방법으로 읽을 때 보이는 TravelID를 쓰시오.
(가) `SELECT * FROM zi_travel`
(나) `ZC_TravelNoAuth`(`as projection on ZI_Travel`, `#NOT_REQUIRED`, 롤 없음)로 읽기
(다) `SELECT * FROM zi_travel WITH PRIVILEGED ACCESS`
(라) `ZI_Travel`의 어노테이션을 `#NOT_ALLOWED`로 바꾼 뒤 (가)

(3) (나)의 결과가 보안상 문제가 되는 이유와, 프로젝션 뷰에 붙여야 할 롤을 쓰시오.

(4) 권한 객체 `ZTRAVAUTH`의 필드 `AGENCY`, `CNTRY`를 뷰 요소 AgencyID, CountryCode에 매핑하는 롤의 where 절을 쓰고, 괄호 안 요소 순서와 권한 필드의 관계, 고정값 필드의 의미를 쓰시오.

(5) `@AccessControl.authorizationCheck` 값 `#CHECK`, `#MANDATORY`, `#NOT_REQUIRED`, `#NOT_ALLOWED`, `#PRIVILEGED_ONLY`의 의미를 각각 쓰시오. "`#NOT_REQUIRED`라고 써 놓고 롤을 만들면?"에도 답하시오.

(6) DCL이 적용되는 조건, 권한 없는 행이 어떻게 처리되는지, `WITH PRIVILEGED ACCESS`를 쓸 때의 주의점, ABAP Cloud에서 권한 객체를 사용자에게 주는 방법을 쓰시오.

<details><summary>정답·해설</summary>

**(1)** (1) `define role` (2) `grant select on` (3) `aspect pfcg_auth`

**(2)**
- (가) T1, T3, T4, T5. 롤1: `pfcg_auth`는 ACTVT = 03인 권한의 ZAGENCY만 조건이 되므로(070002는 활동 02뿐) AgencyID = 070001 → T1, T4. 리터럴 조건 `Price < 60`이 OR → T5. 롤2: USERB가 만들고 상태 O → T3(T2는 상태 A). 한 엔티티에 롤이 여러 개면 OR로 합쳐진다.
- (나) T1~T5 전부. 접근 제어는 ABAP SQL이 그 엔티티를 **직접** 읽을 때만 적용되고, 다른 뷰를 거치면 아래 뷰의 롤은 적용되지 않는다.
- (다) T1~T5 전부. CDS 접근 제어를 건너뛴다.
- (라) T1~T5 전부. `#NOT_ALLOWED`는 롤이 있어도 적용하지 않는다(롤이 있으면 문법 경고).

**(3)** 사용자가 프로젝션(서비스) 뷰로 모든 행을 보게 된다. 프로젝션 뷰에도 롤을 만들고 `@AccessControl.authorizationCheck: #CHECK`로 둔다.

```cds
@MappingRole: true
define role ZC_TRAVEL_ROLE {
  grant select on ZC_Travel
    where inheriting conditions from entity ZI_Travel;
}
```

**(4)** `where ( AgencyID, CountryCode ) = aspect pfcg_auth( ZTRAVAUTH, AGENCY, CNTRY, ACTVT = '03' );` 왼쪽 괄호의 요소 순서와 권한 필드 순서가 짝을 이룬다(AgencyID↔AGENCY, CountryCode↔CNTRY). `ACTVT = '03'`(표시)은 사용자의 권한 중 이 값을 가진 것만 고려하라는 고정값 필드다.

**(5)**
- `#CHECK`: 롤이 있으면 검사, 없으면 문법 경고.
- `#MANDATORY`: 롤이 반드시 있어야 하고 없으면 실행 시 런타임 오류.
- `#NOT_REQUIRED`: 롤이 없어도 경고하지 않음. 롤이 있으면 **실행 시 평가된다**. 그래서 `#NOT_REQUIRED`로 두고 롤을 만들면 행이 걸러진다.
- `#NOT_ALLOWED`: 권한 검사를 하지 않음. 롤이 있으면 경고가 나고 무시.
- `#PRIVILEGED_ONLY`: ABAP SQL에서 `WITH PRIVILEGED ACCESS`로만 읽어야 하는 엔티티.
사용자에게 보여주는 뷰는 `#CHECK`(또는 `#MANDATORY`)로 하고 롤을 만든다.

**(6)** DCL 롤이 활성이고 뷰가 `#CHECK`/`#MANDATORY`(또는 롤이 있는 `#NOT_REQUIRED`)이면 ABAP SQL로 그 엔티티를 읽을 때 권한 조건이 WHERE에 자동으로 붙는다. 권한 없는 행은 오류 없이 결과에서 빠진다. DB 테이블을 직접 읽거나 `WITH PRIVILEGED ACCESS`를 쓰면 적용되지 않으므로 남용하면 보안 구멍이 된다. 기술적 처리(배치, 내부 계산, RAP 내부 로직)에만 쓴다. ABAP Cloud에서는 권한 객체를 IAM 앱·비즈니스 카탈로그·비즈니스 역할로 사용자에게 할당한다(온프레미스는 PFCG 역할).

</details>

---

### C-013. CDS 엔티티 종류와 가상 요소·커스텀 엔티티·테이블 함수 선택 [개념] ★★★
<!-- src: RB-034, RB-035, RB-036, RB-031, RB-032 -->
(1) CDS 엔티티 종류의 문법과 용도를 표로 쓰시오: 뷰 엔티티, 프로젝션 뷰, 추상 엔티티, 커스텀 엔티티, 테이블 함수, 계층, transient 뷰 엔티티, DDIC 기반 뷰. 이 밖의 종류도 두 가지 쓰시오.

(2) RAP action `deductDiscount`가 할인율(%) 하나를 입력받게 하려 한다. 입력 구조를 정의하기에 가장 알맞은 것을 고르고 BDEF에서 참조하는 문법을 쓰시오.
① 커스텀 엔티티 ② 추상 엔티티 ③ CDS 테이블 함수 ④ DDIC 기반 CDS 뷰 ⑤ 프로젝션 뷰

(3) 프로젝션 뷰에 출발까지 남은 일수를 계산하는 가상 요소를 추가한다. 빈칸을 채우시오.

```cds
define root view entity ZC_Travel
  provider contract transactional_query
  as projection on ZR_Travel
{
  key TravelUUID,
      TravelID,
      BeginDate,
      @ObjectModel.____(가)____: 'ABAP:ZCL_TRAVEL_VE'
      ____(나)____ DaysToStart : abap.int4
}
```

```abap
CLASS zcl_travel_ve DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES ____(다)____.
ENDCLASS.

CLASS zcl_travel_ve IMPLEMENTATION.
  METHOD if_sadl_exit_calc_element_read~get_calculation_info.
    INSERT `BEGINDATE` INTO TABLE ____(라)____.
  ENDMETHOD.

  METHOD if_sadl_exit_calc_element_read~calculate.
    DATA lt_travel TYPE STANDARD TABLE OF zc_travel WITH DEFAULT KEY.
    lt_travel = CORRESPONDING #( it_original_data ).
    DATA(lv_today) = cl_abap_context_info=>get_system_date( ).
    LOOP AT lt_travel ASSIGNING FIELD-SYMBOL(<ls_travel>).
      <ls_travel>-DaysToStart = <ls_travel>-BeginDate - lv_today.
    ENDLOOP.
    ct_calculated_data = CORRESPONDING #( ____(마)____ ).
  ENDMETHOD.
ENDCLASS.
```

(4) `get_calculation_info`와 `calculate`가 각각 하는 일을 쓰시오.

(5) 가상 요소의 한계 3가지와 각 한계에 대한 대안(필터·정렬 해결 인터페이스 포함)을 쓰시오. "가상 요소는 언제 쓰나"에 한 문장으로 답하시오.

(6) 다음 요구에 커스텀 엔티티, CDS 테이블 함수, 가상 요소 중 무엇을 쓸지 고르고 이유를 쓰시오. 그리고 커스텀 엔티티와 테이블 함수 각각의 제약을 쓰시오.
(가) 외부 REST API에서 환율 목록을 받아 Fiori 목록에 보여준다.
(나) 수백만 건에 HANA 전용 SQLScript(여러 단계 중간 테이블)가 필요하고 결과를 다른 CDS에서 조인한다.
(다) Travel 목록에 "사용자의 즐겨찾기 여부"를 표시하는데 ABAP 클래스 호출로만 알 수 있고 화면에 수십 건만 나온다.

<details><summary>정답·해설</summary>

**(1)**

| 종류 | 문법 | 용도 |
|---|---|---|
| 뷰 엔티티 | `define view entity` | 기본 데이터 모델. 테이블·다른 CDS에서 SELECT |
| 프로젝션 뷰 | `define view entity ... provider contract ... as projection on` | 서비스별 투영(`transactional_query`, `transactional_interface`, `analytical_query`) |
| 추상 엔티티 | `define abstract entity` | DB에 없는 구조. RAP action·event 파라미터, 원격 서비스 구조 |
| 커스텀 엔티티 | `define custom entity` + `@ObjectModel.query.implementedBy` | ABAP 클래스(`IF_RAP_QUERY_PROVIDER`)가 데이터 제공. 원격 API, 복잡한 ABAP 로직 |
| 테이블 함수 | `define table function ... implemented by method` | AMDP(SQLScript)로 결과 계산 |
| 계층 | `define hierarchy` | 부모–자식 계층 |
| transient 뷰 엔티티 | `define transient view entity ... provider contract analytical_query` | 분석 쿼리. DB 객체 없이 분석 엔진이 해석 |
| DDIC 기반 뷰 | `define view` + `@AbapCatalog.sqlViewName` | 옛 형식. obsolete, 뷰 엔티티로 마이그레이션 |

그 밖: CDS 스칼라 함수, 외부 엔티티, 최신 릴리스의 CDS 테이블 엔티티.

**(2)** ② 추상 엔티티 — DB 대응 객체가 없는 순수 구조라 action·function·event 파라미터에 쓴다. `action deductDiscount parameter ZA_Discount result [1] $self;` 커스텀 엔티티는 읽기 쿼리용, 테이블 함수는 SQLScript 결과용, 프로젝션 뷰는 서비스 노출용.

**(3)** (가) `virtualElementCalculatedBy` (나) `virtual` (다) `if_sadl_exit_calc_element_read` (라) `et_requested_orig_elements` (마) `lt_travel`

**(4)** `get_calculation_info`는 계산에 필요한 원본 필드를 SADL에 알려, 화면에서 그 필드를 요청하지 않아도 함께 읽히게 한다. `calculate`는 읽힌 원본 데이터(`it_original_data`)로 계산해 `ct_calculated_data`에 채운다. 날짜끼리 빼면 일수(정수)가 나온다.

**(5)**
1. SADL(OData) 런타임에서만 계산된다. ABAP SQL로 읽으면 초기값 → 대안: DB에서 계산 가능한 식이면 CDS 요소로 직접 계산(CASE, 날짜 함수).
2. DB에 없는 값이라 기본적으로 필터·정렬 불가 → `IF_SADL_EXIT_FILTER_TRANSFORM`, `IF_SADL_EXIT_SORT_TRANSFORM`으로 원본 필드 조건으로 바꾸거나 CDS 식으로.
3. 앱 서버에서 행마다 계산하므로 행이 많거나 로직이 무거우면 느림(코드 푸시다운 반대) → 값이 저장되어야 하면 RAP determination으로 계산해 테이블에 저장, 외부 데이터면 커스텀 엔티티.
언제: "DB에서 계산할 수 없고(ABAP 클래스 호출, 사용자 컨텍스트 의존) 화면 표시용이며 행 수가 적을 때."

**(6)**
- (가) 커스텀 엔티티: DB에 데이터가 없으므로 `IF_RAP_QUERY_PROVIDER~select`에서 API를 호출해 돌려준다. 페이징·필터·정렬·건수 요청도 직접 처리.
- (나) CDS 테이블 함수: AMDP로 DB에서 계산하고, CDS 엔티티라 다른 CDS·ABAP SQL의 데이터 소스로 쓸 수 있다.
- (다) 가상 요소: 기존 DB 기반 뷰에 ABAP 계산 값 하나를 덧붙이는 용도, 행 수가 적어 부담이 작다.
- 제약: 커스텀 엔티티는 ABAP SQL의 데이터 소스로 쓸 수 없고(SADL/OData 전용) 다른 CDS와 조인도 안 된다. 테이블 함수는 DB 안에서 동작하므로 원격 API 호출을 할 수 없다.

</details>

---

### C-014. CDS 계층·분석 모델·표준 뷰 확장 [코드] ★★★
<!-- src: RB-033, RB-040, RB-041, RB-030 -->
(1) 직원–관리자 관계로 조직 계층을 만드는 CDS 계층이다. 빈칸을 채우시오.

```cds
define view entity ZI_Employee as select from zemployee
  association [0..1] to ZI_Employee as _Manager
    on $projection.Manager = _Manager.Employee
{
  key employee as Employee,
      manager  as Manager,
      name     as Name,
      _Manager
}

define hierarchy ZI_EmployeeHier
  as parent child hierarchy (
    ____(가)____ ZI_Employee
    ____(나)____ _Manager
    ____(다)____ Manager is initial
    siblings order by Employee
  )
{
  Employee, Manager, Name,
  $node.____(라)____ as HierLevel
}
```

(2) 계층의 소스 뷰가 갖춰야 할 조건, `start where`의 의미, `$node`로 얻을 수 있는 속성 3가지 이상, 고아·순환 처리 옵션 이름, ABAP SQL에서 하위 노드를 조회하는 방법을 쓰시오.

(3) 예약 금액을 항공사별로 분석하는 큐브와 분석 쿼리다. 빈칸을 채우시오.

```cds
@Analytics.dataCategory: ____(마)____
define view entity ZI_BookingCube as select from /dmo/booking
  association [0..1] to ZI_CarrierDim as _Carrier
    on $projection.CarrierID = _Carrier.CarrierID
{
  key travel_id     as TravelID,
  key booking_id    as BookingID,
      @ObjectModel.____(바)____: '_Carrier'
      carrier_id    as CarrierID,
      @Semantics.amount.currencyCode: 'CurrencyCode'
      @Aggregation.default: ____(사)____
      flight_price  as FlightPrice,
      currency_code as CurrencyCode,
      _Carrier
}

define transient view entity ZC_BookingQuery
  provider contract ____(아)____
  as projection on ZI_BookingCube
{ CarrierID, FlightPrice, CurrencyCode }
```

(4) 차원·큐브·분석 쿼리의 역할과 핵심 어노테이션(차원 뷰 `ZI_CarrierDim`에 붙일 것 포함)을 표로 쓰고, 옛 분석 쿼리 방식, transient 뷰 엔티티의 특징, 소비 방법(바인딩 유형과 클라이언트), 일반 뷰의 `group by`와 다른 점을 쓰시오.

(5) `ZI_Travel`(데이터 소스 별칭 `travel`)에 커스텀 필드를 추가하는 확장과, 기반 뷰의 확장 허용/금지 어노테이션이다. 빈칸을 채우시오.

```cds
____(자)____ ZI_Travel ____(차)____
{
  travel.zz_priority as ZZPriority,
  _Agency.name       as ZZAgencyName
}
// 기반 뷰에서 모든 확장 금지
@AbapCatalog.viewEnhancementCategory: [ ____(카)____ ]
// 기반 뷰에 GROUP BY가 있는데 확장 허용
@AbapCatalog.viewEnhancementCategory: [ #PROJECTION_LIST, ____(타)____ ]
```

(6) 확장 요소가 쓸 수 있는 것, 기본 확장 범주, DDIC 기반 뷰 확장 문법, ABAP Cloud에서 SAP 표준 뷰를 확장하기 위한 조건과 이름 규칙을 쓰시오.

<details><summary>정답·해설</summary>

**(1)** (가) `source` (나) `child to parent association` (다) `start where` (라) `hierarchy_level`

**(2)** 소스 뷰는 자기 자신을 가리키는 association(자식→부모)을 노출해야 한다. `start where`는 루트 노드 조건. `$node`: `hierarchy_level`, `hierarchy_rank`, `parent_id`, `node_id`, `hierarchy_tree_size`. 옵션: `orphans`, `cycles`. ABAP SQL에서는 `HIERARCHY_DESCENDANTS` 같은 계층 내비게이터로 하위 노드를 조회한다.

**(3)** (마) `#CUBE` (바) `foreignKey.association` (사) `#SUM` (아) `analytical_query`

**(4)**

| 구성 | 역할 | 핵심 문법 |
|---|---|---|
| 차원 | 마스터 데이터(항공사, 고객)와 텍스트·속성 | `@Analytics.dataCategory: #DIMENSION`, `@ObjectModel.representativeKey` |
| 큐브 | 측정값(금액, 건수)과 차원 키를 가진 사실 데이터 | `@Analytics.dataCategory: #CUBE`, 측정값 `@Aggregation.default: #SUM`, 차원 키 `@ObjectModel.foreignKey.association` |
| 분석 쿼리 | 행·열 배치, 필터, 계산 측정값 | `define transient view entity ... provider contract analytical_query as projection on 큐브` |

옛 방식은 `@Analytics.query: true`. transient 뷰 엔티티는 DB 뷰가 만들어지지 않고 분석 엔진이 해석한다. 소비: 서비스 정의에 노출 후 **InA - UI** 바인딩으로 공개해 Fiori 분석 앱, SAP Analytics Cloud, Excel에서 쓴다. 분석 엔진이 큐브의 association을 따라 차원 텍스트를 붙이고 `@Aggregation.default`로 소계·합계를 계산하며, 일반 `group by`와 달리 집계 수준을 소비자가 화면에서 바꿀 수 있다. 금액 측정값은 통화별로 따로 합산된다.

**(5)** (자) `extend view entity` (차) `with` (카) `#NONE` (타) `#GROUP_BY`

**(6)** 확장 요소는 기반 뷰의 데이터 소스와 association을 쓸 수 있다. 기본값은 요소 목록 확장 허용(#PROJECTION_LIST)이고, 집계·UNION이 있는 뷰는 `#GROUP_BY`, `#UNION`을 명시해야 확장할 수 있다. DDIC 기반 뷰는 `extend view ... with ...`와 `@AbapCatalog.sqlViewAppendName`. ABAP Cloud에서 SAP 표준 뷰를 확장하려면 그 뷰가 **C0(extend) 계약**으로 공개되어 있어야 하고, 필드 이름은 `ZZ`/`YY` 접두어로 충돌을 피한다.

</details>

---

## ABAP Cloud·clean core

### C-015. ABAP Cloud 구성 요소·공개 계약·언어 버전 [개념] ★★
<!-- src: RB-053, RB-056, RB-057, RB-064, RP-046 -->
(1) "ABAP Cloud" 개발 모델을 구성하는 요소 4가지와 이 모델이 지향하는 목표를 쓰시오. 이 모델을 쓸 수 있는 환경도 쓰시오.

(2) SAP 저장소 객체의 공개 계약(release contract) C0~C4가 각각 무엇을 보장하는지 예와 함께 표로 쓰시오. 계약이 있는 객체에 대해 SAP가 약속하는 것과, 객체의 release 상태를 ADT에서 확인하는 곳을 쓰시오.

(3) 고객이 ABAP Cloud로 SAP 표준 CDS 뷰에 커스텀 필드를 추가하는 확장(`extend view entity`)을 만들려 한다. 대상 뷰에 있어야 하는 계약을 고르고, C1만 있는 뷰로는 무엇을 할 수 있고 무엇을 못 하는지 쓰시오.
① C0 ② C1 ③ C2 ④ C3 ⑤ C4

(4) ABAP Cloud 언어 버전에서 생기는 대표적인 제약을 4가지 이상 쓰시오.

(5) ABAP 언어 버전에 대한 설명으로 옳지 **않은** 것을 고르고 이유를 쓰시오.
① 언어 버전에는 Standard ABAP, ABAP for Key Users, ABAP for Cloud Development가 있다.
② 언어 버전은 각 개발 객체의 속성이며 ADT Properties에서 확인한다.
③ ABAP for Cloud Development 객체는 공개 계약이 없는 SAP 객체를 문법 검사에서 오류로 막는다.
④ ABAP for Cloud Development 객체는 같은 시스템의 Standard ABAP 고객 객체라면 공개 여부와 관계없이 자유롭게 호출할 수 있다.
⑤ key user가 Custom Logic 앱으로 만든 BAdI 구현은 ABAP for Key Users 버전을 쓴다.

(6) RAP가 ABAP Cloud에서 어떤 위치인지 한 문장으로 쓰시오.

<details><summary>정답·해설</summary>

**(1)**
1. 언어 버전 **ABAP for Cloud Development**: 화면·리스트·리포트·직접 DB 접근 등을 금지한 제한된 ABAP.
2. **공개된(released) API만 사용**: SAP 객체는 공개 계약(C0~C4)이 있는 것만.
3. **ADT(Eclipse) 전용 개발**: SE80, SE24 같은 SAP GUI 트랜잭션을 쓰지 않음.
4. **클라우드용 기술**: RAP(트랜잭션 앱·API), CDS(데이터 모델), 애플리케이션 잡, 애플리케이션 로그, 통신 시나리오 등.
목표: 업그레이드에 안전하고(upgrade-stable) 클라우드에 바로 쓸 수 있는 확장, 즉 **clean core**(표준을 수정하지 않고 공개 인터페이스로만 확장).
환경: BTP ABAP 환경, S/4HANA Cloud Public Edition, S/4HANA 2022 이상 Private Edition·온프레미스(embedded Steampunk)에서 같은 규칙.

**(2)**

| 계약 | 의미 | 예 |
|---|---|---|
| C0 | 확장(extend): 확장 지점이 안정적으로 유지 | 확장 가능한 CDS 뷰·BDEF, 확장 include, BAdI |
| C1 | 시스템 내부 사용(use system-internally): ABAP Cloud·key user 코드에서 직접 사용 | `I_Product`, `I_Currency`, `CL_ABAP_RANDOM_INT`, `cl_abap_context_info`, 데이터 엘리먼트 |
| C2 | 원격 API로 사용 | OData·SOAP 서비스 |
| C3 | 설정(customizing) 콘텐츠 관리 | 설정 테이블 관련 객체 |
| C4 | ABAP 관리 DB 프로시저·함수(AMDP)에서 사용 | AMDP에서 쓸 수 있는 객체 |

계약이 있는 객체는 호환되지 않는 변경(시그니처·구조 변경)을 하지 않는다. 고객도 자기 객체(Tier 2 래퍼 등)를 C1으로 공개할 수 있다. 확인: ADT 객체 Properties의 **API State** 탭.

**(3)** ① C0. C1은 "읽어서 쓰기"만 보장하므로 C1만 있는 뷰는 SELECT는 할 수 있어도 확장은 못 한다.

**(4)** released되지 않은 SAP 테이블·FM 직접 접근 불가(`SELECT FROM mara` 대신 `I_Product`), SAP GUI·Dynpro·`WRITE`·`SUBMIT`·`CALL TRANSACTION` 불가, `sy-datum`/`sy-uname` 대신 `cl_abap_context_info`, 구식 문법 제한(`DESCRIBE TABLE` 등), `EXEC SQL`·ADBC 불가, AMDP는 읽기 전용, ADT에서만 개발.

**(5)** ④ — ABAP Cloud 코드는 고객 객체라도 언어 버전이 Standard ABAP이면 C1으로 공개된 것만 쓸 수 있다. 그래서 Tier 2 래퍼를 공개하는 단계가 필요하다. 같은 ABAP Cloud 소프트웨어 컴포넌트 안의 ABAP for Cloud Development 객체끼리는 자유롭게 쓴다.

**(6)** RAP는 ABAP Cloud에서 트랜잭션 앱과 API를 만드는 표준 모델이다(SEGW는 ABAP Cloud에서 쓸 수 없다).

</details>

---

### C-016. 확장 모델: 3-tier, Tier 2 래퍼, clean core level A~D, 확장 방식 [개념] ★★★
<!-- src: RB-058, RB-059, RB-060, RB-061, IB-148, MX-053 -->
S/4HANA Private Edition 고객사에서 "표준 프로그램을 직접 고쳐 달라"는 요청을 받았다.

(1) Clean Core 원칙을 설명하고, 위 요청에 대한 답변을 한 문장으로 쓰시오.

(2) 3-tier 확장 모델의 각 Tier를 설명하고, Public Edition에서 쓸 수 있는 Tier를 쓰시오.

(3) 필요한 SAP 기능(예: 공개되지 않은 BAPI)에 공개 API가 없을 때의 절차를 쓰고, Tier 2 래퍼를 만드는 단계를 순서대로 쓰시오. CDS의 경우 Tier 2 래퍼는 어떻게 만드는지, 고객이 SAP 객체 자체를 공개할 수 있는지도 쓰시오.

(4) SAP가 2025년에 3-tier 모델을 발전시켜 내놓은 clean core 수준 A~D를 예와 함께 표로 쓰고, 정리 목표와 코드 수준 거버넌스 도구를 쓰시오.

(5) S/4HANA 확장 방식 Key User, Developer(on-stack), Side-by-side를 비교하고, 고르는 기준을 쓰시오.

(6) 확장 방식에 대한 설명으로 옳지 **않은** 것을 고르시오.
① key user 확장은 Custom Fields, Custom Logic 같은 Fiori 앱으로 한다.
② key user 커스텀 로직은 "ABAP for Key Users" 언어 버전으로 작성된다.
③ developer 확장은 ADT에서 ABAP Cloud 규칙으로 S/4HANA 안에 개발한다.
④ side-by-side 확장은 BTP에서 개발하고 원격 API로 S/4HANA와 통신한다.
⑤ S/4HANA Cloud Public Edition에서도 필요하면 Tier 3 클래식 확장을 쓸 수 있다.

(7) embedded Steampunk와 BTP ABAP 환경(Steampunk)을 실행 위치, S/4 데이터 접근, 사용자·권한, 성능 영향, 적합한 경우, 조건으로 비교하시오. 빠진 로컬 API를 원격 Steampunk API로 메우는 것이 권장되는지도 쓰시오.

<details><summary>정답·해설</summary>

**(1)** 표준 코드를 수정하지 않고 SAP이 **릴리스한(안정성을 약속한) API와 확장 지점**만 써서 확장하는 원칙. 업그레이드가 쉬워지고 클라우드 전환이 가능해진다. 답변: "릴리스된 BAdI/확장 지점을 먼저 찾고, 없으면 side-by-side나 대안 설계를 검토하며, 수정(modification)은 최후의 수단이다."

**(2)**

| Tier | 내용 |
|---|---|
| Tier 1 (Cloud Extensibility, ABAP Cloud) | ABAP for Cloud Development, 공개 API(C1)·RAP·CDS만. 업그레이드 안전, 신규 개발의 기본 |
| Tier 2 (Cloud API Enablement) | 공개되지 않은 SAP 객체(BAPI, 클래식 FM 등)를 Standard ABAP 패키지의 고객 래퍼로 감싸 C1 공개, Tier 1에서 사용 |
| Tier 3 (Classic ABAP) | 제약 없는 클래식 개발. 업그레이드 위험이 가장 큼. 수정·암묵적 enhancement는 피하고 줄여 나감 |

Public Edition은 Tier 1(key user, developer, side-by-side)만 가능하고, Tier 2·3은 Private Edition·온프레미스에서만 가능하다.

**(3)**
- 절차: ① Cloudification Repository·ADT Released Objects에서 후속 공개 API를 찾는다 ② 없으면 Tier 2 래퍼를 만들어 공개하고 Tier 1에서는 래퍼만 부른다 ③ SAP에 공개 요청(Customer Influence)을 하고, 공개 API가 나오면 래퍼를 걷어 낸다.
- 래퍼 단계:
  1. Tier 2용 소프트웨어 컴포넌트·패키지(언어 버전 Standard ABAP)를 만든다.
  2. 래퍼 인터페이스와 구현 클래스(필요하면 팩토리)를 만들고 안에서 BAPI를 호출한다. 필요한 파라미터만, 메시지는 예외·결과로 돌려주는 깔끔한 시그니처.
  3. 래퍼 인터페이스·팩토리에 C1 계약을 부여해 "Use in Cloud Development"로 공개한다.
  4. 공개되지 않은 객체 사용에 대한 ATC 지적은 예외(exemption)로 관리한다.
  5. Tier 1 코드는 래퍼만 쓴다.
  6. SAP가 후속 API를 공개하면 래퍼를 지우고 공식 API로 바꾼다.
- CDS: 공개되지 않은 표준 CDS 뷰나 테이블을 감싸는 고객 CDS 뷰를 만들어 C1으로 공개한다. 고객이 SAP 객체 자체를 공개할 수는 없다.

**(4)**

| 수준 | 의미 | 예 |
|---|---|---|
| A — 완전 준수 | 공식 계약이 있는 공개 안정 인터페이스만 | ABAP Cloud + 공개 API, BTP side-by-side |
| B — 준수 | A + SAP가 문서화한 클래식 API·기술(대체로 업그레이드 안정) | 문서화된 일부 BAPI 등 |
| C — 부분 준수 | SAP 내부 객체 접근. 유연하지만 업그레이드 위험 관리 필요 | 공개되지 않은 테이블·클래스 직접 사용 |
| D — 비권장 | 명시적으로 권장하지 않는 기법(clean 아님) | 수정(modification), SAP 테이블에 직접 쓰기, 암묵적 enhancement |

목표: 가능한 한 A·B로 올리고 D를 우선 정리. 도구: ATC. A에 가까울수록 업그레이드 영향이 적다. 래퍼로 격리한다는 생각은 3-tier와 같다.

**(5)**
1. **Key User(In-app)**: Fiori 앱(Custom Fields, Custom Logic, Custom CDS Views)으로 비개발자·키 유저가 필드·간단한 로직 추가.
2. **Developer(On-stack, ABAP Cloud)**: 같은 S/4HANA에서 ADT로 ABAP Cloud 규칙에 따라 RAP·CDS·BAdI 구현.
3. **Side-by-side**: SAP BTP(ABAP 환경, CAP 등)에서 별도 앱을 만들고 API·이벤트로 연동. 코어와 완전히 분리.
기준: 단순 필드·로직은 key user, 복잡한 로직·새 앱이지만 S/4 데이터와 밀접하면 developer, 독립 수명 주기·여러 시스템 연동이면 side-by-side. 온프레미스·Private에서는 클래식 확장도 가능하지만 공개되지 않은 객체 사용은 정도에 따라 관리 대상으로 분류한다.

**(6)** ⑤ — Public Edition은 Tier 1만 쓸 수 있다.

**(7)**

| 항목 | embedded Steampunk | BTP ABAP 환경 |
|---|---|---|
| 실행 위치 | S/4HANA 안(같은 스택) | 별도 BTP 시스템 |
| S/4 데이터 접근 | 공개 CDS·로컬 API 직접 호출(빠름, 강결합) | 원격 API(OData, SOAP, RFC)(느슨한 결합) |
| 사용자·권한 | S/4 사용자·역할 재사용 | 별도 사용자 관리 |
| 성능 영향 | S/4 자원을 함께 씀 | S/4 부하 적음 |
| 적합 | S/4와 밀접한 확장(필드 검증, S/4 BO에 붙는 앱) | 독립 수명 주기, ERP 사용자 아닌 사용자, 다중 시스템 통합, SaaS·멀티테넌시 |
| 조건 | S/4HANA Cloud Public, S/4HANA 2022 이상 | BTP 계정 |

둘 다 같은 ABAP Cloud 규칙이라 개발 방식은 같고 결합 정도와 운영 형태가 기준이다. 빠진 로컬 API를 원격 Steampunk API로 메우는 것은 권장되지 않는다(밀접한 확장이면 embedded + Tier 2 래퍼).

</details>

---

### C-017. ABAP Cloud 규칙 위반 고치기와 콘솔 클래스·ATC·XCO [코드] ★★
<!-- src: RB-054, RB-055, IB-149, MX-054, MX-055, RB-062, MX-056, RB-063, RB-065 -->
다음 클래스의 언어 버전을 ABAP for Cloud Development로 바꾸자 활성화 오류가 났다.

```abap
CLASS zcl_mat_info DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.
ENDCLASS.

CLASS zcl_mat_info IMPLEMENTATION.
  METHOD if_oo_adt_classrun~main.
    DATA lv_lines TYPE i.
    SELECT matnr, mtart FROM mara INTO TABLE @DATA(lt_mat) UP TO 10 ROWS.   " (A)
    SELECT * FROM sflight INTO TABLE @DATA(lt_fl).                           " (B)
    CALL FUNCTION 'BAPI_FLIGHT_GETLIST' EXPORTING airline = 'LH'.           " (C)
    DESCRIBE TABLE lt_mat LINES lv_lines.                                    " (D)
    DATA(lv_today) = sy-datum.                                               " (E)
    LOOP AT lt_fl INTO DATA(ls_fl).
      WRITE: / ls_fl-carrid, ls_fl-fldate.                                   " (F)
    ENDLOOP.
    MESSAGE 'Done' TYPE 'I'.                                                 " (G)
    SUBMIT zreport AND RETURN.                                               " (H)
  ENDMETHOD.
ENDCLASS.
```

(1) (A)~(H) 각각이 왜 금지되는지와 클라우드 방식의 대체를 쓰시오.

(2) ABAP for Cloud Development에서 문법 검사를 통과하는 것을 **모두** 고르시오.
① `SELECT FROM I_Currency FIELDS Currency INTO TABLE @DATA(lt_cur).`
② `WRITE / 'Hello'.`
③ `CALL TRANSACTION 'VA01'.`
④ `DATA(lv_date) = cl_abap_context_info=>get_system_date( ).`
⑤ `SELECT * FROM mara INTO TABLE @DATA(lt_mara).`

(3) ADT에서 F9로 실행하는 콘솔 클래스다. 빈칸을 채우시오.

```abap
CLASS zcl_mx_run DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES ____(가)____.
ENDCLASS.

CLASS zcl_mx_run IMPLEMENTATION.
  METHOD ____(나)____.
    DATA(lv_today) = cl_abap_context_info=>____(다)____( ).
    DATA(lv_user)  = cl_abap_context_info=>____(라)____( ).
    DATA(lo_rnd) = cl_abap_random_int=>create( seed = cl_abap_random=>seed( )
                                               min  = 1
                                               max  = 6 ).
    DATA(lv_dice) = lo_rnd->____(마)____( ).
    SELECT FROM /dmo/flight
      FIELDS carrier_id, flight_date
      WHERE flight_date >= @lv_today
      INTO TABLE @DATA(lt_fl)
      UP TO 5 ROWS.
    ____(바)____->write( lt_fl ).
    out->write( |{ lv_user } / { lv_today DATE = ISO } rolled { lv_dice }| ).
  ENDMETHOD.
ENDCLASS.
```

(4) `CL_ABAP_CONTEXT_INFO`의 다른 메서드 세 가지와, 사용자 시간대 기준 날짜를 얻는 XCO 코드를 쓰시오.

(5) 기존 클래식 코드를 ABAP Cloud로 옮길 때 ATC를 쓰는 방법(점검 변형 이름, Quick Fix, 예외, 정기 실행)과 공개되지 않은 객체의 후속 API를 찾는 방법을 4가지 이상 쓰시오.

(6) XCO 라이브러리가 무엇인지 설명하고(진입점 포함) 쓰임 3가지를 예로 드시오.

<details><summary>정답·해설</summary>

**(1)**

| 줄 | 이유 | 대체 |
|---|---|---|
| (A) | MARA는 공개되지 않은 테이블 | 공개 CDS 뷰 `SELECT Product, ProductType FROM I_Product ...` |
| (B) | SFLIGHT도 공개되지 않은 테이블 | 같은 소프트웨어 컴포넌트의 자기 테이블(예: `/dmo/flight`)이나 공개 CDS 뷰 |
| (C) | 공개되지 않은 FM | 공개 API(RAP BO 인터페이스의 EML 등) 또는 Tier 2 래퍼 |
| (D) | `DESCRIBE TABLE ... LINES` 금지 | `DATA(lv_lines) = lines( lt_mat ).` |
| (E) | `sy-datum` 금지 | `cl_abap_context_info=>get_system_date( )` |
| (F) | 리스트 출력 `WRITE` 금지 | `out->write( lt_fl ).` |
| (G) | 화면에 보내는 `MESSAGE` 금지 | `out->write( 'Done' ).`(RAP 안에서는 `reported`에 메시지 객체) |
| (H) | 실행 프로그램·`SUBMIT` 금지 | 배경 처리는 애플리케이션 잡 |

고친 예:

```abap
METHOD if_oo_adt_classrun~main.
  SELECT Product, ProductType FROM I_Product INTO TABLE @DATA(lt_mat) UP TO 10 ROWS.
  SELECT FROM /dmo/flight FIELDS carrier_id, connection_id, flight_date
    WHERE carrier_id = 'LH' INTO TABLE @DATA(lt_fl).
  DATA(lv_lines) = lines( lt_mat ).
  DATA(lv_today) = cl_abap_context_info=>get_system_date( ).
  out->write( lt_fl ).
  out->write( |{ lv_lines } { lv_today DATE = ISO } Done| ).
ENDMETHOD.
```

그 밖에 클래식 BAdI·Customer Exit도 쓸 수 없고 UI는 Fiori(RAP + OData)로 만든다. 허용되지 않는 문장·객체는 구문 검사(언어 버전)와 ATC가 막는다.

**(2)** ①, ④ — `I_Currency`와 `CL_ABAP_CONTEXT_INFO`는 공개되어 있다. `WRITE`, `CALL TRANSACTION`(`CALL SCREEN`, `SUBMIT`)은 언어 차원에서 금지, MARA는 미공개.

**(3)** (가) `if_oo_adt_classrun` (나) `if_oo_adt_classrun~main` (다) `get_system_date` (라) `get_user_technical_name` (마) `get_next` (바) `out`. `IF_OO_ADT_CLASSRUN`은 공개 인터페이스이고 `main`의 `out` 파라미터로 ADT 콘솔에 출력한다. `out->write`는 내부 테이블도 표 형태로 출력한다. `cl_abap_random_int=>create`는 최솟값·최댓값 사이 정수 난수 생성기를 만든다.

**(4)** `get_system_time( )`, `get_user_time_zone( )`, `get_user_language_abap_format( )`, `get_user_formatted_name( )`. XCO: `xco_cp=>sy->date( xco_cp_time=>time_zone->user )->as( xco_cp_time=>format->iso_8601_extended )->value`.

**(5)**
- ATC: 점검 변형 `ABAP_CLOUD_READINESS`로 금지 문장·미공개 API 사용을 지적받는다. 일부는 Quick Fix로 자동 수정(예: 후속 CDS 뷰로 교체). Tier 2 래퍼처럼 의도적 위반은 예외(exemption) 승인으로 관리. 이송 해제 시·야간 배치로 정기 실행해 Tier 1 위반을 막는다(언어 버전을 쓸 수 없는 2020/2021 릴리스에서는 ATC가 규칙 강제 수단). 언어 버전을 바꾸기 전에 미리 돌린다.
- 후속 객체: ADT Project Explorer의 Released Objects 트리, 객체 Properties → API State, SAP Business Accelerator Hub, GitHub Cloudification Repository / Viewer(예: MARA → `I_Product`).
- S/4HANA에서는 Custom Code Migration 앱으로 안 쓰는 코드를 찾고 남길 코드를 ATC로 점검한 뒤 고친다.

**(6)** XCO(Extension Components)는 ABAP Cloud용으로 공개된 범용 표준 라이브러리로, 클래식 시스템 필드·유틸리티 FM을 대신하는 일관된 API다(진입점 `XCO_CP`, `XCO_CP_*`, 메서드 체이닝). 쓰임: ① 시스템 정보·시간(`xco_cp=>sy->date( ... )`, `xco_cp=>sy->user( )`) ② 저장소 정보 읽기(`xco_cp_abap_repository`로 패키지·클래스·CDS 목록) ③ 코드 생성(테이블·CDS·BDEF·클래스 생성, RAP 생성기) ④ 문자열·JSON(`xco_cp=>string( )`, `xco_cp_json`). `sy-datum`이나 `CONVERT TIME STAMP` 대신 쓸 수 있는 공개 API다.

</details>

---

### C-018. ABAP Cloud의 통신·배경 처리·비동기 처리 [코드] ★★★
<!-- src: RB-066, RB-067, RB-068, RB-083, RB-084, MX-057, RB-094 -->
클래식 ABAP의 SM59 RFC 목적지, `SUBMIT ... VIA JOB`(SM36), aRFC(`STARTING NEW TASK`), 업데이트 태스크는 ABAP Cloud에서 쓸 수 없다.

(1) 통신 시나리오 `Z_FLIGHT_API_CS`의 통신 약정으로 외부 REST API를 GET 호출하는 코드다. 빈칸을 채우고, 상태 코드 확인 방법과 BTP Destination 서비스를 쓸 때의 메서드를 쓰시오.

```abap
TRY.
    DATA(lo_dest) = cl_http_destination_provider=>____(가)____(
                      comm_scenario = 'Z_FLIGHT_API_CS'
                      service_id    = 'Z_FLIGHT_API_REST' ).
    DATA(lo_client) = cl_web_http_client_manager=>____(나)____( lo_dest ).
    lo_client->get_http_request( )->set_uri_path( '/flights?carrier=LH' ).
    DATA(lo_response) = lo_client->execute( ____(다)____ ).
    DATA(lv_json) = lo_response->____(라)____( ).
    lo_client->close( ).
  CATCH cx_http_dest_provider_error cx_web_http_client_error INTO DATA(lx).
ENDTRY.
```

(2) 통신 시나리오, 통신 시스템, 통신 약정의 관계를 쓰고, RAP OData 서비스를 외부 시스템이 호출하게 하려면 필요한 객체·설정을 순서대로 쓰시오. UI용 서비스와 시스템 간 API는 사용자에게 각각 무엇으로 주는지도 쓰시오.

(3) ABAP Cloud에서 외부(또는 S/4HANA의) OData 서비스를 호출해 데이터를 읽는 단계를 쓰고, 그 결과를 Fiori 목록으로 보여주려면 어떤 CDS 엔티티와 결합하는지 쓰시오.

(4) 애플리케이션 잡(application job)을 만드는 데 필요한 클래스·인터페이스·객체, 예약 방법, 로그 기록 API를 쓰시오.

(5) Travel이 승인되면 메일 발송을 비동기로 실행하는 bgPF 코드다. 빈칸을 채우시오.

```abap
CLASS zcl_travel_mail_op DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES ____(마)____.            " 트랜잭션 제어(controlled) 작업
    METHODS constructor IMPORTING iv_travel_uuid TYPE sysuuid_x16.
  PRIVATE SECTION.
    DATA mv_travel_uuid TYPE sysuuid_x16.
ENDCLASS.

CLASS zcl_travel_mail_op IMPLEMENTATION.
  METHOD constructor.
    mv_travel_uuid = iv_travel_uuid.
  ENDMETHOD.
  METHOD if_bgmc_op_single~execute.
    " modify 단계: 데이터 읽기, 메일 내용 준비
    cl_abap_tx=>____(바)____( ).
    " save 단계: 발송 기록 테이블 갱신
  ENDMETHOD.
ENDCLASS.
```

```abap
" RAP save_modified 안에서
TRY.
    DATA(lo_process) = cl_bgmc_process_factory=>____(사)____( )->create( ).
    lo_process->set_name( 'Send travel mail'
             )->set_operation( NEW zcl_travel_mail_op( ls_travel-TravelUUID ) ).
    lo_process->____(아)____( ).
  CATCH cx_bgmc INTO DATA(lx_bgmc).
ENDTRY.
```

(6) bgPF를 쓰는 상황, controlled와 uncontrolled 작업의 차이, 커밋 규칙(시작하는 쪽, RAP 안, 작업 클래스 안)을 쓰시오. 예전 우회 방법은 무엇이었는지도 쓰시오.

(7) 클래식 배경·비동기 기술을 ABAP Cloud에서 대신하는 방법을 정리하시오: 정기 배치, 저장 후 비동기 후속 처리, 저장 시 함께 해야 할 일(업데이트 태스크 대체), 상태 변화 알림, 번호 범위, 잠금.

<details><summary>정답·해설</summary>

**(1)** (가) `create_by_comm_arrangement` (나) `create_by_http_destination` (다) `if_web_http_client=>get` (라) `get_text`. 상태 코드는 `lo_response->get_status( )-code`. BTP Destination 서비스는 `create_by_cloud_destination`.

**(2)** 통신 시나리오(개발자가 정의, 사용할 서비스 목록) → 통신 시스템(대상 호스트·인증, inbound/outbound 사용자) → 통신 약정(시나리오와 시스템 연결). 외부 호출 허용 순서:
1. 서비스 정의 + 서비스 바인딩(보통 `OData V4 - Web API`) 생성·Publish.
2. 통신 시나리오를 만들고 Inbound 탭에 바인딩이 만든 inbound 서비스 추가, 필요한 권한 정의, 시나리오 게시.
3. (관리자, Fiori 앱) 통신 사용자 생성.
4. 통신 시스템을 만들고 inbound 사용자로 통신 사용자 지정.
5. 통신 약정으로 시나리오와 시스템 연결(서비스 URL 표시).
6. 외부 시스템은 그 URL과 통신 사용자 인증(기본 인증, 인증서, OAuth)으로 호출.
UI용 서비스는 비즈니스 카탈로그·IAM 앱·비즈니스 역할로, 시스템 간 API는 통신 시나리오로 준다.

**(3)**
1. 대상 서비스의 `$metadata`(EDMX)를 받는다.
2. ADT에서 **Service Consumption Model**(OData)을 만들고 EDMX를 올린다 → 원격 엔티티에 대응하는 추상 엔티티와 프록시 정보 생성.
3. 통신 시나리오(outbound)·통신 시스템·통신 약정으로 URL·인증 설정.
4. `create_by_comm_arrangement`로 목적지, `create_by_http_destination`으로 HTTP 클라이언트, `/iwbep/cl_cp_factory_remote=>create_v2_remote_proxy`(V4는 `create_v4_remote_proxy`)로 클라이언트 프록시.
5. `create_resource_for_entity_set( )->create_request_for_read( )`로 읽기 요청, 필터·`$top` 설정 후 실행, 결과를 추상 엔티티 타입 테이블로 받음.
6. Fiori에는 **커스텀 엔티티**를 만들고 쿼리 구현 클래스(`IF_RAP_QUERY_PROVIDER~select`)에서 위 호출을 하며 UI의 페이징·필터·정렬을 원격 요청으로 전달. 원격 데이터는 DB에 없으므로 CDS 뷰 엔티티로 만들 수 없고, 원격 호출이 느리므로 페이징을 꼭 전달한다.

**(4)**
1. 잡 클래스: `IF_APJ_DT_EXEC_OBJECT`(설계 시 파라미터 정의, `get_parameters`) + `IF_APJ_RT_EXEC_OBJECT`(실행 로직, `execute`).
2. 잡 카탈로그 항목(Application Job Catalog Entry)에 클래스 등록.
3. 잡 템플릿(Application Job Template): 카탈로그 항목 + 기본 파라미터 값.
4. 운영자는 Fiori 앱 "Application Jobs"에서 즉시·주기 예약하고 결과를 본다. 프로그램에서 예약은 `CL_APJ_RT_API`.
5. 로그: `CL_BALI_LOG`(`cl_bali_log=>create( )`, `add_item( )`, `cl_bali_log_db=>get_instance( )->save_log( )`)로 남기면 잡 결과 화면에서 보인다.
야간 집계·대량 정리 같은 정기 배치에 쓰고, 사용자 요청 직후 비동기 작업은 bgPF가 더 알맞다.

**(5)** (마) `if_bgmc_op_single` (바) `save` (사) `get_default` (아) `save_for_execution`. `save_for_execution`은 실행 요청을 기록할 뿐이고 같은 LUW가 커밋되어야 실제로 시작된다. 반환값(프로세스 모니터)으로 상태를 조회할 수 있다.

**(6)**
- 상황: 사용자 요청(저장)은 빨리 끝내고, 오래 걸리는 후속 작업(대량 계산, 외부 호출, PDF 생성·메일)을 비동기로 확실하게 실행. bgRFC 위에서 동작하며 ABAP Cloud에서 쓸 수 있다.
- controlled(`IF_BGMC_OP_SINGLE`): `execute` 안에서 제어된 SAP LUW를 따른다. modify 단계(읽기·검증) → `cl_abap_tx=>save( )` → DB 변경. 규칙 위반을 프레임워크가 검사. 권장.
- uncontrolled(`IF_BGMC_OP_SINGLE_TX_UNCONTR`, `set_operation_tx_uncontrolled`): 트랜잭션 제어를 개발자가 책임(레거시 코드 호출 등).
- 커밋: 일반 ABAP 코드에서 시작하면 `save_for_execution( )` 뒤에 `COMMIT WORK`. RAP 저장 순서 안에서 등록하면 RAP가 커밋하므로 직접 커밋하지 않는다. 작업 클래스(`execute`) 안에서는 `COMMIT WORK`를 쓰지 않는다.
- 예전 우회: RFC `DESTINATION 'NONE'`에서 `JOB_OPEN`/`JOB_CLOSE`로 배경 잡 생성(ABAP Cloud 불가).

**(7)**

| 요구 | ABAP Cloud 방법 |
|---|---|
| 정기 배치 | Application Jobs(`IF_APJ_*`, 카탈로그·템플릿) |
| 저장 후 비동기 후속 처리 | bgPF(`IF_BGMC_OP_SINGLE`, `cl_bgmc_process_factory`), **COMMIT 뒤에** 실행되어 트랜잭션 일관성 유지 |
| 저장 시 함께 할 일 | `managed with additional save`의 `save_modified` |
| 상태 변화 알림 | RAP 비즈니스 이벤트(`RAISE ENTITY EVENT` + 로컬 이벤트 핸들러/Event Mesh) |
| 번호 범위 | `CL_NUMBERRANGE_RUNTIME` |
| 잠금 | RAP 잠금(`lock master`) 또는 `CL_ABAP_LOCK_OBJECT_FACTORY` |

</details>

---

### C-019. ABAP Cloud에서 쓰는 7.40+ 핵심 문법 [코드] ★★
<!-- src: IB-150, MX-037, MX-038, MX-039, MX-040 -->
(1) 다음 레거시 코드를 같은 결과를 내는 7.40 이후 문법(인라인 선언, 새 SQL, 테이블 식, 문자열 템플릿, VALUE/FOR)으로 다시 쓰시오. 'LH'가 없으면 lv_name은 빈 값이어야 한다.

```abap
DATA: lt_scarr TYPE TABLE OF scarr,
      ls_scarr TYPE scarr,
      lv_name  TYPE s_carrname,
      lv_text  TYPE string,
      lt_ids   TYPE TABLE OF s_carr_id.
SELECT * FROM scarr INTO TABLE lt_scarr WHERE currcode = 'EUR'.
READ TABLE lt_scarr INTO ls_scarr WITH KEY carrid = 'LH'.
IF sy-subrc = 0.
  lv_name = ls_scarr-carrname.
ENDIF.
CONCATENATE 'Airline:' lv_name INTO lv_text SEPARATED BY space.
LOOP AT lt_scarr INTO ls_scarr.
  APPEND ls_scarr-carrid TO lt_ids.
ENDLOOP.
```

(2) 다음 선언에 대한 설명으로 옳지 **않은** 것을 고르고 이유를 쓰시오.

```abap
DATA(a) = 'ABAP'.
DATA(b) = `ABAP`.
DATA(c) = 7 / 2.
DATA(d) = |{ a }X|.
DATA(e) = CONV decfloat34( 7 ) / 2.
```
① a의 타입은 `c LENGTH 4`다. ② b의 타입은 `string`이다. ③ c의 타입은 `i`이고 값은 3이다. ④ d의 타입은 `string`이다. ⑤ e의 값은 3.5다.

(3) 다음 코드 실행 뒤 `lt_sum`의 내용(순서대로), `lv_max`, `ASCENDING`을 지웠을 때 `lt_sum`의 carrid 순서를 쓰시오.

```abap
TYPES: BEGIN OF ty_f, carrid TYPE c LENGTH 3, price TYPE i, END OF ty_f,
       tt_f TYPE STANDARD TABLE OF ty_f WITH EMPTY KEY.
DATA(lt) = VALUE tt_f( ( carrid = 'LH' price = 300 ) ( carrid = 'AA' price = 100 )
                       ( carrid = 'UA' price = 50 )  ( carrid = 'AA' price = 250 ) ).
DATA(lt_sum) = VALUE tt_f(
  FOR GROUPS grp OF ls IN lt GROUP BY ls-carrid ASCENDING
  ( carrid = grp
    price  = REDUCE i( INIT s = 0 FOR m IN GROUP grp NEXT s = s + m-price ) ) ).
DATA(lv_max) = REDUCE i( INIT x = 0 FOR r IN lt_sum
                         NEXT x = COND #( WHEN r-price > x THEN r-price ELSE x ) ).
```

(4) r1, ls2, ls3, r4, r5, r6의 값을 쓰시오.

```abap
TYPES: BEGIN OF ty_c, id TYPE i, name TYPE string, END OF ty_c.
DATA lt TYPE SORTED TABLE OF ty_c WITH UNIQUE KEY id.
lt = VALUE #( ( id = 30 name = `C` ) ( id = 10 name = `A` ) ( id = 20 name = `B` ) ).
DATA(r1)  = lt[ 2 ]-name.
DATA(ls2) = VALUE ty_c( lt[ id = 40 ] OPTIONAL ).
DATA(ls3) = VALUE ty_c( lt[ id = 40 ] DEFAULT VALUE #( id = -1 name = `none` ) ).
DATA(r4)  = xsdbool( line_exists( lt[ name = `C` ] ) ).
DATA(r5)  = line_index( lt[ id = 25 ] ).
TRY.
    DATA(r6) = lt[ id = 99 ]-name.
  CATCH cx_sy_itab_line_not_found.
    r6 = `ERR`.
ENDTRY.
```

(5) s1~s5의 값을 쓰시오(공백은 `␣`).

```abap
DATA lv_kunnr TYPE c LENGTH 10 VALUE '0000012345'.
DATA lv_d     TYPE d VALUE '20261013'.
DATA(s1) = |{ lv_kunnr ALPHA = OUT }|.
DATA(s2) = |{ 42 WIDTH = 6 ALIGN = RIGHT PAD = '0' }|.
DATA(s3) = |{ lv_d DATE = ISO }|.
DATA(s4) = |{ `abap` CASE = UPPER }-{ strlen( `abap ` ) }|.
DATA(s5) = |[{ 'AB' WIDTH = 5 }]|.
```

<details><summary>정답·해설</summary>

**(1)**

```abap
TYPES tt_ids TYPE STANDARD TABLE OF s_carr_id WITH EMPTY KEY.

SELECT * FROM scarr
  WHERE currcode = 'EUR'
  INTO TABLE @DATA(lt_scarr).

DATA(lv_name) = VALUE s_carrname( lt_scarr[ carrid = 'LH' ]-carrname OPTIONAL ).
DATA(lv_text) = |Airline: { lv_name }|.
DATA(lt_ids)  = VALUE tt_ids( FOR ls_scarr IN lt_scarr ( ls_scarr-carrid ) ).
```

- 새 SQL: 호스트 변수 앞 `@`, 쉼표 구분 열 목록, INTO는 끝에.
- 테이블 식은 행이 없으면 `CX_SY_ITAB_LINE_NOT_FOUND`를 내므로 `VALUE type( ... OPTIONAL )`로 감싼다. 인라인 선언 변수에는 `#`으로 타입을 추론할 수 없어 타입을 명시했다.
- `|...{ }...|`는 `CONCATENATE ... SEPARATED BY space`와 같은 결과("Airline: Lufthansa").
- 레거시 `TYPE TABLE OF scarr`는 기본 키(standard key)가 생겨 새 코드와 키가 다를 수 있다(동작에는 영향 없음).

**(2)** ③ — `7 / 2`는 피연산자가 모두 i라 계산 타입이 i이고, i 계산의 `/`는 **반올림**하므로 3.5 → 4다(버림은 `DIV`). ① 텍스트 필드 리터럴은 길이만큼의 c ② 백쿼트 리터럴은 string ④ 문자열 템플릿 결과는 항상 string ⑤ decfloat34가 섞이면 계산 타입이 decfloat34라 3.5.

**(3)** `lt_sum` = (AA, 350), (LH, 300), (UA, 50) / `lv_max` = 350 / ASCENDING 없으면 LH, AA, UA. `GROUP BY ls-carrid`로 같은 carrid가 한 그룹이 되고 그룹 키가 단순 값이라 `grp`를 그대로 carrid에 넣는다. `FOR m IN GROUP grp`로 그룹 행을 돈다(AA = 100+250). ASCENDING이 없으면 그룹이 **처음 나타난 순서**로 만들어진다.

**(4)**

| 변수 | 값 |
|---|---|
| r1 | `B` |
| ls2 | id = 0, name = 빈 문자열 |
| ls3 | id = -1, name = `none` |
| r4 | `X` |
| r5 | 0 |
| r6 | `ERR` |

SORTED 테이블은 키 순서(10, 20, 30)로 저장되어 2번째 행은 id 20. `OPTIONAL`은 초기값 행, `DEFAULT`는 지정 값을 돌려주고 예외를 내지 않는다. `line_exists`는 키가 아닌 컴포넌트로도 검색 가능(선형), `line_index`는 못 찾으면 0. TRY 안에서 인라인 선언한 r6도 그 뒤 같은 메서드 어디서든 쓸 수 있다.

**(5)** s1 = `12345`, s2 = `000042`, s3 = `2026-10-13`, s4 = `ABAP-5`, s5 = `[AB␣␣␣]`. `ALPHA = OUT`은 앞의 0을 지운다(IN은 채움). `WIDTH = 6 ALIGN = RIGHT PAD = '0'`은 6칸 오른쪽 정렬 후 0으로 채움. string 리터럴은 끝 공백을 유지해 `abap␣`의 길이가 5(텍스트 필드 리터럴이면 4). WIDTH만 주면 왼쪽 정렬·공백 채움.

</details>

---

## RAP 구조·구현 유형

### C-020. RAP BO의 계층 객체: composition, 프로젝션, BO 인터페이스 [코드] ★★
<!-- src: RP-001, RP-002, RP-003, RB-024, RB-088 -->
Travel(루트)–Booking(자식) BO를 처음부터 만든다.

```cds
define ____(a)____ view entity ZR_TravelTP
  as select from ztravel_a
  ____(b)____ [0..*] of ZR_BookingTP as _Booking
{
  key travel_uuid           as TravelUUID,
      travel_id             as TravelID,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true
      local_last_changed_at as LocalLastChangedAt,
      @Semantics.systemDateTime.lastChangedAt: true
      last_changed_at       as LastChangedAt,
      _Booking
}

define view entity ZR_BookingTP
  as select from zbooking_a
  association ____(c)____ ZR_TravelTP as _Travel
    on $projection.TravelUUID = _Travel.TravelUUID
{
  key booking_uuid as BookingUUID,
      travel_uuid  as TravelUUID,
      _Travel
}

define root view entity ZC_TravelTP
  provider contract ____(d)____
  as projection on ZR_TravelTP
{
  key TravelUUID,
      TravelID,
      LocalLastChangedAt,
      LastChangedAt,
      _Booking : ____(e)____ ZC_BookingTP
}
```

(1) 빈칸 (a)~(e)를 채우고, 자식 프로젝션 `ZC_BookingTP`의 `_Travel`은 어떻게 다시 연결하는지 쓰시오.

(2) `localInstanceLastChangedAt`과 `lastChangedAt` 필드가 각각 무엇으로 쓰이며 누가 채우는지 쓰시오.

(3) DB 테이블에서 Fiori Elements 미리 보기까지 만들어야 하는 개발 객체를 아래에서 위 순서로 쓰고 역할을 한 줄씩 쓰시오. 이 구조에서 "분리"되어 있는 두 쌍을 쓰시오.

(4) composition, to-parent association, 일반 association의 문법·의미·RAP에서의 역할을 표로 쓰고, 둘 사이의 필수 규칙을 쓰시오.

(5) 프로젝션 레이어에 대한 설명으로 옳지 **않은** 것을 고르고, 나머지가 맞는 이유를 쓰시오.
① 하나의 인터페이스 BO 위에 앱별·API별로 서로 다른 프로젝션을 여러 개 만들 수 있다.
② 프로젝션 BDEF에서는 `use create;`, `use action acceptTravel;`처럼 노출할 동작만 고른다.
③ 트랜잭션 처리용 OData 서비스의 프로젝션 뷰 provider contract는 `transactional_query`다.
④ 프로젝션 BDEF에 새 validation을 선언하면 기반 BO의 저장 시점에 함께 실행된다.
⑤ `provider contract transactional_interface`는 다른 BO나 소비자가 안정적으로 재사용하는 인터페이스 레이어용이다.

(6) RAP BO 인터페이스가 무엇인지(CDS와 BDEF 문법 포함) 설명하고, 프로젝션과의 차이를 쓰시오. ABAP Cloud에서 판매 오더 같은 표준 업무 데이터를 만들 때 BAPI 대신 쓰는 것과 EML 코드 골격을 쓰고, 공개 BO 인터페이스가 없으면 어떻게 하는지 쓰시오.

<details><summary>정답·해설</summary>

**(1)** (a) `root` (b) `composition` (c) `to parent` (d) `transactional_query` (e) `redirected to composition child`. 자식 프로젝션의 `_Travel`은 `_Travel : redirected to parent ZC_TravelTP`. 프로젝션에서는 association 대상을 프로젝션 뷰로 다시 연결해야 한다.

**(2)** `localInstanceLastChangedAt`은 인스턴스 단위 **ETag**(`etag master`), `lastChangedAt`은 Draft의 **total ETag** 필드로 쓰인다. managed BO에서 프레임워크가 자동으로 채운다.

**(3)**

| 순서 | 객체 | 역할 |
|---|---|---|
| 1 | DB 테이블(활성, 필요하면 Draft 테이블) | 데이터 영속화 |
| 2 | 인터페이스(루트) CDS 뷰 `define root view entity ZR_...` | 데이터 모델. composition, association, 의미 어노테이션 |
| 3 | BDEF + 행동 구현 클래스(Behavior Pool `ZBP_...`) | 트랜잭션 동작 선언(CRUD, determination, validation, action, 잠금, ETag, 권한, Draft)과 구현 |
| 4 | 프로젝션 뷰 `ZC_...`(`transactional_query`) + 프로젝션 BDEF(`projection;`, `use ...`) | 서비스별 노출 필드·동작, 검색·텍스트·값 도움말 |
| 5 | 메타데이터 확장(DDLX) | UI 어노테이션 분리 관리 |
| 6 | 서비스 정의 `define service` | 노출할 엔티티 목록(`expose ... as ...`) |
| 7 | 서비스 바인딩 | 프로토콜·용도(OData V2/V4, UI/Web API), Publish 후 Preview |

인터페이스 층(R)은 재사용 BO 모델, 프로젝션 층(C)은 특정 앱·API 관점이다. 분리: 데이터 모델(CDS)과 동작(BDEF), 서비스 정의(무엇을)와 바인딩(어떻게).

**(4)**

| 종류 | 문법 | 의미 | RAP에서 |
|---|---|---|---|
| composition | `composition [0..*] of ZR_Booking as _Booking` | 부모가 자식을 소유(존재 종속) | BO 구조(트리) 정의, create-by-association, 부모 삭제 시 자식도 삭제 |
| to parent | `association to parent ZR_Travel as _Travel on ...` | 자식→부모 역방향, composition과 짝 | 잠금·ETag·권한을 부모에 위임(`lock dependent by _Travel`, `authorization dependent by _Travel`) |
| 일반 association | `association [0..1] to ZI_Agency as _Agency on ...` | 독립 엔티티 간 참조 | 텍스트·값 도움말·내비게이션. 트랜잭션 구조에 포함되지 않아 한 트랜잭션에서 함께 저장되지 않음 |

규칙: composition 대상은 반드시 `to parent`를 정의하고, 최상위 엔티티만 `define root view entity`. "composition은 모델링, to parent는 런타임 위임".

**(5)** ④ — determination·validation은 기반(인터페이스) BO의 업무 로직이라 프로젝션에서 정의하지 않는다(프로젝션 고유로 추가할 수 있는 것은 일부 action/function 등 제한적). ① 프로젝션의 존재 이유가 서비스별 관점 분리 ② `projection;` 헤더와 `use ...`로 재노출 ③ UI/Web API 트랜잭션 서비스는 `transactional_query` ⑤ released API로 공개하는 BO 인터페이스 층(분석용은 `analytical_query`).

**(6)**
- BO 인터페이스: 다른 개발자(소비자)에게 BO를 안정적으로 제공하는 계층. `define root view entity I_... provider contract transactional_interface as projection on R_...`와 인터페이스 BDEF(`interface;`, `use create; use update; use action ...`)로 노출할 필드·작업만 고른다. C1으로 공개하면 ABAP Cloud 코드에서 EML로 쓰고, 내부 구현이 바뀌어도 인터페이스는 유지된다. 프로젝션(`transactional_query`)은 서비스용 투영, BO 인터페이스(`transactional_interface`)는 다른 ABAP 코드가 쓰는 API.
- 표준 BO: SAP가 공개한 RAP BO 인터페이스(예: `I_SalesOrderTP` 같은 `..TP`)를 EML로 호출한다.

```abap
MODIFY ENTITIES OF i_salesordertp
  ENTITY SalesOrder
    CREATE FIELDS ( SalesOrderType SalesOrganization )
    WITH VALUE #( ( %cid = 'SO1' SalesOrderType = 'OR' SalesOrganization = '1010' ) )
  MAPPED DATA(ls_mapped) FAILED DATA(ls_failed) REPORTED DATA(ls_reported).
COMMIT ENTITIES.
```

없으면 공개된 원격 API(OData 등) 또는 Tier 2 래퍼(BAPI 감싸기).

</details>

---

### C-021. 구현 유형 선택과 저장 옵션, 레거시 BAPI 감싸기 [개념] ★★★
<!-- src: RP-005, RP-006, RB-069, RB-070, RB-087 -->
(1) 구현 유형 managed, unmanaged, managed `with unmanaged save`, managed `with additional save`를 프레임워크가 하는 일, 개발자가 할 일, 사용 상황으로 표를 쓰시오.

(2) "기존 BAPI가 있으면 무조건 unmanaged인가?"라는 꼬리 질문에 답하시오.

(3) managed BO 저장 옵션에 대한 설명으로 옳은 것을 고르고, 나머지를 바르게 고치시오.
① `managed with unmanaged save`에서도 `persistent table`을 반드시 지정해야 한다.
② `with additional save`를 쓰면 기본 저장이 생략되고 `save_modified`만 실행된다.
③ 두 옵션 모두 세이버 클래스의 `save_modified`를 재정의해 구현한다.
④ `save_modified`의 `create` 파라미터에는 기본적으로 모든 필드 값이 항상 들어 있다.
⑤ 저장 옵션은 BDEF 헤더에만 쓸 수 있고 엔티티별로 지정할 수 없다.

(4) Travel이 생성되거나 상태가 바뀔 때 로그 테이블에 기록하는 additional save 구현이다. 빈칸을 채우고, 다른 필드 값도 필요할 때의 옵션을 쓰시오.

```
managed ____(가)____ implementation in class zbp_r_travel unique;
strict ( 2 );
```

```abap
CLASS lsc_zr_travel DEFINITION INHERITING FROM cl_abap_behavior_saver.
  PROTECTED SECTION.
    METHODS ____(나)____ REDEFINITION.
ENDCLASS.

CLASS lsc_zr_travel IMPLEMENTATION.
  METHOD save_modified.
    DATA lt_log TYPE STANDARD TABLE OF ztravel_log WITH EMPTY KEY.
    LOOP AT ____(다)____-travel INTO DATA(ls_create).
      APPEND VALUE #( travel_uuid = ls_create-TravelUUID action = 'C' ) TO lt_log.
    ENDLOOP.
    LOOP AT update-travel INTO DATA(ls_update)
         WHERE ____(라)____-OverallStatus = if_abap_behv=>mk-on.
      APPEND VALUE #( travel_uuid = ls_update-TravelUUID action = 'S' ) TO lt_log.
    ENDLOOP.
    IF lt_log IS NOT INITIAL.
      INSERT ztravel_log FROM TABLE @lt_log.
    ENDIF.
  ENDMETHOD.
ENDCLASS.
```

(5) 기존 BAPI(생성·변경)로 unmanaged BO를 만들 때 핸들러(create/update/delete/action, lock, read)와 세이버(check_before_save, save, cleanup)가 각각 무엇을 하는지 쓰시오.

(6) (5)에서 주의할 점을 5가지 쓰시오(커밋, DB 변경 시점, late save 실패 처리와 `sy-subrc`, 금지 문장, ABAP Cloud). 이 패턴의 /DMO/ 참조 예도 쓰시오.

<details><summary>정답·해설</summary>

**(1)**

| 유형 | 프레임워크 | 개발자 | 사용 상황 |
|---|---|---|---|
| managed | 트랜잭션 버퍼, CRUD, 잠금, ETag, DB 저장 | 업무 로직(determination, validation, action, 권한, 기능 제어) | 신규(greenfield) |
| unmanaged | 오케스트레이션(호출 순서)만 | 버퍼, create/update/delete/read/lock 핸들러, 세이버 save 등 전부(보통 레거시 API 호출) | 검증된 레거시 로직(FM, 클래스, 자체 버퍼)이 있는 brownfield |
| managed `with unmanaged save` | 버퍼와 CRUD | 저장(`save_modified`)만 직접, `persistent table` 지정 불가 | 저장만 BAPI·업데이트 FM·다른 구조 테이블로 해야 할 때 |
| managed `with additional save` | 버퍼, CRUD, 기본 저장 | 기본 저장에 추가할 로직(`save_modified`) | 변경 문서, 애플리케이션 로그, 비즈니스 이벤트 발행, 다른 테이블 동기화 |

**(2)** 아니다. 레거시 API가 생성·변경 로직을 다 가지고 있고 자체 버퍼가 있으면 unmanaged가 맞고, 저장 함수만 재사용하면 managed with unmanaged save가 더 간단하다.

**(3)** ③. ① unmanaged save에서는 `persistent table`을 지정할 수 없다 ② additional save는 기본 저장에 "추가", 대체는 unmanaged save ④ 기본은 키와 변경된 필드만, 전체가 필요하면 `with full data` ⑤ `define behavior for ... with unmanaged save`처럼 엔티티 단위로도 지정 가능.

**(4)** (가) `with additional save` (나) `save_modified` (다) `create` (라) `%control`. `create`/`update`/`delete`는 저장될 인스턴스를 담은 깊은 구조이고 기본은 키와 변경 필드만 있으므로, 다른 필드도 필요하면 `with additional save with full data`. managed 저장은 프레임워크가 이미 하므로 여기서는 추가 작업만 한다(로그 키 필드는 생략).

**(5)**
- 상호작용 단계(핸들러 create/update/delete/action): 요청 데이터를 자체 버퍼 클래스(싱글턴)에 쌓는다. 레거시 API에 자체 버퍼가 있으면 "버퍼에 기록" 함수를 부른다. 키를 레거시 API가 돌려주면 그대로(early), 저장 때 정해지면 late numbering.
- `lock`: 레거시 잠금 객체(ENQUEUE FM 또는 `CL_ABAP_LOCK_OBJECT_FACTORY`).
- `read`: 버퍼에 있으면 버퍼, 없으면 DB·레거시 읽기 API.
- `check_before_save`: BAPI 테스트(시뮬레이션) 모드나 자체 검사로 오류를 미리 찾아 `failed`/`reported`.
- `save`: BAPI를 실제 호출해 DB 반영, RETURN 메시지 확인.
- `cleanup`: 버퍼와 레거시 버퍼 초기화.

**(6)**
1. 핸들러·세이버 안에서 `COMMIT WORK`, `BAPI_TRANSACTION_COMMIT` 금지. 커밋은 RAP 프레임워크(또는 `COMMIT ENTITIES`)가 한다. 내부에서 커밋하는 BAPI는 쓸 수 없다.
2. DB 변경(BAPI의 실제 저장)은 late save(`save`)에서만. 상호작용 단계에서 부르면 SAP LUW가 깨지고 Draft·롤백이 동작하지 않는다.
3. 원칙상 late save는 실패하면 안 된다. 그래도 실패할 수 있으면 세이버를 `CL_ABAP_BEHAVIOR_SAVER_FAILED`에서 상속해 `failed`/`reported`를 채운다. 이때 `COMMIT ENTITIES` 후 `sy-subrc = 8`이고 계속하려면 `ROLLBACK ENTITIES`.
4. 화면 처리·`MESSAGE`(INTO 없이)·`CALL TRANSACTION`·`SUBMIT`이 든 레거시 코드는 쓸 수 없다.
5. ABAP Cloud(Tier 1)에서 쓰려면 BAPI를 Tier 2 래퍼로 감싸 C1 공개.
/DMO/ 예: unmanaged Travel의 `/DMO/FLIGHT_TRAVEL_CREATE`, `..._SAVE`, `..._INITIALIZE` 함수(레거시 버퍼 API를 감싸는 패턴).

</details>

---

## BDEF (행동 정의)

### C-022. BDEF 작성: Draft 루트 헤더, 필드 특성, 루트+자식 [작성] ★★★
<!-- src: RP-007, RP-010, RP-011 -->
(1) UUID 키를 쓰는 Draft 가능 Travel BO의 BDEF다. 빈칸을 채우시오.

```abap
managed implementation in class zbp_r_traveltp ____(가)____;
strict ( 2 );
with ____(나)____;

define behavior for ZR_TravelTP alias Travel
____(다)____ table ztravel_a
draft table ztravel_d
etag master LocalLastChangedAt
lock master ____(라)____ LastChangedAt
authorization master ( instance )
{
  create;
  update;
  delete;
  field ( readonly, ____(마)____ ) TravelUUID;
  field ( readonly ) TravelID, LocalLastChangedAt, LastChangedAt;
  field ( ____(바)____ ) CustomerID, BeginDate, EndDate;
  association _Booking { create; with draft; }
  draft action Edit;
  draft action Activate optimized;
  draft action Discard;
  draft action Resume;
  draft ____(사)____ action Prepare;
  ____(아)____ for ztravel_a corresponding
  {
    TravelUUID = travel_uuid;
    TravelID   = travel_id;
  }
}
```

(2) `unique`, `numbering : managed`, `mapping for ... corresponding`의 의미와, Draft BO에 꼭 필요한 BDEF 요소 세 가지(위치 규칙 포함)를 쓰시오.

(3) 필드 특성에 대해 옳지 **않은** 것을 고르고, ①~④를 정적/동적 기능 제어로 분류하시오.
① `field ( readonly ) TotalPrice;` 소비자는 값을 생성·변경할 수 없다.
② `field ( mandatory ) CustomerID;` 저장 전에 값이 있어야 한다.
③ `field ( readonly : update ) TravelID;` 생성할 때만 입력 가능. 외부 번호 키에 `mandatory : create`와 함께 쓴다.
④ `field ( features : instance ) BookingFee;` 인스턴스 상태에 따라 `get_instance_features`에서 정한다.
⑤ `field ( suppress ) Memo;` UI 화면에서만 숨기고 EML과 파생 타입에는 그대로 남는다.

(4) 다음 조건을 만족하는 BDEF를 작성하시오.
- 루트 `ZR_TravelTP`(alias `Travel`, 테이블 `ztravel_a`), 자식 `ZR_BookingTP`(alias `Booking`, 테이블 `zbooking_a`). 두 엔티티 모두 UUID 키(`TravelUUID`, `BookingUUID`)를 프레임워크가 채운다.
- managed, strict 2, Draft 없음, 구현 클래스 `zbp_r_traveltp`.
- 루트: 생성·수정·삭제, ETag `LocalLastChangedAt`, 전역 권한 검사, Booking을 루트를 통해 생성. `TotalPrice`는 읽기 전용.
- 자식: 수정·삭제, 잠금·권한은 부모를 따름, ETag `LocalLastChangedAt`, 부모 키 `TravelUUID`는 소비자가 바꿀 수 없음.
- `BookingFee`가 바뀌면 바로 총액을 다시 계산하는 determination `recalcTotalPrice`, 생성 시 또는 `CustomerID`가 바뀌면 저장 때 검사하는 validation `validateCustomer`.

(5) (4)에 Draft를 켜려면 추가해야 할 것을 모두 쓰시오.

<details><summary>정답·해설</summary>

**(1)** (가) `unique` (나) `draft` (다) `persistent` (라) `total etag` (마) `numbering : managed` (바) `mandatory` (사) `determine` (아) `mapping`

**(2)** `unique`: 각 동작을 한 번만 구현한다는 뜻으로 필수. `numbering : managed`: 16바이트 UUID 키를 프레임워크가 채움(`readonly`와 함께). `mapping for`: CDS 요소 이름(CamelCase)과 테이블 필드 이름이 다를 때 필요하고, `corresponding`은 이름이 같은 필드를 자동 매핑. Draft BO 필수: `with draft;`(헤더), `draft table`, `total etag`(`lock master` 뒤에 씀). 그 밖에 draft action들과 association의 `with draft`.

**(3)** ⑤ — `suppress`는 필드를 BDEF 파생 타입과 모든 RAP API에서 제거한다. UI 숨김은 `@UI.hidden` 같은 어노테이션. ①~③은 정적, ④만 동적 기능 제어.

**(4)**

```abap
managed implementation in class zbp_r_traveltp unique;
strict ( 2 );

define behavior for ZR_TravelTP alias Travel
persistent table ztravel_a
lock master
authorization master ( global )
etag master LocalLastChangedAt
{
  create;
  update;
  delete;

  field ( readonly, numbering : managed ) TravelUUID;
  field ( readonly ) TotalPrice, LocalLastChangedAt;

  association _Booking { create; }

  determination recalcTotalPrice on modify { field BookingFee; }
  validation validateCustomer on save { create; field CustomerID; }
}

define behavior for ZR_BookingTP alias Booking
persistent table zbooking_a
lock dependent by _Travel
authorization dependent by _Travel
etag master LocalLastChangedAt
{
  update;
  delete;

  field ( readonly, numbering : managed ) BookingUUID;
  field ( readonly ) TravelUUID;

  association _Travel;
}
```

채점 포인트: `unique`, `strict ( 2 )`, 루트 `lock master`·`authorization master`, 자식 `lock dependent by`·`authorization dependent by`, `association _Booking { create; }`(create-by-association), 자식에 `create;` 없음, `numbering : managed` + `readonly`, determination `on modify`(즉시 계산), validation `on save`. 테이블 필드명이 CDS 요소명과 다르면 `mapping for` 블록도 필요하다.

**(5)** 헤더 `with draft;`, 루트·자식 각각 `draft table`, 루트 `lock master total etag LastChangedAt`, draft action(Edit, Activate optimized, Discard, Resume, `draft determine action Prepare { validation validateCustomer; }`), `association _Booking { create; with draft; }`, 자식의 `association _Travel { with draft; }`, 프로젝션 BDEF의 `use draft;`.

</details>

---

### C-023. BDEF 오류 찾기와 동시성 제어(ETag·잠금) [코드] ★★★
<!-- src: RP-009, MX-058, RP-008, RB-089 -->
다음 BDEF에는 활성화 시 오류가 되는 곳이 있다.

```abap
managed with unmanaged save implementation in class zbp_r_traveltp unique;
strict ( 2 );

define behavior for ZR_TravelTP alias Travel
persistent table ztravel_a
lock master
etag master LocalLastChangedAt
authorization master ( instance )
{
  create; update; delete;
  field ( readonly, numbering : managed ) TravelUUID;
  determination setTravelID on save { create; }
  association _Booking { create; }
}

define behavior for ZR_BookingTP alias Booking
etag master LocalLastChangedAt
authorization dependent by _Travel
{
  create; update; delete;
  field ( readonly ) TravelUUID;
  association _Travel;
}
```

(1) 오류 세 곳을 찾아 고치시오. 반대로 프레임워크 저장을 쓰려면 무엇을 바꿔야 하는지도 쓰시오.

(2) 루트·자식 BDEF의 그 밖의 규칙(total etag, authorization master, 자식 생성 방식)을 쓰시오.

(3) 고친 BDEF에 대해 옳지 **않은** 것을 고르시오.
① Booking 인스턴스를 바꾸면 잠금은 상위 Travel 인스턴스에 걸린다.
② Booking의 권한 검사는 Travel의 권한 구현을 따른다.
③ Booking도 자기 필드로 etag master를 지정할 수 있다.
④ `lock dependent by _Travel`을 쓰려면 Booking BDEF에 `association _Travel`이 선언돼 있어야 한다.
⑤ Booking에 `create;`를 두면 Booking을 Travel과 상관없이 단독으로 생성할 수 있다.

(4) `etag master`, `etag dependent by`, `total etag`, `lock master`, `lock dependent by`가 각각 무엇을 위한 것인지 낙관적·비관적 동시성 제어와 연결해 설명하고, 각 필드에 붙일 CDS 어노테이션을 쓰시오. managed와 unmanaged에서 잠금·ETag 처리 주체도 쓰시오.

(5) `lock master unmanaged`로 선언한 BO에서 잠금 객체 `EZTRAVEL`로 Travel을 잠그는 핸들러다. 빈칸을 채우시오.

```abap
METHOD lock.   " METHODS lock FOR LOCK IMPORTING keys FOR LOCK Travel.
  TRY.
      DATA(lo_lock) = cl_abap_lock_object_factory=>____(가)____( iv_name = 'EZTRAVEL' ).
    CATCH cx_abap_lock_failure.
      RETURN.
  ENDTRY.
  LOOP AT keys INTO DATA(ls_key).
    TRY.
        lo_lock->____(나)____(
          it_parameter = VALUE #( ( name = 'TRAVEL_ID' value = REF #( ls_key-TravelID ) ) ) ).
      CATCH ____(다)____ INTO DATA(lx_foreign).
        APPEND VALUE #( %tky = ls_key-%tky ) TO ____(라)____-travel.
        APPEND VALUE #( %tky = ls_key-%tky
                        %msg = new_message_with_text(
                                 severity = if_abap_behv_message=>severity-error
                                 text     = |Locked by { lx_foreign->user_name }| ) )
               TO reported-travel.
      CATCH cx_abap_lock_failure.
        APPEND VALUE #( %tky = ls_key-%tky ) TO failed-travel.
    ENDTRY.
  ENDLOOP.
ENDMETHOD.
```

(6) (5)에서 `ENQUEUE_EZ...` FM 대신 이 클래스를 쓰는 이유, 잠금 해제 시점, 이미 잠긴 경우의 `%fail-cause`, managed BO에서 이 메서드가 필요한지를 쓰시오.

<details><summary>정답·해설</summary>

**(1)**
1. `with unmanaged save`와 `persistent table`은 함께 쓸 수 없다 → `persistent table ztravel_a` 삭제(저장은 세이버 `save_modified`에서 직접).
2. 자식 Booking에 잠금 정의가 없다. 루트가 `lock master`이면 자식은 잠금 종속 → `lock dependent by _Travel` 추가.
3. 자식에 `create;`를 직접 선언할 수 없다(composition 자식은 부모의 `association _Booking { create; }`로만 생성) → `create;` 삭제.
반대로 프레임워크 저장을 쓰려면 헤더에서 `with unmanaged save`를 빼고, 자식에도 `persistent table zbooking_a`를 지정한다.

**(2)** `total etag`는 Draft BO에서 필수이고 `lock master` 뒤에 온다. 루트에는 `authorization master`가 반드시 있고, 자식은 `authorization dependent by` 또는 자체 `authorization master`. 자식은 create-by-association으로 만든다.

**(3)** ⑤ — 자식에 단독 `create`를 쓰면 문법 오류다. ①② 잠금·권한은 루트(master)가 책임 ③ etag는 엔티티마다 따로 둘 수 있다 ④ dependent 관계를 따라갈 association이 BDEF에 있어야 한다.

**(4)**
- `etag master <필드>`: **낙관적** 동시성 제어. 클라이언트가 읽을 때 받은 ETag를 수정 요청에 보내고, 서버 값과 다르면(그 사이 누가 바꿨으면) 거부. 인스턴스 단위. `@Semantics.systemDateTime.localInstanceLastChangedAt: true`.
- `etag dependent by _Assoc`: 자식이 부모의 ETag를 사용.
- `total etag <필드>`: Draft BO에서만 필수. Draft의 배타 잠금이 만료된 뒤(낙관적 잠금 단계) Resume할 수 있는지, 즉 Draft를 만든 뒤 활성 데이터가 바뀌지 않았는지를 BO 전체 단위로 비교. `@Semantics.systemDateTime.lastChangedAt: true`. `lock master` 뒤에 쓰고 `etag master`와 다른 필드 권장.
- `lock master`: **비관적** 동시성 제어. 수정 전에 전역 잠금 테이블에 배타 잠금. 루트에 지정.
- `lock dependent by _Travel`: 자식은 루트의 잠금을 따른다(자식 수정 시 루트 인스턴스가 잠김).
- managed BO는 잠금과 ETag 비교를 자동 처리(update, delete, create-by-association, action). unmanaged는 `lock master unmanaged` 또는 unmanaged BO에서 `lock` 메서드를 직접 구현.

**(5)** (가) `get_instance` (나) `enqueue` (다) `cx_abap_foreign_lock` (라) `failed`

**(6)** ABAP Cloud에서는 `ENQUEUE_EZ...` FM 대신 공개 API `CL_ABAP_LOCK_OBJECT_FACTORY`를 쓴다. 잠금은 RAP가 저장·롤백 뒤에 자동으로 풀어 준다. 다른 사용자가 잠갔으면 `failed`(`%fail-cause`는 보통 `if_abap_behv=>cause-locked`)와 메시지. managed BO는 `lock master`만 쓰면 프레임워크가 잠금을 처리하므로 이 메서드가 필요 없다.

</details>

---

## 번호 부여·Determination·Validation·Action

### C-024. 키 번호 부여: managed·외부·early·late [코드] ★★★
<!-- src: RP-012, RP-013, RB-072, RB-073, MX-059, MX-060 -->
(1) 상황 (가)~(라)에 맞는 번호 부여 방식을 쓰고, 각 방식의 BDEF 문법과 구현 위치를 쓰시오.
- (가) 키가 UUID이고 프레임워크가 생성할 때 자동으로 채운다.
- (나) 사용자가 생성 화면에서 키를 직접 입력한다.
- (다) 생성 요청을 처리하는 즉시 핸들러 메서드에서 번호 범위로 키를 부여한다.
- (라) 저장 직전에 최종 번호를 부여해 번호 사이에 빈 번호가 생기지 않게 한다.

(2) `early numbering`을 지정한 Travel의 번호 부여 메서드다. 빈칸을 채우시오.

```abap
CLASS lhc_travel DEFINITION INHERITING FROM ____(1)____.
  PRIVATE SECTION.
    METHODS earlynumbering_create FOR ____(2)____
      IMPORTING entities FOR CREATE Travel.
ENDCLASS.

CLASS lhc_travel IMPLEMENTATION.
  METHOD earlynumbering_create.
    DATA max_id TYPE /dmo/travel_id.
    " 이미 키가 있는 인스턴스는 그대로 반환 (Draft에서 재호출 대비)
    LOOP AT entities INTO DATA(entity) WHERE TravelID IS NOT INITIAL.
      APPEND CORRESPONDING #( entity ) TO ____(3)____-travel.
    ENDLOOP.
    SELECT SINGLE FROM ztravel_a FIELDS MAX( travel_id ) INTO @max_id.
    LOOP AT entities INTO entity WHERE TravelID IS INITIAL.
      max_id += 1.
      APPEND VALUE #( ____(4)____ = entity-%cid
                      %is_draft  = entity-%is_draft
                      TravelID   = max_id ) TO ____(3)____-travel.
    ENDLOOP.
  ENDMETHOD.
ENDCLASS.
```

(3) (2)에서 첫 번째 LOOP가 필요한 이유, 핸들러와 세이버 클래스가 상속하는 클래스, 결과를 돌려주는 방식, 실무에서 `MAX + 1` 대신 쓰는 것과 Draft BO에서 추가로 봐야 할 것을 쓰시오.

(4) TravelID를 저장 직전에 번호 범위로 매기는 late numbering이다. 빈칸을 채우시오.

```
define behavior for ZR_Travel alias Travel
persistent table ztravel_a
lock master
authorization master ( instance )
____(5)____
{
  create; update; delete;
  field ( readonly ) TravelID;
}
```

```abap
CLASS lsc_zr_travel DEFINITION INHERITING FROM cl_abap_behavior_saver.
  PROTECTED SECTION.
    METHODS ____(6)____ REDEFINITION.
ENDCLASS.

CLASS lsc_zr_travel IMPLEMENTATION.
  METHOD adjust_numbers.
    LOOP AT ____(7)____-travel ASSIGNING FIELD-SYMBOL(<ls_travel>).
      TRY.
          cl_numberrange_runtime=>____(8)____(
            EXPORTING nr_range_nr = '01'
                      object      = 'ZTRAVEL'
                      quantity    = 1
            IMPORTING number      = DATA(lv_number) ).
        CATCH cx_number_ranges.
          " 번호를 못 받으면 저장 불가: early save 단계에서 미리 확인해 두어야 한다
      ENDTRY.
      <ls_travel>-TravelID = lv_number.
    ENDLOOP.
  ENDMETHOD.
ENDCLASS.
```

(5) `adjust_numbers`의 호출 시점과 `mapped`에 들어 있는 것, 최종 키가 정해지기 전에 인스턴스를 식별하는 컴포넌트, 소비자가 최종 키를 얻는 문법을 쓰시오. 위 코드를 `SELECT MAX`로 바꾸면 위험한 이유도 쓰시오.

(6) Draft BO에서 early numbering과 late numbering의 차이(번호 공백)를 쓰고, late numbering이 필요한 업무 예와 Draft 테이블에 추가로 필요한 필드를 쓰시오. 기술 키와 의미 키를 나누는 흔한 설계도 쓰시오.

<details><summary>정답·해설</summary>

**(1)**

| 상황 | 방식 | BDEF | 구현 위치 |
|---|---|---|---|
| (가) | managed internal early | `field ( readonly, numbering : managed ) TravelUUID;` | 없음. 키가 16바이트 RAW(UUID), managed BO 전용 |
| (나) | 외부(external) early | 지정 없음(기본), 키에 `field ( mandatory : create, readonly : update )` 권장 | 없음(유일성은 소비자 책임) |
| (다) | unmanaged internal early | `early numbering` | 핸들러 `FOR NUMBERING` 메서드에서 `mapped`에 `%cid`와 새 키 |
| (라) | late numbering | `late numbering` | 세이버 `adjust_numbers`(late save phase), 그 전까지 `%pid`/임시 키 |

**(2)** (1) `cl_abap_behavior_handler` (2) `NUMBERING` (3) `mapped` (4) `%cid`

**(3)** early numbering 메서드는 Draft에서 같은 인스턴스에 다시 호출될 수 있으므로 이미 키가 있는 인스턴스는 건너뛰게(멱등) 구현한다. 핸들러(`lhc_`)는 `CL_ABAP_BEHAVIOR_HANDLER`, 세이버(`lsc_`)는 `CL_ABAP_BEHAVIOR_SAVER`를 상속. 결과는 `mapped`에 "요청의 `%cid` ↔ 새 키" 쌍. 실무에서는 번호 범위(`cl_numberrange_runtime=>number_get`)를 쓰고, Draft BO라면 Draft 테이블의 최대값도 함께 본다.

**(4)** (5) `late numbering` (6) `adjust_numbers` (7) `mapped` (8) `number_get`

**(5)** `adjust_numbers`는 late save phase에서 `save` 직전에 한 번 호출된다(late numbering일 때만). `mapped`에는 새 인스턴스들이 임시 식별자(`%pre` = `%pid` + `%tmp`)와 함께 들어 있고 여기서 `%key`(최종 키)를 채운다. 식별: `%pid`(임시 ID, 임시 키는 `%tmp`, `%tky`에 `%pid` 포함). 최종 키: `COMMIT ENTITIES BEGIN ... CONVERT KEY OF ... END`. late save는 실패하면 안 되므로 번호 범위 확인 같은 위험은 미리 처리한다. `SELECT MAX`는 동시에 저장하는 두 트랜잭션이 같은 MAX를 읽어 키가 겹칠 수 있어 위험하다 → 번호 범위 객체.

**(6)** early numbering은 Draft 생성 시 번호가 확정되어, Draft를 버리면(Discard) 그 번호는 쓰이지 않아 공백이 생긴다. late numbering은 활성화(저장) 직전에 매기므로 공백이 없다. 업무 예: 법적 문서 번호, 회계 전표처럼 "실제로 저장되는 것만 번호를 받아야" 하는 경우. late numbering + Draft면 Draft 테이블에 `DRAFTUUID`(16바이트) 키 필드가 추가로 필요하다. 설계: 내부 기술 키는 managed UUID(early)로, 사람이 보는 의미 키(TravelID)는 별도 필드로 두고 determination이나 late numbering으로 매긴다.

</details>

---

### C-025. Determination·Validation: 실행 시점 추적과 핸들러 선언 [개념] ★★★
<!-- src: RP-014, RP-015, RP-016, RP-020, RB-090 -->
Draft 없는 managed BO `ZR_TravelTP`(alias `Travel`)의 BDEF 일부다. (1)~(6)은 모두 이 BO를 기준으로 한다.

```abap
determination setStatusToOpen on modify { create; }
determination calcTotalPrice  on modify { field BookingFee, CurrencyCode; }
determination setTravelNumber on save   { create; }
validation validateCustomer   on save   { create; field CustomerID; }
validation validateDates      on save   { create; field BeginDate, EndDate; }
```

(1) determination과 validation의 목적, 실행 시점(`on modify`/`on save`), 트리거 조건, 결과를 돌려주는 방법(사용하는 응답 파라미터)을 표로 비교하시오.

(2) `on modify` determination과 `on save` determination을 각각 어떤 경우에 쓰는지 예를 하나씩 드시오. 여러 determination의 실행 순서는 보장되는지, Draft BO에서 validation이 활성화 전에 실행되게 하려면 BDEF에 무엇이 필요한지도 쓰시오.

(3) DB에 이미 저장된 Travel 인스턴스 하나(키 `k`)에 대해 외부 소비자가 아래를 순서대로 실행한다. 모든 문장은 성공한다고 가정한다. 각 EML 문 직후 실행되는 것과 `COMMIT ENTITIES` 때 실행되는 것을 쓰시오.

```abap
" (a)
MODIFY ENTITIES OF zr_traveltp ENTITY Travel
  UPDATE FIELDS ( Description ) WITH VALUE #( ( TravelUUID = k Description = 'Trip' ) ).
" (b)
MODIFY ENTITIES OF zr_traveltp ENTITY Travel
  UPDATE FIELDS ( BookingFee ) WITH VALUE #( ( TravelUUID = k BookingFee = 40 ) ).
" (c)
MODIFY ENTITIES OF zr_traveltp ENTITY Travel
  UPDATE FIELDS ( CustomerID ) WITH VALUE #( ( TravelUUID = k CustomerID = '000042' ) ).
" (d)
COMMIT ENTITIES.
```

(4) 이 BO의 행동 구현 클래스에 있는 로컬 핸들러 선언부다. 빈칸 1~5를 채우고, 전역 권한 메서드의 선언은 인스턴스 권한과 무엇이 다른지 쓰시오.

```abap
CLASS lhc_travel DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    METHODS get_instance_features FOR INSTANCE ____(1)____
      IMPORTING keys REQUEST requested_features FOR Travel RESULT result.

    METHODS get_instance_authorizations FOR INSTANCE ____(2)____
      IMPORTING keys REQUEST requested_authorizations FOR Travel RESULT result.

    METHODS setStatusToOpen FOR ____(3)____ ON MODIFY
      IMPORTING keys FOR Travel~setStatusToOpen.

    METHODS validateDates FOR ____(4)____ ON SAVE
      IMPORTING keys FOR Travel~validateDates.

    METHODS acceptTravel FOR MODIFY
      IMPORTING keys FOR ____(5)____ Travel~acceptTravel RESULT result.
ENDCLASS.
```

(5) 한 트랜잭션에서 Travel 3건을 새로 만들고 `COMMIT ENTITIES`를 실행했다. 이번에는 아래 `validateDates` 구현만 동작한다고 가정한다. (가) `failed-travel`의 줄 수, (나) `reported-travel`의 줄 수와 그중 `%msg`가 있는 줄 수, (다) `COMMIT ENTITIES` 직후 `sy-subrc`, (라) DB에 저장된 Travel 건수를 쓰시오.

| 인스턴스 | BeginDate | EndDate |
|---|---|---|
| T1 | 20261101 | 20261105 |
| T2 | (초기값) | 20261110 |
| T3 | 20261120 | 20261115 |

```abap
METHOD validateDates.
  READ ENTITIES OF zr_traveltp IN LOCAL MODE
    ENTITY Travel FIELDS ( BeginDate EndDate ) WITH CORRESPONDING #( keys )
    RESULT DATA(travels).

  LOOP AT travels INTO DATA(travel).
    APPEND VALUE #( %tky = travel-%tky %state_area = 'DATES' ) TO reported-travel.

    IF travel-BeginDate IS INITIAL OR travel-EndDate IS INITIAL.
      APPEND VALUE #( %tky = travel-%tky ) TO failed-travel.
      APPEND VALUE #( %tky = travel-%tky %state_area = 'DATES'
                      %msg = new_message_with_text(
                               severity = if_abap_behv_message=>severity-error
                               text     = 'Date missing' ) ) TO reported-travel.
    ELSEIF travel-EndDate < travel-BeginDate.
      APPEND VALUE #( %tky = travel-%tky ) TO failed-travel.
      APPEND VALUE #( %tky = travel-%tky %state_area = 'DATES'
                      %msg = new_message_with_text(
                               severity = if_abap_behv_message=>severity-error
                               text     = 'End before begin' ) ) TO reported-travel.
    ENDIF.
  ENDLOOP.
ENDMETHOD.
```

(6) determine action에 대한 설명으로 옳지 **않은** 것을 고르고 이유를 쓰시오.

① determine action은 등록된 determination·validation을 요청 시점에 실행한다.
② `draft determine action Prepare`는 determine action의 일종이다.
③ determine action에는 `on modify` determination도 등록할 수 있다.
④ side effects에서 `determine action ... executed on field ...`로 필드가 바뀔 때 실행하게 할 수 있다.
⑤ 소비자는 EML `EXECUTE`로 determine action을 호출할 수 있다.

<details><summary>정답·해설</summary>

**(1)**

| | determination | validation |
|---|---|---|
| 목적 | 인스턴스 값을 계산해 **바꾼다** | 값을 **검사만** 한다 |
| 실행 시점 | `on modify`: 상호작용 단계, 변경 직후 즉시 / `on save`: 저장 시퀀스의 `finalize` | `on save`만 있음: 저장 시퀀스의 `check_before_save` |
| 트리거 | `create`, `update`, `delete`, `field 필드명` | 같음 |
| 구현 메서드 | `FOR DETERMINE ON MODIFY` / `FOR DETERMINE ON SAVE` | `FOR VALIDATE ON SAVE` |
| 결과 전달 | 데이터 변경(`MODIFY ENTITIES IN LOCAL MODE`), 메시지는 `reported` | `failed`(저장 차단) + `reported`(메시지) |

트리거를 여러 개 쓰면 하나라도 만족할 때 실행된다. `on save`에서는 `update`를 `create` 없이 단독으로 쓸 수 없다. validation이 하나라도 실패하면 트랜잭션 버퍼 전체가 저장되지 않는다(all or nothing).

**(2)** `on modify` 예: 생성 시 상태를 'O'로 기본 설정(`setStatusToOpen`), BookingFee가 바뀌면 총액 재계산(화면에 바로 보여야 함). `on save` 예: 저장할 때 사람이 읽는 문서 번호 부여(`setTravelNumber`), 저장 직전에만 의미 있는 최종 계산. 여러 determination의 실행 순서는 **보장되지 않는다**. Draft BO에서는 `draft determine action Prepare { validation validateDates; ... }`에 등록해야 Draft 활성화 전에 검사가 이루어진다.

**(3)**
- (a) 직후: 없음. `Description`은 어떤 트리거에도 없다.
- (b) 직후: `calcTotalPrice`. `BookingFee`가 트리거 필드이고 `on modify`라 변경 직후 바로 실행된다.
- (c) 직후: 없음. `CustomerID`는 `validateCustomer`의 트리거지만 validation은 `on save`라 저장 때로 미뤄진다.
- (d) `COMMIT ENTITIES`: `validateCustomer`만 실행된다. 저장 시퀀스는 트랜잭션 동안 쌓인 변경을 평가한다. 기존 인스턴스라 `create` 트리거는 해당 없으므로 `setTravelNumber`(on save, create만)는 실행되지 않는다. `BeginDate`/`EndDate`는 바뀌지 않아 `validateDates`도 실행되지 않는다.

**(4)** 1. `FEATURES` 2. `AUTHORIZATION` 3. `DETERMINE` 4. `VALIDATE` 5. `ACTION`

전역 권한은 `METHODS get_global_authorizations FOR GLOBAL AUTHORIZATION IMPORTING REQUEST requested_authorizations FOR Travel RESULT result.`처럼 `keys`가 없다(인스턴스와 무관). 이 메서드들은 ADT 퀵픽스로 자동 생성되며, `failed`/`reported`/`mapped` 같은 응답 파라미터는 선언에 쓰지 않아도 메서드 종류에 맞게 암묵적으로 제공된다.

**(5)** (가) 2줄(T2, T3) (나) 5줄, 그중 `%msg`가 있는 줄 2줄 (다) 4 (라) 0건
- T1: state area 정리용 줄 1개만 추가된다. 날짜 정상.
- T2: 정리용 1줄 + BeginDate가 초기값이라 첫 IF에 걸려 failed 1줄, 메시지 1줄.
- T3: 정리용 1줄 + 20261115 < 20261120이라 ELSEIF에 걸려 failed 1줄, 메시지 1줄.
- reported = 정리용 3 + 메시지 2 = 5, failed = 2.
- validation 실패는 early save phase(`check_before_save`)에서 일어나므로 `COMMIT ENTITIES`는 `sy-subrc = 4`를 돌려주고 상호작용 단계로 돌아간다. 버퍼 전체가 거부되므로 정상인 T1도 저장되지 않는다. 버퍼는 남아 있어 소비자는 값을 고쳐 다시 커밋하거나 `ROLLBACK ENTITIES`를 할 수 있다.

**(6)** ③. determine action에는 `on save` determination과 validation만 등록할 수 있다. `on modify` determination은 이미 변경 즉시 실행되기 때문이다. 대표 사용 예는 저장 전에 화면에서 검사 결과를 바로 보여 주고 싶을 때 side effect와 연결해 validation을 미리 실행하는 것이다.

</details>

---

### C-026. Validation·Determination 구현과 오류 수정 [작성] ★★★
<!-- src: RP-017, RP-018, RP-019 -->
Draft 가능한 Travel BO(`ZR_TravelTP`, alias `Travel`, 자식 Booking은 association `_Booking`)의 행동 구현을 작성한다.

(1) validation `validateDates`를 구현하시오.
- 시작일(`BeginDate`)이나 종료일(`EndDate`)이 비었으면 오류
- 종료일이 시작일보다 앞서면 오류
- 시작일이 오늘보다 이전이면 오류(오늘 날짜는 `cl_abap_context_info=>get_system_date( )`)
- 오류는 해당 필드에 표시하고, 사용자가 고친 뒤 다시 검사하면 이전 메시지가 사라져야 한다(state area `'VALIDATE_DATES'`).
- 메시지는 `new_message_with_text( )`로 만든다.

(2) (1)이 Draft 활성화 전에 실행되도록 BDEF에 필요한 두 줄을 쓰시오.

(3) 다음 validation에서 잘못된 곳 세 가지를 찾아 이유와 함께 고치시오.

```abap
METHOD validateCustomer.
  READ ENTITIES OF zr_traveltp IN LOCAL MODE
    ENTITY Travel FIELDS ( CustomerID ) WITH CORRESPONDING #( keys )
    RESULT DATA(travels).

  LOOP AT travels INTO DATA(travel).
    SELECT SINGLE @abap_true FROM /dmo/customer
      WHERE customer_id = @travel-CustomerID
      INTO @DATA(exists).

    IF exists = abap_false.
      " 잘못된 고객은 기본 고객으로 바꿔서 저장되게 한다
      MODIFY ENTITIES OF zr_traveltp IN LOCAL MODE
        ENTITY Travel UPDATE FIELDS ( CustomerID )
        WITH VALUE #( ( %tky = travel-%tky CustomerID = '000001' ) ).

      APPEND VALUE #( %tky = travel-%tky
                      %msg = new_message_with_text(
                               severity = if_abap_behv_message=>severity-error
                               text     = 'Customer unknown' ) ) TO reported-travel.
    ENDIF.
  ENDLOOP.
ENDMETHOD.
```

(4) `determination recalcTotalPrice on modify { field BookingFee; }`를 구현하시오. 총액(`TotalPrice`) = Travel의 `BookingFee` + 하위 Booking들의 `FlightPrice` 합계다(통화는 모두 같다고 가정). `TotalPrice`는 BDEF에서 `readonly`다.

(5) (4)에서 `readonly` 필드를 수정할 수 있는 이유를 쓰시오. Booking의 `FlightPrice`가 바뀔 때도 총액을 다시 계산하려면 어떻게 설계하는지 쓰시오.

<details><summary>정답·해설</summary>

**(1)** 예시

```abap
METHOD validateDates.
  READ ENTITIES OF zr_traveltp IN LOCAL MODE
    ENTITY Travel
      FIELDS ( BeginDate EndDate )
      WITH CORRESPONDING #( keys )
    RESULT DATA(travels).

  DATA(today) = cl_abap_context_info=>get_system_date( ).

  LOOP AT travels INTO DATA(travel).
    " 이전 상태 메시지 제거
    APPEND VALUE #( %tky        = travel-%tky
                    %state_area = 'VALIDATE_DATES' ) TO reported-travel.

    IF travel-BeginDate IS INITIAL OR travel-EndDate IS INITIAL.
      APPEND VALUE #( %tky = travel-%tky ) TO failed-travel.
      APPEND VALUE #( %tky        = travel-%tky
                      %state_area = 'VALIDATE_DATES'
                      %msg        = new_message_with_text(
                                      severity = if_abap_behv_message=>severity-error
                                      text     = 'Begin and end date are required' )
                      %element-BeginDate = if_abap_behv=>mk-on
                      %element-EndDate   = if_abap_behv=>mk-on ) TO reported-travel.
    ELSEIF travel-EndDate < travel-BeginDate.
      APPEND VALUE #( %tky = travel-%tky ) TO failed-travel.
      APPEND VALUE #( %tky        = travel-%tky
                      %state_area = 'VALIDATE_DATES'
                      %msg        = new_message_with_text(
                                      severity = if_abap_behv_message=>severity-error
                                      text     = 'End date before begin date' )
                      %element-EndDate = if_abap_behv=>mk-on ) TO reported-travel.
    ELSEIF travel-BeginDate < today.
      APPEND VALUE #( %tky = travel-%tky ) TO failed-travel.
      APPEND VALUE #( %tky        = travel-%tky
                      %state_area = 'VALIDATE_DATES'
                      %msg        = new_message_with_text(
                                      severity = if_abap_behv_message=>severity-error
                                      text     = 'Begin date must not be in the past' )
                      %element-BeginDate = if_abap_behv=>mk-on ) TO reported-travel.
    ENDIF.
  ENDLOOP.
ENDMETHOD.
```

채점 포인트: ① `IN LOCAL MODE`로 필요한 필드만 읽기 ② `%tky` 사용(Draft와 활성 인스턴스 구분) ③ 실패 시 `failed`와 `reported` 둘 다 채우기 ④ `%element`로 필드 표시 ⑤ 루프 첫머리에서 같은 `%state_area`로 메시지 없는 줄을 넣어 이전 상태 메시지 삭제 ⑥ 데이터 변경(MODIFY) 없음.

**(2)**
```abap
validation validateDates on save { create; field BeginDate, EndDate; }
draft determine action Prepare { validation validateDates; }
```

**(3)**
1. validation 안에서 `MODIFY ENTITIES`로 데이터를 바꾼다. validation은 검사만 하는 읽기 전용 로직이고, 수정은 RAP BO 계약 위반이라 허용되지 않는다(금지된 문장으로 오류). → MODIFY를 지운다. 값 보정이 필요하면 determination으로 옮긴다.
2. 메시지를 `reported`에만 넣고 `failed`에 넣지 않아 저장이 막히지 않는다. → `APPEND VALUE #( %tky = travel-%tky ) TO failed-travel.`을 추가한다. 메시지에 `%element-CustomerID = if_abap_behv=>mk-on`도 넣으면 좋다.
3. 루프 안에서 `SELECT SINGLE`을 반복한다(성능). 또 `exists`가 이전 반복의 값을 유지할 수 있다. SELECT가 실패하면 대상 변수가 바뀌지 않으므로, 첫 Travel의 고객이 있어 `exists = abap_true`가 되면 두 번째 Travel의 고객이 없어도 `abap_true`로 남아 오류를 놓친다. → 루프 전에 고객 ID를 모아 한 번에 읽고(`FOR ALL ENTRIES` 또는 내부 테이블 조인) 루프에서는 `line_exists( )`로 확인한다. 고객 ID가 비어 있는 경우도 따로 처리하는 것이 좋다.

**(4)** 예시

```abap
METHOD recalcTotalPrice.
  READ ENTITIES OF zr_traveltp IN LOCAL MODE
    ENTITY Travel
      FIELDS ( BookingFee ) WITH CORRESPONDING #( keys )
      RESULT DATA(travels)
    ENTITY Travel BY \_Booking
      FIELDS ( TravelUUID FlightPrice ) WITH CORRESPONDING #( keys )
      RESULT DATA(bookings).

  DATA upd TYPE TABLE FOR UPDATE zr_traveltp\\Travel.

  LOOP AT travels INTO DATA(travel).
    DATA(total) = travel-BookingFee.
    LOOP AT bookings INTO DATA(booking) WHERE TravelUUID = travel-TravelUUID.
      total += booking-FlightPrice.
    ENDLOOP.
    APPEND VALUE #( %tky = travel-%tky TotalPrice = total ) TO upd.
  ENDLOOP.

  MODIFY ENTITIES OF zr_traveltp IN LOCAL MODE
    ENTITY Travel
      UPDATE FIELDS ( TotalPrice ) WITH upd
    REPORTED DATA(upd_reported).

  reported = CORRESPONDING #( DEEP upd_reported ).
ENDMETHOD.
```

채점 포인트: ① `IN LOCAL MODE` ② `BY \_Booking`으로 자식 읽기 ③ `UPDATE FIELDS ( TotalPrice )`로 `%control` 설정 ④ `%tky` 사용 ⑤ `reported` 전달(`DEEP`). `total`의 타입은 `BookingFee`에서 추론되므로 합계 자릿수가 충분한지 확인한다.

**(5)** `IN LOCAL MODE`에서는 기능 제어(readonly 포함)와 권한 검사를 건너뛴다. `readonly`는 소비자에게만 적용되고, BO 내부 구현은 이 필드를 바꿀 수 있다. Booking의 `FlightPrice` 변경에도 반응하려면 Booking 엔티티에 `determination ... on modify { field FlightPrice; }`를 두고, 공통 로직을 internal action(예: `internal action reCalcTotalPrice;`)으로 빼서 Travel과 Booking 양쪽 determination에서 호출한다.

</details>

---

### C-027. Action: 종류, 파라미터 action, 인스턴스 action, factory action [코드] ★★
<!-- src: RP-021, RP-022, RP-023, MX-065 -->
Travel BO에 action을 추가한다.

(1) RAP action의 종류(instance, static, factory, internal, 파라미터·결과가 있는 action)를 BDEF 예와 함께 설명하시오. action에 붙일 수 있는 옵션과, UI에 버튼으로 보이게 하는 조건도 쓰시오.

(2) function은 action과 무엇이 다른지 쓰시오. Draft 전용 action(Edit, Activate, Discard, Resume, Prepare)이 각각 무엇을 하는지 쓰시오.

(3) BDEF에 `action acceptTravel result [1] $self;`가 있다(BO 이름 `zmx_r_travel`). 선언과 구현의 빈칸 1~5를 채우고, 1번과 2번을 쓰는 이유를 쓰시오.

```abap
" 선언
METHODS acceptTravel FOR MODIFY
  IMPORTING keys ____(5)____ Travel~acceptTravel RESULT result.

" 구현
METHOD acceptTravel.
  MODIFY ENTITIES OF zmx_r_travel ____(1)____
    ENTITY Travel
      UPDATE FIELDS ( OverallStatus )
      WITH VALUE #( FOR key IN keys
                    ( ____(2)____ = key-%tky
                      OverallStatus = 'A' ) ).

  READ ENTITIES OF zmx_r_travel IN LOCAL MODE
    ENTITY Travel
      ALL FIELDS WITH ____(3)____( keys )
    RESULT DATA(lt_travel).

  result = VALUE #( FOR ls IN lt_travel
                    ( %tky        = ls-%tky
                      ____(4)____ = ls ) ).
ENDMETHOD.
```

(4) Draft 가능 BO에서 할인율을 받아 `BookingFee`를 깎고 바뀐 인스턴스를 돌려주는 action이다. 빈칸 6~10을 채우시오.

```abap
" BDEF
action ( features : instance ) deductDiscount
  ____(6)____ /dmo/a_travel_discount ____(7)____ [1] ____(8)____;
```

```abap
METHOD deductDiscount.
  DATA upd TYPE TABLE FOR UPDATE zr_traveltp\\Travel.

  READ ENTITIES OF zr_traveltp IN LOCAL MODE
    ENTITY Travel FIELDS ( BookingFee ) WITH CORRESPONDING #( keys )
    RESULT DATA(travels).

  LOOP AT travels INTO DATA(travel).
    DATA(pct) = keys[ KEY draft %tky = travel-%tky ]-____(9)____-discount_percent.
    APPEND VALUE #( %tky       = travel-%tky
                    BookingFee = travel-BookingFee * ( 100 - pct ) / 100 ) TO upd.
  ENDLOOP.

  MODIFY ENTITIES OF zr_traveltp IN LOCAL MODE
    ENTITY Travel UPDATE FIELDS ( BookingFee ) WITH upd.

  READ ENTITIES OF zr_traveltp IN LOCAL MODE
    ENTITY Travel ____(10)____ WITH CORRESPONDING #( travels )
    RESULT DATA(changed).

  result = VALUE #( FOR t IN changed ( %tky = t-%tky  ____(9)____ = t ) ).
ENDMETHOD.
```

(5) (4)의 표 식에서 `KEY draft`를 명시하는 이유를 쓰고, 할인율이 0 이하이거나 100을 넘는 입력은 어떻게 처리해야 하는지 쓰시오.

(6) Draft 없는 managed BO, 키는 `numbering : managed` UUID다. BDEF에 `factory action copyTravel [1];`이 있고 validation은 없다. DB에는 Travel이 5건 있으며, 그중 `k1`은 `OverallStatus = 'A'`, `BookingFee = 20`이다. 아래 구현과 소비자 코드를 실행했을 때 (가) `lines( mapped-travel )` (나) `mapped-travel`의 `%cid` 값들 (다) `k1`에서 복사된 새 인스턴스의 `TravelUUID`가 `k1`과 같은지와 그 `OverallStatus`, `BookingFee` (라) 커밋 후 DB의 Travel 건수를 쓰시오.

```abap
METHOD copyTravel.
  DATA new_travels TYPE TABLE FOR CREATE zr_traveltp\\Travel.

  READ ENTITIES OF zr_traveltp IN LOCAL MODE
    ENTITY Travel ALL FIELDS WITH CORRESPONDING #( keys )
    RESULT DATA(travels).

  LOOP AT travels INTO DATA(travel).
    APPEND VALUE #( %cid          = keys[ KEY entity %key = travel-%key ]-%cid
                    CustomerID    = travel-CustomerID
                    BookingFee    = travel-BookingFee
                    OverallStatus = 'O' ) TO new_travels.
  ENDLOOP.

  MODIFY ENTITIES OF zr_traveltp IN LOCAL MODE
    ENTITY Travel
      CREATE FIELDS ( CustomerID BookingFee OverallStatus ) WITH new_travels
    MAPPED DATA(mapped_create).

  mapped-travel = mapped_create-travel.
ENDMETHOD.
```

```abap
MODIFY ENTITIES OF zr_traveltp
  ENTITY Travel
    EXECUTE copyTravel FROM VALUE #( ( %cid = 'C1' %key-TravelUUID = k1 )
                                     ( %cid = 'C2' %key-TravelUUID = k2 ) )
  MAPPED DATA(mapped) FAILED DATA(failed).
COMMIT ENTITIES.
```

<details><summary>정답·해설</summary>

**(1)**
- instance action: 특정 인스턴스에 대해 실행. `action acceptTravel result [1] $self;`
- static action: 인스턴스와 무관하게 엔티티 전체에 대해 실행. `static action massUpdate;`
- factory action: 새 인스턴스를 만든다. 결과는 `result`가 아니라 `mapped`로 돌려준다. `factory action copyTravel [1];` (instance-bound 또는 `static factory`)
- internal action: BO 구현 안에서만 호출할 수 있다(외부·UI에 노출 안 됨). `internal action reCalcTotalPrice;`
- 파라미터·결과: `action deductDiscount parameter /dmo/a_travel_discount result [1] $self;` 파라미터는 CDS 추상 엔티티(abstract entity)이고, 구현에서 `keys-%param-필드`로 읽는다. 결과 cardinality는 `[0..1]`, `[1]`, `[0..*]`, `[1..*]`, 타입은 `$self` 또는 `entity 다른엔티티`.
- 옵션: `( features : instance )`(동적 기능 제어), `( authorization : none )`, `( lock : none )`, `( precheck )` 등.
- UI 버튼: 프로젝션 BDEF에서 `use action`으로 노출하고, 메타데이터 확장에서 `@UI.lineItem`/`@UI.identification`에 `type: #FOR_ACTION`으로 연결해야 버튼이 보인다.

**(2)** function은 데이터를 바꾸지 않고(잠금도 없음) 값을 계산·조회해 돌려준다. 결과(`result`)가 필수다. Draft action은 구현이 필요 없다.
- Edit: 활성 인스턴스를 Draft 테이블로 복사하고 잠근다.
- Activate: Draft를 활성 테이블로 옮기고 Draft를 지운다(내부적으로 Prepare 실행).
- Discard: Draft를 지운다.
- Resume: 잠금이 만료된 Draft를 다시 편집할 때 잠금을 다시 얻는다.
- Prepare(`draft determine action`): 등록된 on save determination·validation을 실행한다.

**(3)** 1. `IN LOCAL MODE` 2. `%tky` 3. `CORRESPONDING #` 4. `%param` 5. `FOR ACTION`

`IN LOCAL MODE`는 BO 자신의 구현 안에서 기능 제어·권한 검사를 건너뛴다. 그래서 OverallStatus가 읽기 전용이어도 action 안에서는 바꿀 수 있다. `%tky`를 쓰면 Draft BO에서도 `%is_draft`까지 함께 넘어간다. `result [1] $self`이므로 결과는 인스턴스 키(`%tky`)와 바뀐 엔티티 전체(`%param`)다. Fiori Elements는 이 결과로 화면을 새로 고친다.

**(4)** 6. `parameter` 7. `result` 8. `$self` 9. `%param` 10. `ALL FIELDS`

입력 파라미터와 action 결과는 모두 `%param` 구성요소로 다룬다(입력은 `keys[...]-%param-필드`, 결과는 `result`의 `%param`에 인스턴스 전체). 결과가 `$self`면 결과 타입이 자기 엔티티 타입이다.

**(5)** BDEF 파생 타입 테이블은 기본 키가 비어 있는 표준 테이블이고, 정렬 보조 키(`entity`, `cid`, Draft BO의 `draft` 등)가 미리 정의되어 있다. 그래서 표 식에서 `KEY draft %tky = ...`처럼 보조 키를 명시해 찾는다. 할인율이 0 이하이거나 100을 넘는 키는 계산 전에 걸러 `failed`에 넣고, `reported`에는 `%op-%action-deductDiscount = if_abap_behv=>mk-on`과 함께 메시지를 넣는다.

**(6)** (가) 2 (나) `'C1'`, `'C2'` (다) 다르다(프레임워크가 새 UUID를 부여). `OverallStatus = 'O'`, `BookingFee = 20` (라) 7건

읽은 원본 2건마다 호출자가 준 `%cid`를 그대로 붙여 생성 요청을 만든다. 생성할 때 키를 지정하지 않았으므로 managed numbering이 새 UUID를 채우고, `mapped`에 "`%cid` ↔ 새 키"가 담긴다. 이것을 action의 `mapped`로 넘기므로 소비자는 `C1`, `C2`로 새 인스턴스를 찾는다. 원본 Travel은 바뀌지 않고 2건이 추가되어 5 + 2 = 7건이다. 상태는 복사하지 않고 'O'로 지정했다.

</details>

---

## 기능 제어·권한

### C-028. 기능 제어: 정적·인스턴스·전역, precheck [코드] ★★
<!-- src: RP-024, RP-025, RB-080 -->
Travel BO는 상태(`OverallStatus`: O=Open, A=Accepted, X=Rejected)에 따라 편집·삭제·action 버튼을 켜고 끈다.

(1) 다음 구현에서 세 인스턴스의 각 동작이 활성(enabled)인지 비활성(disabled)인지 표로 쓰시오. (T1: `OverallStatus = 'O'`, T2: `'A'`, T3: `'X'`)

```abap
METHOD get_instance_features.
  READ ENTITIES OF zr_traveltp IN LOCAL MODE
    ENTITY Travel FIELDS ( OverallStatus ) WITH CORRESPONDING #( keys )
    RESULT DATA(travels) FAILED failed.

  result = VALUE #( FOR t IN travels
    ( %tky = t-%tky
      %features-%update = COND #( WHEN t-OverallStatus = 'A'
                                  THEN if_abap_behv=>fc-o-disabled ELSE if_abap_behv=>fc-o-enabled )
      %features-%delete = COND #( WHEN t-OverallStatus = 'O'
                                  THEN if_abap_behv=>fc-o-enabled ELSE if_abap_behv=>fc-o-disabled )
      %action-acceptTravel = COND #( WHEN t-OverallStatus = 'A'
                                     THEN if_abap_behv=>fc-o-disabled ELSE if_abap_behv=>fc-o-enabled )
      %action-rejectTravel = COND #( WHEN t-OverallStatus = 'X'
                                     THEN if_abap_behv=>fc-o-disabled ELSE if_abap_behv=>fc-o-enabled )
      %field-BookingFee = COND #( WHEN t-OverallStatus = 'O'
                                  THEN if_abap_behv=>fc-f-unrestricted ELSE if_abap_behv=>fc-f-read_only ) ) ).
ENDMETHOD.
```

(2) (1)이 동작하려면 BDEF에 어떤 선언이 있어야 하는지 쓰시오. 결과 구조에서 동작·action·필드를 각각 어느 구성요소로 채우는지, 어떤 상수 그룹을 쓰는지도 쓰시오.

(3) 정적(static), 인스턴스(동적), 전역(global) 기능 제어의 차이를 BDEF 문법과 구현 메서드로 설명하시오. create에 인스턴스 기능 제어를 쓸 수 없는 이유도 쓰시오.

(4) 기능 제어와 권한 제어는 무엇이 다른지 쓰시오. Fiori Elements는 기능 제어 결과를 화면에 어떻게 반영하는지 쓰시오.

(5) precheck, validation, 기능 제어에 대한 설명으로 옳은 것을 고르고, 나머지가 틀린 이유를 쓰시오.

① validation은 `on modify`로 정의해 입력 즉시 실행되게 할 수 있다.
② precheck는 요청이 트랜잭셔널 버퍼에 들어가기 전에 호출되어 잘못된 요청을 미리 거부한다.
③ 동적 기능 제어(`features : instance`)는 저장 순서의 `check_before_save`에서 실행된다.
④ `IN LOCAL MODE`로 실행한 EML에도 precheck와 권한 검사가 그대로 적용된다.

<details><summary>정답·해설</summary>

**(1)**

| | update | delete | acceptTravel | rejectTravel | BookingFee 필드 |
|---|---|---|---|---|---|
| T1 (O) | enabled | enabled | enabled | enabled | 편집 가능 |
| T2 (A) | disabled | disabled | disabled | enabled | 읽기 전용 |
| T3 (X) | enabled | disabled | enabled | disabled | 읽기 전용 |

**(2)** BDEF에서 각 대상이 `( features : instance )`로 선언되어 있어야 한다. 예: `update ( features : instance ); delete ( features : instance ); action ( features : instance ) acceptTravel result [1] $self; field ( features : instance ) BookingFee;`. 결과는 인스턴스 키(`%tky`)마다 표준 동작은 `%features-%update`/`%features-%delete`(또는 `%update`, `%delete`), action은 `%action-이름`, 필드는 `%field-필드`로 채운다. 동작에는 `if_abap_behv=>fc-o-*`(operation: `enabled`, `disabled`), 필드에는 `if_abap_behv=>fc-f-*`(field: `read_only`, `mandatory`, `unrestricted`, `all`) 상수를 쓴다.

**(3)**
- 정적: BDEF에 고정 규칙으로 선언하고 구현은 필요 없다. `field ( readonly ) ...`, `field ( mandatory ) ...`, `field ( readonly : update ) ...`, `create;`를 쓰지 않으면 생성 불가 등.
- 인스턴스(동적): 인스턴스 데이터(상태 등)에 따라 달라진다. `update ( features : instance );`, `action ( features : instance ) acceptTravel ...;`, `field ( features : instance ) BookingFee;` → `FOR INSTANCE FEATURES` 메서드(`get_instance_features`)에서 인스턴스별로 결과를 채운다.
- 전역: 인스턴스와 무관한 조건(설정값, 시스템 상태 등)으로 동작 자체를 켜고 끈다. `create ( features : global );` → `FOR GLOBAL FEATURES` 메서드.
- create는 아직 인스턴스가 없으므로 인스턴스 기능 제어를 쓸 수 없고, 전역 기능 제어만 가능하다.

**(4)** 기능 제어는 "데이터 상태상 이 동작이 가능한가"(업무 규칙), 권한 제어는 "이 사용자가 이 동작을 해도 되는가"(사용자 권한)를 판단한다. UI에서는 둘 다 버튼 비활성·필드 읽기 전용으로 보일 수 있다. Fiori Elements는 이 결과를 받아 버튼을 회색으로 만들거나 필드를 잠근다. `IN LOCAL MODE` EML은 기능 제어와 권한 검사를 건너뛴다.

**(5)** ②
- ① 틀리다. validation은 `on save`만 가능하다. 입력 즉시 계산은 `on modify` determination이다.
- ② 맞다. `create ( precheck )`, `update ( precheck )`, `action ( precheck ) ...`으로 선언하고 `FOR PRECHECK` 메서드를 구현한다. 버퍼에 들어가기 전에 막으므로 버퍼가 오염되지 않는다.
- ③ 틀리다. 기능 제어는 요청을 처리하기 전(그리고 UI가 버튼 상태를 물을 때) `FOR INSTANCE FEATURES` 메서드로 판단한다.
- ④ 틀리다. `IN LOCAL MODE`는 BO 내부 구현용으로 기능 제어, 권한 검사, precheck를 건너뛴다. 예: 읽기 전용 상태 필드를 action 안에서 바꿀 때.

</details>

---

### C-029. 권한: 전역·인스턴스 권한, DCL, ABAP Cloud 권한 할당 [코드] ★★
<!-- src: RP-026, RP-027, RB-079 -->
대리점(Agency)별로 Travel을 관리하는 회사다. 권한 객체 `ZTRAVEL`(필드 `ACTVT`, 대리점)로 사용자를 통제한다.

(1) RAP의 전역(global) 권한과 인스턴스(instance) 권한의 차이를 BDEF 문법과 구현 메서드로 설명하시오. 동작 단위로 권한을 세분화하는 문법도 쓰시오.

(2) `ZTRAVEL`의 활동 `01`(생성) 권한이 있을 때만 Travel 생성을 허용하는 전역 권한 구현이다. 빈칸을 채우시오.

```abap
METHODS get_global_authorizations FOR ____(1)____ AUTHORIZATION
  IMPORTING ____(2)____ requested_authorizations FOR Travel RESULT result.

METHOD get_global_authorizations.
  IF requested_authorizations-____(3)____ = if_abap_behv=>mk-on.
    AUTHORITY-CHECK OBJECT 'ZTRAVEL' ID 'ACTVT' FIELD '01'.
    result-____(3)____ = COND #( WHEN sy-subrc = 0
                                 THEN if_abap_behv=>____(4)____
                                 ELSE if_abap_behv=>____(5)____ ).
  ENDIF.
ENDMETHOD.
```

(3) (2)에서 `result`의 형태(구조인지 테이블인지)와, 권한이 없을 때 프레임워크가 요청을 어떻게 처리하는지 쓰시오.

(4) 읽기, 생성·static action, 변경·삭제·instance action, 자식 엔티티의 권한을 각각 어디서 어떻게 구현하는지 쓰시오. Draft BO에서 Edit action은 어떤 권한으로 검사하는지, action에 `authorization : update`를 쓰면 어떻게 되는지도 쓰시오.

(5) ABAP Cloud에서 권한 객체를 사용자에게 주는 절차를 쓰고, 온프레미스와 무엇이 다른지 쓰시오.

<details><summary>정답·해설</summary>

**(1)**
- 전역 권한 `authorization master ( global )`: 인스턴스와 무관하게 사용자가 그 동작을 할 수 있는지 판단한다(예: Travel 생성 권한). `FOR GLOBAL AUTHORIZATION` 메서드(`get_global_authorizations`)는 `keys` 없이 `requested_authorizations`만 받는다. create는 전역 권한으로만 검사할 수 있다.
- 인스턴스 권한 `authorization master ( instance )`: 인스턴스 값으로 판단한다(예: 특정 대리점·국가의 Travel만 수정 가능). `FOR INSTANCE AUTHORIZATION` 메서드(`get_instance_authorizations`)에서 키별로 `%update`, `%delete`, `%action-...`에 `if_abap_behv=>auth-allowed`/`auth-unauthorized`를 넣는다.
- `( global, instance )`로 둘 다 지정할 수 있다. 동작 단위로는 `( authorization : none )`, `delete ( authorization : update )`처럼 세분화한다.

**(2)** 1. `GLOBAL` 2. `REQUEST` 3. `%create` 4. `auth-allowed` 5. `auth-unauthorized`

**(3)** 전역 권한은 인스턴스 키가 없으므로 `IMPORTING REQUEST ... RESULT result` 형태이고, `result`는 테이블이 아니라 **구조**다. 요청된 동작(`%create`, `%update`, `%delete`, `%action-...`)만 확인해 채운다. 권한이 없으면 프레임워크가 해당 요청을 `failed`(원인 unauthorized)로 처리한다. 메시지를 직접 남기려면 `reported`도 채운다.

**(4)**
- 읽기: BDEF가 아니라 CDS 접근 제어(DCL)로 제어한다. `define role ... grant select on ZR_TravelTP where ( AgencyID ) = aspect pfcg_auth( ZTRAVEL, ..., ACTVT = '03' );`, 뷰에 `@AccessControl.authorizationCheck: #CHECK`. 인터페이스 뷰와 프로젝션 뷰 각각에 롤을 두고, 프로젝션은 `inheriting conditions from entity`로 물려받는다.
- 생성·static action: 인스턴스가 아직 없으므로 전역 권한(`( global )` 또는 `( global, instance )`) → `FOR GLOBAL AUTHORIZATION` 메서드에서 `AUTHORITY-CHECK OBJECT ... ID 'ACTVT' FIELD '01'` 결과로 `result-%create`를 설정한다.
- 변경·삭제·instance action: 인스턴스 권한 → `FOR INSTANCE AUTHORIZATION` 메서드에서 인스턴스 데이터(예: 대리점)를 읽어 `%update`, `%delete`, `%action-xxx`를 설정한다. `requested_authorizations`를 보고 필요한 것만 검사한다.
- Draft BO의 Edit action(`%action-Edit`)은 변경 권한으로 검사한다. action에 `authorization : update`를 쓰면 그 action은 update 권한 결과를 따른다.
- 자식 엔티티: `authorization dependent by _Travel`로 루트에 위임한다(자식 수정이 루트의 update 권한 검사로 넘어감).
- 정리: BDEF 권한은 수정 계열(create, update, delete, action)을 보호하고, DCL은 읽기 행을 거른다. `IN LOCAL MODE` EML은 BO 자신의 권한 검사를 건너뛴다.

**(5)** 권한 객체(+ 권한 필드) 생성 → IAM 앱에 권한 값 정의 → 비즈니스 카탈로그에 IAM 앱 추가 → 관리자가 비즈니스 역할에 카탈로그를 넣고 사용자에게 할당. 온프레미스는 PFCG 역할로 할당한다. 권한 결과가 거부면 UI에서 버튼이 비활성화되거나 오류 메시지가 나온다.

</details>

---

## Draft

### C-030. Draft 수명 주기와 OData 요청, 상태 추적 [개념] ★★★
<!-- src: RP-028, XE-016, XE-017, MX-061 -->
Draft가 켜진 Travel 서비스(OData V4)를 Fiori Elements에서 쓴다.

(1) (가) 기존 데이터를 편집해 저장하는 흐름과 (나) 새 데이터를 만드는 흐름을 Draft action(Edit, Prepare, Activate, Discard, Resume) 중심으로 설명하시오. 각 단계에서 데이터가 어느 테이블에 있는지, `on modify` determination과 `on save` validation이 언제 실행되는지, 잠금이 어떻게 걸리는지도 쓰시오.

(2) 사용자의 Create, Edit, 필드 변경, Save, Discard 동작이 각각 어떤 OData 요청이 되고 백엔드에서 무슨 일이 일어나는지 표로 쓰시오.

(3) `IsActiveEntity`, `HasDraftEntity`, `HasActiveEntity`, `DraftAdministrativeData`의 의미를 쓰고, Draft가 stateless 웹 환경에서 주는 이점을 쓰시오.

(4) 활성 인스턴스 T1(Description `Old`)만 있고 Draft는 없다. 사용자 A가 다음을 순서대로 했다. 각 단계가 끝난 뒤 활성 테이블 행 수, Draft 테이블 행 수, T1 활성 인스턴스의 Description과 HasDraftEntity를 표로 채우시오.
1. T1에서 Edit
2. Description을 `New`로 바꾸고 필드를 벗어남(자동 저장 완료)
3. Discard
4. 다시 Edit → Description을 `New2`로 변경 → Save(성공)
5. Create 버튼으로 새 여행 T2를 만들고 값을 일부 입력한 뒤 저장하지 않고 브라우저를 닫음

(5) (4)의 2단계 직후 다른 사용자 B가 T1을 열어 Edit를 누르면 어떻게 되는지 쓰시오.

(6) Draft가 켜진 BO에 대한 설명으로 **옳지 않은 것**을 고르고 이유를 쓰시오.

① Draft 테이블을 따로 만들고 BDEF의 `draft table`에 지정해야 한다.
② 루트 엔티티에는 total etag 필드가 있어야 한다.
③ BDEF에 보통 `draft action Edit; draft action Activate optimized; draft action Discard; draft action Resume; draft determine action Prepare;`를 둔다.
④ Draft 인스턴스는 활성 테이블에 함께 저장되며 IsActiveEntity 필드 값으로 구분된다.
⑤ EML로 Draft 인스턴스를 다룰 때는 `%is_draft = if_abap_behv=>mk-on`을 `%tky`에 넣는다.

<details><summary>정답·해설</summary>

**(1)**
- (가) 기존 데이터 편집: Edit → 활성 인스턴스가 Draft 테이블로 복사되고(`%is_draft = mk-on`인 Draft 인스턴스 생성) 활성 인스턴스에 배타적 잠금이 걸린다. 필드를 바꿀 때마다 Draft 테이블이 갱신된다(요청마다 Draft 저장, 이때 validation은 실행 안 됨). `on modify` determination은 변경 즉시 실행된다. 저장 버튼 → Activate → 내부적으로 Prepare 실행(등록된 `on save` determination·validation) → 오류가 없으면 Draft 내용이 활성 테이블에 저장되고 Draft 삭제, 잠금 해제. 오류가 있으면 Draft가 그대로 남고 메시지가 표시된다.
- (나) 새 데이터: 처음부터 Draft 테이블에만 존재한다(활성 데이터 없음). 이후 흐름은 같고, Activate 때 처음 활성 테이블에 들어간다.
- Discard: Draft 행을 지우고 잠금을 푼다. 활성 데이터는 그대로다.
- Resume: 배타 잠금 시간이 지나 잠금이 풀린 Draft를 다시 수정할 때 자동 실행되어 잠금을 다시 건다. 그 사이 활성 데이터가 바뀌었는지는 total ETag로 비교해, 바뀌었으면 이어서 편집할 수 없다.
- validation이 Draft 단계에서 실행되려면 `draft determine action Prepare { validation ...; }`에 등록해야 한다. 코드에서는 Draft와 활성 인스턴스가 같은 키를 가지므로 `%is_draft`를 포함한 `%tky`로 구분한다. Draft 테이블은 ABAP SQL로 직접 읽거나 쓰지 않는다(번호 최대값 조회 같은 예외 제외).

**(2)**

| UI 동작 | OData 요청(대표) | 백엔드 |
|---|---|---|
| Create | `POST Travel` (Draft 인스턴스 생성) | Draft 테이블에 새 행(IsActiveEntity=false). 활성 테이블에는 아직 없음 |
| Edit | `POST Travel(...,IsActiveEntity=true)/<namespace>.Edit` | 활성 인스턴스를 Draft 테이블로 복사, 활성 인스턴스에 배타 잠금 |
| 필드 변경 | `PATCH Travel(...,IsActiveEntity=false)` (필드를 벗어날 때 자동 저장) | Draft 테이블만 갱신. `on modify` determination 등이 실행될 수 있음 |
| Save | `POST Travel(...,IsActiveEntity=false)/<namespace>.Activate` (앞서 Prepare 호출) | Prepare에서 validation 실행 → 통과하면 Draft 내용을 활성 테이블에 저장(save sequence), Draft 삭제, 잠금 해제 |
| Discard(Cancel) | `DELETE Travel(...,IsActiveEntity=false)` | Draft 삭제, 활성 인스턴스는 그대로, 잠금 해제 |

**(3)**
- `IsActiveEntity`: 이 인스턴스가 활성(true)인지 Draft(false)인지. **키의 일부**라서 URL에 항상 들어간다.
- `HasDraftEntity`: 활성 인스턴스에 대응하는 Draft가 있는지(누군가 편집 중).
- `HasActiveEntity`: Draft 인스턴스에 대응하는 활성 인스턴스가 있는지(Edit로 만든 Draft면 true, 새로 Create한 Draft면 false).
- `DraftAdministrativeData`: 누가 언제 만든 Draft인지. List Report의 "Editing Status" 필터와 잠금 표시("Locked by ...")에 쓰인다.
- 이점: 편집 중인 데이터를 서버에 보관하므로 브라우저를 닫아도 이어서 편집(Resume)할 수 있고, 저장 전 검증과 다른 사용자와의 충돌 방지(배타 잠금)를 제공한다.

**(4)**

| 단계 | 활성 행 수 | Draft 행 수 | T1 활성 Description | T1 HasDraftEntity |
|---|---|---|---|---|
| 1 | 1 | 1 | Old | true |
| 2 | 1 | 1 | Old | true |
| 3 | 1 | 0 | Old | false |
| 4 | 1 | 0 | New2 | false |
| 5 | 1 | 1 | New2 | false |

- 2단계의 변경은 Draft에만 저장되므로 활성 값은 여전히 Old다. 다른 사용자는 Save 전까지 New를 볼 수 없다.
- 3단계 Discard는 Draft만 지운다.
- 4단계 Save(Activate)로 Draft 내용이 활성 테이블에 반영되고 Draft는 삭제된다.
- 5단계의 T2는 Draft 테이블에만 있다(IsActiveEntity=false, HasActiveEntity=false). 브라우저를 닫아도 Draft는 서버에 남아 A가 나중에 이어서 편집(Resume)하거나, 기간이 지나면 정리된다. T1의 HasDraftEntity와는 무관하다.

**(5)** B는 Edit할 수 없다. T1은 A의 Draft 때문에 배타 잠금 상태라 "다른 사용자(A)가 편집 중/잠김" 오류가 난다. B는 활성 데이터(`Old`)만 조회할 수 있다. 배타 잠금은 일정 시간 유지되고, 그 뒤에는 잠금이 풀려 다른 사용자가 A의 Draft를 버리고 편집할 수 있게 된다(Draft 수명 설정에 따름). 시스템 설정에 따라 달라지므로 시험에서는 "편집 중에는 다른 사용자가 Edit할 수 없다"까지 답하면 된다.

**(6)** ④. Draft 데이터는 **별도의 Draft 테이블**에 저장된다. Activate 때 활성 테이블로 옮겨지고 Draft는 지워진다. `IsActiveEntity`는 OData에 노출되는 가상 키로, 프레임워크가 어느 테이블에서 읽을지 구분하는 데 쓴다. Draft 테이블은 ADT 퀵픽스로 BDEF에서 생성할 수 있다.

</details>

---

### C-031. Draft 구현: Draft 테이블, %tky, BDEF 오류, 운영 문제 [코드] ★★★
<!-- src: RP-029, RP-030, RB-074, RB-075 -->
Travel BO(`ZR_TravelTP`, 활성 테이블 `ztravel_a`)에 Draft를 켠다.

(1) Draft 테이블 `ztravel_d`를 만든다. 빈칸 1을 채우고, Draft 테이블의 필드 이름 규칙과 만드는 방법을 쓰시오. 아래 필드를 갖는 테이블로 답하고, 필드 표도 함께 쓰시오.

```abap
define table ztravel_d {
  key mandt          : mandt not null;
  key traveluuid     : sysuuid_x16 not null;
  travelid           : /dmo/travel_id;
  locallastchangedat : abp_locinst_lastchange_tstmpl;
  lastchangedat      : abp_lastchange_tstmpl;
  "%admin"           : include ____(1)____;
}
```

(2) Draft 인스턴스만 읽는 EML과 프로젝션 BDEF다. 빈칸 2~5를 채우시오.

```abap
READ ENTITIES OF zr_traveltp
  ENTITY Travel ALL FIELDS
  WITH VALUE #( ( TravelUUID = k  ____(2)____ = if_abap_behv=>____(3)____ ) )
  RESULT DATA(draft_travels).
```

```abap
projection;
strict ( 2 );
use ____(4)____;

define behavior for ZC_TravelTP alias Travel
use ____(5)____
{
  use create;
  use update;
  use delete;
  use action Edit;
  use action Activate;
  use action Discard;
  use action Resume;
  use action Prepare;
  use association _Booking { create; with draft; }
}
```

(3) 다음 Draft BDEF에서 활성화 오류 2가지와 논리 오류 1가지를 찾아 고치시오.

```abap
managed implementation in class zbp_r_travel unique;
strict ( 2 );
with draft;
define behavior for ZR_Travel alias Travel
persistent table ztravel_a
lock master
authorization master ( instance )
etag master LocalLastChangedAt
{
  create; update; delete;
  field ( numbering : managed, readonly ) TravelUUID;

  validation validateDates    on save { create; field BeginDate, EndDate; }
  validation validateCustomer on save { create; field CustomerID; }
  determination setStatus on modify { create; }

  draft action Edit;
  draft action Activate optimized;
  draft action Discard;
  draft action Resume;
  draft determine action Prepare { validation validateDates; }
}
```

(4) Draft BO의 determination이다. 사용자가 새 Travel을 만들었는데(Draft 상태) 상태가 'O'로 채워지지 않는다. 잘못된 곳 두 가지를 찾아 고치시오.

```abap
METHOD setStatusToOpen.
  READ ENTITIES OF zr_traveltp IN LOCAL MODE
    ENTITY Travel FIELDS ( OverallStatus ) WITH CORRESPONDING #( keys )
    RESULT DATA(travels).

  LOOP AT travels INTO DATA(travel) WHERE OverallStatus IS INITIAL.
    IF travel-%is_draft = abap_true.
      MODIFY ENTITIES OF zr_traveltp IN LOCAL MODE
        ENTITY Travel UPDATE FIELDS ( OverallStatus )
        WITH VALUE #( ( %key          = travel-%key
                        OverallStatus = 'O' ) ).
    ENDIF.
  ENDLOOP.
ENDMETHOD.
```

(5) Draft BO를 운영하며 자주 겪는 문제 4가지와 원인·해결 방법을 쓰시오.

<details><summary>정답·해설</summary>

**(1)** 1. `sych_bdl_draft_admin_inc`

| 필드 | 키 | 타입(데이터 요소) | 비고 |
|---|---|---|---|
| mandt | ✔ | mandt | 클라이언트 |
| traveluuid | ✔ | sysuuid_x16 | 활성 엔티티 키와 같음 |
| travelid | | /dmo/travel_id | |
| locallastchangedat | | abp_locinst_lastchange_tstmpl | etag master용 |
| lastchangedat | | abp_lastchange_tstmpl | total etag용 |
| "%admin" | | include sych_bdl_draft_admin_inc | Draft 관리 정보(필수) |

Draft 테이블은 활성 엔티티의 필드를 **CDS 요소 별칭 이름**으로 갖고, Draft 관리 정보(`%admin` include)를 반드시 포함한다. ADT에서 BDEF의 `draft table` 줄에 퀵픽스를 써서 자동 생성할 수 있다.

**(2)** 2. `%is_draft` 3. `mk-on` 4. `draft` 5. `etag`

`%is_draft`가 `if_abap_behv=>mk-on`이면 Draft, `mk-off`(초기값)이면 활성 인스턴스다. 프로젝션에서도 `use draft`, `use etag`, Draft action을 `use action`으로 노출해야 Fiori Elements가 Draft 흐름(Edit·Save·Discard 버튼)을 사용한다.

**(3)**
1. (활성화 오류) `with draft;`인데 `draft table ztravel_d`가 없다 → `persistent table ztravel_a` 다음 줄에 `draft table ztravel_d`를 추가한다.
2. (활성화 오류) Draft BO의 lock master에는 `total etag`가 필요하다 → `lock master total etag LastChangedAt`.
3. (논리 오류) `validateCustomer`가 Prepare에 등록되지 않았다 → `draft determine action Prepare { validation validateDates; validation validateCustomer; }`. 등록하지 않으면 Draft 편집 중 Prepare 때 고객 오류가 상태 메시지로 표시되지 않는다.

**(4)**
1. `%key`에는 Draft 표시(`%is_draft`)가 없다. `%is_draft`가 초기값(활성)으로 간주되어 Draft 인스턴스가 아니라 (존재하지 않는) 활성 인스턴스를 수정하려 하게 된다. → `%tky = travel-%tky`로 바꾼다.
2. `%is_draft`는 `abap_bool`이 아니라 `abp_behv_flag` 타입이다. `abap_true`와 비교하면 의도대로 판단되지 않는다. → `if_abap_behv=>mk-on`과 비교하거나, 이 경우는 Draft/활성 구분이 필요 없으므로 IF 자체를 없앤다.

고친 코드에서는 루프 대신 `MODIFY ... WITH VALUE #( FOR t IN travels WHERE ( OverallStatus IS INITIAL ) ( %tky = t-%tky OverallStatus = 'O' ) )`처럼 한 번에 처리하고 `REPORTED`를 `reported`로 넘기는 것이 좋다. Draft 여부와 상관없이 항상 `%tky`를 쓰면 나중에 Draft를 켜도 코드를 고칠 필요가 없다.

**(5)** 아래 중 4가지

| 문제 | 원인·해결 |
|---|---|
| 테이블·CDS에 필드를 추가했더니 Draft 테이블 오류 | Draft 테이블은 CDS 요소(별칭 이름)와 맞아야 한다. BDEF 퀵픽스로 Draft 테이블을 다시 생성·조정 |
| validation 메시지가 Save를 누를 때만 나오고 입력 중에는 안 나옴 | validation이 `draft determine action Prepare { ... }`에 등록되지 않았다. 등록하고, 즉시 확인이 필요하면 side effect로 determine action 실행 |
| 다른 사용자가 "잠겨 있다"며 편집 못 함 | Draft가 있는 동안 활성 인스턴스는 배타 잠금. 설정된 시간이 지나면 낙관적 잠금 단계로 바뀌고, 오래된 Draft는 정리된다. 사용자에게 Discard하도록 안내 |
| Resume 시 "데이터가 변경됨" 오류 | `total etag` 비교: 활성 데이터가 그 사이 바뀌면 Draft를 이어서 쓸 수 없다. `total etag`(`@Semantics.systemDateTime.lastChangedAt: true`)와 `etag master`(`localInstanceLastChangedAt`)는 다른 필드다 |
| 화면 계산 값이 바로 안 바뀜 | `on modify` determination이 돌아도 UI가 자동으로 다시 읽지 않는다. side effects 정의 필요 |
| EML에서 Draft를 못 찾음 | `%key` 대신 `%tky`(`%is_draft` 포함)를 써야 한다 |
| 활성화 시 키 충돌 | early 외부 번호 등 키 유일성을 Prepare 단계 validation이나 precheck에서 확인 |

핵심은 Draft에서 validation이 입력 시점이 아니라 Prepare(Activate가 내부적으로 호출) 때 실행된다는 점, Draft 데이터는 `on modify` determination으로만 바로 계산된다는 점이다.

</details>

---

## EML·트랜잭션 모델·이벤트

### C-032. EML 문법: READ, 파생 타입, 특수 구성요소, IN LOCAL MODE [코드] ★★
<!-- src: RP-031, RP-036, RP-037, MX-062, RP-039 -->
Travel BO(`ZR_TravelTP`, alias `Travel`, 자식 `_Booking`)를 EML로 다룬다.

(1) 행동 구현 클래스 안에서 Travel과 그 Booking을 읽는 코드다. 빈칸 1~5를 채우고, `FIELDS`와 `ALL FIELDS`의 차이와 `LINK`가 돌려주는 것을 쓰시오.

```abap
READ ENTITIES OF zr_traveltp ____(1)____
  ENTITY Travel
    ____(2)____ ( TravelID OverallStatus ) WITH CORRESPONDING #( keys )
    RESULT DATA(travels)
  ENTITY Travel ____(3)____
    ALL FIELDS WITH CORRESPONDING #( keys )
    RESULT DATA(bookings)
    ____(4)____ DATA(links)
  ____(5)____ DATA(read_failed).
```

(2) BDEF 파생 타입으로 변수를 선언한다. 빈칸 6~12를 채우고, `\\`, `~`, `\_`가 각각 무엇을 지정하는지 쓰시오.

```abap
" Travel 생성용 테이블
DATA create_tab   TYPE TABLE FOR ____(6)____ zr_traveltp\\Travel.
" Travel 한 건 수정용 구조
DATA update_line  TYPE ____(7)____ FOR UPDATE zr_traveltp\\Travel.
" READ ENTITIES의 입력 키 테이블과 결과 테이블
DATA read_keys    TYPE TABLE FOR READ ____(8)____ zr_traveltp\\Travel.
DATA read_result  TYPE TABLE FOR READ ____(9)____ zr_traveltp\\Travel.
" acceptTravel action의 입력 테이블
DATA action_keys  TYPE TABLE FOR ACTION IMPORT zr_traveltp\\Travel____(10)____acceptTravel.
" Travel을 통해 Booking을 생성(create-by-association)하는 입력 테이블
DATA cba_tab      TYPE TABLE FOR CREATE zr_traveltp\\Travel____(11)____.
" 응답 파라미터
DATA failed_resp  TYPE ____(12)____ FOR FAILED zr_traveltp.
```

(3) BDEF 파생 타입의 다음 구성요소를 각각 한 줄로 설명하시오.
`%cid`, `%cid_ref`, `%key`, `%tky`, `%pky`, `%pid`, `%is_draft`, `%control`, `%data`, `%target`, `%param`, `%element`, `%msg`, `%state_area`, `%fail`, `%op`

(4) 세 응답 파라미터 `mapped`, `failed`, `reported`에는 각각 무엇이 들어가는지 쓰시오.

(5) EML 특수 구성요소·응답 파라미터에 대한 설명 중 **옳은 것 2개**를 고르시오.

① `%cid`는 같은 EML 요청 안에서 아직 키가 없는 새 인스턴스를 가리키는 임시 ID다.
② Draft BO의 `%tky`에는 `%key`와 `%is_draft`가 들어 있다(late numbering이면 `%pid`도 포함).
③ `%control`은 READ 결과에서 값이 바뀐 필드를 표시한다.
④ `failed`에는 오류 메시지 텍스트가, `reported`에는 실패한 인스턴스의 키만 들어간다.
⑤ `mapped`는 READ ENTITIES의 결과 데이터를 담는다.

(6) 옳은 것을 **모두** 고르시오.

① `IN LOCAL MODE`는 BO 자신의 행동 구현(또는 auxiliary class) 안에서만 쓸 수 있고, 권한 검사와 기능 제어를 건너뛴다.
② `IN LOCAL MODE`를 쓰면 validation도 실행되지 않으므로 잘못된 데이터가 저장될 수 있다.
③ READ ENTITIES에는 `MAPPED` 응답이 없다.
④ 핸들러 메서드에서 내부 EML의 `reported`를 메서드의 `reported`로 넘길 때 `reported = CORRESPONDING #( DEEP upd_reported )`처럼 쓸 수 있다.
⑤ `failed`에 인스턴스가 있으면 EML 문이 예외 `CX_RAP_FAILED`를 발생시킨다.

<details><summary>정답·해설</summary>

**(1)** 1. `IN LOCAL MODE` 2. `FIELDS` 3. `BY \_Booking` 4. `LINK` 5. `FAILED`

`FIELDS ( ... )`는 지정한 필드만, `ALL FIELDS`는 전체 필드를 읽는다(필요한 필드만 읽는 것이 성능상 유리). `BY \_assoc`은 read-by-association이고, `LINK`는 원본 키와 대상 키의 쌍을 돌려준다. 응답으로 `FAILED`, `REPORTED`를 받을 수 있다(READ에는 `MAPPED`가 없다). `IN LOCAL MODE`는 BO 자신의 구현 안에서만 쓸 수 있다.

**(2)** 6. `CREATE` 7. `STRUCTURE` 8. `IMPORT` 9. `RESULT` 10. `~` 11. `\_Booking` 12. `RESPONSE`

형식은 `TYPE TABLE FOR <동작> bdef\\entity`(테이블), `TYPE STRUCTURE FOR ...`(구조)다. `\\`로 엔티티(alias), `~`로 action·determination 같은 동작, `\_`로 association을 지정한다. 응답은 `TYPE RESPONSE FOR MAPPED/FAILED/REPORTED bdef`(엔티티별 테이블을 구성요소로 갖는 구조)다. 핸들러 메서드의 `keys`, `entities`, `result`도 모두 이런 파생 타입이다.

**(3)**

| 구성요소 | 의미 |
|---|---|
| `%cid` | content ID. 생성 요청에서 키가 아직 없는 새 인스턴스를 가리키는 임시 ID(현재 요청 안에서만 유효) |
| `%cid_ref` | 같은 요청 안에서 `%cid`로 만든 인스턴스를 참조(create-by-association, update, action 등) |
| `%key` | 기본 키 필드 묶음 |
| `%tky` | transactional key. `%key` + `%pid` + `%is_draft`. 상호작용 단계에서 인스턴스를 식별하는 기본 수단 |
| `%pky` | `%key` + `%pid`(late numbering일 때). `%tky`가 없는 문맥에서 사용 |
| `%pid` | late numbering에서 최종 키가 정해지기 전 임시 ID |
| `%is_draft` | Draft 인스턴스(`mk-on`)인지 활성(`mk-off`)인지 |
| `%control` | 요청에서 어떤 필드가 실제로 제공·변경되는지 표시하는 플래그 구조 |
| `%data` | 키와 업무 필드를 묶은 데이터 부분 |
| `%target` | create-by-association에서 만들 자식 인스턴스 목록 |
| `%param` | action/function의 입력 파라미터 또는 결과 값 |
| `%element` | 메시지를 연결할 필드 표시(`%element-필드 = mk-on`) |
| `%msg` | 메시지 객체(`IF_ABAP_BEHV_MESSAGE` 구현) |
| `%state_area` | 상태 메시지 그룹 이름. 같은 이름으로 다시 보고하면 이전 메시지를 대체·삭제 |
| `%fail` | `failed`의 실패 원인(`%fail-cause`: `not_found`, `unauthorized`, `locked`, `disabled`, `unspecific` 등) |
| `%op` | 메시지·실패와 관련된 동작 표시(`%op-%update`, `%op-%action-이름`) |

Draft·late numbering 전환에 대비해 항상 `%tky`를 쓰는 것이 권장된다.

**(4)** `mapped`: 생성된 인스턴스의 `%cid` ↔ 실제 키 대응. `failed`: 실패한 인스턴스의 키와 `%fail`(원인). `reported`: 메시지(`%msg`, `%element`, `%state_area`, `%op`).

**(5)** ①, ②
- ③ `%control`은 입력 쪽에서 "어느 필드를 주거나 요청하는지" 표시하는 플래그다. `UPDATE FIELDS ( ... )`를 쓰면 자동으로 채워진다.
- ④ 반대다. `failed`는 실패한 인스턴스의 키와 `%fail-cause`, `reported`는 메시지(`%msg`)와 관련 필드(`%element`)를 담는다.
- ⑤ `mapped`는 CREATE 때 `%cid`와 실제 키의 대응을 돌려준다. READ 결과는 `RESULT`로 받는다.

**(6)** ①, ③, ④
- ① 옳다. 그래서 소비자에게 `readonly`인 `TotalPrice`를 determination이 수정할 수 있고, 인스턴스 상태로 비활성화된 동작도 내부 로직에서 호출할 수 있다.
- ② 틀리다. 권한·기능 제어만 생략할 뿐 저장 시퀀스의 validation은 그대로 실행된다.
- ③ 옳다. 응답은 `FAILED`, `REPORTED`다.
- ④ 옳다. 엔티티별 테이블을 가진 깊은 구조라 `DEEP`이 필요하다.
- ⑤ 틀리다. EML은 실패를 예외가 아니라 `failed`/`reported`로 돌려준다.

</details>

---

### C-033. EML 실행 결과 추적: %control, failed, deep create, 연관 읽기 [코드] ★★★
<!-- src: RP-032, RP-033, RP-034, RP-035, RP-038, MX-063 -->
Draft 없는 managed BO `ZR_TravelTP`(키 `TravelUUID`, `numbering : managed`)를 소비자 코드에서 다룬다. determination·validation은 없다고 가정한다.

(1) DB의 Travel `k`는 `Description = 'Old'`, `BookingFee = 50`, `OverallStatus = 'O'`다. 아래 코드 실행 후 `t-Description`, `t-BookingFee`, `t-OverallStatus`를 쓰고 이유를 쓰시오.

```abap
MODIFY ENTITIES OF zr_traveltp
  ENTITY Travel
    UPDATE FIELDS ( Description )
      WITH VALUE #( ( TravelUUID = k  Description = 'New'  BookingFee = 99 ) ).

MODIFY ENTITIES OF zr_traveltp
  ENTITY Travel
    UPDATE FIELDS ( BookingFee )
      WITH VALUE #( ( TravelUUID = k ) ).

MODIFY ENTITIES OF zr_traveltp
  ENTITY Travel
    UPDATE FROM VALUE #( ( TravelUUID    = k
                           Description   = 'X'
                           OverallStatus = 'A'
                           %control-OverallStatus = if_abap_behv=>mk-on ) ).

READ ENTITIES OF zr_traveltp
  ENTITY Travel ALL FIELDS WITH VALUE #( ( TravelUUID = k ) )
  RESULT DATA(travels).
DATA(t) = travels[ 1 ].
```

(2) DB에 Travel `k1`(`TravelID = '00000001'`, `Description = 'Trip'`, `OverallStatus = 'O'`)은 있고 `k9`는 없다. 실행 후 (가) `lines( travels )` (나) `travels[ 1 ]-Description` (다) `lines( failed-travel )` (라) `failed-travel[ 1 ]-%fail-cause`의 값(상수 이름)을 쓰시오.

```abap
READ ENTITIES OF zr_traveltp
  ENTITY Travel
    FIELDS ( OverallStatus )
    WITH VALUE #( ( TravelUUID = k1 ) ( TravelUUID = k9 ) )
  RESULT DATA(travels)
  FAILED DATA(failed).
```

(3) 같은 구조의 BO `ZMX_R_Travel`(키 `TravelID`)에 다음 데이터가 있다. Travel 00000001: Booking 0001, 0002, 0003 / Travel 00000002: Booking 없음 / Travel 00000009: 존재하지 않음. 실행 후 (가) `lines( lt_book )` (나) `lines( lt_link )` (다) `ls_failed-travel`에 들어가는 인스턴스와 실패 원인을 쓰시오.

```abap
READ ENTITIES OF zmx_r_travel
  ENTITY Travel BY \_Booking
    FIELDS ( BookingDate )
    WITH VALUE #( ( TravelID = '00000001' )
                  ( TravelID = '00000002' )
                  ( TravelID = '00000009' ) )
  RESULT DATA(lt_book)
  LINK   DATA(lt_link)
  FAILED DATA(ls_failed).
```

(4) 루트 Travel과 자식 Booking 2건을 한 요청에서 만들고 저장하는 소비자 코드다. 빈칸 1~6을 채우시오.

```abap
MODIFY ENTITIES OF zr_traveltp
  ENTITY Travel
    CREATE FIELDS ( CustomerID BeginDate EndDate )
      WITH VALUE #( ( ____(1)____ = 'T1'
                      CustomerID = '000001'
                      BeginDate  = '20261201'
                      EndDate    = '20261210' ) )
    CREATE ____(2)____ FIELDS ( FlightPrice CurrencyCode )
      WITH VALUE #( ( ____(3)____ = 'T1'
                      ____(4)____ = VALUE #( ( %cid = 'B1' FlightPrice = 100 CurrencyCode = 'EUR' )
                                             ( %cid = 'B2' FlightPrice = 200 CurrencyCode = 'EUR' ) ) ) )
  MAPPED DATA(mapped)
  FAILED DATA(failed)
  REPORTED DATA(reported).

____(5)____ RESPONSE OF zr_traveltp
  FAILED DATA(commit_failed)
  REPORTED DATA(commit_reported).

IF ____(6)____ <> 0.
  " 저장 실패 처리
ENDIF.
```

(5) (4)가 오류 없이 실행되었다(Booking도 UUID 키 `numbering : managed`). (가) `lines( mapped-travel )` (나) `lines( mapped-booking )` (다) `mapped-booking`의 `%cid` 값들 (라) `failed`가 비어 있는지 (마) 커밋 후 DB에서 B1, B2의 `TravelUUID`가 `mapped-travel[ 1 ]-TravelUUID`와 같은지를 쓰시오.

(6) Travel을 만들고 Booking 하나를 붙인 뒤, 다른 기존 Travel `k5`의 설명을 바꾸고 저장하려는 소비자 코드다. 의도대로 동작하지 않는 곳 세 군데를 찾아 고치시오.

```abap
MODIFY ENTITIES OF zr_traveltp
  ENTITY Travel
    CREATE FIELDS ( CustomerID BeginDate EndDate )
      WITH VALUE #( ( %cid = 'TR1' CustomerID = '000001'
                      BeginDate = '20261201' EndDate = '20261210' ) )
    CREATE BY \_Booking FIELDS ( FlightPrice CurrencyCode )
      WITH VALUE #( ( %cid_ref = 'T1'
                      %target  = VALUE #( ( %cid = 'B1' FlightPrice = 100 CurrencyCode = 'EUR' ) ) ) )
  ENTITY Travel
    UPDATE FROM VALUE #( ( TravelUUID = k5 Description = 'Changed' ) )
  MAPPED DATA(mapped) FAILED DATA(failed) REPORTED DATA(reported).

COMMIT ENTITIES.
out->write( 'Saved' ).
```

<details><summary>정답·해설</summary>

**(1)** `t-Description = 'New'`, `t-BookingFee = 0`, `t-OverallStatus = 'A'`
- 첫 MODIFY: `FIELDS ( Description )`이라 `%control-Description`만 켜진다. `BookingFee = 99`는 값이 있어도 무시된다 → Description 'New', BookingFee 50.
- 둘째 MODIFY: `%control-BookingFee`가 켜졌는데 값이 초기값이므로 BookingFee가 0으로 바뀐다. "값을 안 줬다"가 아니라 "0으로 바꾼다"로 해석된다.
- 셋째 MODIFY: `UPDATE FROM`은 `%control`을 직접 지정해야 하고 `OverallStatus`만 켰으므로 Description 'X'는 무시된다 → OverallStatus 'A'.
- READ는 같은 트랜잭션의 버퍼 상태를 읽으므로 커밋 전이라도 바뀐 값이 보인다.

**(2)** (가) 1 (나) 초기값(빈 문자열) (다) 1 (라) `if_abap_behv=>cause-not_found`

존재하는 `k1`만 결과에 들어간다. `FIELDS ( OverallStatus )`로 요청한 필드와 키만 채워지고, 요청하지 않은 `Description`은 초기값이다(DB 값 'Trip'이 아님). 없는 키 `k9`는 예외가 아니라 `failed`에 원인 `not_found`로 보고된다. 그래서 EML 다음에는 `sy-subrc` 대신 `failed`를 확인한다.

**(3)** (가) 3 (나) 3 (다) TravelID 00000009 한 건, `%fail-cause = if_abap_behv=>cause-not_found`

연관 읽기는 원본(Travel) 키마다 대상(Booking) 인스턴스를 돌려준다. Travel 1의 Booking 3건이 RESULT에 들어간다. 키 필드(TravelID, BookingID)는 FIELDS에 없어도 항상 채워진다. `LINK`는 원본 키와 대상 키의 쌍(`source-%tky`, `target-%tky`)이므로 3건이다. Travel 2는 존재하지만 자식이 없을 뿐이라 실패가 아니다(결과 0건). Travel 9는 원본 자체가 없어 Travel 엔티티의 `failed`에 들어간다.

**(4)** 1. `%cid` 2. `BY \_Booking` 3. `%cid_ref` 4. `%target` 5. `COMMIT ENTITIES` 6. `sy-subrc`

아직 키가 없는 새 루트를 같은 요청 안에서 참조하려면 생성 쪽에 `%cid`, 참조 쪽에 같은 값의 `%cid_ref`를 쓴다. create-by-association은 부모 참조(`%cid_ref` 또는 `%tky`)와 자식 목록 `%target`으로 이루어진다. MODIFY는 트랜잭션 버퍼만 바꾸므로 `COMMIT ENTITIES`가 있어야 DB에 저장된다. `COMMIT ENTITIES`는 early save phase에서 실패하면 `sy-subrc = 4`를 돌려주므로 반드시 확인한다. 이 코드는 소비자(BO 바깥) 코드이고, 행동 구현 안에서는 `COMMIT ENTITIES`를 쓸 수 없다.

**(5)** (가) 1 (나) 2 (다) `'B1'`, `'B2'` (라) 비어 있다(`failed IS INITIAL`) (마) 같다

`mapped`는 생성된 인스턴스마다 요청의 `%cid`와 프레임워크가 부여한 키를 엔티티별로 돌려준다. 루트 1건, 자식 2건이므로 1줄, 2줄이다. create-by-association으로 만든 자식은 부모 키(`TravelUUID`)가 부모의 새 UUID로 프레임워크에 의해 채워진다. 그래서 자식의 `TravelUUID`는 BDEF에서 `readonly`로 둔다.

**(6)**
1. `%cid_ref = 'T1'`이 생성 쪽 `%cid = 'TR1'`과 다르다. 참조할 인스턴스가 없어 Booking 생성이 실패한다. → `%cid_ref = 'TR1'`. `%cid`는 문자열 비교라 철자가 정확히 같아야 한다.
2. `UPDATE FROM`에 `%control`이 없어 어떤 필드도 변경 대상으로 표시되지 않는다(Description이 바뀌지 않음). → `%control-Description = if_abap_behv=>mk-on`을 넣거나 `UPDATE FIELDS ( Description ) WITH ...`로 바꾼다.
3. `failed`와 `COMMIT ENTITIES` 뒤 `sy-subrc`를 확인하지 않고 무조건 'Saved'를 출력한다. → MODIFY 뒤 `IF failed IS NOT INITIAL` 처리, `COMMIT ENTITIES` 뒤 `IF sy-subrc <> 0`이면 오류 출력과 `ROLLBACK ENTITIES`. EML은 실패해도 예외를 던지지 않고 `failed`/`reported`에 결과를 담기 때문에 확인 코드가 반드시 필요하다.

</details>

---

### C-034. RAP 트랜잭션 모델: 저장 시퀀스, 세이버 순서, 금지 문장, $batch [개념] ★★★
<!-- src: RP-040, RP-041, RP-042, RB-071, MX-064, RB-086, RB-091 -->
Travel BO를 저장할 때 RAP 런타임이 어떤 순서로 무엇을 하는지 살펴본다.

(1) RAP 트랜잭션의 상호작용 단계(interaction phase)와 저장 시퀀스(save sequence)를 설명하시오. early save phase와 late save phase에서 호출되는 세이버 메서드를 순서대로 쓰고, "point of no return"의 의미와 `COMMIT ENTITIES`와 `COMMIT WORK`의 차이를 쓰시오.

(2) late numbering이 **없는** unmanaged BO의 세이버 클래스다. 각 메서드는 호출되면 자기 이름을 `zcl_trace=>log`(문자열 테이블)에 추가한다. `check_before_save`는 버퍼의 오류 플래그가 켜져 있으면 `failed`에 항목을 넣는다.

```abap
CLASS lsc_travel DEFINITION INHERITING FROM cl_abap_behavior_saver.
  PROTECTED SECTION.
    METHODS finalize          REDEFINITION.
    METHODS check_before_save REDEFINITION.
    METHODS cleanup_finalize  REDEFINITION.
    METHODS save              REDEFINITION.
    METHODS cleanup           REDEFINITION.
ENDCLASS.

CLASS lsc_travel IMPLEMENTATION.
  METHOD finalize.
    APPEND `finalize` TO zcl_trace=>log.
  ENDMETHOD.
  METHOD check_before_save.
    APPEND `check_before_save` TO zcl_trace=>log.
    IF lcl_buffer=>error_flag = abap_true.
      APPEND VALUE #( TravelID = lcl_buffer=>travel_id ) TO failed-travel.
    ENDIF.
  ENDMETHOD.
  METHOD cleanup_finalize.
    APPEND `cleanup_finalize` TO zcl_trace=>log.
  ENDMETHOD.
  METHOD save.
    APPEND `save` TO zcl_trace=>log.
    " 버퍼 내용을 DB에 기록
  ENDMETHOD.
  METHOD cleanup.
    APPEND `cleanup` TO zcl_trace=>log.
    " 버퍼 비우기
  ENDMETHOD.
ENDCLASS.
```

(가) 오류 플래그가 켜진 상태에서 소비자가 `COMMIT ENTITIES`를 실행했을 때 `log`의 내용(순서대로)과 `sy-subrc`를 쓰시오.
(나) 이어서 원인을 고쳐 오류 플래그가 꺼진 뒤(log는 비움) 다시 `COMMIT ENTITIES`를 실행했을 때 `log`의 내용과 `sy-subrc`를 쓰시오.

(3) managed BO `ZR_Travel`(Draft 없음)에 `validation validateDates on save { field BeginDate, EndDate; }`가 있고, 종료일이 시작일보다 빠르면 `failed`와 `reported`를 채운다. DB의 해당 Travel은 BeginDate = 20240110, EndDate = 20240115다. 다음 코드 실행 후 ① `ls_failed1-travel`의 행 수 ② `lv_subrc` ③ `ls_failed2-travel`의 행 수 ④ COMMIT 후 DB의 EndDate ⑤ COMMIT 후 트랜잭셔널 버퍼에 EndDate = 20240101 변경이 남아 있는지 ⑥ `COMMIT ENTITIES` 대신 `COMMIT WORK`를 썼다면 어떻게 되는지 쓰시오.

```abap
MODIFY ENTITIES OF zr_travel
  ENTITY Travel
    UPDATE FIELDS ( EndDate )
    WITH VALUE #( ( TravelUUID = lv_uuid  EndDate = '20240101' ) )
  FAILED   DATA(ls_failed1)
  REPORTED DATA(ls_reported1).

COMMIT ENTITIES
  RESPONSE OF zr_travel
  FAILED   DATA(ls_failed2)
  REPORTED DATA(ls_reported2).
DATA(lv_subrc) = sy-subrc.
```

(4) managed BO `ZMX_R_Travel`(키는 managed numbering UUID)의 `validation validateDates on save { create; }`는 EndDate < BeginDate이면 그 인스턴스를 `failed`와 `reported`에 넣는다. ① (A)에서 `lines( ls_mapped-travel )`과 `lines( ls_failed-travel )` ② (B)에서 `sy-subrc`와 `lines( ls_cfailed-travel )` ③ DB에 새로 저장된 Travel 행 수를 쓰시오.

```abap
MODIFY ENTITIES OF zmx_r_travel
  ENTITY Travel
    CREATE FIELDS ( AgencyID CustomerID BeginDate EndDate )
    WITH VALUE #( ( %cid = 'T1' AgencyID = '070001' CustomerID = '000001'
                    BeginDate = '20261101' EndDate = '20261105' )
                  ( %cid = 'T2' AgencyID = '070001' CustomerID = '000002'
                    BeginDate = '20261110' EndDate = '20261101' ) )
  MAPPED DATA(ls_mapped) FAILED DATA(ls_failed) REPORTED DATA(ls_reported).
" (A)
COMMIT ENTITIES RESPONSE OF zmx_r_travel
  FAILED DATA(ls_cfailed) REPORTED DATA(ls_creported).
" (B)
```

(5) managed BO의 action 구현이다. RAP 트랜잭션 규칙에 어긋나는 곳 세 군데를 찾아 이유와 고칠 방법을 쓰시오.

```abap
METHOD acceptTravel.
  MODIFY ENTITIES OF zr_traveltp IN LOCAL MODE
    ENTITY Travel UPDATE FIELDS ( OverallStatus )
    WITH VALUE #( FOR key IN keys ( %tky = key-%tky OverallStatus = 'A' ) )
    FAILED failed REPORTED reported.

  " 승인 이력을 로그 테이블에 바로 기록
  INSERT zaccept_log FROM TABLE @( VALUE #( FOR key IN keys
                                     ( travel_uuid = key-TravelUUID accepted_by = sy-uname ) ) ).
  COMMIT WORK.

  MESSAGE 'Travel accepted' TYPE 'S'.

  READ ENTITIES OF zr_traveltp IN LOCAL MODE
    ENTITY Travel ALL FIELDS WITH CORRESPONDING #( keys )
    RESULT DATA(travels).
  result = VALUE #( FOR t IN travels ( %tky = t-%tky %param = t ) ).
ENDMETHOD.
```

(6) 행동 구현에서 트랜잭션 단계별로 허용되는 작업에 대한 설명으로 옳은 것을 고르고, 나머지가 틀린 이유를 쓰시오.

① DB 변경(INSERT/UPDATE/DELETE)은 상호작용 단계에서 해도 저장 순서에서 함께 커밋되므로 문제없다.
② 업데이트 함수 모듈(`CALL FUNCTION ... IN UPDATE TASK`)은 늦은 저장 단계에서만 등록해야 한다.
③ 동기 RFC(`CALL FUNCTION ... DESTINATION`)는 늦은 저장 단계에서 쓰는 것이 권장된다.
④ `RAISE ENTITY EVENT`는 상호작용 단계에서도 쓸 수 있다.
⑤ `RAISE EXCEPTION`으로 RAP 트랜잭션을 빠져나가는 것은 허용된다.

(7) Fiori Elements(OData V4)가 보내는 `$batch` 요청과 changeset이 RAP 트랜잭션과 어떻게 대응하는지 설명하시오. Draft 앱에서는 무엇이 다른지도 쓰시오.

<details><summary>정답·해설</summary>

**(1)**
- 상호작용 단계: 핸들러 클래스(`lhc_`, `CL_ABAP_BEHAVIOR_HANDLER` 상속)의 메서드(create/update/delete/read, action, `on modify` determination, 기능 제어·권한)가 트랜잭션 버퍼를 바꾼다. 버퍼 데이터는 잠시 불일치할 수 있지만 DB는 바뀌지 않는다.
- 저장 시퀀스: `COMMIT ENTITIES`(OData에서는 프레임워크가 자동 호출)로 시작하고, 세이버 클래스(`lsc_`, `CL_ABAP_BEHAVIOR_SAVER` 상속)의 메서드가 호출된다.
  - early save phase: `finalize`(최종 계산, managed의 `on save` determination) → `check_before_save`(일관성 검사, managed의 validation) → 실패가 있으면 `cleanup_finalize` 후 상호작용 단계로 복귀(`sy-subrc = 4`).
  - late save phase: `adjust_numbers`(late numbering일 때만) → `save`(managed + 저장 옵션이면 `save_modified`) → `cleanup`(버퍼 정리).
- point of no return: late save phase에 들어가면 상호작용 단계로 돌아갈 수 없다. 커밋에 성공하거나, 실패하면 롤백과 런타임 오류다. 그래서 모든 검사는 early save phase에서 끝내야 한다.
- `COMMIT ENTITIES`는 저장 시퀀스를 실행하고 `sy-subrc`와 응답(`RESPONSE OF ... FAILED/REPORTED`)을 돌려주며, 오류 시 상호작용 단계로 돌아갈 수 있다. RAP에서 `COMMIT WORK`도 저장 시퀀스를 실행하지만, 오류가 나면 항상 런타임 오류가 되고 RAP 응답을 받을 수 없다.
- DB 변경(INSERT/UPDATE/DELETE, `CALL FUNCTION ... IN UPDATE TASK`)은 late save phase에서만 허용된다. `ROLLBACK ENTITIES`는 버퍼를 버리고 트랜잭션을 끝낸다.

**(2)**
- (가) `finalize`, `check_before_save`, `cleanup_finalize` / `sy-subrc = 4`
- (나) `finalize`, `check_before_save`, `save`, `cleanup` / `sy-subrc = 0`

early save phase에서 `failed`가 채워지면 late save phase로 가지 않고 `cleanup_finalize`를 호출한 뒤 상호작용 단계로 돌아간다. 버퍼는 유지되므로 수정 후 다시 커밋할 수 있다. 오류가 없으면 late save phase로 넘어가 `save`, `cleanup` 순으로 실행된다. late numbering이 없으므로 `adjust_numbers`는 호출되지 않는다(정의도 없음). `cleanup_finalize`는 실패했을 때만 호출된다.

**(3)** ① 0 ② 4 ③ 1 ④ 20240115(변경 안 됨) ⑤ 남아 있다 ⑥ 런타임 오류(덤프)
- ① `on save` validation은 MODIFY 시점이 아니라 저장 순서에서 실행되므로 MODIFY의 `failed`는 비어 있다.
- ②③ early save phase의 `check_before_save`에서 validation이 실패하면 late save phase로 가지 않고 상호작용 단계로 돌아온다. `sy-subrc = 4`, 응답의 `failed`에 그 인스턴스가 들어간다. (late save phase에서 실패하면 8)
- ④ DB에는 아무것도 쓰이지 않았다.
- ⑤ 버퍼의 변경은 그대로 남아 소비자가 고쳐서 다시 커밋할 수 있다. 포기하려면 `ROLLBACK ENTITIES`.
- ⑥ `COMMIT WORK`도 저장 순서를 시작하지만, 오류가 나면 상호작용 단계로 돌아가는 대신 런타임 오류가 난다. 응답을 받고 오류를 처리하려면 `COMMIT ENTITIES`를 써야 한다.

**(4)** ① 2, 0 ② 4, 1 ③ 0
- `on save` validation은 MODIFY(상호작용 단계)에서는 돌지 않는다. 그래서 (A)에서 두 건 모두 버퍼에 생성되고 mapped 2건, failed 0건이다.
- `COMMIT ENTITIES`가 저장 시퀀스를 시작하면 `check_before_save`에서 validation이 돌아 T2가 실패한다. 실패가 하나라도 있으면 **저장 시퀀스 전체가 취소된다**. T1도 저장되지 않고 `sy-subrc = 4`다.
- RAP 트랜잭션은 "전부 저장 아니면 전부 취소"다. 소비자는 T2를 고치거나 빼고 다시 COMMIT하거나 `ROLLBACK ENTITIES`로 버퍼를 비운다.

**(5)**
1. 상호작용 단계(action)에서 DB를 직접 변경(`INSERT`)했다. DB 변경은 late save phase에서만 허용된다(버퍼가 아직 불일치할 수 있고 Draft·롤백과 어긋남). → 로그 기록은 `managed with additional save`로 바꿔 세이버의 `save_modified`에서 한다.
2. `COMMIT WORK`. 트랜잭션 제어는 RAP 프레임워크 몫이고, 핸들러·세이버 안의 `COMMIT WORK`/`ROLLBACK WORK`/`COMMIT ENTITIES`는 금지다(런타임 오류 `BEHAVIOR_ILLEGAL_STATEMENT`). → 지운다.
3. `MESSAGE ... TYPE 'S'`(INTO 없는 MESSAGE 등 화면 처리)는 행동 구현에서 허용되지 않는다. → `reported-travel`에 `%msg = new_message_with_text( severity = if_abap_behv_message=>severity-success text = 'Travel accepted' )`로 보고한다.

그 밖의 금지 사항: `CALL TRANSACTION`, `SUBMIT`, `RAISE EXCEPTION`으로 트랜잭션 탈출, 상호작용 단계에서의 `CALL FUNCTION ... IN UPDATE TASK`. 커밋하는 BAPI도 action에서 부르면 안 되고 저장 시퀀스(unmanaged save)에서 처리한다. ABAP Cloud에서는 `sy-uname` 대신 `cl_abap_context_info=>get_user_technical_name( )`을 쓴다.

**(6)** ②
- ① 틀리다. DB 변경은 late save phase(`save`, `save_modified`)에서만 허용된다. 다른 단계의 데이터는 일관성이 보장되지 않고, SAP LUW가 여러 DB 트랜잭션으로 쪼개진다.
- ② 맞다. 업데이트 태스크 등록, bgRFC(`IN BACKGROUND UNIT`)도 late save phase에서만 한다.
- ③ 틀리다. sRFC·aRFC는 상호작용 단계와 early save phase에서만 허용되고 late save phase에서는 금지다(암묵적 DB 커밋 위험).
- ④ 틀리다. 이벤트 발행은 late save phase에서만 한다.
- ⑤ 틀리다. 예외로 RAP 트랜잭션을 빠져나가면 안 된다. 오류는 `failed`/`reported`로 전달한다.

**(7)**
- `$batch`는 여러 OData 요청을 HTTP 요청 하나로 묶는다. 그 안의 변경 요청 묶음(changeset, V4에서는 atomicity group)이 하나의 RAP 트랜잭션(LUW)으로 처리된다.
- 한 changeset의 모든 변경(POST/PATCH/DELETE, action)은 상호작용 단계에서 버퍼에 쌓이고, changeset 끝에서 RAP 런타임이 암묵적으로 `COMMIT ENTITIES`에 해당하는 저장 순서를 실행한다.
- 하나라도 실패하면(validation 오류 등) changeset 전체가 저장되지 않는다(원자성). `reported`의 메시지는 OData 오류·`sap-messages`로 전달된다.
- 읽기(GET)는 changeset 밖에서 따로 처리된다.
- Draft 앱에서는 입력 중 PATCH가 각각 Draft 테이블에 바로 저장되고, Activate(Save) 때 활성 데이터에 대한 저장 순서가 실행된다.
- 그래서 행동 구현에서 직접 `COMMIT WORK`하면 안 된다. 커밋 시점은 OData 런타임(또는 EML의 `COMMIT ENTITIES`)이 정한다.

</details>

---

### C-035. RAP 비즈니스 이벤트: 정의·발행·소비 [코드] ★★★
<!-- src: RP-047, RB-081, RB-082 -->
Travel이 승인(`OverallStatus = 'A'`)되면 다른 시스템과 같은 시스템의 알림 모듈에 알린다. BO는 `managed with additional save`다.

(1) BDEF에서 이벤트를 정의하는 방법을 쓰시오(파라미터가 없을 때와 있을 때). 파생 이벤트와 side effect용 이벤트 문법도 쓰시오.

(2) 이벤트를 어디서 어떤 문장으로 발행하는지 쓰고, 그 위치여야 하는 이유를 쓰시오. managed BO에서 필요한 BDEF 설정도 쓰시오.

(3) 이벤트 발행과 로컬 소비 코드의 빈칸 1~5를 채우시오.

```abap
" 행동 구현(세이버)
METHOD save_modified.
  IF update-travel IS NOT INITIAL.
    ____(1)____ zr_travel~travelAccepted
      FROM VALUE #( FOR ls_upd IN update-travel
                    WHERE ( OverallStatus = 'A' AND %control-OverallStatus = if_abap_behv=>mk-on )
                    ( %key = ls_upd-%key ) ).
  ENDIF.
ENDMETHOD.
```

```abap
" 이벤트 핸들러 클래스(전역)
CLASS zcl_travel_evt_handler DEFINITION PUBLIC ____(2)____ zr_travel.
ENDCLASS.
CLASS zcl_travel_evt_handler IMPLEMENTATION.
ENDCLASS.

" 같은 클래스의 Local Types
CLASS lhe_travel DEFINITION INHERITING FROM ____(3)____.
  PRIVATE SECTION.
    METHODS on_accepted ____(4)____ it_accepted FOR zr_travel~travelAccepted.
ENDCLASS.
CLASS lhe_travel IMPLEMENTATION.
  METHOD on_accepted.
    " (읽기 등 modify 단계 작업)
    cl_abap_tx=>____(5)____( ).
    " DB 변경 (예: 알림 테이블에 INSERT)
  ENDMETHOD.
ENDCLASS.
```

(4) (3)의 `save_modified`에서 `%control-OverallStatus`를 함께 확인하는 이유를 쓰시오. 이벤트 핸들러 메서드의 특징(가시성, 파라미터 타입, 응답 파라미터)과 `cl_abap_tx=>save( )`를 부르는 이유를 쓰시오.

(5) 외부 시스템(SAP Event Mesh 등)으로 이벤트를 보내는 방법과, 로컬 소비가 원래 BO를 다시 바꾸려면 어떻게 해야 하는지 쓰시오.

(6) 이벤트와 determination·action은 언제 각각 쓰는지 쓰시오.

<details><summary>정답·해설</summary>

**(1)** 엔티티 행동 본문에 `event travelAccepted;`. 추가 정보를 넘길 때는 `event travelAccepted parameter ZA_TravelEvent;`(파라미터는 CDS 추상 엔티티). 페이로드에는 항상 인스턴스 키가 들어간다. 파생 이벤트는 `managed event ... on ...`, side effect용은 `event ... for side effects`.

**(2)** 저장 시퀀스의 late save phase(세이버의 `save` 또는 `save_modified`)에서 `RAISE ENTITY EVENT zr_travel~travelAccepted FROM VALUE #( ( %key-TravelUUID = ... %param = ... ) )`로 발행한다. 이벤트는 저장이 확정된 사실만 알려야 한다. 상호작용 단계에서 발행하면 나중에 롤백된 변경도 알리게 되므로, RAP는 late save phase 밖에서의 발행을 허용하지 않는다. managed BO는 기본 저장을 쓰므로 `managed with additional save ...`로 세이버의 `save_modified`를 만들고, 거기서 `update-travel` 등을 보고 이벤트를 발행한다.

**(3)** (1) `RAISE ENTITY EVENT` (2) `FOR EVENTS OF` (3) `cl_abap_behavior_event_handler` (4) `FOR ENTITY EVENT` (5) `save`

**(4)** `save_modified`의 `update` 파라미터에는 이번에 바뀐 필드가 `%control`로 표시된다. 그래서 상태가 원래 A였던 건이 아니라 "이번에 A로 바뀐 건"만 고를 수 있다. 이벤트 핸들러 메서드는 PRIVATE 인스턴스 메서드이고, 파라미터 타입은 `TABLE FOR EVENT`(키와 `%param`)이며 응답 파라미터가 없다. 핸들러는 별도 트랜잭션에서 비동기로 실행되며, 제어된 SAP LUW 규칙에 따라 DB를 바꾸기 전에 `cl_abap_tx=>save( )`로 저장 단계로 전환해야 한다.

**(5)** 이벤트 바인딩(Event Binding) 객체로 이벤트를 이벤트 유형(namespace, business object, operation)에 매핑하고, Enterprise Event Enablement 채널(SAP Event Mesh/Advanced Event Mesh 등)을 설정해 외부로 보낸다. 페이로드는 키와 파라미터다. 로컬 소비 쪽에서 원래 BO를 다시 바꾸려면 자기 트랜잭션에서 EML과 `COMMIT ENTITIES`를 쓴다. 소비자가 실패해도 원래 트랜잭션에는 영향이 없다.

**(6)** 이벤트는 "Travel이 승인됨" 같은 결과를 느슨하게(비동기로) 알리는 수단이고, 제공자는 소비자가 무엇을 하는지 모른다. 같은 트랜잭션 안에서 바로 무언가를 해야 하면 이벤트가 아니라 determination이나 action을 쓴다.

</details>

---

## 서비스 노출·OData 프로토콜

### C-036. 서비스 정의·서비스 바인딩과 OData 노출 방식 [개념] ★★
<!-- src: RP-004, RB-092, RB-093, MX-066, RB-046 -->
Travel BO를 Fiori 앱용과 외부 시스템 API용으로 동시에 노출하려 한다.

(1) 서비스 정의와 서비스 바인딩의 차이를 설명하고, Travel·Booking을 노출하는 서비스 정의를 쓰시오.

(2) 서비스 바인딩 유형(OData V4 - UI, OData V4 - Web API, OData V2 - UI, OData V2 - Web API, InA - UI, SQL - Web API)의 용도를 표로 쓰시오. OData V2와 V4를 고르는 기준도 쓰시오.

(3) 하나의 서비스를 여러 버전으로 운영하는 방법을 쓰시오. 온프레미스에서 바인딩을 Publish하면 무엇이 처리되는지도 쓰시오.

(4) 서비스 정의와 서비스 바인딩에 대한 설명으로 옳지 **않은** 것을 고르시오.

① 서비스 정의에서 `expose ZC_Travel as Travel;`처럼 엔티티에 외부 이름(별칭)을 줄 수 있다.
② 값 도움말·텍스트 엔티티도 서비스 정의에 노출하는 것이 일반적이다.
③ 하나의 서비스 정의를 여러 서비스 바인딩에서 쓸 수 있다.
④ OData V4 - Web API 바인딩도 Fiori Elements 미리보기를 제공한다.
⑤ 서비스 바인딩을 Publish해야 서비스 URL로 호출할 수 있다.

(5) 다음 중 옳지 **않은** 것을 고르시오.

① "OData V4 - UI" 바인딩은 Fiori Elements 앱용이며 UI 어노테이션을 메타데이터와 함께 제공한다.
② "OData V4 - Web API" 바인딩은 UI 어노테이션 없이 다른 시스템·프로그램이 쓰는 API용이다.
③ 서비스 정의에서는 노출할 엔티티를 `expose`로 나열하고 별칭을 줄 수 있다.
④ 하나의 서비스 정의에 바인딩 유형이 다른 여러 서비스 바인딩을 만들 수 있다.
⑤ Draft가 켜진 BO는 OData V2 바인딩으로만 노출할 수 있다.

(6) CDS 뷰를 OData 서비스로 노출하는 방법 세 가지(`@OData.publish`, SEGW Reference Data Source, RAP 서비스 정의·바인딩)를 비교하시오.

<details><summary>정답·해설</summary>

**(1)** 서비스 정의는 노출할 엔티티의 범위("무엇을")를 정하고 프로토콜과 무관하다. 서비스 바인딩은 서비스 정의를 특정 프로토콜·용도("어떻게": OData V2/V4, UI/Web API, InA, SQL 등)에 묶는다. Publish해야 엔드포인트가 활성화되고 Fiori Elements Preview가 가능하다. 하나의 서비스 정의에 여러 바인딩(예: V4 UI와 V4 Web API)을 만들 수 있다.

```abap
define service ZUI_TRAVEL {
  expose ZC_TravelTP  as Travel;
  expose ZC_BookingTP as Booking;
}
```

**(2)**

| 유형 | 용도 |
|---|---|
| OData V4 - UI | Fiori Elements·UI5 앱. UI 어노테이션(메타데이터 확장 포함)과 Draft 지원, 미리보기 가능. 신규 개발 표준 |
| OData V4 - Web API | 다른 시스템이 호출하는 API. UI 메타데이터 없음, 미리보기 없음. 통신 시나리오로 공개 |
| OData V2 - UI / Web API | V2만 지원하는 기존 클라이언트·템플릿용 |
| InA - UI | 분석 쿼리(transient 뷰)를 분석 클라이언트(SAP Analytics Cloud, Fiori 분석 앱)에 공개 |
| SQL - Web API | ODBC로 CDS를 SQL 조회(외부 리포팅 도구) |

V4는 신규 개발의 기본값이다(Draft, 그룹화, 효율적인 배치 등 최신 Fiori Elements 기능). V2는 V2만 지원하는 기존 앱·도구·소비자와 호환이 필요할 때 쓴다.

**(3)** 한 서비스 바인딩에 서비스 정의를 여러 버전(0001, 0002 ...)으로 추가할 수 있다. 호환되지 않는 변경은 새 서비스 정의를 새 버전으로 추가해 기존 소비자를 깨뜨리지 않는다. 온프레미스에서는 Publish가 Gateway 서비스 등록(로컬 서비스 엔드포인트)까지 처리한다(V4는 `/IWFND/V4_ADMIN`에서 서비스 그룹 공개를 하기도 한다).

**(4)** ④. Web API 바인딩은 UI 메타데이터 없이 API로만 쓰므로 Fiori Elements 미리보기가 없다. 미리보기는 UI 유형 바인딩에서만 된다(객관식 단골 함정). ②: 값 도움말 뷰는 BO 엔티티에서 참조하면 서비스에 자동으로 노출되지만, 서비스 정의에 명시적으로 함께 노출하는 경우도 흔하다. 노출되지 않은 엔티티로 가는 association은 서비스에서 내비게이션으로 나타나지 않는다.

**(5)** ⑤. Draft BO는 OData V4로 노출하는 것이 권장되며 Fiori Elements V4가 Draft를 완전히 지원한다(V2도 가능). ④처럼 같은 서비스 정의를 UI용 V4와 Web API용 V4로 따로 바인딩하는 경우가 흔하다.

**(6)**

| 방법 | 방식 | 특징 |
|---|---|---|
| `@OData.publish: true` | DDIC 기반 CDS 뷰에 어노테이션, 활성화 시 Gateway 서비스 생성 후 `/IWFND/MAINT_SERVICE`에서 등록 | OData V2, 읽기 위주(쓰기는 BOPF 연동). 뷰 엔티티에서는 쓸 수 없는 옛 방식 |
| SEGW Reference Data Source | SEGW 프로젝트에 CDS를 참조로 매핑, MPC/DPC 생성 | V2. 필요하면 DPC_EXT를 재정의해 로직 추가. 클래식 방식 |
| RAP 서비스 정의 + 서비스 바인딩 | `define service`로 엔티티 노출, 바인딩에서 V2/V4·UI/Web API 선택 후 Publish | 현재 표준. 트랜잭션은 BDEF, UI는 메타데이터 확장. ABAP Cloud에서 유일한 방법 |

S/4HANA 2020 이후 신규 개발은 RAP을 쓴다. 기존 SEGW 서비스 유지보수 질문(MPC/DPC, `GET_ENTITYSET` 재정의)도 함께 나올 수 있다.

</details>

---

### C-037. OData URL: 기본 용어, 쿼리 옵션, HTTP 메서드, V2→V4 변환 [작성] ★★★
<!-- src: XE-001, XE-002, XE-003, XE-004, XE-005, XE-026 -->
OData V4 서비스 루트가 `/sap/opu/odata4/sap/zui_travel_o4/srvd/sap/zui_travel/0001/`이고, entity set `Travel`(키 `TravelID`, Edm.String)에는 `AgencyID`, `Description`, `TotalPrice`(Edm.Decimal), `CurrencyCode`, `OverallStatus` 속성과 navigation `_Booking`이 있다.

(1) OData 서비스의 entity type, entity set, entity, navigation property의 의미를 이 서비스의 예로 쓰시오. `$metadata` 문서에 무엇이 들어 있는지와 UI5/Fiori가 이를 어떻게 쓰는지도 설명하시오.

(2) 서비스 루트 뒤에 붙는 상대 URL을 쓰시오.
- (가) 상태가 `O`이고 TotalPrice가 1000보다 큰 여행의 TravelID, Description, TotalPrice만, TotalPrice 내림차순으로 상위 10건
- (나) TravelID `00000042` 한 건과 그 예약(Booking)들을 함께
- (다) 통화가 `EUR`인 여행의 건수만(숫자 하나)
- (라) 한 페이지 20건 기준 3페이지 데이터와 전체 건수를 함께
- (마) Description에 `Seoul`이 포함된 여행
- (바) 서비스의 메타데이터 문서

(3) 단순화한 `Travel` entity set에 다음 6건이 있다. 각 요청이 돌려주는 결과를 쓰시오. (가), (나)는 결과 행의 TravelID를 순서대로 쓴다.

| TravelID | Status | Price | Currency |
|---|---|---|---|
| 1 | O | 500 | EUR |
| 2 | A | 1500 | EUR |
| 3 | O | 2000 | USD |
| 4 | X | 1200 | EUR |
| 5 | O | 800 | USD |
| 6 | A | 900 | EUR |

```text
(가) Travel?$top=2&$skip=1&$orderby=Price desc&$filter=Status eq 'O' or Price gt 1000 and Currency eq 'EUR'&$select=TravelID
(나) Travel?$filter=(Status eq 'O' or Price gt 1000) and Currency eq 'EUR'&$orderby=Price desc&$skip=1&$top=2&$select=TravelID
(다) Travel/$count?$filter=Currency eq 'USD'
```

(4) OData 작업과 HTTP 메서드의 대응표다. 빈칸 1~7을 채우시오.

| 작업 | OData V2 | OData V4 |
|---|---|---|
| 조회(entity set / entity) | ____(1)____ | GET |
| 생성 | ____(2)____ | POST |
| 일부 속성만 수정 | ____(3)____ (또는 PATCH) | ____(4)____ |
| 전체 교체 | ____(5)____ | PUT |
| 삭제 | DELETE | DELETE |
| 여러 요청을 묶어 한 번에 전송 | POST `/____(6)____` | POST `/____(6)____` |
| 부작용이 있는 동작(V4 action) 호출 | GET 또는 POST (function import에 지정) | ____(7)____ |

(5) OData V2와 V4의 차이에 대한 설명으로 **틀린** 것을 고르시오.

① 응답에 전체 건수를 포함할 때 V2는 `$inlinecount=allpages`, V4는 `$count=true`를 쓴다.
② 문자열 포함 검색은 V2 `substringof('x',Name)`, V4 `contains(Name,'x')`이다.
③ V4는 `$expand=_Booking($select=BookingID;$filter=Price gt 100)`처럼 확장 대상에 쿼리 옵션을 중첩할 수 있다.
④ V2의 function import는 V4에서 action(부작용 있음)과 function(부작용 없음)으로 나뉘고, entity에 묶인(bound) 형태도 지원한다.
⑤ V4의 기본 데이터 형식은 Atom(XML)이며, JSON을 받으려면 `$format=json`을 반드시 붙여야 한다.

(6) 같은 데이터를 V2 서비스(`/sap/opu/odata/sap/ZTRAVEL_SRV/`, entity set `TravelSet`)와 RAP V4 서비스(`/sap/opu/odata4/sap/ztravel_o4/srvd/sap/ztravel/0001/`, entity set `Travel`)로 제공한다. 속성과 navigation 이름은 같고, `BeginDate`는 V2에서 `Edm.DateTime`, V4에서 `Edm.Date`다. 다음 V2 요청과 같은 결과를 주는 V4 요청 URL을 쓰고 변환 포인트를 쓰시오.

```text
/sap/opu/odata/sap/ZTRAVEL_SRV/TravelSet?$filter=substringof('Rome',Description) and BeginDate ge datetime'2026-10-01T00:00:00'&$inlinecount=allpages&$expand=to_Booking&$select=TravelID,Description,to_Booking/BookingID&$format=json
```

<details><summary>정답·해설</summary>

**(1)**
- **entity type**: 데이터 구조 정의(속성, 키, 타입). 예: `TravelType`(TravelID, Description, TotalPrice ...).
- **entity set**: 같은 entity type 인스턴스의 모음이자 URL로 접근하는 단위. 예: `/Travel`. DB 테이블에 비유된다.
- **entity**: entity set 안의 한 건, 키로 접근. 예: `/Travel('00000042')`.
- **navigation property**: 다른 entity(set)로 가는 연관. 예: `/Travel('00000042')/_Booking`. V2는 Association/AssociationSet, V4는 NavigationProperty + NavigationPropertyBinding으로 정의한다.
- **$metadata**: 서비스의 EDMX 문서. entity type/set, 속성 타입(Edm.String, Edm.Decimal ...), 키, navigation, action/function(V2는 function import), 어노테이션(UI, Common, Capabilities 등)이 들어 있다.
- 사용: UI5 OData 모델은 이를 읽어 키 경로 생성, 타입 변환, 요청 생성에 쓰고, Fiori Elements는 어노테이션을 읽어 화면(테이블 컬럼, 필터, 폼)을 런타임에 만든다. 서비스 문서(서비스 루트 URL)는 entity set 목록을 준다. 서비스가 동작하지 않을 때는 먼저 `$metadata`를 브라우저로 열어 보는 것이 기본 점검이다.

**(2)**
- (가) `Travel?$filter=OverallStatus eq 'O' and TotalPrice gt 1000&$select=TravelID,Description,TotalPrice&$orderby=TotalPrice desc&$top=10`
- (나) `Travel('00000042')?$expand=_Booking`
- (다) `Travel/$count?$filter=CurrencyCode eq 'EUR'`
- (라) `Travel?$skip=40&$top=20&$count=true`
- (마) `Travel?$filter=contains(Description,'Seoul')`
- (바) `$metadata`

비교 연산자는 `eq ne gt ge lt le`, 논리 연산자는 `and or not`. 문자열 리터럴은 작은따옴표, 숫자는 그대로 쓴다. 3페이지는 앞의 40건을 건너뛴다(`$skip=(3-1)*20`). (라) V2에서는 전체 건수를 `$inlinecount=allpages`로 받는다. (마) V2는 `substringof('Seoul',Description)`. 서비스가 검색을 지원하면(`@Search.searchable`) `$search=Seoul`로 여러 필드를 한 번에 검색할 수도 있다. (나) 키를 `Travel(TravelID='00000042')`처럼 이름과 함께 써도 되고, Draft 서비스라면 `Travel(TravelID='00000042',IsActiveEntity=true)`처럼 키 전체가 필요하다. URL의 공백 등은 퍼센트 인코딩된다(`%20`).

**(3)** (가) `2, 4` (나) `4, 1` (다) `2`
- 시스템 쿼리 옵션은 URL에 적힌 순서와 관계없이 **$filter → $orderby → $skip → $top → $select** 순으로 적용된다.
- (가) `and`가 `or`보다 우선한다: `Status eq 'O' or (Price gt 1000 and Currency eq 'EUR')`. 괄호 안: 2(1500 EUR), 4(1200 EUR). Status O: 1, 3, 5. 합집합 {1,2,3,4,5}. Price 내림차순: 3(2000), 2(1500), 4(1200), 5(800), 1(500). 1건 건너뛰고 2건 → 2, 4.
- (나) 괄호 안 {1,2,3,4,5} 중 EUR: 1, 2, 4. 내림차순: 2(1500), 4(1200), 1(500). 1건 건너뛰고 2건 → 4, 1.
- (다) USD: 3, 5 → 본문이 숫자만 있는 텍스트 `2`.

**(4)** 1. `GET` 2. `POST` 3. `MERGE` 4. `PATCH` 5. `PUT` 6. `$batch` 7. `POST`

V2의 부분 수정은 SAP Gateway에서 MERGE를 쓴다(방화벽 문제로 `POST` + `X-HTTP-Method: MERGE`로 터널링하기도 함). V4는 표준 PATCH다. PUT은 보내지 않은 속성을 기본값으로 덮어쓸 수 있어 부분 수정에 쓰면 안 된다. V4의 function(부작용 없음)은 GET, action(부작용 있음)은 POST다. RAP BDEF의 `action`은 V4 action(POST), `function`은 V4 function(GET)이 된다.

**(5)** ⑤. V4의 표준 페이로드 형식은 JSON이다(메타데이터 문서만 XML/CSDL). SAP Gateway V2 서비스는 기본이 Atom/XML이라 `$format=json`이나 `Accept: application/json`이 필요했다. 그 밖의 차이: V4 날짜 타입 `Edm.Date`/`Edm.DateTimeOffset`(V2는 `Edm.DateTime`, 리터럴 `datetime'...'`), V4 `$search`, V4 `$apply`(집계), V4 JSON 응답 키 `value`(V2는 `d.results`). RAP 서비스 바인딩은 V2/V4를 모두 만들 수 있지만 새 개발은 V4가 권장이다.

**(6)**
```text
/sap/opu/odata4/sap/ztravel_o4/srvd/sap/ztravel/0001/Travel?$filter=contains(Description,'Rome') and BeginDate ge 2026-10-01&$count=true&$select=TravelID,Description&$expand=to_Booking($select=BookingID)
```
- `substringof('Rome',Description)` → `contains(Description,'Rome')` (인자 순서도 바뀜)
- `datetime'2026-10-01T00:00:00'` → Edm.Date 리터럴 `2026-10-01` (따옴표·접두어 없음)
- `$inlinecount=allpages` → `$count=true` (V4 응답의 `@odata.count`)
- V2의 `$select=...,to_Booking/BookingID` + `$expand` → V4는 확장 대상의 select를 `$expand=to_Booking($select=BookingID)`로 중첩
- `$format=json` → V4는 JSON이 기본이라 불필요
- 응답 구조도 다르다: V2 `{ d: { results: [...], __count: "n" } }`, V4 `{ "@odata.count": n, "value": [...] }`.

</details>

---

### C-038. OData 변경 요청: CSRF 토큰, ETag 낙관적 잠금, 직접 호출 코드 [코드] ★★★
<!-- src: XE-006, XE-007, XE-008 -->
RAP 기반 OData V4 서비스의 `Travel`에 ETag가 정의되어 있다(BDEF `etag master LocalLastChangedAt`). UI5 모델 없이 직접 호출하는 경우도 생각한다.

(1) SAP Gateway/RAP OData 서비스에서 `x-csrf-token`이 필요한 이유와 토큰을 얻고 쓰는 흐름을 설명하시오. UI5 OData 모델을 쓸 때 개발자가 직접 할 일이 있는지도 쓰시오.

(2) 사용자 A, B가 다음 순서로 요청했다. 성공한 PATCH는 `204 No Content`를 반환하고, 토큰·권한 문제는 없다. [3]~[6]의 HTTP 상태 코드를 쓰시오.

```text
[1] A: GET   Travel('42')                              → 200, ETag: W/"T1"
[2] B: GET   Travel('42')                              → 200, ETag: W/"T1"
[3] B: PATCH Travel('42')  If-Match: W/"T1"  {Description:"B"}   → ?
[4] A: PATCH Travel('42')  If-Match: W/"T1"  {Description:"A"}   → ?
[5] A: PATCH Travel('42')  (If-Match 헤더 없음)  {Description:"A"} → ?
[6] A: GET으로 새 ETag W/"T2"를 받은 뒤
       PATCH Travel('42')  If-Match: W/"T2"  {Description:"A"}   → ?
```

(3) (2)에서 ETag가 막는 문제가 무엇인지, 이런 방식을 무엇이라 부르는지 쓰시오. `If-Match: *`의 의미와 UI5·Fiori Elements가 ETag를 다루는 방식도 쓰시오.

(4) 브라우저 `fetch`로 Description만 바꾸려는 코드다. 실패하거나 위험한 부분을 모두 찾아 이유를 쓰고 고친 코드를 쓰시오.

```js
async function updateDescription() {
  const url = "/sap/opu/odata4/sap/zui_travel_o4/srvd/sap/zui_travel/0001/Travel('42')";
  await fetch(url, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ Description: "Changed" })
  });
  alert("saved");
}
```

(5) 이 서비스가 Draft 서비스라면 (4)의 방식으로 활성 인스턴스를 바로 바꿀 수 있는지 쓰시오.

<details><summary>정답·해설</summary>

**(1)**
- 이유: CSRF(Cross-Site Request Forgery) 방지. 사용자가 로그인된 상태에서 다른 사이트가 브라우저 쿠키를 이용해 변경 요청을 몰래 보내는 공격을 막는다. 변경 요청(POST/PUT/PATCH/MERGE/DELETE, `$batch`)에는 세션에 묶인 토큰이 있어야 한다.
- 흐름:
  1. GET(또는 HEAD) 요청에 헤더 `x-csrf-token: Fetch`를 붙여 보낸다(보통 서비스 루트).
  2. 응답 헤더 `x-csrf-token`에 토큰 값이 오고, 세션 쿠키가 설정된다.
  3. 변경 요청에 같은 세션 쿠키와 헤더 `x-csrf-token: <토큰>`을 보낸다.
  4. 토큰이 없거나 만료되면 `403 Forbidden`과 응답 헤더 `x-csrf-token: Required`가 온다 → 다시 Fetch 후 재시도.
- UI5: v2/v4 ODataModel이 토큰 가져오기, 저장, 만료 시 재요청을 자동으로 처리하므로 보통 직접 할 일이 없다(`tokenHandling` 기본 true). 직접 `fetch`/`jQuery.ajax`로 호출할 때만 위 흐름을 구현한다.
- GET은 데이터를 바꾸지 않으므로 토큰 검사가 없다. 테스트 도구(/IWFND/GW_CLIENT, Postman)에서 403이 나면 대부분 이 토큰 문제다.

**(2)** [3] `204`(성공, ETag가 W/"T2"로 바뀜) [4] `412 Precondition Failed` [5] `428 Precondition Required` [6] `204`

**(3)** ETag는 데이터 버전 값이다. 서버는 `If-Match`의 값과 현재 ETag를 비교해 같을 때만 변경한다. [3] 이후 현재 값은 T2이므로 [4]의 T1은 오래된 값 → 412(다른 사람이 먼저 바꿈). 내 변경이 남의 변경을 덮어쓰는 것(lost update)을 막는 **낙관적(optimistic) 잠금**이다. ETag가 정의된 엔티티에 조건 헤더 없이 변경하면 RAP/Gateway는 428을 돌려준다. 무조건 덮어쓰려면 `If-Match: *`를 쓸 수 있지만 낙관적 잠금의 의미가 사라진다. UI5 OData 모델은 읽을 때 받은 ETag(`@odata.etag`, V2 `__metadata.etag`)를 기억했다가 자동으로 `If-Match`를 붙인다. Fiori Elements에서 412가 나면 "다른 사용자가 변경했습니다" 메시지와 함께 새로 고침을 유도한다.

**(4)**
1. CSRF 토큰이 없다 → 403. 먼저 `x-csrf-token: Fetch`로 토큰을 받아 헤더에 넣는다.
2. `If-Match`가 없다 → ETag가 있는 엔티티라 428. 먼저 GET으로 ETag를 받아 `If-Match`에 넣는다.
3. 일부 속성만 바꾸는데 `PUT`(전체 교체)을 썼다 → 보내지 않은 속성이 초기화되거나 거부될 수 있다. `PATCH`를 쓴다.
4. 응답 상태를 확인하지 않고 무조건 "saved"를 띄운다 → `response.ok`를 확인하고 오류 본문(`error.message`)을 보여 준다.

```js
async function updateDescription() {
  const root = "/sap/opu/odata4/sap/zui_travel_o4/srvd/sap/zui_travel/0001/";
  const url = root + "Travel('42')";

  const r1 = await fetch(url, { headers: { "x-csrf-token": "Fetch" } });
  const token = r1.headers.get("x-csrf-token");
  const etag = r1.headers.get("ETag");

  const r2 = await fetch(url, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      "x-csrf-token": token,
      "If-Match": etag
    },
    body: JSON.stringify({ Description: "Changed" })
  });
  if (!r2.ok) {
    const err = await r2.json();
    alert(err.error.message);
    return;
  }
  alert("saved");
}
```

UI5 OData 모델은 1~3을 자동으로 처리한다.

**(5)** 바꿀 수 없다. Draft 서비스에서는 활성 인스턴스를 직접 PATCH할 수 없고, Edit → Draft 인스턴스 PATCH(`IsActiveEntity=false`) → Activate 순서를 따라야 한다(C-030 참고).

</details>

---

## Fiori Elements 연결 (어노테이션·값 도움말·메시지)

### C-039. UI 어노테이션과 메타데이터 확장: List Report·Object Page [작성] ★★★
<!-- src: RP-043, XE-009, XE-010, XE-011, XE-012 -->
Travel 서비스(OData V4 - UI)로 Fiori Elements List Report/Object Page 앱을 만든다.

(1) Fiori Elements 목록·객체 페이지를 위한 메타데이터 확장이다. 빈칸 1~6을 채우시오. (프로젝션 뷰 `ZC_TravelTP`에는 메타데이터 확장을 허용하는 어노테이션 `____(1)____`이 붙어 있다.)

```cds
@Metadata.layer: #____(2)____
@UI.headerInfo: { typeName: 'Travel', typeNamePlural: 'Travels',
                  title: { type: #STANDARD, value: 'TravelID' } }
annotate entity ZC_TravelTP with
{
  @UI.facet: [ { id: 'idTravel', purpose: #STANDARD, position: 10, label: 'Travel',
                 type: #____(3)____ },
               { id: 'idBooking', purpose: #STANDARD, position: 20, label: 'Bookings',
                 type: #LINEITEM_REFERENCE, targetElement: '____(4)____' } ]

  @UI.lineItem:       [ { position: 10 } ]
  @UI.identification: [ { position: 10 } ]
  @UI.____(5)____:    [ { position: 10 } ]     " 목록 위 필터 바에 표시
  TravelID;

  @UI.lineItem: [ { position: 90 },
                  { type: #____(6)____, dataAction: 'acceptTravel', label: 'Accept Travel' } ]
  OverallStatus;
}
```

(2) CDS 어노테이션이 OData V4 `$metadata`에서 어떤 Term으로 나오고 화면에서 무엇이 되는지 정리한 표다. 빈칸 7~12를 채우시오.

| CDS 어노테이션 | `$metadata`의 Term | 화면에서의 결과 |
|---|---|---|
| `@UI.lineItem` | `UI.LineItem` | List Report 테이블 컬럼(또는 Object Page의 하위 테이블 컬럼) |
| `@UI.selectionField` | ____(7)____ | 필터 바의 필터 필드 |
| `@UI.headerInfo` | `UI.HeaderInfo` | Object Page 제목, 테이블 제목(복수형 이름) |
| `@UI.facet` | ____(8)____ | Object Page의 섹션 구성 |
| `@UI.fieldGroup: [{ qualifier: 'Prices' }]` | ____(9)____ | 섹션 안의 폼(필드 묶음) |
| `@UI.identification` | `UI.Identification` | 기본 폼 섹션, 액션 버튼(Object Page 헤더) |
| `@EndUserText.label` | ____(10)____ | 필드 라벨, 컬럼 제목 |
| `@ObjectModel.text.element: ['AgencyName']` | ____(11)____ | 코드 옆에 텍스트 표시(예: `Agency A (070001)`) |
| `@Consumption.valueHelpDefinition` | ____(12)____ | 입력 필드의 값 도움말(F4) 다이얼로그 |
| `@Semantics.amount.currencyCode: 'CurrencyCode'` | `Measures.ISOCurrency` | 금액 옆에 통화 표시 |

(3) 프로젝션 뷰 `ZC_Travel`(`@Metadata.allowExtensions: true` 지정됨)에 대한 메타데이터 확장을 작성하시오.
- 헤더 정보: 단수 `Travel`, 복수 `Travels`, 제목은 `TravelID`, 설명은 `Description`
- Object Page 섹션 2개: `General`(identification 참조), `Prices`(field group `Prices` 참조)
- List Report 컬럼: TravelID(10), Description(20), OverallStatus(30)
- 필터 필드: TravelID, OverallStatus
- General 폼: TravelID, Description / Prices 폼: TotalPrice, CurrencyCode

(4) 어노테이션 한 줄(예: `@UI.lineItem: [{ position: 10 }]`)이 브라우저의 테이블 컬럼이 되기까지 거치는 객체와 단계를 순서대로 설명하시오. 메타데이터 확장 레이어(layer)의 우선순위도 쓰시오.

(5) 서비스 정의는 `ZC_Travel`을 노출한다. 다음 프로젝션 뷰와 MDE를 활성화하려 했는데 활성화 오류가 나거나, 활성화되더라도 Object Page의 Prices 섹션이 비어 있거나 MDE가 반영되지 않는다. 잘못된 곳을 모두 찾아 고치시오.

```cds
@EndUserText.label: 'Travel projection'
@AccessControl.authorizationCheck: #CHECK
define root view entity ZC_Travel
  provider contract transactional_query
  as projection on ZI_Travel
{
  key TravelID,
      Description,
      OverallStatus,
      TotalPrice,
      CurrencyCode
}
```

```cds
@Metadata.layer: #CORE
annotate entity ZC_Travel with
{
  @UI.facet: [{ id: 'Prices', type: #FIELDGROUP_REFERENCE,
                targetQualifier: 'prices', label: 'Prices', position: 10 }]
  @UI.lineItem: [{ position: 10 }]
  TravelID;

  @UI.fieldGroup: [{ qualifier: 'Prices', position: 10 }]
  TotalPrice;

  @UI.selectionField: [{ position: 10 }]
  AgencyID;
}
```

<details><summary>정답·해설</summary>

**(1)** 1. `@Metadata.allowExtensions: true` 2. `CORE`(고객 개발에서는 `#CUSTOMER` 등도 가능) 3. `IDENTIFICATION_REFERENCE` 4. `_Booking` 5. `selectionField` 6. `FOR_ACTION`

`@UI.lineItem`은 목록 표의 열, `@UI.identification`은 객체 페이지의 필드 그룹(IDENTIFICATION_REFERENCE facet이 보여 줌), `@UI.selectionField`는 필터 바, `#LINEITEM_REFERENCE` facet은 자식 목록(association 지정)이다. action 버튼은 `#FOR_ACTION` + `dataAction`(BDEF의 action 이름)으로 만들고, 프로젝션 BDEF에서 `use action`으로 노출되어 있어야 한다.

**(2)** 7. `UI.SelectionFields` 8. `UI.Facets` 9. `UI.FieldGroup#Prices` 10. `Common.Label` 11. `Common.Text` 12. `Common.ValueList`

CDS의 `@UI` 어노테이션은 이름의 첫 글자만 대문자로 바뀌어 같은 이름의 UI 어휘 Term이 되는 경우가 많다(lineItem → LineItem). 단, `@UI.selectionField`(단수)는 엔티티 타입 하나에 대한 `UI.SelectionFields`(복수, 속성 경로 목록)로 모인다. qualifier는 `#Qualifier`로 Term 뒤에 붙는다. Common 어휘(Label, Text, ValueList)는 UI 전용이 아닌 일반 의미 정보다. 이 변환은 서비스 바인딩이 메타데이터를 만들 때 자동으로 일어나고, `$metadata`를 열어 결과를 확인할 수 있다.

**(3)**
```cds
@Metadata.layer: #CORE
@UI: {
  headerInfo: {
    typeName: 'Travel',
    typeNamePlural: 'Travels',
    title:       { type: #STANDARD, value: 'TravelID' },
    description: { value: 'Description' }
  }
}
annotate entity ZC_Travel with
{
  @UI.facet: [
    { id: 'General', purpose: #STANDARD, type: #IDENTIFICATION_REFERENCE,
      label: 'General', position: 10 },
    { id: 'Prices',  purpose: #STANDARD, type: #FIELDGROUP_REFERENCE,
      targetQualifier: 'Prices', label: 'Prices', position: 20 }
  ]

  @UI.lineItem:       [{ position: 10 }]
  @UI.selectionField: [{ position: 10 }]
  @UI.identification: [{ position: 10 }]
  TravelID;

  @UI.lineItem:       [{ position: 20 }]
  @UI.identification: [{ position: 20 }]
  Description;

  @UI.lineItem:       [{ position: 30 }]
  @UI.selectionField: [{ position: 20 }]
  OverallStatus;

  @UI.fieldGroup: [{ qualifier: 'Prices', position: 10 }]
  TotalPrice;

  @UI.fieldGroup: [{ qualifier: 'Prices', position: 20 }]
  CurrencyCode;
}
```

채점 포인트: `@Metadata.layer`(필수), `annotate entity ... with`(구버전 `annotate view`도 허용), `@UI.facet`는 아무 요소 하나 위에 한 번만, `#FIELDGROUP_REFERENCE`의 `targetQualifier`와 `@UI.fieldGroup`의 `qualifier`가 정확히 같아야 함, 각 요소 끝의 세미콜론. 액션 버튼은 `@UI.lineItem: [{ type: #FOR_ACTION, dataAction: 'acceptTravel', label: 'Accept' }]`처럼 추가한다.

**(4)**
1. **CDS 프로젝션 뷰**(또는 그 메타데이터 확장)에 어노테이션을 쓴다. MDE를 쓰려면 대상 뷰에 `@Metadata.allowExtensions: true`.
2. **서비스 정의**가 프로젝션 뷰를 `expose`한다.
3. **서비스 바인딩**(OData V4 - UI)이 서비스를 게시한다. 이때 CDS 어노테이션이 OData 어노테이션(`UI.LineItem` 등)으로 변환되어 `$metadata`에 들어간다.
4. 브라우저의 **Fiori Elements 앱**(manifest의 dataSource가 이 서비스를 가리킴)이 시작될 때 `$metadata`와 어노테이션(+ 로컬 annotation.xml)을 읽는다.
5. Fiori Elements 템플릿이 런타임에 어노테이션을 해석해 XML 뷰를 만든다(템플릿 전처리). `UI.LineItem`의 DataField 순서대로 테이블 컬럼이 생긴다.
6. 데이터는 그 뒤 별도의 OData 요청(`GET Travel?$select=...&$top=...`)으로 채워진다.

레이어 우선순위(높은 것이 이김): `#CUSTOMER` > `#PARTNER` > `#INDUSTRY` > `#LOCALIZATION` > `#CORE`. 같은 레이어 안에서는 MDE가 원래 뷰에 직접 쓴 어노테이션보다 우선한다. 앱 쪽에서는 로컬 annotation.xml이 백엔드 어노테이션을 덮어쓴다. 화면을 코드가 아니라 "메타데이터로 생성"한다는 점이 핵심이라, 백엔드 어노테이션만 고쳐도(캐시를 비우면) 화면이 바뀐다. 서비스 바인딩의 Preview는 4~6단계를 앱 프로젝트 없이 바로 보여 준다.

**(5)**
1. 프로젝션 뷰에 `@Metadata.allowExtensions: true`가 없다 → 이 뷰에 대한 메타데이터 확장이 허용되지 않아 MDE가 활성화되지 않거나(오류) 반영되지 않는다. → 뷰 헤더에 추가한다.
2. `targetQualifier: 'prices'`와 `qualifier: 'Prices'`의 대소문자가 다르다. qualifier는 대소문자를 구분하므로 섹션이 참조하는 `UI.FieldGroup#prices`가 없어 섹션이 비거나 표시되지 않는다. → 둘을 `'Prices'`로 맞춘다.
3. `AgencyID`는 프로젝션 뷰에 없는 요소다 → MDE 활성화 오류. → 프로젝션 뷰에 `AgencyID`를 추가하거나 MDE에서 뺀다.

어노테이션 문제는 ① 허용 여부 ② 철자·대소문자·qualifier 연결 ③ 요소 존재 여부 ④ 브라우저/서버 캐시 순서로 점검한다. 바뀐 결과는 `$metadata`에서 직접 확인하는 것이 가장 빠르다.

</details>

---

### C-040. 값 도움말, side effects, virtual element, custom entity [코드] ★★★
<!-- src: RP-045, XE-013, RB-077, RB-076, RP-044 -->
Travel/Booking 앱에 입력 편의와 계산 필드를 추가하고, DB 뷰가 아닌 데이터 소스도 노출한다.

(1) Booking 프로젝션 뷰의 요소에 값 도움말을 붙인다. `ConnectionID` 값 도움말은 현재 행의 `CarrierID`로 걸러지기만 하고(값을 되돌려 쓰지 않음), 선택하면 `FlightDate`는 값 도움말 행의 값으로 채워지기만 해야 한다. 빈칸 1~5를 채우시오.

```cds
@Consumption.____(1)____: [{
  entity: { name: '/DMO/I_Agency', ____(2)____: 'AgencyID' }
}]
AgencyID,

@Consumption.valueHelpDefinition: [{
  entity: { name: '/DMO/I_Flight', element: 'ConnectionID' },
  ____(3)____: [
    { localElement: 'CarrierID',  element: 'AirlineID',  usage: #____(4)____ },
    { localElement: 'FlightDate', element: 'FlightDate', usage: #____(5)____ }
  ]
}]
ConnectionID,
```

(2) 요구가 바뀌었다. 항공사로 목록을 거르면서 선택하면 항공사도 함께 채우고, 목록에 없는 값을 입력하면 UI에서 오류를 내야 한다. 빈칸 6~10을 채우시오. 작은 고정 목록을 다이얼로그 대신 드롭다운으로 보이게 하려면 값 도움말 대상 뷰에 어떤 어노테이션을 주는지도 쓰시오.

```cds
@Consumption.valueHelpDefinition: [{
    entity: { name: '/DMO/I_Flight', element: ____(6)____ },
    ____(7)____: [
      { ____(8)____: 'CarrierID',  element: 'AirlineID',  usage: ____(9)____ },
      { localElement: 'FlightDate', element: 'FlightDate', usage: #RESULT } ],
    ____(10)____: true
}]
ConnectionID,
```

(3) 값 도움말 뷰는 서비스 정의에 노출해야 하는지, OData에서 어떤 어노테이션으로 나가는지 쓰시오.

(4) Booking의 항공료나 Travel의 예약 수수료가 바뀌면 Travel 총액을 다시 읽고, accept action 실행 후 상태 필드와 reject 버튼 활성 여부를 다시 읽도록 하려 한다. 빈칸 11~14를 채우시오.

```abap
define behavior for ZR_Travel alias Travel
...
{
  ...
  side effects
  {
    field BookingFee ____(11)____ field TotalPrice;
    action acceptTravel affects field OverallStatus, ____(12)____( action rejectTravel );
  }
}

define behavior for ZR_Booking alias Booking
...
{
  ...
  side effects
  {
    field FlightPrice affects field ____(13)____;
  }
}
```

```abap
projection;
strict ( 2 );
use draft;
____(14)____ side effects;
```

(5) side effects가 없으면 determination이 값을 바꿔도 어떤 문제가 생기는지 쓰시오. side effects의 원인과 대상으로 쓸 수 있는 것을 쓰시오.

(6) DB에 없는 필드(예: 출발까지 남은 일수)를 조회 시점에 ABAP로 계산해 보여 주는 virtual element를 정의하는 방법과 제약을 쓰시오.

(7) DB 뷰가 아니라 ABAP 코드로 데이터를 공급하는 custom entity와 쿼리 구현 클래스다. 빈칸 15~19를 채우시오.

```cds
@EndUserText.label: 'Connections (custom entity)'
@ObjectModel.query.____(15)____: 'ABAP:ZCL_CONNECTION_QUERY'
define custom entity ZCE_Connection
{
  key CarrierId    : /dmo/carrier_id;
  key ConnectionId : /dmo/connection_id;
      AirportFrom  : /dmo/airport_from_id;
      AirportTo    : /dmo/airport_to_id;
}
```

```abap
CLASS zcl_connection_query DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES ____(16)____.
ENDCLASS.

CLASS zcl_connection_query IMPLEMENTATION.
  METHOD ____(16)____~select.
    DATA connections TYPE STANDARD TABLE OF zce_connection WITH EMPTY KEY.

    DATA(top)  = io_request->get_paging( )->get_page_size( ).
    DATA(skip) = io_request->get_paging( )->get_offset( ).
    IF top = if_rap_query_paging=>page_size_unlimited.
      top = 0.
    ENDIF.

    IF io_request->____(17)____( ).
      SELECT FROM /dmo/connection
        FIELDS carrier_id      AS CarrierId,
               connection_id   AS ConnectionId,
               airport_from_id AS AirportFrom,
               airport_to_id   AS AirportTo
        ORDER BY carrier_id, connection_id
        INTO CORRESPONDING FIELDS OF TABLE @connections
        UP TO @top ROWS OFFSET @skip.
      io_response->____(18)____( connections ).
    ENDIF.

    IF io_request->is_total_numb_of_rec_requested( ).
      SELECT COUNT( * ) FROM /dmo/connection INTO @DATA(count).
      io_response->____(19)____( count ).
    ENDIF.
  ENDMETHOD.
ENDCLASS.
```

(8) custom entity는 언제 쓰는지, 프레임워크가 해 주지 않아 개발자가 직접 반영해야 하는 것은 무엇인지 쓰시오. (7)에서 `top = 0`으로 바꾸는 이유도 쓰시오.

<details><summary>정답·해설</summary>

**(1)** 1. `valueHelpDefinition` 2. `element` 3. `additionalBinding` 4. `FILTER` 5. `RESULT`

usage: `#FILTER`는 로컬 값을 값 도움말의 필터 조건으로만 쓰고, `#RESULT`는 선택한 행의 값을 로컬 필드에 돌려주며, `#FILTER_AND_RESULT`는 둘 다(기본)다. 코드 옆 텍스트 표시는 `@ObjectModel.text.element`로 따로 지정한다.

**(2)** 6. `'ConnectionID'` 7. `additionalBinding` 8. `localElement` 9. `#FILTER_AND_RESULT` 10. `useForValidation`

`useForValidation: true`는 값 도움말에 없는 값을 입력하면 UI에서 오류로 표시한다(최종 데이터 검증은 여전히 validation으로 해야 한다). 드롭다운: 값 도움말 대상 뷰에 `@ObjectModel.resultSet.sizeCategory: #XS`. 도메인 고정값 기반 뷰를 값 도움말로 쓰기도 한다.

**(3)** BO 엔티티의 `@Consumption.valueHelpDefinition`에서 참조한 값 도움말 뷰는 서비스 정의에 따로 쓰지 않아도 서비스에 자동으로 노출된다. 다만 서비스 정의에 명시적으로 함께 노출해 두는 경우도 흔하다. OData에서는 `Common.ValueList`(또는 `Common.ValueListReference`) 어노테이션으로 나가고, UI5/Fiori Elements가 이를 읽어 F4 다이얼로그를 자동으로 만든다.

**(4)** 11. `affects` 12. `permissions` 13. `_Travel.TotalPrice` 14. `use`

다른 엔티티의 필드는 association 경로로 지정한다. 프로젝션 BDEF에 `use side effects;`가 있어야 서비스 메타데이터에 반영된다.

**(5)** determination이 값을 바꾸더라도 Draft 편집 중 화면이 그 값을 다시 읽지 않아 최신 값이 안 보일 수 있다. side effects는 구현 코드 없이 "백엔드에서 계산한 값을 화면에 즉시 반영"하도록 UI에 다시 읽을 대상을 알려 주는 선언이다. 실제 계산은 determination이 하고, side effects는 새로고침만 담당한다. 원인: 필드 변경, action 실행, `$self`, 이벤트. 대상: `field`, `entity`, `permissions(...)`(기능 제어·권한), `messages`. 예: `side effects { field BookingFee affects field TotalPrice; action acceptTravel affects field OverallStatus, permissions( action rejectTravel ); }`.

**(6)** 프로젝션 뷰에 `@ObjectModel.virtualElementCalculatedBy: 'ABAP:ZCL_CALC'`와 `virtual DaysToStart : abap.int4`를 정의하고, 클래스는 `IF_SADL_EXIT_CALC_ELEMENT_READ`의 `get_calculation_info`(계산에 필요한 원본 필드 지정)와 `calculate`(값 계산)를 구현한다. 제약: OData를 통한 조회에서만 계산되고 ABAP SQL로 뷰를 읽으면 채워지지 않는다. 필터·정렬에 쓰기 어렵다.

**(7)** 15. `implementedBy` 16. `if_rap_query_provider` 17. `is_data_requested` 18. `set_data` 19. `set_total_number_of_records`

**(8)** custom entity는 `select from`이 없고 데이터 소스가 쿼리 구현 클래스다. 외부 API 결과, 계산 결과, SQL로 표현하기 어려운 데이터를 보여 줄 때 쓴다. 프레임워크가 페이징·필터·정렬·검색을 대신 해 주지 않으므로 `io_request`의 `get_paging( )`, `get_filter( )`(예: `get_as_sql_string( )`), `get_sort_elements( )` 등을 직접 반영해야 한다. 페이지 크기가 무제한이면 `get_page_size( )`가 `page_size_unlimited`(-1)를 돌려주는데, -1은 유효한 행 수가 아니므로 `UP TO 0 ROWS`(제한 없음)가 되도록 0으로 바꾼다. 기본은 읽기 전용이고, 트랜잭션 동작이 필요하면 unmanaged BDEF를 붙인다.

</details>

---

### C-041. RAP 메시지: 상태·전이 메시지와 UI 표시 경로 [코드] ★★★
<!-- src: RB-078, XE-014, XE-015 -->
validation 오류를 Fiori 화면의 해당 입력 필드에 빨간 테두리와 메시지 팝오버로 보여 주려 한다.

(1) RAP의 상태 메시지(state message)와 전이 메시지(transition message)의 차이를 쓰시오. 이전 상태 메시지를 지우는 방법도 쓰시오.

(2) `reported`의 `%msg`, `%element`, `%state_area`의 역할을 쓰고, `failed`와 `reported`의 차이를 쓰시오. 메시지 객체를 만드는 방법도 쓰시오.

(3) RAP validation에서 만든 오류 메시지가 화면의 입력 필드 빨간 테두리와 메시지 팝오버로 표시되기까지의 경로를 RAP → OData → UI5 순서로 설명하시오.

(4) 자유형 UI5 앱에서 서버 메시지와 입력 검증 메시지를 한 버튼의 팝오버로 보여 주는 코드다. `Messaging`은 `sap/ui/core/Messaging`(예전 `sap.ui.getCore().getMessageManager()`)이다. 빈칸 1~6을 채우시오.

```js
onInit: function () {
  var oView = this.getView();
  // 뷰의 타입 검증(parse/validation) 오류도 메시지로 수집
  Messaging.____(1)____(oView, true);
  // 모든 메시지를 담은 모델을 이름 "message"로 설정
  oView.setModel(Messaging.____(2)____(), "message");

  this._oPopover = new MessagePopover({
    items: {
      path: "____(3)____",
      template: new MessageItem({
        type: "{message>____(4)____}",
        title: "{message>message}",
        subtitle: "{message>additionalText}"
      })
    }
  });
  oView.____(5)____(this._oPopover);
},

onMessagesPress: function (oEvent) {
  this._oPopover.____(6)____(oEvent.getSource());
}
```

```xml
<Button icon="sap-icon://message-popup"
        text="{= ${message>/}.length }"
        press=".onMessagesPress"/>
```

(5) (4)에서 팝오버를 뷰의 dependent로 넣는 이유와, 새 요청 전에 이전 메시지를 지우는 방법을 쓰시오.

<details><summary>정답·해설</summary>

**(1)**
- 상태 메시지: 인스턴스 데이터의 상태(잘못된 값)를 나타낸다. 주로 validation에서 `%state_area`와 함께 보내고, 데이터가 고쳐질 때까지(Draft에서는 Draft와 함께) 남는다.
- 전이 메시지: 특정 요청(action, 수정 작업)의 결과로 한 번만 보여 주는 메시지다. 응답 후 사라진다.
- 다시 검사할 때 같은 state area의 이전 메시지를 지우려면 `%msg` 없이 `%tky`와 `%state_area`만 넣은 행을 `reported`에 추가한다.

**(2)**
- `%msg`: 메시지 객체. `new_message( id = ... number = ... severity = if_abap_behv_message=>severity-error v1 = ... )` 또는 `new_message_with_text( severity = ... text = ... )`. 메시지 클래스(ADT의 Message Class)를 만들어 쓰거나, `IF_ABAP_BEHV_MESSAGE`를 구현한 예외 클래스를 넣기도 한다.
- `%element-필드 = if_abap_behv=>mk-on`: 오류를 해당 필드에 연결한다(필드가 빨갛게 표시됨).
- `%state_area`: 상태 메시지 묶음 이름. validation별로 구분해 지우고 다시 넣는다.
- `failed`는 "이 인스턴스의 작업이 실패했다"는 사실(`%tky`, `%fail-cause`)이고 저장을 막는 효과가 있다. `reported`는 사용자에게 보여 줄 메시지다. validation 오류는 둘 다 채운다.

**(3)**
1. **RAP**: validation/determination/action 구현에서 `failed-travel`에 키를 넣어 실패를 표시하고, `reported-travel`에 `%msg`와 `%element-<필드> = if_abap_behv=>mk-on`을 넣는다. `%element`가 메시지를 특정 필드에 연결하는 정보다. Draft에서는 `%state_area`로 상태 메시지를 관리한다.
2. **OData**:
   - 요청이 실패하면 HTTP 4xx/5xx와 오류 응답 본문 `{ "error": { "code", "message", "target", "details": [ ... ] } }`. `target`(V2는 `target`/`propertyref`)이 필드 경로를 가리킨다.
   - 성공했지만 함께 보낼 메시지(경고·정보·성공)는 응답 헤더로 간다: V2 `sap-message`, V4 `sap-messages`. V4에서 엔티티에 묶인 상태 메시지는 `Core.Messages` 어노테이션이 붙은 속성(RAP에서는 `SAP__Messages`)으로 엔티티 데이터와 함께 온다.
3. **UI5**: OData 모델의 메시지 파서가 이를 `sap.ui.core.message.Message` 객체로 만들어 `Messaging`(예전 `MessageManager`)에 넣는다. 메시지의 target(엔티티 경로 + 속성)과 같은 경로에 바인딩된 컨트롤이 자동으로 `valueState="Error"`, `valueStateText`를 갖는다. message model(`Messaging.getMessageModel()`)을 `MessagePopover`/`MessageView`에 바인딩해 목록으로 보여 준다. Fiori Elements는 이 처리를 기본으로 해 주며, 오류는 다이얼로그/팝오버, 성공 메시지는 MessageToast로 보여 준다.

핵심은 "백엔드에서 필드를 지정하면 프런트는 경로만 맞으면 자동으로 빨간 테두리"라는 흐름이다. 직접 만든 UI5 앱에서는 뷰를 `Messaging.registerObject(oView, true)`로 등록해야 타입 검증(parse/validate) 오류도 같은 방식으로 표시된다.

**(4)** 1. `registerObject` 2. `getMessageModel` 3. `message>/` 4. `type` 5. `addDependent` 6. `toggle`(또는 `openBy`)

message model의 루트(`/`)는 Message 객체 배열이다. 각 메시지는 `type`(Error/Warning/Success/Information), `message`, `additionalText`, `description`, `target`을 가진다. 버튼 텍스트는 expression binding으로 메시지 건수를 표시했다.

**(5)** 팝오버를 뷰의 dependent로 넣어야 뷰의 "message" 모델을 물려받고 뷰와 함께 소멸된다. 새 요청 전에 이전 메시지를 지우려면 `Messaging.removeAllMessages()`를 호출한다.

</details>

---

## 계층을 가로지르는 개념

### C-042. 계층별 권한·잠금·BDEF 설정과 OData 동작 [개념] ★★★
<!-- src: XE-018, XE-019, XE-022, XE-023 -->
Draft 가능한 Travel 앱을 런치패드에서 연다. 보안과 동시성 제어가 런치패드 → OData → RAP BO → CDS의 어느 계층에서 이루어지는지 정리한다.

(1) 사용자가 런치패드에서 Travel 앱을 열어 목록을 보고 한 건을 수정하기까지, 권한이 검사되는 지점을 계층별(런치패드 → OData 서비스 → RAP BO → CDS)로 쓰고 각각 무엇을 막는지 설명하시오. 권한 문제를 점검하는 도구도 쓰시오.

(2) 권한 관련 설명으로 **틀린** 것을 **모두** 고르시오.

① 사용자의 역할에 앱의 business catalog가 없으면 런치패드에 타일이 보이지 않고, URL로 intent를 직접 입력해도 앱이 열리지 않는다.
② 타일은 보이고 앱도 열리는데 목록에 일부 회사(Agency) 데이터만 보인다면 CDS 접근 제어(DCL)가 원인일 가능성이 크다.
③ BDEF의 instance authorization은 update, delete, action 요청이 실행될 때 검사되며, 권한이 없으면 해당 요청이 거부된다.
④ CDS 뷰에 DCL을 만들어도, 그 뷰를 ABAP SQL `SELECT`로 읽을 때는 접근 제어가 기본으로 적용되지 않는다.
⑤ Fiori Elements에서 `@UI.hidden`으로 Delete 버튼을 숨기면 OData로 DELETE 요청을 직접 보내도 백엔드에서 자동으로 거부되므로 별도 권한 구현이 필요 없다.

(3) 다음 세 가지 잠금·동시성 제어 방식을 비교하고, 비관적(pessimistic) 잠금과 낙관적(optimistic) 잠금 중 어디에 속하는지 쓰시오.
- (가) 클래식 ABAP의 SAP LUW와 ENQUEUE(잠금 객체)
- (나) RAP의 lock(`lock master`)과 Draft의 배타 잠금
- (다) OData의 ETag(`If-Match`)

(4) 이 앱의 BDEF 헤더 부분이다. 빈칸 1~4를 채우시오.

```abap
managed implementation in class zbp_i_travel unique;
strict ( 2 );
with ____(1)____;

define behavior for ZI_Travel alias Travel
persistent table ztravel
draft table ztravel_d
____(2)____ master
total etag LastChangedAt
____(3)____ master ( instance )
____(4)____ master LocalLastChangedAt
{
  create;
  update;
  delete;
  draft action Edit;
  draft action Activate optimized;
  draft action Discard;
  draft action Resume;
  draft determine action Prepare;
}
```

(5) 빈칸 4의 설정은 OData 응답에서 무엇으로 나타나고 UI5 모델은 이를 어떻게 쓰는지 쓰시오. 빈칸 2가 없으면 동시에 편집할 때 어떤 보호가 빠지는지도 쓰시오.

(6) BDEF 한 줄이 여러 계층에 영향을 준다. `with draft`, `etag master`, `authorization master`, `lock master`가 각각 OData·Fiori 화면에 어떻게 나타나는지 쓰시오.

<details><summary>정답·해설</summary>

**(1)**
1. **런치패드(역할)**: 사용자 역할(PFCG 역할, ABAP Cloud에서는 business role)에 앱의 business catalog가 없으면 타일이 안 보이고 intent도 실행되지 않는다. space/page는 표시 배치만 결정한다.
2. **OData 서비스 시작 권한**: 온프레미스는 권한 객체 `S_SERVICE`(서비스 시작 허가, PFCG 역할에 서비스 추가), ABAP Cloud는 IAM 앱/business catalog로 서비스 접근을 허용한다. 없으면 서비스 호출이 403.
3. **RAP BO 권한(BDEF)**: `authorization master ( global, instance )` 등. `get_global_authorizations`(생성 같은 작업 자체를 할 수 있는가), `get_instance_authorizations`(이 인스턴스를 update/delete/action 할 수 있는가). 권한 객체(`AUTHORITY-CHECK OBJECT ...`)로 판단하며, 거부되면 failed/reported로 요청이 실패한다.
4. **CDS 접근 제어(DCL)**: `define role ... grant select on ZI_Travel where (AgencyID) = aspect pfcg_auth(...)`. READ 때 자동으로 WHERE 조건이 붙어 **볼 수 있는 행**을 제한한다. 권한이 없으면 오류가 아니라 결과에서 빠진다.

UI에서 버튼을 숨기는 것(`@UI.hidden`, feature control)은 사용성 기능이지 보안이 아니다. OData URL을 직접 호출하면 우회되므로 반드시 백엔드(BDEF 권한, DCL)에서 검사해야 한다. 점검 도구: SU53(마지막 권한 실패), STAUTHTRACE/ST01(권한 추적).

**(2)** ④, ⑤
- ① 맞다. catalog는 실행 권한을 뜻한다.
- ② 맞다. DCL은 오류를 내지 않고 권한 없는 행을 결과에서 걸러 낸다.
- ③ 맞다.
- ④ 틀리다. ABAP SQL로 CDS 엔티티를 읽을 때도 DCL이 **기본으로 적용된다**. 접근 제어를 건너뛰려면 `WITH PRIVILEGED ACCESS`를 명시해야 한다(RAP 내부 로직 등 제한된 경우).
- ⑤ 틀리다. UI 숨김은 백엔드 검사를 대신하지 않는다. DELETE 차단은 BDEF(`delete` 미선언, instance authorization, feature control)에서 해야 한다.

**(3)**
- (가) **SAP LUW + ENQUEUE**(비관적): SE11 잠금 객체가 생성한 `ENQUEUE_<객체>`/`DEQUEUE_<객체>` 함수로 enqueue 서버의 잠금 테이블(SM12)에 논리 잠금을 건다. 변경은 `CALL FUNCTION ... IN UPDATE TASK` 등으로 모았다가 `COMMIT WORK`에서 한 번에 DB에 반영한다(SAP LUW). 잠금은 커밋 후 업데이트 처리 끝에 해제된다(`_SCOPE`에 따라). 상태가 있는(stateful) SAP GUI 대화에 맞는 방식이다.
- (나) **RAP lock**: BDEF의 `lock master`(하위 엔티티는 `lock dependent by _parent`). 변경 요청이 오면 프레임워크가 lock 메서드를 호출해 ENQUEUE 기반 잠금을 건다(managed는 자동, unmanaged는 `lock` 메서드 구현). non-draft에서는 요청 하나 동안만 짧게 잠근다(비관적이지만 짧음). Draft에서는 Edit 때 활성 인스턴스에 **배타 잠금**을 걸고 Draft가 있는 동안 유지한다 → 사실상 편집 세션 동안의 비관적 잠금. RAP의 save sequence(`finalize`, `check_before_save`, `save`)가 SAP LUW 개념을 대신한다.
- (다) **OData ETag**(낙관적): 잠금을 걸지 않는다. 읽을 때 받은 버전(ETag)을 변경 요청의 `If-Match`로 보내고, 서버가 현재 버전과 비교해 다르면 412로 거부한다. stateless HTTP에 맞다. RAP에서는 `etag master <필드>`(보통 LocalLastChangedAt)로 정의하고, Draft의 `total etag`는 Draft가 만들어진 뒤 활성 데이터가 바뀌었는지 확인하는 데 쓴다.
- 핵심: 비관적 잠금은 "먼저 잠그고 바꾼다"(충돌 예방, 대기·거부 발생), 낙관적 잠금은 "바꿀 때 버전을 비교한다"(충돌 감지, 동시 읽기 자유). 웹/OData는 stateless라 요청 사이에 잠금을 유지하기 어려워 ETag가 기본이고, 긴 편집이 필요할 때 Draft가 서버 측 상태와 배타 잠금을 제공한다.

**(4)** 1. `draft` 2. `lock` 3. `authorization` 4. `etag`

**(5)** `etag master`는 엔티티 응답의 ETag(V4 JSON의 `@odata.etag`, 단건 GET의 `ETag` 헤더)로 나간다. UI5 모델이 이를 저장해 두었다가 수정·삭제·action 요청에 `If-Match` 헤더로 붙이고, 값이 다르면 412가 난다. `lock master`가 없으면 변경 시 enqueue 잠금이 걸리지 않아, Draft Edit 때의 배타 잠금(다른 사용자의 동시 편집 차단)이 없어진다. 실제로는 managed BO의 루트 엔티티에 `lock master`가 필수라서 생략하면 BDEF 문법 검사에서 오류가 난다.

**(6)** `with draft` → OData 키에 IsActiveEntity, Edit/Activate/Discard action, Fiori Elements의 Edit/Save/Discard 버튼. `etag master` → ETag/If-Match. `authorization master` → 요청 거부와 버튼 활성 여부. `lock master` → 서버 잠금.

</details>

---

### C-043. 기술 비교, 앱 개발 순서, 장애 점검, 성능 [작성] ★★★
<!-- src: XE-020, XE-021, XE-024, XE-025, RB-085 -->
S/4HANA(ABAP Cloud 개발 모델)에서 "출장 신청을 목록으로 보고, 관리자가 승인(Approve) 버튼으로 상태를 바꾸는" Fiori 앱을 만들고 운영한다.

(1) OData 서비스를 만드는 세 방식(SAP Gateway Service Builder(SEGW), RAP, CAP)을 언어/런타임, 모델 정의, 구현 방법, 지원 OData 버전, 권장 사용처 관점으로 비교하시오. 면접에서 "왜 RAP인가"에 답할 근거도 쓰시오.

(2) 다음 설명 중 **틀린** 것을 고르시오.

① SEGW 서비스는 생성된 DPC_EXT 클래스에서 `GET_ENTITYSET` 같은 메서드를 재정의해 데이터를 직접 읽어 반환한다.
② RAP managed 시나리오에서는 표준 생성·수정·삭제를 위한 SQL을 개발자가 직접 쓰지 않아도 된다.
③ CAP은 CDS 언어로 데이터 모델과 서비스를 정의하고 Node.js 또는 Java 런타임에서 실행된다.
④ SAP BTP ABAP Environment(ABAP Cloud)에서 새 OData 서비스를 만들 때 권장 방식은 SEGW이다.
⑤ RAP 서비스는 하나의 service definition에 대해 OData V2용과 V4용 service binding을 각각 만들 수 있다.

(3) 이 앱을 RAP + Fiori Elements로 만들 때 만들어야 할 객체를 **생성 순서대로** 번호를 붙여 쓰고, 각 객체의 역할을 한 줄로 쓰시오(객체 이름은 예시로 지어도 된다). 승인 버튼이 화면에 나오게 하는 BDEF와 UI 어노테이션 코드 조각도 쓰시오.

(4) 사용자가 "목록이 비어 있다" 또는 "저장 시 오류가 난다"고 신고했다. 원인을 찾기 위해 브라우저 → 런치패드 → OData/Gateway → ABAP 순서로 확인할 도구와 확인 내용을 쓰시오. HTTP 상태 코드로 계층을 좁히는 방법도 쓰시오.

(5) 앱이 느리다. 점검할 성능 포인트를 행동 구현, CDS 모델, UI·서비스 측면에서 각각 2가지 이상 쓰시오.

<details><summary>정답·해설</summary>

**(1)**

| 관점 | SEGW (Gateway) | RAP | CAP |
|---|---|---|---|
| 언어/런타임 | ABAP (온프레미스 NetWeaver/S/4HANA) | ABAP (S/4HANA 온프레미스·Private·Public Cloud, BTP ABAP Environment) | Node.js 또는 Java (주로 SAP BTP, HANA Cloud) |
| 모델 정의 | SEGW 프로젝트에서 엔티티 타입/셋을 정의하거나 DDIC/RFC/CDS(`@OData.publish`, 참조 데이터 소스)에서 가져옴 | CDS 뷰 엔티티(데이터 모델) + BDEF(동작) + service definition/binding | CDS(CDL) 파일(`db/schema.cds`, `srv/service.cds`) |
| 구현 | 생성된 MPC/DPC 클래스의 `*_EXT`를 재정의(`GET_ENTITYSET`, `CREATE_ENTITY` 등). 거의 모든 것을 손으로 작성 | managed(프레임워크가 CRUD·잠금·Draft 처리) 또는 unmanaged(기존 로직 래핑). behavior pool에는 determination/validation/action만 구현 | 일반 CRUD는 자동, 이벤트 핸들러(`srv.before/on/after`)로 로직 추가 |
| OData 버전 | 주로 V2 (V4도 가능하지만 제한적) | V2, V4 (UI/Web API 바인딩) | V4 기본 (V2는 어댑터) |
| 권장 사용처 | 기존 시스템 유지보수 | S/4HANA와 ABAP Cloud의 신규 개발 표준(clean core) | BTP 위의 사이드바이사이드 확장, 신규 클라우드 앱 |

"왜 RAP인가": 표준화된 트랜잭션 모델(Draft, 잠금, ETag, 권한이 선언적), Fiori Elements와의 자연스러운 연결, ABAP Cloud(릴리스된 API만 사용) 호환. SEGW는 ABAP Cloud(BTP ABAP Environment, Public Cloud 개발자 확장)에서 쓸 수 없다.

**(2)** ④. ABAP Cloud에서는 SEGW를 쓸 수 없고 RAP가 표준이다. ⑤는 맞다. 바인딩 유형(OData V2 - UI, OData V4 - UI, OData V4 - Web API 등)만 다르게 해서 같은 service definition을 여러 바인딩으로 게시할 수 있다.

**(3)**
1. **패키지** `ZTRAVEL_APP`: 모든 객체를 담고 transport에 연결.
2. **DB 테이블** `ZTRAVEL_A`(+ 필요 시 Draft 테이블 `ZTRAVEL_D`): 출장 데이터 저장. 관리 필드(created_by, last_changed_at, local_last_changed_at) 포함.
3. **CDS 인터페이스(기본) 뷰** `ZI_TRAVEL`(root view entity): 데이터 모델, 연관.
4. **BDEF** `ZI_TRAVEL`(managed, with draft, lock/etag/authorization master, action `approve`)과 **behavior pool 클래스** `ZBP_I_TRAVEL`(action, validation, determination, 권한 구현).
5. **CDS 접근 제어(DCL)** `ZI_TRAVEL`: 읽기 권한 행 제한.
6. **CDS 프로젝션 뷰** `ZC_TRAVEL`(`provider contract transactional_query`, `@Metadata.allowExtensions: true`)과 **프로젝션 BDEF**(`use action approve;` 등).
7. **메타데이터 확장** `ZC_TRAVEL`: lineItem, selectionField, headerInfo, facet, 승인 버튼.
8. **Service definition** `ZUI_TRAVEL`: `expose ZC_TRAVEL as Travel;`
9. **Service binding** `ZUI_TRAVEL_O4`(OData V4 - UI) → 게시(Publish), Preview로 확인.
10. **Fiori Elements 앱 생성**(BAS/VS Code의 SAP Fiori tools, List Report Page 템플릿) → 필요 시 manifest/로컬 어노테이션 조정.
11. **배포**: ABAP 저장소(BSP 앱)로 deploy.
12. **런치패드 설정**: 앱 descriptor(IAM 앱) → business catalog에 추가 → business role(또는 PFCG 역할)에 catalog/space/page 할당 → 사용자에게 역할 할당.

```abap
" BDEF (ZI_TRAVEL)
action ( features : instance ) approve result [1] $self;
" projection BDEF (ZC_TRAVEL)
use action approve;
```

```cds
// MDE (ZC_TRAVEL)
@UI.lineItem: [ { position: 10 },
                { type: #FOR_ACTION, dataAction: 'approve', label: 'Approve' } ]
@UI.identification: [ { position: 10 },
                      { type: #FOR_ACTION, dataAction: 'approve', label: 'Approve' } ]
TravelID;
```

채점 포인트는 순서(데이터 → 모델 → 동작 → 투영 → UI 어노테이션 → 서비스 → 바인딩 → 앱 → 배포 → 런치패드)와 각 객체의 역할이다. `features : instance`로 이미 승인된 건은 버튼을 비활성화(`get_instance_features`)할 수 있다. action 구현에서는 `MODIFY ENTITIES ... IN LOCAL MODE`로 상태를 바꾸고 `result`에 바뀐 인스턴스를 돌려줘야 화면이 갱신된다.

**(4)**
1. **브라우저**: 개발자 도구 Network 탭에서 OData 요청(`$batch` 안의 개별 응답)의 상태 코드(401/403/404/412/428/500)와 오류 본문(`error.message`, `details`) 확인. Console의 UI5 오류. UI5 진단 도구(Ctrl+Alt+Shift+S, Support Assistant)로 바인딩·모델 확인.
2. **런치패드**: 타일/intent 문제면 역할에 catalog와 target mapping이 있는지, 앱의 dataSource URI가 맞는지.
3. **OData/Gateway**: 서비스 URL과 `$metadata`를 직접 호출해 서비스가 게시되었는지(service binding Publish, 온프레미스 `/IWFND/MAINT_SERVICE`), `/IWFND/ERROR_LOG`(Gateway 오류 로그), `/IWFND/GW_CLIENT`(요청 재현), `/IWFND/TRACES`.
4. **ABAP**: `ST22`(덤프), `SU53`/권한 추적(`STAUTHTRACE`) — 403이나 빈 목록이면 DCL·권한 확인, ADT 디버거(behavior pool 브레이크포인트), CDS 뷰를 ADT Data Preview로 직접 조회해 데이터가 있는지와 DCL 영향 확인.

- 목록이 빔: 데이터 없음 / DCL로 걸러짐 / 필터 기본값 / `$filter` 오류.
- 저장 오류: validation 메시지(정상 동작), 권한(BDEF), 412/428(ETag), 잠금(다른 사용자 편집 중), 덤프.
- 핵심은 "어느 계층에서 처음 실패했는가"로 좁히는 것이다. HTTP 응답 코드가 그 계층을 가장 빨리 알려 준다: 403 권한/CSRF, 404 서비스·엔티티 없음, 412/428 ETag, 400 요청·검증 오류, 500 백엔드 덤프.

**(5)**
- 행동 구현
  1. 핸들러는 대량 처리(mass-enabled)로 작성한다. `keys` 전체를 한 번의 `READ ENTITIES ... WITH CORRESPONDING #( keys )`로 읽고, 키마다 SELECT·READ를 반복하지 않는다.
  2. 필요한 필드만 읽고(`FIELDS ( ... )`), 이미 읽은 데이터를 재사용한다.
  3. determination·validation의 트리거를 꼭 필요한 필드로 한정(`field ...`)하고, 무거운 로직은 `on modify` 대신 `on save`나 determine action으로 옮긴다.
  4. 내부 처리는 `IN LOCAL MODE`로 불필요한 권한·기능 제어 호출을 피한다.
  5. 무거운 후속 작업은 bgPF·이벤트로 비동기화한다.
  6. `get_instance_features`, `get_instance_authorizations`도 목록을 표시할 때마다 호출되므로 가볍게 만든다.
- CDS 모델
  1. 목록 화면에 쓰지 않는 to-many association·복잡한 계산을 투영 뷰에서 빼고, 필요한 곳에서만 경로를 쓴다.
  2. virtual element 남용 금지(행마다 ABAP 계산). 가능하면 CDS 식으로 계산한다.
  3. 값 도움말·텍스트 뷰를 가볍게 하고, DCL 조건이 인덱스 없는 필드 조인으로 무거워지지 않게 한다.
- UI·서비스
  1. 페이징(`$top`/`$skip`), 필요한 컬럼만(`$select`), 기본 필터(`@UI.selectionField`, 필수 필터)로 대량 조회를 막는다.
  2. side effects 대상을 최소화한다(`field *`, `entity` 전체 새로고침 남용 금지).
  3. ST05·SAT·ADT 프로파일러와 브라우저 네트워크 도구로 실제 요청과 SQL을 측정한다.
- "RAP는 느리다"보다 "핸들러를 단건 처리로 짜서 느리다"가 대부분이다. 핸들러 파라미터가 테이블(한 번에 여러 인스턴스)이라는 점을 강조한다.

</details>

---

## 테스트

### C-044. CDS·ABAP SQL 테스트 더블 [코드] ★★
<!-- src: RB-095, RB-096, RB-097, RB-099, RB-100 -->
C-009의 통계 뷰 `ZI_FlightStat`는 테이블 `zflight`를 carrid별로 집계해 `cnt`(행 수), `conn_cnt`(서로 다른 connid 수), `type_cnt`(서로 다른 planetype 수), `occ_sum`, `occ_max`, `occ_min`(seatsocc의 합·최대·최소)을 돌려준다. 이 뷰와 이를 쓰는 ABAP 코드를 실제 DB 데이터와 상관없이 테스트한다.

(1) CDS 테스트 클래스의 빈칸 1~5를 채우시오.

```abap
CLASS ltc_flight_stat DEFINITION FINAL FOR TESTING
  DURATION SHORT RISK LEVEL HARMLESS.
  PRIVATE SECTION.
    CLASS-DATA go_env TYPE REF TO ____(1)____.
    CLASS-METHODS class_setup.
    CLASS-METHODS class_teardown.
    METHODS setup.
    METHODS count_per_carrier FOR TESTING.
ENDCLASS.

CLASS ltc_flight_stat IMPLEMENTATION.
  METHOD class_setup.
    go_env = cl_cds_test_environment=>create( ____(2)____ = 'ZI_FLIGHTSTAT' ).
  ENDMETHOD.

  METHOD setup.
    go_env->____(3)____( ).
  ENDMETHOD.

  METHOD class_teardown.
    go_env->____(4)____( ).
  ENDMETHOD.

  METHOD count_per_carrier.
    DATA lt_flight TYPE STANDARD TABLE OF zflight WITH EMPTY KEY.
    lt_flight = VALUE #( ( carrid = 'LH' connid = '0400' planetype = 'A340' seatsocc = 300 )
                         ( carrid = 'LH' connid = '0402' planetype = 'A380' seatsocc = 400 ) ).
    go_env->____(5)____( i_data = lt_flight ).

    SELECT SINGLE cnt FROM zi_flightstat WHERE carrid = 'LH' INTO @DATA(lv_cnt).
    cl_abap_unit_assert=>assert_equals( act = lv_cnt exp = 2 ).
  ENDMETHOD.
ENDCLASS.
```

(2) 같은 방식으로 다른 테스트 메서드에서 다음 데이터를 넣고 SELECT했다. 각 단언(assert)의 통과 여부를 쓰시오(실제 DB의 `zflight`에는 LH 행이 100건 있다고 가정). 실제로 실행되는 단언은 어디까지인지도 쓰시오.

```abap
lt_flight = VALUE #(
  ( carrid = 'LH' connid = '0400' planetype = 'A340' seatsocc = 300 )
  ( carrid = 'LH' connid = '0400' planetype = 'A340' seatsocc = 100 )
  ( carrid = 'LH' connid = '0402' planetype = 'A340' seatsocc = 200 )
  ( carrid = 'AA' connid = '0017' planetype = 'B747' seatsocc = 150 ) ).
go_env->insert_test_data( i_data = lt_flight ).

SELECT SINGLE * FROM zi_flightstat WHERE carrid = 'LH' INTO @DATA(ls_lh).

cl_abap_unit_assert=>assert_equals( act = ls_lh-cnt      exp = 3 ).    " (가)
cl_abap_unit_assert=>assert_equals( act = ls_lh-conn_cnt exp = 2 ).    " (나)
cl_abap_unit_assert=>assert_equals( act = ls_lh-type_cnt exp = 2 ).    " (다)
cl_abap_unit_assert=>assert_equals( act = ls_lh-occ_sum  exp = 600 ).  " (라)
cl_abap_unit_assert=>assert_equals( act = ls_lh-occ_min  exp = 100 ).  " (마)
```

(3) 클래스 안의 ABAP SQL(`SELECT ... FROM sflight`)을 실제 DB 없이 테스트하는 코드의 빈칸 6~8을 채우시오. CDS 테스트 더블과 ABAP SQL 테스트 더블은 각각 언제 쓰는지도 쓰시오.

```abap
CLASS-DATA go_sql_env TYPE REF TO if_osql_test_environment.

METHOD class_setup.
  go_sql_env = ____(6)____=>create(
                 ____(7)____ = VALUE #( ( 'SFLIGHT' ) ) ).
ENDMETHOD.

METHOD setup.
  go_sql_env->clear_doubles( ).
ENDMETHOD.

METHOD test_occupancy.
  DATA lt_sflight TYPE STANDARD TABLE OF sflight WITH EMPTY KEY.
  lt_sflight = VALUE #( ( carrid = 'LH' connid = '0400' fldate = '20260801'
                          seatsmax = 200 seatsocc = 150 ) ).
  go_sql_env->____(8)____( lt_sflight ).
  " 테스트 대상 메서드 호출 후 assert
ENDMETHOD.

METHOD class_teardown.
  go_sql_env->destroy( ).
ENDMETHOD.
```

(4) 다음 CDS 테스트 클래스에서 잘못된 점 3가지를 찾아 고치시오.

```abap
CLASS ltc_stat DEFINITION FINAL
  DURATION SHORT RISK LEVEL HARMLESS.
  PRIVATE SECTION.
    DATA mo_env TYPE REF TO if_cds_test_environment.
    METHODS setup.
    METHODS test_lh FOR TESTING.
    METHODS test_aa FOR TESTING.
ENDCLASS.

CLASS ltc_stat IMPLEMENTATION.
  METHOD setup.
    mo_env = cl_cds_test_environment=>create( i_for_entity = 'ZI_FLIGHTSTAT' ).
  ENDMETHOD.
  METHOD test_lh.
    mo_env->insert_test_data( i_data = gt_lh_data ).
    ...
  ENDMETHOD.
  METHOD test_aa.
    mo_env->insert_test_data( i_data = gt_aa_data ).
    ...
  ENDMETHOD.
ENDCLASS.
```

(5) 다음 중 상황과 테스트 도구가 잘못 짝지어진 것을 고르고, 바른 도구를 쓰시오.

① CDS 뷰의 CASE·집계 로직 검증 — `CL_CDS_TEST_ENVIRONMENT`
② 메서드 안 ABAP SQL이 읽는 테이블 대체 — `CL_OSQL_TEST_ENVIRONMENT`
③ 다른 RAP BO의 트랜잭셔널 버퍼 대체 — `CL_BOTD_TXBUFDBL_BO_TEST_ENV`
④ 로컬 RAP 핸들러 클래스 인스턴스 생성 — `CREATE OBJECT ... FOR TESTING`
⑤ 인터페이스로 주입한 의존 객체 대체 — `CL_OSQL_TEST_ENVIRONMENT`

<details><summary>정답·해설</summary>

**(1)** 1. `if_cds_test_environment` 2. `i_for_entity` 3. `clear_doubles` 4. `destroy` 5. `insert_test_data`

`create( i_for_entity = ... )`는 테스트 대상 CDS가 읽는 데이터 소스(여기서는 `zflight`)를 테스트 더블로 바꾼다. 테스트 중 그 CDS를 SELECT하면 실제 테이블 대신 더블의 데이터가 읽힌다. 환경 생성은 비싸므로 `class_setup`에서 한 번, 데이터 초기화는 `setup`에서 매번, 정리는 `class_teardown`에서 한다.

**(2)** (가) 통과 (나) 통과 (다) 실패 (라) 통과 (마) 통과

테스트 더블에는 넣은 4건만 있고 실제 DB의 100건은 보이지 않는다. LH 행은 3건(cnt = 3), connid는 0400, 0402 두 가지(conn_cnt = 2), planetype은 모두 A340이라 type_cnt = 1이므로 (다)가 실패한다. 합계 300 + 100 + 200 = 600, 최소 100. `assert_equals`는 첫 실패에서 테스트 메서드를 중단하므로 실제로는 (다)에서 멈추고 (라)(마)는 실행되지 않는다(문제는 값 자체가 맞는지를 물었다).

**(3)** 6. `cl_osql_test_environment` 7. `i_dependency_list` 8. `insert_test_data`

ABAP SQL 테스트 더블은 테스트 대상 코드가 읽는 DB 테이블·CDS 뷰를 목록으로 받아 더블로 바꾼다. CDS 테스트 더블(`cl_cds_test_environment`)은 "CDS 뷰 자체의 로직"을, ABAP SQL 테스트 더블은 "ABAP 코드의 SQL에 의존하는 로직"을 테스트할 때 쓴다.

**(4)**
1. 클래스 정의에 `FOR TESTING`이 없다 → `CLASS ltc_stat DEFINITION FINAL FOR TESTING DURATION SHORT RISK LEVEL HARMLESS.` 없으면 테스트 클래스로 인식되지 않고 `FOR TESTING` 메서드 선언도 오류가 난다.
2. 테스트 환경을 `setup`에서 테스트마다 만든다(느리고 정리도 안 됨) → `CLASS-DATA`로 바꾸고 `class_setup`에서 한 번 `create`, `class_teardown`에서 `destroy( )`.
3. 테스트 사이에 더블 데이터를 지우지 않는다 → `setup`에서 `clear_doubles( )`를 호출해 앞 테스트의 데이터가 다음 테스트에 섞이지 않게 한다.

테스트 메서드는 실행 순서가 정해져 있지 않으므로 각 테스트는 독립적이어야 하고, 그래서 공유 데이터 초기화(`setup`)가 중요하다.

**(5)** ⑤. 인터페이스로 주입한 의존 객체는 테스트용 구현 클래스(test double)를 직접 만들거나 ABAP OO 테스트 더블 프레임워크(`CL_ABAP_TESTDOUBLE=>create( 'ZIF_...' )`)로 대체한다. `CL_OSQL_TEST_ENVIRONMENT`는 DB 접근 대체용이다. 함수 모듈 호출은 함수 모듈 테스트 더블(`CL_FUNCTION_TEST_ENVIRONMENT`)로 대체할 수 있다.

</details>

---

### C-045. RAP BO 테스트와 의존성 격리 [개념] ★★★
<!-- src: RP-048, RB-098 -->
Travel BO(`ZR_TravelTP`)와 이 BO를 EML로 읽는 다른 클래스를 테스트한다.

(1) RAP BO를 테스트하는 방법을 (가) 핸들러 메서드 단위 테스트 (나) EML을 통한 BO 테스트 (다) OData 서비스 수준 테스트로 나누어 설명하시오.

(2) DB·CDS 의존성과 다른 RAP BO 의존성을 각각 어떻게 격리하는지 쓰시오.

(3) 다음 세 상황에서 각각 어떤 테스트 기법을 쓰는지 쓰시오.
- (가) 행동 구현의 validation 메서드 하나만 단독으로 테스트하고 싶다.
- (나) 다른 RAP BO를 EML로 읽는 내 클래스를 그 BO의 실제 데이터·로직 없이 테스트하고 싶다.
- (다) 다른 BO에 대한 MODIFY EML 호출의 응답(failed 등)을 원하는 대로 흉내 내고 싶다.

(4) 테스트 클래스 선언과 `class_setup`/`setup`/`class_teardown`에서 할 일을 쓰시오. 실제 BO에 EML을 보내고 `ROLLBACK ENTITIES`로 되돌리는 통합 테스트의 한계도 쓰시오.

<details><summary>정답·해설</summary>

**(1)**
- (가) 핸들러 메서드 단위: 로컬 핸들러 클래스는 행동 풀 내부에 있으므로 테스트 클래스를 `LOCAL FRIENDS`로 선언하거나 테스트 include에 두고, 핸들러 인스턴스를 만들어 메서드(예: `validateDates`)에 `keys`를 넣어 직접 호출한 뒤 `failed`/`reported`를 검증한다. 메서드 안의 EML은 테스트 더블로 대체한다.
- (나) BO 테스트: 테스트 클래스에서 `MODIFY ENTITIES`/`READ ENTITIES`/`COMMIT ENTITIES`로 실제 흐름(생성 → action → 저장)을 실행하고 `mapped`/`failed`/`reported`와 결과 값을 `cl_abap_unit_assert`로 검증한다. `teardown`에서 `ROLLBACK ENTITIES`. 클래스 주석 `"! @testing BDEF:ZR_TravelTP`로 테스트 대상 BO를 연결한다.
- (다) 서비스 테스트: Local Client Proxy(`cl_web_odata_client_factory=>create_v4_local_proxy`)로 OData 요청을 시스템 안에서 보내 프로젝션·서비스 바인딩까지 검증한다.

**(2)** DB 테이블·CDS는 `cl_osql_test_environment`, `cl_cds_test_environment`로 테스트 더블을 만들고 테스트 데이터를 넣는다. 다른 RAP BO(EML 의존성)는 `cl_botd_txbufdbl_bo_test_env`(트랜잭셔널 버퍼 더블)나 `cl_botd_mockemlapi_bo_test_env`(EML API 목)로 대체한다.

**(3)**
- (가) 행동 풀의 테스트 include에서 `CREATE OBJECT lo_handler FOR TESTING.`으로 로컬 핸들러 클래스 인스턴스를 만들고 validation 메서드를 직접 호출한다(핸들러 클래스는 보통 직접 인스턴스화할 수 없어 `FOR TESTING` 변형을 쓴다). 메서드가 EML로 읽는 데이터는 트랜잭셔널 버퍼 더블이나 CDS 테스트 더블로 준비한다.
- (나) 트랜잭셔널 버퍼 테스트 더블: `cl_botd_txbufdbl_bo_test_env=>create( environment_config = cl_botd_txbufdbl_bo_test_env=>prepare_environment_config( )->set_bdef_dependencies( VALUE #( ( 'ZR_TRAVEL' ) ) ) )`, `get_test_double( 'ZR_TRAVEL' )->insert_test_data( ... )`. EML이 실제 BO 대신 이 버퍼를 읽고 쓴다.
- (다) EML API 목(mock): `cl_botd_mockemlapi_bo_test_env`로 특정 EML 호출에 대한 출력(결과, failed, reported)을 미리 설정한다.

**(4)** 테스트 클래스는 `FOR TESTING RISK LEVEL HARMLESS DURATION SHORT`로 선언한다. `class_setup`에서 테스트 환경 생성, `setup`에서 `clear_doubles`와 데이터 삽입, `class_teardown`에서 `destroy`. 테스트 더블을 쓰면 실제 DB에 영향이 없고 결과가 반복 가능하다. 실제 BO에 EML을 보내고 `ROLLBACK ENTITIES`로 되돌리는 통합 테스트도 가능하지만, 데이터와 다른 BO 로직에 의존해 불안정하다. 단위 테스트는 의존성을 더블로 바꾸는 것이 원칙이다.

</details>

---

## 손코딩

### C-046. 손코딩: 파라미터 CDS 뷰 엔티티와 AMDP [작성] ★★★
<!-- src: HC-038, HC-039 -->
항공편(SFLIGHT)과 예약(SBOOK) 데이터를 기간별·노선별로 분석한다. 앞의 두 문항은 CDS, 뒤의 두 문항은 AMDP로 푼다.

(1) 다음 CDS 뷰 엔티티 `ZHC_I_FlightPeriod`를 작성하시오.
- 데이터 원본 SFLIGHT, 파라미터 `p_from_date`, `p_to_date`(abap.dats). `p_from_date`는 지정하지 않으면 시스템 날짜가 들어가도록 한다.
- 비행일이 두 파라미터 사이인 항공편만.
- 요소: CarrierId, ConnectionId, FlightDate(키 3개), Price(통화 의미 주석), Currency, SeatsMax, SeatsOccupied, 계산 요소 FreeSeats(= SeatsMax − SeatsOccupied), 항공사 이름 CarrierName(연관에서).
- 연관: `_Carrier`(SCARR, 1:1), `_Booking`(SBOOK, 0..*)를 노출.
- 권한 검사 불필요.

(2) ABAP 프로그램에서 2026-12-01 ~ 2026-12-31 기간, 빈 좌석이 있는 항공편의 CarrierId, CarrierName, ConnectionId, FlightDate, FreeSeats와 연관 경로로 항공사 URL을 읽는 SELECT를 쓰시오.

(3) (2)에서 `\_Booking-bookid`를 SELECT 목록에 넣으면 결과가 어떻게 바뀌는지 쓰시오.

(4) 글로벌 클래스 `ZCL_HC_AMDP_REVENUE`에 AMDP 프로시저 메서드 `get_top_connections`를 작성하시오.
- 입력: 연도 `iv_year`(문자 4자리), 상위 개수 `iv_top`(i)
- 출력: 테이블 `et_result`(carrid, connid, 예약 건수 bookings, 매출 합계 revenue, 통화 currency). SBOOK에서 해당 연도 비행, 취소되지 않은 예약을 노선·통화별로 집계해 매출 내림차순 상위 N개
- 현재 클라이언트 데이터만 읽는다. 읽기 전용.

(5) (4)의 메서드를 호출해 결과를 출력하는 콘솔 실행 코드(`if_oo_adt_classrun~main`)를 쓰시오.

(6) (1)~(3)과 (4)~(5)는 각각 100점 만점으로 채점한다. 이 문제를 CDS가 아니라 AMDP로 푸는 것이 적절한 경우는 언제인지 쓰시오.

<details><summary>정답·해설</summary>

**(1)**

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Flights in a period'
define view entity ZHC_I_FlightPeriod
  with parameters
    @Environment.systemField: #SYSTEM_DATE
    p_from_date : abap.dats,
    p_to_date   : abap.dats
  as select from sflight
  association [1..1] to scarr as _Carrier
    on $projection.CarrierId = _Carrier.carrid
  association [0..*] to sbook as _Booking
    on  $projection.CarrierId    = _Booking.carrid
    and $projection.ConnectionId = _Booking.connid
    and $projection.FlightDate   = _Booking.fldate
{
  key carrid               as CarrierId,
  key connid               as ConnectionId,
  key fldate               as FlightDate,
      @Semantics.amount.currencyCode: 'Currency'
      price                as Price,
      currency             as Currency,
      seatsmax             as SeatsMax,
      seatsocc             as SeatsOccupied,
      seatsmax - seatsocc  as FreeSeats,
      _Carrier.carrname    as CarrierName,

      _Carrier,
      _Booking
}
where fldate between $parameters.p_from_date and $parameters.p_to_date
```

**(2)**

```abap
SELECT FROM zhc_i_flightperiod( p_from_date = '20261201',
                                p_to_date   = '20261231' )
  FIELDS CarrierId,
         CarrierName,
         ConnectionId,
         FlightDate,
         FreeSeats,
         \_Carrier-url AS CarrierUrl
  WHERE FreeSeats > 0
  ORDER BY CarrierId, FlightDate
  INTO TABLE @DATA(lt_free).
```

**(3)** `_Booking`은 0..* 연관이라 경로 식이 LEFT OUTER JOIN으로 바뀌어 항공편 1건이 예약 수만큼 여러 행으로 늘어난다(예약이 없는 항공편은 bookid가 초기값인 1행). 집계가 목적이면 뷰에서 `count(*)`/GROUP BY를 쓰거나 별도 SELECT로 처리해야 한다.

채점 기준((1)~(3), 100점)

| 항목 | 배점 |
|---|---|
| `define view entity ... with parameters ... as select from` 구조 | 15 |
| 시스템 날짜 기본 파라미터 주석 | 10 |
| 연관 두 개(카디널리티, `$projection` ON 조건) + 노출 | 20 |
| 키, 별칭, 금액 의미 주석(view entity에서 필수), 계산 요소, 연관 경로 요소 | 20 |
| WHERE에서 `$parameters` 사용 | 10 |
| (2) 파라미터 전달 문법, 경로 식 `\_Carrier-url`, WHERE/ORDER BY | 15 |
| (3) to-many 경로의 행 증가 설명 | 10 |

- CDS 뷰 엔티티에서 CURR 타입 요소는 `@Semantics.amount.currencyCode`로 통화 요소를 지정하지 않으면 문법 오류다(DDIC 기반 뷰와 다른 점).
- `@Environment.systemField: #SYSTEM_DATE`가 붙은 파라미터는 ABAP SQL에서 생략할 수 있고, 생략하면 `sy-datum`(클라우드에서는 시스템 날짜)이 자동으로 들어간다.
- ABAP SQL에서 CDS 파라미터는 `엔티티( p1 = ..., p2 = ... )`처럼 쉼표로 구분한다. 연관 경로는 `\_연관-요소`.
- 클라이언트 필드는 뷰 엔티티에서 자동 처리되므로 선택 목록에 mandt를 쓰지 않는다.
- `$projection` 대신 원본 필드 이름(`sflight.carrid`)을 ON 조건에 써도 된다.

**(4)·(5)** (4)의 클래스 정의·AMDP 메서드와 (5)의 `if_oo_adt_classrun~main`을 한 클래스로 쓴다.

```abap
CLASS zcl_hc_amdp_revenue DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES if_amdp_marker_hdb.
    INTERFACES if_oo_adt_classrun.

    TYPES: BEGIN OF ty_rev,
             carrid   TYPE s_carr_id,
             connid   TYPE s_conn_id,
             bookings TYPE i,
             revenue  TYPE p LENGTH 9 DECIMALS 2,
             currency TYPE s_currcode,
           END OF ty_rev,
           tt_rev TYPE STANDARD TABLE OF ty_rev WITH EMPTY KEY.

    METHODS get_top_connections
      IMPORTING VALUE(iv_year)   TYPE char4
                VALUE(iv_top)    TYPE i
      EXPORTING VALUE(et_result) TYPE tt_rev.
ENDCLASS.

CLASS zcl_hc_amdp_revenue IMPLEMENTATION.

  METHOD get_top_connections BY DATABASE PROCEDURE
                             FOR HDB
                             LANGUAGE SQLSCRIPT
                             OPTIONS READ-ONLY
                             USING sbook.
    et_result = SELECT carrid,
                       connid,
                       CAST( COUNT(*) AS INTEGER )            AS bookings,
                       CAST( SUM( loccuram ) AS DECIMAL(17,2) ) AS revenue,
                       loccurkey                              AS currency
                  FROM sbook
                 WHERE mandt     = SESSION_CONTEXT('CLIENT')
                   AND LEFT( fldate, 4 ) = :iv_year
                   AND cancelled <> 'X'
                 GROUP BY carrid, connid, loccurkey
                 ORDER BY revenue DESC
                 LIMIT :iv_top;
  ENDMETHOD.

  METHOD if_oo_adt_classrun~main.
    TRY.
        get_top_connections( EXPORTING iv_year   = '2026'
                                       iv_top    = 5
                             IMPORTING et_result = DATA(lt_rev) ).
        out->write( lt_rev ).
      CATCH cx_amdp_error INTO DATA(lx).
        out->write( lx->get_text( ) ).
    ENDTRY.
  ENDMETHOD.

ENDCLASS.
```

채점 기준((4)~(5), 100점)

| 항목 | 배점 |
|---|---|
| `INTERFACES if_amdp_marker_hdb` | 10 |
| 파라미터 모두 VALUE 전달, 결과 테이블 타입 정의 | 15 |
| `BY DATABASE PROCEDURE FOR HDB LANGUAGE SQLSCRIPT OPTIONS READ-ONLY USING sbook` | 20 |
| SQLScript: 집계·GROUP BY·ORDER BY·LIMIT, 파라미터 앞 콜론 | 25 |
| 클라이언트 조건(SESSION_CONTEXT('CLIENT') 또는 클라이언트 파라미터) | 15 |
| 호출 코드와 예외 처리 | 15 |

- AMDP 메서드의 파라미터는 모두 값 전달(VALUE)이어야 하고, 반환값(RETURNING)은 프로시저에서 쓸 수 없다(EXPORTING 사용). 구조나 깊은 타입이 아닌 기본형·평면 테이블만 가능하다.
- SQLScript 안에서는 ABAP SQL과 달리 클라이언트가 자동 처리되지 않는다. `SESSION_CONTEXT('CLIENT')`로 거르거나, 7.52 이상이면 `AMDP OPTIONS CDS SESSION CLIENT current`를 쓴다. 이 조건을 빠뜨리는 것이 가장 흔한 감점이다.
- `USING`에 쓰는 테이블/뷰를 모두 선언해야 하며, SQLScript에서 ABAP 변수는 `:iv_top`처럼 콜론을 붙인다. SQLScript의 문장 끝은 `;`.
- `COUNT(*)`는 BIGINT, `SUM`은 더 큰 DECIMAL을 돌려주므로 출력 컴포넌트 타입(i, p 9,2)에 맞게 CAST한다. 출력 테이블과 결과 컬럼은 이름·순서·타입이 맞아야 한다.

**(6)** 면접 단골 질문이다. 가능하면 CDS/ABAP SQL로 해결하고, 그것으로 표현하기 어려운 절차적 DB 로직(SQLScript 함수, 다단계 계산)만 AMDP로 쓴다. AMDP는 HANA 전용이고 디버깅도 별도다.

</details>

---

### C-047. 손코딩: 여행 BO 전체 구현(BDEF + validation + determination + action + 기능 제어) [작성] ★★★
<!-- src: HC-040, MX-067 -->
데이터 모델 `ZR_HC_Travel`(테이블 `zhc_travel`)이 있다. 요소와 테이블 필드는 다음과 같다.

| CDS 요소 | 테이블 필드 | 비고 |
|---|---|---|
| TravelUUID | travel_uuid | 키, RAW16 |
| TravelID | travel_id | |
| AgencyID / CustomerID | agency_id / customer_id | |
| BeginDate / EndDate | begin_date / end_date | |
| Description | description | |
| TotalPrice / CurrencyCode | total_price / currency_code | |
| OverallStatus | overall_status | O 열림, A 승인, X 거절 |
| LocalLastChangedAt | local_last_changed_at | ETag |

(1) managed, strict(2), Draft 없음, 구현 클래스 `zbp_r_hc_travel`로 다음을 만족하는 **BDEF**를 작성하시오.
- 생성·수정·삭제, TravelUUID는 프레임워크가 채움, OverallStatus는 읽기 전용, CustomerID·BeginDate·EndDate 필수
- 전역 권한 검사
- 생성 시 상태가 비어 있으면 `O`로 넣는 determination `setInitialStatus`
- 저장 시(생성 또는 CustomerID 변경) 고객을 검사하는 validation `validateCustomer`
- action `acceptTravel`, `rejectTravel`(결과는 자기 자신 1건, 인스턴스 기능 제어)
- 테이블 필드와 CDS 요소의 mapping

(2) 핸들러 클래스의 **선언부**를 작성하시오(전역 권한, 인스턴스 기능 제어, action 2개, determination, validation).

(3) 전역 권한(모든 작업 허용으로 구현)과 인스턴스 기능 제어(이미 승인된 여행은 accept 버튼, 이미 거절된 여행은 reject 버튼 비활성화)를 구현하시오.

(4) action `acceptTravel`, `rejectTravel`을 구현하시오.

(5) determination `setInitialStatus`와 validation `validateCustomer`를 구현하시오. validation은 고객이 `/dmo/customer`에 있는지 검사하고, 오류는 CustomerID 필드에 표시하며, 고쳐지면 메시지가 사라져야 한다.

(6) (1)~(5)는 100점 만점으로 채점한다. 같은 구조의 BO `ZMX_R_Travel`(별칭 Travel, OverallStatus: O=진행, A=승인, X=취소)에 다음을 추가하시오(7점).
- BDEF: 인스턴스 action `cancelTravel`. 결과는 자기 자신 한 건이고 동적 기능 제어를 받는다.
- 핸들러 `cancelTravel`: 이미 취소(X)된 건은 오류 메시지와 함께 실패 처리하고, 나머지는 X로 바꾼 뒤 결과를 돌려준다.
- `get_instance_features`: OverallStatus가 X이면 `cancelTravel` 버튼을 비활성화한다.

(7) (6)에서 기능 제어로 버튼을 비활성화했는데도 action 안에서 상태를 다시 검사해야 하는 이유를 쓰시오. 기능 제어 결과가 Fiori Elements의 버튼으로 보이려면 무엇이 더 필요한지도 쓰시오.

<details><summary>정답·해설</summary>

**(1)~(5)** BDEF `ZR_HC_Travel`:

```abap
managed implementation in class zbp_r_hc_travel unique;
strict ( 2 );

define behavior for ZR_HC_Travel alias Travel
persistent table zhc_travel
lock master
authorization master ( global )
etag master LocalLastChangedAt
{
  create;
  update;
  delete;

  field ( numbering : managed, readonly ) TravelUUID;
  field ( readonly ) OverallStatus, LocalLastChangedAt;
  field ( mandatory ) CustomerID, BeginDate, EndDate;

  action ( features : instance ) acceptTravel result [1] $self;
  action ( features : instance ) rejectTravel result [1] $self;

  determination setInitialStatus on modify { create; }
  validation validateCustomer on save { create; field CustomerID; }

  mapping for zhc_travel
  {
    TravelUUID         = travel_uuid;
    TravelID           = travel_id;
    AgencyID           = agency_id;
    CustomerID         = customer_id;
    BeginDate          = begin_date;
    EndDate            = end_date;
    Description        = description;
    TotalPrice         = total_price;
    CurrencyCode       = currency_code;
    OverallStatus      = overall_status;
    LocalLastChangedAt = local_last_changed_at;
  }
}
```

핸들러(클래스 `zbp_r_hc_travel`의 Local Types). 선언부가 (2), `get_global_authorizations`·`get_instance_features`가 (3), action 두 개가 (4), `setInitialStatus`·`validateCustomer`가 (5)의 답이다.

```abap
CLASS lhc_travel DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    CONSTANTS:
      BEGIN OF c_status,
        open     TYPE c LENGTH 1 VALUE 'O',
        accepted TYPE c LENGTH 1 VALUE 'A',
        rejected TYPE c LENGTH 1 VALUE 'X',
      END OF c_status.

    METHODS get_global_authorizations FOR GLOBAL AUTHORIZATION
      IMPORTING REQUEST requested_authorizations FOR Travel RESULT result.

    METHODS get_instance_features FOR INSTANCE FEATURES
      IMPORTING keys REQUEST requested_features FOR Travel RESULT result.

    METHODS acceptTravel FOR MODIFY
      IMPORTING keys FOR ACTION Travel~acceptTravel RESULT result.

    METHODS rejectTravel FOR MODIFY
      IMPORTING keys FOR ACTION Travel~rejectTravel RESULT result.

    METHODS setInitialStatus FOR DETERMINE ON MODIFY
      IMPORTING keys FOR Travel~setInitialStatus.

    METHODS validateCustomer FOR VALIDATE ON SAVE
      IMPORTING keys FOR Travel~validateCustomer.

ENDCLASS.

CLASS lhc_travel IMPLEMENTATION.

  METHOD get_global_authorizations.
    result = VALUE #( %create                = if_abap_behv=>auth-allowed
                      %update                = if_abap_behv=>auth-allowed
                      %delete                = if_abap_behv=>auth-allowed
                      %action-acceptTravel   = if_abap_behv=>auth-allowed
                      %action-rejectTravel   = if_abap_behv=>auth-allowed ).
  ENDMETHOD.

  METHOD get_instance_features.
    READ ENTITIES OF zr_hc_travel IN LOCAL MODE
      ENTITY Travel
        FIELDS ( OverallStatus ) WITH CORRESPONDING #( keys )
      RESULT DATA(travels)
      FAILED failed.

    result = VALUE #( FOR t IN travels
                      ( %tky                 = t-%tky
                        %action-acceptTravel = COND #( WHEN t-OverallStatus = c_status-accepted
                                                       THEN if_abap_behv=>fc-o-disabled
                                                       ELSE if_abap_behv=>fc-o-enabled )
                        %action-rejectTravel = COND #( WHEN t-OverallStatus = c_status-rejected
                                                       THEN if_abap_behv=>fc-o-disabled
                                                       ELSE if_abap_behv=>fc-o-enabled ) ) ).
  ENDMETHOD.

  METHOD acceptTravel.
    MODIFY ENTITIES OF zr_hc_travel IN LOCAL MODE
      ENTITY Travel
        UPDATE FIELDS ( OverallStatus )
        WITH VALUE #( FOR key IN keys ( %tky          = key-%tky
                                        OverallStatus = c_status-accepted ) )
      FAILED failed
      REPORTED reported.

    READ ENTITIES OF zr_hc_travel IN LOCAL MODE
      ENTITY Travel
        ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(travels).

    result = VALUE #( FOR t IN travels ( %tky = t-%tky %param = t ) ).
  ENDMETHOD.

  METHOD rejectTravel.
    MODIFY ENTITIES OF zr_hc_travel IN LOCAL MODE
      ENTITY Travel
        UPDATE FIELDS ( OverallStatus )
        WITH VALUE #( FOR key IN keys ( %tky          = key-%tky
                                        OverallStatus = c_status-rejected ) )
      FAILED failed
      REPORTED reported.

    READ ENTITIES OF zr_hc_travel IN LOCAL MODE
      ENTITY Travel
        ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(travels).

    result = VALUE #( FOR t IN travels ( %tky = t-%tky %param = t ) ).
  ENDMETHOD.

  METHOD setInitialStatus.
    READ ENTITIES OF zr_hc_travel IN LOCAL MODE
      ENTITY Travel
        FIELDS ( OverallStatus ) WITH CORRESPONDING #( keys )
      RESULT DATA(travels).

    DELETE travels WHERE OverallStatus IS NOT INITIAL.
    CHECK travels IS NOT INITIAL.

    MODIFY ENTITIES OF zr_hc_travel IN LOCAL MODE
      ENTITY Travel
        UPDATE FIELDS ( OverallStatus )
        WITH VALUE #( FOR t IN travels ( %tky          = t-%tky
                                         OverallStatus = c_status-open ) )
      REPORTED DATA(update_reported).

    reported = CORRESPONDING #( DEEP update_reported ).
  ENDMETHOD.

  METHOD validateCustomer.
    READ ENTITIES OF zr_hc_travel IN LOCAL MODE
      ENTITY Travel
        FIELDS ( CustomerID ) WITH CORRESPONDING #( keys )
      RESULT DATA(travels).

    DATA customers TYPE SORTED TABLE OF /dmo/customer WITH UNIQUE KEY customer_id.
    customers = CORRESPONDING #( travels DISCARDING DUPLICATES
                                 MAPPING customer_id = CustomerID EXCEPT * ).
    DELETE customers WHERE customer_id IS INITIAL.

    IF customers IS NOT INITIAL.
      SELECT FROM /dmo/customer
        FIELDS customer_id
        FOR ALL ENTRIES IN @customers
        WHERE customer_id = @customers-customer_id
        INTO TABLE @DATA(valid_customers).
    ENDIF.

    LOOP AT travels INTO DATA(travel).
      " 이전 메시지 지우기(같은 state area를 빈 메시지로)
      APPEND VALUE #( %tky        = travel-%tky
                      %state_area = 'VALIDATE_CUSTOMER' ) TO reported-travel.

      IF travel-CustomerID IS INITIAL
         OR NOT line_exists( valid_customers[ customer_id = travel-CustomerID ] ).
        APPEND VALUE #( %tky = travel-%tky ) TO failed-travel.
        APPEND VALUE #( %tky                = travel-%tky
                        %state_area         = 'VALIDATE_CUSTOMER'
                        %msg                = new_message_with_text(
                                                severity = if_abap_behv_message=>severity-error
                                                text     = |고객 { travel-CustomerID }이(가) 없습니다| )
                        %element-CustomerID = if_abap_behv=>mk-on ) TO reported-travel.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.
```

채점 기준((1)~(5), 100점)

| 항목 | 배점 |
|---|---|
| BDEF 헤더(managed, implementation class, strict(2)), lock/authorization/etag master | 10 |
| BDEF 필드 특성(numbering managed, readonly, mandatory), mapping | 10 |
| BDEF action(features : instance, result [1] $self), determination, validation 트리거 | 15 |
| 핸들러 메서드 선언 시그니처(FOR GLOBAL AUTHORIZATION, INSTANCE FEATURES, ACTION, DETERMINE ON MODIFY, VALIDATE ON SAVE) | 15 |
| 기능 제어: READ IN LOCAL MODE + fc-o-enabled/disabled | 10 |
| action: MODIFY IN LOCAL MODE로 상태 변경 + 결과 읽어 `%param`에 반환 | 15 |
| determination: 비어 있을 때만 갱신, reported 전달 | 10 |
| validation: 고객 일괄 조회, failed/reported, state area 지우기, `%element` | 15 |

- `IN LOCAL MODE`는 자기 BO 안에서 권한·기능 제어 검사를 건너뛴다. 기능 제어로 막힌(readonly) OverallStatus를 action/determination이 바꿀 수 있는 이유다.
- 핸들러에서 `COMMIT WORK`, `ROLLBACK WORK`, 직접 DB 갱신은 금지다(저장은 managed 프레임워크가 save 시퀀스에서 한다).
- determination `on modify { create; }`는 생성 직후 같은 요청 안에서 실행되고, validation `on save`는 저장 직전에 실행된다. validation에서 failed를 채우면 저장 전체가 거부된다.
- validation 첫 APPEND(메시지 없는 state area 행)는 이전 검사에서 남은 같은 영역의 메시지를 지우는 관용구다(draft에서 특히 중요).
- 고객을 루프 안에서 한 건씩 SELECT하지 않고 `FOR ALL ENTRIES`로 한 번에 읽는다(빈 테이블이면 FAE가 전체를 읽으므로 그 전에 IS NOT INITIAL 확인).
- action 결과 `result [1] $self`는 `%param`에 갱신된 인스턴스를 넣어 돌려준다. UI는 이 값으로 화면을 새로 그린다.

**(6)** 예시. BDEF:

```abap
define behavior for ZMX_R_Travel alias Travel
...
{
  ...
  action ( features : instance ) cancelTravel result [1] $self;
}
```

핸들러 선언:

```abap
METHODS get_instance_features FOR INSTANCE FEATURES
  IMPORTING keys REQUEST requested_features FOR Travel RESULT result.
METHODS cancelTravel FOR MODIFY
  IMPORTING keys FOR ACTION Travel~cancelTravel RESULT result.
```

구현:

```abap
METHOD cancelTravel.
  READ ENTITIES OF zmx_r_travel IN LOCAL MODE
    ENTITY Travel FIELDS ( OverallStatus ) WITH CORRESPONDING #( keys )
    RESULT DATA(lt_travel).

  LOOP AT lt_travel INTO DATA(ls_travel) WHERE OverallStatus = 'X'.
    APPEND VALUE #( %tky = ls_travel-%tky ) TO failed-travel.
    APPEND VALUE #( %tky = ls_travel-%tky
                    %msg = new_message_with_text(
                             severity = if_abap_behv_message=>severity-error
                             text     = '이미 취소된 출장입니다' ) ) TO reported-travel.
  ENDLOOP.
  DELETE lt_travel WHERE OverallStatus = 'X'.

  MODIFY ENTITIES OF zmx_r_travel IN LOCAL MODE
    ENTITY Travel UPDATE FIELDS ( OverallStatus )
    WITH VALUE #( FOR t IN lt_travel ( %tky = t-%tky OverallStatus = 'X' ) ).

  READ ENTITIES OF zmx_r_travel IN LOCAL MODE
    ENTITY Travel ALL FIELDS WITH CORRESPONDING #( lt_travel )
    RESULT DATA(lt_done).
  result = VALUE #( FOR d IN lt_done ( %tky = d-%tky %param = d ) ).
ENDMETHOD.

METHOD get_instance_features.
  READ ENTITIES OF zmx_r_travel IN LOCAL MODE
    ENTITY Travel FIELDS ( OverallStatus ) WITH CORRESPONDING #( keys )
    RESULT DATA(lt_travel) FAILED failed.

  result = VALUE #( FOR t IN lt_travel
    ( %tky = t-%tky
      %action-cancelTravel = COND #( WHEN t-OverallStatus = 'X'
                                     THEN if_abap_behv=>fc-o-disabled
                                     ELSE if_abap_behv=>fc-o-enabled ) ) ).
ENDMETHOD.
```

채점 기준((6), 7점)

- BDEF: `action ( features : instance ) ... result [1] $self` 1점
- 핸들러 선언 두 개(`FOR INSTANCE FEATURES`, `FOR ACTION ... RESULT`) 1점
- action에서 IN LOCAL MODE로 읽고 상태 확인 1점
- 실패 건의 `failed`와 `reported`(`%msg`) 처리 1점
- 나머지 건 UPDATE 1점
- `result`에 `%tky`와 `%param` 채움 1점
- `get_instance_features`의 `%action-cancelTravel`과 `fc-o-disabled/enabled` 1점

**(7)** 기능 제어는 UI에서 버튼을 비활성화할 뿐이다. 다른 소비자(EML, Web API)가 호출할 수 있으므로 action 안의 상태 검사를 빼면 안 된다. 기능 제어 결과가 Fiori Elements에서 버튼 활성/비활성으로 보이려면 메타데이터 확장의 `@UI.lineItem`/`@UI.identification`에 `#FOR_ACTION`이 있어야 한다.

</details>

---

### C-048. 손코딩: EML 소비자 코드 [작성] ★★★
<!-- src: HC-041, RP-049 -->
콘솔 클래스(`if_oo_adt_classrun~main`)에서 Travel BO를 EML로 다룬다. (1)은 `ZR_TravelTP`, (3)은 C-047의 `ZR_HC_Travel`을 쓴다.

(1) 다음을 수행하는 코드를 작성하시오.
- 한 번의 `MODIFY ENTITIES`로 Travel 1건(`CustomerID = '000001'`, `BeginDate = '20261201'`, `EndDate = '20261210'`)을 만들고, 같은 요청 안에서 그 인스턴스에 action `acceptTravel`을 실행한다.
- MODIFY 단계에서 실패하면 `'Modify failed'`를 출력하고 롤백한다.
- 저장하고, 저장이 실패하면 `'Commit failed'`를 출력하고 롤백, 성공하면 새 Travel의 키(`TravelUUID`)를 출력한다.

(2) (1)에서 새 키는 어디서 얻는지, late numbering BO라면 무엇이 달라지는지 쓰시오.

(3) 콘솔 클래스 `ZCL_HC_EML_CLEANUP`를 작성하시오.
- ① 시작일이 오늘보다 이전인데 아직 상태가 `O`인 여행의 키를 ABAP SQL로 찾는다(없으면 "대상 없음" 출력 후 종료).
- ② 한 번의 `MODIFY ENTITIES`로 그 여행들의 Description을 `Auto-rejected YYYY-MM-DD`로 바꾸고 action `rejectTravel`을 실행한다.
- ③ 같은 요청에서, 상태가 이미 `X`이고 종료일이 1년 넘게 지난 여행은 삭제한다.
- ④ MODIFY 단계 실패 시 reported의 메시지를 모두 출력하고 롤백, 성공하면 커밋하고 커밋 실패도 처리한다.
- ⑤ 성공하면 ② 대상 여행을 다시 읽어 TravelID, OverallStatus, Description을 출력한다.

(4) (3)에서 조건 검색을 EML이 아니라 ABAP SQL로 먼저 하는 이유를 쓰시오. 이미 거절된 여행에 `rejectTravel`을 실행하면 어떻게 되는지, `COMMIT ENTITIES`를 쓸 수 있는 곳과 없는 곳도 쓰시오.

(5) (3)에서 `%tky` 대신 `TravelUUID`를 직접 채운 이유와, Draft BO라면 어떻게 해야 하는지 쓰시오.

<details><summary>정답·해설</summary>

**(1)** 예시

```abap
METHOD if_oo_adt_classrun~main.
  MODIFY ENTITIES OF zr_traveltp
    ENTITY Travel
      CREATE FIELDS ( CustomerID BeginDate EndDate )
        WITH VALUE #( ( %cid       = 'T1'
                        CustomerID = '000001'
                        BeginDate  = '20261201'
                        EndDate    = '20261210' ) )
      EXECUTE acceptTravel
        FROM VALUE #( ( %cid_ref = 'T1' ) )
    MAPPED DATA(mapped)
    FAILED DATA(failed)
    REPORTED DATA(reported).

  IF failed IS NOT INITIAL.
    out->write( 'Modify failed' ).
    ROLLBACK ENTITIES.
    RETURN.
  ENDIF.

  COMMIT ENTITIES RESPONSE OF zr_traveltp
    FAILED DATA(commit_failed)
    REPORTED DATA(commit_reported).

  IF sy-subrc <> 0.
    out->write( 'Commit failed' ).
    ROLLBACK ENTITIES.
  ELSE.
    out->write( mapped-travel[ 1 ]-TravelUUID ).
  ENDIF.
ENDMETHOD.
```

채점 포인트: ① `%cid`로 생성하고 `%cid_ref`로 같은 요청의 action에 연결 ② action은 `EXECUTE ... FROM` ③ `failed` 확인 ④ `COMMIT ENTITIES` 후 `sy-subrc` 확인 ⑤ 실패 시 `ROLLBACK ENTITIES` ⑥ 새 키는 `mapped`에서 얻기.

**(2)** 새 키는 `mapped`에서 얻는다. managed UUID라면 MODIFY 직후 `mapped`에 이미 최종 키가 있다. late numbering이면 MODIFY 시점에는 임시 키(`%pid`)뿐이므로 `COMMIT ENTITIES BEGIN ... CONVERT KEY OF ... END`로 최종 키를 얻어야 한다.

**(3)**

```abap
CLASS zcl_hc_eml_cleanup DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.
ENDCLASS.

CLASS zcl_hc_eml_cleanup IMPLEMENTATION.
  METHOD if_oo_adt_classrun~main.
    DATA(lv_today)    = cl_abap_context_info=>get_system_date( ).
    DATA(lv_year_ago) = CONV d( lv_today - 365 ).

    " 1) 대상 찾기
    SELECT FROM zr_hc_travel
      FIELDS TravelUUID
      WHERE OverallStatus = 'O'
        AND BeginDate     < @lv_today
      INTO TABLE @DATA(lt_open).

    SELECT FROM zr_hc_travel
      FIELDS TravelUUID
      WHERE OverallStatus = 'X'
        AND EndDate       < @lv_year_ago
      INTO TABLE @DATA(lt_old_rejected).

    IF lt_open IS INITIAL AND lt_old_rejected IS INITIAL.
      out->write( '대상 없음' ).
      RETURN.
    ENDIF.

    " 2)+3) 한 번의 MODIFY 요청
    MODIFY ENTITIES OF zr_hc_travel
      ENTITY Travel
        UPDATE FIELDS ( Description )
        WITH VALUE #( FOR o IN lt_open
                      ( TravelUUID  = o-TravelUUID
                        Description = |Auto-rejected { lv_today DATE = ISO }| ) )
        EXECUTE rejectTravel
        FROM VALUE #( FOR o IN lt_open ( TravelUUID = o-TravelUUID ) )
        DELETE FROM VALUE #( FOR r IN lt_old_rejected ( TravelUUID = r-TravelUUID ) )
      FAILED   DATA(ls_failed)
      REPORTED DATA(ls_reported).

    " 4) 결과 처리
    IF ls_failed IS NOT INITIAL.
      LOOP AT ls_reported-travel INTO DATA(ls_rep) WHERE %msg IS BOUND.
        out->write( ls_rep-%msg->if_message~get_text( ) ).
      ENDLOOP.
      ROLLBACK ENTITIES.
      RETURN.
    ENDIF.

    COMMIT ENTITIES
      RESPONSE OF zr_hc_travel
      FAILED   DATA(ls_commit_failed)
      REPORTED DATA(ls_commit_reported).
    IF sy-subrc <> 0 OR ls_commit_failed IS NOT INITIAL.
      LOOP AT ls_commit_reported-travel INTO DATA(ls_crep) WHERE %msg IS BOUND.
        out->write( ls_crep-%msg->if_message~get_text( ) ).
      ENDLOOP.
      ROLLBACK ENTITIES.
      RETURN.
    ENDIF.

    " 5) 다시 읽기
    READ ENTITIES OF zr_hc_travel
      ENTITY Travel
        FIELDS ( TravelID OverallStatus Description )
        WITH VALUE #( FOR o IN lt_open ( TravelUUID = o-TravelUUID ) )
      RESULT DATA(lt_after).

    LOOP AT lt_after INTO DATA(ls_after).
      out->write( |{ ls_after-TravelID } { ls_after-OverallStatus } { ls_after-Description }| ).
    ENDLOOP.
    out->write( |삭제 { lines( lt_old_rejected ) }건| ).
  ENDMETHOD.
ENDCLASS.
```

채점 기준(100점)

| 항목 | 배점 |
|---|---|
| ABAP SQL로 키 수집(CDS 엔티티 사용, 날짜 계산) | 10 |
| MODIFY ENTITIES 안에 UPDATE FIELDS + EXECUTE + DELETE를 한 요청으로 | 25 |
| `FOR` 식으로 파생 타입 테이블 만들기 | 10 |
| FAILED/REPORTED 받기, 메시지 텍스트 출력(`%msg->if_message~get_text`) | 15 |
| 실패 시 ROLLBACK ENTITIES | 10 |
| COMMIT ENTITIES RESPONSE OF ... + sy-subrc/실패 확인 | 15 |
| READ ENTITIES로 재조회와 출력 | 15 |

**(4)** EML의 MODIFY/READ는 키로만 동작하므로 조건 검색은 ABAP SQL(또는 CDS)로 먼저 키를 구한다. 소비자(BO 밖)는 `IN LOCAL MODE`를 쓸 수 없어 권한·기능 제어가 적용된다. 이미 거절된 여행에 `rejectTravel`을 실행하면 C-047의 기능 제어 때문에 failed가 된다(그래서 대상을 상태 O로 걸렀다). MODIFY는 트랜잭션 버퍼만 바꾸고, `COMMIT ENTITIES`가 save 시퀀스(validation → save)를 돌려 실제로 저장한다. validation 실패는 커밋 응답의 FAILED로 돌아온다. 콘솔 클래스(ADT classrun)나 일반 ABAP에서는 `COMMIT ENTITIES`를 쓰고, RAP 핸들러 안에서는 쓰면 안 된다.

**(5)** 키가 TravelUUID 하나이고 Draft가 없으므로 `%tky` 대신 `TravelUUID` 필드를 직접 채웠다. Draft BO라면 `%is_draft`까지 들어 있는 `%tky`를 써야 한다.

</details>

---

### C-049. 손코딩: custom entity 쿼리 구현(필터·페이징·건수) [작성] ★★★
<!-- src: MX-068 -->
다음 custom entity를 Fiori Elements 목록에서 쓰려 한다. 데이터는 `/dmo/flight`에서 읽고 LoadPct = 점유율(소수 1자리)이다.

```cds
@EndUserText.label: '항공편 점유율'
@ObjectModel.query.implementedBy: 'ABAP:ZCL_MX_LOAD_QUERY'
define custom entity ZMX_CE_FlightLoad
{
  key CarrierId    : /dmo/carrier_id;
  key ConnectionId : /dmo/connection_id;
  key FlightDate   : /dmo/flight_date;
      LoadPct      : abap.dec(5,1);
}
```

(1) 페이징(`$top`/`$skip`), 항공사 필터, 건수(`$count`) 요청을 지원하는 쿼리 구현 클래스 `ZCL_MX_LOAD_QUERY`를 작성하시오(8점).

(2) 페이지 크기가 무제한으로 요청되면 `get_page_size( )`가 무엇을 돌려주고, `UP TO ... ROWS`에 무엇을 넘겨야 하는지 쓰시오.

(3) 필터를 range로 바꿀 수 없을 때 어떤 예외가 나는지, 점유율 계산에서 0으로 나누기를 어떻게 막는지, OFFSET을 쓸 때 ORDER BY가 필요한 이유를 쓰시오.

(4) 요청되지 않은 데이터를 `set_data`하거나 요청된 건수를 돌려주지 않으면 어떻게 되는지 쓰시오. 정렬 요청은 어떻게 받는지, custom entity는 언제 쓰는지도 쓰시오.

<details><summary>정답·해설</summary>

**(1)** 예시

```abap
CLASS zcl_mx_load_query DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES if_rap_query_provider.
ENDCLASS.

CLASS zcl_mx_load_query IMPLEMENTATION.
  METHOD if_rap_query_provider~select.
    DATA lt_res     TYPE STANDARD TABLE OF zmx_ce_flightload WITH EMPTY KEY.
    DATA lr_carrier TYPE RANGE OF /dmo/carrier_id.

    " 1) 필터 → range
    TRY.
        DATA(lt_ranges) = io_request->get_filter( )->get_as_ranges( ).
      CATCH cx_rap_query_filter_no_range.
        " range로 바꿀 수 없는 필터는 이 예제에서 무시
    ENDTRY.
    READ TABLE lt_ranges INTO DATA(ls_rng) WITH KEY name = 'CARRIERID'.
    IF sy-subrc = 0.
      lr_carrier = CORRESPONDING #( ls_rng-range ).
    ENDIF.

    " 2) 페이징
    DATA(lv_skip) = io_request->get_paging( )->get_offset( ).
    DATA(lv_top)  = io_request->get_paging( )->get_page_size( ).
    IF lv_top = if_rap_query_paging=>page_size_unlimited.   " -1
      lv_top = 0.                        " UP TO 0 ROWS = 제한 없음
    ENDIF.

    " 3) 데이터
    IF io_request->is_data_requested( ).
      SELECT FROM /dmo/flight
        FIELDS carrier_id    AS CarrierId,
               connection_id AS ConnectionId,
               flight_date   AS FlightDate,
               division( seats_occupied * 100, seats_max, 1 ) AS LoadPct
        WHERE carrier_id IN @lr_carrier
          AND seats_max > 0
        ORDER BY carrier_id, connection_id, flight_date
        INTO CORRESPONDING FIELDS OF TABLE @lt_res
        UP TO @lv_top ROWS OFFSET @lv_skip.
      io_response->set_data( lt_res ).
    ENDIF.

    " 4) 건수
    IF io_request->is_total_numb_of_rec_requested( ).
      SELECT COUNT( * ) FROM /dmo/flight
        WHERE carrier_id IN @lr_carrier
          AND seats_max > 0
        INTO @DATA(lv_cnt).
      io_response->set_total_number_of_records( lv_cnt ).
    ENDIF.
  ENDMETHOD.
ENDCLASS.
```

채점 기준(8점)

- `IF_RAP_QUERY_PROVIDER~SELECT` 구현 1점
- 필터를 `get_filter( )->get_as_ranges( )`로 받아 WHERE에 반영 2점
- 페이징 `get_offset`/`get_page_size`와 `UP TO ... OFFSET`, 무제한(-1) 처리 2점
- `is_data_requested` 확인 후 `set_data` 1점
- `is_total_numb_of_rec_requested` 확인 후 건수 계산과 `set_total_number_of_records` 1점
- 0으로 나누기 방지와 OFFSET용 ORDER BY 1점

**(2)** 무제한이면 `get_page_size( )`가 `if_rap_query_paging=>page_size_unlimited`(-1)를 돌려준다. ABAP SQL에서 `UP TO 0 ROWS`는 행 수 제한이 없다는 뜻이므로 0을 넘긴다. (원본 답안은 이때 1000으로 바꿨는데, 그러면 1000건 넘는 데이터가 잘린다. 0으로 바로잡았다.)

**(3)** range로 바꿀 수 없는 필터면 `get_as_ranges( )`가 `cx_rap_query_filter_no_range`를 낸다(예제에서는 잡아서 무시). 0으로 나누기는 `seats_max > 0` 조건으로 막는다. OFFSET 페이징은 정렬이 고정되어야 페이지 사이에 행이 겹치거나 빠지지 않으므로 ORDER BY가 필요하다.

**(4)** custom entity는 DB 테이블이 없으므로 프레임워크가 SQL을 만들어 주지 않는다. OData 요청 옵션을 직접 해석해야 한다. 요청되지 않은 데이터를 `set_data`하거나, 요청된 건수를 돌려주지 않으면 런타임 예외가 난다. 정렬 요청은 `get_sort_elements( )`로 받을 수 있다(여기서는 고정 정렬). 외부 API 결과나 계산 결과를 RAP/Fiori로 보여 줄 때 이 방식을 쓴다.

</details>

---

## 출처

**SAP 공식 문서·샘플**
- SAP-samples ABAP cheat sheets: https://github.com/SAP-samples/abap-cheat-sheets
  - CDS View Entities: https://github.com/SAP-samples/abap-cheat-sheets/blob/main/15_CDS_View_Entities.md
  - ABAP for RAP: EML: https://github.com/SAP-samples/abap-cheat-sheets/blob/main/08_EML_ABAP_for_RAP.md
  - RAP Behavior Definition Language: https://github.com/SAP-samples/abap-cheat-sheets/blob/main/36_RAP_Behavior_Definition_Language.md
  - ABAP for Cloud Development: https://github.com/SAP-samples/abap-cheat-sheets/blob/main/19_ABAP_for_Cloud_Development.md
  - AMDP: https://github.com/SAP-samples/abap-cheat-sheets/blob/main/12_AMDP.md
  - ABAP Unit Tests: https://github.com/SAP-samples/abap-cheat-sheets/blob/main/14_ABAP_Unit_Tests.md
- RAP 개발 가이드(SAP Help): https://help.sap.com/docs/abap-cloud/abap-rap/abap-restful-application-programming-model
  - 구현 유형: https://help.sap.com/docs/abap-cloud/abap-rap/business-object-implementation-types
  - Draft: https://help.sap.com/docs/abap-cloud/abap-rap/draft
- ABAP Keyword Documentation, RAP BDL: https://help.sap.com/docs/abap-cloud/abap-keyword/rap-bdl-for-behavior-definitions
- ABAP Keyword Documentation: https://help.sap.com/doc/abapdocu_latest_index_htm/latest/en-US/index.htm
- RAP100 공식 실습(SAP-samples/abap-platform-rap100): https://github.com/SAP-samples/abap-platform-rap100
- SAP Tutorials: https://developers.sap.com/tutorials/abap-environment-rap100-validation.html , https://developers.sap.com/tutorials/abap-environment-rap100-determination.html , https://developers.sap.com/tutorials/abap-environment-rap100-instance-action.html
- SAP Tutorials(Fiori tools + RAP): https://developers.sap.com/tutorials/fiori-tools-rap-modify-list-report.html , https://developers.sap.com/tutorials/fiori-tools-rap-prepare-service.html
- ABAP Cloud FAQ(SAP Community): https://pages.community.sap.com/topics/abap/abap-cloud-faq
- SAP News, Clean core levels A–D(2025.08): https://news.sap.com/2025/08/extend-sap-s4hana-cloud-right-way-clean-clear/
- SAP Community 블로그, Introducing the Background Processing Framework: https://answers.sap.com/t5/technology-blogs-by-sap/introducing-the-background-processing-framework/ba-p/13579056
- SAP Community 블로그, Conventional ABAP to ABAP on HANA mapping: https://blogs.sap.com/2018/03/18/conventional-abap-to-abap-on-hana-mapping-blog-1-of-2/
- OData 문서(V2/V4 URL 규칙, 쿼리 옵션): https://www.odata.org/documentation/
- UI5 데이터 바인딩과 모델: https://ui5.sap.com/1.38.63/docs/guide/68b9644a253741e8a4b9e4279a35c247.html

**SAP Learning·인증**
- SAP Certified Associate – Back-End Developer – ABAP Cloud(C_ABAPD): https://learning.sap.com/certifications/sap-certified-associate-back-end-developer-abap-cloud , https://training.sap.com/certification/C_ABAPD_2309
- C_FIORD 주제 영역: https://training.sap.com/certification/C_FIORD_2404
- Acquire Core ABAP Skills: https://learning.sap.com/learning-journeys/acquire-core-abap-skills
- Explaining Extensibility Model Best Practices(Practicing Clean Core Extensibility): https://learning.sap.com/learning-journeys/practicing-clean-core-extensibility-for-sap-s-4hana-cloud/explaining-extensibility-model-best-practices_e290f382-800e-40ef-a203-85a13115f487
- Preventing Unauthorized Access to Data: https://learning.sap.com/courses/building-data-models-with-the-abap-dictionary-and-abap-core-data-services/preventing-unauthorized-access-to-data_e73ee8f7-8547-44d6-95a8-2675a62ee0cf
- Implementing SQL Expressions in CDS Views: https://learning.sap.com/courses/building-data-models-with-the-abap-dictionary-and-abap-core-data-services/implementing-sql-expressions-in-cds-views_a9962c08-c5df-46a6-ba30-a74acf5c86b2
- Implementing Authority Checks: https://learning.sap.com/courses/building-transactional-apps-with-the-abap-restful-application-programming-model/implementing-authority-checks
- Implementing Input Checks Using Validations: https://learning.sap.com/courses/building-transactional-apps-with-the-abap-restful-application-programming-model/implementing-input-checks-using-validations
- SAP 인증 시험 형식 해설(eursap): https://eursap.eu/blog/an-introduction-to-sap-certification-exams-how-to-make-the-most-of-your-sap-certification-attempt

**면접 질문·후기·기술 블로그**
- 15 ABAP on HANA Interview Questions and Answers(climbtheladder): https://climbtheladder.com/abap-on-hana-interview-questions/
- SAP ABAP on HANA Interview Questions & Answers(ERPVITS): https://www.erpvits.com/blog/sap-abap-on-hana-interview-questions-answers/
- SAP ABAP on HANA Interview Questions(Mindmajix): https://mindmajix.com/sap-abap-on-hana-interview-questions
- SAP ABAP Interview Questions(Mindmajix): https://mindmajix.com/sap-abap-interview-questions
- SAP ABAP Interview Questions(Final Round AI): https://www.finalroundai.com/blog/sap-abap-interview-questions
- SAP ABAP Interview Questions(InterviewBit): https://www.interviewbit.com/sap-abap-interview-questions/
- SAP ABAP Interview Questions(Guru99): https://www.guru99.com/sap-abap-interview-questions.html
- SAP PRESS 블로그, SAP ECC vs SAP S/4HANA technical foundations: https://blog.sap-press.com/sap-ecc-vs-sap-s4hana-technical-foundations
- AmbitionBox Capgemini SAP ABAP Consultant 면접 후기: https://www.ambitionbox.com/interviews/capgemini-interview-questions/sap-abap-consultant
- Glassdoor ABAP Developer 면접 질문(Capgemini 후기 포함): https://static.glassdoor.fr/Interview/abap-developer-interview-questions-SRCH_KO0,14_IP98.htm
- Glassdoor ABAP 면접 질문(ALSTOM: RFC/OData/ALE/CDS): https://static.glassdoor.fr/Interview/abap-interview-questions-SRCH_KO0,4_IP78.htm
- Glassdoor SAP "SAP ABAP Developer" 후기(DDIC~BTP, OData CRUDQ): https://static-pc.glassdoor.de/Interview/SAP-SAP-ABAP-Developer-Interview-Questions-EI_IE10471.0,3_KO4,22.htm
- Glassdoor Accenture SAP ABAP Developer 후기(HANA CDS·OData): https://static-pc.glassdoor.de/Interview/Accenture-SAP-ABAP-Developer-Interview-Questions-EI_IE4138.0,9_KO10,28_IP3.htm
- Glassdoor Infosys 후기(RAP·OO, 코드 작성): https://www.glassdoor.sg/Interview/Infosys-Interview-E7927-RVW63485517.htm
- ABAP CDS Views Series Part 5: Virtual Elements, Parameters(aixsap): https://aixsap.com/abap-cds-views-series-part-5-virtual-elements-parameters-and-session-variables-for-dynamic-data-modeling/
- Handle asynchronous task in background job from RAP(erpqna): https://www.erpqna.com/handle-asynchronous-task-in-background-job-from-a-stateless-ui-application-using-rap-business-object/
