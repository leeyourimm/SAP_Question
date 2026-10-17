## 1. 관리형(Managed) BO와 Draft

### R-01. Travel 앱 골격: 테이블부터 Fiori 미리보기까지 [작성] ★★
<!-- covers: DDIC 테이블, 데이터 생성 클래스, root view entity, composition, association to parent, @Semantics, LOB, projection view, transactional_query, value help, additionalBinding, useForValidation, text element, localized, @Search, semanticKey, metadata extension, @UI.headerInfo, @UI.facet, lineItem, identification, fieldGroup, dataPoint, criticality, textArrangement, multiLineText, virtual element, managed BDEF, strict(2), with draft, draft table, late numbering, adjust_numbers, lock master, total etag, etag master, global authorization, projection BDEF, service definition, service binding, OData V4 -->

**목표**
- Travel(여행)과 Booking(예약) 두 엔터티로 이루어진 관리형(managed) RAP BO를 테이블부터 직접 만들 수 있습니다.
- 기본 뷰(R), 프로젝션 뷰(C), 메타데이터 확장(MDE)의 역할을 나누고, 어노테이션을 하나씩 붙여 가며 각 어노테이션이 UI와 런타임에 어떤 효과를 내는지 확인할 수 있습니다.
- `with draft` + `late numbering` 조합에서 draft 테이블에 왜 `DRAFTUUID`/`PARENTDRAFTUUID`가 필요한지 설명할 수 있습니다.
- 세이버 클래스의 `adjust_numbers`로 최종 키를 저장 직전에 매기는 흐름을 구현할 수 있습니다.
- 서비스 정의·바인딩을 만들고 Fiori elements 미리보기에서 목록·상세·생성·수정·삭제·draft 동작을 확인할 수 있습니다.

**전제**
- SAP BTP ABAP Environment(Trial), ADT, 패키지 `ZRAP_###` (`###` = 본인 이니셜 3자리).
- 표준 데모 객체: `/DMO/TRAVEL`, `/DMO/BOOKING`(복사 원본), `/DMO/I_Agency`, `/DMO/I_Customer`, `/DMO/I_Carrier`, `/DMO/I_Connection`, `/DMO/I_Flight`, `/DMO/I_Overall_Status_VH`, `/DMO/I_Booking_Status_VH`, 값 도움말 `/DMO/I_Agency_StdVH`, `/DMO/I_Customer_StdVH`, `/DMO/I_Carrier_StdVH`, `/DMO/I_Connection_StdVH`, `/DMO/I_Flight_StdVH`, 그리고 SAP 표준 `I_Currency`, `I_CurrencyStdVH`.
- `/DMO/TRAVEL`이 비어 있으면 먼저 `/DMO/CL_FLIGHT_DATA_GENERATOR`를 콘솔 실행(F9)하세요.
- 이 문제는 "돌아가는 최소한"까지만 만듭니다. 검증·결정·액션·기능 제어·사이드 이펙트는 R-02, 인터페이스 계층은 R-03, 이벤트·추가 저장은 R-04에서 이 BO를 확장합니다.

**만들 객체**

| 순서 | 객체 유형 | 이름 | 역할 |
|---|---|---|---|
| 1 | 데이터베이스 테이블 | `ZRAP_ATRAV_###` | Travel 활성 데이터 |
| 2 | 데이터베이스 테이블 | `ZRAP_ABOOK_###` | Booking 활성 데이터 |
| 3 | ABAP 클래스 | `ZCL_RAP_GEN_DATA_###` | /DMO 데이터를 복사하는 콘솔 클래스 |
| 4 | CDS 뷰 엔터티 | `ZRAP_R_TRAVEL_###` | 기본 BO 루트 엔터티 |
| 5 | CDS 뷰 엔터티 | `ZRAP_R_BOOKING_###` | 기본 BO 자식 엔터티 |
| 6 | CDS 프로젝션 뷰 | `ZRAP_C_TRAVEL_###` | UI용 루트 프로젝션 |
| 7 | CDS 프로젝션 뷰 | `ZRAP_C_BOOKING_###` | UI용 자식 프로젝션 |
| 8 | ABAP 클래스 | `ZCL_RAP_TRAV_VE_###` | 가상 요소 `OverallStatusCriticality` 계산 |
| 9 | 메타데이터 확장 | `ZRAP_C_TRAVEL_###` | Travel UI 레이아웃 |
| 10 | 메타데이터 확장 | `ZRAP_C_BOOKING_###` | Booking UI 레이아웃 |
| 11 | 행동 정의(BDEF) | `ZRAP_R_TRAVEL_###` | managed + draft + late numbering |
| 12 | 데이터베이스 테이블 | `ZRAP_DTRAV_###`, `ZRAP_DBOOK_###` | draft 테이블(퀵 픽스로 생성) |
| 13 | ABAP 클래스(행동 풀) | `ZBP_RAP_R_TRAVEL_###` | 전역 권한 + `adjust_numbers` |
| 14 | 행동 정의(BDEF) | `ZRAP_C_TRAVEL_###` | 프로젝션 행동 |
| 15 | 서비스 정의 | `ZRAP_UI_TRAVEL_###` | 노출할 엔터티 목록 |
| 16 | 서비스 바인딩 | `ZRAP_UI_TRAVEL_O4_###` | OData V4 - UI |

> **키 전략 한눈에 (왜 어떤 BO에는 UUID 키가 없나요?)**
> RAP는 UUID 키를 **필수로 요구하지 않습니다.** 새로 만드는 관리형 BO에는 `sysuuid_x16` 키 + `numbering : managed`가 가장 간단하고 권장되는 방식이지만, 업무 번호를 키로 쓰는 것도 공식 방식입니다(SAP Flight 참조 시나리오의 `/DMO/I_Travel_M`도 TravelID가 키). 이 문제집은 번호 매기는 방식을 모두 연습하려고 BO마다 키를 다르게 잡았습니다.
>
> | 문제 | 활성 테이블 키 | 번호 매기기 | 이렇게 정한 이유 |
> |---|---|---|---|
> | R-01~R-04 Travel/Booking | TravelID, BookingID (업무 번호) | late numbering (`adjust_numbers`) | 저장 직전에 번호를 매기는 방식을 연습. 대신 draft 테이블에는 `DRAFTUUID`/`PARENTDRAFTUUID` 키가 필요(8단계) |
> | R-05~R-07 레거시 주문 | OrderID, ItemNo | 레거시 Z 클래스가 매김 (unmanaged) | 이미 있는 레거시 테이블 키를 바꿀 수 없다는 상황 |
> | R-09 Singleton 설정 | AgencyID | 사용자가 입력 (external) | 설정 데이터는 업무 키 자체가 식별자 |
> | R-11 조직도(계층) | OrgID, UnitID | early numbering (`earlynumbering_create/cba`) | 생성 즉시 번호를 매기는 방식을 연습 |
> | R-18 생성기 실습 | TaskID | 사용자가 입력 | RAP100 생성기 결과와 비교하려고 같은 모양을 씀 |
> | R-10 Supplier, R-11 Project, R-14 Quote, R-15 Loan, R-16 Ticket | `..._uuid` (`sysuuid_x16`) | **managed numbering** | 권장 방식. 사람이 읽는 번호(예: SupplierID)는 키가 아닌 필드로 두고 결정(determination)으로 채움 |
>
> 컨트롤·스위치·로그용 보조 테이블(`zrap_ctrl_###`, `zrap_loansw_###`, `zrap_pcat_###` 등)은 BO가 아니라서 키 방식과 관계없습니다.

#### 1단계. 활성 테이블 두 개 만들기

요구사항
1. 패키지 `ZRAP_###`에서 **New > Other ABAP Repository Object > Database Table**로 `ZRAP_ATRAV_###`(설명: `Travel active data`)를 만드세요.
2. 아래 필드 표대로 정의하세요. `travel_id`는 키이며, 값은 저장 시점에 BO가 매깁니다(late numbering). 금액 두 필드는 `currency_code`를 참조합니다.
3. 같은 방법으로 `ZRAP_ABOOK_###`(설명: `Booking active data`)를 만드세요. 키는 `client`, `travel_id`, `booking_id`입니다.
4. 테이블 헤더 어노테이션: 확장 불가(`#NOT_EXTENSIBLE`), 투명 테이블, 전달 클래스 A, 데이터 유지 관리 제한(`#RESTRICTED`).

`ZRAP_ATRAV_###`

| 필드 | 키 | 데이터 엘리먼트 | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | ✓ | (내장) abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| travel_id | ✓ | /dmo/travel_id | NUMC | 8 | 0 | 여행 번호 (late numbering) |
| agency_id | | /dmo/agency_id | NUMC | 6 | 0 | 여행사 |
| customer_id | | /dmo/customer_id | NUMC | 6 | 0 | 고객 |
| begin_date | | /dmo/begin_date | DATS | 8 | 0 | 시작일 |
| end_date | | /dmo/end_date | DATS | 8 | 0 | 종료일 |
| booking_fee | | /dmo/booking_fee | CURR | 16 | 2 | 예약 수수료 (참조: currency_code) |
| total_price | | /dmo/total_price | CURR | 16 | 2 | 총액 (참조: currency_code) |
| currency_code | | /dmo/currency_code | CUKY | 5 | 0 | 통화 |
| description | | /dmo/description | SSTR | 1024 | 0 | 설명 |
| overall_status | | /dmo/overall_status | CHAR | 1 | 0 | 상태 O/A/X |
| attachment | | /dmo/attachment | RSTR | 0 | 0 | 첨부 파일(LOB) |
| mime_type | | /dmo/mime_type | CHAR | 128 | 0 | MIME 타입 |
| file_name | | /dmo/filename | CHAR | 128 | 0 | 파일 이름 |
| created_by | | abp_creation_user | CHAR | 12 | 0 | 생성자 |
| created_at | | abp_creation_tstmpl | DEC (TIMESTAMPL) | 21 | 7 | 생성 시각 |
| local_last_changed_by | | abp_locinst_lastchange_user | CHAR | 12 | 0 | 인스턴스 최종 변경자 |
| local_last_changed_at | | abp_locinst_lastchange_tstmpl | DEC (TIMESTAMPL) | 21 | 7 | 인스턴스 최종 변경 시각 (ETag) |
| last_changed_at | | abp_lastchange_tstmpl | DEC (TIMESTAMPL) | 21 | 7 | 최종 변경 시각 (total ETag) |

`ZRAP_ABOOK_###`

| 필드 | 키 | 데이터 엘리먼트 | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | ✓ | (내장) abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| travel_id | ✓ | /dmo/travel_id | NUMC | 8 | 0 | 상위 여행 번호 |
| booking_id | ✓ | /dmo/booking_id | NUMC | 4 | 0 | 예약 번호 (late numbering) |
| booking_date | | /dmo/booking_date | DATS | 8 | 0 | 예약일 |
| customer_id | | /dmo/customer_id | NUMC | 6 | 0 | 고객 |
| carrier_id | | /dmo/carrier_id | CHAR | 3 | 0 | 항공사 |
| connection_id | | /dmo/connection_id | NUMC | 4 | 0 | 노선 번호 |
| flight_date | | /dmo/flight_date | DATS | 8 | 0 | 비행일 |
| flight_price | | /dmo/flight_price | CURR | 16 | 2 | 항공료 (참조: currency_code) |
| currency_code | | /dmo/currency_code | CUKY | 5 | 0 | 통화 |
| booking_status | | /dmo/booking_status | CHAR | 1 | 0 | 상태 N/B/X |
| local_last_changed_at | | abp_locinst_lastchange_tstmpl | DEC (TIMESTAMPL) | 21 | 7 | 인스턴스 최종 변경 시각 (ETag) |

**직접 추가할 어노테이션**
- `@EndUserText.label` — 테이블 설명 문구.
- `@AbapCatalog.enhancement.category` — 이 테이블을 append로 확장할 수 있는지.
- `@AbapCatalog.tableCategory` — 투명 테이블인지 등 테이블 종류.
- `@AbapCatalog.deliveryClass` — 애플리케이션 데이터인지(전달 클래스).
- `@AbapCatalog.dataMaintenance` — 일반 유지 관리 도구에서 직접 수정할 수 있는지.
- `@Semantics.amount.currencyCode` — 금액 필드가 어느 통화 필드를 따르는지.

**확인**
- 두 테이블이 오류 없이 활성화됩니다(Ctrl+F3).
- 테이블에서 F8(Data Preview)을 누르면 빈 테이블이 열립니다.

<details><summary>정답·해설</summary>

```cds
@EndUserText.label : 'Travel active data'                 // 테이블 설명
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE      // append 확장 불가
@AbapCatalog.tableCategory : #TRANSPARENT                // 투명 테이블
@AbapCatalog.deliveryClass : #A                          // 애플리케이션 데이터
@AbapCatalog.dataMaintenance : #RESTRICTED               // 직접 유지 관리 제한
define table zrap_atrav_### {

  key client            : abap.clnt not null;
  key travel_id         : /dmo/travel_id not null;
  agency_id             : /dmo/agency_id;
  customer_id           : /dmo/customer_id;
  begin_date            : /dmo/begin_date;
  end_date              : /dmo/end_date;
  @Semantics.amount.currencyCode : 'zrap_atrav_###.currency_code'   // 금액 → 통화 참조
  booking_fee           : /dmo/booking_fee;
  @Semantics.amount.currencyCode : 'zrap_atrav_###.currency_code'   // 금액 → 통화 참조
  total_price           : /dmo/total_price;
  currency_code         : /dmo/currency_code;
  description           : /dmo/description;
  overall_status        : /dmo/overall_status;
  attachment            : /dmo/attachment;
  mime_type             : /dmo/mime_type;
  file_name             : /dmo/filename;
  created_by            : abp_creation_user;
  created_at            : abp_creation_tstmpl;
  local_last_changed_by : abp_locinst_lastchange_user;
  local_last_changed_at : abp_locinst_lastchange_tstmpl;
  last_changed_at       : abp_lastchange_tstmpl;

}
```

```cds
@EndUserText.label : 'Booking active data'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_abook_### {

  key client            : abap.clnt not null;
  key travel_id         : /dmo/travel_id not null;
  key booking_id        : /dmo/booking_id not null;
  booking_date          : /dmo/booking_date;
  customer_id           : /dmo/customer_id;
  carrier_id            : /dmo/carrier_id;
  connection_id         : /dmo/connection_id;
  flight_date           : /dmo/flight_date;
  @Semantics.amount.currencyCode : 'zrap_abook_###.currency_code'   // 금액 → 통화 참조
  flight_price          : /dmo/flight_price;
  currency_code         : /dmo/currency_code;
  booking_status        : /dmo/booking_status;
  local_last_changed_at : abp_locinst_lastchange_tstmpl;

}
```

**왜 이렇게 쓰나**
- 관리 필드에 `abp_*` 데이터 엘리먼트를 쓰는 이유: 관리형 BO는 CDS의 `@Semantics.user.*`/`@Semantics.systemDateTime.*` 어노테이션이 붙은 필드를 **프레임워크가 자동으로 채웁니다**. 이 자동 처리가 되려면 타입이 사용자 이름(CHAR 12)·타임스탬프(TIMESTAMPL 등)와 호환되어야 합니다.
- `local_last_changed_at`(인스턴스 ETag)과 `last_changed_at`(total ETag)을 **따로** 둡니다. draft BO에서는 둘 다 필요하며, 같은 필드를 쓰지 않는 것이 권장됩니다(3·8단계에서 사용).
- Booking에는 생성자 필드가 없습니다. 자식은 잠금·권한을 부모에 맡기므로(`lock dependent`, `authorization dependent`) ETag용 `local_last_changed_at`만 있으면 충분합니다.
- `description`은 `/dmo/description`을 따르며, 로컬에서 확인한 Flight 참조 시나리오 소스에서는 도메인 `/DMO/TEXT`가 `SSTR 1024`로 정의되어 있습니다. 시스템 버전에 따라 다를 수 있으니 ADT에서 F2로 확인하세요(실제 시스템에서 확인 필요).

**자주 나는 오류와 해결**
- 금액 필드에 `@Semantics.amount.currencyCode`가 없으면 활성화 시 참조 필드 관련 오류가 납니다. 값은 `'테이블명.필드명'` 형식(소문자 그대로)으로 적으세요.

</details>

#### 2단계. 데모 데이터 생성 클래스 만들기

요구사항
1. 클래스 `ZCL_RAP_GEN_DATA_###`를 만들고 인터페이스 `IF_OO_ADT_CLASSRUN`을 구현하세요(F9로 콘솔 실행).
2. 실행할 때마다 `ZRAP_ABOOK_###`, `ZRAP_ATRAV_###`를 먼저 비우세요.
3. `/DMO/TRAVEL`에서 여행 번호 오름차순으로 **50건**을 `ZRAP_ATRAV_###`에 복사하세요. 필드 대응:
   - `status`(N=New, P=Planned, B=Booked, X=Cancelled) → `overall_status`: `B`→`A`(Accepted), `X`→`X`(Rejected), 그 외→`O`(Open)
   - `createdby`→`created_by`, `createdat`→`created_at`, `lastchangedby`→`local_last_changed_by`, `lastchangedat`→`local_last_changed_at`와 `last_changed_at` 둘 다
   - `attachment`, `mime_type`, `file_name`은 빈 값
4. 방금 복사한 여행에 속하는 예약만 `/DMO/BOOKING`에서 `ZRAP_ABOOK_###`로 복사하세요. `booking_status`는 상위 여행 상태가 `A`면 `B`(Booked), `X`면 `X`(Cancelled), 그 외 `N`(New). `local_last_changed_at`은 상위 여행 값을 그대로 씁니다.
5. 루프 안에서 SELECT/INSERT 하지 말고, `INSERT ... FROM ( SELECT ... )` 서브쿼리로 한 번에 넣으세요.
6. 마지막에 두 테이블의 건수를 콘솔에 출력하세요. 예: `Travel rows: 50`, `Booking rows: 1xx`.

**확인**
- F9 실행 후 콘솔에 건수가 나옵니다.
- 두 테이블 Data Preview에서 데이터가 보이고, `overall_status`에 O/A/X만 있는지 확인하세요.

<details><summary>정답·해설</summary>

```abap
CLASS zcl_rap_gen_data_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.

ENDCLASS.


CLASS zcl_rap_gen_data_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.

    DATA attachment TYPE /dmo/attachment.
    DATA mime_type  TYPE /dmo/mime_type.
    DATA file_name  TYPE /dmo/filename.

    " 1) clear old data (child first)
    DELETE FROM zrap_abook_###.                         "#EC CI_NOWHERE
    DELETE FROM zrap_atrav_###.                         "#EC CI_NOWHERE
    " After step 8 (draft tables exist) you may also clear drafts:
    " DELETE FROM zrap_dbook_###.
    " DELETE FROM zrap_dtrav_###.

    " 2) travels: column order must follow the target table (client is implicit)
    INSERT zrap_atrav_### FROM (
      SELECT FROM /dmo/travel AS travel
        FIELDS
          travel~travel_id      AS travel_id,
          travel~agency_id      AS agency_id,
          travel~customer_id    AS customer_id,
          travel~begin_date     AS begin_date,
          travel~end_date       AS end_date,
          travel~booking_fee    AS booking_fee,
          travel~total_price    AS total_price,
          travel~currency_code  AS currency_code,
          travel~description    AS description,
          CASE travel~status    " N(New) | P(Planned) | B(Booked) | X(Cancelled)
            WHEN 'B' THEN 'A'
            WHEN 'X' THEN 'X'
            ELSE 'O'
          END                   AS overall_status,
          @attachment           AS attachment,
          @mime_type            AS mime_type,
          @file_name            AS file_name,
          travel~createdby      AS created_by,
          travel~createdat      AS created_at,
          travel~lastchangedby  AS local_last_changed_by,
          travel~lastchangedat  AS local_last_changed_at,
          travel~lastchangedat  AS last_changed_at
        ORDER BY travel~travel_id
        UP TO 50 ROWS ).

    " 3) bookings of the copied travels only (join with our own table, no loop)
    INSERT zrap_abook_### FROM (
      SELECT FROM /dmo/booking AS booking
        INNER JOIN zrap_atrav_### AS travel
          ON travel~travel_id = booking~travel_id
        FIELDS
          booking~travel_id      AS travel_id,
          booking~booking_id     AS booking_id,
          booking~booking_date   AS booking_date,
          booking~customer_id    AS customer_id,
          booking~carrier_id     AS carrier_id,
          booking~connection_id  AS connection_id,
          booking~flight_date    AS flight_date,
          booking~flight_price   AS flight_price,
          booking~currency_code  AS currency_code,
          CASE travel~overall_status
            WHEN 'A' THEN 'B'
            WHEN 'X' THEN 'X'
            ELSE 'N'
          END                    AS booking_status,
          travel~local_last_changed_at AS local_last_changed_at ).

    COMMIT WORK.

    " 4) report
    SELECT COUNT( * ) FROM zrap_atrav_### INTO @DATA(travel_count).
    SELECT COUNT( * ) FROM zrap_abook_### INTO @DATA(booking_count).
    out->write( |Travel rows: { travel_count }| ).
    out->write( |Booking rows: { booking_count }| ).

  ENDMETHOD.

ENDCLASS.
```

**클래스 구조 해설**
- `if_oo_adt_classrun~main`: ADT에서 F9를 누르면 호출되는 유일한 진입점입니다. `out` 파라미터(콘솔 출력 객체)로 결과를 씁니다.
- `INSERT dbtab FROM ( SELECT ... )`: 결과 집합의 열이 **대상 테이블 열 순서대로** 들어가므로(client 제외) FIELDS 순서를 테이블 정의와 똑같이 맞춰야 합니다. 같은 원본 열(`lastchangedat`)을 두 번 꺼내 두 대상 열에 넣을 수 있습니다.
- 예약 복사는 방금 넣은 `zrap_atrav_###`와 조인하여 "복사한 50건의 여행에 속한 예약"만 고릅니다. 같은 DB 트랜잭션 안이므로 커밋 전에도 보입니다.
- 이 클래스는 RAP BO를 거치지 않고 테이블에 직접 씁니다. **BO가 아직 없거나 초기 데이터를 넣을 때만** 이렇게 하고, BO가 생긴 뒤의 변경은 EML(`MODIFY ENTITIES`)로 해야 검증·결정이 실행됩니다.
- 원본 패턴은 RAP100 데이터 생성 클래스와 Flight 참조 시나리오의 draft 데이터 생성 클래스(상태 CASE 변환)를 따랐습니다.

</details>

#### 3단계. 기본 BO 뷰: 루트 Travel과 자식 Booking

요구사항
1. **New > Other > Data Definition**으로 `ZRAP_R_TRAVEL_###`(템플릿: Define Root View Entity, 원본 `zrap_atrav_###`)와 `ZRAP_R_BOOKING_###`(템플릿: Define View Entity, 원본 `zrap_abook_###`)를 만드세요.
2. 모든 필드에 CamelCase 별칭을 붙이세요. Travel: `TravelID, AgencyID, CustomerID, BeginDate, EndDate, BookingFee, TotalPrice, CurrencyCode, Description, OverallStatus, Attachment, MimeType, FileName, CreatedBy, CreatedAt, LocalLastChangedBy, LocalLastChangedAt, LastChangedAt`. Booking: `TravelID, BookingID, BookingDate, CustomerID, CarrierID, ConnectionID, FlightDate, FlightPrice, CurrencyCode, BookingStatus, LocalLastChangedAt`.
3. Travel → Booking은 `composition [0..*] of ZRAP_R_BOOKING_### as _Booking`, Booking → Travel은 `association to parent ZRAP_R_TRAVEL_### as _Travel`로 정의하세요.
4. 연관(association)을 정의하고 select 목록 끝에 노출하세요.
   - Travel: `_Agency`(/DMO/I_Agency, AgencyID), `_Customer`(/DMO/I_Customer, CustomerID), `_OverallStatus`(/DMO/I_Overall_Status_VH, OverallStatus), `_Currency`(I_Currency, `Currency` 필드와 연결)
   - Booking: `_Customer`, `_Carrier`(/DMO/I_Carrier, `AirlineID`와 연결), `_Connection`(/DMO/I_Connection, AirlineID+ConnectionID), `_Flight`(/DMO/I_Flight, AirlineID+ConnectionID+FlightDate), `_BookingStatus`(/DMO/I_Booking_Status_VH), `_Currency`
5. 두 뷰 모두 MDE와 프로젝션에서 어노테이션을 덧붙일 수 있게 허용하고, 접근 제어는 지금은 요구하지 않음으로 두세요.
6. 두 뷰는 서로를 참조하므로 **동시에 활성화**(Ctrl+Shift+F3, 두 객체 모두 선택)하세요.

**직접 추가할 어노테이션**
- `@AccessControl.authorizationCheck` — CDS 접근 제어(DCL) 확인을 할지.
- `@Metadata.allowExtensions` — 메타데이터 확장으로 어노테이션을 덧붙일 수 있게 허용.
- `@EndUserText.label` — 뷰 설명.
- `@Semantics.amount.currencyCode` — 금액 요소가 따르는 통화 요소(별칭 이름, 대소문자 구분).
- `@Semantics.largeObject` (`mimeType`, `fileName`, `contentDispositionPreference`) — 이 요소가 OData 스트림(파일 업로드/다운로드)임을 알림.
- `@Semantics.mimeType` — 이 요소가 MIME 타입을 담는다고 알림.
- `@Semantics.user.createdBy` — 생성자를 프레임워크가 자동 기입.
- `@Semantics.systemDateTime.createdAt` — 생성 시각 자동 기입.
- `@Semantics.user.localInstanceLastChangedBy` — 인스턴스 최종 변경자 자동 기입.
- `@Semantics.systemDateTime.localInstanceLastChangedAt` — 인스턴스 최종 변경 시각 자동 기입(ETag로 사용).
- `@Semantics.systemDateTime.lastChangedAt` — 최종 변경 시각 자동 기입(draft의 total ETag로 사용).

**확인**
- 두 뷰가 함께 활성화됩니다.
- `ZRAP_R_TRAVEL_###`에서 F8(Data Preview) → 행 하나 선택 → 연관 `_Booking`을 따라가면 그 여행의 예약이 보입니다.

<details><summary>정답·해설</summary>

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED   // DCL 확인 안 함(접근 제어를 붙일 때 #CHECK로 바꿈) (→ 어노테이션 탭: @AccessControl.authorizationCheck)
@Metadata.allowExtensions: true                    // MDE 허용 (→ 어노테이션 탭: @Metadata.allowExtensions)
@EndUserText.label: 'Travel - base BO view'        // 설명 (→ 어노테이션 탭: @EndUserText.label)
define root view entity ZRAP_R_TRAVEL_###
  as select from zrap_atrav_### as Travel

  composition [0..*] of ZRAP_R_BOOKING_###       as _Booking

  association [0..1] to /DMO/I_Agency            as _Agency        on $projection.AgencyID      = _Agency.AgencyID
  association [0..1] to /DMO/I_Customer          as _Customer      on $projection.CustomerID    = _Customer.CustomerID
  association [1..1] to /DMO/I_Overall_Status_VH as _OverallStatus on $projection.OverallStatus = _OverallStatus.OverallStatus
  association [0..1] to I_Currency               as _Currency      on $projection.CurrencyCode  = _Currency.Currency
{
  key travel_id             as TravelID,
      agency_id             as AgencyID,
      customer_id           as CustomerID,
      begin_date            as BeginDate,
      end_date              as EndDate,
      @Semantics.amount.currencyCode: 'CurrencyCode'          // 금액 → 통화 요소 (→ 어노테이션 탭: @Semantics.amount.currencyCode)
      booking_fee           as BookingFee,
      @Semantics.amount.currencyCode: 'CurrencyCode'
      total_price           as TotalPrice,
      currency_code         as CurrencyCode,
      description           as Description,
      overall_status        as OverallStatus,
      @Semantics.largeObject: { mimeType: 'MimeType',         // MIME 타입 요소(대소문자 구분) (→ 어노테이션 탭: @Semantics.largeObject)
                                fileName: 'FileName',         // 파일 이름 요소
                                contentDispositionPreference: #ATTACHMENT } // 브라우저에서 내려받기
      attachment            as Attachment,
      @Semantics.mimeType: true                               // MIME 타입 요소 (→ 어노테이션 탭: @Semantics.mimeType)
      mime_type             as MimeType,
      file_name             as FileName,
      @Semantics.user.createdBy: true                         // 생성자 자동 기입 (→ 어노테이션 탭: @Semantics.user.createdBy)
      created_by            as CreatedBy,
      @Semantics.systemDateTime.createdAt: true               // 생성 시각 자동 기입 (→ 어노테이션 탭: @Semantics.systemDateTime.createdAt)
      created_at            as CreatedAt,
      @Semantics.user.localInstanceLastChangedBy: true        // 인스턴스 변경자 자동 기입 (→ 어노테이션 탭: @Semantics.user.localInstanceLastChangedBy)
      local_last_changed_by as LocalLastChangedBy,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true // 인스턴스 ETag (→ 어노테이션 탭: @Semantics.systemDateTime.localInstanceLastChangedAt)
      local_last_changed_at as LocalLastChangedAt,
      @Semantics.systemDateTime.lastChangedAt: true           // total ETag (→ 어노테이션 탭: @Semantics.systemDateTime.lastChangedAt)
      last_changed_at       as LastChangedAt,

      // exposed associations
      _Booking,
      _Agency,
      _Customer,
      _OverallStatus,
      _Currency
}
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@Metadata.allowExtensions: true
@EndUserText.label: 'Booking - base BO view'
define view entity ZRAP_R_BOOKING_###
  as select from zrap_abook_### as Booking

  association        to parent ZRAP_R_TRAVEL_###  as _Travel        on  $projection.TravelID      = _Travel.TravelID
  association [1..1] to /DMO/I_Customer           as _Customer      on  $projection.CustomerID    = _Customer.CustomerID
  association [1..1] to /DMO/I_Carrier            as _Carrier       on  $projection.CarrierID     = _Carrier.AirlineID
  association [1..1] to /DMO/I_Connection         as _Connection    on  $projection.CarrierID     = _Connection.AirlineID
                                                                    and $projection.ConnectionID  = _Connection.ConnectionID
  association [1..1] to /DMO/I_Flight             as _Flight        on  $projection.CarrierID     = _Flight.AirlineID
                                                                    and $projection.ConnectionID  = _Flight.ConnectionID
                                                                    and $projection.FlightDate    = _Flight.FlightDate
  association [1..1] to /DMO/I_Booking_Status_VH  as _BookingStatus on  $projection.BookingStatus = _BookingStatus.BookingStatus
  association [0..1] to I_Currency                as _Currency      on  $projection.CurrencyCode  = _Currency.Currency
{
  key travel_id             as TravelID,
  key booking_id            as BookingID,
      booking_date          as BookingDate,
      customer_id           as CustomerID,
      carrier_id            as CarrierID,
      connection_id         as ConnectionID,
      flight_date           as FlightDate,
      @Semantics.amount.currencyCode: 'CurrencyCode'          // 금액 → 통화
      flight_price          as FlightPrice,
      currency_code         as CurrencyCode,
      booking_status        as BookingStatus,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true // 자식 인스턴스 ETag
      local_last_changed_at as LocalLastChangedAt,

      // exposed associations
      _Travel,
      _Customer,
      _Carrier,
      _Connection,
      _Flight,
      _BookingStatus,
      _Currency
}
```

**왜 이렇게 쓰나**
- `define root view entity`: BO 구조의 맨 위(루트)입니다. 루트만 잠금(`lock master`)과 draft의 기준이 될 수 있습니다.
- `composition [0..*] of` ↔ `association to parent`: 이 한 쌍이 "Booking은 Travel에 **속한다**(독립적으로 존재하지 않는다)"는 BO 구조를 정의합니다. 부모를 지우면 자식도 지워지고, 자식 생성은 부모를 통해서만(`create by association`) 할 수 있습니다. 일반 `association`은 단순 참조(여행사·고객 마스터)입니다.
- `@Semantics.*` 관리 필드 어노테이션이 있어야 관리형 BO가 생성/변경 시 해당 필드를 **코드 없이** 채웁니다. 특히 `localInstanceLastChangedAt`이 있어야 관리형 BO가 ETag 값을 자동 갱신합니다.
- `@Semantics.largeObject`의 `mimeType`/`fileName` 값은 **CDS 별칭 이름을 대소문자까지** 정확히 써야 합니다. 이 어노테이션이 붙으면 Fiori 상세 화면에 업로드/다운로드 컨트롤이 생깁니다.
- `_Carrier`의 연결 대상 필드는 `/DMO/I_Carrier`의 키 이름인 `AirlineID`입니다(우리 쪽은 `CarrierID`).

**자주 나는 오류와 해결**
- 한쪽만 활성화하면 "다른 쪽 뷰가 없다"는 오류가 납니다. 두 뷰를 모두 선택해 함께 활성화하세요.

</details>

#### 4단계. 프로젝션 뷰: 값 도움말·텍스트·검색

요구사항
1. `ZRAP_C_TRAVEL_###`: `ZRAP_R_TRAVEL_###`에 대한 **root** 프로젝션 뷰, provider contract `transactional_query`.
2. `ZRAP_C_BOOKING_###`: `ZRAP_R_BOOKING_###`에 대한 프로젝션 뷰. `_Travel`은 부모 프로젝션으로, Travel의 `_Booking`은 자식 프로젝션으로 리다이렉트하세요.
3. Travel에 추가할 요소: `AgencyName`(`_Agency.Name`), `CustomerName`(`_Customer.LastName`), `OverallStatusText`(`_OverallStatus._Text.Text`, 로그온 언어 텍스트만).
4. Booking에 추가할 요소: `CustomerName`, `CarrierName`(`_Carrier.Name`), `BookingStatusText`(`_BookingStatus._Text.Text`, 로그온 언어).
5. 값 도움말(F4):
   - Travel: AgencyID → `/DMO/I_Agency_StdVH`, CustomerID → `/DMO/I_Customer_StdVH`, CurrencyCode → `I_CurrencyStdVH`(`Currency`), OverallStatus → `/DMO/I_Overall_Status_VH`. 모두 입력값을 값 도움말 목록으로 **검증**하도록 하세요.
   - Booking: CustomerID → `/DMO/I_Customer_StdVH`, CarrierID → `/DMO/I_Carrier_StdVH`(`AirlineID`), ConnectionID → `/DMO/I_Connection_StdVH`(이미 입력된 항공사로 **필터**), FlightDate → `/DMO/I_Flight_StdVH`(항공사·노선으로 필터하고, 고르면 FlightPrice·CurrencyCode까지 **채워짐**), CurrencyCode, BookingStatus → `/DMO/I_Booking_Status_VH`.
6. 코드 필드 옆에 텍스트가 나오도록 텍스트 요소를 연결하세요(AgencyID↔AgencyName 등).
7. 목록 화면 검색창에서 TravelID, AgencyID, CustomerID(Booking은 BookingID)로 찾을 수 있게 하세요. TravelID 검색은 오타를 어느 정도 허용(0.9)하세요.
8. 사용자에게 보이는 업무 키(semantic key)는 Travel=TravelID, Booking=BookingID입니다.
9. Travel에 가상 요소 `OverallStatusCriticality : abap.int1`(라벨 `Overall Status Criticality`)을 선언하고 계산 클래스 `ZCL_RAP_TRAV_VE_###`를 지정하세요(클래스는 5단계에서 만듭니다).
10. 관리 필드(CreatedBy 등)도 프로젝션에 남겨 두세요(MDE에서 숨기거나 관리 그룹에 보여 줍니다).

**직접 추가할 어노테이션**
- `@ObjectModel.semanticKey` — 사용자 관점의 업무 키(UI에서 draft 표시와 함께 강조).
- `@Search.searchable` — 이 뷰에 자유 텍스트 검색을 켬.
- `@Search.defaultSearchElement` — 검색창 입력이 이 요소를 대상으로 검색됨.
- `@Search.fuzzinessThreshold` — 유사 검색 허용 정도.
- `@Consumption.valueHelpDefinition` (`entity.name`, `entity.element`) — 값 도움말로 쓸 엔터티와 대응 요소.
- `@Consumption.valueHelpDefinition` `useForValidation` — 값 도움말에 없는 값을 입력하면 UI에서 바로 오류 표시.
- `@Consumption.valueHelpDefinition` `additionalBinding` (`localElement`, `element`, `usage: #FILTER / #RESULT / #FILTER_AND_RESULT`) — 다른 필드 값으로 목록을 거르거나, 고른 행의 다른 열로 내 필드를 채움.
- `@ObjectModel.text.element` — 이 코드 필드의 설명 텍스트가 들어 있는 요소.
- `: localized` (요소 뒤 키워드) — 텍스트 연관에서 로그온 언어 행만 고름.
- `@ObjectModel.virtualElementCalculatedBy` — 가상 요소를 계산할 ABAP 클래스(`'ABAP:클래스명'`).
- `@EndUserText.label` — 가상 요소 라벨.
- `@Metadata.allowExtensions`, `@AccessControl.authorizationCheck`, `@EndUserText.label` — 3단계와 같은 용도.

**확인**
- 두 프로젝션 뷰가 함께 활성화됩니다(가상 요소 클래스가 아직 없다는 경고가 나오면 5단계 뒤 다시 활성화).
- `ZRAP_C_TRAVEL_###` Data Preview에서 `AgencyName`, `CustomerName`, `OverallStatusText`가 채워져 보입니다. (가상 요소는 SQL Data Preview에서는 계산되지 않습니다. OData를 통해서만 계산됩니다.)

<details><summary>정답·해설</summary>

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@Metadata.allowExtensions: true                     // MDE 허용
@EndUserText.label: 'Travel - projection for UI'
@ObjectModel.semanticKey: [ 'TravelID' ]            // 업무 키 (→ 어노테이션 탭: @ObjectModel.semanticKey)
@Search.searchable: true                            // 자유 텍스트 검색 켜기 (→ 어노테이션 탭: @Search.searchable)
define root view entity ZRAP_C_TRAVEL_###
  provider contract transactional_query             // 트랜잭션 UI/API용 프로젝션
  as projection on ZRAP_R_TRAVEL_###
{
      @Search.defaultSearchElement: true            // 검색 대상 (→ 어노테이션 탭: @Search.defaultSearchElement)
      @Search.fuzzinessThreshold: 0.90              // 유사 검색 정도 (→ 어노테이션 탭: @Search.fuzzinessThreshold)
  key TravelID,

      @Search.defaultSearchElement: true
      @Consumption.valueHelpDefinition: [ { entity: { name: '/DMO/I_Agency_StdVH', element: 'AgencyID' }, // F4 원본 (→ 어노테이션 탭: @Consumption.valueHelpDefinition)
                                            useForValidation: true } ]                                   // 입력값 검증 (→ 어노테이션 탭: @Consumption.valueHelpDefinition.useForValidation)
      @ObjectModel.text.element: [ 'AgencyName' ]   // 코드 ↔ 텍스트 연결 (→ 어노테이션 탭: @ObjectModel.text.element)
      AgencyID,
      _Agency.Name              as AgencyName,

      @Search.defaultSearchElement: true
      @Consumption.valueHelpDefinition: [ { entity: { name: '/DMO/I_Customer_StdVH', element: 'CustomerID' },
                                            useForValidation: true } ]
      @ObjectModel.text.element: [ 'CustomerName' ]
      CustomerID,
      _Customer.LastName        as CustomerName,

      BeginDate,
      EndDate,
      BookingFee,
      TotalPrice,

      @Consumption.valueHelpDefinition: [ { entity: { name: 'I_CurrencyStdVH', element: 'Currency' },
                                            useForValidation: true } ]
      CurrencyCode,

      Description,

      @Consumption.valueHelpDefinition: [ { entity: { name: '/DMO/I_Overall_Status_VH', element: 'OverallStatus' },
                                            useForValidation: true } ]
      @ObjectModel.text.element: [ 'OverallStatusText' ]
      OverallStatus,
      _OverallStatus._Text.Text as OverallStatusText : localized,   // 로그온 언어 텍스트만 (→ 어노테이션 탭: localized)

      @ObjectModel.virtualElementCalculatedBy: 'ABAP:ZCL_RAP_TRAV_VE_###'  // 계산 클래스 (→ 어노테이션 탭: @ObjectModel.virtualElementCalculatedBy)
      @EndUserText.label: 'Overall Status Criticality'
      virtual OverallStatusCriticality : abap.int1,

      Attachment,
      MimeType,
      FileName,
      CreatedBy,
      CreatedAt,
      LocalLastChangedBy,
      LocalLastChangedAt,
      LastChangedAt,

      /* Associations */
      _Booking : redirected to composition child ZRAP_C_BOOKING_###,
      _Agency,
      _Customer,
      _OverallStatus,
      _Currency
}
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@Metadata.allowExtensions: true
@EndUserText.label: 'Booking - projection for UI'
@ObjectModel.semanticKey: [ 'BookingID' ]
@Search.searchable: true
define view entity ZRAP_C_BOOKING_###
  as projection on ZRAP_R_BOOKING_###
{
      @Search.defaultSearchElement: true
  key TravelID,

      @Search.defaultSearchElement: true
  key BookingID,

      BookingDate,

      @Consumption.valueHelpDefinition: [ { entity: { name: '/DMO/I_Customer_StdVH', element: 'CustomerID' },
                                            useForValidation: true } ]
      @ObjectModel.text.element: [ 'CustomerName' ]
      CustomerID,
      _Customer.LastName        as CustomerName,

      // 1) carrier
      @Consumption.valueHelpDefinition: [ { entity: { name: '/DMO/I_Carrier_StdVH', element: 'AirlineID' },
                                            useForValidation: true } ]
      @ObjectModel.text.element: [ 'CarrierName' ]
      CarrierID,
      _Carrier.Name             as CarrierName,

      // 2) connection: filtered by the carrier already entered, returns carrier too
      @Consumption.valueHelpDefinition: [ { entity: { name: '/DMO/I_Connection_StdVH', element: 'ConnectionID' },
                                            additionalBinding: [ { localElement: 'CarrierID', element: 'AirlineID', usage: #FILTER_AND_RESULT } ], // 필터+결과 (→ 어노테이션 탭: @Consumption.valueHelpDefinition.additionalBinding)
                                            useForValidation: true } ]
      ConnectionID,

      // 3) flight: filtered by carrier + connection, fills price and currency
      @Consumption.valueHelpDefinition: [ { entity: { name: '/DMO/I_Flight_StdVH', element: 'FlightDate' },
                                            additionalBinding: [ { localElement: 'CarrierID',    element: 'AirlineID',    usage: #FILTER_AND_RESULT },
                                                                 { localElement: 'ConnectionID', element: 'ConnectionID', usage: #FILTER_AND_RESULT },
                                                                 { localElement: 'FlightPrice',  element: 'Price',        usage: #RESULT },
                                                                 { localElement: 'CurrencyCode', element: 'CurrencyCode', usage: #RESULT } ],
                                            useForValidation: true } ]
      FlightDate,

      FlightPrice,

      @Consumption.valueHelpDefinition: [ { entity: { name: 'I_CurrencyStdVH', element: 'Currency' },
                                            useForValidation: true } ]
      CurrencyCode,

      @Consumption.valueHelpDefinition: [ { entity: { name: '/DMO/I_Booking_Status_VH', element: 'BookingStatus' },
                                            useForValidation: true } ]
      @ObjectModel.text.element: [ 'BookingStatusText' ]
      BookingStatus,
      _BookingStatus._Text.Text as BookingStatusText : localized,

      LocalLastChangedAt,

      /* Associations */
      _Travel : redirected to parent ZRAP_C_TRAVEL_###,
      _Customer,
      _Carrier,
      _Connection,
      _Flight,
      _BookingStatus,
      _Currency
}
```

**왜 이렇게 쓰나**
- `provider contract transactional_query`: 이 프로젝션이 "트랜잭션 처리가 되는 UI/API용 쿼리"라는 계약입니다. 루트 프로젝션에 지정하며, 이 계약이 있어야 프로젝션 BDEF(10단계)를 얹을 수 있습니다.
- `redirected to composition child` / `redirected to parent`: 기본 뷰의 composition은 기본 뷰(R)를 가리킵니다. 서비스는 프로젝션(C)끼리 연결되어야 하므로 대상을 프로젝션으로 바꿔 줍니다. 빠뜨리면 BO 구조가 프로젝션 계층에서 끊깁니다.
- `additionalBinding`의 `usage`:
  - `#FILTER`: 내 필드 값으로 값 도움말 목록을 거르기만 함
  - `#RESULT`: 목록에서 고른 행의 값을 내 필드에 채우기만 함
  - `#FILTER_AND_RESULT`: 둘 다
  그래서 FlightDate 도움말을 열면 이미 입력한 항공사·노선의 비행편만 보이고, 하나를 고르면 항공료·통화까지 채워집니다.
- `useForValidation: true`는 **UI(프론트엔드) 검증**일 뿐입니다. EML이나 Web API로 들어오는 값은 막지 못하므로 R-02에서 백엔드 검증(validation)을 꼭 추가합니다.
- `: localized`: `_Text`는 언어별로 여러 행(`[0..*]`)이라 그대로 쓰면 행이 늘어납니다. `localized`를 붙이면 로그온 언어 행만 골라 1건이 됩니다.
- `/DMO/I_Overall_Status_VH`는 원래 `_Text` 연관을 가지고 있으므로 경로 `_OverallStatus._Text.Text`를 쓸 수 있습니다.
- 금액 어노테이션은 기본 뷰에서 전파되므로 프로젝션에서 다시 쓰지 않았습니다(RAP110 정답처럼 다시 써도 문제는 없습니다).
- 가상 요소는 DB에 열이 없고, OData 요청 때 SADL이 클래스 메서드를 불러 값을 채웁니다. 그래서 Data Preview(SQL)에서는 빈 값입니다.

**자주 나는 오류와 해결**
- 가상 요소 클래스가 아직 없어서 활성화가 막히면, 5단계 클래스를 먼저 빈 메서드로 만들고(클래스가 C 뷰 타입을 쓰므로 C 뷰 → 클래스 → C 뷰 재활성화 순서가 될 수 있음) 다시 활성화하세요(실제 시스템에서 확인 필요: 오류인지 경고인지).

</details>

#### 5단계. 가상 요소 계산 클래스 ZCL_RAP_TRAV_VE_###

요구사항
1. 클래스 `ZCL_RAP_TRAV_VE_###`를 만들고 `IF_SADL_EXIT_CALC_ELEMENT_READ`를 구현하세요.
2. `get_calculation_info`: 엔터티가 `ZRAP_C_TRAVEL_###`이고 `OVERALLSTATUSCRITICALITY`가 요청되면, 계산에 필요한 원본 요소 `OVERALLSTATUS`를 반드시 읽도록 알려 주세요.
3. `calculate`: 상태별 critical 값 — `X`(Rejected) → 1(빨강), `O`(Open) → 2(주황), `A`(Accepted) → 3(초록), 그 외 0(중립).
4. 상태값과 critical 값은 상수 구조(`BEGIN OF ...`)로 정의하세요.

**확인**
- 클래스 활성화 후 `ZRAP_C_TRAVEL_###`를 다시 활성화합니다.
- 11단계 미리보기에서 상태 열 색이 상태별로 다르게 보입니다(색은 6단계 MDE의 `criticality`를 넣어야 보입니다).

<details><summary>정답·해설</summary>

```abap
CLASS zcl_rap_trav_ve_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_sadl_exit_calc_element_read.

  PRIVATE SECTION.
    CONSTANTS:
      BEGIN OF travel_status,
        open     TYPE c LENGTH 1 VALUE 'O',
        accepted TYPE c LENGTH 1 VALUE 'A',
        rejected TYPE c LENGTH 1 VALUE 'X',
      END OF travel_status,
      BEGIN OF criticality,
        neutral  TYPE int1 VALUE 0,
        negative TYPE int1 VALUE 1,   " red
        critical TYPE int1 VALUE 2,   " orange
        positive TYPE int1 VALUE 3,   " green
      END OF criticality.

    CONSTANTS c_entity_travel TYPE string VALUE `ZRAP_C_TRAVEL_###`.
    CONSTANTS c_ve_criticality TYPE string VALUE `OVERALLSTATUSCRITICALITY`.

ENDCLASS.


CLASS zcl_rap_trav_ve_### IMPLEMENTATION.

  METHOD if_sadl_exit_calc_element_read~get_calculation_info.
    " called BEFORE the database read: tell SADL which real elements we need
    IF iv_entity <> c_entity_travel.
      RETURN.
    ENDIF.

    LOOP AT it_requested_calc_elements INTO DATA(calc_element).
      CASE calc_element.
        WHEN c_ve_criticality.
          APPEND 'OVERALLSTATUS' TO et_requested_orig_elements.
      ENDCASE.
    ENDLOOP.
  ENDMETHOD.


  METHOD if_sadl_exit_calc_element_read~calculate.
    " called AFTER the database read: fill the virtual element per row
    IF NOT line_exists( it_requested_calc_elements[ table_line = c_ve_criticality ] ).
      RETURN.
    ENDIF.

    DATA travels TYPE STANDARD TABLE OF zrap_c_travel_### WITH DEFAULT KEY.
    travels = CORRESPONDING #( it_original_data ).

    LOOP AT travels ASSIGNING FIELD-SYMBOL(<travel>).
      <travel>-OverallStatusCriticality = SWITCH #( <travel>-OverallStatus
                                            WHEN travel_status-rejected THEN criticality-negative
                                            WHEN travel_status-open     THEN criticality-critical
                                            WHEN travel_status-accepted THEN criticality-positive
                                            ELSE criticality-neutral ).
    ENDLOOP.

    ct_calculated_data = CORRESPONDING #( travels ).
  ENDMETHOD.

ENDCLASS.
```

**클래스 구조 해설**
- `get_calculation_info`: SADL이 **DB를 읽기 전에** 부릅니다. UI가 `OverallStatusCriticality`만 요청해도(`$select`) 계산에 필요한 `OverallStatus`를 함께 읽도록 `et_requested_orig_elements`에 넣어 줍니다. 요소 이름은 **대문자**로 비교합니다.
- `calculate`: SADL이 **DB를 읽은 뒤** 부릅니다. `it_original_data`(읽은 행들)를 받아 `ct_calculated_data`(가상 요소 값이 채워진 행들)를 돌려줍니다. 두 파라미터 모두 일반 타입이라 `CORRESPONDING`으로 C 뷰 타입 테이블에 옮겨 계산합니다.
- 이 클래스는 BDEF와 무관하며 **읽기 전용**입니다. EML `READ ENTITIES`로는 가상 요소가 계산되지 않습니다(OData/SADL 경로에서만).
- critical 값 0~3의 의미(중립/빨강/주황/초록)는 RAP110 정답 클래스의 주석과 같습니다.

</details>

#### 6단계. Travel 메타데이터 확장(UI 레이아웃)

요구사항
1. `ZRAP_C_TRAVEL_###`에 대한 메타데이터 확장(같은 이름)을 만들고 레이어는 `#CUSTOMER`로 하세요.
2. 헤더 정보: 단수 `Travel`, 복수 `Travels`, 제목=TravelID, 부제=Description.
3. 목록 기본 정렬: TravelID 내림차순, 표 형태.
4. 상세(Object Page) 구성:
   - 헤더 영역: 상태(OverallStatus, 색 표시)와 총액(TotalPrice) 두 개의 데이터 포인트
   - 본문 컬렉션 `Travel` 아래: `General Information`(identification), `Dates`(필드 그룹 `DatesGroup`), `Prices`(필드 그룹 `PricesGroup`)
   - 별도 섹션: `Attachment`(필드 그룹 `AttachmentGroup`), `Administrative Data`(필드 그룹 `AdminGroup`), `Bookings`(예약 표)
5. 목록 열: TravelID, AgencyID, CustomerID, BeginDate, EndDate, TotalPrice, OverallStatus(색 표시).
6. 필터 바: TravelID, AgencyID, CustomerID, OverallStatus.
7. 텍스트 표시 방식: AgencyID·CustomerID는 "텍스트 (코드)", OverallStatus는 텍스트만.
8. Description은 여러 줄 입력칸.
9. Attachment는 `Upload a File` 라벨로 첨부 그룹에 보이게.
10. 숨길 요소: AgencyName, CustomerName, OverallStatusText, OverallStatusCriticality, MimeType, FileName, LocalLastChangedBy, LocalLastChangedAt, LastChangedAt. CreatedBy·CreatedAt은 관리 그룹에서만 보이게.

**직접 추가할 어노테이션**
- `@Metadata.layer` — 이 MDE의 우선순위 레이어.
- `@UI.headerInfo` (`typeName`, `typeNamePlural`, `title`, `description`) — 목록 제목·상세 화면 제목/부제.
- `@UI.presentationVariant` (`sortOrder`, `visualizations`) — 목록 기본 정렬과 표시 형태.
- `@UI.facet` (`id`, `purpose: #HEADER/#STANDARD`, `type: #COLLECTION / #IDENTIFICATION_REFERENCE / #FIELDGROUP_REFERENCE / #LINEITEM_REFERENCE / #DATAPOINT_REFERENCE`, `parentId`, `targetQualifier`, `targetElement`, `label`, `position`) — 상세 화면의 섹션 구조.
- `@UI.lineItem` (`position`, `importance`, `criticality`) — 목록 표의 열.
- `@UI.identification` — `IDENTIFICATION_REFERENCE` 섹션에 나오는 필드.
- `@UI.fieldGroup` (`qualifier`, `position`, `label`) — 이름 붙은 필드 묶음.
- `@UI.selectionField` — 필터 바 필드.
- `@UI.dataPoint` (`title`, `criticality`) — 헤더 등에 크게 보이는 핵심 값.
- `@UI.textArrangement` — 코드와 텍스트를 어떤 순서로 보일지.
- `@UI.multiLineText` — 여러 줄 입력칸.
- `@UI.hidden` — UI에서 숨김(OData에는 남음).

**확인**
- 활성화 후(서비스는 11단계) 미리보기에서: 목록 정렬이 TravelID 내림차순, 상태 열이 색으로 표시, 상세 화면 헤더에 상태·총액, 섹션 5개(General/Dates/Prices는 한 컬렉션 안), 예약 표, 첨부 업로드 버튼이 보입니다.

<details><summary>정답·해설</summary>

```cds
@Metadata.layer: #CUSTOMER                                  // MDE 레이어 (→ 어노테이션 탭: @Metadata.layer)
@UI: {
  headerInfo: { typeName: 'Travel',                         // 단수 이름 (→ 어노테이션 탭: @UI.headerInfo)
                typeNamePlural: 'Travels',                  // 목록 제목
                title:       { type: #STANDARD, value: 'TravelID' },     // 상세 제목
                description: { type: #STANDARD, value: 'Description' } },// 상세 부제
  presentationVariant: [ { sortOrder: [ { by: 'TravelID', direction: #DESC } ], // 기본 정렬 (→ 어노테이션 탭: @UI.presentationVariant)
                           visualizations: [ { type: #AS_LINEITEM } ] } ]       // 표로 표시
}
annotate entity ZRAP_C_TRAVEL_### with
{
  @UI.facet: [
    // ----- header area -----
    { id: 'HeaderStatus',  purpose: #HEADER,   type: #DATAPOINT_REFERENCE,   // 헤더 데이터 포인트 (→ 어노테이션 탭: @UI.facet)
      targetQualifier: 'OverallStatus', position: 10 },
    { id: 'HeaderPrice',   purpose: #HEADER,   type: #DATAPOINT_REFERENCE,
      targetQualifier: 'TotalPrice',    position: 20 },
    // ----- body -----
    { id: 'TravelCollection', purpose: #STANDARD, type: #COLLECTION,         // 하위 섹션 묶음
      label: 'Travel', position: 10 },
    { id: 'General',  parentId: 'TravelCollection', purpose: #STANDARD,
      type: #IDENTIFICATION_REFERENCE, label: 'General Information', position: 10 },
    { id: 'Dates',    parentId: 'TravelCollection', purpose: #STANDARD,
      type: #FIELDGROUP_REFERENCE, targetQualifier: 'DatesGroup',  label: 'Dates',  position: 20 },
    { id: 'Prices',   parentId: 'TravelCollection', purpose: #STANDARD,
      type: #FIELDGROUP_REFERENCE, targetQualifier: 'PricesGroup', label: 'Prices', position: 30 },
    { id: 'Attachment', purpose: #STANDARD, type: #FIELDGROUP_REFERENCE,
      targetQualifier: 'AttachmentGroup', label: 'Attachment', position: 20 },
    { id: 'Admin',      purpose: #STANDARD, type: #FIELDGROUP_REFERENCE,
      targetQualifier: 'AdminGroup', label: 'Administrative Data', position: 30 },
    { id: 'Booking',    purpose: #STANDARD, type: #LINEITEM_REFERENCE,      // 자식 표
      targetElement: '_Booking', label: 'Bookings', position: 40 }
  ]

  @UI.lineItem:       [ { position: 10, importance: #HIGH } ]   // 목록 열 (→ 어노테이션 탭: @UI.lineItem)
  @UI.identification: [ { position: 10 } ]                      // General 섹션 (→ 어노테이션 탭: @UI.identification)
  @UI.selectionField: [ { position: 10 } ]                      // 필터 바 (→ 어노테이션 탭: @UI.selectionField)
  TravelID;

  @UI.lineItem:       [ { position: 20, importance: #HIGH } ]
  @UI.identification: [ { position: 20 } ]
  @UI.selectionField: [ { position: 20 } ]
  @UI.textArrangement: #TEXT_FIRST                              // "텍스트 (코드)" (→ 어노테이션 탭: @UI.textArrangement)
  AgencyID;

  @UI.hidden: true                                              // 숨김 (→ 어노테이션 탭: @UI.hidden)
  AgencyName;

  @UI.lineItem:       [ { position: 30, importance: #HIGH } ]
  @UI.identification: [ { position: 30 } ]
  @UI.selectionField: [ { position: 30 } ]
  @UI.textArrangement: #TEXT_FIRST
  CustomerID;

  @UI.hidden: true
  CustomerName;

  @UI.lineItem:   [ { position: 40, importance: #MEDIUM } ]
  @UI.fieldGroup: [ { qualifier: 'DatesGroup', position: 10 } ] // 필드 그룹 (→ 어노테이션 탭: @UI.fieldGroup)
  BeginDate;

  @UI.lineItem:   [ { position: 50, importance: #MEDIUM } ]
  @UI.fieldGroup: [ { qualifier: 'DatesGroup', position: 20 } ]
  EndDate;

  @UI.fieldGroup: [ { qualifier: 'PricesGroup', position: 10 } ]
  BookingFee;

  @UI.lineItem:   [ { position: 60, importance: #HIGH } ]
  @UI.fieldGroup: [ { qualifier: 'PricesGroup', position: 20 } ]
  @UI.dataPoint:  { title: 'Total Price' }                      // 헤더 데이터 포인트 (→ 어노테이션 탭: @UI.dataPoint)
  TotalPrice;

  @UI.fieldGroup: [ { qualifier: 'PricesGroup', position: 30 } ]
  CurrencyCode;

  @UI.identification: [ { position: 40 } ]
  @UI.multiLineText: true                                       // 여러 줄 입력 (→ 어노테이션 탭: @UI.multiLineText)
  Description;

  @UI.lineItem:       [ { position: 70, importance: #HIGH, criticality: 'OverallStatusCriticality' } ] // 색 표시
  @UI.identification: [ { position: 50, criticality: 'OverallStatusCriticality' } ]
  @UI.selectionField: [ { position: 40 } ]
  @UI.dataPoint:      { title: 'Status', criticality: 'OverallStatusCriticality' }
  @UI.textArrangement: #TEXT_ONLY                               // 텍스트만
  OverallStatus;

  @UI.hidden: true
  OverallStatusText;

  @UI.hidden: true
  OverallStatusCriticality;

  @UI.fieldGroup: [ { qualifier: 'AttachmentGroup', position: 10, label: 'Upload a File' } ]
  Attachment;

  @UI.hidden: true
  MimeType;

  @UI.hidden: true
  FileName;

  @UI.fieldGroup: [ { qualifier: 'AdminGroup', position: 10 } ]
  CreatedBy;

  @UI.fieldGroup: [ { qualifier: 'AdminGroup', position: 20 } ]
  CreatedAt;

  @UI.hidden: true
  LocalLastChangedBy;

  @UI.hidden: true
  LocalLastChangedAt;

  @UI.hidden: true
  LastChangedAt;
}
```

**왜 이렇게 쓰나**
- `@UI.facet`은 상세 화면의 **틀**만 정의하고, 각 틀에 무엇이 들어갈지는 요소 쪽 어노테이션이 정합니다.
  - `#IDENTIFICATION_REFERENCE` → `@UI.identification`이 붙은 요소들
  - `#FIELDGROUP_REFERENCE` + `targetQualifier: 'DatesGroup'` → `@UI.fieldGroup: [{ qualifier: 'DatesGroup' }]` 요소들
  - `#LINEITEM_REFERENCE` + `targetElement: '_Booking'` → 자식 엔터티(Booking MDE)의 `@UI.lineItem` 열들
  - `#DATAPOINT_REFERENCE` + `purpose: #HEADER` → 헤더 영역의 `@UI.dataPoint`
  - `#COLLECTION` → 다른 facet들이 `parentId`로 들어가는 묶음
- 헤더 데이터 포인트의 `targetQualifier`에 **요소 이름**(`OverallStatus`, `TotalPrice`)을 쓰고 `@UI.dataPoint`에는 qualifier를 따로 주지 않았습니다. Flight 참조 시나리오(`/DMO/C_BookingSupplement_U`의 `Price`)에서 확인한 패턴입니다.
- `criticality: 'OverallStatusCriticality'`는 값이 아니라 **요소 이름**을 가리킵니다. 그 요소(가상 요소)의 0~3 값으로 색이 정해집니다.
- `@UI.textArrangement`는 4단계의 `@ObjectModel.text.element`가 있어야 효과가 있습니다.
- `@UI.hidden`은 화면에서만 숨길 뿐 OData 응답에는 남습니다. 숨겨도 ETag(`LocalLastChangedAt`)는 계속 동작합니다.
- `selectionVariant`(목록의 미리 정의된 필터 탭)는 로컬 공식 예제에서 확인하지 못해 넣지 않았습니다.

</details>

#### 7단계. Booking 메타데이터 확장

요구사항
1. `ZRAP_C_BOOKING_###` 메타데이터 확장(레이어 `#CUSTOMER`).
2. 헤더 정보: 단수 `Booking`, 복수 `Bookings`, 제목=BookingID, 부제=CarrierName.
3. 정렬: BookingID 오름차순.
4. 상세: 헤더 데이터 포인트 FlightPrice, 섹션 `Booking`(identification), `Flight`(필드 그룹 `FlightGroup`: CarrierID, ConnectionID, FlightDate, FlightPrice, CurrencyCode).
5. 표(Travel 상세의 Bookings 섹션) 열: BookingID, BookingDate, CustomerID, CarrierID, ConnectionID, FlightDate, FlightPrice, BookingStatus.
6. CustomerID·CarrierID는 "텍스트 (코드)", BookingStatus는 텍스트만.
7. 숨길 요소: TravelID(표에서만 제외하고 identification에는 보이기), CustomerName, CarrierName, BookingStatusText, LocalLastChangedAt.

**직접 추가할 어노테이션**
- 6단계와 같은 `@Metadata.layer`, `@UI.headerInfo`, `@UI.presentationVariant`, `@UI.facet`, `@UI.lineItem`, `@UI.identification`, `@UI.fieldGroup`, `@UI.dataPoint`, `@UI.textArrangement`, `@UI.hidden`.

**확인**
- 미리보기에서 Travel 상세 → Bookings 표의 열 순서가 요구사항대로이고, 예약 행을 누르면 Booking 상세가 열립니다.

<details><summary>정답·해설</summary>

```cds
@Metadata.layer: #CUSTOMER
@UI: {
  headerInfo: { typeName: 'Booking',
                typeNamePlural: 'Bookings',
                title:       { type: #STANDARD, value: 'BookingID' },
                description: { type: #STANDARD, value: 'CarrierName' } },
  presentationVariant: [ { sortOrder: [ { by: 'BookingID', direction: #ASC } ],
                           visualizations: [ { type: #AS_LINEITEM } ] } ]
}
annotate entity ZRAP_C_BOOKING_### with
{
  @UI.facet: [
    { id: 'HeaderPrice', purpose: #HEADER, type: #DATAPOINT_REFERENCE,
      targetQualifier: 'FlightPrice', position: 10 },
    { id: 'Booking', purpose: #STANDARD, type: #IDENTIFICATION_REFERENCE,
      label: 'Booking', position: 10 },
    { id: 'Flight',  purpose: #STANDARD, type: #FIELDGROUP_REFERENCE,
      targetQualifier: 'FlightGroup', label: 'Flight', position: 20 }
  ]

  @UI.identification: [ { position: 10 } ]          // 표에는 넣지 않고 상세에만
  TravelID;

  @UI.lineItem:       [ { position: 10, importance: #HIGH } ]
  @UI.identification: [ { position: 20 } ]
  BookingID;

  @UI.lineItem:       [ { position: 20, importance: #MEDIUM } ]
  @UI.identification: [ { position: 30 } ]
  BookingDate;

  @UI.lineItem:       [ { position: 30, importance: #HIGH } ]
  @UI.identification: [ { position: 40 } ]
  @UI.textArrangement: #TEXT_FIRST
  CustomerID;

  @UI.hidden: true
  CustomerName;

  @UI.lineItem:   [ { position: 40, importance: #HIGH } ]
  @UI.fieldGroup: [ { qualifier: 'FlightGroup', position: 10 } ]
  @UI.textArrangement: #TEXT_FIRST
  CarrierID;

  @UI.hidden: true
  CarrierName;

  @UI.lineItem:   [ { position: 50, importance: #HIGH } ]
  @UI.fieldGroup: [ { qualifier: 'FlightGroup', position: 20 } ]
  ConnectionID;

  @UI.lineItem:   [ { position: 60, importance: #HIGH } ]
  @UI.fieldGroup: [ { qualifier: 'FlightGroup', position: 30 } ]
  FlightDate;

  @UI.lineItem:   [ { position: 70, importance: #MEDIUM } ]
  @UI.fieldGroup: [ { qualifier: 'FlightGroup', position: 40 } ]
  @UI.dataPoint:  { title: 'Flight Price' }
  FlightPrice;

  @UI.fieldGroup: [ { qualifier: 'FlightGroup', position: 50 } ]
  CurrencyCode;

  @UI.lineItem:       [ { position: 80, importance: #HIGH } ]
  @UI.identification: [ { position: 50 } ]
  @UI.textArrangement: #TEXT_ONLY
  BookingStatus;

  @UI.hidden: true
  BookingStatusText;

  @UI.hidden: true
  LocalLastChangedAt;
}
```

**왜 이렇게 쓰나**
- Travel MDE의 `#LINEITEM_REFERENCE`(targetElement `_Booking`)는 **Booking MDE의 `@UI.lineItem`**을 표 열로 씁니다. 그래서 자식 표 모양은 자식 MDE에서 정합니다.
- 비행 관련 필드를 `FlightGroup`으로 모아 두면 4단계의 연쇄 값 도움말(항공사 → 노선 → 비행일 → 가격·통화)을 한 화면 묶음에서 확인하기 좋습니다.

</details>

#### 8단계. 기본 BDEF와 draft 테이블

요구사항
1. `ZRAP_R_TRAVEL_###`에서 오른쪽 클릭 → **New Behavior Definition**으로 같은 이름의 BDEF를 만들고(구현 유형 Managed), 아래 내용을 갖추세요.
   - 헤더: 구현 클래스 `ZBP_RAP_R_TRAVEL_###`(unique), `strict ( 2 )`, `with draft`
   - Travel(alias `Travel`): 활성 테이블 `zrap_atrav_###`, draft 테이블 `zrap_dtrav_###`, 인스턴스 ETag=`LocalLastChangedAt`, `lock master`, total ETag=`LastChangedAt`, 전역 권한 `authorization master ( global )`, `late numbering`
   - Travel 필드: TravelID와 관리 필드 5개(CreatedBy, CreatedAt, LocalLastChangedBy, LocalLastChangedAt, LastChangedAt)는 읽기 전용
   - Travel 연산: create, update, delete, `_Booking`으로 자식 생성(draft 포함)
   - draft 액션: Edit, Activate(optimized), Discard, Resume, Prepare(지금은 검증 없음)
   - 테이블 필드 매핑(CDS 별칭 ↔ 테이블 필드)
   - Booking(alias `Booking`): 활성 `zrap_abook_###`, draft `zrap_dbook_###`, ETag=`LocalLastChangedAt`, 잠금·권한은 `_Travel`에 의존, `late numbering`, TravelID·BookingID·LocalLastChangedAt 읽기 전용, update, delete, `_Travel` 연관(draft 포함), 매핑
2. 저장하면 draft 테이블이 없다는 오류가 납니다. `draft table zrap_dtrav_###`에 커서를 두고 **Ctrl+1 → Create draft table** 퀵 픽스로 테이블을 생성·활성화하세요. `zrap_dbook_###`도 같은 방법으로 만드세요.
3. 생성된 draft 테이블 정의를 열어 `DRAFTUUID`, `PARENTDRAFTUUID`(Booking), `"%admin"` include가 있는지 확인하세요.
4. BDEF를 활성화하세요. (행동 풀 클래스가 없다는 오류는 9단계에서 해결합니다.)

**확인**
- 두 draft 테이블이 활성화되어 있고, 아래 정답의 필드 표와 같은 구조입니다.
- BDEF에 남은 오류가 "구현 클래스 `ZBP_RAP_R_TRAVEL_###`가 없다"뿐입니다.

<details><summary>정답·해설</summary>

```bdef
managed implementation in class zbp_rap_r_travel_### unique; // 행동 풀(late numbering 때문에 헤더에 지정)
strict ( 2 );                                                // 최신 엄격 문법 검사
with draft;                                                  // BO 전체 draft 사용

define behavior for ZRAP_R_TRAVEL_### alias Travel
persistent table zrap_atrav_###          // 활성 데이터 저장 테이블
draft table zrap_dtrav_###               // draft 데이터 저장 테이블
etag master LocalLastChangedAt           // 인스턴스 ETag(낙관적 잠금, OData If-Match)
lock master total etag LastChangedAt     // 루트가 잠금 주체 + draft Resume 판단용 total ETag
authorization master ( global )          // 전역 권한 확인(9단계 메서드)
late numbering                           // 키는 저장 직전 adjust_numbers에서
{
  field ( readonly ) TravelID;                                   // late numbering 키
  field ( readonly ) CreatedBy, CreatedAt, LocalLastChangedBy,
                     LocalLastChangedAt, LastChangedAt;          // 프레임워크가 채우는 관리 필드

  create;
  update;
  delete;

  association _Booking { create; with draft; }   // 부모를 통해 자식 생성, draft에서도

  draft action Edit;                // 활성 → draft 편집 시작
  draft action Activate optimized;  // draft → 활성 저장
  draft action Discard;             // draft 버리기
  draft action Resume;              // 잠금 만료된 draft 다시 열기
  draft determine action Prepare;   // Activate 전 검증 묶음(R-02에서 검증 추가)

  mapping for zrap_atrav_###
    {
      TravelID           = travel_id;
      AgencyID           = agency_id;
      CustomerID         = customer_id;
      BeginDate          = begin_date;
      EndDate            = end_date;
      BookingFee         = booking_fee;
      TotalPrice         = total_price;
      CurrencyCode       = currency_code;
      Description        = description;
      OverallStatus      = overall_status;
      Attachment         = attachment;
      MimeType           = mime_type;
      FileName           = file_name;
      CreatedBy          = created_by;
      CreatedAt          = created_at;
      LocalLastChangedBy = local_last_changed_by;
      LocalLastChangedAt = local_last_changed_at;
      LastChangedAt      = last_changed_at;
    }
}

define behavior for ZRAP_R_BOOKING_### alias Booking
persistent table zrap_abook_###
draft table zrap_dbook_###
etag master LocalLastChangedAt
lock dependent by _Travel                // 잠금은 부모 Travel이 대신
authorization dependent by _Travel       // 권한도 부모 Travel이 대신
late numbering
{
  field ( readonly ) TravelID, BookingID, LocalLastChangedAt;

  update;
  delete;

  association _Travel { with draft; }

  mapping for zrap_abook_###
    {
      TravelID           = travel_id;
      BookingID          = booking_id;
      BookingDate        = booking_date;
      CustomerID         = customer_id;
      CarrierID          = carrier_id;
      ConnectionID       = connection_id;
      FlightDate         = flight_date;
      FlightPrice        = flight_price;
      CurrencyCode       = currency_code;
      BookingStatus      = booking_status;
      LocalLastChangedAt = local_last_changed_at;
    }
}
```

퀵 픽스로 만들어지는 draft 테이블(시스템 버전에 따라 헤더 어노테이션 값이나 필드 순서가 조금 다를 수 있습니다. 실제 시스템에서 확인 필요):

```cds
@EndUserText.label : 'Draft table for entity ZRAP_R_TRAVEL_###'
@AbapCatalog.enhancement.category : #EXTENSIBLE_ANY
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_dtrav_### {

  key mandt          : mandt not null;
  key travelid       : /dmo/travel_id not null;
  key draftuuid      : sdraft_uuid not null;          // late numbering이라 필요한 draft 키
  agencyid           : /dmo/agency_id;
  customerid         : /dmo/customer_id;
  begindate          : /dmo/begin_date;
  enddate            : /dmo/end_date;
  @Semantics.amount.currencyCode : 'zrap_dtrav_###.currencycode'
  bookingfee         : /dmo/booking_fee;
  @Semantics.amount.currencyCode : 'zrap_dtrav_###.currencycode'
  totalprice         : /dmo/total_price;
  currencycode       : /dmo/currency_code;
  description        : /dmo/description;
  overallstatus      : /dmo/overall_status;
  attachment         : /dmo/attachment;
  mimetype           : /dmo/mime_type;
  filename           : /dmo/filename;
  createdby          : abp_creation_user;
  createdat          : abp_creation_tstmpl;
  locallastchangedby : abp_locinst_lastchange_user;
  locallastchangedat : abp_locinst_lastchange_tstmpl;
  lastchangedat      : abp_lastchange_tstmpl;
  "%admin"           : include sych_bdl_draft_admin_inc;   // draft 관리 정보

}
```

```cds
@EndUserText.label : 'Draft table for entity ZRAP_R_BOOKING_###'
@AbapCatalog.enhancement.category : #EXTENSIBLE_ANY
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_dbook_### {

  key mandt          : mandt not null;
  key travelid       : /dmo/travel_id not null;
  key bookingid      : /dmo/booking_id not null;
  key draftuuid      : sdraft_uuid not null;          // 이 draft 행 자신의 키
  parentdraftuuid    : sdraft_uuid;                   // 부모 Travel draft의 DRAFTUUID
  bookingdate        : /dmo/booking_date;
  customerid         : /dmo/customer_id;
  carrierid          : /dmo/carrier_id;
  connectionid       : /dmo/connection_id;
  flightdate         : /dmo/flight_date;
  @Semantics.amount.currencyCode : 'zrap_dbook_###.currencycode'
  flightprice        : /dmo/flight_price;
  currencycode       : /dmo/currency_code;
  bookingstatus      : /dmo/booking_status;
  locallastchangedat : abp_locinst_lastchange_tstmpl;
  "%admin"           : include sych_bdl_draft_admin_inc;

}
```

`ZRAP_DTRAV_###` 필드 표

| 필드 | 키 | 데이터 엘리먼트 | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| mandt | ✓ | mandt | CLNT | 3 | 0 | 클라이언트 |
| travelid | ✓ | /dmo/travel_id | NUMC | 8 | 0 | 새 draft에서는 빈 값 |
| draftuuid | ✓ | sdraft_uuid | RAW | 16 | 0 | draft 인스턴스 키 |
| agencyid ~ lastchangedat | | (활성 테이블과 같은 데이터 엘리먼트) | | | | CDS 별칭과 같은 이름(밑줄 없음) |
| "%admin" | | include sych_bdl_draft_admin_inc | | | | draft 관리 정보(소유자, 변경 시각 등) |

`ZRAP_DBOOK_###` 필드 표

| 필드 | 키 | 데이터 엘리먼트 | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| mandt | ✓ | mandt | CLNT | 3 | 0 | 클라이언트 |
| travelid | ✓ | /dmo/travel_id | NUMC | 8 | 0 | |
| bookingid | ✓ | /dmo/booking_id | NUMC | 4 | 0 | 새 draft에서는 빈 값 |
| draftuuid | ✓ | sdraft_uuid | RAW | 16 | 0 | draft 인스턴스 키 |
| parentdraftuuid | | sdraft_uuid | RAW | 16 | 0 | 부모 draft 연결 |
| bookingdate ~ locallastchangedat | | (활성 테이블과 같은 데이터 엘리먼트) | | | | |
| "%admin" | | include sych_bdl_draft_admin_inc | | | | draft 관리 정보 |

**왜 이렇게 쓰나**
- **late numbering + draft에서 `DRAFTUUID`가 필요한 이유**: late numbering에서는 TravelID/BookingID가 Activate(저장) 직전까지 비어 있습니다. 그런데 draft 행은 그 전부터 DB에 저장되어야 하므로, 비어 있는 업무 키 대신 행을 구별할 UUID 키(`DRAFTUUID`)가 필요합니다. 자식 draft는 어느 부모 draft에 속하는지 `PARENTDRAFTUUID`로 연결합니다(RAP110 연습 3의 설명과 같은 내용).
- draft 테이블 필드 이름은 **CDS 별칭**(밑줄 없는 TravelID → travelid)과 같아야 하므로 mapping이 필요 없습니다. 그래서 직접 만들기보다 퀵 픽스로 만드는 것이 안전합니다. 나중에 CDS에 필드를 추가하면 퀵 픽스 "Recreate draft table"로 다시 맞추세요.
- `lock master total etag LastChangedAt`: draft BO에서는 total ETag가 필수입니다. 편집 중 잠금이 만료된 뒤 Resume할 때 활성 데이터가 그 사이 바뀌었는지를 이 값으로 비교합니다. 인스턴스 ETag(`etag master LocalLastChangedAt`)와 다른 필드를 쓰세요.
- `late numbering`을 쓰면 `adjust_numbers`를 구현할 행동 풀이 필요하므로, 구현 클래스를 엔터티가 아니라 **헤더**(`managed implementation in class ... unique`)에 지정했습니다(RAP110 연습 3.2.1). 세이버 클래스는 BO 전체에 하나입니다.
- `draft determine action Prepare;`: Activate 직전에 실행될 검증 목록입니다. 지금은 검증이 없으므로 비워 두고, R-02에서 `{ validation ...; }`를 채웁니다.
- `Activate optimized`: 변경이 없는 draft 자식 등에 대해 불필요한 처리를 줄이는 최적화 옵션입니다(cheat sheet BDEF 예제와 RF `/DMO/R_Travel_D`에서 사용).
- Booking의 구현 클래스(`ZBP_RAP_R_BOOKING_###`)는 아직 구현할 메서드가 없어 지정하지 않았습니다. R-02에서 Booking 검증·결정을 추가할 때 `implementation in class zbp_rap_r_booking_### unique`를 붙입니다.

**자주 나는 오류와 해결**
- draft 테이블에 `DRAFTUUID`/`PARENTDRAFTUUID`가 없다는 오류: draft 테이블을 late numbering 지정 **전에** 만든 경우입니다. 퀵 픽스 "Recreate draft table"로 다시 만드세요(RAP110 연습 3.1 3~5번).
- total ETag 필드의 `@Semantics.systemDateTime.lastChangedAt`이 없으면 관리형 BO가 값을 자동으로 채우지 못합니다. 3단계 어노테이션을 확인하세요.

</details>

#### 9단계. 행동 풀: 전역 권한과 adjust_numbers

요구사항
1. BDEF 첫 줄의 `zbp_rap_r_travel_###`에 커서를 두고 Ctrl+1 → 클래스 생성 퀵 픽스로 행동 풀을 만드세요.
2. Local Types 탭에 다음을 구현하세요.
   - 핸들러 `lhc_travel`: `get_global_authorizations` — 지금은 요청된 create/update/delete/Edit를 모두 **허용**으로 돌려줍니다(실제 권한 확인은 뒤 문제에서 교체).
   - 세이버 `lsc_zrap_r_travel_###`: `adjust_numbers`만 재정의.
3. `adjust_numbers` 규칙
   - Travel: 활성 테이블의 `MAX( travel_id )` + 1부터 차례로 부여.
   - Booking: 우선 각 예약의 TravelID를 정합니다. 기존 여행에 추가된 예약은 `%tmp-TravelID`에 이미 값이 있고, 새 여행과 함께 만든 예약은 `READ ENTITIES ... BY \_Travel ... LINK`로 부모의 `%pid`를 찾아 `mapped-travel`에서 방금 매긴 TravelID를 가져옵니다.
   - 그다음 여행별로 기존 `MAX( booking_id )` + 10씩 부여. 여행별 최대값은 **SELECT 한 번**(`GROUP BY travel_id`)으로 가져오고, 루프 안 SELECT는 하지 마세요.
4. R-02·R-03·R-04에서 이 클래스에 메서드가 늘어납니다. 지금은 위 두 개만 두세요.

**확인**
- 행동 풀과 BDEF가 모두 활성화됩니다.
- 11단계 미리보기에서 새 여행을 만들 때 TravelID가 비어 있다가, **Create(저장)를 누른 뒤** 번호가 생깁니다. 새 예약 번호는 기존 최대 + 10입니다.

<details><summary>정답·해설</summary>

전역 클래스(퀵 픽스가 만든 그대로):

```abap
CLASS zbp_rap_r_travel_### DEFINITION
  PUBLIC
  ABSTRACT
  FINAL
  FOR BEHAVIOR OF zrap_r_travel_###.
ENDCLASS.


CLASS zbp_rap_r_travel_### IMPLEMENTATION.
ENDCLASS.
```

Local Types:

```abap
**********************************************************************
* Handler: Travel
**********************************************************************
CLASS lhc_travel DEFINITION INHERITING FROM cl_abap_behavior_handler.

  PRIVATE SECTION.
    METHODS get_global_authorizations FOR GLOBAL AUTHORIZATION
      IMPORTING REQUEST requested_authorizations FOR Travel RESULT result.

ENDCLASS.


CLASS lhc_travel IMPLEMENTATION.

  METHOD get_global_authorizations.
    " R-01: allow everything that is requested.
    " Real checks (AUTHORITY-CHECK, messages) replace this later.
    IF requested_authorizations-%create = if_abap_behv=>mk-on.
      result-%create = if_abap_behv=>auth-allowed.
    ENDIF.

    IF requested_authorizations-%update = if_abap_behv=>mk-on.
      result-%update = if_abap_behv=>auth-allowed.
    ENDIF.

    IF requested_authorizations-%delete = if_abap_behv=>mk-on.
      result-%delete = if_abap_behv=>auth-allowed.
    ENDIF.

    " draft action Edit is authorized like update
    IF requested_authorizations-%action-Edit = if_abap_behv=>mk-on.
      result-%action-Edit = if_abap_behv=>auth-allowed.
    ENDIF.
  ENDMETHOD.

ENDCLASS.


**********************************************************************
* Saver: whole BO (late numbering)
**********************************************************************
CLASS lsc_zrap_r_travel_### DEFINITION INHERITING FROM cl_abap_behavior_saver.

  PROTECTED SECTION.
    METHODS adjust_numbers REDEFINITION.

  PRIVATE SECTION.
    TYPES:
      BEGIN OF ty_max_booking,
        travel_id      TYPE /dmo/travel_id,
        max_booking_id TYPE /dmo/booking_id,
      END OF ty_max_booking.

ENDCLASS.


CLASS lsc_zrap_r_travel_### IMPLEMENTATION.

  METHOD adjust_numbers.

    "--------------------------------------------------------------
    " 1) Travel: next number = MAX( travel_id ) + 1
    "--------------------------------------------------------------
    IF mapped-travel IS NOT INITIAL.
      SELECT SINGLE FROM zrap_atrav_###
        FIELDS MAX( travel_id )
        INTO @DATA(max_travel_id).

      LOOP AT mapped-travel ASSIGNING FIELD-SYMBOL(<travel>).
        max_travel_id += 1.
        <travel>-TravelID = max_travel_id.
      ENDLOOP.
    ENDIF.

    "--------------------------------------------------------------
    " 2) Booking
    "--------------------------------------------------------------
    IF mapped-booking IS NOT INITIAL.

      " 2a) parent of bookings created together with a NEW travel
      READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
        ENTITY Booking BY \_Travel
          FROM VALUE #( FOR booking IN mapped-booking WHERE ( %tmp-TravelID IS INITIAL )
                        ( %pid = booking-%pid
                          %key = booking-%tmp ) )
        LINK DATA(booking_to_travel_links).

      " 2b) final TravelID of every new booking
      LOOP AT mapped-booking ASSIGNING FIELD-SYMBOL(<booking>).
        <booking>-TravelID =
          COND #( WHEN <booking>-%tmp-TravelID IS INITIAL
                  THEN mapped-travel[ %pid = booking_to_travel_links[ source-%pid = <booking>-%pid ]-target-%pid ]-TravelID
                  ELSE <booking>-%tmp-TravelID ).
      ENDLOOP.

      " 2c) current max booking id per travel - one SELECT
      DATA travel_id_range TYPE RANGE OF /dmo/travel_id.
      travel_id_range = VALUE #( FOR GROUPS travel_key OF b IN mapped-booking
                                   GROUP BY b-TravelID
                                   ( sign = 'I' option = 'EQ' low = travel_key ) ).

      DATA max_bookings TYPE HASHED TABLE OF ty_max_booking WITH UNIQUE KEY travel_id.
      SELECT FROM zrap_abook_###
        FIELDS travel_id,
               MAX( booking_id ) AS max_booking_id
        WHERE travel_id IN @travel_id_range
        GROUP BY travel_id
        INTO TABLE @max_bookings.

      " 2d) number per travel in steps of 10
      LOOP AT mapped-booking ASSIGNING <booking>
           GROUP BY <booking>-TravelID INTO DATA(travel_group).

        DATA(max_booking_id) = VALUE /dmo/booking_id(
                                 max_bookings[ travel_id = travel_group ]-max_booking_id OPTIONAL ).

        LOOP AT GROUP travel_group ASSIGNING FIELD-SYMBOL(<booking_in_group>).
          max_booking_id += 10.
          <booking_in_group>-BookingID = max_booking_id.
        ENDLOOP.
      ENDLOOP.

    ENDIF.

  ENDMETHOD.

ENDCLASS.
```

**클래스 구조 해설**
- `get_global_authorizations FOR GLOBAL AUTHORIZATION`: BDEF의 `authorization master ( global )` 줄에서 생깁니다. 파생 타입 `requested_authorizations`에는 요청된 연산(`%create`, `%update`, `%delete`, `%action-Edit` 등) 표시가, `result`에는 같은 구조로 허용/거부(`if_abap_behv=>auth-allowed / auth-unauthorized`)를 넣습니다. 프레임워크는 **인스턴스를 읽기 전에** 이 메서드를 불러 버튼 표시(Create/Edit/Delete)와 실제 연산 허용을 정합니다. 여기서는 값을 명시적으로 `auth-allowed`로 채웠습니다.
- draft BO에서 `Edit`은 별도 액션이므로 `%action-Edit`도 함께 허용해야 상세 화면에 Edit 버튼이 나옵니다(RF `/DMO/BP_TRAVEL_D`도 Edit을 update처럼 처리).
- `adjust_numbers`: BDEF의 `late numbering`에서 필요해지는 세이버 메서드입니다. 저장 시퀀스에서 `finalize` → `check_before_save` **뒤**, `save` **앞**에 한 번 호출됩니다. 이 시점은 "더 이상 실패할 수 없는 지점" 이후라서 여기서 번호를 받아도 버려지는 번호가 생기지 않습니다.
  - `mapped-travel` / `mapped-booking`: 이번 저장에서 새로 만들어진 인스턴스 목록입니다. `%pid`(임시 ID)와 `%tmp`(사용자에게 보였던 임시 키)가 들어 있고, 우리가 최종 키(`TravelID`, `BookingID`)를 채워 돌려줍니다. 프레임워크는 이 값으로 활성 테이블에 INSERT 합니다.
  - `READ ENTITIES ... BY \_Travel ... LINK`: 새 여행과 새 예약을 함께 만든 경우 예약의 `%tmp-TravelID`가 비어 있으므로, 연관을 따라 부모의 `%pid`를 찾고, 그 `%pid`로 방금 매긴 TravelID를 `mapped-travel`에서 가져옵니다. 이미 있는 여행에 예약만 추가한 경우는 `%tmp-TravelID`에 기존 번호가 들어 있습니다.
  - 예약 번호는 RAP110처럼 여행별 최대값 + 10이지만, RAP110이 그룹 루프 안에서 SELECT 하던 부분을 **SELECT 한 번(GROUP BY)**과 해시 테이블 조회로 바꿨습니다.
- `MAX( travel_id )` 방식의 한계: 두 사용자가 동시에 저장하면 같은 번호를 받을 수 있습니다. 실무에서는 RAP110처럼 번호 범위 객체(`cl_numberrange_runtime=>number_get`)를 씁니다. 이 문제집에서는 번호 범위 객체를 만들 필요가 없도록 SELECT MAX를 썼습니다.
- R-02 이후 이 행동 풀에 검증·결정·액션 메서드가 추가되어도 `adjust_numbers`는 그대로 둡니다.

**자주 나는 오류와 해결**
- `adjust_numbers`에서 `mapped-travel[ %pid = ... ]` 줄이 덤프(ITAB_LINE_NOT_FOUND)를 낸다면, 예약을 부모 없이 만든 경우입니다. UI에서는 생기지 않으며, EML 테스트 시 `CREATE BY \_Booking`을 같은 요청에서 `%cid_ref`로 부모와 연결했는지 확인하세요.

</details>

#### 10단계. 프로젝션 BDEF

요구사항
1. `ZRAP_C_TRAVEL_###` 오른쪽 클릭 → New Behavior Definition(구현 유형 Projection).
2. `strict ( 2 )`, `use draft`.
3. Travel: ETag 사용, create/update/delete, draft 액션 5개(Edit, Activate, Discard, Resume, Prepare), `_Booking` 자식 생성(draft 포함)을 노출.
4. Booking: ETag 사용, update/delete, `_Travel` 연관(draft 포함) 노출.

**확인**
- 활성화 성공. 기본 BDEF에 없는 연산을 `use`하면 오류가 나는지 한 줄 넣어 확인해 보세요(예: Booking에 `use create;` → 오류, 확인 뒤 삭제).

<details><summary>정답·해설</summary>

```bdef
projection;          // 기본 BDEF 위에 얹는 프로젝션
strict ( 2 );
use draft;           // 기본 BO의 draft 기능을 이 서비스에서도 사용

define behavior for ZRAP_C_TRAVEL_### alias Travel
use etag             // 기본 BDEF의 etag master를 OData ETag로 사용
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

define behavior for ZRAP_C_BOOKING_### alias Booking
use etag
{
  use update;
  use delete;

  use association _Travel { with draft; }
}
```

**왜 이렇게 쓰나**
- 프로젝션 BDEF는 기본 BO의 행동 중 **이 서비스에 공개할 것만** 고릅니다. 같은 기본 BO 위에 "관리자용"(삭제 가능)과 "조회용"(update만) 프로젝션을 따로 둘 수 있습니다.
- `use draft`를 빼면 draft 액션을 `use`할 수 없고, Fiori 앱은 draft 없이 바로 저장하는 방식이 됩니다.
- `use etag`가 있어야 OData 응답에 ETag가 실리고, 수정 요청에서 `If-Match`로 동시 변경을 막습니다.

</details>

#### 11단계. 서비스 정의·바인딩·Fiori 미리보기

요구사항
1. `ZRAP_C_TRAVEL_###` 오른쪽 클릭 → New Service Definition `ZRAP_UI_TRAVEL_###`. 대표 엔터티는 Travel 프로젝션입니다.
2. 노출할 엔터티와 별칭: `ZRAP_C_TRAVEL_###` as `Travel`, `ZRAP_C_BOOKING_###` as `Booking`, 그리고 사용한 값 도움말 뷰 `/DMO/I_Agency_StdVH` as `Agency`, `/DMO/I_Customer_StdVH` as `Customer`, `/DMO/I_Carrier_StdVH` as `Carrier`, `/DMO/I_Connection_StdVH` as `Connection`, `/DMO/I_Flight_StdVH` as `Flight`, `/DMO/I_Overall_Status_VH` as `OverallStatus`, `/DMO/I_Booking_Status_VH` as `BookingStatus`, `I_CurrencyStdVH` as `Currency`.
3. 서비스 정의 오른쪽 클릭 → New Service Binding `ZRAP_UI_TRAVEL_O4_###`, 바인딩 유형 **OData V4 - UI**. 활성화 후 **Publish**.
4. 엔터티 셋 `Travel` 선택 → **Preview**로 Fiori elements 앱을 여세요.
5. 다음을 직접 해 보세요.
   - 목록: Go, 필터 바(AgencyID 값 도움말), 검색창에 여행 번호 일부 입력
   - 상세: 헤더 상태 색, 섹션 구성, 첨부 파일 업로드 후 다운로드
   - Create → 값 입력(여행사·고객 F4, 잘못된 통화 입력 시 즉시 오류) → Bookings에서 예약 추가(항공사 → 노선 → 비행일 순서로 F4, 비행일 선택 시 가격·통화 자동 입력) → Create(저장) → TravelID/BookingID가 생겼는지 확인
   - 기존 여행 Edit → 값 변경 → 브라우저 탭 닫기 → 다시 열어 draft("Unsaved Changes")가 남아 있는지 확인 → Discard
   - Delete

**직접 추가할 어노테이션**
- `@EndUserText.label` — 서비스 설명.
- `@ObjectModel.leadingEntity.name` — 서비스의 대표(시작) 엔터티.

**확인**
- 바인딩 화면에 Service URL과 엔터티 셋 목록이 보이고, 미리보기에서 위 동작이 모두 됩니다.
- 저장 후 Data Preview(`ZRAP_ATRAV_###`)에 새 행이 있고 `created_by`, `created_at`, `last_changed_at`이 채워져 있습니다(관리형 BO의 자동 기입).

<details><summary>정답·해설</summary>

```cds
@EndUserText.label: 'Travel UI service'                      // 설명
@ObjectModel.leadingEntity.name: 'ZRAP_C_TRAVEL_###'         // 대표 엔터티 (→ 어노테이션 탭: @ObjectModel.leadingEntity.name)
define service ZRAP_UI_TRAVEL_### {
  expose ZRAP_C_TRAVEL_###        as Travel;
  expose ZRAP_C_BOOKING_###       as Booking;
  // value help entities used in the projections
  expose /DMO/I_Agency_StdVH      as Agency;
  expose /DMO/I_Customer_StdVH    as Customer;
  expose /DMO/I_Carrier_StdVH     as Carrier;
  expose /DMO/I_Connection_StdVH  as Connection;
  expose /DMO/I_Flight_StdVH      as Flight;
  expose /DMO/I_Overall_Status_VH as OverallStatus;
  expose /DMO/I_Booking_Status_VH as BookingStatus;
  expose I_CurrencyStdVH          as Currency;
}
```

서비스 바인딩 만들기(코드 없음, 마법사):

| 항목 | 값 |
|---|---|
| Name | `ZRAP_UI_TRAVEL_O4_###` |
| Description | `Travel UI service - OData V4` |
| Binding Type | `OData V4 - UI` |
| Service Definition | `ZRAP_UI_TRAVEL_###` |

활성화 → **Publish**(로컬 서비스 엔드포인트 게시) → 엔터티 셋 `Travel` 선택 → **Preview**.

**왜 이렇게 쓰나**
- 서비스 정의는 "무엇을" 노출할지(엔터티 목록·별칭), 서비스 바인딩은 "어떻게"(프로토콜·용도) 노출할지 정합니다. 같은 서비스 정의로 바인딩을 여러 개 만들 수 있습니다.
- 값 도움말 뷰를 서비스에 노출해 두어야 F4 요청이 같은 서비스 안에서 처리됩니다(Flight 참조 시나리오의 `/DMO/UI_TRAVEL_A_D`도 값 도움말 뷰를 모두 노출합니다).
- **OData V2 vs V4**
  - V4: 최신 프로토콜. draft가 있는 RAP BO의 Fiori elements 앱은 V4를 권장합니다. 이 문제집은 V4를 씁니다.
  - V2: 오래된 앱·도구 호환용. 새로 만드는 앱에서는 쓸 이유가 적습니다.
- **UI vs Web API**
  - UI 바인딩: `@UI.*` 어노테이션, 값 도움말 등 화면용 메타데이터가 함께 나가며 Fiori elements 미리보기를 쓸 수 있습니다.
  - Web API 바인딩: 시스템 간(A2A) 호출용입니다. UI 메타데이터 없이 데이터와 연산만 노출하며 미리보기가 없습니다. 뒤 문제에서 같은 서비스 정의로 `ZRAP_API_TRAVEL_O4_###`를 만듭니다.
- 미리보기에서 저장 전 TravelID가 비어 있는 것은 late numbering 때문입니다. 저장(Activate) 순간 `adjust_numbers`가 번호를 매깁니다.
- 탭을 닫아도 draft가 남는 이유: draft는 DB(draft 테이블)에 저장되므로 세션이 끝나도 사라지지 않습니다. 다른 사용자는 그동안 같은 여행을 편집할 수 없습니다(배타 잠금 기간).

**자주 나는 오류와 해결**
- Publish가 회색이면 서비스 정의·바인딩이 활성화되지 않은 상태입니다. 둘 다 활성화하세요.
- 미리보기가 "Unauthorized" 또는 빈 화면이면 브라우저에서 BTP 계정으로 다시 로그인하세요.
- 저장 시 "draft 테이블 구조가 맞지 않다"는 오류가 나면 CDS에 필드를 추가한 뒤 draft 테이블을 다시 만들지 않은 경우입니다. 8단계 퀵 픽스 "Recreate draft table"을 실행하세요.

</details>

## 출처
- SAP-samples/abap-platform-rap110 — `src/zrap110_r_traveltp_sol.ddls.asddls`, `zrap110_r_bookingtp_sol.ddls.asddls`, `zrap110_c_traveltp_sol.ddls.asddls`, `zrap110_c_bookingtp_sol.ddls.asddls`, `zrap110_c_traveltp_sol.ddlx.asddlxs`, `zrap110_c_bookingtp_sol.ddlx.asddlxs`, `zrap110_r_traveltp_sol.bdef.asbdef`, `zrap110_c_traveltp_sol.bdef.asbdef`, `zrap110_ui_travel_sol.srvd.srvdsrv`, `zrap110_calc_trav_elem_sol.clas.abap`, `zrap110_bp_traveltp_sol.clas.abap`, `zrap110_bp_traveltp_sol.clas.locals_imp.abap`, `zrap110_atravsol.tabl.xml`, `zrap110_abooksol.tabl.xml`, `zrap110_dtravsol.tabl.xml`, `zrap110_dbooksol.tabl.xml`: https://github.com/SAP-samples/abap-platform-rap110/tree/main/src
- SAP-samples/abap-platform-rap110 — 연습 1~5 README: https://github.com/SAP-samples/abap-platform-rap110/tree/main/exercises (ex01, ex02, ex03, ex04, ex05)
- SAP-samples/abap-platform-refscen-flight (ABAP-platform-cloud 브랜치) — `src/draft/`(`/DMO/R_Travel_D` CDS·BDEF, `/DMO/C_Travel_A_D`, `/DMO/C_Booking_A_D` CDS·MDE, `/DMO/UI_TRAVEL_A_D`, `/DMO/BP_TRAVEL_D` 권한 메서드, `/DMO/CL_DATA_GENERATOR_DRAFT`), `src/legacy/`(`/DMO/TRAVEL`, `/DMO/BOOKING`, include 구조, 데이터 엘리먼트·도메인), `src/reuse/`(`/DMO/I_*_StdVH`, `/DMO/I_Overall_Status_VH`, `/DMO/I_Booking_Status_VH`, 상태 도메인), `src/readonly/`(`/DMO/C_Flight_R` MDE: fieldGroup·COLLECTION facet), `src/unmanaged/`(`/DMO/C_BookingSupplement_U` MDE: 헤더 DATAPOINT_REFERENCE), `src/reuse/agency/rev/`(multiLineText, dataPoint): https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud
- SAP-samples/abap-platform-rap100 — `src/zcl_rap100_gen_data_sol.clas.abap`, `exercises/ex01/README.md`(테이블 정의, 바인딩 유형): https://github.com/SAP-samples/abap-platform-rap100
- SAP-samples/abap-platform-rap-workshops — `src/z_onlineshop_000/zc_onlineshop_000.ddlx.asddlxs`(headerInfo.description, multiLineText): https://github.com/SAP-samples/abap-platform-rap-workshops
- SAP-samples/abap-cheat-sheets — `15_CDS_View_Entities.md`, `26_ABAP_Dictionary.md`(테이블 정의 문법), `36_RAP_Behavior_Definition_Language.md`(draft table·`%admin`·DRAFTUUID, ETag, late numbering, BDEF 예제): https://github.com/SAP-samples/abap-cheat-sheets
