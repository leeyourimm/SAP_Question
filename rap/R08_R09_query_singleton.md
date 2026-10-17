## 3. 특수 BO 패턴

### R-08. Custom Entity와 Unmanaged Query: 직접 조회 로직 쓰기 [작성] ★★★
<!-- covers: define custom entity, @ObjectModel.query.implementedBy, if_rap_query_provider~select, is_data_requested, is_total_numb_of_rec_requested, get_paging, if_rap_query_paging=>page_size_unlimited, get_sort_elements, get_filter get_as_ranges, get_as_sql_string, cx_rap_query_filter_no_range, get_search_expression, get_requested_elements, set_total_number_of_records, set_data, SELECT FROM @itab, abap_sortorder_tab, @UI.dataPoint #PROGRESS, criticality, @Search.searchable, value help custom entity, additionalBinding, ABAP Unit cl_osql_test_environment, read-only 모델 비교 -->

**목표**
- 데이터베이스 뷰로는 표현하기 어려운 계산(좌석 이용률, 신호등 색)을 ABAP 코드로 만들어 OData 엔터티로 내보내는 **custom entity + unmanaged query**를 직접 만들 수 있습니다.
- `if_rap_query_provider~select` 안에서 요청 객체(`io_request`)가 주는 정보(데이터 요청 여부, 건수 요청 여부, 필터, 검색, 정렬, 페이징, 요청 필드)를 하나도 빠짐없이 처리할 수 있습니다.
- 필터를 range로 받는 방법(`get_as_ranges`)과 SQL 문자열로 받는 방법(`get_as_sql_string`)의 장단점과 SQL 인젝션 관점의 차이를 설명할 수 있습니다.
- custom entity 하나만으로 List Report + Object Page(텍스트, 신호등, 진행 막대, 값 도움말)를 만들 수 있습니다.
- 조회 로직을 테스트하기 쉬운 메서드로 나누고 ABAP Unit(SQL 테스트 더블)으로 검증할 수 있습니다.
- view entity / custom entity / table function 중 언제 무엇을 쓰는지 판단할 수 있습니다.

**전제**
- 패키지 `ZRAP_###`가 있고, 트라이얼 시스템에 ABAP Flight Reference Scenario 데이터(`/DMO/FLIGHT`, `/DMO/CONNECTION`, `/DMO/CARRIER`)가 들어 있어야 합니다. 비어 있으면 표준 클래스 `/DMO/CL_FLIGHT_DATA_GENERATOR`를 F9로 실행해 채우세요(트라이얼에는 보통 이미 들어 있습니다).
- 10단계(심화)만 R-01의 Booking(`ZRAP_R_BOOKING_###`, `ZRAP_C_BOOKING_###`)을 사용합니다.
- custom entity는 **트랜잭션(BDEF)이 없는 읽기 전용** 엔터티입니다. 이 문제에는 BDEF가 없습니다.

**만들 객체**

| 순서 | 객체 유형 | 이름 | 역할 |
|---|---|---|---|
| 1 | Data Definition (custom entity) | `ZRAP_CE_FLIGHT_###` | 항공편 + 계산 필드(이용률, 신호등) |
| 2 | ABAP Class | `ZCL_RAP_CE_FLIGHT_###` | 쿼리 제공자(`if_rap_query_provider`) + 콘솔(`if_oo_adt_classrun`) + 테스트 가능한 도우미 메서드 |
| 3 | Data Definition (custom entity) | `ZRAP_CE_PLANE_VH_###` | 기종(PlaneType) 값 도움말용 custom entity |
| 4 | ABAP Class | `ZCL_RAP_CE_PLANE_VH_###` | 값 도움말 쿼리 제공자 |
| 5 | Service Definition | `ZRAP_UI_FLIGHT_CE_###` | 서비스 정의 |
| 6 | Service Binding | `ZRAP_UI_FLIGHT_CE_O4_###` | OData V4 UI 바인딩 |
| 7 | (심화) 기존 CDS 수정 | `ZRAP_R_BOOKING_###`, `ZRAP_C_BOOKING_###` | custom entity로 가는 연관 / 값 도움말 |

#### 1단계. Custom entity 정의하기

요구사항
1. ADT에서 패키지 `ZRAP_###` → New → Data Definition, 이름 `ZRAP_CE_FLIGHT_###`, 설명 `Flight utilization (custom entity)`. 템플릿 선택 화면까지 **Next**로 가서 `Define Custom Entity with Parameters` 템플릿을 고른 뒤 `with parameters ...` 부분을 지우세요(파라미터 없는 custom entity 템플릿이 따로 없을 수 있습니다).
2. 요소(필드)는 아래와 같이 정의합니다. 타입은 /DMO 데이터 엘리먼트를 우선 사용합니다.

| 요소 | 키 | 타입 | 의미 |
|---|---|---|---|
| CarrierID | 키 | `/dmo/carrier_id` | 항공사 |
| ConnectionID | 키 | `/dmo/connection_id` | 노선 번호 |
| FlightDate | 키 | `/dmo/flight_date` | 운항일 |
| CarrierName | | `/dmo/carrier_name` | 항공사 이름(텍스트) |
| DepartureAirport | | `/dmo/airport_from_id` | 출발 공항 |
| DestinationAirport | | `/dmo/airport_to_id` | 도착 공항 |
| PlaneType | | `/dmo/plane_type_id` | 기종 |
| Price | | `/dmo/flight_price` | 운임(통화 금액) |
| CurrencyCode | | `/dmo/currency_code` | 통화 |
| SeatsMax | | `/dmo/plane_seats_max` | 최대 좌석 |
| SeatsOccupied | | `/dmo/plane_seats_occupied` | 예약 좌석 |
| SeatsFree | | `/dmo/plane_seats_max` | 남은 좌석(계산) |
| UtilizationPct | | `abap.dec(5,2)` | 이용률 %(계산) |
| UtilizationCriticality | | `abap.int1` | 신호등 값 0~3(계산) |

3. 엔터티 헤더에 이 엔터티의 데이터를 만들어 줄 ABAP 클래스 `ZCL_RAP_CE_FLIGHT_###`를 지정합니다(클래스는 2단계에서 만듭니다).
4. 이 단계에서는 UI 어노테이션을 넣지 않습니다(6단계에서 추가).

**직접 추가할 어노테이션**
- `@EndUserText.label` — 엔터티 설명.
- `@ObjectModel.query.implementedBy` — 이 엔터티의 SELECT를 대신 처리할 ABAP 클래스를 지정(`'ABAP:클래스명'` 형식).
- `@Semantics.amount.currencyCode` — 운임 필드가 어느 통화 필드를 따르는지.
- `@EndUserText.label` (요소 단위) — 데이터 엘리먼트가 없는 계산 필드(`abap.dec`, `abap.int1`)의 화면 라벨.

**확인**
- 활성화가 성공해야 합니다. 클래스가 아직 없으므로 "class not found" 류의 **경고**가 날 수 있는데, 2단계 후에 사라집니다.
- custom entity는 데이터베이스 객체가 아니므로 **Data Preview(F8)가 동작하지 않습니다**. 대신 2단계의 콘솔과 8단계의 Fiori Preview로 확인합니다.

<details><summary>정답·해설</summary>

```cds
@EndUserText.label: 'Flight utilization (custom entity)'      // 엔터티 설명 (→ 어노테이션 탭: @EndUserText.label)
@ObjectModel.query.implementedBy: 'ABAP:ZCL_RAP_CE_FLIGHT_###' // SELECT를 처리할 쿼리 제공자 클래스 (→ 어노테이션 탭: @ObjectModel.query.implementedBy)
define custom entity ZRAP_CE_FLIGHT_###
{
  key CarrierID              : /dmo/carrier_id;
  key ConnectionID           : /dmo/connection_id;
  key FlightDate             : /dmo/flight_date;
      CarrierName            : /dmo/carrier_name;
      DepartureAirport       : /dmo/airport_from_id;
      DestinationAirport     : /dmo/airport_to_id;
      PlaneType              : /dmo/plane_type_id;
      @Semantics.amount.currencyCode: 'CurrencyCode'           // Price는 CurrencyCode를 통화로 사용 (→ 어노테이션 탭: @Semantics.amount.currencyCode)
      Price                  : /dmo/flight_price;
      CurrencyCode           : /dmo/currency_code;
      SeatsMax               : /dmo/plane_seats_max;
      SeatsOccupied          : /dmo/plane_seats_occupied;
      @EndUserText.label: 'Free Seats'                          // 계산 필드의 라벨 (→ 어노테이션 탭: @EndUserText.label)
      SeatsFree              : /dmo/plane_seats_max;
      @EndUserText.label: 'Utilization (%)'
      UtilizationPct         : abap.dec( 5, 2 );
      @EndUserText.label: 'Utilization Criticality'
      UtilizationCriticality : abap.int1;
}
```

왜 이렇게 쓰나
- `define custom entity`는 **데이터 소스(`as select from`)가 없는** CDS 엔터티입니다. 요소 목록과 타입만 정의하고, 실제 데이터는 `@ObjectModel.query.implementedBy`가 가리키는 클래스가 런타임에 만들어 돌려줍니다. 그래서 문법이 abstract entity와 비슷합니다(요소마다 `이름 : 타입;`).
- openSAP 예제에는 `define root custom entity`도 나옵니다. `root`는 custom entity를 RAP BO의 루트로 쓰거나(unmanaged BO의 읽기 전용 루트처럼) 다른 custom entity와 composition을 맺을 때 필요합니다. 이 문제처럼 **읽기 전용 목록 하나**만 내보낼 때는 `root` 없이 충분합니다.
- 요소 이름은 OData 속성 이름이 되고, 2단계 이후 클래스에서 **필터 range 이름(대문자, 예: `CARRIERID`)과 SQL 필터 문자열의 열 이름**으로 그대로 쓰입니다. 그래서 요소 이름을 데이터베이스 열 이름과 다르게(카멜 표기) 지어 두면 "DB 열 ↔ 엔터티 요소" 매핑을 클래스에서 직접 해야 한다는 점을 기억하세요(4단계에서 다룹니다).
- custom entity는 ABAP 타입으로도 쓸 수 있습니다. `TYPE STANDARD TABLE OF zrap_ce_flight_###`로 내부 테이블을 만들면 요소와 같은 컴포넌트를 가진 표가 됩니다(SAP RAP630 예제가 이렇게 씁니다).
- 권한: custom entity에는 DCL(access control)이 적용되지 않습니다. 권한 검사가 필요하면 쿼리 제공자 클래스 안에서 직접 해야 합니다.

자주 나는 오류와 해결
- 템플릿에서 `with parameters` 를 지우지 않고 활성화하면 파라미터 타입 오류가 납니다. 파라미터 줄 전체를 지우세요.
- 금액 필드에 `@Semantics.amount.currencyCode`를 빼면 통화 금액 타입(CURR) 요소에 참조 통화가 없다는 오류/경고가 납니다.

</details>

#### 2단계. 조회 엔진 클래스와 콘솔 테스트 (select 이전에 로직부터)

요구사항
1. 클래스 `ZCL_RAP_CE_FLIGHT_###`(PUBLIC FINAL CREATE PUBLIC)를 만들고 `if_oo_adt_classrun`과 `if_rap_query_provider` 인터페이스를 모두 구현하도록 선언합니다. `if_rap_query_provider~select`는 이 단계에서는 **비워 둡니다**(3단계에서 채움).
2. 테스트하기 쉽게 로직을 다음 공개 메서드로 나눕니다.
   - `calc_utilization` (정적): 최대 좌석·예약 좌석 → 이용률(소수 2자리 반올림). 최대 좌석이 0 이하이면 0.
   - `get_criticality` (정적): 이용률 80 이상 → 3(긍정, 초록), 50 이상 → 2(주의, 노랑), 그 외 → 1(부정, 빨강). 상수 구조 `criticality`(neutral 0, negative 1, critical 2, positive 3)를 사용합니다.
   - `read_flights` (인스턴스): `if_rap_query_filter=>tt_name_range_pairs` 형식의 range를 받아 `/DMO/FLIGHT` ⋈ `/DMO/CONNECTION`을 **한 번의 SELECT**로 읽고(키 3개 + 출발/도착 공항 range를 DB로 내려 보냄), 계산 필드를 채워 돌려줍니다. 파라미터 `iv_with_names = abap_true`일 때만 `/DMO/CARRIER`에서 항공사 이름을 **한 번의 SELECT(FOR ALL ENTRIES)**로 채웁니다(루프 안 SELECT 금지).
3. `if_oo_adt_classrun~main`에서 range 테이블을 직접 만들어(항공사 `AA` 또는 `LH`, 운항일 오늘 이후) `read_flights`를 호출하고, 건수와 앞 5건을 출력합니다.

**확인**
- F9로 실행 → 콘솔에 `Flights read: N` 과 5건의 표가 나오고, `UtilizationPct`, `UtilizationCriticality`, `SeatsFree`가 채워져 있어야 합니다.
- range에 없는 항공사(예: `XX`)로 바꾸면 0건이 나와야 합니다.

<details><summary>정답·해설</summary>

```abap
CLASS zcl_rap_ce_flight_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.
    INTERFACES if_rap_query_provider.

    TYPES tt_flight TYPE STANDARD TABLE OF zrap_ce_flight_### WITH EMPTY KEY.

    CONSTANTS:
      BEGIN OF criticality,
        neutral  TYPE i VALUE 0,
        negative TYPE i VALUE 1,
        critical TYPE i VALUE 2,
        positive TYPE i VALUE 3,
      END OF criticality.

    "! 이용률(%) = 예약 좌석 * 100 / 최대 좌석, 소수 2자리 반올림
    CLASS-METHODS calc_utilization
      IMPORTING seats_max      TYPE /dmo/plane_seats_max
                seats_occupied TYPE /dmo/plane_seats_occupied
      RETURNING VALUE(result)  TYPE zrap_ce_flight_###-utilizationpct.

    "! 이용률 → 신호등 값(1 빨강, 2 노랑, 3 초록)
    CLASS-METHODS get_criticality
      IMPORTING utilization_pct TYPE zrap_ce_flight_###-utilizationpct
      RETURNING VALUE(result)   TYPE zrap_ce_flight_###-utilizationcriticality.

    "! DB에서 항공편을 읽고 계산 필드를 채움 (range는 DB로 push-down)
    METHODS read_flights
      IMPORTING it_ranges         TYPE if_rap_query_filter=>tt_name_range_pairs OPTIONAL
                iv_with_names     TYPE abap_bool DEFAULT abap_true
      RETURNING VALUE(rt_flights) TYPE tt_flight.

  PROTECTED SECTION.
  PRIVATE SECTION.
    METHODS add_carrier_names
      CHANGING ct_flights TYPE tt_flight.
ENDCLASS.


CLASS zcl_rap_ce_flight_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.
    " 1) range를 직접 만들기: OData $filter가 get_as_ranges( )로 넘어올 때와 같은 형태
    DATA lt_ranges TYPE if_rap_query_filter=>tt_name_range_pairs.

    lt_ranges = VALUE #(
      ( name  = 'CARRIERID'
        range = VALUE #( ( sign = 'I' option = 'EQ' low = 'AA' )
                         ( sign = 'I' option = 'EQ' low = 'LH' ) ) )
      ( name  = 'FLIGHTDATE'
        range = VALUE #( ( sign = 'I' option = 'GE'
                           low  = cl_abap_context_info=>get_system_date( ) ) ) ) ).

    " 2) 조회
    DATA(lt_flights) = read_flights( it_ranges = lt_ranges ).

    out->write( |Flights read: { lines( lt_flights ) }| ).

    " 3) 앞 5건만 출력
    DATA(lt_top5) = lt_flights.
    IF lines( lt_top5 ) > 5.
      DELETE lt_top5 FROM 6.
    ENDIF.
    out->write( lt_top5 ).
  ENDMETHOD.


  METHOD calc_utilization.
    IF seats_max <= 0.
      result = 0.
      RETURN.
    ENDIF.
    " 정수끼리 나누면 정수 나눗셈이 되므로 decfloat34로 바꿔서 계산
    DATA(lv_pct) = CONV decfloat34( seats_occupied ) * 100 / seats_max.
    result = round( val = lv_pct dec = 2 ).
  ENDMETHOD.


  METHOD get_criticality.
    result = COND #( WHEN utilization_pct >= 80 THEN criticality-positive
                     WHEN utilization_pct >= 50 THEN criticality-critical
                     ELSE                            criticality-negative ).
  ENDMETHOD.


  METHOD read_flights.
    " 엔터티 요소 이름(대문자) → DB 열에 맞는 range 테이블
    DATA lr_carrier     TYPE RANGE OF /dmo/carrier_id.
    DATA lr_connection  TYPE RANGE OF /dmo/connection_id.
    DATA lr_flight_date TYPE RANGE OF /dmo/flight_date.
    DATA lr_from        TYPE RANGE OF /dmo/airport_from_id.
    DATA lr_to          TYPE RANGE OF /dmo/airport_to_id.

    LOOP AT it_ranges INTO DATA(ls_range).
      CASE ls_range-name.
        WHEN 'CARRIERID'.
          lr_carrier     = CORRESPONDING #( ls_range-range ).
        WHEN 'CONNECTIONID'.
          lr_connection  = CORRESPONDING #( ls_range-range ).
        WHEN 'FLIGHTDATE'.
          lr_flight_date = CORRESPONDING #( ls_range-range ).
        WHEN 'DEPARTUREAIRPORT'.
          lr_from        = CORRESPONDING #( ls_range-range ).
        WHEN 'DESTINATIONAIRPORT'.
          lr_to          = CORRESPONDING #( ls_range-range ).
        WHEN OTHERS.
          " 계산 필드(UtilizationPct 등)나 텍스트 필드는 DB로 내릴 수 없음
          " → select에서 SQL 문자열로 내부 테이블을 한 번 더 거른다 (4단계)
      ENDCASE.
    ENDLOOP.

    SELECT FROM /dmo/flight AS f
           INNER JOIN /dmo/connection AS c
              ON  c~carrier_id    = f~carrier_id
              AND c~connection_id = f~connection_id
      FIELDS f~carrier_id      AS carrierid,
             f~connection_id   AS connectionid,
             f~flight_date     AS flightdate,
             c~airport_from_id AS departureairport,
             c~airport_to_id   AS destinationairport,
             f~plane_type_id   AS planetype,
             f~price           AS price,
             f~currency_code   AS currencycode,
             f~seats_max       AS seatsmax,
             f~seats_occupied  AS seatsoccupied
      WHERE f~carrier_id      IN @lr_carrier
        AND f~connection_id   IN @lr_connection
        AND f~flight_date     IN @lr_flight_date
        AND c~airport_from_id IN @lr_from
        AND c~airport_to_id   IN @lr_to
      INTO CORRESPONDING FIELDS OF TABLE @rt_flights.

    " 계산 필드 채우기 (DB 접근 없음)
    LOOP AT rt_flights ASSIGNING FIELD-SYMBOL(<ls_flight>).
      <ls_flight>-seatsfree              = <ls_flight>-seatsmax - <ls_flight>-seatsoccupied.
      <ls_flight>-utilizationpct         = calc_utilization( seats_max      = <ls_flight>-seatsmax
                                                             seats_occupied = <ls_flight>-seatsoccupied ).
      <ls_flight>-utilizationcriticality = get_criticality( <ls_flight>-utilizationpct ).
    ENDLOOP.

    IF iv_with_names = abap_true.
      add_carrier_names( CHANGING ct_flights = rt_flights ).
    ENDIF.
  ENDMETHOD.


  METHOD add_carrier_names.
    CHECK ct_flights IS NOT INITIAL.

    " 항공사 ID 중복 제거 → 한 번의 SELECT
    DATA lt_carrier_ids TYPE SORTED TABLE OF /dmo/carrier_id WITH UNIQUE KEY table_line.
    lt_carrier_ids = CORRESPONDING #( ct_flights DISCARDING DUPLICATES MAPPING table_line = carrierid ).

    SELECT FROM /dmo/carrier
      FIELDS carrier_id, name
      FOR ALL ENTRIES IN @lt_carrier_ids
      WHERE carrier_id = @lt_carrier_ids-table_line
      INTO TABLE @DATA(lt_carriers).

    SORT lt_carriers BY carrier_id.

    LOOP AT ct_flights ASSIGNING FIELD-SYMBOL(<ls_flight>).
      READ TABLE lt_carriers INTO DATA(ls_carrier)
           WITH KEY carrier_id = <ls_flight>-carrierid BINARY SEARCH.
      IF sy-subrc = 0.
        <ls_flight>-carriername = ls_carrier-name.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.


  METHOD if_rap_query_provider~select.
    " 3단계에서 구현
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나
- **select를 바로 짜지 않고 조회 엔진부터 만드는 이유**: `select`는 `io_request`/`io_response` 객체가 있어야만 호출할 수 있어서 콘솔이나 단위 테스트에서 직접 부르기 어렵습니다. 그래서 SAP openSAP 예제(`get_agencies`)처럼 실제 로직을 **일반 메서드**로 빼 두고, `select`는 요청을 풀어서 그 메서드를 호출하는 얇은 껍데기로 만듭니다. 9단계의 ABAP Unit도 이 구조 덕분에 가능합니다.
- `if_rap_query_filter=>tt_name_range_pairs`는 `name`(엔터티 요소 이름, 대문자)과 `range`(`sign`/`option`/`low`/`high`) 쌍의 테이블입니다. openSAP·RAP620 예제가 콘솔에서 이 타입으로 필터를 직접 만들어 테스트합니다.
- `CORRESPONDING #( ls_range-range )`로 `RANGE OF /dmo/carrier_id` 같은 **타입이 정해진 range**로 옮긴 뒤 `IN @lr_...`로 쓰면 값이 **호스트 변수로 바인딩**되므로 SQL 인젝션 위험이 없습니다. range가 비어 있으면 `IN`은 "조건 없음"과 같습니다.
- 이름 읽기를 별도 메서드로 뺀 것은 4단계의 `get_requested_elements( )` 최적화(요청되지 않으면 안 읽기)를 보여 주기 위해서입니다. `FOR ALL ENTRIES` 전에 **빈 테이블 체크**(`CHECK ct_flights IS NOT INITIAL`)는 필수입니다(빈 테이블이면 WHERE가 무시되어 전부 읽음).
- `/DMO/` 테이블을 직접 읽는 대신 `/DMO/I_Flight`, `/DMO/I_Connection` 같은 CDS 뷰를 읽어도 됩니다. 이 문제는 "테이블에서 직접 읽어 계산하는 조회 엔진"을 보여 주려고 테이블을 사용했습니다.

자주 나는 오류와 해결
- `calc_utilization`에서 `seats_occupied * 100 / seats_max`를 그대로 쓰면 정수 연산이라 소수점이 사라집니다. `CONV decfloat34( ... )`로 바꿔 계산하세요.
- `INTO CORRESPONDING FIELDS OF TABLE`을 빼고 `INTO TABLE`로 쓰면, SELECT 열 순서와 custom entity 요소 순서가 다르기 때문에 타입 오류가 납니다.

</details>

#### 3단계. if_rap_query_provider~select 기본: 데이터 요청과 건수 요청

요구사항
1. `select`에서 필터·정렬·페이징을 아직 처리하지 않는 **최소 구현**을 만듭니다.
   - `io_request->is_total_numb_of_rec_requested( )`가 참이면 전체 건수를 `io_response->set_total_number_of_records( )`로 넘깁니다.
   - `io_request->is_data_requested( )`가 참이면 데이터를 `io_response->set_data( )`로 넘깁니다.
   - 두 메서드는 **요청된 경우에만** 호출합니다.
2. 이 단계의 select는 2단계 클래스의 `if_rap_query_provider~select` 메서드만 바꿉니다(나머지는 그대로).

**확인**
- 8단계에서 서비스를 만들고 나서 돌아와 확인해도 됩니다. Fiori Preview에서 Go를 누르면 목록이 나오지만, 아직 페이징을 하지 않으므로 **스크롤해도 같은 데이터가 반복**되거나, 필터를 넣어도 걸러지지 않는 것을 볼 수 있습니다. 이것이 4·5단계가 필요한 이유입니다.

<details><summary>정답·해설</summary>

```abap
  METHOD if_rap_query_provider~select.
    " (최소 구현) 필터/정렬/페이징 미처리 → 4·5단계에서 교체
    DATA(lt_flights) = read_flights( ).

    " $count 또는 $inlinecount가 요청된 경우에만 건수 설정
    IF io_request->is_total_numb_of_rec_requested( ).
      io_response->set_total_number_of_records( lines( lt_flights ) ).
    ENDIF.

    " 데이터가 요청된 경우에만 데이터 설정 ($count만 요청되면 데이터 요청은 거짓)
    IF io_request->is_data_requested( ).
      io_response->set_data( lt_flights ).
    ENDIF.
  ENDMETHOD.
```

왜 이렇게 쓰나
- OData 클라이언트는 같은 엔터티 셋에 대해 "데이터만", "건수만(`/$count`)", "데이터 + 건수(`$count=true`)"를 요청할 수 있습니다. openSAP 해설: "비즈니스 데이터가 요청되면 `set_data()`로 반드시 넘겨야 하고, 전체 건수가 요청되면 `set_total_number_of_records()`로 반드시 넘겨야 한다." 그래서 두 가지 `is_..._requested( )`로 갈라 처리합니다.
- 요청되지 않은 것을 설정하거나, 요청된 것을 빠뜨리면 런타임에 쿼리 제공자 계약 위반 예외가 납니다(정확한 예외 이름은 실제 시스템에서 확인 필요).
- **클래스 구조 해설**: `if_rap_query_provider`에는 메서드가 `select` 하나뿐이며 시그니처는 `IMPORTING io_request TYPE REF TO if_rap_query_request, io_response TYPE REF TO if_rap_query_response RAISING cx_rap_query_provider` 형태입니다. BDEF에서 생기는 파생 타입이 아니라 **인터페이스에 고정된 시그니처**이고, OData 요청(목록 읽기, 단건 읽기, 값 도움말 조회, `$count`)이 이 엔터티에 올 때마다 프레임워크가 호출합니다. 단건 읽기(Object Page)도 "키 필터가 걸린 목록 읽기"로 들어옵니다.

자주 나는 오류와 해결
- RAP620 예제처럼 건수 요청 여부와 관계없이 항상 `set_total_number_of_records`를 호출하는 코드도 있습니다. 이 문제는 openSAP 예제처럼 **요청됐을 때만** 호출하는 쪽을 권장합니다.

</details>

#### 4단계. 필터: get_as_ranges와 get_as_sql_string, 그리고 요청 필드

요구사항
1. 필터를 두 가지 방식으로 **모두** 받습니다.
   - `io_request->get_filter( )->get_as_sql_string( )` → 문자열. 항상 받을 수 있습니다.
   - `io_request->get_filter( )->get_as_ranges( )` → `tt_name_range_pairs`. 필터를 range로 표현할 수 없으면(예: 서로 다른 필드를 `or`로 묶은 `$filter`) 예외 `cx_rap_query_filter_no_range`가 납니다. 이때는 range를 비우고 계속 진행합니다.
2. range는 `read_flights`에 넘겨 **DB push-down**에 쓰고, 그 결과 내부 테이블에 SQL 문자열 필터를 **한 번 더** 적용합니다(`SELECT * FROM @lt_flights AS flights WHERE (lv_sql_filter)`). 이렇게 해야 `UtilizationPct ge 80` 같은 계산 필드 필터도 맞게 동작합니다. 이 부분을 정적 메서드 `apply_sql_filter`로 만듭니다.
3. `io_request->get_requested_elements( )`로 요청된 요소 목록을 받아, `CARRIERNAME`이 요청되지 않았고 검색어도 없고 필터·정렬에도 `CARRIERNAME`이 없으면 `iv_with_names = abap_false`로 항공사 이름 읽기를 건너뜁니다.

**확인**
- 8단계 이후 Fiori Preview에서 항공사 = `AA` 필터 → `AA`만 나와야 합니다.
- 브라우저 주소창에서 서비스 URL 뒤에 `Flight?$filter=UtilizationPct ge 80` 을 붙여 호출하면 이용률 80 이상만 나와야 합니다.
- `Flight?$filter=CarrierID eq 'AA' or PlaneType eq 'A380-800'` 처럼 서로 다른 필드를 `or`로 묶으면 range 변환이 안 되지만(예외를 잡아 range 없이 진행) 결과는 SQL 문자열 필터 덕분에 맞아야 합니다.

<details><summary>정답·해설</summary>

클래스 정의부 PUBLIC SECTION에 추가:

```abap
    "! SQL 필터 문자열(엔터티 요소 이름 기준)을 내부 테이블에 적용
    CLASS-METHODS apply_sql_filter
      IMPORTING iv_sql_filter TYPE string
      CHANGING  ct_flights    TYPE tt_flight.
```

구현부에 추가하고 select를 교체:

```abap
  METHOD apply_sql_filter.
    CHECK iv_sql_filter IS NOT INITIAL.

    DATA(lt_source) = ct_flights.
    " 내부 테이블을 데이터 소스로 하는 ABAP SQL: 열 이름 = custom entity 요소 이름
    SELECT * FROM @lt_source AS flights
      WHERE (iv_sql_filter)
      INTO TABLE @ct_flights.
  ENDMETHOD.


  METHOD if_rap_query_provider~select.
    DATA lt_ranges TYPE if_rap_query_filter=>tt_name_range_pairs.

    " 1) 필터: SQL 문자열은 항상, range는 가능한 경우만
    DATA(lo_filter)     = io_request->get_filter( ).
    DATA(lv_sql_filter) = lo_filter->get_as_sql_string( ).
    TRY.
        lt_ranges = lo_filter->get_as_ranges( ).
      CATCH cx_rap_query_filter_no_range.
        " range로 표현 불가(예: 다른 필드끼리 or) → push-down 포기, SQL 문자열로만 거름
        CLEAR lt_ranges.
    ENDTRY.

    " 2) 요청 필드 (대소문자 통일)
    DATA(lt_requested) = VALUE string_table( FOR lv_element IN io_request->get_requested_elements( )
                                             ( to_upper( lv_element ) ) ).

    DATA(lv_need_names) = xsdbool( line_exists( lt_requested[ table_line = `CARRIERNAME` ] )
                                   OR to_upper( lv_sql_filter ) CS 'CARRIERNAME' ).

    " 3) DB 읽기(range push-down) → 내부 테이블에 SQL 문자열 필터
    DATA(lt_flights) = read_flights( it_ranges     = lt_ranges
                                     iv_with_names = lv_need_names ).
    apply_sql_filter( EXPORTING iv_sql_filter = lv_sql_filter
                      CHANGING  ct_flights    = lt_flights ).

    IF io_request->is_total_numb_of_rec_requested( ).
      io_response->set_total_number_of_records( lines( lt_flights ) ).
    ENDIF.

    IF io_request->is_data_requested( ).
      io_response->set_data( lt_flights ).
    ENDIF.
  ENDMETHOD.
```

왜 이렇게 쓰나 — 두 필터 방식 비교

| | `get_as_ranges( )` | `get_as_sql_string( )` |
|---|---|---|
| 결과 형태 | 요소별 range 테이블 | `CARRIERID = 'AA' AND ...` 같은 WHERE 문자열 |
| 표현 가능 범위 | 요소별 조건의 AND 조합만. 다른 요소끼리 OR 등은 `cx_rap_query_filter_no_range` | OData `$filter`가 표현하는 조건 전부 |
| 쓰는 곳 | 타입이 있는 range로 바꿔 `IN @range`(바인딩), 원격 API 호출 파라미터(openSAP의 `create_by_range`) | `WHERE (lv_sql_filter)` 동적 조건 |
| 열 이름 | 요소 이름 → 코드에서 DB 열로 매핑 가능 | **요소 이름 그대로**. DB 열 이름이 다르면 DB 테이블에 바로 쓸 수 없음 |
| 인젝션 | 값이 바인딩되므로 안전 | 프레임워크가 OData 요청을 파싱해 만든 문자열이라 그대로 쓰는 것은 공식 예제 패턴(RAP630, reuse-services). 단, **이 문자열에 직접 사용자 입력을 이어 붙이면 위험** → `cl_abap_dyn_prg=>escape_quotes( )` 등으로 이스케이프 필요 |

- 이 문제는 두 방식을 **함께** 씁니다. range로 DB에서 먼저 줄이고(성능), SQL 문자열로 내부 테이블을 정확히 거릅니다(정확성: 계산 필드·OR 조건). SAP 공식 예제(RAP630 `ZRAP630_CL_VH_PRODUCT_SOL`, basic-trial `ZCL_CE_AC_PRODUCT`)도 `SELECT * FROM @business_data ... WHERE (filter_condition)` 형태로 내부 테이블에 SQL 문자열을 적용합니다.
- 요소 이름을 DB 열과 **똑같이** 만들었다면(예: custom entity 요소 `carrier_id`) SQL 문자열을 DB SELECT에 바로 쓸 수도 있습니다. 하지만 RAP 관례(카멜 표기 별칭)와 맞지 않고 계산 필드는 여전히 DB에 없으므로, 이 문제처럼 "range는 DB, 문자열은 내부 테이블" 구성이 실무에서 다루기 쉽습니다.
- `cx_rap_query_filter_no_range`를 잡는 패턴은 공개 RAP 예제 문서(mindsquare RAP_Samples)에서 확인했습니다. SAP 공식 저장소 코드에서는 확인하지 못했으므로 예외 클래스 이름은 ADT 코드 완성(Ctrl+Space)으로 한 번 확인하세요(실제 시스템에서 확인 필요).
- `get_requested_elements( )`는 `$select`로 요청된 요소 목록입니다. 요청되지 않은 비싼 필드(원격 호출, 추가 SELECT)를 건너뛰는 데 씁니다. 반환 값이 대문자인지 확실하지 않으므로 `to_upper`로 통일했습니다.

자주 나는 오류와 해결
- `SELECT ... FROM @itab WHERE (dyn)`에서 문자열에 itab에 없는 열 이름이 들어 있으면 `CX_SY_DYNAMIC_OSQL_SEMANTICS` 런타임 오류가 납니다. 프레임워크 문자열은 custom entity 요소 이름을 쓰므로 내부 테이블 타입을 반드시 custom entity 타입(`tt_flight`)으로 두세요.

</details>

#### 5단계. 검색, 정렬, 페이징 — select 완성

요구사항
1. **검색**: `io_request->get_search_expression( )`이 비어 있지 않으면 `CarrierName`, `DepartureAirport`, `DestinationAirport`, `PlaneType` 중 하나라도 검색어를 포함(대소문자 무시)하는 행만 남깁니다. 동적 SQL을 만들지 말고 ABAP 비교(`CS`)로 처리합니다. 정적 메서드 `apply_search`.
2. **건수**: 필터·검색까지 적용한 뒤, 정렬·페이징 **전**의 건수를 total count로 넘깁니다.
3. **정렬**: `io_request->get_sort_elements( )`의 각 행(`element_name`, `descending`)을 `abap_sortorder_tab`으로 바꿔 `SORT ... BY (otab)`로 정렬합니다. 정렬 요청이 없으면 `CarrierID`, `ConnectionID`, `FlightDate` 오름차순. 정적 메서드 `apply_sort`.
4. **페이징**: `get_paging( )->get_offset( )`만큼 앞을 버리고, `get_page_size( )`만큼 남깁니다. 페이지 크기가 `if_rap_query_paging=>page_size_unlimited`이면 자르지 않습니다. 정적 메서드 `apply_paging`.
5. 4단계의 이름 읽기 조건에 "검색어가 있거나 정렬에 `CARRIERNAME`이 있으면"을 추가합니다.
6. 아래 정답의 **클래스 전체 코드**로 교체합니다.

**확인**
- Fiori Preview에서 검색창에 `Frankfurt`의 공항 코드 `FRA` 입력 → 출발 또는 도착이 FRA인 항공편만.
- 열 머리글 정렬(이용률 내림차순) → 이용률이 큰 순서.
- 목록을 아래로 스크롤하면 다음 페이지가 이어서 로드되고 **같은 행이 반복되지 않아야** 합니다. 표 제목 옆 건수 `(N)`이 필터 결과 전체 건수와 같아야 합니다.
- 주소창 `Flight?$top=3&$skip=2&$count=true` → 3건, `@odata.count`는 전체 건수.

<details><summary>정답·해설</summary>

```abap
CLASS zcl_rap_ce_flight_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.
    INTERFACES if_rap_query_provider.

    TYPES tt_flight TYPE STANDARD TABLE OF zrap_ce_flight_### WITH EMPTY KEY.

    CONSTANTS:
      BEGIN OF criticality,
        neutral  TYPE i VALUE 0,
        negative TYPE i VALUE 1,
        critical TYPE i VALUE 2,
        positive TYPE i VALUE 3,
      END OF criticality.

    "! 이용률(%) = 예약 좌석 * 100 / 최대 좌석, 소수 2자리 반올림
    CLASS-METHODS calc_utilization
      IMPORTING seats_max      TYPE /dmo/plane_seats_max
                seats_occupied TYPE /dmo/plane_seats_occupied
      RETURNING VALUE(result)  TYPE zrap_ce_flight_###-utilizationpct.

    "! 이용률 → 신호등 값(1 빨강, 2 노랑, 3 초록)
    CLASS-METHODS get_criticality
      IMPORTING utilization_pct TYPE zrap_ce_flight_###-utilizationpct
      RETURNING VALUE(result)   TYPE zrap_ce_flight_###-utilizationcriticality.

    "! DB에서 항공편을 읽고 계산 필드를 채움 (range는 DB로 push-down)
    METHODS read_flights
      IMPORTING it_ranges         TYPE if_rap_query_filter=>tt_name_range_pairs OPTIONAL
                iv_with_names     TYPE abap_bool DEFAULT abap_true
      RETURNING VALUE(rt_flights) TYPE tt_flight.

    "! SQL 필터 문자열(엔터티 요소 이름 기준)을 내부 테이블에 적용
    CLASS-METHODS apply_sql_filter
      IMPORTING iv_sql_filter TYPE string
      CHANGING  ct_flights    TYPE tt_flight.

    "! 자유 검색어(대소문자 무시)로 거르기
    CLASS-METHODS apply_search
      IMPORTING iv_search  TYPE string
      CHANGING  ct_flights TYPE tt_flight.

    "! 동적 정렬 (비어 있으면 키 순)
    CLASS-METHODS apply_sort
      IMPORTING it_sort    TYPE abap_sortorder_tab
      CHANGING  ct_flights TYPE tt_flight.

    "! offset/page size로 자르기
    CLASS-METHODS apply_paging
      IMPORTING iv_offset    TYPE int8
                iv_page_size TYPE int8
      CHANGING  ct_flights   TYPE tt_flight.

  PROTECTED SECTION.
  PRIVATE SECTION.
    METHODS add_carrier_names
      CHANGING ct_flights TYPE tt_flight.
ENDCLASS.


CLASS zcl_rap_ce_flight_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.
    DATA lt_ranges TYPE if_rap_query_filter=>tt_name_range_pairs.

    " (1) range 필터: AA 또는 LH, 오늘 이후
    lt_ranges = VALUE #(
      ( name  = 'CARRIERID'
        range = VALUE #( ( sign = 'I' option = 'EQ' low = 'AA' )
                         ( sign = 'I' option = 'EQ' low = 'LH' ) ) )
      ( name  = 'FLIGHTDATE'
        range = VALUE #( ( sign = 'I' option = 'GE'
                           low  = cl_abap_context_info=>get_system_date( ) ) ) ) ).

    DATA(lt_flights) = read_flights( it_ranges = lt_ranges ).
    out->write( |1) range push-down: { lines( lt_flights ) } flights| ).

    " (2) 계산 필드 필터: OData가 만들어 줄 SQL 문자열을 흉내
    apply_sql_filter( EXPORTING iv_sql_filter = `UTILIZATIONPCT >= 50`
                      CHANGING  ct_flights    = lt_flights ).
    out->write( |2) + UtilizationPct >= 50: { lines( lt_flights ) } flights| ).

    " (3) 정렬: 이용률 내림차순
    apply_sort( EXPORTING it_sort    = VALUE #( ( name = 'UTILIZATIONPCT' descending = abap_true ) )
                CHANGING  ct_flights = lt_flights ).

    " (4) 페이징: 2건 건너뛰고 3건
    DATA(lv_total) = lines( lt_flights ).
    apply_paging( EXPORTING iv_offset    = 2
                            iv_page_size = 3
                  CHANGING  ct_flights   = lt_flights ).
    out->write( |3) total { lv_total }, page (skip 2, top 3):| ).
    out->write( lt_flights ).
  ENDMETHOD.


  METHOD if_rap_query_provider~select.
    DATA lt_ranges TYPE if_rap_query_filter=>tt_name_range_pairs.

    " 1) 필터: SQL 문자열은 항상, range는 가능한 경우만
    DATA(lo_filter)     = io_request->get_filter( ).
    DATA(lv_sql_filter) = lo_filter->get_as_sql_string( ).
    TRY.
        lt_ranges = lo_filter->get_as_ranges( ).
      CATCH cx_rap_query_filter_no_range.
        CLEAR lt_ranges.
    ENDTRY.

    " 2) 검색어, 요청 필드, 정렬 요청
    DATA(lv_search) = io_request->get_search_expression( ).

    DATA(lt_requested) = VALUE string_table( FOR lv_element IN io_request->get_requested_elements( )
                                             ( to_upper( lv_element ) ) ).

    DATA(lt_sort) = VALUE abap_sortorder_tab( FOR ls_sort_element IN io_request->get_sort_elements( )
                                              ( name       = to_upper( ls_sort_element-element_name )
                                                descending = ls_sort_element-descending ) ).

    " 항공사 이름이 화면/필터/검색/정렬 어디에도 필요 없으면 읽지 않음
    DATA(lv_need_names) = xsdbool( line_exists( lt_requested[ table_line = `CARRIERNAME` ] )
                                   OR lv_search IS NOT INITIAL
                                   OR to_upper( lv_sql_filter ) CS 'CARRIERNAME'
                                   OR line_exists( lt_sort[ name = 'CARRIERNAME' ] ) ).

    " 3) 읽기 → 필터 → 검색
    DATA(lt_flights) = read_flights( it_ranges     = lt_ranges
                                     iv_with_names = lv_need_names ).
    apply_sql_filter( EXPORTING iv_sql_filter = lv_sql_filter
                      CHANGING  ct_flights    = lt_flights ).
    apply_search( EXPORTING iv_search  = lv_search
                  CHANGING  ct_flights = lt_flights ).

    " 4) 건수: 페이징 전 전체 건수
    IF io_request->is_total_numb_of_rec_requested( ).
      io_response->set_total_number_of_records( lines( lt_flights ) ).
    ENDIF.

    " 5) 데이터: 정렬 → 페이징 → 반환
    IF io_request->is_data_requested( ).
      apply_sort( EXPORTING it_sort    = lt_sort
                  CHANGING  ct_flights = lt_flights ).

      DATA(lo_paging) = io_request->get_paging( ).
      apply_paging( EXPORTING iv_offset    = lo_paging->get_offset( )
                              iv_page_size = lo_paging->get_page_size( )
                    CHANGING  ct_flights   = lt_flights ).

      io_response->set_data( lt_flights ).
    ENDIF.
  ENDMETHOD.


  METHOD calc_utilization.
    IF seats_max <= 0.
      result = 0.
      RETURN.
    ENDIF.
    DATA(lv_pct) = CONV decfloat34( seats_occupied ) * 100 / seats_max.
    result = round( val = lv_pct dec = 2 ).
  ENDMETHOD.


  METHOD get_criticality.
    result = COND #( WHEN utilization_pct >= 80 THEN criticality-positive
                     WHEN utilization_pct >= 50 THEN criticality-critical
                     ELSE                            criticality-negative ).
  ENDMETHOD.


  METHOD read_flights.
    DATA lr_carrier     TYPE RANGE OF /dmo/carrier_id.
    DATA lr_connection  TYPE RANGE OF /dmo/connection_id.
    DATA lr_flight_date TYPE RANGE OF /dmo/flight_date.
    DATA lr_from        TYPE RANGE OF /dmo/airport_from_id.
    DATA lr_to          TYPE RANGE OF /dmo/airport_to_id.

    LOOP AT it_ranges INTO DATA(ls_range).
      CASE ls_range-name.
        WHEN 'CARRIERID'.
          lr_carrier     = CORRESPONDING #( ls_range-range ).
        WHEN 'CONNECTIONID'.
          lr_connection  = CORRESPONDING #( ls_range-range ).
        WHEN 'FLIGHTDATE'.
          lr_flight_date = CORRESPONDING #( ls_range-range ).
        WHEN 'DEPARTUREAIRPORT'.
          lr_from        = CORRESPONDING #( ls_range-range ).
        WHEN 'DESTINATIONAIRPORT'.
          lr_to          = CORRESPONDING #( ls_range-range ).
        WHEN OTHERS.
          " 계산/텍스트 필드는 apply_sql_filter에서 처리
      ENDCASE.
    ENDLOOP.

    SELECT FROM /dmo/flight AS f
           INNER JOIN /dmo/connection AS c
              ON  c~carrier_id    = f~carrier_id
              AND c~connection_id = f~connection_id
      FIELDS f~carrier_id      AS carrierid,
             f~connection_id   AS connectionid,
             f~flight_date     AS flightdate,
             c~airport_from_id AS departureairport,
             c~airport_to_id   AS destinationairport,
             f~plane_type_id   AS planetype,
             f~price           AS price,
             f~currency_code   AS currencycode,
             f~seats_max       AS seatsmax,
             f~seats_occupied  AS seatsoccupied
      WHERE f~carrier_id      IN @lr_carrier
        AND f~connection_id   IN @lr_connection
        AND f~flight_date     IN @lr_flight_date
        AND c~airport_from_id IN @lr_from
        AND c~airport_to_id   IN @lr_to
      INTO CORRESPONDING FIELDS OF TABLE @rt_flights.

    LOOP AT rt_flights ASSIGNING FIELD-SYMBOL(<ls_flight>).
      <ls_flight>-seatsfree              = <ls_flight>-seatsmax - <ls_flight>-seatsoccupied.
      <ls_flight>-utilizationpct         = calc_utilization( seats_max      = <ls_flight>-seatsmax
                                                             seats_occupied = <ls_flight>-seatsoccupied ).
      <ls_flight>-utilizationcriticality = get_criticality( <ls_flight>-utilizationpct ).
    ENDLOOP.

    IF iv_with_names = abap_true.
      add_carrier_names( CHANGING ct_flights = rt_flights ).
    ENDIF.
  ENDMETHOD.


  METHOD add_carrier_names.
    CHECK ct_flights IS NOT INITIAL.

    DATA lt_carrier_ids TYPE SORTED TABLE OF /dmo/carrier_id WITH UNIQUE KEY table_line.
    lt_carrier_ids = CORRESPONDING #( ct_flights DISCARDING DUPLICATES MAPPING table_line = carrierid ).

    SELECT FROM /dmo/carrier
      FIELDS carrier_id, name
      FOR ALL ENTRIES IN @lt_carrier_ids
      WHERE carrier_id = @lt_carrier_ids-table_line
      INTO TABLE @DATA(lt_carriers).

    SORT lt_carriers BY carrier_id.

    LOOP AT ct_flights ASSIGNING FIELD-SYMBOL(<ls_flight>).
      READ TABLE lt_carriers INTO DATA(ls_carrier)
           WITH KEY carrier_id = <ls_flight>-carrierid BINARY SEARCH.
      IF sy-subrc = 0.
        <ls_flight>-carriername = ls_carrier-name.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.


  METHOD apply_sql_filter.
    CHECK iv_sql_filter IS NOT INITIAL.

    DATA(lt_source) = ct_flights.
    SELECT * FROM @lt_source AS flights
      WHERE (iv_sql_filter)
      INTO TABLE @ct_flights.
  ENDMETHOD.


  METHOD apply_search.
    CHECK iv_search IS NOT INITIAL.

    " Fiori가 따옴표/별표를 붙여 보낼 수 있으므로 제거 (형식은 실제 시스템에서 확인 필요)
    DATA(lv_term) = condense( replace( val  = replace( val = iv_search sub = `"` with = `` occ = 0 )
                                       sub  = `*` with = `` occ = 0 ) ).
    CHECK lv_term IS NOT INITIAL.

    " CS(contains string)는 대소문자를 구분하지 않음 → 동적 SQL 없이 안전하게 검색
    DELETE ct_flights WHERE NOT (    carriername        CS lv_term
                                  OR departureairport   CS lv_term
                                  OR destinationairport CS lv_term
                                  OR planetype          CS lv_term ).
  ENDMETHOD.


  METHOD apply_sort.
    DATA(lt_sort) = it_sort.
    IF lt_sort IS INITIAL.
      lt_sort = VALUE #( ( name = 'CARRIERID' )
                         ( name = 'CONNECTIONID' )
                         ( name = 'FLIGHTDATE' ) ).
    ENDIF.
    SORT ct_flights BY (lt_sort).
  ENDMETHOD.


  METHOD apply_paging.
    " offset만큼 앞을 버림
    IF iv_offset > 0.
      IF iv_offset >= lines( ct_flights ).
        CLEAR ct_flights.
        RETURN.
      ENDIF.
      DELETE ct_flights FROM 1 TO CONV i( iv_offset ).
    ENDIF.

    " page size만큼 남김 (무제한이면 자르지 않음)
    IF iv_page_size <> if_rap_query_paging=>page_size_unlimited
       AND iv_page_size > 0
       AND lines( ct_flights ) > iv_page_size.
      DELETE ct_flights FROM CONV i( iv_page_size + 1 ).
    ENDIF.
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나
- **처리 순서가 중요합니다**: 필터 → 검색 → **건수** → 정렬 → 페이징. 건수를 페이징 뒤에 세면 Fiori 표 제목의 건수가 페이지 크기(예: 30)로 고정되어 스크롤 로딩이 멈춥니다.
- **정렬**: `get_sort_elements( )`의 각 행에는 `element_name`과 `descending`이 있습니다(공개 RAP 예제 코드에서 확인). `abap_sortorder_tab`의 `name`/`descending`에 그대로 옮겨 `SORT itab BY (otab)`를 쓰면 정렬 필드 수와 방향이 몇 개든 한 줄로 처리됩니다(ABAP cheat sheet "Dynamic Programming" 참고).
- **페이징**: `get_page_size( )`는 클라이언트가 `$top`을 주지 않으면 `if_rap_query_paging=>page_size_unlimited`를 돌려줍니다. 공개 예제들은 이 상수를 0으로 바꿔 `UP TO @lv_max_rows ROWS`에 넘깁니다(ABAP SQL에서 `UP TO 0 ROWS`는 "제한 없음"). 데이터를 DB에서 바로 자를 수 있는 경우의 형태는 아래와 같습니다.

```abap
    " (참고) 계산 필드 필터가 없어 정렬/페이징을 DB에 맡길 수 있을 때의 형태
    DATA(lv_offset)    = io_request->get_paging( )->get_offset( ).
    DATA(lv_page_size) = io_request->get_paging( )->get_page_size( ).
    DATA(lv_max_rows)  = COND int8( WHEN lv_page_size = if_rap_query_paging=>page_size_unlimited
                                    THEN 0 ELSE lv_page_size ).
    SELECT FROM /dmo/flight
      FIELDS carrier_id, connection_id, flight_date, seats_max, seats_occupied
      WHERE carrier_id IN @lr_carrier
      ORDER BY carrier_id, connection_id, flight_date
      INTO TABLE @DATA(lt_db_page)
      OFFSET @lv_offset
      UP TO @lv_max_rows ROWS.
```

- 이 문제는 계산 필드(`UtilizationPct`)로 필터·정렬할 수 있어야 하므로 **DB에서 넉넉히 읽고 ABAP에서 정렬·페이징**합니다. 데이터가 수십만 건이면 이 방식은 느립니다. 그때는 계산을 CDS 식으로 옮겨 view entity를 쓰는 편이 낫습니다(10단계 비교표).
- **검색**: `get_search_expression( )`은 검색창 문자열입니다. 공개 예제 중에는 이 값을 `|DESCRIPTION LIKE '%{ cl_abap_dyn_prg=>escape_quotes( lv_search ) }%'|`처럼 동적 WHERE에 이어 붙이는 것도 있는데, 이때 `escape_quotes`를 빼면 **SQL 인젝션**이 됩니다. 이 정답은 동적 SQL을 만들지 않고 ABAP `CS` 비교로 처리해 이 위험을 없앴습니다. 검색 문자열에 따옴표나 `*`가 붙어 오는지는 Fiori 버전에 따라 다를 수 있습니다(실제 시스템에서 확인 필요).
- **클래스 구조 해설**: `apply_*`를 정적 메서드로 둔 이유는 DB 접근이 없어 9단계에서 테스트 더블 없이 바로 검증할 수 있기 때문입니다. `select`는 OData 요청 1건당 1회 호출되며, 같은 요청 안에서 상태를 유지할 필요가 없으므로 인스턴스 속성을 쓰지 않습니다.

자주 나는 오류와 해결
- `SORT ... BY (otab)`에 테이블에 없는 컴포넌트 이름이 들어가면 런타임 오류가 납니다. 정렬 요소 이름을 `to_upper`로 맞추고, custom entity 요소 이름과 같은지 확인하세요.
- `DELETE ct_flights FROM 1 TO iv_offset`에서 `int8`을 바로 쓰면 타입 오류가 날 수 있어 `CONV i( )`를 썼습니다.

</details>

#### 6단계. List Report / Object Page UI 어노테이션

요구사항
1. 1단계 custom entity에 **직접** UI 어노테이션을 넣습니다(메타데이터 확장(MDE)으로 빼는 방식은 해설 참고).
2. 엔터티 수준: 헤더 정보(유형 이름 `Flight`/`Flights`, 제목 = 항공사, 설명 = 노선 번호), 기본 정렬 = 운항일 내림차순, 검색 가능.
3. 목록(lineItem): 항공사(이름과 함께), 노선, 운항일, 출발, 도착, 기종, 운임, 이용률(신호등 색), 좌석 진행 막대(예약/최대).
4. 필터 바(selectionField): 항공사, 운항일, 출발 공항, 도착 공항, 기종.
5. 검색 대상: 항공사 이름, 출발·도착 공항, 기종.
6. Object Page: 머리글에 좌석 진행 막대, 본문에 "Flight"(일반 정보)와 "Seats"(좌석) 두 섹션.
7. 항공사 ID 옆에 이름이 보이도록 텍스트 연결, `CarrierName`은 목록에서 따로 보이지 않게.
8. 화면 라벨이 필요한 요소에는 `@EndUserText.label` 사용.

**직접 추가할 어노테이션**
- `@UI.headerInfo` — Object Page 제목/설명, 목록 제목의 단수·복수 이름.
- `@UI.presentationVariant` — 목록의 기본 정렬과 표시 방식.
- `@Search.searchable` / `@Search.defaultSearchElement` — 검색창을 켜고, 검색 대상 요소를 지정.
- `@UI.facet` — Object Page 섹션 구성(IDENTIFICATION, FIELDGROUP, 머리글 DATAPOINT 참조).
- `@UI.lineItem` — 목록 열(위치, 중요도, 신호등 `criticality`, `type: #AS_DATAPOINT`).
- `@UI.identification` / `@UI.fieldGroup` — Object Page 섹션 안의 필드.
- `@UI.selectionField` — 필터 바 필드.
- `@UI.dataPoint` — 진행 막대(`visualization`, 목표 값 요소, 신호등).
- `@ObjectModel.text.element` / `@UI.textArrangement` — ID 옆에 이름 표시 방식.
- `@UI.hidden` — 텍스트 필드를 열 선택에서 숨김.

**확인**
- 8단계 서비스 바인딩 후 Preview: 필터 바 5개, 검색창, 목록 열이 보이고 이용률 숫자가 빨강/노랑/초록, 좌석 열이 진행 막대로 보여야 합니다.
- 행 클릭 → Object Page 머리글에 진행 막대, 섹션 2개.

<details><summary>정답·해설</summary>

```cds
@EndUserText.label: 'Flight utilization (custom entity)'
@ObjectModel.query.implementedBy: 'ABAP:ZCL_RAP_CE_FLIGHT_###'  // (→ 어노테이션 탭: @ObjectModel.query.implementedBy)

@UI.headerInfo: { typeName:       'Flight',                       // Object Page 유형 이름 (→ 어노테이션 탭: @UI.headerInfo)
                  typeNamePlural: 'Flights',                      // 목록 제목
                  title:          { type: #STANDARD, value: 'CarrierID' },
                  description:    { type: #STANDARD, value: 'ConnectionID' } }
@UI.presentationVariant: [{ sortOrder:      [{ by: 'FlightDate', direction: #DESC }],   // 기본 정렬 (→ 어노테이션 탭: @UI.presentationVariant)
                            visualizations: [{ type: #AS_LINEITEM }] }]
@Search.searchable: true                                          // 검색창 활성화 → get_search_expression( ) (→ 어노테이션 탭: @Search.searchable)

define custom entity ZRAP_CE_FLIGHT_###
{
      @UI.facet: [ { id:              'Flight',                   // 일반 정보 섹션 (→ 어노테이션 탭: @UI.facet)
                     purpose:         #STANDARD,
                     type:            #IDENTIFICATION_REFERENCE,
                     label:           'Flight',
                     position:        10 },
                   { id:              'Seats',                    // 좌석 섹션 = fieldGroup 'Seats'
                     purpose:         #STANDARD,
                     type:            #FIELDGROUP_REFERENCE,
                     targetQualifier: 'Seats',
                     label:           'Seats',
                     position:        20 },
                   { id:              'SeatsHeader',              // 머리글에 진행 막대 = dataPoint 'SeatsProgress'
                     purpose:         #HEADER,
                     type:            #DATAPOINT_REFERENCE,
                     targetQualifier: 'SeatsProgress',
                     position:        10 } ]

      @UI.lineItem:       [{ position: 10, importance: #HIGH }]   // 목록 열 (→ 어노테이션 탭: @UI.lineItem)
      @UI.identification: [{ position: 10 }]                      // 'Flight' 섹션 필드 (→ 어노테이션 탭: @UI.identification)
      @UI.selectionField: [{ position: 10 }]                      // 필터 바 (→ 어노테이션 탭: @UI.selectionField)
      @ObjectModel.text.element: ['CarrierName']                  // ID의 텍스트 = CarrierName (→ 어노테이션 탭: @ObjectModel.text.element)
      @UI.textArrangement: #TEXT_FIRST                            // "이름 (ID)" 형태 (→ 어노테이션 탭: @UI.textArrangement)
  key CarrierID              : /dmo/carrier_id;

      @UI.lineItem:       [{ position: 20, importance: #HIGH }]
      @UI.identification: [{ position: 20 }]
  key ConnectionID           : /dmo/connection_id;

      @UI.lineItem:       [{ position: 30, importance: #HIGH }]
      @UI.identification: [{ position: 30 }]
      @UI.selectionField: [{ position: 20 }]
  key FlightDate             : /dmo/flight_date;

      @UI.hidden: true                                            // 텍스트 필드는 열 선택에서 숨김 (→ 어노테이션 탭: @UI.hidden)
      @Search.defaultSearchElement: true                          // 검색 대상 (→ 어노테이션 탭: @Search.defaultSearchElement)
      CarrierName            : /dmo/carrier_name;

      @UI.lineItem:       [{ position: 40, importance: #MEDIUM }]
      @UI.identification: [{ position: 40 }]
      @UI.selectionField: [{ position: 30 }]
      @Search.defaultSearchElement: true
      DepartureAirport       : /dmo/airport_from_id;

      @UI.lineItem:       [{ position: 50, importance: #MEDIUM }]
      @UI.identification: [{ position: 50 }]
      @UI.selectionField: [{ position: 40 }]
      @Search.defaultSearchElement: true
      DestinationAirport     : /dmo/airport_to_id;

      @UI.lineItem:       [{ position: 60, importance: #LOW }]
      @UI.identification: [{ position: 60 }]
      @UI.selectionField: [{ position: 50 }]
      @Search.defaultSearchElement: true
      PlaneType              : /dmo/plane_type_id;

      @UI.lineItem:       [{ position: 70, importance: #MEDIUM }]
      @UI.identification: [{ position: 70 }]
      @Semantics.amount.currencyCode: 'CurrencyCode'              // (→ 어노테이션 탭: @Semantics.amount.currencyCode)
      Price                  : /dmo/flight_price;

      CurrencyCode           : /dmo/currency_code;

      @UI.fieldGroup: [{ qualifier: 'Seats', position: 10 }]      // 'Seats' 섹션 필드 (→ 어노테이션 탭: @UI.fieldGroup)
      SeatsMax               : /dmo/plane_seats_max;

      @UI.dataPoint: { qualifier:          'SeatsProgress',       // 진행 막대 정의 (→ 어노테이션 탭: @UI.dataPoint)
                       title:              'Seats Occupied',
                       targetValueElement: 'SeatsMax',            // 100%에 해당하는 값 = 최대 좌석
                       visualization:      #PROGRESS,             // 진행 막대로 표시
                       criticality:        'UtilizationCriticality' }  // 막대 색 = 신호등 값
      @UI.lineItem:   [{ position: 90, importance: #HIGH, type: #AS_DATAPOINT, valueQualifier: 'SeatsProgress', label: 'Seats' }]  // 목록에 진행 막대
      @UI.fieldGroup: [{ qualifier: 'Seats', position: 20 }]
      SeatsOccupied          : /dmo/plane_seats_occupied;

      @EndUserText.label: 'Free Seats'                            // (→ 어노테이션 탭: @EndUserText.label)
      @UI.fieldGroup: [{ qualifier: 'Seats', position: 30 }]
      SeatsFree              : /dmo/plane_seats_max;

      @EndUserText.label: 'Utilization (%)'
      @UI.lineItem:   [{ position: 80, importance: #HIGH, criticality: 'UtilizationCriticality' }]   // 숫자를 신호등 색으로
      @UI.fieldGroup: [{ qualifier: 'Seats', position: 40, criticality: 'UtilizationCriticality' }]
      UtilizationPct         : abap.dec( 5, 2 );

      @EndUserText.label: 'Utilization Criticality'
      @UI.hidden: true                                            // 색 계산용 값은 화면에 노출하지 않음
      UtilizationCriticality : abap.int1;
}
```

왜 이렇게 쓰나
- **어노테이션 위치**: openSAP 예제는 UI 어노테이션이 없는 custom entity를 그대로 노출했고("UI 어노테이션이 없어서 열이 안 보인다"), 이 문제는 엔터티 소스 안에 직접 넣었습니다. 메타데이터 확장(MDE)으로 빼려면 엔터티에 `@Metadata.allowExtensions: true`를 붙이고 `annotate entity ZRAP_CE_FLIGHT_### with { ... }`를 만드는데, **custom entity에 MDE를 붙이는 공식 예제는 로컬 자료에서 확인하지 못했습니다**(실제 시스템에서 확인 필요). 확실한 방법인 엔터티 직접 기술을 정답으로 했습니다.
- **진행 막대**: `@UI.dataPoint`의 `visualization: #PROGRESS` + `targetValueElement`는 Flight Reference Scenario의 Agency Review(`HelpfulCount` / `HelpfulTotal`)와 같은 패턴입니다. 목록에서는 같은 요소의 `@UI.lineItem`에 `type: #AS_DATAPOINT`를 주고, 머리글에서는 `@UI.facet`의 `#DATAPOINT_REFERENCE` + `targetQualifier`로 참조합니다. RAP110의 `RemainingDaysToFlight`처럼 고정 목표 값(`targetValue`)을 쓰는 방식도 있습니다.
- **신호등**: `criticality: '요소이름'`은 그 요소 값 0(회색)/1(빨강)/2(노랑)/3(초록)으로 색을 정합니다. 그래서 2단계에서 `criticality` 상수를 0~3으로 정의했습니다. 값을 ABAP에서 계산하는 것이 custom entity의 장점입니다(view entity라면 CASE 식).
- **텍스트**: `@ObjectModel.text.element`는 같은 엔터티 안의 텍스트 요소를 가리킵니다. custom entity에는 연관(`_Carrier.Name`) 경로를 쓸 수 없으므로 텍스트를 직접 요소로 만들어 클래스에서 채웁니다.
- `@Search.searchable: true`를 붙이면 OData `$search`가 허용되고 그 값이 `get_search_expression( )`으로 들어옵니다. custom entity에서는 퍼지 검색 같은 DB 기능이 자동으로 붙지 않고 **5단계의 `apply_search`가 검색 의미를 결정**합니다.

자주 나는 오류와 해결
- `@UI.lineItem`의 `valueQualifier`와 `@UI.dataPoint`의 `qualifier`가 다르면 진행 막대 대신 빈 칸이 나옵니다.
- `@UI.facet`을 키가 아닌 요소에 붙여도 되지만, 엔터티에 한 번만 있어야 합니다. 보통 첫 요소 위에 둡니다.

</details>

#### 7단계. 값 도움말: CDS 값 도움말 뷰 + custom entity 값 도움말

요구사항
1. `CarrierID` 필터·필드의 값 도움말로 표준 뷰 `/DMO/I_Carrier_StdVH`(요소 `AirlineID`)를 연결합니다.
2. `DepartureAirport`, `DestinationAirport`에는 `/DMO/I_Airport_StdVH`(요소 `AirportID`)를 연결합니다.
3. `PlaneType`의 값 도움말은 **custom entity로 직접 만듭니다**.
   - custom entity `ZRAP_CE_PLANE_VH_###`: 키 `PlaneType`(`/dmo/plane_type_id`), `FlightCount`(`abap.int4`, 라벨 `Number of Flights`), `MaxSeats`(`/dmo/plane_seats_max`, 라벨 `Max. Seats`). 쿼리 클래스 `ZCL_RAP_CE_PLANE_VH_###`. 목록 열(`@UI.lineItem`)과 검색 가능 지정.
   - 클래스는 `/DMO/FLIGHT`를 기종별로 집계(`COUNT(*)`, `MAX( seats_max )`)한 뒤, 6단계와 같은 원리로 SQL 문자열 필터 → 검색 → 건수 → 정렬 → 페이징을 처리합니다.
4. 1단계 custom entity의 `PlaneType`에 이 custom entity를 값 도움말로 연결합니다.

**직접 추가할 어노테이션**
- `@Consumption.valueHelpDefinition` — 필드에 값 도움말 엔터티와 대응 요소를 지정.
- `@ObjectModel.query.implementedBy` — 값 도움말 custom entity의 쿼리 클래스.
- `@Search.searchable` / `@Search.defaultSearchElement` — 값 도움말 대화상자 안의 검색창.
- `@UI.lineItem` — 값 도움말 대화상자의 열.
- `@EndUserText.label` — 계산 요소 라벨.

**확인**
- 필터 바의 항공사 입력란 옆 값 도움말 버튼 → 항공사 목록(이름 포함).
- 기종 값 도움말 → 기종별 항공편 수/최대 좌석 목록. 대화상자 검색창에 `A3` 입력 → A3로 시작/포함하는 기종만.
- 서비스 바인딩 화면에서 엔터티 목록에 값 도움말 엔터티가 자동으로 추가되어 보입니다(8단계).

<details><summary>정답·해설</summary>

값 도움말 custom entity:

```cds
@EndUserText.label: 'Plane type value help'
@ObjectModel.query.implementedBy: 'ABAP:ZCL_RAP_CE_PLANE_VH_###'   // 값 도움말 데이터도 ABAP이 만듦 (→ 어노테이션 탭: @ObjectModel.query.implementedBy)
@Search.searchable: true                                              // 값 도움말 대화상자 검색창 (→ 어노테이션 탭: @Search.searchable)
define custom entity ZRAP_CE_PLANE_VH_###
{
      @UI.lineItem: [{ position: 10 }]                                // 대화상자 열 (→ 어노테이션 탭: @UI.lineItem)
      @Search.defaultSearchElement: true                              // 검색 대상 (→ 어노테이션 탭: @Search.defaultSearchElement)
  key PlaneType   : /dmo/plane_type_id;

      @UI.lineItem: [{ position: 20 }]
      @EndUserText.label: 'Number of Flights'                         // (→ 어노테이션 탭: @EndUserText.label)
      FlightCount : abap.int4;

      @UI.lineItem: [{ position: 30 }]
      @EndUserText.label: 'Max. Seats'
      MaxSeats    : /dmo/plane_seats_max;
}
```

값 도움말 쿼리 클래스:

```abap
CLASS zcl_rap_ce_plane_vh_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_rap_query_provider.
    TYPES tt_plane TYPE STANDARD TABLE OF zrap_ce_plane_vh_### WITH EMPTY KEY.
  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.


CLASS zcl_rap_ce_plane_vh_### IMPLEMENTATION.

  METHOD if_rap_query_provider~select.
    DATA lt_planes TYPE tt_plane.

    " 1) 기종별 집계 (DB에서 한 번)
    SELECT FROM /dmo/flight
      FIELDS plane_type_id    AS planetype,
             COUNT( * )       AS flightcount,
             MAX( seats_max ) AS maxseats
      GROUP BY plane_type_id
      INTO CORRESPONDING FIELDS OF TABLE @lt_planes.

    " 2) SQL 문자열 필터 (요소 이름 기준이라 내부 테이블에 적용)
    DATA(lv_sql_filter) = io_request->get_filter( )->get_as_sql_string( ).
    IF lv_sql_filter IS NOT INITIAL.
      DATA(lt_source) = lt_planes.
      SELECT * FROM @lt_source AS planes
        WHERE (lv_sql_filter)
        INTO TABLE @lt_planes.
    ENDIF.

    " 3) 검색 (동적 SQL 없이 CS 비교)
    DATA(lv_search) = condense( replace( val = replace( val = io_request->get_search_expression( )
                                                        sub = `"` with = `` occ = 0 )
                                         sub = `*` with = `` occ = 0 ) ).
    IF lv_search IS NOT INITIAL.
      DELETE lt_planes WHERE NOT planetype CS lv_search.
    ENDIF.

    " 4) 건수
    IF io_request->is_total_numb_of_rec_requested( ).
      io_response->set_total_number_of_records( lines( lt_planes ) ).
    ENDIF.

    " 5) 정렬 + 페이징 + 데이터
    IF io_request->is_data_requested( ).
      DATA(lt_sort) = VALUE abap_sortorder_tab( FOR ls_sort IN io_request->get_sort_elements( )
                                                ( name       = to_upper( ls_sort-element_name )
                                                  descending = ls_sort-descending ) ).
      IF lt_sort IS INITIAL.
        lt_sort = VALUE #( ( name = 'PLANETYPE' ) ).
      ENDIF.
      SORT lt_planes BY (lt_sort).

      DATA(lv_offset)    = io_request->get_paging( )->get_offset( ).
      DATA(lv_page_size) = io_request->get_paging( )->get_page_size( ).
      IF lv_offset > 0.
        IF lv_offset >= lines( lt_planes ).
          CLEAR lt_planes.
        ELSE.
          DELETE lt_planes FROM 1 TO CONV i( lv_offset ).
        ENDIF.
      ENDIF.
      IF lv_page_size <> if_rap_query_paging=>page_size_unlimited
         AND lv_page_size > 0
         AND lines( lt_planes ) > lv_page_size.
        DELETE lt_planes FROM CONV i( lv_page_size + 1 ).
      ENDIF.

      io_response->set_data( lt_planes ).
    ENDIF.
  ENDMETHOD.

ENDCLASS.
```

`ZRAP_CE_FLIGHT_###`에서 바꿀 요소 3개(나머지는 6단계와 같음):

```cds
      @Consumption.valueHelpDefinition: [{ entity: { name: '/DMO/I_Carrier_StdVH', element: 'AirlineID' } }]  // 항공사 값 도움말 (→ 어노테이션 탭: @Consumption.valueHelpDefinition)
      @UI.lineItem:       [{ position: 10, importance: #HIGH }]
      @UI.identification: [{ position: 10 }]
      @UI.selectionField: [{ position: 10 }]
      @ObjectModel.text.element: ['CarrierName']
      @UI.textArrangement: #TEXT_FIRST
  key CarrierID              : /dmo/carrier_id;
```

```cds
      @Consumption.valueHelpDefinition: [{ entity: { name: '/DMO/I_Airport_StdVH', element: 'AirportID' } }]
      @UI.lineItem:       [{ position: 40, importance: #MEDIUM }]
      @UI.identification: [{ position: 40 }]
      @UI.selectionField: [{ position: 30 }]
      @Search.defaultSearchElement: true
      DepartureAirport       : /dmo/airport_from_id;

      @Consumption.valueHelpDefinition: [{ entity: { name: '/DMO/I_Airport_StdVH', element: 'AirportID' } }]
      @UI.lineItem:       [{ position: 50, importance: #MEDIUM }]
      @UI.identification: [{ position: 50 }]
      @UI.selectionField: [{ position: 40 }]
      @Search.defaultSearchElement: true
      DestinationAirport     : /dmo/airport_to_id;
```

```cds
      @Consumption.valueHelpDefinition: [{ entity: { name: 'ZRAP_CE_PLANE_VH_###', element: 'PlaneType' } }]  // custom entity 값 도움말
      @UI.lineItem:       [{ position: 60, importance: #LOW }]
      @UI.identification: [{ position: 60 }]
      @UI.selectionField: [{ position: 50 }]
      @Search.defaultSearchElement: true
      PlaneType              : /dmo/plane_type_id;
```

왜 이렇게 쓰나
- 값 도움말 엔터티는 **view entity든 custom entity든 같은 어노테이션**(`@Consumption.valueHelpDefinition`)으로 연결합니다. openSAP Week 5는 원격 OData(ES5)의 여행사를 custom entity로 감싸 Travel의 `AgencyID` 값 도움말로 썼습니다. 즉 "DB에 없는 데이터를 값 도움말로 보여 주기"가 custom entity의 대표 용도입니다.
- openSAP 해설에 따르면 값 도움말로 쓰인 엔터티는 서비스 바인딩의 엔터티 목록에 **자동으로 추가**됩니다(기술 이름으로). 이름을 예쁘게 하려면 서비스 정의에 `expose`로 별칭을 줍니다(8단계).
- `/DMO/I_Airport_StdVH`의 키 요소 이름은 `AirportID`입니다(Flight Reference Scenario `reuse` 패키지 소스에서 확인). 시스템 버전이 다르면 F3으로 열어 한 번 더 확인하세요.
- 값 도움말 클래스도 `is_data_requested`/`is_total_numb_of_rec_requested`를 지켜야 합니다. 값 도움말 대화상자는 보통 `$count=true`와 `$top`을 함께 보냅니다.

자주 나는 오류와 해결
- 값 도움말 대화상자가 "데이터 없음"이면 집계 SELECT의 별칭이 custom entity 요소 이름과 다른지(`INTO CORRESPONDING FIELDS`) 확인하세요.

</details>

#### 8단계. 서비스 정의·바인딩과 Fiori Preview에서 쿼리 동작 확인

요구사항
1. 서비스 정의 `ZRAP_UI_FLIGHT_CE_###`: `ZRAP_CE_FLIGHT_###`를 `Flight`로, `ZRAP_CE_PLANE_VH_###`를 `PlaneTypeVH`로 노출합니다.
2. 서비스 바인딩 `ZRAP_UI_FLIGHT_CE_O4_###`: Binding Type `OData V4 - UI`, Publish.
3. 아래 시나리오를 차례로 실행해 select의 각 분기가 맞게 동작하는지 확인하고, 각 시나리오가 `io_request`의 어떤 메서드를 거치는지 표로 정리합니다.
   - (a) Go만 누르기, (b) 항공사 필터, (c) 검색, (d) 이용률 열 내림차순 정렬, (e) 끝까지 스크롤, (f) 행 클릭(Object Page), (g) 기종 값 도움말.
4. 브라우저에서 OData URL을 직접 호출해 `$count`, `$top`, `$skip`, `$orderby`, `$filter`, `$search`, `$select`를 확인합니다(서비스 URL은 바인딩 화면의 Service URL 링크).
5. 디버깅: `select` 첫 줄에 중단점(외부 중단점, ADT의 Toggle Breakpoint)을 걸고 Preview에서 Go → `io_request`의 값을 Variables 창에서 확인합니다.

**확인**
- 각 시나리오의 화면 결과와 디버거에서 본 값(`get_paging( )`의 offset/page size, 필터 문자열)이 아래 정답 표와 맞는지 확인합니다.

<details><summary>정답·해설</summary>

```cds
@EndUserText.label: 'Flight utilization service'
define service ZRAP_UI_FLIGHT_CE_### {
  expose ZRAP_CE_FLIGHT_###   as Flight;
  expose ZRAP_CE_PLANE_VH_### as PlaneTypeVH;
}
```

시나리오와 `io_request` 메서드

| 시나리오 | 대략적인 OData 요청 | 거치는 메서드 / 기대 결과 |
|---|---|---|
| (a) Go | `Flight?$count=true&$orderby=FlightDate desc&$select=...&$skip=0&$top=30` | `is_data_requested`=참, `is_total_numb_of_rec_requested`=참, `get_sort_elements`=FLIGHTDATE desc(presentationVariant), page size 30 정도 |
| (b) 항공사 필터 | `$filter=CarrierID eq 'AA'` | `get_as_ranges`에 `CARRIERID`, `get_as_sql_string`에 `CARRIERID = 'AA'` 형태 → DB push-down |
| (c) 검색 | `$search=FRA` | `get_search_expression` = `FRA`(따옴표가 붙을 수 있음) → `apply_search` |
| (d) 정렬 | `$orderby=UtilizationPct desc` | `get_sort_elements` → `apply_sort` |
| (e) 스크롤 | `$skip=30&$top=30` | offset 30 → 다음 페이지. 건수는 그대로 |
| (f) Object Page | `Flight(CarrierID='AA',ConnectionID='0017',FlightDate=...)` | 키 3개 필터가 걸린 select 호출. 건수 요청은 없음 |
| (g) 기종 값 도움말 | `PlaneTypeVH?$count=true&$top=...` | 값 도움말 클래스의 select |

브라우저 직접 호출 예(서비스 URL 뒤에 붙임)
- `Flight/$count` → 숫자만. `is_data_requested`=거짓이므로 `set_data`를 부르면 안 됩니다.
- `Flight?$top=3&$skip=2&$count=true&$orderby=UtilizationPct desc`
- `Flight?$filter=UtilizationPct ge 80 and CarrierID eq 'LH'`
- `Flight?$select=CarrierID,ConnectionID,FlightDate` → `CARRIERNAME`이 요청되지 않아 `add_carrier_names`가 호출되지 않는 것을 디버거로 확인.

왜 이렇게 쓰나
- custom entity는 BDEF가 없어도 서비스에 노출할 수 있습니다. 읽기 전용 엔터티이므로 Preview에 Create/Edit 버튼이 없습니다.
- 위 OData 요청 형태는 Fiori Elements 버전에 따라 조금씩 다릅니다(예: `$select` 목록, 기본 page size). 정확한 값은 디버거나 브라우저 개발자 도구의 Network 탭에서 확인하세요(실제 시스템에서 확인 필요).

자주 나는 오류와 해결
- Preview에서 "The query implementation class ... does not exist" 류의 오류: `@ObjectModel.query.implementedBy` 문자열의 클래스 이름 오타, 또는 `ABAP:` 접두어 누락.
- 스크롤 시 같은 행이 반복: 페이징 미구현(3단계 상태). 건수가 30에서 멈춤: 페이징 **후** 건수를 셌음.

</details>

#### 9단계. ABAP Unit으로 쿼리 로직 검증하기

요구사항
1. `ZCL_RAP_CE_FLIGHT_###`의 **Test Classes** 탭에 테스트 클래스 `ltc_flight_query`(`FOR TESTING DURATION SHORT RISK LEVEL HARMLESS`)를 만듭니다.
2. DB 없이 검증하는 테스트:
   - `calc_utilization`: 150/200 → 75.00, 1/3 → 33.33, 최대 0 → 0.
   - `get_criticality`: 80 → 3, 79.99 → 2, 10 → 1.
   - `apply_paging`: 10건에서 offset 2, size 3 → 3건이고 첫 행이 원래 3번째 행. size `page_size_unlimited` → offset 이후 전부.
   - `apply_sql_filter`: `UTILIZATIONPCT >= 50` → 해당 행만.
   - `apply_sort`: `UTILIZATIONPCT` 내림차순 → 첫 행이 최대.
3. SQL 테스트 더블(`cl_osql_test_environment`)로 `/DMO/FLIGHT`, `/DMO/CONNECTION`, `/DMO/CARRIER`를 대체하고 `read_flights`를 검증:
   - 테스트 데이터 3건(AA 2건, LH 1건) 입력 → range `CARRIERID = AA` → 2건, 항공사 이름이 채워짐, 이용률 계산이 맞음.
4. `select` 자체는 `io_request` 구현이 필요하므로 이 단계에서는 테스트하지 않습니다(해설 참고).

**확인**
- 클래스에서 Ctrl+Shift+F10(Run As → ABAP Unit Test) → 모든 테스트 초록.

<details><summary>정답·해설</summary>

```abap
CLASS ltc_flight_query DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    CLASS-DATA sql_env TYPE REF TO if_osql_test_environment.
    DATA cut TYPE REF TO zcl_rap_ce_flight_###.

    CLASS-METHODS class_setup.
    CLASS-METHODS class_teardown.
    METHODS setup.

    METHODS utilization_is_rounded     FOR TESTING.
    METHODS utilization_zero_max_seats FOR TESTING.
    METHODS criticality_thresholds     FOR TESTING.
    METHODS paging_offset_and_size     FOR TESTING.
    METHODS paging_unlimited           FOR TESTING.
    METHODS sql_filter_on_calc_field   FOR TESTING.
    METHODS sort_descending            FOR TESTING.
    METHODS read_flights_with_range    FOR TESTING.

    METHODS build_ten_rows
      RETURNING VALUE(result) TYPE zcl_rap_ce_flight_###=>tt_flight.
ENDCLASS.


CLASS ltc_flight_query IMPLEMENTATION.

  METHOD class_setup.
    sql_env = cl_osql_test_environment=>create(
                i_dependency_list = VALUE #( ( '/DMO/FLIGHT' )
                                             ( '/DMO/CONNECTION' )
                                             ( '/DMO/CARRIER' ) ) ).
  ENDMETHOD.

  METHOD class_teardown.
    sql_env->destroy( ).
  ENDMETHOD.

  METHOD setup.
    sql_env->clear_doubles( ).
    cut = NEW #( ).
  ENDMETHOD.

  METHOD build_ten_rows.
    " ConnectionID 1~10, 이용률 10, 20, ..., 100
    DO 10 TIMES.
      APPEND VALUE #( carrierid      = 'AA'
                      connectionid   = CONV #( sy-index )
                      flightdate     = '20300101'
                      utilizationpct = sy-index * 10 ) TO result.
    ENDDO.
  ENDMETHOD.

  METHOD utilization_is_rounded.
    cl_abap_unit_assert=>assert_equals(
      act = zcl_rap_ce_flight_###=>calc_utilization( seats_max = 200 seats_occupied = 150 )
      exp = CONV zrap_ce_flight_###-utilizationpct( '75.00' ) ).
    cl_abap_unit_assert=>assert_equals(
      act = zcl_rap_ce_flight_###=>calc_utilization( seats_max = 3 seats_occupied = 1 )
      exp = CONV zrap_ce_flight_###-utilizationpct( '33.33' ) ).
  ENDMETHOD.

  METHOD utilization_zero_max_seats.
    cl_abap_unit_assert=>assert_initial(
      zcl_rap_ce_flight_###=>calc_utilization( seats_max = 0 seats_occupied = 5 ) ).
  ENDMETHOD.

  METHOD criticality_thresholds.
    cl_abap_unit_assert=>assert_equals(
      act = zcl_rap_ce_flight_###=>get_criticality( '80.00' )
      exp = zcl_rap_ce_flight_###=>criticality-positive ).
    cl_abap_unit_assert=>assert_equals(
      act = zcl_rap_ce_flight_###=>get_criticality( '79.99' )
      exp = zcl_rap_ce_flight_###=>criticality-critical ).
    cl_abap_unit_assert=>assert_equals(
      act = zcl_rap_ce_flight_###=>get_criticality( '10.00' )
      exp = zcl_rap_ce_flight_###=>criticality-negative ).
  ENDMETHOD.

  METHOD paging_offset_and_size.
    DATA(lt_rows) = build_ten_rows( ).
    zcl_rap_ce_flight_###=>apply_paging( EXPORTING iv_offset    = 2
                                                   iv_page_size = 3
                                         CHANGING  ct_flights   = lt_rows ).
    cl_abap_unit_assert=>assert_equals( act = lines( lt_rows ) exp = 3 ).
    cl_abap_unit_assert=>assert_equals( act = lt_rows[ 1 ]-connectionid
                                        exp = CONV /dmo/connection_id( 3 ) ).
  ENDMETHOD.

  METHOD paging_unlimited.
    DATA(lt_rows) = build_ten_rows( ).
    zcl_rap_ce_flight_###=>apply_paging( EXPORTING iv_offset    = 4
                                                   iv_page_size = if_rap_query_paging=>page_size_unlimited
                                         CHANGING  ct_flights   = lt_rows ).
    cl_abap_unit_assert=>assert_equals( act = lines( lt_rows ) exp = 6 ).
  ENDMETHOD.

  METHOD sql_filter_on_calc_field.
    DATA(lt_rows) = build_ten_rows( ).
    zcl_rap_ce_flight_###=>apply_sql_filter( EXPORTING iv_sql_filter = `UTILIZATIONPCT >= 50`
                                             CHANGING  ct_flights    = lt_rows ).
    cl_abap_unit_assert=>assert_equals( act = lines( lt_rows ) exp = 6 ).
  ENDMETHOD.

  METHOD sort_descending.
    DATA(lt_rows) = build_ten_rows( ).
    zcl_rap_ce_flight_###=>apply_sort(
      EXPORTING it_sort    = VALUE #( ( name = 'UTILIZATIONPCT' descending = abap_true ) )
      CHANGING  ct_flights = lt_rows ).
    cl_abap_unit_assert=>assert_equals( act = lt_rows[ 1 ]-utilizationpct
                                        exp = CONV zrap_ce_flight_###-utilizationpct( 100 ) ).
  ENDMETHOD.

  METHOD read_flights_with_range.
    DATA lt_flight     TYPE STANDARD TABLE OF /dmo/flight WITH EMPTY KEY.
    DATA lt_connection TYPE STANDARD TABLE OF /dmo/connection WITH EMPTY KEY.
    DATA lt_carrier    TYPE STANDARD TABLE OF /dmo/carrier WITH EMPTY KEY.

    lt_flight = VALUE #(
      ( carrier_id = 'AA' connection_id = '0017' flight_date = '20300101'
        seats_max = 200 seats_occupied = 180 price = '100.00' currency_code = 'USD' )
      ( carrier_id = 'AA' connection_id = '0017' flight_date = '20300102'
        seats_max = 200 seats_occupied = 50  price = '100.00' currency_code = 'USD' )
      ( carrier_id = 'LH' connection_id = '0400' flight_date = '20300101'
        seats_max = 100 seats_occupied = 60  price = '200.00' currency_code = 'EUR' ) ).
    lt_connection = VALUE #(
      ( carrier_id = 'AA' connection_id = '0017' airport_from_id = 'JFK' airport_to_id = 'SFO' )
      ( carrier_id = 'LH' connection_id = '0400' airport_from_id = 'FRA' airport_to_id = 'JFK' ) ).
    lt_carrier = VALUE #(
      ( carrier_id = 'AA' name = 'American Airlines' currency_code = 'USD' )
      ( carrier_id = 'LH' name = 'Lufthansa'         currency_code = 'EUR' ) ).

    sql_env->insert_test_data( lt_flight ).
    sql_env->insert_test_data( lt_connection ).
    sql_env->insert_test_data( lt_carrier ).

    DATA(lt_result) = cut->read_flights(
      it_ranges = VALUE #( ( name  = 'CARRIERID'
                             range = VALUE #( ( sign = 'I' option = 'EQ' low = 'AA' ) ) ) ) ).

    cl_abap_unit_assert=>assert_equals( act = lines( lt_result ) exp = 2 ).

    DATA(ls_first) = lt_result[ flightdate = '20300101' ].
    cl_abap_unit_assert=>assert_equals( act = ls_first-carriername
                                        exp = CONV /dmo/carrier_name( 'American Airlines' ) ).
    cl_abap_unit_assert=>assert_equals( act = ls_first-utilizationpct
                                        exp = CONV zrap_ce_flight_###-utilizationpct( 90 ) ).
    cl_abap_unit_assert=>assert_equals( act = ls_first-utilizationcriticality
                                        exp = CONV zrap_ce_flight_###-utilizationcriticality(
                                                zcl_rap_ce_flight_###=>criticality-positive ) ).
    cl_abap_unit_assert=>assert_equals( act = ls_first-departureairport
                                        exp = CONV /dmo/airport_from_id( 'JFK' ) ).
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나
- `cl_osql_test_environment=>create( i_dependency_list = ... )`는 ABAP SQL이 읽는 테이블을 테스트 더블로 바꿉니다(ABAP cheat sheet "ABAP Unit Tests"). `clear_doubles( )`로 테스트마다 비우고, `insert_test_data( )`로 필요한 행만 넣습니다. 그래서 실제 `/DMO/` 데이터가 바뀌어도 테스트 결과가 변하지 않습니다.
- `select`를 직접 테스트하려면 `if_rap_query_request`, `if_rap_query_filter`, `if_rap_query_paging`, `if_rap_query_response`를 구현한 가짜 객체(또는 `cl_abap_testdouble`)가 필요합니다. 인터페이스 메서드가 많고 릴리스 상태도 확인하지 못했기 때문에(실제 시스템에서 확인 필요), 이 문제는 **로직을 도우미 메서드로 분리해 그쪽을 테스트**하는 방법을 택했습니다. 이것이 2단계에서 구조를 나눈 이유입니다.
- 테스트 클래스는 테스트 대상 클래스의 PUBLIC 메서드만 쓰므로 `FRIENDS` 선언이 필요 없습니다.

자주 나는 오류와 해결
- `/DMO/` 테이블을 더블로 만들 수 없다는 오류가 나면, 대신 `/DMO/I_Flight` 등 CDS 뷰를 읽도록 바꾸고 `cl_cds_test_environment`를 쓰세요.
- `connectionid = CONV #( sy-index )`에서 NUMC 변환 경고가 날 수 있지만 동작에는 문제 없습니다.

</details>

#### 10단계. (심화) 관리형 BO에서 custom entity 쓰기와 읽기 전용 모델 비교

요구사항
1. R-01의 Booking 루트 뷰 `ZRAP_R_BOOKING_###`에 custom entity로 가는 연관 `_FlightUtil`을 추가합니다(조건: 항공사·노선·운항일 3개 키). Booking의 별칭이 `CarrierID`, `ConnectionID`, `FlightDate`가 아니면 R-01에서 정한 이름에 맞춥니다.
2. Booking 프로젝션 `ZRAP_C_BOOKING_###`의 `FlightDate`에 custom entity를 **값 도움말**로 연결합니다. 값 도움말에서 항공편을 고르면 항공사·노선이 함께 채워지고, 이미 입력된 항공사·노선으로 목록이 걸러지도록 `additionalBinding`을 사용합니다.
3. 프로젝션에서 `_FlightUtil.UtilizationPct as ...` 처럼 **연관 경로로 custom entity 필드를 꺼내는 것**이 되는지 활성화로 시험해 보고, 결과를 기록합니다.
4. 아래 세 가지 읽기 전용 모델을 비교하는 표를 직접 작성합니다: CDS view entity / custom entity(+ unmanaged query) / CDS table function(AMDP). 항목: 데이터 출처, 계산 위치, 필터·정렬·페이징 처리 주체, 성능, 트랜잭션(BDEF) 가능 여부, 대표 용도.

**직접 추가할 어노테이션**
- `@Consumption.valueHelpDefinition` (+ `additionalBinding`, `usage`) — 값 도움말 결과로 다른 필드를 함께 채우고, 다른 필드 값으로 값 도움말을 거르기.

**확인**
- Booking Object Page에서 운항일 값 도움말 → 이용률·진행 막대가 있는 항공편 목록, 선택하면 항공사·노선·운항일이 함께 채워집니다.
- 3번 시험에서 활성화 오류가 나면 그 메시지를 기록합니다(정답 해설의 openSAP 메시지와 비교).

<details><summary>정답·해설</summary>

`ZRAP_R_BOOKING_###`에 추가(기존 연관 아래, 요소 목록 끝에 `_FlightUtil` 노출):

```cds
  association [0..1] to ZRAP_CE_FLIGHT_### as _FlightUtil on  $projection.CarrierID    = _FlightUtil.CarrierID
                                                          and $projection.ConnectionID = _FlightUtil.ConnectionID
                                                          and $projection.FlightDate   = _FlightUtil.FlightDate
```

```cds
      /* Associations */
      _FlightUtil
```

`ZRAP_C_BOOKING_###`의 `FlightDate` 요소:

```cds
      @Consumption.valueHelpDefinition: [{ entity: { name: 'ZRAP_CE_FLIGHT_###', element: 'FlightDate' },   // custom entity 값 도움말 (→ 어노테이션 탭: @Consumption.valueHelpDefinition)
                                           additionalBinding: [ { localElement: 'CarrierID',    element: 'CarrierID',    usage: #FILTER_AND_RESULT },
                                                                { localElement: 'ConnectionID', element: 'ConnectionID', usage: #FILTER_AND_RESULT } ] }]
      FlightDate,
```

3번 시험 결과(예상)
- openSAP Week 5 Unit 5에서 Travel 인터페이스 뷰의 `_Agency` 연관을 custom entity로 바꾼 뒤, 프로젝션에 `_Agency.Name as AgencyName`이 남아 있으면 **"Association "_AGENCY" of entity "ZCE_RAP_AGENCY_####" cannot be used"** 오류가 났고, 해설은 "custom entity는 프로젝션의 일부가 될 수 없으므로(경로로 필드를 꺼낼 수 없으므로) 그 필드를 지웠다"고 설명합니다. 같은 오류가 날 것으로 예상합니다. 최신 릴리스에서 허용 범위가 바뀌었는지는 확인하지 못했습니다(실제 시스템에서 확인 필요).
- 따라서 **R 뷰의 연관 자체는 정의할 수 있고**(openSAP과 ABAP 릴리스 노트 "custom entity를 연관 대상으로 하는 경우의 ON 조건 규칙"이 이를 전제), UI에 custom entity 데이터를 보여 주는 확실한 방법은 ① 값 도움말, ② 서비스에 custom entity를 별도 엔터티 셋으로 노출해 따로 조회, ③ 행동 구현에서 쿼리 클래스의 공개 메서드를 직접 호출(openSAP은 `validateAgency`에서 `get_agencies( )`를 호출)입니다. 프로젝션에서 `_FlightUtil` 연관을 `redirected` 없이 그대로 노출해 Object Page 섹션으로 보여 줄 수 있는지는 확인하지 못했습니다(실제 시스템에서 확인 필요).

읽기 전용 모델 비교

| 항목 | CDS view entity | custom entity + unmanaged query | CDS table function (AMDP) |
|---|---|---|---|
| 데이터 출처 | DB 테이블/뷰(SQL) | 무엇이든: DB, 원격 OData/HTTP, 메모리 계산, 로그 API | DB(HANA SQLScript) |
| 계산 위치 | DB(CDS 식, CASE, 집계) | ABAP 애플리케이션 서버 | DB(SQLScript) |
| 필터/정렬/페이징/건수 | 프레임워크가 자동으로 SQL에 반영 | **개발자가 select에서 직접 구현**(이 문제 3~5단계) | 프레임워크가 자동(함수 결과에 SQL 적용) |
| 검색 | `@Search` + DB 검색 | `get_search_expression( )`으로 직접 | view entity로 감싸면 가능 |
| 대량 데이터 성능 | 가장 좋음 | 구현에 따라 다름(ABAP으로 가져오면 느림) | 좋음(복잡한 DB 로직) |
| DCL 권한 | 적용 | 적용 안 됨(클래스에서 직접) | view entity로 감싸서 적용 |
| 트랜잭션(BDEF) | 관리형/비관리형 BO의 데이터 모델 | 비관리형 BO의 데이터 모델로도 사용 가능(`root custom entity`) | 직접 BO로 쓰지 않음 |
| 대표 용도 | 일반 목록/보고서/BO 모델 | 원격 서비스 래핑(openSAP), 애플리케이션 로그 조회(SAP 예제 `zapp_cl_show_appl_log`), ABAP 계산이 꼭 필요한 값 | SQL로 표현 어려운 DB 계산(window 함수 조합, 반복 로직) |
| 클라우드(ABAP Cloud) | 가능 | 가능 | 가능(AMDP는 HANA 전용) |

- 결론: **DB에 있고 SQL로 계산 가능하면 view entity**가 기본입니다. 이 문제의 이용률도 사실 CDS 식으로 계산할 수 있으므로, 실무라면 view entity가 더 낫습니다. custom entity는 "DB 밖의 데이터" 또는 "ABAP 로직이 꼭 필요한 값"에 씁니다. 이 문제는 select의 모든 기능을 연습하려고 일부러 custom entity를 썼습니다.
- table function은 이 문제집 범위를 넘으므로 비교만 했습니다. 문법은 다루지 않습니다.

</details>

### R-09. Singleton BO로 설정 테이블 관리 앱 만들기 (with unmanaged save, multi-inline edit) [작성] ★★★
<!-- covers: singleton root entity, I_Language left outer join on 0 = 0, max() LastChangedAtMax, composition to child, with unmanaged save (entity level), lock master, total etag, ##DRAFT_OP_NOT_REQUIRED, draft table %admin include, lock dependent by, authorization dependent by, authorization master global, get_global_authorizations, delete features instance, draft determine action Prepare with child validations, %path, %state_area, determination on modify, save_modified, cleanup_finalize, LINEITEM_REFERENCE multi-inline edit, @ObjectModel.leadingEntity.name, delivery class C, Business Configuration Maintenance Object, mbc_cp_api rap_table_cts, transport recording, EML Edit Activate CREATE BY association -->

**목표**
- 여러 행으로 된 설정 테이블 전체를 **하나의 객체(싱글턴)**로 묶어, 한 번의 Edit로 표 전체를 잠그고 여러 행을 인라인으로 고친 뒤 한 번에 저장하는 앱을 만들 수 있습니다.
- DB 테이블이 없는 가상 루트(`I_Language` 기반, `1 as SingletonID`)를 만들고, 루트에만 `with unmanaged save`를 거는 이유를 설명할 수 있습니다.
- `lock master` + `total etag`(자식 변경 시각의 최댓값)로 테이블 전체의 동시 편집을 제어할 수 있습니다.
- 자식 검증을 루트의 `Prepare`에 묶고, 메시지에 `%path`를 채워 Fiori가 올바른 행에 오류를 표시하게 할 수 있습니다.
- 납품 클래스 C(customizing) 테이블의 의미와, ADT의 Business Configuration 유지보수 객체 생성기가 만드는 전송 기록 구조를 설명할 수 있습니다.

**전제**
- R-02에서 만든 메시지 클래스 `ZRAP_MSG_###`, 예외 클래스 `ZCM_RAP_###`(CX_STATIC_CHECK 상속, `IF_ABAP_BEHV_MESSAGE` + `IF_T100_DYN_MSG`, 생성자에 `textid`, `severity` 파라미터).
- 표준 객체: `/DMO/I_Agency`, `/DMO/I_Agency_StdVH`, `I_Currency`, `I_CurrencyStdVH`, `I_Language`.
- 이 문제는 Flight Reference Scenario의 싱글턴 예제(`/DMO/I_CarriersLockSingleton_S`, `/DMO/I_Carrier_S`)를 본보기로 합니다. 막히면 ADT에서 그 객체들을 F3으로 열어 비교하세요.

**만들 객체**

| 순서 | 객체 유형 | 이름 | 역할 |
|---|---|---|---|
| 1 | Database Table | `ZRAP_CFG_###` | 여행사별 할인 규칙(납품 클래스 C) |
| 2 | ABAP Class | `ZCL_RAP_CFG_DATA_###` | 데모 데이터 입력 콘솔 |
| 3 | Message Class / Exception Class (확장) | `ZRAP_MSG_###`, `ZCM_RAP_###` | 메시지 090~093 추가 |
| 4 | Data Definition | `ZRAP_I_CFG_S_###` | 싱글턴 루트(가상) |
| 5 | Data Definition | `ZRAP_I_CFG_###` | 자식: 할인 규칙 1행 |
| 6 | Behavior Definition | `ZRAP_I_CFG_S_###` | managed + draft, 루트 unmanaged save |
| 7 | Database Table (draft) | `ZRAP_DCFG_S_###`, `ZRAP_DCFG_###` | draft 테이블 |
| 8 | ABAP Class (행동 풀) | `ZBP_RAP_I_CFG_S_###` | 핸들러 2개 + 세이버 |
| 9 | Data Definition | `ZRAP_C_CFG_S_###`, `ZRAP_C_CFG_###` | 프로젝션 |
| 10 | Behavior Definition | `ZRAP_C_CFG_S_###` | 프로젝션 BDEF |
| 11 | Metadata Extension | `ZRAP_C_CFG_S_###`, `ZRAP_C_CFG_###` | UI |
| 12 | Service Definition / Binding | `ZRAP_UI_CFG_###` / `ZRAP_UI_CFG_O4_###` | OData V4 UI |
| 13 | ABAP Class | `ZCL_RAP_CFG_EML_###` | EML 콘솔 테스트 |

#### 1단계. 설정 테이블과 데모 데이터

요구사항
1. 테이블 `ZRAP_CFG_###`를 만듭니다. 여행사(agency)마다 1행: 최대 할인율, 최대 할인 금액(통화 포함), 활성 여부, 관리 필드.

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | X | abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| agency_id | X | /dmo/agency_id | NUMC | 6 | 0 | 여행사 ID |
| max_discount_pct | | abap.dec | DEC | 5 | 2 | 최대 할인율(%) 0~50 |
| max_discount_amt | | /dmo/total_price | CURR | 16 | 2 | 최대 할인 금액, 참조 필드 `currency_code` |
| currency_code | | /dmo/currency_code | CUKY | 5 | 0 | 통화 |
| is_active | | abap_boolean | CHAR | 1 | 0 | 규칙 활성 여부 |
| local_created_by | | abp_creation_user | CHAR | 12 | 0 | 생성자 |
| local_created_at | | abp_creation_tstmpl | DEC | 21 | 7 | 생성 시각 |
| local_last_changed_by | | abp_locinst_lastchange_user | CHAR | 12 | 0 | 최종 변경자 |
| local_last_changed_at | | abp_locinst_lastchange_tstmpl | DEC | 21 | 7 | 행 최종 변경 시각(etag) |
| last_changed_at | | abp_lastchange_tstmpl | DEC | 21 | 7 | 최종 변경 시각(total etag 계산용) |

2. 납품 클래스는 **C**(customizing)로, 데이터 유지보수는 허용(`#ALLOWED`)으로 합니다.
3. 콘솔 클래스 `ZCL_RAP_CFG_DATA_###`: 테이블을 비우고 3행(070001: 10%, 100 EUR, 활성 / 070002: 5%, 50 USD, 활성 / 070003: 0%, 0 EUR, 비활성)을 넣은 뒤 건수를 출력합니다. 관리 필드도 채웁니다.

**확인**
- 테이블 활성화 성공, 콘솔 실행 후 `3 rules inserted`, Data Preview(F8)로 3행 확인.

<details><summary>정답·해설</summary>

```abap
@EndUserText.label : 'Agency discount rules (configuration)'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #C
@AbapCatalog.dataMaintenance : #ALLOWED
define table zrap_cfg_### {

  key client            : abap.clnt not null;
  key agency_id         : /dmo/agency_id not null;
  max_discount_pct      : abap.dec(5,2);
  @Semantics.amount.currencyCode : 'zrap_cfg_###.currency_code'
  max_discount_amt      : /dmo/total_price;
  currency_code         : /dmo/currency_code;
  is_active             : abap_boolean;
  local_created_by      : abp_creation_user;
  local_created_at      : abp_creation_tstmpl;
  local_last_changed_by : abp_locinst_lastchange_user;
  local_last_changed_at : abp_locinst_lastchange_tstmpl;
  last_changed_at       : abp_lastchange_tstmpl;

}
```

```abap
CLASS zcl_rap_cfg_data_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.
  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.


CLASS zcl_rap_cfg_data_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.
    DATA lt_rules TYPE STANDARD TABLE OF zrap_cfg_### WITH EMPTY KEY.

    GET TIME STAMP FIELD DATA(lv_now).
    DATA(lv_user) = cl_abap_context_info=>get_user_technical_name( ).

    lt_rules = VALUE #(
      ( agency_id = '070001' max_discount_pct = '10.00' max_discount_amt = '100.00' currency_code = 'EUR' is_active = abap_true )
      ( agency_id = '070002' max_discount_pct = '5.00'  max_discount_amt = '50.00'  currency_code = 'USD' is_active = abap_true )
      ( agency_id = '070003' max_discount_pct = '0.00'  max_discount_amt = '0.00'   currency_code = 'EUR' is_active = abap_false ) ).

    LOOP AT lt_rules ASSIGNING FIELD-SYMBOL(<ls_rule>).
      <ls_rule>-local_created_by      = lv_user.
      <ls_rule>-local_created_at      = lv_now.
      <ls_rule>-local_last_changed_by = lv_user.
      <ls_rule>-local_last_changed_at = lv_now.
      <ls_rule>-last_changed_at       = lv_now.
    ENDLOOP.

    DELETE FROM zrap_cfg_###.
    INSERT zrap_cfg_### FROM TABLE @lt_rules.

    out->write( |{ lines( lt_rules ) } rules inserted| ).
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나 — 납품 클래스 C
- `@AbapCatalog.deliveryClass : #A`는 업무(application) 데이터, `#C`는 **고객이 설정하는 customizing 데이터**입니다. C 테이블의 행은 업무 데이터가 아니라 "시스템이 어떻게 동작할지 정하는 값"이라서, 개발/품질/운영 시스템 사이에서 **전송 요청으로 옮기는 대상**입니다. 이 문제의 할인 규칙이 바로 그런 데이터입니다.
- C 테이블의 변경을 자동으로 전송 요청에 기록하는 기능은 이 문제의 수작업 BO에는 없습니다. ADT의 Business Configuration 유지보수 객체 생성기가 그 코드를 만들어 주며, 10단계에서 구조를 살펴봅니다.
- 관리 필드를 둘로 나눈 이유: `local_last_changed_at`은 **행 단위 etag**(누가 그 행을 바꿨는지), `last_changed_at`은 4단계에서 루트가 `max()`로 모아 **테이블 전체의 total etag**를 만드는 데 씁니다. Flight Reference Scenario의 `/dmo/carrier`도 같은 구성입니다.
- 실제 시스템의 여행사 ID가 070001~070003이 아니면 `/DMO/I_Agency` Data Preview로 있는 ID를 골라 바꾸세요(5단계 검증이 존재 여부를 확인합니다).

</details>

#### 2단계. 메시지와 예외 클래스 확장

요구사항
1. 메시지 클래스 `ZRAP_MSG_###`에 다음 메시지를 추가합니다(번호가 이미 쓰이고 있으면 비어 있는 번호로 바꾸고 이후 코드도 맞춥니다).
   - 090 `Agency &1: max. discount &2 % must be between 0 and 50`
   - 091 `Agency &1: max. discount amount must not be negative`
   - 092 `Currency code &1 is not valid`
   - 093 `Agency &1 does not exist`
2. 예외 클래스 `ZCM_RAP_###`에 텍스트 ID 상수 4개(`cfg_discount_out_of_range`, `cfg_amount_negative`, `cfg_currency_invalid`, `cfg_agency_unknown`), 속성 3개(`cfg_agency_id`, `cfg_discount_pct`(string), `cfg_currency`), 생성자 OPTIONAL 파라미터 3개를 추가하고 생성자에서 속성에 대입합니다. R-02에서 만든 기존 상수·속성·파라미터는 그대로 둡니다.

**확인**
- 예외 클래스 활성화 성공. 기존 R-02~R-04 코드가 그대로 활성화되는지(Ctrl+Shift+F3 일괄 활성화) 확인합니다.

<details><summary>정답·해설</summary>

PUBLIC SECTION의 `CONSTANTS`에 추가:

```abap
    CONSTANTS:
      BEGIN OF cfg_discount_out_of_range,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '090',
        attr1 TYPE scx_attrname VALUE 'CFG_AGENCY_ID',
        attr2 TYPE scx_attrname VALUE 'CFG_DISCOUNT_PCT',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF cfg_discount_out_of_range,
      BEGIN OF cfg_amount_negative,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '091',
        attr1 TYPE scx_attrname VALUE 'CFG_AGENCY_ID',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF cfg_amount_negative,
      BEGIN OF cfg_currency_invalid,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '092',
        attr1 TYPE scx_attrname VALUE 'CFG_CURRENCY',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF cfg_currency_invalid,
      BEGIN OF cfg_agency_unknown,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '093',
        attr1 TYPE scx_attrname VALUE 'CFG_AGENCY_ID',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF cfg_agency_unknown.
```

PUBLIC SECTION에 속성 추가:

```abap
    DATA cfg_agency_id    TYPE /dmo/agency_id     READ-ONLY.
    DATA cfg_discount_pct TYPE string             READ-ONLY.
    DATA cfg_currency     TYPE /dmo/currency_code READ-ONLY.
```

생성자 정의의 IMPORTING 목록 끝에 추가:

```abap
          cfg_agency_id    TYPE /dmo/agency_id     OPTIONAL
          cfg_discount_pct TYPE string             OPTIONAL
          cfg_currency     TYPE /dmo/currency_code OPTIONAL
```

생성자 구현의 `super->constructor( ... )` 호출 뒤에 추가:

```abap
    me->cfg_agency_id    = cfg_agency_id.
    me->cfg_discount_pct = cfg_discount_pct.
    me->cfg_currency     = cfg_currency.
```

왜 이렇게 쓰나
- 텍스트 ID 상수의 `attr1`~`attr4`에는 **속성 이름(대문자)**을 적습니다. 메시지의 `&1`~`&4` 자리에 그 속성 값이 들어갑니다(Flight Reference Scenario `/DMO/CX_CARRIERS_S`의 `MV_AIRLINE_ID`와 같은 방식).
- 속성 이름에 `cfg_` 접두어를 붙인 것은 R-02에서 이미 `agency_id` 같은 이름을 썼을 가능성 때문에 충돌을 피하려는 것입니다. R-02 생성자의 파라미터 이름이 다르면(예: `iv_severity`) 5단계 코드의 `NEW zcm_rap_###( ... )` 호출도 그 이름에 맞추세요.
- 할인율은 메시지에 `10.00`처럼 보이도록 string으로 받아 호출하는 쪽에서 `|{ 값 }|`로 넘깁니다.

</details>

#### 3단계. 싱글턴 루트와 자식 CDS

요구사항
1. 루트 `ZRAP_I_CFG_S_###`(root view entity)
   - 데이터 소스는 `I_Language`(현재 로그온 언어 1행만 `where`로 남김)이고, `ZRAP_CFG_###`를 `left outer join ... on 0 = 0`으로 붙입니다.
   - 요소: 키 `SingletonID`(리터럴 1), `LastChangedAtMax`(= 설정 테이블 `last_changed_at`의 최댓값), 자식으로 가는 composition `_DiscountRule`(0..*).
2. 자식 `ZRAP_I_CFG_###`(view entity)
   - `ZRAP_CFG_###`에서 선택. 모든 필드를 CamelCase 별칭으로(`AgencyID`, `MaxDiscountPct`, `MaxDiscountAmt`, `CurrencyCode`, `IsActive`, `LocalCreatedBy`, `LocalCreatedAt`, `LocalLastChangedBy`, `LocalLastChangedAt`, `LastChangedAt`).
   - 루트와 같은 리터럴 `1 as SingletonID`, 부모 연관 `_Singleton`, `/DMO/I_Agency`로 가는 `_Agency`, `I_Currency`로 가는 `_Currency`.
   - 관리 필드는 RAP가 자동으로 채우도록 의미 어노테이션을 붙입니다.

**직접 추가할 어노테이션**
- `@AccessControl.authorizationCheck` — 이 실습은 DCL을 만들지 않음.
- `@EndUserText.label` — 뷰 설명.
- `@Metadata.ignorePropagatedAnnotations` — 하위 소스(테이블/데이터 엘리먼트)의 어노테이션을 물려받지 않게.
- `@Semantics.amount.currencyCode` — 금액 → 통화 필드.
- `@Semantics.user.createdBy` / `@Semantics.systemDateTime.createdAt` / `@Semantics.user.lastChangedBy` / `@Semantics.systemDateTime.localInstanceLastChangedAt` / `@Semantics.systemDateTime.lastChangedAt` — 관리형 BO가 자동으로 채울 관리 필드 표시(행 etag, total etag 용도).

**확인**
- 두 뷰를 함께 활성화(Ctrl+Shift+F3). 루트 Data Preview → **설정 테이블이 비어 있어도** `SingletonID = 1` 한 행이 보여야 합니다. `LastChangedAtMax`는 1단계 데이터의 시각.
- 자식 Data Preview → 3행, `SingletonID` 모두 1.

<details><summary>정답·해설</summary>

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED           // DCL 없음 (→ 어노테이션 탭: @AccessControl.authorizationCheck)
@EndUserText.label: 'Discount rules - singleton root'      // (→ 어노테이션 탭: @EndUserText.label)
define root view entity ZRAP_I_CFG_S_###
  as select from    I_Language
    left outer join zrap_cfg_### as cfg on 0 = 0
  composition [0..*] of ZRAP_I_CFG_### as _DiscountRule
{
  key 1                        as SingletonID,
      max( cfg.last_changed_at ) as LastChangedAtMax,
      _DiscountRule
}
where
  I_Language.Language = $session.system_language
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Discount rule (configuration row)'
@Metadata.ignorePropagatedAnnotations: true                // 하위 어노테이션 전파 무시 (→ 어노테이션 탭: @Metadata.ignorePropagatedAnnotations)
define view entity ZRAP_I_CFG_###
  as select from zrap_cfg_###
  association        to parent ZRAP_I_CFG_S_### as _Singleton on $projection.SingletonID = _Singleton.SingletonID
  association [0..1] to /DMO/I_Agency           as _Agency    on $projection.AgencyID     = _Agency.AgencyID
  association [0..1] to I_Currency              as _Currency  on $projection.CurrencyCode = _Currency.Currency
{
  key agency_id             as AgencyID,
      1                     as SingletonID,
      max_discount_pct      as MaxDiscountPct,
      @Semantics.amount.currencyCode: 'CurrencyCode'        // (→ 어노테이션 탭: @Semantics.amount.currencyCode)
      max_discount_amt      as MaxDiscountAmt,
      currency_code         as CurrencyCode,
      is_active             as IsActive,
      @Semantics.user.createdBy: true                       // 생성자 자동 기입 (→ 어노테이션 탭: @Semantics.user.createdBy)
      local_created_by      as LocalCreatedBy,
      @Semantics.systemDateTime.createdAt: true             // (→ 어노테이션 탭: @Semantics.systemDateTime.createdAt)
      local_created_at      as LocalCreatedAt,
      @Semantics.user.lastChangedBy: true                   // (→ 어노테이션 탭: @Semantics.user.lastChangedBy)
      local_last_changed_by as LocalLastChangedBy,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true  // 행 etag (→ 어노테이션 탭: @Semantics.systemDateTime.localInstanceLastChangedAt)
      local_last_changed_at as LocalLastChangedAt,
      @Semantics.systemDateTime.lastChangedAt: true         // 루트 total etag의 재료 (→ 어노테이션 탭: @Semantics.systemDateTime.lastChangedAt)
      last_changed_at       as LastChangedAt,

      /* Associations */
      _Singleton,
      _Agency,
      _Currency
}
```

왜 이렇게 쓰나
- **싱글턴이란**: 인스턴스가 항상 정확히 1개인 루트 엔터티입니다. 설정 테이블은 행이 여러 개지만 "설정 전체"를 하나의 BO 인스턴스로 다루면 ① 한 번의 Edit로 전체가 잠기고(동시에 두 사람이 다른 행을 고쳐 규칙이 서로 모순되는 일을 막음), ② 여러 행을 한 화면 표에서 고친 뒤 한 번에 Activate할 수 있습니다.
- **왜 `I_Language`인가**: 루트에는 실제 테이블이 없지만 CDS는 데이터 소스가 필요합니다. `I_Language`에서 현재 언어 1행만 남기면 **항상 정확히 1행**이 나옵니다. 여기에 설정 테이블을 `left outer join ... on 0 = 0`(항상 참)으로 붙이고 `max()`로 집계하면, 설정 테이블이 비어 있어도 루트 1행이 존재합니다(비어 있으면 `LastChangedAtMax`만 null/초기값). 이것이 Flight Reference Scenario `/DMO/I_CarriersLockSingleton_S`와 BC 생성기 출력이 공통으로 쓰는 형태입니다.
- `key 1 as SingletonID`와 자식의 `1 as SingletonID`가 부모-자식 조건이 됩니다. 이 리터럴은 Reference Scenario의 draft 테이블에서 INT1 타입으로 정의되어 있어(4단계 draft 테이블), 리터럴 1의 타입이 INT1로 추론되는 것으로 보입니다.
- `max( cfg.last_changed_at )`: 자식 어느 행이 바뀌어도 `last_changed_at`이 갱신되므로 최댓값이 바뀝니다. 4단계에서 이것을 루트의 `total etag`로 써서 "테이블 전체가 마지막으로 바뀐 시각"을 나타냅니다.
- Reference Scenario의 루트에는 `@Semantics.valueRange.maximum: '1'`도 붙어 있습니다. 싱글턴임을 나타내려는 것으로 보이나 정확한 효과는 로컬 자료에서 확인하지 못해 정답에서는 뺐습니다(필요하면 추가해 비교해 보세요, 실제 시스템에서 확인 필요).

자주 나는 오류와 해결
- `left outer join` 대신 `inner join`을 쓰면 설정 테이블이 비었을 때 루트가 0행이 되어 Edit할 대상이 없어집니다.
- 자식에 `1 as SingletonID`를 빼면 `association to parent` 조건을 만들 수 없습니다.

</details>

#### 4단계. 행동 정의(BDEF)와 draft 테이블

요구사항
1. `ZRAP_I_CFG_S_###`에서 New Behavior Definition(구현 유형 Managed). 헤더: 행동 풀 `ZBP_RAP_I_CFG_S_###`, `strict ( 2 )`, `with draft`.
2. 루트 `DiscountRuleAll`(별칭):
   - `with unmanaged save`(루트에는 persistent table 없음), draft 테이블 `zrap_dcfg_s_###`, `lock master`, `total etag LastChangedAtMax`, `authorization master ( global )`, 표준 연산이 없다는 경고를 억제하는 pragma `##DRAFT_OP_NOT_REQUIRED`.
   - 자식 생성: `association _DiscountRule { create; with draft; }`.
   - `SingletonID`, `LastChangedAtMax` 읽기 전용.
   - draft 액션 Edit, Activate(optimized), Discard, Resume, `draft determine action Prepare`에 자식 검증 3개를 등록.
3. 자식 `DiscountRule`:
   - persistent table `zrap_cfg_###`, draft 테이블 `zrap_dcfg_###`, `lock dependent by _Singleton`, `authorization dependent by _Singleton`, `etag master LocalLastChangedAt`.
   - `update`, `delete ( features : instance )`(활성 규칙은 삭제 불가).
   - 필드 제어: 관리 필드·`SingletonID` 읽기 전용, `AgencyID`는 생성 시 필수·이후 읽기 전용, `MaxDiscountPct`·`CurrencyCode` 필수.
   - 결정 `setActiveOnCreate`(생성 시 `IsActive` = 참).
   - 검증 `validateDiscount`(할인율·금액), `validateCurrency`, `validateAgency` — 모두 on save, 생성 및 해당 필드 변경 시.
   - 테이블 열과 CDS 요소의 `mapping`.
4. draft 테이블 두 개를 만듭니다(BDEF의 draft table 이름에서 Ctrl+1 quick fix로 생성 가능). 필드 이름은 CDS 별칭과 같게, `"%admin"` include 포함.

`ZRAP_DCFG_S_###`(루트 draft)

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| mandt | X | mandt | CLNT | 3 | 0 | 클라이언트 |
| singletonid | X | abap.int1 | INT1 | 3 | 0 | 싱글턴 키(항상 1) |
| lastchangedatmax | | abp_lastchange_tstmpl | DEC | 21 | 7 | total etag |
| "%admin" | | include sych_bdl_draft_admin_inc | | | | draft 관리 정보 |

`ZRAP_DCFG_###`(자식 draft)

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| mandt | X | mandt | CLNT | 3 | 0 | 클라이언트 |
| agencyid | X | /dmo/agency_id | NUMC | 6 | 0 | 여행사 ID |
| singletonid | | abap.int1 | INT1 | 3 | 0 | 부모 키 |
| maxdiscountpct | | abap.dec | DEC | 5 | 2 | 최대 할인율 |
| maxdiscountamt | | /dmo/total_price | CURR | 16 | 2 | 최대 할인 금액, 참조 필드 `currencycode` |
| currencycode | | /dmo/currency_code | CUKY | 5 | 0 | 통화 |
| isactive | | abap_boolean | CHAR | 1 | 0 | 활성 |
| localcreatedby ~ lastchangedat | | 1단계 관리 필드와 같은 데이터 엘리먼트 | | | | 관리 필드 5개 |
| "%admin" | | include sych_bdl_draft_admin_inc | | | | draft 관리 정보 |

**확인**
- draft 테이블 → BDEF 순서로 활성화. 행동 풀이 아직 없다는 오류가 나면 BDEF 첫 줄 클래스 이름에서 Ctrl+1 → 행동 풀 생성(5단계).

<details><summary>정답·해설</summary>

```bdef
managed implementation in class zbp_rap_i_cfg_s_### unique;
strict ( 2 );
with draft;

define behavior for ZRAP_I_CFG_S_### alias DiscountRuleAll
with unmanaged save
draft table zrap_dcfg_s_###
lock master
total etag LastChangedAtMax
authorization master ( global )
##DRAFT_OP_NOT_REQUIRED
{
  association _DiscountRule { create; with draft; }

  field ( readonly ) SingletonID, LastChangedAtMax;

  draft action Edit;
  draft action Activate optimized;
  draft action Discard;
  draft action Resume;
  draft determine action Prepare
  {
    validation DiscountRule ~ validateDiscount;
    validation DiscountRule ~ validateCurrency;
    validation DiscountRule ~ validateAgency;
  }
}

define behavior for ZRAP_I_CFG_### alias DiscountRule
persistent table zrap_cfg_###
draft table zrap_dcfg_###
lock dependent by _Singleton
authorization dependent by _Singleton
etag master LocalLastChangedAt
{
  update;
  delete ( features : instance );

  field ( readonly ) SingletonID, LocalCreatedBy, LocalCreatedAt, LocalLastChangedBy, LocalLastChangedAt, LastChangedAt;
  field ( mandatory : create, readonly : update ) AgencyID;
  field ( mandatory ) MaxDiscountPct, CurrencyCode;

  association _Singleton { with draft; }

  determination setActiveOnCreate on modify { create; }

  validation validateDiscount on save { create; field MaxDiscountPct, MaxDiscountAmt; }
  validation validateCurrency on save { create; field CurrencyCode; }
  validation validateAgency on save { create; field AgencyID; }

  mapping for zrap_cfg_###
  {
    AgencyID           = agency_id;
    MaxDiscountPct     = max_discount_pct;
    MaxDiscountAmt     = max_discount_amt;
    CurrencyCode       = currency_code;
    IsActive           = is_active;
    LocalCreatedBy     = local_created_by;
    LocalCreatedAt     = local_created_at;
    LocalLastChangedBy = local_last_changed_by;
    LocalLastChangedAt = local_last_changed_at;
    LastChangedAt      = last_changed_at;
  }
}
```

draft 테이블:

```abap
@EndUserText.label : 'Draft table for ZRAP_I_CFG_S_###'
@AbapCatalog.enhancement.category : #EXTENSIBLE_ANY
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_dcfg_s_### {

  key mandt        : mandt not null;
  key singletonid  : abap.int1 not null;
  lastchangedatmax : abp_lastchange_tstmpl;
  "%admin"         : include sych_bdl_draft_admin_inc;

}
```

```abap
@EndUserText.label : 'Draft table for ZRAP_I_CFG_###'
@AbapCatalog.enhancement.category : #EXTENSIBLE_ANY
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_dcfg_### {

  key mandt          : mandt not null;
  key agencyid       : /dmo/agency_id not null;
  singletonid        : abap.int1;
  maxdiscountpct     : abap.dec(5,2);
  @Semantics.amount.currencyCode : 'zrap_dcfg_###.currencycode'
  maxdiscountamt     : /dmo/total_price;
  currencycode       : /dmo/currency_code;
  isactive           : abap_boolean;
  localcreatedby     : abp_creation_user;
  localcreatedat     : abp_creation_tstmpl;
  locallastchangedby : abp_locinst_lastchange_user;
  locallastchangedat : abp_locinst_lastchange_tstmpl;
  lastchangedat      : abp_lastchange_tstmpl;
  "%admin"           : include sych_bdl_draft_admin_inc;

}
```

왜 이렇게 쓰나 — 줄별 해설
- `with unmanaged save`(루트 줄): 루트는 가상 엔터티라 저장할 테이블이 없습니다. BDL cheat sheet 설명대로 `with unmanaged save`는 헤더뿐 아니라 **엔터티별**로 쓸 수 있고, 이 경우 그 엔터티에는 `persistent table`을 쓸 수 없습니다. 자식은 `persistent table`이 있으므로 **관리형 저장**(프레임워크가 INSERT/UPDATE/DELETE)이 그대로 동작합니다. 그래서 행동 풀의 `save_modified`는 비어 있어도 됩니다(6단계).
- `lock master`(루트) + `lock dependent by _Singleton`(자식): 어떤 행을 고치든 **루트 하나가 잠깁니다**. 즉 설정 테이블 전체가 한 사람에게만 편집 가능합니다. 이것이 싱글턴 패턴의 핵심 목적입니다.
- `total etag LastChangedAtMax`: draft BO에서 필수입니다. BDL cheat sheet: draft를 만들면 활성 인스턴스가 일정 시간 독점 잠금되고, 잠금이 풀린 뒤(optimistic 단계)에는 draft의 total etag와 활성 인스턴스의 total etag를 비교해 같을 때만 Resume을 허용합니다. 여기서는 자식 변경 시각의 최댓값이 바뀌면 "누군가 그 사이 설정을 바꿨다"는 뜻이 됩니다.
- `etag master LocalLastChangedAt`(자식): 행 단위 낙관적 잠금. cheat sheet 권고대로 total etag와 다른 필드를 씁니다.
- `##DRAFT_OP_NOT_REQUIRED`: Reference Scenario 싱글턴 루트에 그대로 있는 pragma입니다. 루트에 `create`/`update`/`delete`가 없는(싱글턴은 만들거나 지우지 않음) draft 엔터티에 대해 나는 경고를 억제하는 것으로 이해됩니다(경고의 정확한 문구는 실제 시스템에서 확인 필요). pragma를 지우고 활성화해 어떤 경고가 나는지 직접 확인해 보세요.
- `authorization master ( global )`: Reference Scenario는 `( none )`이지만, 설정 앱은 "설정 담당자만 편집" 같은 **사용자 단위** 검사가 자연스러워 global로 했습니다(BC 생성기 출력도 global). 루트에 `update`가 없어서 global 권한 결과 구조에 어떤 컴포넌트가 생기는지는 6단계에서 확인합니다. 활성화 시 권한 관련 오류가 나면 Reference Scenario처럼 `( none )`으로 바꾸고 6단계의 권한 메서드를 지우세요(실제 시스템에서 확인 필요).
- `draft determine action Prepare { validation DiscountRule ~ validateDiscount; ... }`: 자식 검증을 **루트의 Prepare**에 등록합니다. Fiori에서 Save를 누르면 Activate 전에 Prepare가 실행되어 draft 상태에서 오류를 보여 줍니다. `strict ( 2 )`에서는 draft BO의 검증을 Prepare에 등록하지 않으면 경고가 납니다.
- `delete ( features : instance )`: 행마다 삭제 버튼을 켜고 끕니다(5단계).
- draft 테이블: BDL cheat sheet에 따라 draft 테이블은 CDS **별칭 이름**의 필드를 가져야 하고, `"%admin": include sych_bdl_draft_admin_inc;`가 필요합니다. 이 BO는 late numbering이 아니므로 `DRAFTUUID` 키는 필요 없습니다(키 = `AgencyID`, 외부에서 입력).

**클래스 구조 해설(BDEF → 행동 풀)**
- `delete ( features : instance )` → `get_instance_features FOR INSTANCE FEATURES ... FOR DiscountRule`
- `determination setActiveOnCreate` → `FOR DETERMINE ON MODIFY IMPORTING keys FOR DiscountRule~setActiveOnCreate`
- `validation ...` → `FOR VALIDATE ON SAVE IMPORTING keys FOR DiscountRule~...`
- `authorization master ( global )` → 루트 핸들러의 `get_global_authorizations FOR GLOBAL AUTHORIZATION`
- `with unmanaged save` → 세이버 클래스의 `save_modified` 재정의가 필요

</details>

#### 5단계. 행동 풀 (1): 자식 핸들러 — 결정, 검증, 인스턴스 기능

요구사항
1. 행동 풀 `ZBP_RAP_I_CFG_S_###`의 Local Types에 자식 핸들러 `lhc_discountrule`을 만듭니다.
2. 상수: state area 이름 3개, 할인율 한계(0, 50).
3. `setActiveOnCreate`: 새로 만든 행 중 `IsActive`가 거짓인 행을 참으로(IN LOCAL MODE MODIFY).
4. `validateDiscount`: 할인율이 0 미만 또는 50 초과면 메시지 090, 금액이 음수면 091. 오류 필드 강조(`%element`), 부모 경로(`%path`) 포함.
5. `validateCurrency`: 통화가 `I_Currency`에 없으면 092(빈 값은 필수 필드 검사에 맡김).
6. `validateAgency`: 여행사가 `/DMO/I_Agency`에 없으면 093.
7. `get_instance_features`: `IsActive`가 참이면 삭제 비활성.
8. 모든 검증은 먼저 해당 state area의 메시지를 지우고(빈 `%state_area` 행 추가), DB 확인은 루프 밖에서 한 번에 합니다.

**확인**
- 행동 풀 활성화 성공(6단계의 루트 핸들러·세이버까지 넣은 뒤 활성화해도 됩니다).

<details><summary>정답·해설</summary>

```abap
CLASS lhc_discountrule DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.

    CONSTANTS:
      BEGIN OF state_area,
        discount TYPE string VALUE 'VALIDATE_DISCOUNT',
        currency TYPE string VALUE 'VALIDATE_CURRENCY',
        agency   TYPE string VALUE 'VALIDATE_AGENCY',
      END OF state_area,
      BEGIN OF discount_limit,
        min_pct TYPE p LENGTH 5 DECIMALS 2 VALUE '0.00',
        max_pct TYPE p LENGTH 5 DECIMALS 2 VALUE '50.00',
      END OF discount_limit.

    METHODS get_instance_features FOR INSTANCE FEATURES
      IMPORTING keys REQUEST requested_features FOR DiscountRule RESULT result.

    METHODS setactiveoncreate FOR DETERMINE ON MODIFY
      IMPORTING keys FOR DiscountRule~setActiveOnCreate.

    METHODS validatediscount FOR VALIDATE ON SAVE
      IMPORTING keys FOR DiscountRule~validateDiscount.

    METHODS validatecurrency FOR VALIDATE ON SAVE
      IMPORTING keys FOR DiscountRule~validateCurrency.

    METHODS validateagency FOR VALIDATE ON SAVE
      IMPORTING keys FOR DiscountRule~validateAgency.
ENDCLASS.


CLASS lhc_discountrule IMPLEMENTATION.

  METHOD get_instance_features.
    READ ENTITIES OF zrap_i_cfg_s_### IN LOCAL MODE
      ENTITY DiscountRule
        FIELDS ( IsActive )
        WITH CORRESPONDING #( keys )
      RESULT DATA(lt_rules)
      FAILED failed.

    " 활성 규칙은 먼저 비활성화해야 삭제 가능
    result = VALUE #( FOR ls_rule IN lt_rules
                      ( %tky    = ls_rule-%tky
                        %delete = COND #( WHEN ls_rule-IsActive = abap_true
                                          THEN if_abap_behv=>fc-o-disabled
                                          ELSE if_abap_behv=>fc-o-enabled ) ) ).
  ENDMETHOD.


  METHOD setactiveoncreate.
    READ ENTITIES OF zrap_i_cfg_s_### IN LOCAL MODE
      ENTITY DiscountRule
        FIELDS ( IsActive )
        WITH CORRESPONDING #( keys )
      RESULT DATA(lt_rules).

    DELETE lt_rules WHERE IsActive = abap_true.
    CHECK lt_rules IS NOT INITIAL.

    MODIFY ENTITIES OF zrap_i_cfg_s_### IN LOCAL MODE
      ENTITY DiscountRule
        UPDATE FIELDS ( IsActive )
        WITH VALUE #( FOR ls_rule IN lt_rules
                      ( %tky     = ls_rule-%tky
                        IsActive = abap_true ) )
      REPORTED DATA(lt_update_reported).

    reported = CORRESPONDING #( DEEP lt_update_reported ).
  ENDMETHOD.


  METHOD validatediscount.
    READ ENTITIES OF zrap_i_cfg_s_### IN LOCAL MODE
      ENTITY DiscountRule
        FIELDS ( SingletonID MaxDiscountPct MaxDiscountAmt )
        WITH CORRESPONDING #( keys )
      RESULT DATA(lt_rules).

    LOOP AT lt_rules ASSIGNING FIELD-SYMBOL(<ls_rule>).
      " 1) 이전 메시지 지우기
      APPEND VALUE #( %tky        = <ls_rule>-%tky
                      %state_area = state_area-discount ) TO reported-discountrule.

      " 2) 할인율 범위
      IF <ls_rule>-MaxDiscountPct < discount_limit-min_pct
         OR <ls_rule>-MaxDiscountPct > discount_limit-max_pct.
        APPEND VALUE #( %tky = <ls_rule>-%tky ) TO failed-discountrule.
        APPEND VALUE #( %tky                    = <ls_rule>-%tky
                        %state_area             = state_area-discount
                        %msg                    = NEW zcm_rap_###(
                                                    textid           = zcm_rap_###=>cfg_discount_out_of_range
                                                    severity         = if_abap_behv_message=>severity-error
                                                    cfg_agency_id    = <ls_rule>-AgencyID
                                                    cfg_discount_pct = |{ <ls_rule>-MaxDiscountPct }| )
                        %element-MaxDiscountPct = if_abap_behv=>mk-on
                        %path-discountruleall   = CORRESPONDING #( <ls_rule> )
                      ) TO reported-discountrule.
      ENDIF.

      " 3) 금액은 음수 불가
      IF <ls_rule>-MaxDiscountAmt < 0.
        APPEND VALUE #( %tky = <ls_rule>-%tky ) TO failed-discountrule.
        APPEND VALUE #( %tky                    = <ls_rule>-%tky
                        %state_area             = state_area-discount
                        %msg                    = NEW zcm_rap_###(
                                                    textid        = zcm_rap_###=>cfg_amount_negative
                                                    severity      = if_abap_behv_message=>severity-error
                                                    cfg_agency_id = <ls_rule>-AgencyID )
                        %element-MaxDiscountAmt = if_abap_behv=>mk-on
                        %path-discountruleall   = CORRESPONDING #( <ls_rule> )
                      ) TO reported-discountrule.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.


  METHOD validatecurrency.
    DATA lt_currencies TYPE SORTED TABLE OF I_Currency WITH UNIQUE KEY Currency.

    READ ENTITIES OF zrap_i_cfg_s_### IN LOCAL MODE
      ENTITY DiscountRule
        FIELDS ( SingletonID CurrencyCode )
        WITH CORRESPONDING #( keys )
      RESULT DATA(lt_rules).

    " 통화 코드 모아서 한 번에 확인
    lt_currencies = CORRESPONDING #( lt_rules DISCARDING DUPLICATES MAPPING Currency = CurrencyCode EXCEPT * ).
    DELETE lt_currencies WHERE Currency IS INITIAL.

    IF lt_currencies IS NOT INITIAL.
      SELECT FROM I_Currency
        FIELDS Currency
        FOR ALL ENTRIES IN @lt_currencies
        WHERE Currency = @lt_currencies-Currency
        INTO TABLE @DATA(lt_currencies_db).
    ENDIF.

    LOOP AT lt_rules ASSIGNING FIELD-SYMBOL(<ls_rule>).
      APPEND VALUE #( %tky        = <ls_rule>-%tky
                      %state_area = state_area-currency ) TO reported-discountrule.

      " 빈 값은 field ( mandatory )가 처리 → 여기서는 존재하지 않는 코드만
      IF <ls_rule>-CurrencyCode IS NOT INITIAL
         AND NOT line_exists( lt_currencies_db[ Currency = <ls_rule>-CurrencyCode ] ).
        APPEND VALUE #( %tky = <ls_rule>-%tky ) TO failed-discountrule.
        APPEND VALUE #( %tky                  = <ls_rule>-%tky
                        %state_area           = state_area-currency
                        %msg                  = NEW zcm_rap_###(
                                                  textid       = zcm_rap_###=>cfg_currency_invalid
                                                  severity     = if_abap_behv_message=>severity-error
                                                  cfg_currency = <ls_rule>-CurrencyCode )
                        %element-CurrencyCode = if_abap_behv=>mk-on
                        %path-discountruleall = CORRESPONDING #( <ls_rule> )
                      ) TO reported-discountrule.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.


  METHOD validateagency.
    DATA lt_agencies TYPE SORTED TABLE OF /dmo/agency_id WITH UNIQUE KEY table_line.

    READ ENTITIES OF zrap_i_cfg_s_### IN LOCAL MODE
      ENTITY DiscountRule
        FIELDS ( SingletonID AgencyID )
        WITH CORRESPONDING #( keys )
      RESULT DATA(lt_rules).

    lt_agencies = CORRESPONDING #( lt_rules DISCARDING DUPLICATES MAPPING table_line = AgencyID EXCEPT * ).
    DELETE lt_agencies WHERE table_line IS INITIAL.

    IF lt_agencies IS NOT INITIAL.
      SELECT FROM /DMO/I_Agency
        FIELDS AgencyID
        FOR ALL ENTRIES IN @lt_agencies
        WHERE AgencyID = @lt_agencies-table_line
        INTO TABLE @DATA(lt_agencies_db).
    ENDIF.

    LOOP AT lt_rules ASSIGNING FIELD-SYMBOL(<ls_rule>).
      APPEND VALUE #( %tky        = <ls_rule>-%tky
                      %state_area = state_area-agency ) TO reported-discountrule.

      IF NOT line_exists( lt_agencies_db[ AgencyID = <ls_rule>-AgencyID ] ).
        APPEND VALUE #( %tky = <ls_rule>-%tky ) TO failed-discountrule.
        APPEND VALUE #( %tky                  = <ls_rule>-%tky
                        %state_area           = state_area-agency
                        %msg                  = NEW zcm_rap_###(
                                                  textid        = zcm_rap_###=>cfg_agency_unknown
                                                  severity      = if_abap_behv_message=>severity-error
                                                  cfg_agency_id = <ls_rule>-AgencyID )
                        %element-AgencyID     = if_abap_behv=>mk-on
                        %path-discountruleall = CORRESPONDING #( <ls_rule> )
                      ) TO reported-discountrule.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나
- **`%path-discountruleall`**: 자식 메시지에 부모(싱글턴) 키를 붙입니다. Fiori는 Object Page(루트)의 표 안에서 어느 행의 오류인지 이 경로로 찾아 해당 셀을 빨갛게 표시합니다. Reference Scenario `validateName`도 `%path-carrierslocksingleton = CORRESPONDING #( <carrier> )`로 같은 일을 합니다. `CORRESPONDING`이 `%is_draft`와 `SingletonID`를 옮기므로 **READ의 FIELDS에 `SingletonID`를 꼭 넣어야** 합니다.
- **state area**: 검증마다 고유 이름으로 먼저 빈 메시지를 넣어 지난번 메시지를 지우고, 오류가 있으면 같은 이름으로 다시 넣습니다. 그래서 고친 행의 오류는 다음 Prepare에서 사라집니다.
- DB 확인은 키를 모아 **한 번의 `FOR ALL ENTRIES`**로 하고, 빈 테이블이면 SELECT하지 않습니다(빈 테이블 FAE는 전체 읽기).
- `get_instance_features`는 READ에 `FAILED failed`를 넘겨 이미 지워진 행 같은 경우 프레임워크에 실패를 그대로 알립니다(Reference Scenario와 동일).
- 결정은 생성 직후 `IsActive`를 켭니다. 사용자가 이후 끄는 것은 막지 않습니다(`on modify { create; }`라서 생성 때만 실행).

**클래스 구조 해설**
- 메서드 시그니처의 `FOR DiscountRule`, `DiscountRule~validateDiscount`는 BDEF의 **별칭**에서 옵니다. `keys`의 타입은 파생 타입(`TYPE TABLE FOR VALIDATION ...` 등)이며 draft BO라 `%tky`에 `%is_draft`가 들어 있습니다.
- `failed`, `reported`는 핸들러 메서드에 암묵적으로 있는 응답 파라미터입니다. 검증은 Prepare/Activate(또는 draft 없는 save) 때, 인스턴스 기능은 UI가 버튼 상태를 물을 때, 결정은 생성 직후 호출됩니다.

자주 나는 오류와 해결
- `%path-discountruleall`에서 "컴포넌트 없음": `%path-` 뒤에는 루트 **별칭을 소문자로** 씁니다(`DiscountRuleAll` → `discountruleall`). 별칭을 바꿨다면 맞추세요.
- `NEW zcm_rap_###( cfg_agency_id = ... )`에서 "파라미터 없음": 2단계 생성자 확장을 빠뜨렸습니다.

</details>

#### 6단계. 행동 풀 (2): 루트 핸들러(global 권한)와 세이버(unmanaged save)

요구사항
1. 같은 Local Types에 루트 핸들러 `lhc_discountruleall`을 추가합니다.
   - `get_global_authorizations`: 요청된 Edit 액션에 대해 허용/거부를 돌려줍니다. 판단은 private 메서드 `is_config_admin`(실습에서는 항상 참)으로 분리합니다.
2. 세이버 클래스 `lsc_zrap_i_cfg_s_###`을 추가합니다.
   - `save_modified`, `cleanup_finalize` 재정의. 루트는 저장할 테이블이 없으므로 `save_modified`는 비어 있지만, 무엇이 들어오는지와 BC 생성기가 여기서 무엇을 하는지 주석으로 남깁니다.
3. 5단계 코드 아래에 붙인 뒤 행동 풀 전체를 활성화합니다.

**확인**
- 행동 풀 활성화 성공. `is_config_admin`을 임시로 `abap_false`로 바꾸면 8단계 Preview에서 Edit 버튼이 비활성(또는 권한 없음 메시지)이 되는지 확인한 뒤 되돌립니다.

<details><summary>정답·해설</summary>

```abap
CLASS lhc_discountruleall DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.

    METHODS get_global_authorizations FOR GLOBAL AUTHORIZATION
      IMPORTING REQUEST requested_authorizations FOR DiscountRuleAll RESULT result.

    METHODS is_config_admin
      RETURNING VALUE(result) TYPE abap_bool.
ENDCLASS.


CLASS lhc_discountruleall IMPLEMENTATION.

  METHOD get_global_authorizations.
    DATA(lv_auth) = COND #( WHEN is_config_admin( ) = abap_true
                            THEN if_abap_behv=>auth-allowed
                            ELSE if_abap_behv=>auth-unauthorized ).

    " 요청된 항목에만 답한다
    IF requested_authorizations-%action-Edit = if_abap_behv=>mk-on.
      result-%action-Edit = lv_auth.
    ENDIF.
  ENDMETHOD.


  METHOD is_config_admin.
    " 실습: 항상 허용.
    " 실무: 자체 권한 객체(IAM)로 AUTHORITY-CHECK OBJECT ... 를 하고 sy-subrc로 판단.
    result = abap_true.
  ENDMETHOD.

ENDCLASS.


CLASS lsc_zrap_i_cfg_s_### DEFINITION INHERITING FROM cl_abap_behavior_saver.
  PROTECTED SECTION.
    METHODS save_modified REDEFINITION.
    METHODS cleanup_finalize REDEFINITION.
ENDCLASS.


CLASS lsc_zrap_i_cfg_s_### IMPLEMENTATION.

  METHOD save_modified.
    " 루트 DiscountRuleAll은 'with unmanaged save' 이고 DB 테이블이 없다.
    "  - 루트 값(SingletonID, LastChangedAtMax)은 모두 자식 테이블에서 계산되므로 저장할 것이 없다.
    "  - 자식 DiscountRule은 persistent table이 있어 프레임워크(managed)가 저장한다.
    " BC 유지보수 객체 생성기가 만든 코드는 이 자리에서
    "  create/update/delete 를 전송 요청에 기록한다 (10단계 참고).
  ENDMETHOD.


  METHOD cleanup_finalize.
    " 자체 버퍼가 없으므로 정리할 것 없음
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나
- **global 권한**: 인스턴스 데이터와 관계없이 "이 사용자가 설정을 편집할 수 있는가"만 묻습니다. 싱글턴은 인스턴스가 하나뿐이라 instance 권한보다 global이 자연스럽습니다. 자식은 `authorization dependent by _Singleton`이므로 자식 수정 권한도 루트(마스터)의 판단을 따릅니다.
- `result`의 구조는 BDEF에서 생성되므로 루트에 무엇을 선언했는지에 따라 컴포넌트가 달라집니다. 여기서는 `%action-Edit`만 다뤘습니다. `result-`까지 쓰고 Ctrl+Space를 눌러 생성된 컴포넌트(예: `%assoc-_DiscountRule` 존재 여부)를 직접 확인하세요(실제 시스템에서 확인 필요). BC 생성기 출력(10단계)은 루트에 `update`가 있어 `result-%update`와 `result-%action-Edit`를 함께 채웁니다.
- **unmanaged save인데 save_modified가 비어 있는 이유**: Reference Scenario `lsc_I_CARRIERSLOCKSINGLETON_S`도 `save_modified`와 `cleanup_finalize`가 비어 있습니다. "루트를 저장하는 방법을 내가 정하겠다(그런데 저장할 것이 없다)"는 선언으로 루트에 persistent table 없이 managed BO를 만들 수 있게 하는 것이 목적입니다. `save_modified`의 `create`/`update`/`delete` 파라미터는 `TYPE REQUEST FOR CHANGE`/`REQUEST FOR DELETE` 파생 타입입니다(EML cheat sheet).
- **세이버와 핸들러의 분리**: 핸들러(`lhc_*`)는 상호작용 단계(검증·결정·권한·기능)를, 세이버(`lsc_*`)는 저장 단계를 담당합니다. 세이버는 행동 풀에 **하나만** 둡니다.

**클래스 구조 해설**
- `get_global_authorizations`는 BDEF 루트의 `authorization master ( global )`에서 생기며, UI가 버튼 상태를 정할 때와 수정 요청이 들어올 때 호출됩니다. `REQUEST requested_authorizations`에는 무엇을 물었는지가 `mk-on`으로 표시됩니다.
- `save_modified`는 루트의 `with unmanaged save` 때문에 재정의가 필요하며 저장 순서의 `save` 단계(Activate 후 COMMIT 시)에 호출됩니다.

</details>

#### 7단계. 프로젝션, 프로젝션 BDEF, 메타데이터 확장(UI)

요구사항
1. 루트 프로젝션 `ZRAP_C_CFG_S_###`(`provider contract transactional_query`): `SingletonID`, `LastChangedAtMax`(화면에서 숨김), `_DiscountRule`을 자식 프로젝션으로 redirect. 의미 키 = `SingletonID`.
2. 자식 프로젝션 `ZRAP_C_CFG_###`: 모든 업무 필드 + `_Agency.Name as AgencyName`(텍스트). `AgencyID` 값 도움말 `/DMO/I_Agency_StdVH`, `CurrencyCode` 값 도움말 `I_CurrencyStdVH`(둘 다 입력값 검증에도 사용). `SingletonID` 숨김. 의미 키 = `AgencyID`. `_Singleton`은 부모로 redirect.
3. 프로젝션 BDEF `ZRAP_C_CFG_S_###`: `use draft`, 루트는 draft 액션 5개와 자식 생성(`with draft`), 자식은 `use etag`, update/delete, 부모 연관.
4. MDE
   - 루트: 머리글 이름 `Discount Rules`, 본문은 **자식 표 하나**(LINEITEM_REFERENCE, 라벨 `Agency Discount Rules`).
   - 자식: 머리글(제목 = 여행사 ID, 설명 = 여행사 이름), 표 열(여행사, 할인율, 금액, 통화, 활성), Object Page 섹션 1개(identification).

**직접 추가할 어노테이션**
- `@ObjectModel.semanticKey` — 사용자에게 보이는 업무 키(draft 표시, 메시지 위치).
- `@Metadata.allowExtensions` — MDE 허용.
- `@Consumption.hidden` — OData/화면에서 필드 숨김.
- `@Consumption.valueHelpDefinition` (+ `useForValidation`) — 값 도움말과 입력값 검증.
- `@ObjectModel.text.element` / `@UI.textArrangement` — 여행사 ID 옆 이름.
- `@Metadata.layer` — MDE 계층.
- `@UI.headerInfo`, `@UI.facet`(`#LINEITEM_REFERENCE` + `targetElement`, `#IDENTIFICATION_REFERENCE`), `@UI.lineItem`, `@UI.identification` — 싱글턴 Object Page의 표와 자식 상세.

**확인**
- 프로젝션 CDS 2개 → 프로젝션 BDEF → MDE 2개 순서로 활성화 성공.

<details><summary>정답·해설</summary>

```cds
@EndUserText.label: 'Discount rules - singleton (projection)'
@AccessControl.authorizationCheck: #NOT_REQUIRED
@Metadata.allowExtensions: true                         // MDE 허용 (→ 어노테이션 탭: @Metadata.allowExtensions)
@ObjectModel.semanticKey: [ 'SingletonID' ]             // 업무 키 (→ 어노테이션 탭: @ObjectModel.semanticKey)
define root view entity ZRAP_C_CFG_S_###
  provider contract transactional_query
  as projection on ZRAP_I_CFG_S_###
{
  key SingletonID,

      @Consumption.hidden: true                         // etag용 값은 화면에 노출하지 않음 (→ 어노테이션 탭: @Consumption.hidden)
      LastChangedAtMax,

      /* Associations */
      _DiscountRule : redirected to composition child ZRAP_C_CFG_###
}
```

```cds
@EndUserText.label: 'Discount rule (projection)'
@AccessControl.authorizationCheck: #NOT_REQUIRED
@Metadata.allowExtensions: true
@ObjectModel.semanticKey: [ 'AgencyID' ]
define view entity ZRAP_C_CFG_###
  as projection on ZRAP_I_CFG_###
{
      @Consumption.valueHelpDefinition: [{ entity: { name: '/DMO/I_Agency_StdVH', element: 'AgencyID' },   // 값 도움말 (→ 어노테이션 탭: @Consumption.valueHelpDefinition)
                                           useForValidation: true }]                                        // 입력값이 값 도움말에 있는지 UI가 검사
      @ObjectModel.text.element: [ 'AgencyName' ]       // ID의 텍스트 (→ 어노테이션 탭: @ObjectModel.text.element)
      @UI.textArrangement: #TEXT_LAST                   // "ID (이름)" (→ 어노테이션 탭: @UI.textArrangement)
  key AgencyID,

      _Agency.Name as AgencyName,

      @Consumption.hidden: true
      SingletonID,

      MaxDiscountPct,
      MaxDiscountAmt,

      @Consumption.valueHelpDefinition: [{ entity: { name: 'I_CurrencyStdVH', element: 'Currency' },
                                           useForValidation: true }]
      CurrencyCode,

      IsActive,
      LocalCreatedBy,
      LocalCreatedAt,
      LocalLastChangedBy,
      LocalLastChangedAt,
      LastChangedAt,

      /* Associations */
      _Singleton : redirected to parent ZRAP_C_CFG_S_###,
      _Agency,
      _Currency
}
```

```bdef
projection;
strict ( 2 );
use draft;

define behavior for ZRAP_C_CFG_S_### alias DiscountRuleAll
{
  use action Activate;
  use action Discard;
  use action Edit;
  use action Prepare;
  use action Resume;

  use association _DiscountRule { create; with draft; }
}

define behavior for ZRAP_C_CFG_### alias DiscountRule
use etag
{
  use update;
  use delete;

  use association _Singleton { with draft; }
}
```

```cds
@Metadata.layer: #CORE                                    // (→ 어노테이션 탭: @Metadata.layer)
@UI: { headerInfo: { typeName:       'Discount Rules',   // (→ 어노테이션 탭: @UI.headerInfo)
                     typeNamePlural: 'Discount Rules',
                     title: { type: #STANDARD, value: 'SingletonID' } } }
annotate entity ZRAP_C_CFG_S_### with
{
  @UI.facet: [ { id:            'DiscountRules',          // 싱글턴 페이지 = 자식 표 하나 (→ 어노테이션 탭: @UI.facet)
                 purpose:       #STANDARD,
                 type:          #LINEITEM_REFERENCE,     // 연관 대상의 lineItem을 표로 표시
                 label:         'Agency Discount Rules',
                 position:      10,
                 targetElement: '_DiscountRule' } ]

  @UI.lineItem: [{ position: 10 }]                        // (→ 어노테이션 탭: @UI.lineItem)
  SingletonID;
}
```

```cds
@Metadata.layer: #CORE
@UI: { headerInfo: { typeName:       'Discount Rule',
                     typeNamePlural: 'Discount Rules',
                     title:       { type: #STANDARD, value: 'AgencyID' },
                     description: { type: #STANDARD, value: 'AgencyName' } } }
annotate entity ZRAP_C_CFG_### with
{
  @UI.facet: [ { id:       'Rule',
                 purpose:  #STANDARD,
                 type:     #IDENTIFICATION_REFERENCE,
                 label:    'Discount Rule',
                 position: 10 } ]

  @UI.lineItem:       [{ position: 10, importance: #HIGH }]
  @UI.identification: [{ position: 10 }]                  // (→ 어노테이션 탭: @UI.identification)
  AgencyID;

  @UI.lineItem:       [{ position: 20, importance: #HIGH, label: 'Max. Discount (%)' }]
  @UI.identification: [{ position: 20, label: 'Max. Discount (%)' }]
  MaxDiscountPct;

  @UI.lineItem:       [{ position: 30, importance: #MEDIUM, label: 'Max. Discount Amount' }]
  @UI.identification: [{ position: 30, label: 'Max. Discount Amount' }]
  MaxDiscountAmt;

  @UI.lineItem:       [{ position: 40, importance: #MEDIUM }]
  @UI.identification: [{ position: 40 }]
  CurrencyCode;

  @UI.lineItem:       [{ position: 50, importance: #HIGH, label: 'Active' }]
  @UI.identification: [{ position: 50, label: 'Active' }]
  IsActive;

  @UI.hidden: true                                        // (→ 어노테이션 탭: @UI.hidden)
  AgencyName;

  @UI.hidden: true
  LocalLastChangedAt;
}
```

왜 이렇게 쓰나
- **multi-inline edit**: 싱글턴 루트의 Object Page에 자식 표 하나(`#LINEITEM_REFERENCE`)만 두면, Edit를 누르는 순간 표 전체가 편집 모드가 되어 여러 행을 셀 단위로 고치고 표 위 Create로 새 행을 표 안에 추가할 수 있습니다. Reference Scenario의 서비스 이름이 "Multi-Inline-Edit Scenario"이고 facet 라벨이 `'Carrier Multi Inline Edit'`인 이유입니다. 표 안 편집을 켜는 별도 어노테이션은 쓰지 않았습니다(Reference Scenario도 없음). 행 생성을 숨기는 `@UI.createHidden` 같은 어노테이션은 로컬 자료에서 확인하지 못해 쓰지 않았습니다.
- 자식 MDE의 `@UI.facet`(IDENTIFICATION)은 행을 클릭했을 때 열리는 자식 Object Page용입니다. multi-inline edit에서는 거의 쓰지 않지만 없으면 행 클릭 시 빈 페이지가 됩니다.
- `use etag`(자식): 프로젝션에서 기본 BO의 etag(`LocalLastChangedAt`)를 OData ETag로 내보냅니다. Reference Scenario와 같습니다.
- 루트 projection에 `@Consumption.hidden: true LastChangedAtMax`: total etag 값은 내부용이라 숨깁니다(Reference Scenario 동일).

</details>

#### 8단계. 서비스와 Fiori Preview: 싱글턴 편집·잠금·검증 확인

요구사항
1. 서비스 정의 `ZRAP_UI_CFG_###`: 루트를 `DiscountRuleAll`, 자식을 `DiscountRule`로 노출하고, **주 엔터티(leading entity)**를 루트로 지정합니다.
2. 서비스 바인딩 `ZRAP_UI_CFG_O4_###`(OData V4 - UI), Publish.
3. Preview(`DiscountRuleAll`)에서 다음을 순서대로 시험합니다.
   - (a) 목록에 1행(SingletonID 1) → 클릭 → 표에 3행.
   - (b) Edit → 표가 편집 가능. 070002 할인율을 60으로, Create로 새 행(070004, 15%, 200 EUR) 추가 → Save → 060 행에 090 오류가 셀에 표시, 저장 안 됨.
   - (c) 60을 20으로 고쳐 Save → 성공. 새 행의 Active가 자동으로 체크되어 있어야 함.
   - (d) 070001(활성) 행은 삭제 불가, Active 해제 후 저장 → 다시 Edit → 삭제 가능.
   - (e) 다른 브라우저(다른 사용자, 가능하면)에서 같은 앱을 열고 Edit → 잠금 메시지(누군가 편집 중).
   - (f) Edit 상태에서 브라우저를 닫고 다시 열면 "draft가 있음" → 이어서 편집(Resume).

**직접 추가할 어노테이션**
- `@ObjectModel.leadingEntity.name` — 서비스의 주 엔터티(앱 진입 엔터티) 지정.

**확인**
- 위 (a)~(f)의 화면 결과가 정답 표와 일치하는지 확인합니다.

<details><summary>정답·해설</summary>

```cds
@EndUserText.label: 'Discount rule maintenance'
@ObjectModel.leadingEntity.name: 'ZRAP_C_CFG_S_###'
define service ZRAP_UI_CFG_### {
  expose ZRAP_C_CFG_S_### as DiscountRuleAll;
  expose ZRAP_C_CFG_###   as DiscountRule;
}
```

| 시험 | 기대 결과 | 관련 BDEF/코드 |
|---|---|---|
| (a) | 루트 1행, 자식 3행 | `I_Language` + left outer join, `1 as SingletonID` |
| (b) | Save 시 Prepare → `validateDiscount` 실패, 할인율 셀 강조, 메시지 090 | `draft determine action Prepare`, `%element`, `%path` |
| (c) | 성공, 새 행 Active 체크 | `setActiveOnCreate`, 자식 managed 저장 |
| (d) | 활성 행 삭제 버튼 비활성 | `delete ( features : instance )` |
| (e) | 두 번째 사용자는 편집 불가(잠금) — 어느 행을 고치든 | `lock master`(루트) + `lock dependent by` |
| (f) | 기존 draft 이어서 편집 | `draft action Resume`, `total etag` |

왜 이렇게 쓰나
- `@ObjectModel.leadingEntity.name`: 서비스 안 여러 엔터티 중 앱이 시작할 엔터티를 지정합니다. Reference Scenario `/DMO/UI_Carriers_S`가 같은 어노테이션을 씁니다.
- Preview는 List Report로 시작하므로 싱글턴 1행이 목록에 보이고 클릭해야 표가 나옵니다. 목록을 건너뛰고 바로 Object Page를 여는 설정은 Fiori 앱 설정(manifest) 영역이라 이 문제 범위 밖입니다(BC 생성기로 만든 객체는 별도의 설정 유지보수 앱에서 열리는 것으로 알려져 있음, 10단계).
- (e)에서 같은 사용자로 두 창을 열면 잠금 대신 "내 draft"로 이어지므로, 잠금을 보려면 다른 사용자가 필요합니다. 트라이얼에서 사용자 두 명을 쓰기 어렵다면 이 시험은 개념 확인으로 대신합니다.
- 활성 행의 삭제 버튼은 Active를 해제한 직후 바로 켜지지 않을 수 있습니다(기능 제어는 다시 읽을 때 계산). 저장 후 다시 Edit하면 확실히 확인됩니다.

자주 나는 오류와 해결
- Save 시 "Etag mismatch" 류의 오류가 계속 나면 1단계 데모 데이터의 `local_last_changed_at`이 비어 있지 않은지 확인합니다(데모 클래스에서 채움).

</details>

#### 9단계. EML 콘솔로 싱글턴 다루기

요구사항
1. 콘솔 클래스 `ZCL_RAP_CFG_EML_###`에서 다음을 차례로 실행하고 결과를 출력합니다.
   - (1) 싱글턴(`SingletonID = 1`)에 `Edit` 실행 → draft 생성. 실패하면(이미 draft/잠금) 원인 출력 후 종료.
   - (2) draft 루트 아래에 자식 생성(`CREATE BY \_DiscountRule`): 070005, 할인율 80%(의도적 오류), 300 EUR.
   - (3) `Activate` → 실패, reported의 메시지 텍스트 출력.
   - (4) 그 draft 행을 15%로 `UPDATE`(`%is_draft` = on).
   - (5) 다시 `Activate` → 성공, `COMMIT ENTITIES`.
   - (6) 활성 데이터를 루트에서 연관으로 읽어(`READ ... BY \_DiscountRule`) 출력.
2. 070005가 실제 여행사 ID가 아니면 바꿉니다.

**확인**
- F9 실행 → 단계별 출력: Edit OK → Create OK → Activate failed: `Agency 070005: max. discount 80.00 % must be between 0 and 50` → Update OK → Activate OK → 규칙 목록에 070005 포함.
- 다시 실행하면 이미 070005가 있으므로 (2)에서 키 중복 실패가 나는 것을 확인하고, Preview에서 그 행을 지운 뒤 다시 실행합니다.

<details><summary>정답·해설</summary>

```abap
CLASS zcl_rap_cfg_eml_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.
  PROTECTED SECTION.
  PRIVATE SECTION.
    CONSTANTS c_singleton_id TYPE i VALUE 1.
    CONSTANTS c_agency_id    TYPE /dmo/agency_id VALUE '070005'.
ENDCLASS.


CLASS zcl_rap_cfg_eml_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.

    " (1) Edit: 활성 싱글턴 → draft
    MODIFY ENTITIES OF zrap_i_cfg_s_###
      ENTITY DiscountRuleAll
        EXECUTE Edit FROM VALUE #( ( %key-SingletonID = c_singleton_id ) )
      FAILED   DATA(ls_failed_edit)
      REPORTED DATA(ls_reported_edit).

    IF ls_failed_edit IS NOT INITIAL.
      out->write( |(1) Edit failed, cause: { ls_failed_edit-discountruleall[ 1 ]-%fail-cause }| ).
      ROLLBACK ENTITIES.
      RETURN.
    ENDIF.
    out->write( '(1) Edit OK - draft created' ).

    " (2) draft 루트 아래에 자식 생성 (할인율 80% → 검증 오류 예정)
    MODIFY ENTITIES OF zrap_i_cfg_s_###
      ENTITY DiscountRuleAll
        CREATE BY \_DiscountRule
        FIELDS ( AgencyID MaxDiscountPct MaxDiscountAmt CurrencyCode )
        WITH VALUE #( ( %is_draft   = if_abap_behv=>mk-on
                        SingletonID = c_singleton_id
                        %target     = VALUE #( ( %cid           = 'RULE_NEW'
                                                 %is_draft      = if_abap_behv=>mk-on
                                                 AgencyID       = c_agency_id
                                                 MaxDiscountPct = '80.00'
                                                 MaxDiscountAmt = '300.00'
                                                 CurrencyCode   = 'EUR' ) ) ) )
      MAPPED   DATA(ls_mapped_cba)
      FAILED   DATA(ls_failed_cba)
      REPORTED DATA(ls_reported_cba).

    IF ls_failed_cba IS NOT INITIAL.
      out->write( |(2) Create failed (key exists?), cause: { ls_failed_cba-discountrule[ 1 ]-%fail-cause }| ).
      ROLLBACK ENTITIES.
      RETURN.
    ENDIF.
    out->write( '(2) Create in draft OK' ).

    " (3) Activate → Prepare의 검증 실패 예상
    MODIFY ENTITIES OF zrap_i_cfg_s_###
      ENTITY DiscountRuleAll
        EXECUTE Activate FROM VALUE #( ( %key-SingletonID = c_singleton_id ) )
      FAILED   DATA(ls_failed_act1)
      REPORTED DATA(ls_reported_act1).

    IF ls_failed_act1 IS NOT INITIAL.
      out->write( '(3) Activate failed:' ).
      LOOP AT ls_reported_act1-discountrule INTO DATA(ls_msg) WHERE %msg IS BOUND.
        out->write( |    { ls_msg-AgencyID }: { ls_msg-%msg->if_message~get_text( ) }| ).
      ENDLOOP.
    ENDIF.

    " (4) draft 행 수정
    MODIFY ENTITIES OF zrap_i_cfg_s_###
      ENTITY DiscountRule
        UPDATE FIELDS ( MaxDiscountPct )
        WITH VALUE #( ( %is_draft      = if_abap_behv=>mk-on
                        AgencyID       = c_agency_id
                        MaxDiscountPct = '15.00' ) )
      FAILED DATA(ls_failed_upd).
    out->write( COND string( WHEN ls_failed_upd IS INITIAL THEN '(4) Update OK'
                                                           ELSE '(4) Update failed' ) ).

    " (5) 다시 Activate + COMMIT
    MODIFY ENTITIES OF zrap_i_cfg_s_###
      ENTITY DiscountRuleAll
        EXECUTE Activate FROM VALUE #( ( %key-SingletonID = c_singleton_id ) )
      FAILED   DATA(ls_failed_act2)
      REPORTED DATA(ls_reported_act2).

    IF ls_failed_act2 IS NOT INITIAL.
      out->write( '(5) Activate failed again - rollback' ).
      ROLLBACK ENTITIES.
      RETURN.
    ENDIF.

    COMMIT ENTITIES
      RESPONSE OF zrap_i_cfg_s_###
      FAILED   DATA(ls_failed_commit)
      REPORTED DATA(ls_reported_commit).

    IF ls_failed_commit IS NOT INITIAL.
      out->write( '(5) Commit failed' ).
      RETURN.
    ENDIF.
    out->write( '(5) Activate + Commit OK' ).

    " (6) 활성 데이터 읽기 (루트 → 자식)
    READ ENTITIES OF zrap_i_cfg_s_###
      ENTITY DiscountRuleAll
        BY \_DiscountRule
        FIELDS ( AgencyID MaxDiscountPct MaxDiscountAmt CurrencyCode IsActive )
        WITH VALUE #( ( %is_draft = if_abap_behv=>mk-off SingletonID = c_singleton_id ) )
      RESULT DATA(lt_rules).

    out->write( '(6) Active rules:' ).
    out->write( lt_rules ).
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나
- 싱글턴의 키는 항상 1이므로 `%key-SingletonID = 1`로 Edit/Activate를 실행합니다. draft BO에서는 활성 인스턴스를 직접 고칠 수 없고 **Edit로 draft를 만든 뒤** draft를 고쳐 Activate해야 합니다(RAP100 ex09 해설: "EML로는 자신의 draft만 수정할 수 있고, draft가 없는 활성 인스턴스를 조작하려면 먼저 Edit를 실행").
- `CREATE BY \_DiscountRule`의 바깥 행은 **부모의 키**(`%is_draft` + `SingletonID`)이고, `%target` 안이 새 자식 행입니다. 부모가 draft이므로 자식도 `%is_draft = mk-on`이어야 합니다.
- Activate는 내부적으로 Prepare(등록된 검증)를 먼저 실행하므로 검증 실패 시 Activate가 `failed`를 돌려주고 draft는 그대로 남습니다. 그래서 (4)에서 같은 draft를 고칠 수 있습니다.
- `COMMIT ENTITIES`에서 세이버가 동작합니다. 루트의 `save_modified`(비어 있음)가 호출되고 자식은 프레임워크가 `ZRAP_CFG_###`에 저장합니다.
- `Edit`에는 기존 draft를 유지할지 정하는 파라미터(`preserve_changes`로 알려짐)가 있는데, 로컬 자료에서 확인하지 못해 쓰지 않았습니다(실제 시스템에서 확인 필요). draft가 이미 있으면 (1)에서 실패하므로 Preview에서 Discard한 뒤 다시 실행하세요.

자주 나는 오류와 해결
- (1) 실패 원인이 `locked`: Preview에서 편집 중인 draft가 남아 있습니다. Preview에서 Discard하거나 같은 사용자로 Resume 후 저장하세요.
- (6)이 빈 결과: `%is_draft = mk-off`(활성)로 읽어야 커밋된 데이터가 보입니다.

</details>

#### 10단계. Business Configuration 유지보수 객체 생성기와 전송 기록

요구사항
1. ADT에서 설정 테이블 `ZRAP_CFG_###`를 우클릭했을 때 RAP 객체 생성(Generate ABAP Repository Objects) 메뉴에 **Business Configuration Maintenance Object** 생성기가 있는지 확인합니다(없으면 이 단계는 읽기만 합니다). **이 문제의 BO와 이름이 겹치지 않도록** 생성기로 실제 생성은 하지 않거나, 별도 접두어로 시험 생성 후 삭제합니다.
2. 아래 정답의 "생성기 출력 구조"를 읽고, 이 문제에서 손으로 만든 BO와 **다른 점**을 표로 정리합니다(루트 CDS 필드, BDEF 헤더, 루트 연산, 액션, 세이버, 자식 검증, 권한).
3. 손으로 만든 BO에 전송 기록을 붙인다면 어떤 객체에 무엇을 추가해야 하는지 목록으로 작성합니다.

**확인**
- 비교표에 7개 항목 이상, 추가 목록에 최소 4개 항목(CDS, BDEF, 액션 파라미터, 세이버)이 있으면 됩니다.

<details><summary>정답·해설</summary>

확인한 범위
- 이 생성기의 공식 문서는 열어 보지 못했습니다. 아래 구조는 **생성기가 만든 코드를 커밋해 둔 공개 GitHub 저장소**(panterb/RUse_S4의 `z_ad_example2`, 테이블 `ZAD_BUSCONF`)에서 확인한 것이며, 생성기 버전에 따라 다를 수 있습니다. 메뉴 이름·마법사 화면·생성된 앱을 여는 Fiori 앱 이름은 실제 시스템에서 확인하세요.

생성기 출력 구조(해당 저장소 기준)
- 루트 CDS: 이 문제와 같은 `select from I_Language left outer join <테이블> on 0 = 0`, `key 1 as SingletonID`, `max( ... ) as LastChangedAtMax`에 더해 **`cast( '' as SXCO_TRANSPORT ) as TransportRequestID`**, **`cast( 'X' as ABAP_BOOLEAN preserving type ) as HideTransport`**가 있습니다.
- BDEF 헤더: `managed with additional save implementation in class ... unique; strict; with draft;`
- 루트: `draft table ...`, `with unmanaged save`, `lock master total etag LastChangedAtMax`, `authorization master( global )`, 연산 `update; internal create; internal delete;`, `draft action ( features : instance ) Edit;`, 그리고 액션 **`action ( features : instance ) SelectCustomizingTransptReq parameter D_SelectCustomizingTransptReqP result [1] $self;`**, `association _... { create ( features : instance ); with draft; }`.
- 자식: `update( features : global ); delete( features : global );`, 검증 **`validation ValidateRecordChanges on save ##NOT_ASSIGNED_TO_DETACT { create; update; delete; }`**.
- 행동 풀:
  - 로컬 클래스 `LHC_RAP_TDAT_CTS`가 `mbc_cp_api=>rap_table_cts( table_entity_relations = VALUE #( ( entity = '<자식 별칭>' table = '<테이블>' ) ) )`로 `IF_MBC_CP_RAP_TABLE_CTS` 객체를 만듭니다.
  - 세이버 `save_modified`: 루트 update에서 `TransportRequestID`를 꺼내, 비어 있지 않으면 `->record_changes( transport_request = ... create = REF #( create ) update = REF #( update ) delete = REF #( delete ) )`로 **변경 행을 전송 요청에 기록**합니다.
  - 자식 검증 `ValidateRecordChanges`: draft 루트 테이블에서 `TransportRequestID`를 읽어 `->validate_changes( transport_request = ... table = ... keys = REF #( keys ) reported = REF #( reported ) failed = REF #( failed ) change = REF #( change-<자식> ) )`로 전송 가능 여부를 검사합니다.
  - 인스턴스/글로벌 기능: `cl_bcfg_cd_reuse_api_factory=>get_cust_obj_service_instance( ... )->is_editable( )`로 이 시스템에서 설정 편집이 허용되는지, `get_transport_service_instance( ... )->is_transport_allowed( )`로 전송 선택이 가능한지 판단합니다.
  - 권한: `AUTHORITY-CHECK OBJECT 'S_TABU_NAM' ID 'TABLE' FIELD '<CDS 이름>' ID 'ACTVT' FIELD '02'`로 global 권한을 판단합니다.
- MDE는 `@Metadata.layer: #CUSTOMER`이고, 루트 페이지에 Transport 섹션(`hidden: #(HideTransport)`)과 `type: #FOR_ACTION, dataAction: 'SelectCustomizingTransptReq'` 버튼이 있습니다.

비교표

| 항목 | 이 문제(수작업) | BC 생성기 출력 |
|---|---|---|
| 루트 CDS | `SingletonID`, `LastChangedAtMax` | + `TransportRequestID`, `HideTransport` |
| BDEF 헤더 | `managed implementation in class ... unique` | `managed with additional save implementation in class ... unique` |
| 루트 연산 | 없음(`##DRAFT_OP_NOT_REQUIRED`) | `update; internal create; internal delete;` |
| 액션 | draft 액션만 | + `SelectCustomizingTransptReq`(전송 요청 선택) |
| 세이버 | `save_modified` 비어 있음 | `record_changes`로 전송 기록 |
| 자식 검증 | 업무 검증 3개 | + `ValidateRecordChanges`(전송 검증) |
| 편집 가능 여부 | 항상 | `is_editable( )`, `is_transport_allowed( )` 기능 제어 |
| 권한 | `is_config_admin`(실습용) | `S_TABU_NAM` 검사 |
| MDE 계층 | `#CORE` | `#CUSTOMER` |

수작업 BO에 전송 기록을 붙이려면(참고, 실제 시스템에서 확인 필요)
1. 루트 CDS `ZRAP_I_CFG_S_###`에 `TransportRequestID`(`SXCO_TRANSPORT`), `HideTransport` 계산 필드 추가, 루트 draft 테이블에도 같은 필드 추가.
2. BDEF 루트에 `update`(TransportRequestID를 draft에 기록하기 위해)와 `SelectCustomizingTransptReq` 액션(파라미터 추상 엔터티 `D_SelectCustomizingTransptReqP`는 표준 객체로 보임) 추가, 구현은 생성기처럼 `MODIFY ... UPDATE FIELDS ( TransportRequestID HideTransport )`.
3. 세이버 `save_modified`에서 `mbc_cp_api=>rap_table_cts( ... )->record_changes( ... )` 호출.
4. 자식에 `ValidateRecordChanges` 검증(`validate_changes`) 추가.
5. 편집 가능 여부/전송 가능 여부 기능 제어(`cl_bcfg_cd_reuse_api_factory`).
6. 프로젝션·MDE에 Transport 섹션과 액션 버튼.

왜 이렇게 쓰나
- 납품 클래스 C 테이블은 시스템 간 전송 대상인데, RAP BO는 DB를 바꿀 뿐 전송 요청에 자동으로 기록하지 않습니다. 그래서 생성기는 루트를 `with unmanaged save`로 두고, **루트의 저장 단계(`save_modified`)를 "변경 내용을 전송 요청에 기록하는 자리"로 사용**합니다. 이 문제에서 `save_modified`가 비어 있던 그 자리입니다. 싱글턴 루트가 단순한 기술적 꼼수가 아니라 "설정 전체 = 하나의 전송 단위"라는 업무 의미를 가진다는 점이 핵심입니다.
- 실무에서 설정 테이블 유지보수 앱이 필요하면 **생성기를 쓰는 것이 원칙**이고, 이 문제는 그 안에서 무슨 일이 일어나는지 이해하려고 손으로 만든 것입니다.

</details>

## 출처

- SAP-samples/abap-platform-refscen-flight (ABAP-platform-cloud 브랜치)
  - 싱글턴 예제 `/DMO/I_CarriersLockSingleton_S`, `/DMO/I_Carrier_S`, 프로젝션·MDE·BDEF·행동 풀·예외 클래스·draft 테이블·서비스: https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/reuse/carrier
  - 읽기 전용 예제 `/DMO/I_Flight_R`, `/DMO/C_Flight_R`(dataPoint, chart): https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/readonly
  - 값 도움말 `/DMO/I_Carrier_StdVH`, `/DMO/I_Agency_StdVH`, `/DMO/I_Airport_StdVH`, `/DMO/I_Carrier`, Agency Review MDE(진행 막대): https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/reuse
  - 테이블 `/DMO/FLIGHT`, `/DMO/CONNECTION`, 데이터 엘리먼트·도메인: https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/legacy
  - `additionalBinding` 값 도움말: https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/draft
- SAP-samples/abap-platform-rap-opensap Week 5 Unit 3~6(custom entity, `if_rap_query_provider`, 연관·프로젝션 제약, 값 도움말 자동 노출): https://github.com/SAP-samples/abap-platform-rap-opensap/tree/main/week5
- SAP-samples/abap-platform-rap-workshops RAP620 Exercise 3(custom entity와 쿼리 클래스): https://github.com/SAP-samples/abap-platform-rap-workshops/tree/main/rap6xx/rap620/exercises/ex3
- SAP-samples/abap-platform-rap630 `zrap630_cl_vh_product_sol`(`get_as_sql_string` + `SELECT FROM @itab`): https://github.com/SAP-samples/abap-platform-rap630/blob/main/src/zrap630_cl_vh_product_sol.clas.abap
- SAP-samples/abap-platform-reuse-services `zreusecl_vh_product_002`: https://github.com/SAP-samples/abap-platform-reuse-services/blob/main/src/zreusecl_vh_product_002.clas.abap
- SAP-samples/abap-platform-basic-trial `zcl_ce_ac_product`(ranges + SQL 문자열 + 페이징): https://github.com/SAP-samples/abap-platform-basic-trial/blob/main/src/zcl_ce_ac_product.clas.abap
- SAP-samples/abap-platform-application-jobs `zapp_cl_show_appl_log`(custom entity로 애플리케이션 로그 조회): https://github.com/SAP-samples/abap-platform-application-jobs/blob/main/src/zapp_cl_show_appl_log.clas.abap
- SAP-samples/abap-platform-rap110 Exercise 5(`@UI.dataPoint` `#PROGRESS`, `#AS_DATAPOINT`): https://github.com/SAP-samples/abap-platform-rap110/tree/main/exercises/ex05
- SAP-samples/abap-platform-rap100 `zrap100_cl_eml_sol`, Exercise 9(draft EML Edit/Activate): https://github.com/SAP-samples/abap-platform-rap100
- SAP-samples/abap-cheat-sheets: `36_RAP_Behavior_Definition_Language.md`(unmanaged save, total etag, draft table `%admin`), `08_EML_ABAP_for_RAP.md`(REQUEST FOR CHANGE), `14_ABAP_Unit_Tests.md`(`cl_osql_test_environment`), `06_Dynamic_Programming.md`(`abap_sortorder_tab`), `03_ABAP_SQL.md`(내부 테이블 데이터 소스), `33_ABAP_Release_News.md`(custom entity 관련 릴리스 노트): https://github.com/SAP-samples/abap-cheat-sheets
- (공개 커뮤니티 예제, SAP 공식 아님) mindsquare-Custom-Solutions/RAP_Samples README(`cx_rap_query_filter_no_range`, `get_search_expression`, `page_size_unlimited`, `get_sort_elements`): https://github.com/mindsquare-Custom-Solutions/RAP_Samples/blob/main/README.md
- (공개 커뮤니티 예제, SAP 공식 아님) extension-inspector `zei_cl_qp_helper`(`page_size_unlimited`, `element_name`/`descending`): https://github.com/extension-inspector/extension-inspector/blob/main/backend/zei_cl_qp_helper.clas.abap
- (공개 커뮤니티 저장소, BC 생성기 출력 예) panterb/RUse_S4 `src/z_ad_example2`(`zbp_i_varianttable_s`, `zi_varianttable_s` 등): https://github.com/panterb/RUse_S4/tree/master/src/z_ad_example2
