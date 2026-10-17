## 4. EML과 테스트

### R-12. EML 완전 정복: 콘솔 클래스로 BO 조작하기 [작성] ★★★
<!-- covers: EML, READ ENTITIES, READ ENTITY, FIELDS, ALL FIELDS, FROM, %control, read by association, LINK, FAILED, REPORTED, MAPPED, MODIFY ENTITIES, CREATE BY, %cid, %cid_ref, AUTO FILL CID, deep create, EXECUTE action, %param, factory action, static default factory action, function, static function, draft EML, %is_draft, Edit, Activate, Discard, Prepare, Resume, COMMIT ENTITIES, RESPONSE OF, RESPONSES, IN SIMULATION MODE, COMMIT ENTITIES BEGIN END, CONVERT KEY, %pid, %tmp, ROLLBACK ENTITIES, SET LOCKS, GET PERMISSIONS, ONLY GLOBAL, ONLY INSTANCE, PRIVILEGED, IN LOCAL MODE, AUGMENTING, interface BDEF, dynamic EML, MODIFY ENTITIES OPERATIONS, READ ENTITIES OPERATIONS, abp_behv_changes_tab, abp_behv_retrievals_tab, BDEF derived types, TYPE TABLE FOR, TYPE STRUCTURE FOR, TYPE RESPONSE FOR, %tky, %key, %pky, %data, %element, %fail-cause, %msg, if_message, cl_abap_tx, cl_abap_behv_aux, unmanaged EML -->

**목표**
- BDEF 파생 타입(`TYPE TABLE FOR ...`, `TYPE STRUCTURE FOR ...`, `TYPE RESPONSE FOR ...`)과 `%` 컴포넌트(`%tky`, `%key`, `%pky`, `%pid`, `%tmp`, `%cid`, `%cid_ref`, `%control`, `%data`, `%param`, `%element`, `%fail-cause`, `%msg`)를 직접 선언하고 채워 볼 수 있습니다.
- `READ`/`MODIFY`/`COMMIT`/`ROLLBACK ENTITIES`, `SET LOCKS`, `GET PERMISSIONS`를 짧은 형식·긴 형식·동적 형식으로 모두 쓸 수 있습니다.
- 액션(인스턴스·팩토리·정적 기본 팩토리·반복 가능), 함수(인스턴스·정적), draft 액션(Edit/Activate/Discard/Prepare/Resume)을 EML로 실행하고 결과를 해석할 수 있습니다.
- late numbering BO에서 `%pid` → 최종 키를 `COMMIT ENTITIES BEGIN ... CONVERT KEY ... END`로 얻을 수 있습니다.
- 기본 BO(R), 인터페이스 BO(I), 프로젝션 BO(C), 비관리형 BO(Order)에 대해 EML이 어떻게 같고 다른지 설명할 수 있습니다.
- `reported`의 메시지를 꺼내 읽고, 트랜잭션 단계(`cl_abap_tx`)를 어겼을 때 어떤 오류가 나는지 압니다.

**전제**
- R-01 ~ R-04에서 만든 관리형 draft Travel BO가 활성화되어 있어야 합니다. 이 문제는 다음 이름을 그대로 씁니다(다르게 만들었다면 그 이름으로 바꾸세요).
  - BDEF `ZRAP_R_TRAVEL_###`(별칭 `Travel`, `Booking`), late numbering, `with draft`, `with privileged mode disabling NoCheckWhenPrivileged`
  - 액션 `acceptTravel`/`rejectTravel`(result [1] $self), `deductDiscount`(parameter `ZRAP_A_DISCOUNT_###`, 필드 `discount_percent`), 팩토리 액션 `copyTravel [1]`, 정적 기본 팩토리 액션 `createTravel`(parameter `ZRAP_A_CREATE_TRAVEL_###`: `customer_id`, `agency_id`, `carrier_id`, `connection_id`, `flight_date`), 반복 가능 액션 `addServiceFee`, 정적 함수 `getOpenTravelCount`(결과 `ZRAP_A_TRAVEL_STAT_###`)
  - Booking 함수 `getDaysToFlight`(결과 `ZRAP_A_DAYS_TO_FLIGHT_###`: `initial_days_to_flight`, `remaining_days_to_flight`, `days_to_flight_indicator`)
  - 메시지 클래스 `ZRAP_MSG_###`, 예외 클래스 `ZCM_RAP_###`
  - 인터페이스 BDEF `ZRAP_I_TRAVEL_###`(R-03, `with privileged mode`), 프로젝션 BDEF `ZRAP_C_TRAVEL_###`
- R-01의 `ZCL_RAP_GEN_DATA_###`로 Travel/Booking 데모 데이터가 들어가 있어야 합니다(`OverallStatus = 'O'`인 Travel이 최소 3건).
- 11단계는 R-05 ~ R-06의 비관리형 Order BO `ZRAP_R_ORDER_U_###`(별칭 `Order`, `Item`, 구성 `_Items`, 액션 `approveOrder`)가 필요합니다.
- 표준 객체: `/DMO/CUSTOMER`, `/DMO/AGENCY`, `/DMO/FLIGHT`(트라이얼 시스템에 기본 제공)

**만들 객체**

| 순서 | 객체 유형 | 이름 | 역할 |
|---|---|---|---|
| 1 | ABAP 클래스 | `ZCL_RAP_EML_###` | EML 실습 콘솔 클래스(`if_oo_adt_classrun`). 단계마다 메서드를 하나씩 추가 |

> 진행 방법: 각 단계에서 메서드를 하나 추가하고, `if_oo_adt_classrun~main`에서 그 단계 메서드만 호출한 뒤 F9로 실행하세요. 단계별 정답 코드는 "추가할 부분"만 보여 주고, 10단계 정답 끝에 `main`의 최종 모습을 보여 줍니다. 콘솔 출력 예시의 번호·날짜는 시스템마다 다릅니다.

#### 1단계. 콘솔 클래스 골격과 BDEF 파생 타입 탐색

요구사항
1. `ZCL_RAP_EML_###` 클래스를 만들고 `if_oo_adt_classrun`을 구현하세요.
2. 단계별 메서드는 모두 `IMPORTING out TYPE REF TO if_oo_adt_classrun_out` 하나만 받는 public 인스턴스 메서드로 만듭니다. 이번 단계에서는 `m01_derived_types`를 만듭니다.
3. 공용 헬퍼를 만드세요.
   - `prepare_sample_data`: `ZRAP_ATRAV_###`에서 상태 `O`인 Travel 하나, `ZRAP_ABOOK_###`에서 Booking 하나, `/DMO/CUSTOMER`·`/DMO/AGENCY`에서 아무 고객·여행사 하나, `/DMO/FLIGHT`에서 오늘 이후 항공편 하나를 읽어 private 속성(`mv_travel_id`, `ms_booking_key`, `mv_customer_id`, `mv_agency_id`, `ms_flight`)에 넣습니다. `main` 맨 앞에서 한 번 호출합니다.
   - `print_failed`: `RESPONSE FOR FAILED EARLY ZRAP_R_TRAVEL_###`를 받아 Travel/Booking 실패 줄마다 `키 / %fail-cause / 실패한 연산 플래그`를 출력합니다.
   - `print_reported`: `RESPONSE FOR REPORTED EARLY`를 받아 메시지마다 `심각도 / 텍스트 / %element로 표시된 필드`를 출력합니다. 메시지가 없는 줄(상태 메시지 지우기 줄)은 `(state area 지우기: 이름)`으로 출력합니다.
   - `print_reported_late`: `RESPONSE FOR REPORTED LATE`용 같은 헬퍼(저장 단계 응답용).
4. `m01_derived_types`에서 다음 타입의 데이터 객체를 **모두** 선언하고, `cl_abap_typedescr=>describe_by_data( )->absolute_name`으로 이름을 출력하세요.
   - `TYPE TABLE FOR CREATE` / `UPDATE` / `DELETE` / `READ IMPORT` / `READ RESULT` (Travel), `TYPE TABLE FOR CREATE ZRAP_R_TRAVEL_###\_Booking`, `TYPE TABLE FOR READ RESULT ZRAP_R_TRAVEL_###\_Booking`, `TYPE TABLE FOR READ LINK ZRAP_R_TRAVEL_###\_Booking`
   - `TYPE TABLE FOR ACTION IMPORT/RESULT ZRAP_R_TRAVEL_###~deductDiscount`, `TYPE TABLE FOR FUNCTION IMPORT/RESULT ZRAP_R_TRAVEL_###\\Booking~getDaysToFlight`
   - `TYPE STRUCTURE FOR UPDATE`, `TYPE STRUCTURE FOR PERMISSIONS REQUEST`
   - `TYPE RESPONSE FOR MAPPED/FAILED/REPORTED` (EARLY, LATE 모두)
5. `TYPE TABLE FOR UPDATE` 한 줄에 키를 넣는 방법 6가지(`TravelID`, `%key-TravelID`, `%tky-TravelID`, `%tky-%key-TravelID`, `%pky-TravelID`, `%data-TravelID`)를 모두 써 보고, 모두 같은 값이 되는지 `ASSERT`로 확인하세요.
6. `TYPE TABLE FOR DETERMINATION`이나 `TYPE TABLE FOR VALIDATION`을 콘솔 클래스에 선언하면 어떤 일이 일어나는지 직접 써 보고(주석으로 남김) 이유를 적으세요.

**확인** 활성화 후 F9로 실행하면 콘솔에 파생 타입 이름 목록이 나오고 `ASSERT`에서 덤프가 나지 않아야 합니다. ADT에서 `upd_tab`에 커서를 두고 F2를 누르면 `%tky`, `%pky`, `%pid`, `%is_draft`, `%control`이 보여야 합니다.

<details><summary>정답·해설</summary>

```abap
CLASS zcl_rap_eml_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.

    "단계별 실습 메서드 (단계가 진행되며 아래 목록이 늘어납니다)
    METHODS m01_derived_types IMPORTING out TYPE REF TO if_oo_adt_classrun_out.

  PRIVATE SECTION.
    "BDEF 파생 타입 별칭 - 여러 메서드에서 재사용
    TYPES ty_failed         TYPE RESPONSE FOR FAILED EARLY zrap_r_travel_###.
    TYPES ty_reported       TYPE RESPONSE FOR REPORTED EARLY zrap_r_travel_###.
    TYPES ty_reported_late  TYPE RESPONSE FOR REPORTED LATE zrap_r_travel_###.

    TYPES: BEGIN OF ty_booking_key,
             travel_id  TYPE /dmo/travel_id,
             booking_id TYPE /dmo/booking_id,
           END OF ty_booking_key.

    TYPES: BEGIN OF ty_flight,
             carrier_id    TYPE /dmo/carrier_id,
             connection_id TYPE /dmo/connection_id,
             flight_date   TYPE /dmo/flight_date,
             price         TYPE /dmo/flight_price,
             currency_code TYPE /dmo/currency_code,
           END OF ty_flight.

    DATA mv_travel_id   TYPE /dmo/travel_id.
    DATA ms_booking_key TYPE ty_booking_key.
    DATA mv_customer_id TYPE /dmo/customer_id.
    DATA mv_agency_id   TYPE /dmo/agency_id.
    DATA ms_flight      TYPE ty_flight.

    METHODS prepare_sample_data IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
    METHODS print_failed
      IMPORTING out    TYPE REF TO if_oo_adt_classrun_out
                failed TYPE ty_failed.
    METHODS print_reported
      IMPORTING out      TYPE REF TO if_oo_adt_classrun_out
                reported TYPE ty_reported.
    METHODS print_reported_late
      IMPORTING out      TYPE REF TO if_oo_adt_classrun_out
                reported TYPE ty_reported_late.
    METHODS severity_text
      IMPORTING msg         TYPE REF TO if_abap_behv_message
      RETURNING VALUE(text) TYPE string.
ENDCLASS.


CLASS zcl_rap_eml_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.
    prepare_sample_data( out ).
    m01_derived_types( out ).
  ENDMETHOD.


  METHOD prepare_sample_data.
    "콘솔 클래스는 RAP BO의 '소비자'입니다. 소비자는 SELECT로 데이터를 읽어도 되지만,
    "BO 데이터를 바꿀 때는 반드시 EML을 써야 합니다(테이블 직접 변경 금지).
    SELECT SINGLE FROM zrap_atrav_###
      FIELDS travel_id
      WHERE overall_status = 'O'
      INTO @mv_travel_id.

    SELECT SINGLE FROM zrap_abook_###
      FIELDS travel_id, booking_id
      INTO @ms_booking_key.

    SELECT SINGLE FROM /dmo/customer FIELDS customer_id INTO @mv_customer_id.
    SELECT SINGLE FROM /dmo/agency   FIELDS agency_id   INTO @mv_agency_id.

    DATA(today) = cl_abap_context_info=>get_system_date( ).
    SELECT SINGLE FROM /dmo/flight
      FIELDS carrier_id, connection_id, flight_date, price, currency_code
      WHERE flight_date > @today
      INTO @ms_flight.

    out->write( |샘플 Travel { mv_travel_id }, Booking { ms_booking_key-travel_id }/{ ms_booking_key-booking_id }, | &&
                |고객 { mv_customer_id }, 여행사 { mv_agency_id }, 항공편 { ms_flight-carrier_id } { ms_flight-connection_id } { ms_flight-flight_date }| ).
  ENDMETHOD.


  METHOD print_failed.
    "failed는 깊은 구조: 엔터티 별칭마다 하나의 내부 테이블(failed-travel, failed-booking)
    LOOP AT failed-travel INTO DATA(f_travel).
      out->write( |  FAILED Travel { f_travel-TravelID } (draft={ f_travel-%is_draft }, pid={ f_travel-%pid }) | &&
                  |cause={ f_travel-%fail-cause } create={ f_travel-%create } update={ f_travel-%update } | &&
                  |delete={ f_travel-%delete } acceptTravel={ f_travel-%action-acceptTravel }| ).
    ENDLOOP.
    LOOP AT failed-booking INTO DATA(f_booking).
      out->write( |  FAILED Booking { f_booking-TravelID }/{ f_booking-BookingID } cause={ f_booking-%fail-cause }| ).
    ENDLOOP.
  ENDMETHOD.


  METHOD print_reported.
    LOOP AT reported-travel INTO DATA(r_travel).
      IF r_travel-%msg IS NOT BOUND.
        "%msg 없이 %state_area만 있는 줄 = '이 영역의 이전 상태 메시지를 지워라'는 신호
        out->write( |  (state area 지우기: { r_travel-%state_area }) Travel { r_travel-TravelID }| ).
        CONTINUE.
      ENDIF.
      out->write( |  { severity_text( r_travel-%msg ) } Travel { r_travel-TravelID }: { r_travel-%msg->if_message~get_text( ) }| &&
                  |{ COND string( WHEN r_travel-%element-CustomerID = if_abap_behv=>mk-on THEN ` [필드 CustomerID]` ) }| &&
                  |{ COND string( WHEN r_travel-%element-BeginDate  = if_abap_behv=>mk-on THEN ` [필드 BeginDate]` ) }| &&
                  |{ COND string( WHEN r_travel-%element-AgencyID   = if_abap_behv=>mk-on THEN ` [필드 AgencyID]` ) }| ).
    ENDLOOP.
    LOOP AT reported-booking INTO DATA(r_booking).
      CHECK r_booking-%msg IS BOUND.
      out->write( |  { severity_text( r_booking-%msg ) } Booking { r_booking-TravelID }/{ r_booking-BookingID }: | &&
                  |{ r_booking-%msg->if_message~get_text( ) }| ).
    ENDLOOP.
    "%other: 특정 엔터티에 묶이지 않는 메시지
    LOOP AT reported-%other INTO DATA(other_msg).
      out->write( |  (other) { other_msg->if_message~get_text( ) }| ).
    ENDLOOP.
  ENDMETHOD.


  METHOD print_reported_late.
    LOOP AT reported-travel INTO DATA(r_travel).
      CHECK r_travel-%msg IS BOUND.
      out->write( |  { severity_text( r_travel-%msg ) } (save) Travel { r_travel-TravelID }: { r_travel-%msg->if_message~get_text( ) }| ).
    ENDLOOP.
    LOOP AT reported-booking INTO DATA(r_booking).
      CHECK r_booking-%msg IS BOUND.
      out->write( |  { severity_text( r_booking-%msg ) } (save) Booking { r_booking-BookingID }: { r_booking-%msg->if_message~get_text( ) }| ).
    ENDLOOP.
  ENDMETHOD.


  METHOD severity_text.
    "if_abap_behv_message~m_severity: if_abap_behv_message=>severity-error/warning/information/success
    text = SWITCH #( msg->m_severity
                     WHEN if_abap_behv_message=>severity-error       THEN `E`
                     WHEN if_abap_behv_message=>severity-warning     THEN `W`
                     WHEN if_abap_behv_message=>severity-information THEN `I`
                     WHEN if_abap_behv_message=>severity-success     THEN `S`
                     ELSE `?` ).
  ENDMETHOD.


  METHOD m01_derived_types.
    out->write( `=== 1단계: BDEF 파생 타입 ===` ).

    "--- 표 형태 (TYPE TABLE FOR ...) : 대부분의 EML 피연산자 ---
    DATA create_tab   TYPE TABLE FOR CREATE zrap_r_travel_###.            "CREATE 입력 (%cid, %data, %control)
    DATA update_tab   TYPE TABLE FOR UPDATE zrap_r_travel_###.            "UPDATE 입력 (%cid_ref, %tky, %control)
    DATA delete_tab   TYPE TABLE FOR DELETE zrap_r_travel_###.            "DELETE 입력 (%cid_ref, %tky)
    DATA read_imp     TYPE TABLE FOR READ IMPORT zrap_r_travel_###.       "READ 입력 (키 + %control)
    DATA read_res     TYPE TABLE FOR READ RESULT zrap_r_travel_###.       "READ 결과
    DATA cba_tab      TYPE TABLE FOR CREATE zrap_r_travel_###\_Booking.   "CREATE BY \_Booking 입력 (%target)
    DATA rba_res      TYPE TABLE FOR READ RESULT zrap_r_travel_###\_Booking. "READ BY \_Booking 결과
    DATA rba_link     TYPE TABLE FOR READ LINK zrap_r_travel_###\_Booking.   "source/target 키 쌍
    DATA act_imp      TYPE TABLE FOR ACTION IMPORT zrap_r_travel_###~deductDiscount.  "%param 포함
    DATA act_res      TYPE TABLE FOR ACTION RESULT zrap_r_travel_###~deductDiscount.  "result [1] $self
    DATA fct_imp      TYPE TABLE FOR FUNCTION IMPORT zrap_r_travel_###\\Booking~getDaysToFlight.
    DATA fct_res      TYPE TABLE FOR FUNCTION RESULT zrap_r_travel_###\\Booking~getDaysToFlight.

    "--- 구조 형태 (TYPE STRUCTURE FOR ...) : 표의 줄 타입 / 일부 문장의 단일 피연산자 ---
    DATA update_wa    TYPE STRUCTURE FOR UPDATE zrap_r_travel_###.
    DATA perm_request TYPE STRUCTURE FOR PERMISSIONS REQUEST zrap_r_travel_###.

    "--- 응답 (TYPE RESPONSE FOR ...) : 엔터티별 표를 가진 깊은 구조 ---
    DATA mapped_early   TYPE RESPONSE FOR MAPPED EARLY zrap_r_travel_###.   "상호작용 단계 (EARLY = 생략 가능)
    DATA failed_early   TYPE RESPONSE FOR FAILED EARLY zrap_r_travel_###.
    DATA reported_early TYPE RESPONSE FOR REPORTED EARLY zrap_r_travel_###.
    DATA mapped_late    TYPE RESPONSE FOR MAPPED LATE zrap_r_travel_###.    "저장 단계 (adjust_numbers 의 mapped: %tmp 포함)
    DATA failed_late    TYPE RESPONSE FOR FAILED LATE zrap_r_travel_###.
    DATA reported_late  TYPE RESPONSE FOR REPORTED LATE zrap_r_travel_###.

    "구현 클래스(행동 풀) 안에서만 쓸 수 있는 타입 - 콘솔 클래스에서는 문법 오류가 납니다.
    "DATA det TYPE TABLE FOR DETERMINATION zrap_r_travel_###~setInitialValues.
    "DATA val TYPE TABLE FOR VALIDATION zrap_r_travel_###~validateCustomer.
    "DATA feat TYPE TABLE FOR INSTANCE FEATURES RESULT zrap_r_travel_###.

    DATA(names) = VALUE string_table(
      ( cl_abap_typedescr=>describe_by_data( create_tab )->absolute_name )
      ( cl_abap_typedescr=>describe_by_data( update_tab )->absolute_name )
      ( cl_abap_typedescr=>describe_by_data( delete_tab )->absolute_name )
      ( cl_abap_typedescr=>describe_by_data( read_imp )->absolute_name )
      ( cl_abap_typedescr=>describe_by_data( read_res )->absolute_name )
      ( cl_abap_typedescr=>describe_by_data( cba_tab )->absolute_name )
      ( cl_abap_typedescr=>describe_by_data( rba_res )->absolute_name )
      ( cl_abap_typedescr=>describe_by_data( rba_link )->absolute_name )
      ( cl_abap_typedescr=>describe_by_data( act_imp )->absolute_name )
      ( cl_abap_typedescr=>describe_by_data( act_res )->absolute_name )
      ( cl_abap_typedescr=>describe_by_data( fct_imp )->absolute_name )
      ( cl_abap_typedescr=>describe_by_data( fct_res )->absolute_name )
      ( cl_abap_typedescr=>describe_by_data( update_wa )->absolute_name )
      ( cl_abap_typedescr=>describe_by_data( perm_request )->absolute_name )
      ( cl_abap_typedescr=>describe_by_data( mapped_early )->absolute_name )
      ( cl_abap_typedescr=>describe_by_data( failed_early )->absolute_name )
      ( cl_abap_typedescr=>describe_by_data( reported_early )->absolute_name )
      ( cl_abap_typedescr=>describe_by_data( mapped_late )->absolute_name )
      ( cl_abap_typedescr=>describe_by_data( failed_late )->absolute_name )
      ( cl_abap_typedescr=>describe_by_data( reported_late )->absolute_name ) ).
    out->write( names ).

    "--- 키 컴포넌트 그룹: 모두 같은 TravelID 컴포넌트를 가리킵니다 ---
    update_tab = VALUE #(
      ( TravelID              = '00000001' )
      ( %key-TravelID         = '00000002' )
      ( %tky-TravelID         = '00000003' )
      ( %tky-%key-TravelID    = '00000004' )
      ( %pky-TravelID         = '00000005' )
      ( %data-TravelID        = '00000006' ) ).

    ASSERT update_tab[ 1 ]-%tky-TravelID = '00000001'.
    ASSERT update_tab[ 2 ]-TravelID      = '00000002'.
    ASSERT update_tab[ 3 ]-%key-TravelID = '00000003'.
    ASSERT update_tab[ 4 ]-%pky-TravelID = '00000004'.
    ASSERT update_tab[ 5 ]-%data-TravelID = '00000005'.
    ASSERT update_tab[ 6 ]-%tky-%pky-%key-TravelID = '00000006'.

    "%tky = %pky(%pid + %key) + %is_draft  (late numbering + draft BO 이므로 셋 다 있음)
    update_wa = VALUE #( %tky = VALUE #( %is_draft = if_abap_behv=>mk-on
                                         TravelID  = '00000007' )
                         Description          = 'demo'
                         %control-Description = if_abap_behv=>mk-on ).
    out->write( |%tky-%is_draft={ update_wa-%is_draft }, %pid(초기값)={ update_wa-%pid }, %control-Description={ update_wa-%control-Description }| ).

    "%param: 액션 파라미터 (추상 엔터티 ZRAP_A_DISCOUNT_### 의 필드)
    act_imp = VALUE #( ( TravelID = '00000001' %param-discount_percent = 10 ) ).
    out->write( |deductDiscount %param-discount_percent = { act_imp[ 1 ]-%param-discount_percent }| ).

    "CREATE BY 의 %target: 자식 인스턴스 표
    cba_tab = VALUE #( ( %cid_ref = 'T1'
                         %target  = VALUE #( ( %cid = 'B1' CarrierID = 'LH' ) ) ) ).
    out->write( |cba %target 줄 수 = { lines( cba_tab[ 1 ]-%target ) }| ).

    CLEAR: create_tab, delete_tab, read_imp, read_res, rba_res, rba_link, act_res,
           fct_imp, fct_res, perm_request, mapped_early, failed_early, reported_early,
           mapped_late, failed_late, reported_late.
  ENDMETHOD.

ENDCLASS.
```

콘솔 출력 예시

```
샘플 Travel 00000003, Booking 00000001/0010, 고객 000001, 여행사 070001, 항공편 LH 0400 20261121
=== 1단계: BDEF 파생 타입 ===
\BDEF=ZRAP_R_TRAVEL_###\TYPE=CREATE\ENTITY=TRAVEL ...
...
%tky-%is_draft=01, %pid(초기값)=00000000000000000000000000000000, %control-Description=01
deductDiscount %param-discount_percent = 10
cba %target 줄 수 = 1
```

(절대 타입 이름의 정확한 표기는 시스템에서 확인하세요. 중요한 것은 F2로 본 컴포넌트 구성입니다.)

**왜 이렇게 쓰나**
- EML 문장의 피연산자와 행동 풀 메서드의 파라미터는 모두 BDEF에서 파생된 타입입니다. BDEF에 `create;`가 없으면 `TYPE TABLE FOR CREATE`도 만들 수 없고, `late numbering`이 없으면 `%pid`가 없으며, `with draft`가 없으면 `%is_draft`가 없습니다. 즉 F2로 타입을 보면 BDEF가 어떻게 정의되었는지 거꾸로 알 수 있습니다.
- 짧은 형식 `zrap_r_travel_###`은 루트 엔터티, `zrap_r_travel_###\\Booking`은 별칭으로 지정한 자식 엔터티, `zrap_r_travel_###\_Booking`은 연관을 뜻합니다. 액션·함수는 `~이름`으로 붙입니다.
- `%tky`를 쓰는 습관을 들이세요. 지금은 draft·late numbering BO라서 `%tky`에 `%is_draft`, `%pid`가 다 들어 있고, 나중에 BO 구조가 바뀌어도 코드를 고칠 일이 줄어듭니다. 반대로 서로 다른 엔터티의 `%tky`끼리 대입(`booking-%tky = travel-%tky`)하면 구성이 달라 문법 경고·오류가 나므로 `CORRESPONDING #( )`을 씁니다.
- `FOR DETERMINATION`, `FOR VALIDATION`, `FOR ... FEATURES`, `FOR ... AUTHORIZATION`, `FOR CHANGE` 타입은 구현 클래스 안에서만 쓸 수 있습니다. 콘솔 클래스에 선언하면 활성화 단계에서 문법 오류가 납니다(오류 문구는 시스템에서 확인).
- `EARLY`/`LATE`: 상호작용 단계(MODIFY/READ, 대부분의 핸들러 메서드)와 저장 단계(`COMMIT ENTITIES` 응답, 세이버 메서드)의 응답 타입이 다릅니다. 예를 들어 `RESPONSE FOR MAPPED LATE`에는 `adjust_numbers`에서 쓰는 `%tmp`(이전 임시 키)가 들어 있습니다.

**자주 나는 오류와 해결**
- `Type "ZRAP_R_TRAVEL_###~DEDUCTDISCOUNT" is unknown` 같은 오류: 액션 이름의 대소문자는 상관없지만 BDEF에 `parameter`가 없는 액션에는 `%param`이 없습니다. BDEF의 액션 정의를 다시 보세요.
- 함수 타입은 Booking 엔터티에 있으므로 `zrap_r_travel_###\\Booking~getDaysToFlight`처럼 엔터티를 꼭 적어야 합니다.

</details>

#### 2단계. READ ENTITIES: 필드 지정, 연관 읽기, FAILED/REPORTED

요구사항
1. 메서드 `m02_read`를 추가하세요.
2. **긴 형식 + FIELDS**: `READ ENTITIES OF zrap_r_travel_### ENTITY Travel FIELDS ( TravelID CustomerID BeginDate EndDate TotalPrice CurrencyCode OverallStatus ) WITH ...`로 `mv_travel_id`와 존재하지 않는 `'99999999'` 두 키를 읽고, 결과 건수와 `failed-travel`의 `%fail-cause`를 출력하세요. `%fail-cause`가 `if_abap_behv=>cause-not_found`인지 비교해 "없음"이라고 출력합니다.
3. **ALL FIELDS**: 같은 Travel을 `ALL FIELDS WITH`로 읽어 `Description`, `LastChangedAt`을 출력하세요.
4. **FROM + %control**: `TYPE TABLE FOR READ IMPORT`를 직접 채워 `%control-Description`, `%control-BookingFee`만 켜서 읽으세요. 결과의 `TotalPrice`가 비어 있는지(읽지 않았으니 초기값) 확인해 출력합니다.
5. **짧은 형식**: `READ ENTITY zrap_r_travel_###\\Booking`으로 `ms_booking_key`의 Booking을 `FIELDS ( FlightDate FlightPrice BookingStatus )`로 읽으세요.
6. **연관 읽기(부모→자식)**: `ENTITY Travel BY \_Booking`으로 `mv_travel_id`의 모든 Booking을 읽고 `LINK`로 받은 source/target 키 쌍을 출력하세요.
7. **연관 읽기(자식→부모)**: `ENTITY Booking BY \_Travel`로 Booking에서 부모 Travel의 `Description`을 읽으세요.
8. **한 문장에서 여러 읽기("깊은 읽기")**: 한 `READ ENTITIES` 문장 안에 `ENTITY Travel ... RESULT`와 `ENTITY Travel BY \_Booking ... RESULT`를 함께 넣어 Travel 1건과 그 Booking들을 한 번에 읽고, Travel마다 Booking 수를 출력하세요.
9. draft BO이므로 `%is_draft`를 지정하지 않으면 무엇을 읽는지(활성/draft) 주석으로 적으세요.

**확인** 콘솔에 "99999999: 없음(not_found)" 줄, `%control`로 읽지 않은 `TotalPrice = 0.00`, LINK 줄 수 = Booking 수, 한 문장 읽기 결과가 2단계 6번과 같은 건수로 나와야 합니다.

<details><summary>정답·해설</summary>

정의부 `PUBLIC SECTION`에 추가:

```abap
    METHODS m02_read IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
```

구현부에 추가:

```abap
  METHOD m02_read.
    out->write( `=== 2단계: READ ENTITIES ===` ).

    "1) 긴 형식 + FIELDS ( ... ) WITH : 나열한 필드의 %control 이 자동으로 켜짐
    READ ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        FIELDS ( TravelID CustomerID BeginDate EndDate TotalPrice CurrencyCode OverallStatus )
        WITH VALUE #( ( TravelID = mv_travel_id )
                      ( TravelID = '99999999' ) )        "없는 키
        RESULT DATA(travels)
      FAILED DATA(failed)
      REPORTED DATA(reported).

    out->write( |읽은 Travel 수: { lines( travels ) }| ).
    LOOP AT travels INTO DATA(travel).
      out->write( |  { travel-TravelID } 고객 { travel-CustomerID } { travel-BeginDate }~{ travel-EndDate } | &&
                  |{ travel-TotalPrice } { travel-CurrencyCode } 상태 { travel-OverallStatus }| ).
    ENDLOOP.
    LOOP AT failed-travel INTO DATA(f).
      out->write( |  { f-TravelID }: { COND string( WHEN f-%fail-cause = if_abap_behv=>cause-not_found
                                                     THEN `없음(not_found)`
                                                     ELSE |원인 { f-%fail-cause }| ) }| ).
    ENDLOOP.
    print_reported( out = out reported = reported ).

    "2) ALL FIELDS WITH : 모든 필드
    READ ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        ALL FIELDS WITH VALUE #( ( TravelID = mv_travel_id ) )
        RESULT DATA(travels_all).
    out->write( |ALL FIELDS: 설명="{ travels_all[ 1 ]-Description }", LastChangedAt={ travels_all[ 1 ]-LastChangedAt }| ).

    "3) FROM : %control 을 직접 채움 (FIELDS 대신)
    DATA read_keys TYPE TABLE FOR READ IMPORT zrap_r_travel_###.
    read_keys = VALUE #( ( TravelID             = mv_travel_id
                           %control-Description = if_abap_behv=>mk-on
                           %control-BookingFee  = if_abap_behv=>mk-on ) ).
    READ ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        FROM read_keys
        RESULT DATA(travels_ctrl).
    out->write( |FROM+%control: 설명="{ travels_ctrl[ 1 ]-Description }", 수수료={ travels_ctrl[ 1 ]-BookingFee }, | &&
                |TotalPrice(안 읽음)={ travels_ctrl[ 1 ]-TotalPrice }| ).

    "4) 짧은 형식 READ ENTITY : 엔터티 하나, ENTITY 절 없이
    READ ENTITY zrap_r_travel_###\\Booking
      FIELDS ( FlightDate FlightPrice BookingStatus )
      WITH VALUE #( ( TravelID  = ms_booking_key-travel_id
                      BookingID = ms_booking_key-booking_id ) )
      RESULT DATA(bookings_short).
    IF bookings_short IS NOT INITIAL.
      out->write( |READ ENTITY(짧은 형식): 비행일 { bookings_short[ 1 ]-FlightDate } 가격 { bookings_short[ 1 ]-FlightPrice } | &&
                  |상태 { bookings_short[ 1 ]-BookingStatus }| ).
    ENDIF.

    "5) 연관 읽기 부모 -> 자식, LINK 로 키 쌍 받기
    READ ENTITIES OF zrap_r_travel_###
      ENTITY Travel BY \_Booking
        FIELDS ( BookingID CarrierID ConnectionID FlightDate )
        WITH VALUE #( ( TravelID = mv_travel_id ) )
        RESULT DATA(bookings)
        LINK DATA(links).
    out->write( |BY \\_Booking: Booking { lines( bookings ) }건, LINK { lines( links ) }줄| ).
    LOOP AT links INTO DATA(link).
      out->write( |  source { link-source-TravelID } -> target { link-target-TravelID }/{ link-target-BookingID }| ).
    ENDLOOP.

    "6) 연관 읽기 자식 -> 부모
    READ ENTITIES OF zrap_r_travel_###
      ENTITY Booking BY \_Travel
        FIELDS ( Description )
        WITH VALUE #( ( TravelID  = ms_booking_key-travel_id
                        BookingID = ms_booking_key-booking_id ) )
        RESULT DATA(parents).
    IF parents IS NOT INITIAL.
      out->write( |BY \\_Travel: 부모 설명="{ parents[ 1 ]-Description }"| ).
    ENDIF.

    "7) 한 문장에서 여러 ENTITY 절: 루트 + 자식을 한 요청으로
    "   EML 결과는 '평평한' 표 여러 개입니다. 깊은(중첩) 결과 타입은 없으므로 LINK 나 키로 묶습니다.
    READ ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        FIELDS ( Description OverallStatus ) WITH VALUE #( ( TravelID = mv_travel_id ) )
        RESULT DATA(deep_travels)
      ENTITY Travel BY \_Booking
        FIELDS ( BookingID FlightPrice ) WITH VALUE #( ( TravelID = mv_travel_id ) )
        RESULT DATA(deep_bookings)
      FAILED DATA(deep_failed).
    LOOP AT deep_travels INTO DATA(dt).
      out->write( |한 문장 읽기: Travel { dt-TravelID } → Booking { lines( FILTER #( deep_bookings USING KEY entity
                                                                                     WHERE TravelID = dt-TravelID ) ) }건| ).
    ENDLOOP.
    print_failed( out = out failed = deep_failed ).

    "%is_draft 를 지정하지 않으면 if_abap_behv=>mk-off(활성 인스턴스)를 읽습니다.
    "draft 를 읽으려면 키에 %is_draft = if_abap_behv=>mk-on 을 넣습니다(6단계).
  ENDMETHOD.
```

> `FILTER #( ... USING KEY entity WHERE TravelID = ... )` 부분은 결과 표의 보조 키 `entity`(`%key` 포함, 08 치트시트 "Secondary Table Keys" 참고)를 쓰는 예입니다. `FILTER`가 이 키 구성과 맞지 않는다는 문법 오류가 나면 `REDUCE i( INIT n = 0 FOR b IN deep_bookings WHERE ( TravelID = dt-TravelID ) NEXT n = n + 1 )`로 바꾸세요(실제 시스템에서 확인 필요).

콘솔 출력 예시

```
=== 2단계: READ ENTITIES ===
읽은 Travel 수: 1
  00000003 고객 000001 20261120~20261130 1250.00 EUR 상태 O
  99999999: 없음(not_found)
ALL FIELDS: 설명="Business trip", LastChangedAt=20261017031522.1234560
FROM+%control: 설명="Business trip", 수수료=50.00, TotalPrice(안 읽음)=0.00
READ ENTITY(짧은 형식): 비행일 20261121 가격 600.00 상태 N
BY \_Booking: Booking 2건, LINK 2줄
  source 00000003 -> target 00000003/0010
  source 00000003 -> target 00000003/0020
BY \_Travel: 부모 설명="Business trip"
한 문장 읽기: Travel 00000003 → Booking 2건
```

**왜 이렇게 쓰나**
- `READ`는 BDEF에 따로 적지 않아도 모든 엔터티에서 항상 쓸 수 있습니다. 결과는 트랜잭션 버퍼의 현재 상태입니다. 같은 LUW에서 아직 저장하지 않은 변경도 보입니다.
- `FIELDS ( ... ) WITH`는 `%control`을 자동으로 채우는 지름길이고, `FROM`은 `%control`을 직접 채워야 합니다. `%control`을 켜지 않은 필드는 결과에 초기값으로 옵니다. 필요한 필드만 읽는 것이 성능상 좋고, 행동 풀 안에서는 3장 품질 기준대로 반드시 `FIELDS ( ... )`로 필요한 필드만 읽습니다.
- 없는 키는 예외가 아니라 `failed`로 돌아옵니다. `%fail-cause`로 원인(`not_found`, `locked`, `unauthorized`, `disabled` 등)을 구분하세요. `reported`에는 메시지가 들어 있을 수도, 없을 수도 있습니다(관리형 읽기는 보통 메시지 없이 failed만).
- `LINK`는 연관 읽기에서 "어느 부모의 어느 자식인지" 키 쌍을 돌려줍니다. 결과 표만으로는 부모를 알기 어려운 경우(예: 부모 키가 자식 키에 없을 때)에 필요합니다.

</details>

#### 3단계. MODIFY ENTITIES: CREATE, %cid/%cid_ref, 깊은 생성, UPDATE, DELETE

요구사항
1. 메서드 `m03_modify`를 추가하세요. 시작할 때 `ROLLBACK ENTITIES.`로 버퍼를 비웁니다.
2. **짧은 형식 CREATE**: `MODIFY ENTITY zrap_r_travel_### CREATE FIELDS ( ... ) WITH ...`로 Travel 1건을 만드세요(`%cid = 'T_SHORT'`, 고객·여행사 = 샘플, 시작일 = 오늘+30, 종료일 = 오늘+40, 수수료 20 EUR, 설명 `'EML short form'`). `mapped-travel`의 `%cid`, `%pid`, `TravelID`를 출력하고 late numbering이라 `TravelID`가 비어 있음을 확인하세요.
3. **깊은 생성 + 같은 요청 안의 참조**: 긴 형식 한 문장에서
   - Travel `%cid = 'T_DEEP'` 생성,
   - `CREATE BY \_Booking`으로 `%cid_ref = 'T_DEEP'`에 Booking 2건(`%cid = 'B1'`, `'B2'`, 샘플 항공편, `BookingStatus = 'N'`) 생성,
   - `UPDATE FIELDS ( Description )`로 `%cid_ref = 'T_DEEP'`의 설명을 `'changed via %cid_ref'`로 변경,
   - `ENTITY Booking UPDATE FIELDS ( FlightPrice )`로 `%cid_ref = 'B2'`의 가격을 999로 변경
   을 한 번에 하세요. `MAPPED`, `FAILED`, `REPORTED`를 받아 출력합니다.
4. 같은 요청 안의 인스턴스를 `READ`로 다시 읽어 설명·가격·`TotalPrice`(결정 `calculateTotalPrice`가 계산)를 출력하세요. 이때 키로 무엇을 넘겨야 하는지 생각해 보세요(힌트: `mapped`의 `%pid`).
5. **AUTO FILL CID**: `%cid`를 지정하지 않고 `CREATE AUTO FILL CID FIELDS ( ... ) WITH`로 1건 만드세요.
6. **UPDATE(기존 인스턴스)**: 샘플 Travel의 `Description`을 `FROM` + `%control`로 바꾸고, `BookingFee`는 값만 넣고 `%control`을 끈 상태로 두어 바뀌지 않음을 확인하세요.
7. **DELETE**: 2번에서 만든 `T_SHORT`를 `%pid`로 삭제하세요(`DELETE FROM`).
8. 마지막에 `ROLLBACK ENTITIES`로 모두 버리고, 같은 `%pid`로 다시 읽어 `failed`가 나오는지 확인하세요.

**확인** 콘솔에 `mapped`의 `%pid`(16바이트 값)와 비어 있는 `TravelID`, 같은 요청에서 바꾼 설명 `'changed via %cid_ref'`, Booking 가격 999, ROLLBACK 이후 `not_found`가 나와야 합니다. DB 테이블(Data Preview)에는 아무것도 저장되지 않아야 합니다.

<details><summary>정답·해설</summary>

정의부에 추가:

```abap
    METHODS m03_modify IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
```

구현부에 추가:

```abap
  METHOD m03_modify.
    out->write( `=== 3단계: MODIFY ENTITIES ===` ).
    ROLLBACK ENTITIES.   "이전 단계의 버퍼 내용을 확실히 비움

    DATA(today) = cl_abap_context_info=>get_system_date( ).

    "1) 짧은 형식 CREATE (엔터티 하나, ENTITY 절 없음)
    MODIFY ENTITY zrap_r_travel_###
      CREATE FIELDS ( CustomerID AgencyID BeginDate EndDate BookingFee CurrencyCode Description )
      WITH VALUE #( ( %cid         = 'T_SHORT'
                      CustomerID   = mv_customer_id
                      AgencyID     = mv_agency_id
                      BeginDate    = today + 30
                      EndDate      = today + 40
                      BookingFee   = '20.00'
                      CurrencyCode = 'EUR'
                      Description  = 'EML short form' ) )
      MAPPED DATA(mapped_short)
      FAILED DATA(failed_short)
      REPORTED DATA(reported_short).

    LOOP AT mapped_short-travel INTO DATA(ms).
      out->write( |CREATE(짧은): %cid={ ms-%cid } %pid={ ms-%pid } TravelID="{ ms-TravelID }" (late numbering → 아직 비어 있음)| ).
    ENDLOOP.
    print_failed( out = out failed = failed_short ).
    print_reported( out = out reported = reported_short ).

    "2) 긴 형식: 루트 생성 + CREATE BY \_Booking + %cid_ref 로 같은 요청 안에서 UPDATE
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        CREATE FIELDS ( CustomerID AgencyID BeginDate EndDate BookingFee CurrencyCode Description )
        WITH VALUE #( ( %cid         = 'T_DEEP'
                        CustomerID   = mv_customer_id
                        AgencyID     = mv_agency_id
                        BeginDate    = ms_flight-flight_date
                        EndDate      = ms_flight-flight_date + 5
                        BookingFee   = '30.00'
                        CurrencyCode = ms_flight-currency_code
                        Description  = 'EML deep create' ) )
        CREATE BY \_Booking
          FIELDS ( CustomerID CarrierID ConnectionID FlightDate FlightPrice CurrencyCode BookingStatus )
          WITH VALUE #( ( %cid_ref = 'T_DEEP'                "부모를 %cid 로 참조
                          %target  = VALUE #(
                            ( %cid          = 'B1'
                              CustomerID    = mv_customer_id
                              CarrierID     = ms_flight-carrier_id
                              ConnectionID  = ms_flight-connection_id
                              FlightDate    = ms_flight-flight_date
                              FlightPrice   = ms_flight-price
                              CurrencyCode  = ms_flight-currency_code
                              BookingStatus = 'N' )
                            ( %cid          = 'B2'
                              CustomerID    = mv_customer_id
                              CarrierID     = ms_flight-carrier_id
                              ConnectionID  = ms_flight-connection_id
                              FlightDate    = ms_flight-flight_date
                              FlightPrice   = ms_flight-price
                              CurrencyCode  = ms_flight-currency_code
                              BookingStatus = 'N' ) ) ) )
        UPDATE FIELDS ( Description )
          WITH VALUE #( ( %cid_ref = 'T_DEEP' Description = 'changed via %cid_ref' ) )
      ENTITY Booking
        UPDATE FIELDS ( FlightPrice )
          WITH VALUE #( ( %cid_ref = 'B2' FlightPrice = '999.00' ) )
      MAPPED DATA(mapped_deep)
      FAILED DATA(failed_deep)
      REPORTED DATA(reported_deep).

    out->write( |깊은 생성: mapped Travel { lines( mapped_deep-travel ) }건, Booking { lines( mapped_deep-booking ) }건| ).
    LOOP AT mapped_deep-booking INTO DATA(mb).
      out->write( |  Booking %cid={ mb-%cid } %pid={ mb-%pid }| ).
    ENDLOOP.
    print_failed( out = out failed = failed_deep ).
    print_reported( out = out reported = reported_deep ).

    "3) 같은 LUW 안에서 다시 읽기: 키 대신 mapped 의 %pid(+%key)를 그대로 넘김
    "   CORRESPONDING 으로 %pid, %key, %is_draft 등 이름이 같은 컴포넌트가 복사됨
    IF mapped_deep-travel IS NOT INITIAL.
      READ ENTITIES OF zrap_r_travel_###
        ENTITY Travel
          FIELDS ( Description TotalPrice CurrencyCode ) WITH CORRESPONDING #( mapped_deep-travel )
          RESULT DATA(new_travels)
        ENTITY Booking
          FIELDS ( FlightPrice ) WITH CORRESPONDING #( mapped_deep-booking )
          RESULT DATA(new_bookings).
      out->write( |다시 읽기: 설명="{ new_travels[ 1 ]-Description }" 합계={ new_travels[ 1 ]-TotalPrice } { new_travels[ 1 ]-CurrencyCode }| ).
      LOOP AT new_bookings INTO DATA(nb).
        out->write( |  Booking 가격 { nb-FlightPrice }| ).
      ENDLOOP.
    ENDIF.

    "4) AUTO FILL CID : %cid 자동 채움 (그 대신 같은 요청에서 %cid_ref 로 참조 불가)
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        CREATE AUTO FILL CID
        FIELDS ( CustomerID AgencyID BeginDate EndDate CurrencyCode Description )
        WITH VALUE #( ( CustomerID   = mv_customer_id
                        AgencyID     = mv_agency_id
                        BeginDate    = today + 50
                        EndDate      = today + 55
                        CurrencyCode = 'EUR'
                        Description  = 'AUTO FILL CID' ) )
      MAPPED DATA(mapped_auto).
    out->write( |AUTO FILL CID: 자동 %cid="{ mapped_auto-travel[ 1 ]-%cid }"| ).

    "5) 기존 인스턴스 UPDATE (FROM + %control)
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        UPDATE FROM VALUE #( ( TravelID             = mv_travel_id
                               Description          = 'updated by EML'
                               BookingFee           = '12345.00'          "%control 꺼짐 → 무시됨
                               %control-Description = if_abap_behv=>mk-on
                               %control-BookingFee  = if_abap_behv=>mk-off ) )
      FAILED DATA(failed_upd)
      REPORTED DATA(reported_upd).
    print_failed( out = out failed = failed_upd ).
    print_reported( out = out reported = reported_upd ).

    READ ENTITIES OF zrap_r_travel_###
      ENTITY Travel FIELDS ( Description BookingFee ) WITH VALUE #( ( TravelID = mv_travel_id ) )
      RESULT DATA(upd_check).
    out->write( |UPDATE 후: 설명="{ upd_check[ 1 ]-Description }" 수수료={ upd_check[ 1 ]-BookingFee } (12345 아님)| ).

    "6) DELETE : %pid 로 (late numbering 이라 아직 TravelID 가 없음)
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        DELETE FROM VALUE #( ( %pid = mapped_short-travel[ 1 ]-%pid ) )
      FAILED DATA(failed_del).
    out->write( |DELETE: 실패 { lines( failed_del-travel ) }건| ).

    "7) ROLLBACK ENTITIES : 버퍼 전체를 버림 (DB 에는 아무 것도 안 감)
    ROLLBACK ENTITIES.
    READ ENTITIES OF zrap_r_travel_###
      ENTITY Travel FIELDS ( Description ) WITH CORRESPONDING #( mapped_deep-travel )
      RESULT DATA(after_rollback)
      FAILED DATA(failed_rb).
    out->write( |ROLLBACK 후 다시 읽기: 결과 { lines( after_rollback ) }건| ).
    print_failed( out = out failed = failed_rb ).
  ENDMETHOD.
```

콘솔 출력 예시

```
=== 3단계: MODIFY ENTITIES ===
CREATE(짧은): %cid=T_SHORT %pid=3F2A...C1 TravelID="" (late numbering → 아직 비어 있음)
깊은 생성: mapped Travel 1건, Booking 2건
  Booking %cid=B1 %pid=7B10...04
  Booking %cid=B2 %pid=7B10...05
다시 읽기: 설명="changed via %cid_ref" 합계=1229.00 EUR
  Booking 가격 600.00
  Booking 가격 999.00
AUTO FILL CID: 자동 %cid="..."
UPDATE 후: 설명="updated by EML" 수수료=50.00 (12345 아님)
DELETE: 실패 0건
ROLLBACK 후 다시 읽기: 결과 0건
  FAILED Travel  (draft=00, pid=...) cause=1 ...
```

(합계 1229 = 수수료 30 + 600 + 999 처럼 R-02의 `calculateTotalPrice` 규칙에 따라 달라집니다. `%fail-cause`의 숫자 값은 상수 이름으로 비교하세요.)

**왜 이렇게 쓰나**
- `%cid`는 한 EML 요청 안에서만 유효한 임시 이름표입니다. 키가 아직 없는 새 인스턴스를 같은 요청 안에서 `%cid_ref`로 다시 가리킬 수 있습니다(UPDATE, DELETE, CREATE BY, EXECUTE). 쓸 일이 없어도 `%cid`는 항상 채우는 것이 원칙이며, 귀찮으면 `AUTO FILL CID`를 씁니다.
- late numbering에서 새 인스턴스의 최종 `TravelID`는 저장 단계의 `adjust_numbers`에서야 정해집니다. 그때까지 인스턴스를 가리키는 것은 `%pid`(+ 비어 있는 `%key`)입니다. 다음 EML 문장에서는 `CORRESPONDING #( mapped-travel )`처럼 `mapped`를 그대로 키로 넘기면 `%pid`와 `%key`가 함께 넘어가 안전합니다.
- 깊은 생성은 `CREATE` + `CREATE BY \_Booking`을 한 문장에 넣는 것입니다. 자식 `%target` 줄마다 `%cid`를 주면 다음 줄에서 자식도 `%cid_ref`로 바꿀 수 있습니다. 루트와 자식을 한 요청에 넣으면 결정(determination)도 한 번에 정리된 상태에서 실행됩니다.
- `FIELDS`에 없는 필드나 `%control`이 꺼진 필드는 값이 있어도 무시됩니다. 이는 "보낸 필드만 바꾼다(PATCH)"는 OData 동작과 같습니다.
- `ROLLBACK ENTITIES`는 버퍼와 잠금을 모두 버리고 `cleanup`을 부릅니다. 콘솔에서 실험할 때 DB를 더럽히지 않는 가장 좋은 방법입니다.

**자주 나는 오류와 해결**
- `%cid_ref`로 가리킨 `%cid`가 같은 요청에 없으면 런타임 오류가 납니다(08 치트시트 Update 예제 주석). `%cid_ref`는 같은 `MODIFY` 문장 안에서만 쓰세요.
- 읽기 전용 필드(`TravelID`, `TotalPrice` 등)를 `FIELDS`에 넣으면 `failed`가 나거나 런타임 오류가 납니다(BDEF `field ( readonly )`).
- 필수 필드(`field ( mandatory )`)를 빠뜨려도 MODIFY는 성공하고, 저장 단계 검증이나 draft Prepare에서 오류가 납니다. 이 차이는 4단계에서 확인합니다.

</details>

#### 4단계. COMMIT ENTITIES 변형과 late numbering 최종 키 얻기

요구사항
1. 메서드 `m04_commit`과, 재사용할 private 메서드 `create_travel_and_commit RETURNING VALUE(travel_id) TYPE /dmo/travel_id`를 추가하세요.
2. `create_travel_and_commit`: Travel 1건 + Booking 1건을 깊은 생성한 뒤 `COMMIT ENTITIES BEGIN RESPONSE OF zrap_r_travel_### FAILED DATA(...) REPORTED DATA(...)`, `CONVERT KEY`, `COMMIT ENTITIES END.`로 최종 `TravelID`를 받아 돌려주세요. `sy-subrc`가 0이 아니면 빈 값을 돌려줍니다.
3. `m04_commit`에서 다음을 차례로 해 보세요.
   - (a) **짧은 형식** `COMMIT ENTITIES.` 후 `sy-subrc` 출력 (성공 사례: 샘플 Travel의 설명 변경)
   - (b) **RESPONSES**: 일부러 검증 오류(고객 `'999999'`, 종료일 < 시작일)가 나는 Travel을 만들고 `COMMIT ENTITIES RESPONSES FAILED DATA(f) REPORTED DATA(r).` → `sy-subrc = 4`, 응답 표(`abp_behv_response_tab`) 줄 수 출력
   - (c) 같은 오류를 **RESPONSE OF**(긴 형식)로 받아 `print_reported_late`로 메시지(`Customer 999999 does not exist.` 등) 출력, 이어서 `ROLLBACK ENTITIES`
   - (d) **IN SIMULATION MODE**: 정상 Travel을 만들어 `COMMIT ENTITIES IN SIMULATION MODE.` → DB에 없음을 SELECT로 확인 → `ROLLBACK ENTITIES`
   - (e) `create_travel_and_commit`을 호출해 최종 TravelID를 출력하고, 그 TravelID로 `ZRAP_ATRAV_###`를 SELECT해 저장됐는지 확인
4. 왜 오류가 MODIFY 때가 아니라 COMMIT 때 나는지, `sy-subrc = 4` 다음에 무엇을 해야 하는지 주석으로 설명하세요.

**확인** (b)·(c)에서 `sy-subrc = 4`와 R-02의 검증 메시지, (d)에서 "DB에 없음", (e)에서 8자리 최종 TravelID와 DB 존재 확인이 출력되어야 합니다.

<details><summary>정답·해설</summary>

정의부에 추가:

```abap
    METHODS m04_commit IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
```

`PRIVATE SECTION`에 추가:

```abap
    METHODS create_travel_and_commit
      IMPORTING out              TYPE REF TO if_oo_adt_classrun_out
                description      TYPE /dmo/description DEFAULT 'EML committed'
      RETURNING VALUE(travel_id) TYPE /dmo/travel_id.
```

구현부에 추가:

```abap
  METHOD create_travel_and_commit.
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        CREATE FIELDS ( CustomerID AgencyID BeginDate EndDate BookingFee CurrencyCode Description )
        WITH VALUE #( ( %cid         = 'NEW'
                        CustomerID   = mv_customer_id
                        AgencyID     = mv_agency_id
                        BeginDate    = ms_flight-flight_date
                        EndDate      = ms_flight-flight_date + 3
                        BookingFee   = '15.00'
                        CurrencyCode = ms_flight-currency_code
                        Description  = description ) )
        CREATE BY \_Booking
          FIELDS ( CustomerID CarrierID ConnectionID FlightDate FlightPrice CurrencyCode BookingStatus )
          WITH VALUE #( ( %cid_ref = 'NEW'
                          %target  = VALUE #( ( %cid          = 'NEW_B1'
                                                CustomerID    = mv_customer_id
                                                CarrierID     = ms_flight-carrier_id
                                                ConnectionID  = ms_flight-connection_id
                                                FlightDate    = ms_flight-flight_date
                                                FlightPrice   = ms_flight-price
                                                CurrencyCode  = ms_flight-currency_code
                                                BookingStatus = 'N' ) ) ) )
      MAPPED DATA(mapped)
      FAILED DATA(failed)
      REPORTED DATA(reported).

    IF failed IS NOT INITIAL.
      print_failed( out = out failed = failed ).
      print_reported( out = out reported = reported ).
      ROLLBACK ENTITIES.
      RETURN.
    ENDIF.

    "커밋 범위(commit scope): BEGIN ~ END 사이에서만 CONVERT KEY 로 %pid -> 최종 키 변환 가능
    COMMIT ENTITIES BEGIN
      RESPONSE OF zrap_r_travel_###
        FAILED   DATA(failed_late)
        REPORTED DATA(reported_late).

    IF sy-subrc = 0.
      "CONVERT KEY : 저장 단계의 adjust_numbers 가 정한 최종 키를 %pid 로 조회
      "(정확한 문법 형태는 실제 시스템에서 확인 필요. 08 치트시트: CONVERT KEY OF some_bo FROM ...-%pid TO DATA(some_key))
      CONVERT KEY OF zrap_r_travel_###
        FROM mapped-travel[ 1 ]-%pid
        TO DATA(final_key).
      travel_id = final_key-TravelID.
    ELSE.
      print_reported_late( out = out reported = reported_late ).
    ENDIF.

    COMMIT ENTITIES END.
  ENDMETHOD.


  METHOD m04_commit.
    out->write( `=== 4단계: COMMIT ENTITIES ===` ).
    ROLLBACK ENTITIES.
    DATA(today) = cl_abap_context_info=>get_system_date( ).

    "(a) 짧은 형식 COMMIT ENTITIES
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel UPDATE FIELDS ( Description )
        WITH VALUE #( ( TravelID = mv_travel_id Description = |EML commit { today }| ) ).
    COMMIT ENTITIES.
    out->write( |(a) COMMIT ENTITIES sy-subrc = { sy-subrc }| ).

    "(b) 저장 단계 검증 실패 → RESPONSES (동적 형태 응답 표)
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        CREATE FIELDS ( CustomerID AgencyID BeginDate EndDate CurrencyCode Description )
        WITH VALUE #( ( %cid         = 'BAD'
                        CustomerID   = '999999'          "없는 고객 → validateCustomer
                        AgencyID     = mv_agency_id
                        BeginDate    = today + 20
                        EndDate      = today + 10        "종료 < 시작 → validateDates
                        CurrencyCode = 'EUR'
                        Description  = 'should fail' ) )
      FAILED DATA(failed_bad).
    out->write( |(b) MODIFY 단계 failed = { lines( failed_bad-travel ) }건 (검증은 아직 안 돌았음)| ).

    COMMIT ENTITIES RESPONSES FAILED DATA(resp_failed) REPORTED DATA(resp_reported).
    out->write( |(b) COMMIT sy-subrc = { sy-subrc }, 응답 표 failed { lines( resp_failed ) }줄 / reported { lines( resp_reported ) }줄| ).
    "sy-subrc = 4 : 이른 저장 단계(finalize/check_before_save)에서 실패 → 늦은 저장 단계로 가지 않고
    "상호작용 단계로 돌아옴. 버퍼에는 잘못된 인스턴스가 그대로 남아 있음.

    "(c) 긴 형식 RESPONSE OF : 엔터티별로 타입이 정해진 응답(LATE)
    COMMIT ENTITIES RESPONSE OF zrap_r_travel_###
      FAILED   DATA(failed_c)
      REPORTED DATA(reported_c).
    out->write( |(c) COMMIT sy-subrc = { sy-subrc }, failed Travel { lines( failed_c-travel ) }건| ).
    print_reported_late( out = out reported = reported_c ).
    "버퍼를 고치거나(UPDATE) 버려야(ROLLBACK) 다음 작업을 할 수 있음
    ROLLBACK ENTITIES.

    "(d) IN SIMULATION MODE : 이른 저장 단계만 실행, DB 저장(COMMIT WORK) 없음
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        CREATE FIELDS ( CustomerID AgencyID BeginDate EndDate CurrencyCode Description )
        WITH VALUE #( ( %cid         = 'SIM'
                        CustomerID   = mv_customer_id
                        AgencyID     = mv_agency_id
                        BeginDate    = today + 20
                        EndDate      = today + 25
                        CurrencyCode = 'EUR'
                        Description  = 'simulation only' ) ).
    COMMIT ENTITIES IN SIMULATION MODE.
    DATA(sim_subrc) = sy-subrc.
    SELECT COUNT(*) FROM zrap_atrav_### WHERE description = 'simulation only' INTO @DATA(sim_count).
    out->write( |(d) 시뮬레이션 sy-subrc = { sim_subrc }, DB 건수 = { sim_count } (0 이어야 함)| ).
    ROLLBACK ENTITIES.

    "(e) 커밋 범위 + CONVERT KEY 로 최종 키 얻기
    DATA(new_id) = create_travel_and_commit( out ).
    IF new_id IS INITIAL.
      out->write( `(e) 저장 실패` ).
      RETURN.
    ENDIF.
    SELECT SINGLE FROM zrap_atrav_### FIELDS travel_id, total_price, currency_code, overall_status
      WHERE travel_id = @new_id
      INTO @DATA(saved).
    out->write( |(e) 최종 TravelID = { new_id }, DB: 합계 { saved-total_price } { saved-currency_code } 상태 { saved-overall_status }| ).
  ENDMETHOD.
```

콘솔 출력 예시

```
=== 4단계: COMMIT ENTITIES ===
(a) COMMIT ENTITIES sy-subrc = 0
(b) MODIFY 단계 failed = 0건 (검증은 아직 안 돌았음)
(b) COMMIT sy-subrc = 4, 응답 표 failed 1줄 / reported 1줄
(c) COMMIT sy-subrc = 4, failed Travel 1건
  E (save) Travel : Customer 999999 does not exist.
  E (save) Travel : Begin date 20261106 must not be after end date 20261027.
(d) 시뮬레이션 sy-subrc = 0, DB 건수 = 0 (0 이어야 함)
(e) 최종 TravelID = 00000123, DB: 합계 615.00 EUR 상태 O
```

**왜 이렇게 쓰나**
- `on save` 검증은 `COMMIT ENTITIES`가 시작한 저장 순서의 `check_before_save` 시점에 돕니다. 그래서 MODIFY는 성공하고 COMMIT에서 `sy-subrc = 4`가 됩니다. 이른 저장 단계에서 실패하면 늦은 저장 단계(adjust_numbers, save)로 가지 않고 상호작용 단계로 돌아옵니다. 이때 버퍼를 고치거나 `ROLLBACK ENTITIES`로 버려야 합니다.
- `RESPONSES`(동적 형태)는 `abp_behv_response_tab` 타입으로 여러 BO의 응답을 한꺼번에 받고, `RESPONSE OF bdef`(긴 형식)는 BO마다 타입이 정해진 `failed`/`reported`(LATE)를 받습니다. 메시지를 읽으려면 긴 형식이 편합니다.
- `COMMIT ENTITIES`는 `COMMIT WORK`를 포함하지만, 저장 순서 오류 시 런타임 오류 대신 `sy-subrc`로 돌려주고 응답을 받을 수 있다는 점이 다릅니다. 콘솔에서는 항상 `COMMIT ENTITIES`를 쓰세요.
- late numbering의 최종 키는 `adjust_numbers` 이후에야 생기므로, 소비자가 그 키를 알려면 커밋 범위(`COMMIT ENTITIES BEGIN ... END`) 안에서 `CONVERT KEY`로 물어봐야 합니다. `END` 뒤에는 변환할 수 없습니다.

**자주 나는 오류와 해결**
- `COMMIT ENTITIES`는 행동 풀(핸들러·세이버) 안에서 쓸 수 없습니다. 콘솔·테스트 클래스·일반 소비자 클래스에서만 씁니다.
- `CONVERT KEY` 문법 오류가 나면 키 소스로 `%pid` 대신 임시 키 그룹(`%pre` 또는 `%pid`+`%tmp`)을 요구하는 형태일 수 있습니다. ADT에서 `CONVERT KEY`에 F1을 눌러 현재 릴리스 문법을 확인하세요(실제 시스템에서 확인 필요).

</details>

#### 5단계. 액션과 함수 실행: %param, RESULT, 팩토리, 정적 액션, 기능 제어

요구사항
1. 메서드 `m05_actions`를 추가하세요. 4단계의 `create_travel_and_commit`으로 새 Travel 하나를 만들어 시작합니다.
2. **결과가 있는 인스턴스 액션**: `acceptTravel`을 실행하고 `RESULT`의 `%param-OverallStatus`와 `reported`의 성공 메시지(R-02의 `Travel &1 has been accepted.`)를 출력하세요.
3. **기능 제어로 막힌 액션**: 같은 Travel에 `acceptTravel`을 한 번 더 실행해 `failed-travel`의 `%fail-cause`(`disabled` 예상)와 `%action-acceptTravel` 플래그를 출력하세요.
4. **파라미터가 있는 액션**: 다른 Travel(상태 O인 샘플)에 `deductDiscount`를 `%param-discount_percent = 150`(오류)과 `= 10`(정상)으로 각각 실행하세요. 오류는 메시지 `Enter a discount between 1 and 100 percent.`가, 정상은 줄어든 `BookingFee`가 결과로 나와야 합니다.
5. **팩토리 액션**: `copyTravel`을 `%cid = 'COPY1'`로 실행하고 `mapped-travel`에서 새 인스턴스의 `%cid`, `%pid`를 출력하세요. 같은 요청에서 `%cid_ref = 'COPY1'`로 복사본 설명을 바꾸세요.
6. **정적 기본 팩토리 액션**: `createTravel`을 `%cid = 'STATIC1'`, `%param`(고객·여행사·항공편)으로 실행해 새 Travel + Booking이 생기는지 `mapped`로 확인하세요.
7. **반복 가능 액션**: `addServiceFee`를 같은 Travel에 한 요청에서 두 번 실행하세요(`%cid = 'FEE1'`, `'FEE2'`).
8. **인스턴스 함수**: Booking의 `getDaysToFlight`를 `READ ENTITIES ... ENTITY Booking EXECUTE getDaysToFlight FROM ... RESULT`로 호출해 `%param`의 세 값을 출력하세요.
9. **정적 함수**: `getOpenTravelCount`를 호출해 상태별 건수를 출력하세요.
10. 액션 실행분 중 2·5·6·7번은 `COMMIT ENTITIES RESPONSE OF`로 저장하고, 4번(할인)은 `ROLLBACK ENTITIES`로 버려 샘플 데이터를 보존하세요(순서 주의: 4번을 먼저 하고 롤백, 그다음 나머지).

**확인** 콘솔에 `acceptTravel` 결과 상태 `A`, 두 번째 실행의 `disabled`, 할인 오류 메시지, 복사본·정적 생성 `mapped`, `getDaysToFlight` 값, 상태별 건수가 나와야 합니다. Fiori Preview에서 복사본과 `createTravel`로 만든 Travel이 보여야 합니다.

<details><summary>정답·해설</summary>

정의부에 추가:

```abap
    METHODS m05_actions IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
```

구현부에 추가:

```abap
  METHOD m05_actions.
    out->write( `=== 5단계: 액션과 함수 ===` ).
    ROLLBACK ENTITIES.

    "------------------------------------------------------------------
    "(4) 파라미터가 있는 액션 - 먼저 실행하고 롤백 (샘플 보존)
    "------------------------------------------------------------------
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        EXECUTE deductDiscount
          FROM VALUE #( ( %cid_ref = '' TravelID = mv_travel_id %param-discount_percent = 150 ) )
        RESULT DATA(disc_bad)
      FAILED DATA(disc_bad_failed)
      REPORTED DATA(disc_bad_reported).
    out->write( |deductDiscount(150%): 결과 { lines( disc_bad ) }건| ).
    print_failed( out = out failed = disc_bad_failed ).
    print_reported( out = out reported = disc_bad_reported ).

    READ ENTITIES OF zrap_r_travel_###
      ENTITY Travel FIELDS ( BookingFee ) WITH VALUE #( ( TravelID = mv_travel_id ) )
      RESULT DATA(fee_before).

    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        EXECUTE deductDiscount
          FROM VALUE #( ( TravelID = mv_travel_id %param-discount_percent = 10 ) )
        RESULT DATA(disc_ok).
    IF disc_ok IS NOT INITIAL.
      "result [1] $self : %param 에 액션 후 인스턴스 전체가 들어옴
      out->write( |deductDiscount(10%): 수수료 { fee_before[ 1 ]-BookingFee } -> { disc_ok[ 1 ]-%param-BookingFee }| ).
    ENDIF.
    ROLLBACK ENTITIES.   "할인은 저장하지 않음

    "------------------------------------------------------------------
    "(2)(3) 결과가 있는 액션 + 기능 제어
    "------------------------------------------------------------------
    DATA(new_id) = create_travel_and_commit( out = out description = 'for actions' ).
    CHECK new_id IS NOT INITIAL.

    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        EXECUTE acceptTravel FROM VALUE #( ( TravelID = new_id ) )
        RESULT DATA(accept_result)
      FAILED DATA(accept_failed)
      REPORTED DATA(accept_reported).
    out->write( |acceptTravel: 결과 상태 = { accept_result[ 1 ]-%param-OverallStatus }| ).
    print_reported( out = out reported = accept_reported ).

    "같은 트랜잭션에서 다시 실행 → get_instance_features 가 acceptTravel 을 disabled 로 돌려줌
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        EXECUTE acceptTravel FROM VALUE #( ( TravelID = new_id ) )
      FAILED DATA(accept2_failed)
      REPORTED DATA(accept2_reported).
    LOOP AT accept2_failed-travel INTO DATA(af).
      out->write( |acceptTravel 재실행: cause={ COND string( WHEN af-%fail-cause = if_abap_behv=>cause-disabled THEN `disabled`
                                                               ELSE |{ af-%fail-cause }| ) } | &&
                  |%action-acceptTravel={ af-%action-acceptTravel }| ).
    ENDLOOP.
    print_reported( out = out reported = accept2_reported ).

    "------------------------------------------------------------------
    "(5) 팩토리 액션 copyTravel [1] : %cid 로 새 인스턴스 식별, 같은 요청에서 %cid_ref 사용
    "------------------------------------------------------------------
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        EXECUTE copyTravel
          FROM VALUE #( ( %cid = 'COPY1' TravelID = new_id ) )
        UPDATE FIELDS ( Description )
          WITH VALUE #( ( %cid_ref = 'COPY1' Description = 'copy of travel' ) )
      MAPPED DATA(copy_mapped)
      FAILED DATA(copy_failed)
      REPORTED DATA(copy_reported).
    LOOP AT copy_mapped-travel INTO DATA(cm).
      out->write( |copyTravel: 새 인스턴스 %cid={ cm-%cid } %pid={ cm-%pid }| ).
    ENDLOOP.
    print_failed( out = out failed = copy_failed ).
    print_reported( out = out reported = copy_reported ).

    "------------------------------------------------------------------
    "(6) 정적 기본 팩토리 액션 createTravel : 인스턴스 키 없이 %cid + %param
    "------------------------------------------------------------------
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        EXECUTE createTravel
          FROM VALUE #( ( %cid   = 'STATIC1'
                          %param = VALUE #( customer_id   = mv_customer_id
                                            agency_id     = mv_agency_id
                                            carrier_id    = ms_flight-carrier_id
                                            connection_id = ms_flight-connection_id
                                            flight_date   = ms_flight-flight_date ) ) )
      MAPPED DATA(static_mapped)
      FAILED DATA(static_failed)
      REPORTED DATA(static_reported).
    out->write( |createTravel: mapped Travel { lines( static_mapped-travel ) }건, Booking { lines( static_mapped-booking ) }건| ).
    print_failed( out = out failed = static_failed ).
    print_reported( out = out reported = static_reported ).

    "------------------------------------------------------------------
    "(7) 반복 가능 액션 : 같은 인스턴스에 한 요청에서 여러 번 → %cid 로 구분
    "    (repeatable 액션 입력에 %cid 가 있는지는 실제 시스템에서 확인 필요)
    "------------------------------------------------------------------
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        EXECUTE addServiceFee
          FROM VALUE #( ( %cid = 'FEE1' TravelID = new_id )
                        ( %cid = 'FEE2' TravelID = new_id ) )
        RESULT DATA(fee_result)
      FAILED DATA(fee_failed).
    out->write( |addServiceFee x2: 결과 { lines( fee_result ) }건, 실패 { lines( fee_failed-travel ) }건| ).

    COMMIT ENTITIES RESPONSE OF zrap_r_travel_###
      FAILED   DATA(commit_failed)
      REPORTED DATA(commit_reported).
    out->write( |액션 결과 저장 sy-subrc = { sy-subrc }| ).
    print_reported_late( out = out reported = commit_reported ).

    "------------------------------------------------------------------
    "(8) 인스턴스 함수 : READ ENTITIES ... EXECUTE (함수는 읽기 연산)
    "------------------------------------------------------------------
    READ ENTITIES OF zrap_r_travel_###
      ENTITY Travel BY \_Booking
        FIELDS ( BookingID ) WITH VALUE #( ( TravelID = new_id ) )
        RESULT DATA(new_bookings).

    READ ENTITIES OF zrap_r_travel_###
      ENTITY Booking
        EXECUTE getDaysToFlight
          FROM VALUE #( FOR b IN new_bookings ( %tky = b-%tky ) )
        RESULT DATA(days_result)
      FAILED DATA(days_failed).
    LOOP AT days_result INTO DATA(d).
      out->write( |getDaysToFlight { d-TravelID }/{ d-BookingID }: 처음 { d-%param-initial_days_to_flight }일, | &&
                  |남은 { d-%param-remaining_days_to_flight }일, 지표 { d-%param-days_to_flight_indicator }| ).
    ENDLOOP.

    "------------------------------------------------------------------
    "(9) 정적 함수 : 키 없이 %cid 만 (정적 연산 입력 구성은 실제 시스템에서 확인 필요)
    "------------------------------------------------------------------
    READ ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        EXECUTE getOpenTravelCount FROM VALUE #( ( %cid = 'STAT' ) )
        RESULT DATA(stat_result).
    IF stat_result IS NOT INITIAL.
      out->write( |getOpenTravelCount: O={ stat_result[ 1 ]-%param-open_count } | &&
                  |A={ stat_result[ 1 ]-%param-accepted_count } X={ stat_result[ 1 ]-%param-rejected_count }| ).
    ENDIF.
  ENDMETHOD.
```

> 4번 첫 번째 호출의 `%cid_ref = ''`는 필요 없는 값입니다. 지워도 됩니다(인스턴스 액션은 키나 `%cid_ref` 중 하나로 대상을 지정).

콘솔 출력 예시

```
=== 5단계: 액션과 함수 ===
deductDiscount(150%): 결과 0건
  FAILED Travel 00000003 (draft=00, pid=...) cause=0 ... 
  E Travel 00000003: Enter a discount between 1 and 100 percent.
deductDiscount(10%): 수수료 50.00 -> 45.00
acceptTravel: 결과 상태 = A
  S Travel 00000124: Travel 00000124 has been accepted.
acceptTravel 재실행: cause=disabled %action-acceptTravel=01
copyTravel: 새 인스턴스 %cid=COPY1 %pid=...
createTravel: mapped Travel 1건, Booking 1건
addServiceFee x2: 결과 2건, 실패 0건
액션 결과 저장 sy-subrc = 0
getDaysToFlight 00000124/0010: 처음 35일, 남은 35일, 지표 ...
getOpenTravelCount: O=12 A=3 X=1
```

**왜 이렇게 쓰나**
- 액션은 변경 연산이므로 `MODIFY ... EXECUTE`, 함수는 읽기 연산이므로 `READ ... EXECUTE`입니다. 함수는 버퍼를 바꾸지 않으므로 잠금도 걸지 않습니다.
- `result [1] $self` 액션의 `RESULT`는 줄마다 `%tky`와 `%param`(=액션 후 인스턴스 전체)을 줍니다. UI는 이 결과로 화면을 새로 그립니다.
- 팩토리 액션은 "새 인스턴스를 만드는 액션"이라 입력에 `%cid`가 있고 응답이 `mapped`로 옵니다. 정적(static) 팩토리 액션은 기존 인스턴스 없이 `%cid`와 `%param`만으로 실행합니다. `default`가 붙으면 Fiori 목록의 "생성" 버튼이 이 액션으로 바뀝니다(EML 입장에서는 같은 정적 액션).
- 기능 제어(`features : instance`)로 막힌 액션은 `failed`에 `%fail-cause = disabled`와 `%action-이름 = mk-on`이 들어옵니다. EML 소비자도 UI와 똑같이 기능 제어를 받습니다. 행동 풀 안에서 `IN LOCAL MODE`를 쓰면 이 검사를 건너뜁니다(8단계).
- 할인 오류는 핸들러가 직접 `failed`/`reported`를 채운 경우입니다(R-02의 `ZCM_RAP_###=>discount_invalid`). 이런 "상호작용 단계 검사"는 MODIFY 직후 바로 보이고, `on save` 검증은 COMMIT 때 보인다는 차이를 4단계와 비교하세요.

**자주 나는 오류와 해결**
- 정적 함수/정적 액션 입력에 `%cid`가 없다는 문법 오류가 나면 해당 파생 타입을 F2로 열어 실제 컴포넌트를 확인하고 그에 맞게 고치세요.
- `getDaysToFlight`를 `ENTITY Travel`로 호출하면 "함수가 없다"는 오류가 납니다. 함수는 Booking에 정의되어 있습니다.

</details>

#### 6단계. draft EML: %is_draft와 Edit / Activate / Discard / Prepare / Resume

요구사항
1. 메서드 `m06_draft`를 추가하세요.
2. **draft 생성**: `%is_draft = if_abap_behv=>mk-on`으로 Travel을 만들고(필수 필드 `EndDate`는 일부러 비움) `COMMIT ENTITIES`로 draft 테이블에 저장하세요. `ZRAP_DTRAV_###`에 줄이 생겼는지 SELECT로 확인합니다(활성 테이블에는 없음).
3. **draft 읽기**: `mapped`의 `%pid`와 `%is_draft = mk-on`으로 읽어 설명을 출력하세요.
4. **Prepare**: draft에 `EXECUTE Prepare`를 실행해 `EndDate` 누락 오류(검증 `validateDates`)가 `reported`로 오는지 확인하세요.
5. draft를 `EndDate`를 채워 `UPDATE`(`%is_draft = mk-on`)한 뒤 다시 Prepare → 오류가 없어야 합니다.
6. **Activate**: `EXECUTE Activate AUTO FILL CID WITH ...`로 활성화하고, 커밋 범위에서 `CONVERT KEY`로 최종 TravelID를 얻으세요. draft 테이블에서 사라지고 활성 테이블에 생겼는지 확인합니다.
7. **Edit**: 활성 Travel에 `EXECUTE Edit`(`%param-preserve_changes = abap_true`)를 실행해 draft를 만들고, draft만 설명을 바꾼 뒤 활성/ draft를 각각 읽어 설명이 다름을 출력하세요. `COMMIT ENTITIES`로 draft를 저장합니다.
8. **Resume**: 같은 Travel에 `EXECUTE Resume`을 실행해 결과(성공 또는 failed)를 출력하세요. 언제 Resume이 필요한지 주석으로 설명합니다.
9. **Discard**: draft를 `EXECUTE Discard`로 버리고 `COMMIT ENTITIES`, draft 테이블에서 사라졌는지 확인하세요.

**확인** 단계별로 draft 테이블/활성 테이블의 건수 변화가 콘솔에 나와야 합니다: 생성 후(draft 1, 활성 0) → 활성화 후(draft 0, 활성 1) → Edit 후(draft 1, 활성 1, 설명 다름) → Discard 후(draft 0, 활성 1).

<details><summary>정답·해설</summary>

정의부에 추가:

```abap
    METHODS m06_draft IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
```

구현부에 추가:

```abap
  METHOD m06_draft.
    out->write( `=== 6단계: draft EML ===` ).
    ROLLBACK ENTITIES.
    DATA(today) = cl_abap_context_info=>get_system_date( ).
    CONSTANTS c_desc TYPE /dmo/description VALUE 'EML draft demo'.

    "(1) draft 생성 : %is_draft = mk-on
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        CREATE FIELDS ( CustomerID AgencyID BeginDate CurrencyCode Description )
        WITH VALUE #( ( %cid         = 'DRAFT1'
                        %is_draft    = if_abap_behv=>mk-on
                        CustomerID   = mv_customer_id
                        AgencyID     = mv_agency_id
                        BeginDate    = today + 60
                        CurrencyCode = 'EUR'
                        Description  = c_desc ) )          "EndDate 는 일부러 비움
      MAPPED DATA(draft_mapped)
      FAILED DATA(draft_failed)
      REPORTED DATA(draft_reported).
    print_failed( out = out failed = draft_failed ).
    COMMIT ENTITIES.   "draft 인스턴스는 draft 테이블로 저장됨 (검증은 돌지 않음)

    SELECT COUNT(*) FROM zrap_dtrav_### WHERE description = @c_desc INTO @DATA(cnt_draft).
    SELECT COUNT(*) FROM zrap_atrav_### WHERE description = @c_desc INTO @DATA(cnt_active).
    out->write( |(1) draft 생성 후: draft { cnt_draft }, 활성 { cnt_active }| ).

    "(2) draft 읽기 : %pid + %is_draft
    READ ENTITIES OF zrap_r_travel_###
      ENTITY Travel FIELDS ( Description EndDate ) WITH CORRESPONDING #( draft_mapped-travel )
      RESULT DATA(draft_read).
    out->write( |(2) draft 읽기: 설명="{ draft_read[ 1 ]-Description }" EndDate="{ draft_read[ 1 ]-EndDate }" draft={ draft_read[ 1 ]-%is_draft }| ).

    "(3) Prepare : draft 결정 액션 → BDEF 의 draft determine action Prepare { validation ...; } 실행
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        EXECUTE Prepare FROM CORRESPONDING #( draft_mapped-travel )
      FAILED DATA(prep_failed)
      REPORTED DATA(prep_reported).
    out->write( |(3) Prepare: 실패 { lines( prep_failed-travel ) }건| ).
    print_reported( out = out reported = prep_reported ).

    "(4) draft 수정 후 다시 Prepare
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        UPDATE FIELDS ( EndDate )
          WITH VALUE #( FOR m IN draft_mapped-travel
                        ( %tky = m-%tky EndDate = today + 65 ) )   "m-%tky 에 %is_draft = mk-on 포함
        EXECUTE Prepare FROM CORRESPONDING #( draft_mapped-travel )
      FAILED DATA(prep2_failed)
      REPORTED DATA(prep2_reported).
    out->write( |(4) 수정 후 Prepare: 실패 { lines( prep2_failed-travel ) }건| ).

    "(5) Activate : draft → 활성. 새 활성 인스턴스가 생기므로 %cid 필요 (AUTO FILL CID)
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        EXECUTE Activate AUTO FILL CID WITH CORRESPONDING #( draft_mapped-travel )
      MAPPED DATA(act_mapped)
      FAILED DATA(act_failed)
      REPORTED DATA(act_reported).
    print_failed( out = out failed = act_failed ).
    print_reported( out = out reported = act_reported ).

    DATA active_id TYPE /dmo/travel_id.
    COMMIT ENTITIES BEGIN
      RESPONSE OF zrap_r_travel_### FAILED DATA(act_failed_late) REPORTED DATA(act_reported_late).
    IF sy-subrc = 0 AND act_mapped-travel IS NOT INITIAL.
      "활성화로 생긴 활성 인스턴스의 %pid → 최종 키 (문법 형태는 실제 시스템에서 확인 필요)
      CONVERT KEY OF zrap_r_travel_### FROM act_mapped-travel[ 1 ]-%pid TO DATA(act_key).
      active_id = act_key-TravelID.
    ELSE.
      print_reported_late( out = out reported = act_reported_late ).
    ENDIF.
    COMMIT ENTITIES END.

    SELECT COUNT(*) FROM zrap_dtrav_### WHERE description = @c_desc INTO @cnt_draft.
    SELECT COUNT(*) FROM zrap_atrav_### WHERE description = @c_desc INTO @cnt_active.
    out->write( |(5) Activate 후: TravelID { active_id }, draft { cnt_draft }, 활성 { cnt_active }| ).
    CHECK active_id IS NOT INITIAL.

    "(6) Edit : 활성 → draft 복사본 생성 + 배타적 잠금
    "    %param-preserve_changes = abap_true : 이미 draft 가 있으면 덮어쓰지 않고 실패
    "    (Edit 입력의 %param 구성은 실제 시스템에서 확인 필요)
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        EXECUTE Edit FROM VALUE #( ( TravelID = active_id %param-preserve_changes = abap_true ) )
      MAPPED DATA(edit_mapped)
      FAILED DATA(edit_failed)
      REPORTED DATA(edit_reported).
    print_failed( out = out failed = edit_failed ).

    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        UPDATE FIELDS ( Description )
          WITH VALUE #( ( %is_draft = if_abap_behv=>mk-on TravelID = active_id Description = 'changed only in draft' ) ).

    READ ENTITIES OF zrap_r_travel_###
      ENTITY Travel FIELDS ( Description )
        WITH VALUE #( ( %is_draft = if_abap_behv=>mk-off TravelID = active_id )
                      ( %is_draft = if_abap_behv=>mk-on  TravelID = active_id ) )
      RESULT DATA(both).
    LOOP AT both INTO DATA(bt).
      out->write( |(6) { COND string( WHEN bt-%is_draft = if_abap_behv=>mk-on THEN `draft` ELSE `활성` ) }: "{ bt-Description }"| ).
    ENDLOOP.
    COMMIT ENTITIES.   "draft 변경 저장 (활성은 그대로)

    "(7) Resume : draft 는 있는데 배타적 잠금이 끊긴 경우(세션 종료·잠금 만료 후 다시 편집) 잠금을 다시 얻음.
    "    같은 세션에서 바로 부르면 이미 잠금이 있어 그냥 성공하거나, 구현에 따라 실패할 수 있음.
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        EXECUTE Resume FROM VALUE #( ( TravelID = active_id ) )
      FAILED DATA(resume_failed)
      REPORTED DATA(resume_reported).
    out->write( |(7) Resume: 실패 { lines( resume_failed-travel ) }건| ).
    print_reported( out = out reported = resume_reported ).

    "(8) Discard : draft 버리기 (활성은 그대로)
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        EXECUTE Discard FROM VALUE #( ( TravelID = active_id ) )
      FAILED DATA(discard_failed).
    COMMIT ENTITIES.
    SELECT COUNT(*) FROM zrap_dtrav_### WHERE travelid = @active_id INTO @cnt_draft.
    out->write( |(8) Discard 후: draft { cnt_draft }건, 실패 { lines( discard_failed-travel ) }건| ).
  ENDMETHOD.
```

> draft 테이블 필드명은 규격대로 CDS 별칭과 같게(`TRAVELID`, `DESCRIPTION`) 만들었다고 가정합니다. draft 액션(`Prepare`, `Activate`, `Discard`, `Resume`, `Edit`) 입력 타입의 키 구성은 `CORRESPONDING #( mapped-travel )`처럼 이름 매칭으로 넘기면 안전합니다. 키 필드만 쓴 `VALUE #( ( TravelID = ... ) )` 형태에서 문법 오류가 나면 F2로 입력 타입을 보고 `%key-`/`%pky-` 형태로 바꾸세요.

콘솔 출력 예시

```
=== 6단계: draft EML ===
(1) draft 생성 후: draft 1, 활성 0
(2) draft 읽기: 설명="EML draft demo" EndDate="00000000" draft=01
(3) Prepare: 실패 1건
  (state area 지우기: VALIDATE_DATES) Travel 
  E Travel : Enter a begin date and an end date. [필드 BeginDate]
(4) 수정 후 Prepare: 실패 0건
(5) Activate 후: TravelID 00000126, draft 0, 활성 1
(6) 활성: "EML draft demo"
(6) draft: "changed only in draft"
(7) Resume: 실패 0건
(8) Discard 후: draft 0건, 실패 0건
```

**왜 이렇게 쓰나**
- draft BO의 모든 인스턴스는 `%is_draft`로 활성/draft를 구분합니다. 지정하지 않으면 활성(`mk-off`)입니다. draft 인스턴스를 `COMMIT ENTITIES`하면 draft 테이블에만 저장되고 `on save` 검증·`adjust_numbers`는 돌지 않습니다. 그래서 필수 필드가 비어 있어도 저장됩니다.
- `Prepare`는 BDEF의 `draft determine action Prepare { validation ...; }`에 적은 검증을 draft에 대해 미리 실행합니다. Fiori의 "저장" 버튼은 `Prepare` → `Activate` 순서로 부릅니다.
- `Activate`는 draft를 활성 인스턴스로 옮기고 draft를 지웁니다. late numbering이라 활성 인스턴스의 최종 번호는 이 커밋의 `adjust_numbers`에서 정해지므로 다시 `CONVERT KEY`가 필요합니다.
- `Edit`은 활성 인스턴스의 draft 복사본을 만들고 배타적 잠금을 겁니다. `preserve_changes = abap_true`이면 이미 draft가 있을 때 덮어쓰지 않습니다. `Resume`은 잠금이 끊긴 기존 draft를 다시 편집 상태로 만들 때, `Discard`는 draft를 버릴 때 씁니다. R-02의 Resume은 `with additional implementation`이라 핸들러의 `Resume` 메서드도 같이 실행됩니다.

**자주 나는 오류와 해결**
- draft가 있는 Travel을 활성 인스턴스로 바로 UPDATE하면 `failed`(`locked`)가 납니다. draft를 통해 바꾸거나 먼저 Discard하세요.
- Activate에서 `%cid`가 없다는 오류가 나면 `AUTO FILL CID`를 빠뜨린 것입니다(08 치트시트 draft 예제도 `EXECUTE activate AUTO FILL CID WITH ...`).

</details>

#### 7단계. SET LOCKS와 GET PERMISSIONS

요구사항
1. 메서드 `m07_locks_permissions`를 추가하세요.
2. **SET LOCKS 세 형식**:
   - 짧은 형식 `SET LOCKS ENTITY zrap_r_travel_### FROM ... FAILED ...`로 샘플 Travel 잠금
   - 긴 형식 `SET LOCKS OF zrap_r_travel_### ENTITY Travel FROM ... ENTITY Booking FROM ... FAILED ... REPORTED ...`
   - 동적 형식 `SET LOCKS locks_tab FAILED ... REPORTED ...` (`abp_behv_locks_tab`)
   각 결과의 실패 건수를 출력하고, Booking은 `lock dependent`라 잠그면 실제로 무엇이 잠기는지 주석으로 적으세요.
3. **GET PERMISSIONS ONLY GLOBAL**: `TYPE STRUCTURE FOR PERMISSIONS REQUEST`에 `%create`, `%update`, `%delete`, `%action-acceptTravel`을 켜고 짧은 형식으로 전역 권한/전역 기능 제어를 받으세요.
4. **GET PERMISSIONS ONLY INSTANCE**: 상태 O인 샘플 Travel과 5단계에서 승인한 Travel(상태 A) 두 건에 대해 `%update`, `%delete`, `%action-acceptTravel`, `%action-rejectTravel`, `%field-BookingFee`, `%assoc-_Booking`을 요청하세요. 결과의 `instances` 표를 읽어 값이 `if_abap_behv=>perm-o-enabled`/`perm-o-disabled`, 필드는 `perm-f-...` 중 무엇인지 사람이 읽을 문장으로 출력합니다.
5. 마지막에 `ROLLBACK ENTITIES`로 잠금을 푸세요.

**확인** 같은 사용자의 같은 세션이므로 잠금 실패 0건, 상태 A Travel의 `acceptTravel`은 disabled, 상태 O는 enabled로 출력되어야 합니다.

<details><summary>정답·해설</summary>

정의부에 추가:

```abap
    METHODS m07_locks_permissions IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
```

구현부에 추가:

```abap
  METHOD m07_locks_permissions.
    out->write( `=== 7단계: SET LOCKS / GET PERMISSIONS ===` ).
    ROLLBACK ENTITIES.

    "------------------------------------------------------------------
    " SET LOCKS
    "------------------------------------------------------------------
    "짧은 형식 : 엔터티 하나
    SET LOCKS ENTITY zrap_r_travel_###
      FROM VALUE #( ( TravelID = mv_travel_id ) )
      FAILED DATA(lock_failed_short).
    out->write( |SET LOCKS(짧은): 실패 { lines( lock_failed_short-travel ) }건| ).

    "긴 형식 : 구성 트리의 여러 엔터티
    "Booking 은 lock dependent by _Travel → 실제 잠금은 lock master 인 부모 Travel 에 걸림
    SET LOCKS OF zrap_r_travel_###
      ENTITY Travel  FROM VALUE #( ( TravelID = mv_travel_id ) )
      ENTITY Booking FROM VALUE #( ( TravelID  = ms_booking_key-travel_id
                                     BookingID = ms_booking_key-booking_id ) )
      FAILED   DATA(lock_failed_long)
      REPORTED DATA(lock_reported_long).
    out->write( |SET LOCKS(긴): 실패 Travel { lines( lock_failed_long-travel ) } / Booking { lines( lock_failed_long-booking ) }| ).

    "동적 형식 : 엔터티 이름(대문자) + TYPE TABLE FOR KEY OF 참조
    DATA travel_keys TYPE TABLE FOR KEY OF zrap_r_travel_###.
    travel_keys = VALUE #( ( TravelID = mv_travel_id ) ).
    DATA(locks_tab) = VALUE abp_behv_locks_tab(
      ( entity_name = 'ZRAP_R_TRAVEL_###' instances = REF #( travel_keys ) ) ).
    SET LOCKS locks_tab
      FAILED   DATA(lock_failed_dyn)
      REPORTED DATA(lock_reported_dyn).
    out->write( |SET LOCKS(동적): 실패 응답 줄 { lines( lock_failed_dyn ) }| ).

    "------------------------------------------------------------------
    " GET PERMISSIONS ONLY GLOBAL : 전역 권한 + 전역/정적 기능 제어
    "------------------------------------------------------------------
    DATA request TYPE STRUCTURE FOR PERMISSIONS REQUEST zrap_r_travel_###.
    request = VALUE #( %create              = if_abap_behv=>mk-on
                       %update              = if_abap_behv=>mk-on
                       %delete              = if_abap_behv=>mk-on
                       %action-acceptTravel = if_abap_behv=>mk-on ).

    GET PERMISSIONS ONLY GLOBAL ENTITY zrap_r_travel_###
      REQUEST request
      RESULT DATA(perm_global)
      FAILED DATA(perm_global_failed)
      REPORTED DATA(perm_global_reported).
    out->write( |GLOBAL: create={ perm_global-global-%create } update={ perm_global-global-%update } | &&
                |delete={ perm_global-global-%delete } (perm-o-enabled={ if_abap_behv=>perm-o-enabled }, | &&
                |perm-o-disabled={ if_abap_behv=>perm-o-disabled })| ).

    "------------------------------------------------------------------
    " GET PERMISSIONS ONLY INSTANCE : 인스턴스 권한 + 인스턴스 기능 제어
    "------------------------------------------------------------------
    SELECT SINGLE FROM zrap_atrav_### FIELDS travel_id WHERE overall_status = 'A' INTO @DATA(accepted_id).

    DATA perm_keys TYPE TABLE FOR PERMISSIONS KEY zrap_r_travel_###.
    perm_keys = VALUE #( ( TravelID = mv_travel_id )
                         ( TravelID = accepted_id ) ).

    request = VALUE #( %update              = if_abap_behv=>mk-on
                       %delete              = if_abap_behv=>mk-on
                       %action-acceptTravel = if_abap_behv=>mk-on
                       %action-rejectTravel = if_abap_behv=>mk-on
                       %field-BookingFee    = if_abap_behv=>mk-on
                       %assoc-_Booking      = if_abap_behv=>mk-on ).

    "긴 형식: OF bdef ENTITY ... FROM keys (rf /DMO/TC_TRAVEL_M_BO_CONSUMER 와 같은 형태)
    GET PERMISSIONS ONLY INSTANCE OF zrap_r_travel_###
      ENTITY Travel
      FROM perm_keys
      REQUEST request
      RESULT DATA(perm_inst)
      FAILED DATA(perm_inst_failed)
      REPORTED DATA(perm_inst_reported).

    LOOP AT perm_inst-instances INTO DATA(pi).
      out->write( |INSTANCE { pi-TravelID }: | &&
                  |acceptTravel { COND string( WHEN pi-%action-acceptTravel = if_abap_behv=>perm-o-disabled THEN `불가` ELSE `가능` ) }, | &&
                  |rejectTravel { COND string( WHEN pi-%action-rejectTravel = if_abap_behv=>perm-o-disabled THEN `불가` ELSE `가능` ) }, | &&
                  |update { COND string( WHEN pi-%update = if_abap_behv=>perm-o-disabled THEN `불가` ELSE `가능` ) }, | &&
                  |BookingFee { COND string( WHEN pi-%field-BookingFee = if_abap_behv=>perm-f-read_only THEN `읽기 전용` ELSE `편집 가능` ) }, | &&
                  |Booking 생성 { COND string( WHEN pi-%assoc-_Booking = if_abap_behv=>perm-o-disabled THEN `불가` ELSE `가능` ) }| ).
    ENDLOOP.
    print_failed( out = out failed = perm_inst_failed ).

    ROLLBACK ENTITIES.   "잠금 해제
  ENDMETHOD.
```

> `if_abap_behv=>perm-f-read_only`의 정확한 상수 이름은 F2로 `if_abap_behv=>perm-f`를 열어 확인하세요(08 치트시트 표에는 구조 상수 `PERM-F`, `PERM-O`만 나옴). `GET PERMISSIONS ONLY GLOBAL` 결과 구조의 `global` 컴포넌트와 `ONLY INSTANCE` 결과의 `instances` 컴포넌트는 rf의 `/DMO/TC_BOTD_TRAVEL_M_DEMOS`에 나오는 형태(`global-%create`, `instances = VALUE #( ( %key-... %update ... ) )`)를 따랐습니다.

콘솔 출력 예시

```
=== 7단계: SET LOCKS / GET PERMISSIONS ===
SET LOCKS(짧은): 실패 0건
SET LOCKS(긴): 실패 Travel 0 / Booking 0
SET LOCKS(동적): 실패 응답 줄 0
GLOBAL: create=00 update=00 delete=00 (perm-o-enabled=00, perm-o-disabled=01)
INSTANCE 00000003: acceptTravel 가능, rejectTravel 가능, update 가능, BookingFee 편집 가능, Booking 생성 가능
INSTANCE 00000124: acceptTravel 불가, rejectTravel 가능, update 가능, BookingFee 읽기 전용, Booking 생성 가능
```

(실제 enabled/disabled 조합은 R-03의 `get_instance_features` 규칙을 따릅니다.)

**왜 이렇게 쓰나**
- 관리형 BO는 UPDATE·액션 전에 프레임워크가 자동으로 잠그므로 보통 `SET LOCKS`가 필요 없습니다. 여러 단계로 나뉜 처리 중간에 남이 바꾸지 못하게 미리 잡아 둘 때 씁니다. 잠금은 트랜잭션이 끝날 때(COMMIT/ROLLBACK) 풀립니다.
- 자식 엔터티를 잠가도 실제 enqueue는 `lock master`(Travel)에 걸립니다. 그래서 Booking 하나를 잠그면 같은 Travel의 다른 Booking도 남이 바꿀 수 없습니다.
- `GET PERMISSIONS`는 실제로 연산을 실행하지 않고 "할 수 있는지"만 묻습니다. Fiori가 버튼을 회색으로 만들 때 쓰는 정보와 같습니다. `ONLY GLOBAL`은 전역 권한·전역/정적 기능 제어, `ONLY INSTANCE`는 인스턴스 권한·인스턴스 기능 제어만 묻고, `ONLY` 없이 쓰면 모두 합친 결과를 줍니다.

</details>

#### 8단계. 계층별 EML: 기본 BO, 인터페이스 BO, 프로젝션 BO, PRIVILEGED, IN LOCAL MODE, AUGMENTING

요구사항
1. 메서드 `m08_layers`를 추가하세요.
2. 같은 Travel을 세 계층에서 각각 읽으세요: `READ ENTITIES OF zrap_r_travel_###`, `OF zrap_i_travel_###`, `OF zrap_c_travel_###`. 세 결과의 `Description`이 같은지 출력합니다.
3. 인터페이스 BO로 `acceptTravel`을 실행하세요(상태 O 샘플이 아니라 4단계 방식으로 새로 만든 Travel 사용). 인터페이스 BDEF에 `use action`이 없는 연산(예: 내부 액션 `reCalcTotalPrice`)을 인터페이스로 실행하면 어떻게 되는지 주석으로 적으세요.
4. **PRIVILEGED**: `MODIFY ENTITIES OF zrap_i_travel_### PRIVILEGED ENTITY Travel ...`로 `rejectTravel`을 실행하세요. 인증 컨텍스트 `NoCheckWhenPrivileged`(권한 객체 `/DMO/TRVL`)가 꺼진다는 것이 무슨 뜻인지 주석으로 설명합니다.
5. `IN LOCAL MODE`를 콘솔에 써 보고(주석 처리로 남김) 왜 안 되는지 적으세요.
6. `MODIFY AUGMENTING ENTITY`가 어디에서만 쓰이는지, 이 문제의 BO에 적용한다면 어떤 코드가 되는지 예시를 주석으로 쓰세요(실행하지 않음).
7. 끝에 `COMMIT ENTITIES`로 저장합니다.

**확인** 세 계층의 설명이 같고, 인터페이스로 실행한 `acceptTravel`/`rejectTravel`이 DB 상태를 A/X로 바꿔야 합니다.

<details><summary>정답·해설</summary>

정의부에 추가:

```abap
    METHODS m08_layers IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
```

구현부에 추가:

```abap
  METHOD m08_layers.
    out->write( `=== 8단계: 계층별 EML ===` ).
    ROLLBACK ENTITIES.

    "(1) 같은 인스턴스를 세 계층에서 읽기
    READ ENTITIES OF zrap_r_travel_###
      ENTITY Travel FIELDS ( Description ) WITH VALUE #( ( TravelID = mv_travel_id ) )
      RESULT DATA(r_layer).
    READ ENTITIES OF zrap_i_travel_###          "인터페이스 BO: 안정적인 소비 계약(transactional_interface)
      ENTITY Travel FIELDS ( Description ) WITH VALUE #( ( TravelID = mv_travel_id ) )
      RESULT DATA(i_layer).
    READ ENTITIES OF zrap_c_travel_###          "프로젝션 BO: 서비스(UI)용 계층
      ENTITY Travel FIELDS ( Description ) WITH VALUE #( ( TravelID = mv_travel_id ) )
      RESULT DATA(c_layer).
    out->write( |R="{ r_layer[ 1 ]-Description }" I="{ i_layer[ 1 ]-Description }" C="{ c_layer[ 1 ]-Description }"| ).

    "(2) 인터페이스 BO 로 액션 실행 (use action acceptTravel 이 있어야 함)
    DATA(id_accept) = create_travel_and_commit( out = out description = 'via interface' ).
    DATA(id_reject) = create_travel_and_commit( out = out description = 'via interface privileged' ).
    CHECK id_accept IS NOT INITIAL AND id_reject IS NOT INITIAL.

    MODIFY ENTITIES OF zrap_i_travel_###
      ENTITY Travel
        EXECUTE acceptTravel FROM VALUE #( ( TravelID = id_accept ) )
        RESULT DATA(i_accept_result)
      FAILED DATA(i_accept_failed).
    out->write( |인터페이스 acceptTravel: 상태 { VALUE #( i_accept_result[ 1 ]-%param-OverallStatus OPTIONAL ) }, 실패 { lines( i_accept_failed-travel ) }| ).

    "인터페이스 BDEF 에 use 로 노출하지 않은 연산은 인터페이스 이름으로 부를 수 없음 → 문법 오류
    "MODIFY ENTITIES OF zrap_i_travel_### ENTITY Travel EXECUTE reCalcTotalPrice FROM ...

    "(3) PRIVILEGED : BDEF 의 with privileged mode (disabling NoCheckWhenPrivileged)
    "    → 인증 컨텍스트 NoCheckWhenPrivileged 에 넣은 권한 객체(/DMO/TRVL)의 AUTHORITY-CHECK 를
    "      이 요청 동안 '항상 통과'로 취급. 기능 제어·검증은 그대로 적용됨.
    "    (PRIVILEGED 의 정확한 위치는 실제 시스템에서 확인 필요)
    MODIFY ENTITIES OF zrap_i_travel_### PRIVILEGED
      ENTITY Travel
        EXECUTE rejectTravel FROM VALUE #( ( TravelID = id_reject ) )
        RESULT DATA(i_reject_result)
      FAILED DATA(i_reject_failed)
      REPORTED DATA(i_reject_reported).
    out->write( |PRIVILEGED rejectTravel: 상태 { VALUE #( i_reject_result[ 1 ]-%param-OverallStatus OPTIONAL ) }, 실패 { lines( i_reject_failed-travel ) }| ).

    "(4) IN LOCAL MODE : 행동 풀(구현 클래스와 ABP 보조 클래스) 안에서만 허용 → 콘솔에서는 문법 오류
    "MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
    "  ENTITY Travel UPDATE FIELDS ( OverallStatus ) WITH VALUE #( ( TravelID = id_accept OverallStatus = 'O' ) ).
    "IN LOCAL MODE 는 기능 제어·권한·precheck 를 건너뛰므로, 외부 소비자에게 열면 BO 규칙을 우회하게 됨.

    "(5) AUGMENTING : 프로젝션 BO 의 행동 구현(프로젝션 BDEF 의 augment)에서만 사용, 응답 파라미터 없음.
    "    예) 프로젝션에서 들어온 Travel 생성 요청에 기본 설명을 보강
    "    METHOD augment_create.  (프로젝션 행동 풀 lhc_travel_c)
    "      MODIFY AUGMENTING ENTITY zrap_r_travel_###
    "        UPDATE FIELDS ( Description )
    "        WITH VALUE #( FOR e IN entities WHERE ( Description IS INITIAL )
    "                      ( %cid_ref = e-%cid  Description = 'created in UI' ) ).
    "    ENDMETHOD.
    "    요청에 없던 인스턴스를 추가할 때는 RELATING TO ... BY relates_tab(abp_behv_relating_tab) 사용.

    COMMIT ENTITIES RESPONSE OF zrap_r_travel_### FAILED DATA(c_failed) REPORTED DATA(c_reported).
    out->write( |저장 sy-subrc = { sy-subrc }| ).
    print_reported_late( out = out reported = c_reported ).

    SELECT FROM zrap_atrav_### FIELDS travel_id, overall_status
      WHERE travel_id IN ( @id_accept, @id_reject )
      INTO TABLE @DATA(final_status).
    LOOP AT final_status INTO DATA(fs).
      out->write( |DB { fs-travel_id }: 상태 { fs-overall_status }| ).
    ENDLOOP.
  ENDMETHOD.
```

> `augment_create` 예시는 개념 설명용입니다. 프로젝션 BDEF에 `augment` 정의가 없으면 이런 메서드는 만들 수 없습니다. `AUGMENTING`은 08 치트시트 "AUGMENTING Addition" 절에 나온 문법(`MODIFY AUGMENTING ENTITY some_bdef UPDATE FROM ...`, `RELATING TO ... BY relates_tab`)만 썼습니다.

콘솔 출력 예시

```
=== 8단계: 계층별 EML ===
R="EML commit 20261017" I="EML commit 20261017" C="EML commit 20261017"
인터페이스 acceptTravel: 상태 A, 실패 0
PRIVILEGED rejectTravel: 상태 X, 실패 0
저장 sy-subrc = 0
DB 00000127: 상태 A
DB 00000128: 상태 X
```

**왜 이렇게 쓰나**
- 세 계층 모두 같은 트랜잭션 버퍼(기본 BO)를 공유합니다. 계층마다 다른 것은 "무엇을 노출하는가"입니다. 프로젝션 BDEF와 인터페이스 BDEF는 `use create`, `use action ...`처럼 노출할 연산을 고르고, 노출하지 않은 연산·필드는 그 이름으로 부를 수 없습니다.
- 다른 BO·다른 소프트웨어 구성요소의 코드가 이 BO를 쓸 때는 인터페이스 BO(`ZRAP_I_TRAVEL_###`)를 쓰는 것이 원칙입니다. 기본 BO가 바뀌어도 인터페이스가 계약을 지켜 주고, C.1 릴리스 계약도 인터페이스 BO에 줍니다. 프로젝션 BO(C)는 특정 UI 서비스용이라 다른 코드가 쓰기에 적합하지 않습니다.
- `PRIVILEGED`는 BDEF 헤더의 `with privileged mode disabling 컨텍스트`와 짝입니다. 그 컨텍스트에 나열한 권한 객체의 검사만 꺼지고, 기능 제어·검증·잠금은 그대로입니다. 시스템 작업(예: 배치 승인)처럼 사용자 권한과 무관하게 실행해야 할 때 씁니다.
- `IN LOCAL MODE`는 BO 자신의 구현 안에서 "내 규칙은 내가 우회한다"는 뜻이라 소비자는 쓸 수 없고, `PRIVILEGED`는 소비자가 "권한만 우회해 달라"고 요청하는 것이라 BDEF가 허용해야만 쓸 수 있습니다.

**자주 나는 오류와 해결**
- `PRIVILEGED`를 썼는데 BDEF가 privileged mode를 허용하지 않으면 문법 오류가 납니다. 인터페이스 BDEF에 `with privileged mode;`, 기본 BDEF에 `with privileged mode disabling ...;`가 있는지 확인하세요(R-03).

</details>

#### 9단계. 동적 EML: READ/MODIFY ENTITIES OPERATIONS와 런타임 타입

요구사항
1. 메서드 `m09_dynamic`을 추가하세요.
2. **동적 READ**: `abp_behv_retrievals_tab` 하나에 (a) Travel 읽기(`op = if_abap_behv=>op-r-read`) (b) Travel → Booking 연관 읽기(`op-r-read_ba`, `sub_name = '_BOOKING'`, `links` 포함)를 넣어 `READ ENTITIES OPERATIONS`로 한 번에 실행하세요. 입력 표의 `%control`은 직접 채웁니다.
3. **동적 MODIFY**: `abp_behv_changes_tab`에 (a) Travel 생성(`op-m-create`) (b) 생성한 Travel에 Booking 생성(`op-m-create_ba`, `sub_name = '_BOOKING'`) (c) 샘플 Travel 설명 수정(`op-m-update`)을 넣고 `MODIFY ENTITIES OPERATIONS`로 실행하세요. `MAPPED`를 받아 출력하고 `ROLLBACK ENTITIES`로 버립니다.
4. **런타임 BDEF 파생 타입**: 엔터티 이름 문자열만으로 `cl_abap_tabledescr=>get_bdef_derived_type( p_entity = ... p_kind = abp_bdef_derived_type-create )`를 써서 `TYPE TABLE FOR CREATE`와 같은 표를 `CREATE DATA ... TYPE HANDLE`로 만들고, 정적 타입과 호환되는지 `applies_to_data`로 확인하세요.
5. 동적 형식을 언제 쓰는지 주석으로 정리하세요.

**확인** 동적 READ 결과 건수가 2단계의 결과와 같고, 동적 MODIFY의 `mapped`에 Travel 1건 + Booking 1건이 나오며, `applies_to_data` 결과가 `X`여야 합니다.

<details><summary>정답·해설</summary>

정의부에 추가:

```abap
    METHODS m09_dynamic IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
```

구현부에 추가:

```abap
  METHOD m09_dynamic.
    out->write( `=== 9단계: 동적 EML ===` ).
    ROLLBACK ENTITIES.

    "------------------------------------------------------------------
    " 동적 READ : READ ENTITIES OPERATIONS
    "------------------------------------------------------------------
    DATA: op_read      TYPE abp_behv_retrievals_tab,
          read_in      TYPE TABLE FOR READ IMPORT zrap_r_travel_###,
          read_out     TYPE TABLE FOR READ RESULT zrap_r_travel_###,
          rba_in       TYPE TABLE FOR READ IMPORT zrap_r_travel_###\_Booking,
          rba_out      TYPE TABLE FOR READ RESULT zrap_r_travel_###\_Booking,
          rba_link     TYPE TABLE FOR READ LINK zrap_r_travel_###\_Booking.

    read_in = VALUE #( ( TravelID               = mv_travel_id
                         %control-Description   = if_abap_behv=>mk-on
                         %control-OverallStatus = if_abap_behv=>mk-on ) ).
    rba_in  = VALUE #( ( TravelID               = mv_travel_id
                         %control-BookingID     = if_abap_behv=>mk-on
                         %control-FlightPrice   = if_abap_behv=>mk-on ) ).

    op_read = VALUE #(
      ( op          = if_abap_behv=>op-r-read
        entity_name = 'ZRAP_R_TRAVEL_###'           "엔터티 이름(대문자), 별칭 아님
        instances   = REF #( read_in )
        results     = REF #( read_out ) )
      ( op          = if_abap_behv=>op-r-read_ba
        entity_name = 'ZRAP_R_TRAVEL_###'
        sub_name    = '_BOOKING'                    "연관 이름(대문자)
        full        = abap_true                     "대상 인스턴스 전체
        instances   = REF #( rba_in )
        results     = REF #( rba_out )
        links       = REF #( rba_link ) ) ).

    READ ENTITIES OPERATIONS op_read.
    out->write( |동적 READ: Travel { lines( read_out ) }건(설명 "{ VALUE #( read_out[ 1 ]-Description OPTIONAL ) }"), | &&
                |Booking { lines( rba_out ) }건, LINK { lines( rba_link ) }줄| ).

    "------------------------------------------------------------------
    " 동적 MODIFY : MODIFY ENTITIES OPERATIONS
    "------------------------------------------------------------------
    DATA: op_modify  TYPE abp_behv_changes_tab,
          create_in  TYPE TABLE FOR CREATE zrap_r_travel_###,
          cba_in     TYPE TABLE FOR CREATE zrap_r_travel_###\_Booking,
          update_in  TYPE TABLE FOR UPDATE zrap_r_travel_###.

    DATA(today) = cl_abap_context_info=>get_system_date( ).
    create_in = VALUE #( ( %cid                  = 'DYN_T'
                           CustomerID            = mv_customer_id
                           AgencyID              = mv_agency_id
                           BeginDate             = ms_flight-flight_date
                           EndDate               = ms_flight-flight_date + 2
                           CurrencyCode          = ms_flight-currency_code
                           Description           = 'dynamic create'
                           %control-CustomerID   = if_abap_behv=>mk-on
                           %control-AgencyID     = if_abap_behv=>mk-on
                           %control-BeginDate    = if_abap_behv=>mk-on
                           %control-EndDate      = if_abap_behv=>mk-on
                           %control-CurrencyCode = if_abap_behv=>mk-on
                           %control-Description  = if_abap_behv=>mk-on ) ).
    cba_in = VALUE #( ( %cid_ref = 'DYN_T'
                        %target  = VALUE #( ( %cid                   = 'DYN_B'
                                              CustomerID             = mv_customer_id
                                              CarrierID              = ms_flight-carrier_id
                                              ConnectionID           = ms_flight-connection_id
                                              FlightDate             = ms_flight-flight_date
                                              BookingStatus          = 'N'
                                              %control-CustomerID    = if_abap_behv=>mk-on
                                              %control-CarrierID     = if_abap_behv=>mk-on
                                              %control-ConnectionID  = if_abap_behv=>mk-on
                                              %control-FlightDate    = if_abap_behv=>mk-on
                                              %control-BookingStatus = if_abap_behv=>mk-on ) ) ) ).
    update_in = VALUE #( ( TravelID             = mv_travel_id
                           Description          = |dynamic update { today }|
                           %control-Description = if_abap_behv=>mk-on ) ).

    op_modify = VALUE #(
      ( op = if_abap_behv=>op-m-create    entity_name = 'ZRAP_R_TRAVEL_###'                     instances = REF #( create_in ) )
      ( op = if_abap_behv=>op-m-create_ba entity_name = 'ZRAP_R_TRAVEL_###' sub_name = '_BOOKING' instances = REF #( cba_in ) )
      ( op = if_abap_behv=>op-m-update    entity_name = 'ZRAP_R_TRAVEL_###'                     instances = REF #( update_in ) ) ).

    MODIFY ENTITIES OPERATIONS op_modify
      MAPPED   DATA(dyn_mapped)
      FAILED   DATA(dyn_failed)
      REPORTED DATA(dyn_reported).
    "응답도 동적 형태(abp_behv_response_tab)일 수 있으므로 줄 수만 출력
    out->write( |동적 MODIFY: mapped { lines( dyn_mapped ) }줄, failed { lines( dyn_failed ) }줄| ).
    ROLLBACK ENTITIES.

    "------------------------------------------------------------------
    " 런타임에 BDEF 파생 타입 만들기
    "------------------------------------------------------------------
    DATA dref TYPE REF TO data.
    DATA static_create TYPE TABLE FOR CREATE zrap_r_travel_###.
    DATA(tdo) = cl_abap_tabledescr=>get_bdef_derived_type(
                  p_entity = 'ZRAP_R_TRAVEL_###'
                  p_kind   = abp_bdef_derived_type-create ).
    CREATE DATA dref TYPE HANDLE tdo.
    DATA(dyn_tdo) = CAST cl_abap_tabledescr( cl_abap_typedescr=>describe_by_data( dref->* ) ).
    out->write( |get_bdef_derived_type 호환: { dyn_tdo->applies_to_data( static_create ) }| ).

    "언제 동적 형식을 쓰나
    "- 대상 BO/엔터티 이름을 실행 시점에만 아는 일반화 도구(데이터 이관, 범용 업로드, 테스트 헬퍼)
    "- 여러 BO 에 대한 연산을 한 문장에 모아 실행할 때
    "- 그 밖의 일반 비즈니스 코드는 정적 형식이 타입 검사·가독성 면에서 훨씬 낫다
  ENDMETHOD.
```

> `MODIFY ENTITIES OPERATIONS`의 `MAPPED`/`FAILED`/`REPORTED` 인라인 선언 타입은 08 치트시트 예제(`MAPPED DATA(m) FAILED DATA(f) REPORTED DATA(r)`)대로 썼습니다. 생성되는 타입이 표가 아니라 구조라서 `lines( )`에서 문법 오류가 나면 F2로 타입을 보고 출력 방식을 바꾸세요(실제 시스템에서 확인 필요).

콘솔 출력 예시

```
=== 9단계: 동적 EML ===
동적 READ: Travel 1건(설명 "EML commit 20261017"), Booking 2건, LINK 2줄
동적 MODIFY: mapped 2줄, failed 0줄
get_bdef_derived_type 호환: X
```

**왜 이렇게 쓰나**
- 동적 형식의 연산 표(`abp_behv_retrievals_tab`, `abp_behv_changes_tab`, `abp_behv_locks_tab`)는 "연산 종류(`op`) + 엔터티 이름 + 입력/결과 표 참조"로 이루어집니다. 입력 표는 여전히 BDEF 파생 타입이어야 하므로, 타입까지 동적으로 만들려면 `get_bdef_derived_type`을 같이 씁니다.
- 동적 형식에서는 `FIELDS ( ... )` 지름길이 없으므로 `%control`을 반드시 직접 채웁니다. 빠뜨리면 아무 필드도 바뀌지/읽히지 않습니다.
- `entity_name`은 별칭(`Travel`)이 아니라 CDS 엔터티 이름(`ZRAP_R_TRAVEL_###`)입니다. 연관 이름도 대문자 `'_BOOKING'`입니다.

</details>

#### 10단계. 메시지 다루기와 트랜잭션 단계(cl_abap_tx)

요구사항
1. 메서드 `m10_messages_phases`를 추가하세요.
2. **메시지 해부**: 4단계 (b)처럼 오류가 나는 Travel을 COMMIT하고 `RESPONSE OF`로 받은 `reported-travel`의 각 줄에서 다음을 출력하세요.
   - `%msg->if_message~get_text( )`, `%msg->m_severity`
   - `%msg`를 `ZCM_RAP_###`으로 `CAST`해 `if_t100_message~t100key-msgid`, `msgno`
   - `%element`에서 켜진 필드, `%state_area`
3. **상호작용 단계 메시지와 저장 단계 메시지 비교**: 5단계의 할인 오류(상호작용)와 위 검증 오류(저장)가 어느 응답에 들어오는지 표로 주석에 정리하세요.
4. **cl_abap_behv_aux**: 콘솔에서 `cl_abap_behv_aux=>get_current_phase( )`를 호출해 결과를 출력하세요(행동 풀 밖에서 무엇이 나오는지 관찰).
5. **트랜잭션 단계 위반 실험**: 상수 `c_show_dump TYPE abap_bool VALUE abap_false`를 두고, `abap_true`로 바꾸면 `cl_abap_tx=>modify( )` 다음에 `DELETE FROM zrap_tlog_### WHERE travel_id = '99999999'`를 실행해 런타임 오류를 직접 보도록 만드세요. 기본값에서는 `cl_abap_tx=>save( )` 다음에 같은 문장을 실행해 정상(0건 삭제)임을 출력합니다.
6. `main`을 최종 형태로 정리하세요(1~10단계 메서드를 순서대로 호출, 11단계는 R-06 이후).

**확인** 메시지마다 메시지 클래스 `ZRAP_MSG_###`와 번호(예: 002, 005)가 출력되고, `c_show_dump = abap_true`로 실행하면 런타임 오류 `BEHAVIOR_ILLEGAL_STMT_IN_CALL`이 납니다(ST22에 해당하는 ADT "ABAP Runtime Errors" 뷰에서 확인).

<details><summary>정답·해설</summary>

정의부에 추가:

```abap
    METHODS m10_messages_phases IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
```

구현부에 추가:

```abap
  METHOD m10_messages_phases.
    out->write( `=== 10단계: 메시지와 트랜잭션 단계 ===` ).
    ROLLBACK ENTITIES.
    CONSTANTS c_show_dump TYPE abap_bool VALUE abap_false.
    DATA(today) = cl_abap_context_info=>get_system_date( ).

    "(1) 저장 단계 메시지 해부
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        CREATE FIELDS ( CustomerID AgencyID BeginDate EndDate CurrencyCode )
        WITH VALUE #( ( %cid = 'MSG' CustomerID = '999999' AgencyID = mv_agency_id
                        BeginDate = today - 1 EndDate = today + 3 CurrencyCode = 'EUR' ) ).
    COMMIT ENTITIES RESPONSE OF zrap_r_travel_###
      FAILED   DATA(failed_late)
      REPORTED DATA(reported_late).
    out->write( |COMMIT sy-subrc = { sy-subrc }| ).

    LOOP AT reported_late-travel INTO DATA(rep).
      IF rep-%msg IS NOT BOUND.
        out->write( |  [state area 지우기] { rep-%state_area }| ).
        CONTINUE.
      ENDIF.
      DATA(fields) = ``.
      IF rep-%element-CustomerID = if_abap_behv=>mk-on. fields = fields && ` CustomerID`. ENDIF.
      IF rep-%element-BeginDate  = if_abap_behv=>mk-on. fields = fields && ` BeginDate`.  ENDIF.
      IF rep-%element-EndDate    = if_abap_behv=>mk-on. fields = fields && ` EndDate`.    ENDIF.
      IF rep-%element-AgencyID   = if_abap_behv=>mk-on. fields = fields && ` AgencyID`.   ENDIF.

      "예외 클래스 기반 메시지면 T100 키를 꺼낼 수 있음
      DATA(t100) = ``.
      TRY.
          DATA(cm) = CAST zcm_rap_###( rep-%msg ).
          t100 = |{ cm->if_t100_message~t100key-msgid } { cm->if_t100_message~t100key-msgno }|.
        CATCH cx_sy_move_cast_error.
          t100 = `(ZCM 아님)`.
      ENDTRY.

      out->write( |  { severity_text( rep-%msg ) } [{ t100 }] area={ rep-%state_area } 필드:{ fields } → { rep-%msg->if_message~get_text( ) }| ).
    ENDLOOP.
    ROLLBACK ENTITIES.

    "(2) 메시지가 어느 응답에 들어오나
    "    | 검사 종류                         | 언제 실행      | 결과가 들어오는 곳                        |
    "    | 핸들러의 즉시 검사(deductDiscount) | MODIFY 시     | MODIFY 의 FAILED/REPORTED (EARLY)        |
    "    | precheck_create / precheck_update | MODIFY 직전   | MODIFY 의 FAILED/REPORTED (EARLY)        |
    "    | validation on save               | COMMIT 시     | COMMIT RESPONSE(S) 의 FAILED/REPORTED(LATE)|
    "    | draft 의 validation              | Prepare 시    | EXECUTE Prepare 의 FAILED/REPORTED       |

    "(3) 행동 풀 밖에서의 RAP 단계 정보
    DATA(phase) = cl_abap_behv_aux=>get_current_phase( ).
    out->write( |cl_abap_behv_aux=>get_current_phase( ) = "{ phase }" (콘솔은 RAP 핸들러 밖)| ).

    "(4) 트랜잭션 단계 위반 실험 (cl_abap_tx : 제어된 SAP LUW)
    IF c_show_dump = abap_true.
      cl_abap_tx=>modify( ).
      "modify 단계에서 DB 변경 → ABAP Cloud 에서는 런타임 오류 BEHAVIOR_ILLEGAL_STMT_IN_CALL
      DELETE FROM zrap_tlog_### WHERE travel_id = '99999999'.
    ENDIF.

    cl_abap_tx=>save( ).
    "save 단계에서는 DB 변경 허용
    DELETE FROM zrap_tlog_### WHERE travel_id = '99999999'.
    out->write( |save 단계 DELETE: sy-subrc = { sy-subrc }, 삭제 { sy-dbcnt }건| ).
    "주의: 이 뒤로 이 LUW 에서 EML MODIFY 를 하면 save 단계 규칙에 걸릴 수 있으므로
    "      10단계를 main 의 마지막에 둡니다(실제 동작은 시스템에서 확인 필요).
  ENDMETHOD.
```

`main` 최종 형태:

```abap
  METHOD if_oo_adt_classrun~main.
    prepare_sample_data( out ).
    m01_derived_types( out ).
    m02_read( out ).
    m03_modify( out ).
    m04_commit( out ).
    m05_actions( out ).
    m06_draft( out ).
    m07_locks_permissions( out ).
    m08_layers( out ).
    m09_dynamic( out ).
    "m11_unmanaged( out ).   "R-06 완료 후 주석 해제
    m10_messages_phases( out ).   "트랜잭션 단계를 바꾸므로 항상 마지막
  ENDMETHOD.
```

> `zrap_tlog_###`의 `travel_id` 필드는 R-04에서 만든 변경 로그 테이블 구조를 가정했습니다. 필드명이 다르면 그 테이블의 키 필드로 바꾸세요. 목적은 "아무 줄도 지우지 않는 DB 변경 문장"을 실행하는 것입니다.

콘솔 출력 예시

```
=== 10단계: 메시지와 트랜잭션 단계 ===
COMMIT sy-subrc = 4
  [state area 지우기] VALIDATE_CUSTOMER
  E [ZRAP_MSG_### 002] area=VALIDATE_CUSTOMER 필드: CustomerID → Customer 999999 does not exist.
  [state area 지우기] VALIDATE_DATES
  E [ZRAP_MSG_### 006] area=VALIDATE_DATES 필드: BeginDate → Begin date 20261016 must be on or after today.
cl_abap_behv_aux=>get_current_phase( ) = ""
save 단계 DELETE: sy-subrc = 4, 삭제 0건
```

**왜 이렇게 쓰나**
- `%msg`는 `IF_ABAP_BEHV_MESSAGE` 참조입니다. 텍스트는 `if_message~get_text( )`, 심각도는 `m_severity`로 읽습니다. R-02처럼 예외 클래스로 메시지를 만들면 `CAST`로 T100 키와 속성(고객 번호 등)까지 꺼낼 수 있어 테스트에서 "어떤 메시지인지" 정확히 비교할 수 있습니다(R-13에서 사용).
- `%state_area`만 있고 `%msg`가 없는 줄은 "이 검증 영역의 이전 메시지를 지우라"는 신호입니다. Fiori는 이 줄을 보고 오래된 오류를 화면에서 지웁니다. 그래서 검증이 성공해도 `reported`가 비어 있지 않을 수 있습니다.
- 제어된 SAP LUW(`cl_abap_tx`)에서 modify 단계의 DB 변경은 금지입니다. RAP 핸들러 메서드는 기본으로 modify 단계에서 돌기 때문에 핸들러에서 `INSERT/UPDATE/DELETE dbtab`을 쓰면 같은 런타임 오류가 납니다. DB 변경은 세이버의 `save`/`save_modified`에서만 합니다.

**자주 나는 오류와 해결**
- `BEHAVIOR_ILLEGAL_STMT_IN_CALL`: modify 단계(또는 핸들러 안)에서 DB를 바꿨습니다. 세이버 메서드로 옮기거나, 직접 만든 소비자 코드라면 `cl_abap_tx=>save( )` 뒤로 옮기세요(17 SAP LUW 치트시트).
- `CAST zcm_rap_###` 실패: 프레임워크가 만든 메시지(예: 잠금 메시지)는 예외 클래스가 다릅니다. 반드시 `TRY ... CATCH cx_sy_move_cast_error`로 감쌉니다.

</details>

#### 11단계. 비교 실습: 비관리형 Order BO에 같은 EML 쓰기

요구사항
1. 메서드 `m11_unmanaged`를 추가하세요(R-05 ~ R-06 완료 후).
2. `ZRAP_R_ORDER_U_###`에 깊은 생성을 하세요: 루트 `Order`(`%cid = 'O1'`, `Requester = 'EML TEST'`, `SupplierID` = 샘플 여행사, `OrderDate` = 오늘, `DeliveryDate` = 오늘+14, `CurrencyCode = 'EUR'`, `Note = 'created by EML'`) + `CREATE BY \_Items`로 품목 2건(`ProductID`, `ItemText`, `Quantity`, `QuantityUnit = 'EA'`, `UnitPrice`).
3. `mapped-order`에서 임시 키(`%key-OrderID`, 예: 9000000001)를 출력하고, 같은 요청 안에서 `%cid_ref = 'O1'`로 `approveOrder`를 실행하세요.
4. `READ ENTITIES ... ENTITY Order BY \_Items`로 임시 키 상태의 품목을 읽어 `ItemAmount`, 헤더 `TotalAmount`를 출력하세요(레거시 버퍼가 계산).
5. 없는 주문 `'0000000001'`을 UPDATE해 비관리형 핸들러가 채운 `%fail-cause`와 메시지를 출력하세요.
6. `COMMIT ENTITIES BEGIN ... CONVERT KEY ... END`로 최종 키를 얻으세요. 이 BO는 `%pid`를 채우지 않으므로 임시 키(`%tmp`)를 넘기는 형태가 필요합니다(문법 확인 필요). 실패 시 대안으로 `ZLEG_ORDH_###`에서 `note = 'created by EML'`인 최신 주문을 SELECT하세요.
7. 관리형과 비교해 "소비자 입장에서 같은 점/다른 점"을 표로 정리하세요.

**확인** 임시 키 9000000001 → 최종 키(레거시 번호), 승인 상태 `A`, 레거시 테이블 `ZLEG_ORDH_###`/`ZLEG_ORDI_###`에 각각 1건/2건이 저장되어야 합니다.

<details><summary>정답·해설</summary>

정의부에 추가:

```abap
    METHODS m11_unmanaged IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
```

구현부에 추가:

```abap
  METHOD m11_unmanaged.
    out->write( `=== 11단계: 비관리형 Order BO ===` ).
    ROLLBACK ENTITIES.
    DATA(today) = cl_abap_context_info=>get_system_date( ).

    SELECT FROM /dmo/supplement FIELDS supplement_id, price, currency_code
      WHERE currency_code = 'EUR'
      ORDER BY supplement_id
      INTO TABLE @DATA(products)
      UP TO 2 ROWS.
    CHECK lines( products ) = 2.

    "(1) 깊은 생성 + 같은 요청에서 액션 (소비자 코드 모양은 관리형과 완전히 같음)
    MODIFY ENTITIES OF zrap_r_order_u_###
      ENTITY Order
        CREATE FIELDS ( Requester SupplierID OrderDate DeliveryDate CurrencyCode Note )
        WITH VALUE #( ( %cid         = 'O1'
                        Requester    = 'EML TEST'
                        SupplierID   = mv_agency_id
                        OrderDate    = today
                        DeliveryDate = today + 14
                        CurrencyCode = 'EUR'
                        Note         = 'created by EML' ) )
        CREATE BY \_Items
          FIELDS ( ProductID ItemText Quantity QuantityUnit UnitPrice )
          WITH VALUE #( ( %cid_ref = 'O1'
                          %target  = VALUE #(
                            ( %cid = 'I1' ProductID = products[ 1 ]-supplement_id ItemText = 'first item'
                              Quantity = 2 QuantityUnit = 'EA' UnitPrice = products[ 1 ]-price )
                            ( %cid = 'I2' ProductID = products[ 2 ]-supplement_id ItemText = 'second item'
                              Quantity = 1 QuantityUnit = 'EA' UnitPrice = products[ 2 ]-price ) ) ) )
        EXECUTE approveOrder FROM VALUE #( ( %cid_ref = 'O1' ) )
      MAPPED DATA(mapped)
      FAILED DATA(failed)
      REPORTED DATA(reported).

    LOOP AT mapped-order INTO DATA(mo).
      "비관리형 late numbering: 핸들러(레거시 API)가 임시 키를 %key 에 넣어 돌려줌, %pid 는 비어 있음
      out->write( |Order 임시 키 { mo-OrderID } (%pid 비어 있음: { xsdbool( mo-%pid IS INITIAL ) })| ).
    ENDLOOP.
    out->write( |Item mapped { lines( mapped-item ) }건, failed Order { lines( failed-order ) }건| ).
    LOOP AT reported-order INTO DATA(ro) WHERE %msg IS BOUND.
      out->write( |  { severity_text( ro-%msg ) } { ro-%msg->if_message~get_text( ) }| ).
    ENDLOOP.
    CHECK mapped-order IS NOT INITIAL.

    "(2) 임시 키로 읽기 - 레거시 버퍼(트랜잭션 버퍼 역할)의 현재 상태
    READ ENTITIES OF zrap_r_order_u_###
      ENTITY Order
        FIELDS ( Status TotalAmount CurrencyCode ) WITH CORRESPONDING #( mapped-order )
        RESULT DATA(orders)
      ENTITY Order BY \_Items
        FIELDS ( ItemNo ItemAmount ) WITH CORRESPONDING #( mapped-order )
        RESULT DATA(items).
    out->write( |버퍼 상태: 상태 { orders[ 1 ]-Status } 합계 { orders[ 1 ]-TotalAmount } { orders[ 1 ]-CurrencyCode }, 품목 { lines( items ) }건| ).

    "(3) 없는 인스턴스 → 비관리형 핸들러가 직접 채운 %fail-cause
    MODIFY ENTITIES OF zrap_r_order_u_###
      ENTITY Order
        UPDATE FIELDS ( Note ) WITH VALUE #( ( OrderID = '0000000001' Note = 'x' ) )
      FAILED DATA(upd_failed)
      REPORTED DATA(upd_reported).
    LOOP AT upd_failed-order INTO DATA(fo).
      out->write( |없는 주문 UPDATE: cause={ COND string( WHEN fo-%fail-cause = if_abap_behv=>cause-not_found THEN `not_found`
                                                           ELSE |{ fo-%fail-cause }| ) }| ).
    ENDLOOP.
    LOOP AT upd_reported-order INTO DATA(ru) WHERE %msg IS BOUND.
      out->write( |  { ru-%msg->if_message~get_text( ) }| ).
    ENDLOOP.

    "(4) 저장 + 최종 키
    DATA final_order_id TYPE zrap_r_order_u_###-OrderID.
    COMMIT ENTITIES BEGIN
      RESPONSE OF zrap_r_order_u_### FAILED DATA(c_failed) REPORTED DATA(c_reported).
    IF sy-subrc = 0.
      "%pid 를 쓰지 않는 BO: 임시 키를 %tmp 로 넘기는 형태 (실제 시스템에서 확인 필요)
      CONVERT KEY OF zrap_r_order_u_###
        FROM TEMPORARY VALUE #( %pid = mapped-order[ 1 ]-%pid
                                %tmp = mapped-order[ 1 ]-%key )
        TO DATA(order_key).
      final_order_id = order_key-OrderID.
    ENDIF.
    COMMIT ENTITIES END.

    IF final_order_id IS INITIAL.
      "대안: 레거시 테이블에서 방금 저장한 주문 찾기
      SELECT FROM zleg_ordh_### FIELDS MAX( order_id ) WHERE note = 'created by EML' INTO @final_order_id.
    ENDIF.
    SELECT COUNT(*) FROM zleg_ordi_### WHERE order_id = @final_order_id INTO @DATA(item_count).
    out->write( |최종 OrderID { final_order_id }, 레거시 품목 { item_count }건| ).
  ENDMETHOD.
```

> `ZLEG_ORDH_###`/`ZLEG_ORDI_###`의 `order_id`, `note` 필드명은 R-05의 레거시 테이블 설계를 가정했습니다. `CONVERT KEY ... FROM TEMPORARY`의 정확한 문법은 ADT의 F1로 확인하세요(실제 시스템에서 확인 필요). 이 줄에서 문법 오류가 나면 지우고 SELECT 대안만 쓰면 됩니다.

콘솔 출력 예시

```
=== 11단계: 비관리형 Order BO ===
Order 임시 키 9000000001 (%pid 비어 있음: X)
Item mapped 2건, failed Order 0건
버퍼 상태: 상태 A 합계 270.00 EUR, 품목 2건
없는 주문 UPDATE: cause=not_found
  Order 0000000001 does not exist.
최종 OrderID 0000000042, 레거시 품목 2건
```

관리형 vs 비관리형 – 소비자 입장 비교

| 관점 | 관리형 Travel | 비관리형 Order |
|---|---|---|
| EML 문법 | 같음 | 같음 |
| 트랜잭션 버퍼 | 프레임워크 | 레거시 클래스 `ZCL_LEG_ORDER_###`의 자체 버퍼 |
| late numbering 임시 식별 | `%pid`(프레임워크가 생성) | `%key`에 임시 번호(9000000001부터), `%pid`는 비어 있음 |
| `failed`/`%fail-cause` | 프레임워크가 not_found/locked 등 채움 | 핸들러가 직접 채움(품질이 구현에 달림) |
| `ROLLBACK ENTITIES` | 버퍼 자동 정리 | 세이버 `cleanup`이 레거시 버퍼를 비워야 함 |
| `READ ... WITH CHANGES` | 행동 풀 안에서 가능 | 불가(관리형 전용) |

**왜 이렇게 쓰나**
- EML은 BO 구현 방식(관리형/비관리형)을 숨기는 계약입니다. 소비자 코드는 같고, 차이는 "응답이 얼마나 정확하게 채워지는가"에서 드러납니다. 그래서 비관리형 BO를 만들 때는 `failed`의 `%fail-cause`, `mapped`의 `%cid`↔임시 키, `cleanup`을 계약대로 구현하는 것이 품질의 핵심입니다(R-06).
- 08 치트시트의 "Late Numbering and Key Identification" 절대로, 저장 단계에서는 상호작용 단계의 임시 키가 `%tmp`로 옮겨지고 `%key`에 최종 키가 들어갑니다. 비관리형 BO는 `%pid` 대신 `%key`에 임시 키를 쓰므로 `%tmp`가 그 값을 받습니다.

</details>


### R-13. RAP BO 테스트: ABAP Unit, 테스트 더블, OData 수준 테스트 [작성] ★★★
<!-- covers: ABAP Unit, FOR TESTING, RISK LEVEL, DURATION, class_setup, setup, teardown, class_teardown, cl_abap_unit_assert, DEFINITION DEFERRED FOR TESTING, FRIENDS, CREATE OBJECT FOR TESTING, @testing BDEF, @testing SRVB, CDS test double framework, cl_cds_test_environment, create_for_multiple_cds, enable_double_redirection, i_select_base_dependencies, insert_test_data, clear_doubles, ABAP SQL test double framework, cl_osql_test_environment, MAPPING TO ENTITY, TYPE TABLE FOR VALIDATION, TYPE TABLE FOR DETERMINATION, TYPE TABLE FOR ACTION IMPORT, TYPE TABLE FOR ACTION RESULT, TYPE TABLE FOR FUNCTION IMPORT, TYPE TABLE FOR FUNCTION RESULT, TYPE TABLE FOR INSTANCE FEATURES, GLOBAL AUTHORIZATION, TYPE TABLE FOR AUTHORIZATION, RESPONSE FOR FAILED LATE, RESPONSE FOR REPORTED LATE, RESPONSE FOR MAPPED LATE, REQUEST FOR CHANGE, REQUEST FOR DELETE, state message test, %state_area, %element, t100key, if_abap_behavior_testdouble, cl_abap_behv_test_environment, set_test_double, unset_test_double, saver test, adjust_numbers, %tmp, %pid, save_modified, cl_aunit_authority_check, RAP BO test double framework, cl_botd_txbufdbl_bo_test_env, cl_botd_mockemlapi_bo_test_env, handle_draft, if_botd_bufdbl_fields_handler, cl_botd_mockemlapi_bldrfactory, configure_call, when_input, then_set_output, ignore_input, for_times, verify, is_called_times, GET PERMISSIONS test, COMMIT ENTITIES in test, integration test, CDS view unit test, test_associations, OData local client proxy, cl_web_odata_client_factory, create_v2_local_proxy, navigate_with_key, set_if_match, create_filter_factory, set_deep_business_data, cl_abap_testdouble, TEST-SEAM, TEST-INJECTION, code coverage -->

**목표**
- 행동 풀(Behavior Pool)의 핸들러·세이버 메서드를 프레임워크 없이 직접 호출하는 **단위 테스트**를 쓸 수 있습니다(`CREATE OBJECT ... FOR TESTING`, `FRIENDS`).
- CDS 테스트 더블(`cl_cds_test_environment`)과 SQL 테스트 더블(`cl_osql_test_environment`)로 DB 데이터를 통제하고, 검증·결정·액션·기능 제어·권한·`adjust_numbers`·`save_modified`를 각각 검사할 수 있습니다.
- 다른 RAP BO에 기대는 코드를 **RAP BO 테스트 더블 프레임워크**(트랜잭션 버퍼 더블, EML API 목)로 격리할 수 있고, 둘 중 무엇을 언제 쓰는지 고를 수 있습니다.
- `COMMIT ENTITIES`까지 포함한 **통합 테스트**, CDS 뷰 자체의 **뷰 테스트**, 로컬 OData 클라이언트 프록시로 서비스 바인딩을 부르는 **OData 수준 테스트**를 만들 수 있습니다.
- 테스트 결과에서 `failed`/`reported`(메시지 클래스·번호·필드·state area)를 정확히 단언(assert)할 수 있습니다.

**전제**
- R-01 ~ R-04의 관리형 draft Travel BO가 활성화되어 있어야 합니다. 이 문제는 다음 이름을 그대로 씁니다.
  - BDEF `ZRAP_R_TRAVEL_###`(별칭 `Travel`, `Booking`), late numbering, `with draft`, `managed with additional save with full data`
  - 행동 풀 `ZBP_RAP_R_TRAVEL_###`: 핸들러 `lhc_travel`(상수 `travel_status`, `state_area`, `c_ctrl_id`, 메서드 `setInitialValues`, `validateCustomer`, `validateAgency`, `validateDates`, `acceptTravel`, `rejectTravel`, `deductDiscount`, `reCalcTotalPrice`, `GetDefaultsFordeductDiscount`, `get_instance_features`, `get_global_features`, `get_global_authorizations`, `get_instance_authorizations`, `is_update_granted`), 세이버 `lsc_zrap_r_travel_###`(`adjust_numbers`, `save_modified`)
  - 활성 테이블 `ZRAP_ATRAV_###`, `ZRAP_ABOOK_###`, 변경 로그 `ZRAP_TLOG_###`(R-04: `log_uuid`, `travel_id`, `booking_id`, `entity_name`, `operation`, `field_name`, `new_value`, `changed_by`, `changed_at`), 스위치 테이블 `ZRAP_CTRL_###`(R-03: `ctrl_id`, `create_closed`, `sunday_closed`, `deny_country`), 이벤트 로그 `ZRAP_EVLOG_###`
  - 예외 클래스 `ZCM_RAP_###`(상수 `enter_customer_id`, `customer_unknown`, `agency_unknown`, `enter_dates`, `begin_date_after_end_date`, `begin_date_in_past`, `discount_invalid`, `travel_accepted`, `not_authorized_country` 등)
  - 프로젝션 `ZRAP_C_TRAVEL_###`/`ZRAP_C_BOOKING_###`, 서비스 정의 `ZRAP_UI_TRAVEL_###`(Travel을 `Travel`, Booking을 `Booking`이라는 이름으로 노출)
- R-12에서 EML 문법을 익혔어야 합니다.
- 표준 객체: `/DMO/CUSTOMER`, `/DMO/AGENCY`, `/DMO/I_Agency`, `/DMO/I_Customer`, `/DMO/FLIGHT`, `/DMO/CARRIER`

**만들 객체**

| 순서 | 객체 유형 | 이름 | 역할 |
|---|---|---|---|
| 1 | 행동 풀 Test Classes 탭 | `ZBP_RAP_R_TRAVEL_###` (CCAU) | 핸들러 단위 테스트 `ltc_travel_handler`, EML 스텁 테스트 `ltc_travel_stub`, 세이버 테스트 `ltc_saver`, `ltc_saver_numbers` |
| 2 | 행동 풀 Local Types 수정 | `ZBP_RAP_R_TRAVEL_###` (CCIMP) | `DEFINITION DEFERRED FOR TESTING`, `FRIENDS` 추가 |
| 3 | ABAP 클래스(테스트 전용) | `ZTC_RAP_TRAVEL_EML_###` | `COMMIT ENTITIES`까지 하는 BO 통합 테스트 |
| 4 | ABAP 클래스 | `ZCL_RAP_TRAV_APPROVER_###` | Travel BO를 EML로 쓰는 소비자(테스트 대상 코드) |
| 5 | 4번의 Test Classes 탭 | `ZCL_RAP_TRAV_APPROVER_###` (CCAU) | 트랜잭션 버퍼 더블 테스트, EML API 목 테스트 |
| 6 | 데이터 정의(CDS 뷰 엔터티) | `ZRAP_I_TRAVEL_KPI_###` | 계산 필드가 있는 조회용 뷰(뷰 테스트 대상) |
| 7 | ABAP 클래스(테스트 전용) | `ZTC_RAP_TRAVEL_KPI_###` | CDS 뷰 테스트 |
| 8 | 서비스 바인딩 | `ZRAP_API_TRAVEL_O2_###` | OData V2 - Web API 바인딩(로컬 프록시 테스트용) |
| 9 | ABAP 클래스(테스트 전용) | `ZTC_RAP_TRAVEL_ODATA_###` | 로컬 OData 클라이언트 프록시 테스트 |

> 진행 방법: 단계마다 테스트 메서드를 추가하고 `Ctrl+Shift+F10`(Run As → ABAP Unit Test)으로 실행합니다. 결과는 ADT의 **ABAP Unit** 뷰에 나옵니다. 단계별 정답 코드는 "추가할 부분"만 보여 주고, 처음 만드는 클래스는 전체를 보여 줍니다. 아래 테스트 데이터의 날짜는 모두 `cl_abap_context_info=>get_system_date( )` 기준으로 계산하므로 언제 실행해도 같은 결과가 나와야 합니다.

#### 1단계. 테스트 전략과 준비: 어떤 더블을 언제 쓰나, 행동 풀 열어 주기

요구사항
1. 아래 표를 읽고, 이 문제에서 만들 테스트가 각각 무엇을 격리하는지 이해하세요(정답 해설에 같은 표가 있습니다).

| 테스트 대상 | 기대는 것(의존성) | 쓰는 도구 |
|---|---|---|
| 핸들러 메서드(검증·결정·액션·기능·권한) | DB 테이블, 다른 표준 테이블 | CDS 테스트 더블 + SQL 테스트 더블 |
| 핸들러 메서드 안의 EML 자체 | 트랜잭션 버퍼 | `if_abap_behavior_testdouble` 스텁 |
| 세이버 메서드 | DB 테이블 | SQL 테스트 더블 |
| BO 전체(EML → COMMIT) | DB 테이블 | CDS + SQL 테스트 더블(통합 테스트) |
| BO를 **쓰는** 다른 코드 | RAP BO 전체 | 트랜잭션 버퍼 더블 또는 EML API 목 |
| CDS 뷰 계산 로직 | 뷰가 읽는 테이블·뷰 | CDS 테스트 더블 |
| OData 서비스 | BO + 서비스 바인딩 | 로컬 OData 클라이언트 프록시 + CDS 테스트 더블 |

2. `ZBP_RAP_R_TRAVEL_###`의 **Local Types** 탭에서 `lhc_travel` 정의 바로 앞에 테스트 클래스 `ltc_travel_handler`, `ltc_travel_stub`의 지연 선언(`DEFINITION DEFERRED FOR TESTING`)을 넣고, `lhc_travel`이 두 클래스를 `FRIENDS`로 선언하게 하세요. 세이버 `lsc_zrap_r_travel_###`도 같은 방식으로 `ltc_saver`, `ltc_saver_numbers`에게 열어 주세요.
3. **Test Classes** 탭에 `ltc_travel_handler`를 만드세요.
   - ABAP Doc `"! @testing BDEF:ZRAP_R_TRAVEL_###`로 BDEF와 연결합니다.
   - `DURATION SHORT`, `RISK LEVEL HARMLESS`
   - `class_setup`: 테스트 대상 `lhc_travel` 인스턴스를 만들고, CDS 테스트 환경(`ZRAP_R_TRAVEL_###`, `ZRAP_R_BOOKING_###`)과 SQL 테스트 환경(`/DMO/CUSTOMER`, `/DMO/AGENCY`, `/DMO/I_AGENCY`, `/DMO/FLIGHT`, `ZRAP_CTRL_###`)을 만듭니다. CDS 환경은 RAP 프레임워크가 더블을 읽도록 리디렉션을 켭니다.
   - `setup`: 모든 더블을 비웁니다. `teardown`: `ROLLBACK ENTITIES`로 트랜잭션 버퍼를 비웁니다. `class_teardown`: 두 환경을 없앱니다.
   - 공용 타입 `tt_travel_db`(`ZRAP_ATRAV_###` 표), `tt_booking_db`(`ZRAP_ABOOK_###` 표)와 상수 `c_travel_1`~`c_travel_4`(`'00000001'`~`'00000004'`)를 둡니다.
4. 첫 테스트 `setinitialvalues_defaults`: 결정 `setInitialValues`를 직접 호출합니다.
   - 테스트 데이터: Travel 1은 키만 있음, Travel 2는 시작일·종료일·통화(`USD`)·상태(`A`)가 모두 채워짐.
   - 기대: Travel 1은 시작일 = 오늘+1, 종료일 = 오늘+15, 통화 `EUR`, 상태 `O`. Travel 2는 그대로. `reported`는 비어 있음.
   - 결과는 `READ ENTITIES`(테스트 클래스는 BO 바깥이므로 `IN LOCAL MODE` 없이)로 읽어 기대 표와 통째로 비교합니다.

**확인** 활성화 후 `Ctrl+Shift+F10`을 누르면 ABAP Unit 뷰에 `LTC_TRAVEL_HANDLER→SETINITIALVALUES_DEFAULTS`가 초록색으로 나옵니다. 실제 테이블 `ZRAP_ATRAV_###`의 Data Preview를 테스트 전후로 비교해 데이터가 바뀌지 않았는지도 보세요.

<details><summary>정답·해설</summary>

**테스트 전략 표(해설)**

| 도구 | 무엇을 바꿔치기하나 | 장점 | 한계 |
|---|---|---|---|
| CDS 테스트 더블 `cl_cds_test_environment` | CDS 엔터티가 읽는 테이블(또는 뷰) | BO의 실제 로직(결정·검증·저장)이 그대로 돌아감 | BO 로직 전체가 함께 실행되므로 "단위"가 커짐 |
| SQL 테스트 더블 `cl_osql_test_environment` | ABAP SQL이 읽고 쓰는 테이블 | 표준 테이블(`/DMO/CUSTOMER`) 내용을 통제 | CDS 엔터티 자체의 의존성은 CDS 더블로 |
| `if_abap_behavior_testdouble` 스텁 | 특정 BO에 대한 모든 READ/MODIFY | 핸들러 메서드만 순수하게 검사 | READ/MODIFY를 직접 흉내 내야 함 |
| 트랜잭션 버퍼 더블 `cl_botd_txbufdbl_bo_test_env` | 소비 코드가 부르는 BO | 생성·수정·삭제·읽기를 실제처럼 기억 | 액션·함수 등은 지원하지 않음(→ 목) |
| EML API 목 `cl_botd_mockemlapi_bo_test_env` | 소비 코드가 부르는 BO | 액션·권한·잠금까지 "입력→출력"으로 설정 | 입력을 정확히 맞춰 설정해야 함 |
| 로컬 OData 프록시 `cl_web_odata_client_factory` | HTTP 계층(없음) | 서비스 바인딩·프로젝션·BO를 한 번에 | 느리고 실패 원인을 찾기 어려움 |

행동 풀 **Local Types**(CCIMP) 탭 – `lhc_travel` 정의 앞부분을 다음처럼 바꿉니다(나머지 정의는 R-02~R-03 그대로).

```abap
"Test classes are defined in the Test Classes include - announce them here
CLASS ltc_travel_handler DEFINITION DEFERRED FOR TESTING.
CLASS ltc_travel_stub    DEFINITION DEFERRED FOR TESTING.

CLASS lhc_travel DEFINITION INHERITING FROM cl_abap_behavior_handler
  FRIENDS ltc_travel_handler ltc_travel_stub.   "tests may call private handler methods
```

세이버 정의 앞부분(같은 탭의 아래쪽)도 바꿉니다.

```abap
CLASS ltc_saver         DEFINITION DEFERRED FOR TESTING.
CLASS ltc_saver_numbers DEFINITION DEFERRED FOR TESTING.

CLASS lsc_zrap_r_travel_### DEFINITION INHERITING FROM cl_abap_behavior_saver
  FRIENDS ltc_saver ltc_saver_numbers.          "tests may call protected saver methods
```

**Test Classes** 탭(CCAU) 전체 – 이번 단계 분량:

```abap
"! @testing BDEF:ZRAP_R_TRAVEL_###
CLASS ltc_travel_handler DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    TYPES tt_travel_db  TYPE STANDARD TABLE OF zrap_atrav_### WITH EMPTY KEY.
    TYPES tt_booking_db TYPE STANDARD TABLE OF zrap_abook_### WITH EMPTY KEY.

    CONSTANTS:
      c_travel_1 TYPE /dmo/travel_id VALUE '00000001',
      c_travel_2 TYPE /dmo/travel_id VALUE '00000002',
      c_travel_3 TYPE /dmo/travel_id VALUE '00000003',
      c_travel_4 TYPE /dmo/travel_id VALUE '00000004'.

    CLASS-DATA class_under_test     TYPE REF TO lhc_travel.
    CLASS-DATA cds_test_environment TYPE REF TO if_cds_test_environment.
    CLASS-DATA sql_test_environment TYPE REF TO if_osql_test_environment.

    CLASS-METHODS class_setup.
    CLASS-METHODS class_teardown.
    METHODS setup.
    METHODS teardown.

    "----- tests (one block per step) -----
    METHODS setinitialvalues_defaults FOR TESTING.
ENDCLASS.


CLASS ltc_travel_handler IMPLEMENTATION.

  METHOD class_setup.
    "Handler classes are abstract for the outside world - FOR TESTING creates one anyway
    CREATE OBJECT class_under_test FOR TESTING.

    "Double the tables behind the BO's CDS entities (zrap_atrav_###, zrap_abook_###)
    cds_test_environment = cl_cds_test_environment=>create_for_multiple_cds(
                             i_for_entities = VALUE #(
                               ( i_for_entity = 'ZRAP_R_TRAVEL_###' )
                               ( i_for_entity = 'ZRAP_R_BOOKING_###' ) ) ).
    "Let the RAP framework (transactional buffer, managed save) use the doubles too
    cds_test_environment->enable_double_redirection( ).

    "Double the tables the handler code reads with ABAP SQL
    sql_test_environment = cl_osql_test_environment=>create(
                             i_dependency_list = VALUE #( ( '/DMO/CUSTOMER' )
                                                          ( '/DMO/AGENCY' )
                                                          ( '/DMO/I_AGENCY' )
                                                          ( '/DMO/FLIGHT' )
                                                          ( 'ZRAP_CTRL_###' ) ) ).
  ENDMETHOD.

  METHOD setup.
    "every test starts with empty doubles
    cds_test_environment->clear_doubles( ).
    sql_test_environment->clear_doubles( ).
  ENDMETHOD.

  METHOD teardown.
    "throw away the transactional buffer filled by the handler under test
    ROLLBACK ENTITIES.                                 "#EC CI_ROLLBACK
  ENDMETHOD.

  METHOD class_teardown.
    cds_test_environment->destroy( ).
    sql_test_environment->destroy( ).
  ENDMETHOD.


  METHOD setinitialvalues_defaults.
    DATA travel_mock_data TYPE tt_travel_db.
    DATA travels_to_test  TYPE TABLE FOR DETERMINATION zrap_r_travel_###\\Travel~setInitialValues.
    DATA reported         TYPE RESPONSE FOR REPORTED LATE zrap_r_travel_###.
    DATA exp_travels      TYPE TABLE FOR READ RESULT zrap_r_travel_###\\Travel.

    DATA(today) = cl_abap_context_info=>get_system_date( ).

    "given: travel 1 is empty, travel 2 is already complete
    travel_mock_data = VALUE #(
      ( travel_id = c_travel_1 )
      ( travel_id = c_travel_2  begin_date = today + 5  end_date = today + 9
        currency_code = 'USD'   overall_status = 'A' ) ).
    cds_test_environment->insert_test_data( travel_mock_data ).

    "keys of the determination: only the key fields (%is_draft = 00 = active instance)
    travels_to_test = CORRESPONDING #( travel_mock_data MAPPING TravelID = travel_id EXCEPT * ).

    "when
    class_under_test->setinitialvalues(
      EXPORTING keys     = travels_to_test
      CHANGING  reported = reported ).

    "then
    cl_abap_unit_assert=>assert_initial( act = reported msg = 'no messages expected' ).

    READ ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        FIELDS ( BeginDate EndDate CurrencyCode OverallStatus )
        WITH CORRESPONDING #( travels_to_test )
      RESULT DATA(read_result).

    exp_travels = VALUE #(
      %is_draft = if_abap_behv=>mk-off
      ( TravelID = c_travel_1  BeginDate = today + 1  EndDate = today + 15
        CurrencyCode = 'EUR'   OverallStatus = class_under_test->travel_status-open )
      ( TravelID = c_travel_2  BeginDate = today + 5  EndDate = today + 9
        CurrencyCode = 'USD'   OverallStatus = 'A' ) ).

    SORT read_result BY TravelID.
    SORT exp_travels BY TravelID.
    cl_abap_unit_assert=>assert_equals( exp = exp_travels act = read_result ).
  ENDMETHOD.

ENDCLASS.
```

**왜 이렇게 쓰나**
- 핸들러 클래스는 `CL_ABAP_BEHAVIOR_HANDLER`를 상속하고 메서드가 모두 PRIVATE이라 보통은 만들 수도 부를 수도 없습니다. `CREATE OBJECT ... FOR TESTING`은 테스트 클래스 안에서만 이를 허용하고, `FRIENDS`가 PRIVATE 메서드·상수(`travel_status`)를 열어 줍니다. 테스트 클래스는 Test Classes 탭에 있으므로 Local Types 탭에서는 `DEFINITION DEFERRED FOR TESTING`으로 이름만 먼저 알립니다(참조 시나리오 `/DMO/BP_TRAVEL_D`와 같은 방식).
- `create_for_multiple_cds`는 BO의 CDS 엔터티가 읽는 테이블(`ZRAP_ATRAV_###`, `ZRAP_ABOOK_###`)을 테스트 더블로 바꿉니다. `enable_double_redirection`을 켜면 RAP 프레임워크가 버퍼를 채울 때도 더블을 읽습니다. 그래서 `insert_test_data`에는 **CDS 엔터티가 아니라 테이블 타입**(`zrap_atrav_###`)의 데이터를 넣습니다.
- 핸들러가 ABAP SQL로 직접 읽는 테이블(`/DMO/CUSTOMER` 등)은 CDS 엔터티의 의존성이 아니므로 SQL 테스트 더블로 따로 바꿉니다. 같은 테이블을 두 환경에 동시에 넣지 마세요.
- `/DMO/I_AGENCY`는 CDS 뷰입니다. R-03의 인스턴스 권한이 이 뷰를 조인하므로 SQL 테스트 환경에 넣었습니다. CDS 뷰를 `cl_osql_test_environment`의 의존성 목록에 넣을 수 있는지는 실제 시스템에서 확인 필요입니다. 안 되면 이 줄을 빼고 4단계의 인스턴스 권한 테스트만 건너뛰세요.
- 결정은 버퍼를 바꾸고 아무것도 돌려주지 않으므로, 결과는 **다시 읽어서** 검사합니다. 테스트 클래스는 BO 바깥 코드이므로 `IN LOCAL MODE`를 쓰지 않습니다.
- `teardown`의 `ROLLBACK ENTITIES`가 없으면 앞 테스트가 버퍼에 남긴 인스턴스가 다음 테스트에 섞입니다.
- `RISK LEVEL HARMLESS`는 "영속 데이터를 바꾸지 않는다"는 약속입니다. 더블만 쓰므로 지킬 수 있습니다. 실제 DB를 바꾸는 테스트는 `DANGEROUS`로 표시해야 합니다(6단계).

**자주 나는 오류와 해결**
- `CREATE OBJECT ... FOR TESTING`에서 "not allowed" 계열 오류: 테스트 클래스 정의에 `FOR TESTING`이 빠졌거나, 코드를 Local Types 탭에 썼습니다. Test Classes 탭에 써야 합니다.
- `CORRESPONDING #( ... MAPPING TravelID = travel_id EXCEPT * )`에서 `EXCEPT *`를 빼면 이름이 같은 다른 필드가 없으므로 결과는 같지만, 의도를 분명히 하려고 붙였습니다.
- 결과 비교가 `%is_draft` 때문에 실패하면 기대 표에도 `%is_draft = if_abap_behv=>mk-off`를 넣었는지 보세요.

**클래스 구조 해설**
- `keys`의 타입 `TABLE FOR DETERMINATION ...~setInitialValues`, `reported`의 타입 `RESPONSE FOR REPORTED LATE`는 BDEF의 `determination setInitialValues on modify { create; }` 한 줄에서 파생됩니다. 결정은 저장 직전·수정 직후 어느 쪽이든 LATE 응답 타입을 씁니다.
- 실제 실행에서는 프레임워크가 Travel 생성 직후 이 메서드를 부르지만, 테스트에서는 우리가 직접 부릅니다. 따라서 "언제 불리는가"(트리거 조건)는 이 테스트가 검사하지 않습니다. 그것은 7단계 통합 테스트가 맡습니다.

</details>

#### 2단계. 검증 테스트: failed, reported, state area, 메시지 번호까지

요구사항
1. `ltc_travel_handler`에 테스트 메서드 6개를 추가하세요.
   - `validatecustomer_success`: 고객 `000001`이 `/DMO/CUSTOMER` 더블에 있고 Travel의 고객도 `000001`. 기대: `failed` 비어 있음, `reported-travel`은 state area 지우기 줄 1개(메시지 없음, `%state_area = 'VALIDATE_CUSTOMER'`).
   - `validatecustomer_unknown`: Travel 고객 `999999`(더블에 없음). 기대: `failed-travel` 1줄, `reported-travel` 2줄. 메시지가 있는 줄은 메시지 클래스 `ZRAP_MSG_###` 번호 `002`(`zcm_rap_###=>customer_unknown`), 심각도 오류, `%element-CustomerID` 켜짐, `%state_area = 'VALIDATE_CUSTOMER'`.
   - `validatecustomer_initial`: 고객이 비어 있음. 기대: 메시지 `zcm_rap_###=>enter_customer_id`.
   - `validateagency_unknown`: 여행사 `070099`(더블에 없음, `070001`만 있음). 기대: `zcm_rap_###=>agency_unknown`, `%element-AgencyID`.
   - `validatedates_table`: 다음 6가지 경우를 표로 만들어 한 번에 검사합니다. 기대 실패 줄 수와 기대 메시지(`textid`)를 표에 같이 둡니다.

| 경우 | 시작일 | 종료일 | 기대 failed 줄 | 기대 메시지 |
|---|---|---|---|---|
| 1 | 비어 있음 | 오늘+5 | 1 | `enter_dates` |
| 2 | 오늘+5 | 비어 있음 | 1 | `enter_dates` |
| 3 | 오늘+9 | 오늘+5 | 1 | `begin_date_after_end_date` |
| 4 | 오늘-1 | 오늘+5 | 1 | `begin_date_in_past` |
| 5 | 오늘 | 오늘 | 0 | 없음 |
| 6 | 오늘+1 | 오늘+10 | 0 | 없음 |

2. 메시지 검사는 헬퍼 메서드 `assert_message`(입력: `reported-travel` 한 줄, 기대 `textid`, 기대 state area)로 만드세요. `%msg`를 `ZCM_RAP_###`로 `CAST`해 `if_t100_message~t100key`를 비교합니다.
3. 상태 메시지를 지우는 줄(`%msg`가 비어 있는 줄)과 진짜 메시지 줄을 구분해 세는 헬퍼 `count_messages`도 만드세요.

**확인** 6개 테스트가 모두 초록색입니다. 일부러 `validateCustomer`의 `%element-CustomerID` 줄을 주석 처리하고 다시 실행해 `validatecustomer_unknown`이 빨간색이 되는지, 실패 메시지가 무엇을 알려 주는지 확인한 뒤 원래대로 돌려 놓으세요.

<details><summary>정답·해설</summary>

정의부 `PRIVATE SECTION`의 테스트 목록에 추가:

```abap
    METHODS validatecustomer_success FOR TESTING.
    METHODS validatecustomer_unknown FOR TESTING.
    METHODS validatecustomer_initial FOR TESTING.
    METHODS validateagency_unknown   FOR TESTING.
    METHODS validatedates_table      FOR TESTING.

    "----- helpers -----
    METHODS assert_message
      IMPORTING reported_line TYPE STRUCTURE FOR REPORTED LATE zrap_r_travel_###\\Travel
                exp_textid    TYPE scx_t100key
                exp_area      TYPE string.
    METHODS count_messages
      IMPORTING reported_tab  TYPE TABLE FOR REPORTED LATE zrap_r_travel_###\\Travel
      RETURNING VALUE(count)  TYPE i.
```

구현부에 추가:

```abap
  METHOD assert_message.
    "a real message line has %msg bound; a state-clearing line has only %tky + %state_area
    cl_abap_unit_assert=>assert_bound( act = reported_line-%msg msg = 'message expected' ).

    "our messages are exception objects of ZCM_RAP_### -> compare the T100 key exactly
    DATA(message) = CAST zcm_rap_###( reported_line-%msg ).
    cl_abap_unit_assert=>assert_equals( exp = exp_textid
                                        act = message->if_t100_message~t100key
                                        msg = 'wrong message' ).
    cl_abap_unit_assert=>assert_equals( exp = if_abap_behv_message=>severity-error
                                        act = reported_line-%msg->m_severity
                                        msg = 'error severity expected' ).
    cl_abap_unit_assert=>assert_equals( exp = exp_area
                                        act = reported_line-%state_area
                                        msg = 'wrong state area' ).
  ENDMETHOD.

  METHOD count_messages.
    LOOP AT reported_tab TRANSPORTING NO FIELDS WHERE %msg IS BOUND.
      count += 1.
    ENDLOOP.
  ENDMETHOD.


  METHOD validatecustomer_success.
    DATA customer_mock_data TYPE STANDARD TABLE OF /dmo/customer WITH EMPTY KEY.
    DATA travel_mock_data   TYPE tt_travel_db.
    DATA travels_to_test    TYPE TABLE FOR VALIDATION zrap_r_travel_###\\Travel~validateCustomer.
    DATA failed             TYPE RESPONSE FOR FAILED LATE zrap_r_travel_###.
    DATA reported           TYPE RESPONSE FOR REPORTED LATE zrap_r_travel_###.

    customer_mock_data = VALUE #( ( customer_id = '000001' last_name = 'Kim' ) ).
    sql_test_environment->insert_test_data( customer_mock_data ).

    travel_mock_data = VALUE #( ( travel_id = c_travel_1 customer_id = '000001' ) ).
    cds_test_environment->insert_test_data( travel_mock_data ).

    travels_to_test = CORRESPONDING #( travel_mock_data MAPPING TravelID = travel_id EXCEPT * ).

    class_under_test->validatecustomer(
      EXPORTING keys     = travels_to_test
      CHANGING  failed   = failed
                reported = reported ).

    cl_abap_unit_assert=>assert_initial( act = failed msg = 'no failure expected' ).
    "exactly one line: the 'clear old state messages' line
    cl_abap_unit_assert=>assert_equals( exp = 1 act = lines( reported-travel ) ).
    cl_abap_unit_assert=>assert_equals( exp = 0 act = count_messages( reported-travel ) ).
    cl_abap_unit_assert=>assert_equals( exp = class_under_test->state_area-customer
                                        act = reported-travel[ 1 ]-%state_area ).
  ENDMETHOD.

  METHOD validatecustomer_unknown.
    DATA customer_mock_data TYPE STANDARD TABLE OF /dmo/customer WITH EMPTY KEY.
    DATA travel_mock_data   TYPE tt_travel_db.
    DATA travels_to_test    TYPE TABLE FOR VALIDATION zrap_r_travel_###\\Travel~validateCustomer.
    DATA failed             TYPE RESPONSE FOR FAILED LATE zrap_r_travel_###.
    DATA reported           TYPE RESPONSE FOR REPORTED LATE zrap_r_travel_###.

    customer_mock_data = VALUE #( ( customer_id = '000001' ) ).
    sql_test_environment->insert_test_data( customer_mock_data ).

    travel_mock_data = VALUE #( ( travel_id = c_travel_1 customer_id = '999999' ) ).
    cds_test_environment->insert_test_data( travel_mock_data ).

    travels_to_test = CORRESPONDING #( travel_mock_data MAPPING TravelID = travel_id EXCEPT * ).

    class_under_test->validatecustomer(
      EXPORTING keys     = travels_to_test
      CHANGING  failed   = failed
                reported = reported ).

    cl_abap_unit_assert=>assert_equals( exp = 1 act = lines( failed-travel ) ).
    cl_abap_unit_assert=>assert_equals( exp = c_travel_1 act = failed-travel[ 1 ]-TravelID ).

    "2 lines = 1 state-clearing line + 1 error message
    cl_abap_unit_assert=>assert_equals( exp = 2 act = lines( reported-travel ) ).
    cl_abap_unit_assert=>assert_equals( exp = 1 act = count_messages( reported-travel ) ).

    LOOP AT reported-travel INTO DATA(message_line) WHERE %msg IS BOUND.
      assert_message( reported_line = message_line
                      exp_textid    = zcm_rap_###=>customer_unknown
                      exp_area      = class_under_test->state_area-customer ).
      "the field to highlight on the UI
      cl_abap_unit_assert=>assert_equals( exp = if_abap_behv=>mk-on
                                          act = message_line-%element-CustomerID ).
    ENDLOOP.
  ENDMETHOD.

  METHOD validatecustomer_initial.
    DATA travel_mock_data TYPE tt_travel_db.
    DATA travels_to_test  TYPE TABLE FOR VALIDATION zrap_r_travel_###\\Travel~validateCustomer.
    DATA failed           TYPE RESPONSE FOR FAILED LATE zrap_r_travel_###.
    DATA reported         TYPE RESPONSE FOR REPORTED LATE zrap_r_travel_###.

    travel_mock_data = VALUE #( ( travel_id = c_travel_1 ) ).   "no customer
    cds_test_environment->insert_test_data( travel_mock_data ).

    travels_to_test = CORRESPONDING #( travel_mock_data MAPPING TravelID = travel_id EXCEPT * ).

    class_under_test->validatecustomer(
      EXPORTING keys     = travels_to_test
      CHANGING  failed   = failed
                reported = reported ).

    cl_abap_unit_assert=>assert_equals( exp = 1 act = lines( failed-travel ) ).
    cl_abap_unit_assert=>assert_equals( exp = 1 act = count_messages( reported-travel ) ).
    LOOP AT reported-travel INTO DATA(message_line) WHERE %msg IS BOUND.
      assert_message( reported_line = message_line
                      exp_textid    = zcm_rap_###=>enter_customer_id
                      exp_area      = class_under_test->state_area-customer ).
    ENDLOOP.
  ENDMETHOD.

  METHOD validateagency_unknown.
    DATA agency_mock_data TYPE STANDARD TABLE OF /dmo/agency WITH EMPTY KEY.
    DATA travel_mock_data TYPE tt_travel_db.
    DATA travels_to_test  TYPE TABLE FOR VALIDATION zrap_r_travel_###\\Travel~validateAgency.
    DATA failed           TYPE RESPONSE FOR FAILED LATE zrap_r_travel_###.
    DATA reported         TYPE RESPONSE FOR REPORTED LATE zrap_r_travel_###.

    agency_mock_data = VALUE #( ( agency_id = '070001' name = 'Agency 070001' country_code = 'DE' ) ).
    sql_test_environment->insert_test_data( agency_mock_data ).

    travel_mock_data = VALUE #( ( travel_id = c_travel_1 agency_id = '070001' )     "valid
                                ( travel_id = c_travel_2 agency_id = '070099' ) ).  "unknown
    cds_test_environment->insert_test_data( travel_mock_data ).

    travels_to_test = CORRESPONDING #( travel_mock_data MAPPING TravelID = travel_id EXCEPT * ).

    class_under_test->validateagency(
      EXPORTING keys     = travels_to_test
      CHANGING  failed   = failed
                reported = reported ).

    "only travel 2 fails
    cl_abap_unit_assert=>assert_equals( exp = 1 act = lines( failed-travel ) ).
    cl_abap_unit_assert=>assert_equals( exp = c_travel_2 act = failed-travel[ 1 ]-TravelID ).

    "2 state-clearing lines (one per travel) + 1 message
    cl_abap_unit_assert=>assert_equals( exp = 3 act = lines( reported-travel ) ).
    LOOP AT reported-travel INTO DATA(message_line) WHERE %msg IS BOUND.
      cl_abap_unit_assert=>assert_equals( exp = c_travel_2 act = message_line-TravelID ).
      assert_message( reported_line = message_line
                      exp_textid    = zcm_rap_###=>agency_unknown
                      exp_area      = class_under_test->state_area-agency ).
      cl_abap_unit_assert=>assert_equals( exp = if_abap_behv=>mk-on
                                          act = message_line-%element-AgencyID ).
    ENDLOOP.
  ENDMETHOD.

  METHOD validatedates_table.
    TYPES: BEGIN OF ty_case,
             travel_id   TYPE /dmo/travel_id,
             begin_date  TYPE /dmo/begin_date,
             end_date    TYPE /dmo/end_date,
             exp_failed  TYPE i,
             exp_textid  TYPE scx_t100key,
             description TYPE string,
           END OF ty_case.
    DATA cases            TYPE STANDARD TABLE OF ty_case WITH EMPTY KEY.
    DATA travel_mock_data TYPE tt_travel_db.
    DATA travels_to_test  TYPE TABLE FOR VALIDATION zrap_r_travel_###\\Travel~validateDates.
    DATA failed           TYPE RESPONSE FOR FAILED LATE zrap_r_travel_###.
    DATA reported         TYPE RESPONSE FOR REPORTED LATE zrap_r_travel_###.

    DATA(today) = cl_abap_context_info=>get_system_date( ).

    cases = VALUE #(
      ( travel_id = '00000001'                        end_date = today + 5
        exp_failed = 1 exp_textid = zcm_rap_###=>enter_dates               description = `begin initial` )
      ( travel_id = '00000002' begin_date = today + 5
        exp_failed = 1 exp_textid = zcm_rap_###=>enter_dates               description = `end initial` )
      ( travel_id = '00000003' begin_date = today + 9 end_date = today + 5
        exp_failed = 1 exp_textid = zcm_rap_###=>begin_date_after_end_date description = `begin > end` )
      ( travel_id = '00000004' begin_date = today - 1 end_date = today + 5
        exp_failed = 1 exp_textid = zcm_rap_###=>begin_date_in_past        description = `begin in past` )
      ( travel_id = '00000005' begin_date = today     end_date = today
        exp_failed = 0                                                     description = `one-day trip today` )
      ( travel_id = '00000006' begin_date = today + 1 end_date = today + 10
        exp_failed = 0                                                     description = `normal trip` ) ).

    travel_mock_data = CORRESPONDING #( cases ).
    cds_test_environment->insert_test_data( travel_mock_data ).
    travels_to_test = CORRESPONDING #( travel_mock_data MAPPING TravelID = travel_id EXCEPT * ).

    class_under_test->validatedates(
      EXPORTING keys     = travels_to_test
      CHANGING  failed   = failed
                reported = reported ).

    "check every case separately and keep going after a failed check (quit-no)
    LOOP AT cases INTO DATA(case).
      DATA(failed_count) = REDUCE i( INIT n = 0
                                     FOR f IN failed-travel WHERE ( TravelID = case-travel_id )
                                     NEXT n = n + 1 ).
      cl_abap_unit_assert=>assert_equals( exp  = case-exp_failed
                                          act  = failed_count
                                          quit = if_abap_unit_constant=>quit-no
                                          msg  = |failed lines for case '{ case-description }'| ).

      LOOP AT reported-travel INTO DATA(message_line)
           WHERE TravelID = case-travel_id AND %msg IS BOUND.
        DATA(message) = CAST zcm_rap_###( message_line-%msg ).
        cl_abap_unit_assert=>assert_equals( exp  = case-exp_textid
                                            act  = message->if_t100_message~t100key
                                            quit = if_abap_unit_constant=>quit-no
                                            msg  = |message for case '{ case-description }'| ).
      ENDLOOP.
      IF sy-subrc <> 0 AND case-exp_failed > 0.
        cl_abap_unit_assert=>fail( msg  = |no message for case '{ case-description }'|
                                   quit = if_abap_unit_constant=>quit-no ).
      ENDIF.
    ENDLOOP.

    "every travel gets exactly one state-clearing line
    cl_abap_unit_assert=>assert_equals(
      exp = lines( cases )
      act = lines( reported-travel ) - count_messages( reported-travel ) ).
  ENDMETHOD.
```

**왜 이렇게 쓰나**
- R-02 검증은 메시지를 쓰기 전에 그 state area의 **지우기 줄**(메시지 없는 줄)을 먼저 넣습니다. 그래서 성공해도 `reported`가 비어 있지 않습니다. `reported`를 `assert_initial`로 검사하면 성공 테스트가 실패합니다. 참조 시나리오도 성공 시 `lines( reported-travel ) = 1`을 기대합니다.
- 메시지 비교는 텍스트가 아니라 **T100 키**로 합니다. 텍스트는 번역·문구 수정으로 바뀌지만 키는 바뀌지 않습니다. `%msg`의 정적 타입은 `IF_ABAP_BEHV_MESSAGE`라서 `CAST zcm_rap_###`로 내려야 `if_t100_message~t100key`가 보입니다. `zcm_rap_###=>customer_unknown` 같은 상수 자체가 `scx_t100key` 타입이므로 그대로 `exp`에 넣습니다.
- `quit = if_abap_unit_constant=>quit-no`는 단언이 실패해도 메서드를 멈추지 않고 다음 경우를 계속 검사하게 합니다. 표 기반 테스트에서 한 번에 모든 실패를 보려면 필요합니다.
- 검증은 저장 단계(early save)에서 돌기 때문에 응답 타입이 `FAILED LATE`/`REPORTED LATE`입니다. `failed` 줄에는 `%fail-cause`를 넣지 않는 것이 검증의 관례입니다(실패 이유는 메시지가 설명합니다).

**자주 나는 오류와 해결**
- `assert_message`의 파라미터 타입 `STRUCTURE FOR REPORTED LATE ...\\Travel`, `count_messages`의 `TABLE FOR REPORTED LATE ...\\Travel`이 활성화되지 않으면, 클래스 앞부분에 `TYPES ty_reported_late TYPE RESPONSE FOR REPORTED LATE zrap_r_travel_###.`를 두고 `TYPE ty_reported_late-travel`(표), `TYPE LINE OF ty_reported_late-travel`(줄)로 바꿔 보세요. 엔터티 단위 응답 타입의 정확한 표기는 실제 시스템에서 확인 필요입니다.
- `CAST zcm_rap_###`에서 `CX_SY_MOVE_CAST_ERROR` 덤프: 그 메시지가 `ZCM_RAP_###`가 아닌 다른 클래스(예: 프레임워크 메시지)로 만들어졌습니다. 그 줄의 `%msg`를 디버거로 보세요.

**클래스 구조 해설**
- `TABLE FOR VALIDATION zrap_r_travel_###\\Travel~validateCustomer`는 BDEF의 `validation validateCustomer on save { ... }`에서 생깁니다. 키만 들어 있습니다(검증은 데이터를 직접 읽어야 함).
- 실제로는 프레임워크가 `COMMIT ENTITIES`나 `Prepare`/`Activate` 때 트리거 조건(`create; field CustomerID;`)이 맞는 인스턴스만 모아 호출합니다. 단위 테스트는 트리거 조건과 무관하게 "주어진 키에 대해 올바른 판정을 하는가"만 봅니다.

</details>

#### 3단계. 결정·액션·함수 테스트: 결과(%param), 버퍼 변화, 연쇄 결정

요구사항
1. 테스트 메서드를 추가하세요.
   - `accepttravel_sets_status`: 상태 `O`인 Travel. `acceptTravel` 호출 뒤 `failed`가 비어 있고, `result` 1줄의 `%param-OverallStatus = 'A'`, 다시 읽은 상태도 `A`. `reported`에는 오류가 없고 성공 메시지(`zcm_rap_###=>travel_accepted`) 1개.
   - `rejecttravel_sets_status`: 같은 방식, 상태 `X`.
   - `deductdiscount_invalid_param`: 할인율 `0`과 `150`. 기대: `failed-travel` 2줄, `reported-travel` 2줄(모두 `discount_invalid`, `%op-%action-deductDiscount` 켜짐), `result` 비어 있음.
   - `deductdiscount_success`: 수수료 `100.00 EUR`, Booking 없음, 할인 10%. 기대: `result[ 1 ]-%param-BookingFee = '90.00'`, 다시 읽은 `TotalPrice = '90.00'`(BookingFee가 바뀌어 결정 `calculateTotalPrice`가 연쇄 실행됨).
   - `recalctotalprice_one_currency`: 수수료 `10 EUR`, Booking 2건(`100 EUR`, `200 EUR`). 내부 액션 `reCalcTotalPrice` 호출 뒤 `TotalPrice = 310`.
   - `getdefaults_discount`: 총액 `4999.99`이면 기본 할인율 10, `5000`이면 20.
2. 메시지 심각도별 개수를 세는 헬퍼 `count_by_severity`(입력: `RESPONSE FOR REPORTED EARLY`의 Travel 표, 심각도)를 추가하세요.

**확인** 모든 테스트가 초록색입니다. `deductdiscount_success`에서 `TotalPrice`가 0이면 결정이 연쇄 실행되지 않은 것입니다. 이때는 BDEF의 `determination calculateTotalPrice on modify { create; field BookingFee, CurrencyCode; }`를 확인하세요.

<details><summary>정답·해설</summary>

정의부 테스트 목록에 추가:

```abap
    METHODS accepttravel_sets_status      FOR TESTING.
    METHODS rejecttravel_sets_status      FOR TESTING.
    METHODS deductdiscount_invalid_param  FOR TESTING.
    METHODS deductdiscount_success        FOR TESTING.
    METHODS recalctotalprice_one_currency FOR TESTING.
    METHODS getdefaults_discount          FOR TESTING.

    METHODS count_by_severity
      IMPORTING reported_tab TYPE TABLE FOR REPORTED EARLY zrap_r_travel_###\\Travel
                severity     TYPE if_abap_behv_message=>t_severity
      RETURNING VALUE(count) TYPE i.
```

구현부에 추가:

```abap
  METHOD count_by_severity.
    LOOP AT reported_tab INTO DATA(line) WHERE %msg IS BOUND.
      IF line-%msg->m_severity = severity.
        count += 1.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.


  METHOD accepttravel_sets_status.
    DATA travel_mock_data TYPE tt_travel_db.
    DATA travels_to_test  TYPE TABLE FOR ACTION IMPORT zrap_r_travel_###\\Travel~acceptTravel.
    DATA result           TYPE TABLE FOR ACTION RESULT zrap_r_travel_###\\Travel~acceptTravel.
    DATA mapped           TYPE RESPONSE FOR MAPPED EARLY zrap_r_travel_###.
    DATA failed           TYPE RESPONSE FOR FAILED EARLY zrap_r_travel_###.
    DATA reported         TYPE RESPONSE FOR REPORTED EARLY zrap_r_travel_###.

    travel_mock_data = VALUE #( ( travel_id = c_travel_1
                                  overall_status = class_under_test->travel_status-open ) ).
    cds_test_environment->insert_test_data( travel_mock_data ).
    travels_to_test = CORRESPONDING #( travel_mock_data MAPPING TravelID = travel_id EXCEPT * ).

    class_under_test->accepttravel(
      EXPORTING keys     = travels_to_test
      CHANGING  result   = result
                mapped   = mapped
                failed   = failed
                reported = reported ).

    cl_abap_unit_assert=>assert_initial( act = failed msg = 'failed' ).
    cl_abap_unit_assert=>assert_initial( act = mapped msg = 'an action on $self maps nothing' ).

    "result [1] $self: one line per key, %param = the whole instance after the change
    cl_abap_unit_assert=>assert_equals( exp = 1 act = lines( result ) ).
    cl_abap_unit_assert=>assert_equals( exp = c_travel_1 act = result[ 1 ]-TravelID ).
    cl_abap_unit_assert=>assert_equals( exp = class_under_test->travel_status-accepted
                                        act = result[ 1 ]-%param-OverallStatus ).

    "success message, but no error
    cl_abap_unit_assert=>assert_equals(
      exp = 0
      act = count_by_severity( reported_tab = reported-travel
                               severity     = if_abap_behv_message=>severity-error ) ).
    cl_abap_unit_assert=>assert_equals(
      exp = 1
      act = count_by_severity( reported_tab = reported-travel
                               severity     = if_abap_behv_message=>severity-success ) ).
    DATA(message) = CAST zcm_rap_###( reported-travel[ 1 ]-%msg ).
    cl_abap_unit_assert=>assert_equals( exp = zcm_rap_###=>travel_accepted
                                        act = message->if_t100_message~t100key ).

    "the buffer really changed
    READ ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        FIELDS ( OverallStatus ) WITH CORRESPONDING #( travels_to_test )
      RESULT DATA(read_result).
    cl_abap_unit_assert=>assert_equals( exp = class_under_test->travel_status-accepted
                                        act = read_result[ 1 ]-OverallStatus ).
  ENDMETHOD.

  METHOD rejecttravel_sets_status.
    DATA travel_mock_data TYPE tt_travel_db.
    DATA travels_to_test  TYPE TABLE FOR ACTION IMPORT zrap_r_travel_###\\Travel~rejectTravel.
    DATA result           TYPE TABLE FOR ACTION RESULT zrap_r_travel_###\\Travel~rejectTravel.
    DATA mapped           TYPE RESPONSE FOR MAPPED EARLY zrap_r_travel_###.
    DATA failed           TYPE RESPONSE FOR FAILED EARLY zrap_r_travel_###.
    DATA reported         TYPE RESPONSE FOR REPORTED EARLY zrap_r_travel_###.

    travel_mock_data = VALUE #( ( travel_id = c_travel_1
                                  overall_status = class_under_test->travel_status-open ) ).
    cds_test_environment->insert_test_data( travel_mock_data ).
    travels_to_test = CORRESPONDING #( travel_mock_data MAPPING TravelID = travel_id EXCEPT * ).

    class_under_test->rejecttravel(
      EXPORTING keys     = travels_to_test
      CHANGING  result   = result
                mapped   = mapped
                failed   = failed
                reported = reported ).

    cl_abap_unit_assert=>assert_initial( act = failed ).
    cl_abap_unit_assert=>assert_equals( exp = class_under_test->travel_status-rejected
                                        act = result[ 1 ]-%param-OverallStatus ).
    cl_abap_unit_assert=>assert_equals(
      exp = 0
      act = count_by_severity( reported_tab = reported-travel
                               severity     = if_abap_behv_message=>severity-error ) ).
  ENDMETHOD.

  METHOD deductdiscount_invalid_param.
    DATA travels_to_test TYPE TABLE FOR ACTION IMPORT zrap_r_travel_###\\Travel~deductDiscount.
    DATA result          TYPE TABLE FOR ACTION RESULT zrap_r_travel_###\\Travel~deductDiscount.
    DATA mapped          TYPE RESPONSE FOR MAPPED EARLY zrap_r_travel_###.
    DATA failed          TYPE RESPONSE FOR FAILED EARLY zrap_r_travel_###.
    DATA reported        TYPE RESPONSE FOR REPORTED EARLY zrap_r_travel_###.

    "the parameter check happens before any read - no test data needed
    travels_to_test = VALUE #( %is_draft = if_abap_behv=>mk-off
                               ( TravelID = c_travel_1  %param-discount_percent = 0 )
                               ( TravelID = c_travel_2  %param-discount_percent = 150 ) ).

    class_under_test->deductdiscount(
      EXPORTING keys     = travels_to_test
      CHANGING  result   = result
                mapped   = mapped
                failed   = failed
                reported = reported ).

    cl_abap_unit_assert=>assert_initial( act = result msg = 'no result for invalid input' ).
    cl_abap_unit_assert=>assert_equals( exp = 2 act = lines( failed-travel ) ).
    cl_abap_unit_assert=>assert_equals( exp = 2 act = lines( reported-travel ) ).

    LOOP AT reported-travel INTO DATA(message_line).
      DATA(message) = CAST zcm_rap_###( message_line-%msg ).
      cl_abap_unit_assert=>assert_equals( exp = zcm_rap_###=>discount_invalid
                                          act = message->if_t100_message~t100key ).
      "the message belongs to the action call (shown in the action dialog)
      cl_abap_unit_assert=>assert_equals( exp = if_abap_behv=>mk-on
                                          act = message_line-%op-%action-deductDiscount ).
    ENDLOOP.
  ENDMETHOD.

  METHOD deductdiscount_success.
    DATA travel_mock_data TYPE tt_travel_db.
    DATA travels_to_test  TYPE TABLE FOR ACTION IMPORT zrap_r_travel_###\\Travel~deductDiscount.
    DATA result           TYPE TABLE FOR ACTION RESULT zrap_r_travel_###\\Travel~deductDiscount.
    DATA mapped           TYPE RESPONSE FOR MAPPED EARLY zrap_r_travel_###.
    DATA failed           TYPE RESPONSE FOR FAILED EARLY zrap_r_travel_###.
    DATA reported         TYPE RESPONSE FOR REPORTED EARLY zrap_r_travel_###.

    travel_mock_data = VALUE #( ( travel_id = c_travel_1  booking_fee = '100.00'  currency_code = 'EUR' ) ).
    cds_test_environment->insert_test_data( travel_mock_data ).

    travels_to_test = VALUE #( ( TravelID = c_travel_1  %param-discount_percent = 10 ) ).

    class_under_test->deductdiscount(
      EXPORTING keys     = travels_to_test
      CHANGING  result   = result
                mapped   = mapped
                failed   = failed
                reported = reported ).

    cl_abap_unit_assert=>assert_initial( act = failed ).
    cl_abap_unit_assert=>assert_initial( act = reported ).
    cl_abap_unit_assert=>assert_equals( exp = CONV /dmo/booking_fee( '90.00' )
                                        act = result[ 1 ]-%param-BookingFee ).

    "BookingFee changed -> determination calculateTotalPrice -> reCalcTotalPrice ran as well
    READ ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        FIELDS ( BookingFee TotalPrice ) WITH CORRESPONDING #( travels_to_test )
      RESULT DATA(read_result).
    cl_abap_unit_assert=>assert_equals( exp = CONV /dmo/total_price( '90.00' )
                                        act = read_result[ 1 ]-TotalPrice ).
  ENDMETHOD.

  METHOD recalctotalprice_one_currency.
    DATA travel_mock_data  TYPE tt_travel_db.
    DATA booking_mock_data TYPE tt_booking_db.
    DATA travels_to_test   TYPE TABLE FOR ACTION IMPORT zrap_r_travel_###\\Travel~reCalcTotalPrice.
    DATA mapped            TYPE RESPONSE FOR MAPPED EARLY zrap_r_travel_###.
    DATA failed            TYPE RESPONSE FOR FAILED EARLY zrap_r_travel_###.
    DATA reported          TYPE RESPONSE FOR REPORTED EARLY zrap_r_travel_###.

    travel_mock_data = VALUE #( ( travel_id = c_travel_1  booking_fee = '10.00'  currency_code = 'EUR' ) ).
    cds_test_environment->insert_test_data( travel_mock_data ).

    booking_mock_data = VALUE #( travel_id = c_travel_1  currency_code = 'EUR'
                                 ( booking_id = '0010'  flight_price = '100.00' )
                                 ( booking_id = '0020'  flight_price = '200.00' ) ).
    cds_test_environment->insert_test_data( booking_mock_data ).

    travels_to_test = VALUE #( ( %is_draft = if_abap_behv=>mk-off  TravelID = c_travel_1 ) ).

    "internal action: no result parameter
    class_under_test->recalctotalprice(
      EXPORTING keys     = travels_to_test
      CHANGING  mapped   = mapped
                failed   = failed
                reported = reported ).

    cl_abap_unit_assert=>assert_initial( act = failed ).

    READ ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        FIELDS ( TotalPrice CurrencyCode ) WITH CORRESPONDING #( travels_to_test )
      RESULT DATA(read_result).
    cl_abap_unit_assert=>assert_equals( exp = CONV /dmo/total_price( '310.00' )
                                        act = read_result[ 1 ]-TotalPrice ).
  ENDMETHOD.

  METHOD getdefaults_discount.
    DATA travel_mock_data TYPE tt_travel_db.
    DATA travels_to_test  TYPE TABLE FOR FUNCTION IMPORT zrap_r_travel_###\\Travel~GetDefaultsFordeductDiscount.
    DATA result           TYPE TABLE FOR FUNCTION RESULT zrap_r_travel_###\\Travel~GetDefaultsFordeductDiscount.
    DATA failed           TYPE RESPONSE FOR FAILED EARLY zrap_r_travel_###.
    DATA reported         TYPE RESPONSE FOR REPORTED EARLY zrap_r_travel_###.

    travel_mock_data = VALUE #( currency_code = 'EUR'
                                ( travel_id = c_travel_1  total_price = '4999.99' )
                                ( travel_id = c_travel_2  total_price = '5000.00' ) ).
    cds_test_environment->insert_test_data( travel_mock_data ).
    travels_to_test = CORRESPONDING #( travel_mock_data MAPPING TravelID = travel_id EXCEPT * ).

    class_under_test->getdefaultsfordeductdiscount(
      EXPORTING keys     = travels_to_test
      CHANGING  result   = result
                failed   = failed
                reported = reported ).

    cl_abap_unit_assert=>assert_initial( act = failed ).
    SORT result BY TravelID.
    cl_abap_unit_assert=>assert_equals( exp = 10 act = result[ 1 ]-%param-discount_percent ).
    cl_abap_unit_assert=>assert_equals( exp = 20 act = result[ 2 ]-%param-discount_percent ).
  ENDMETHOD.
```

**왜 이렇게 쓰나**
- 액션 테스트는 **세 가지**를 봅니다: 응답(`failed`/`reported`), 결과(`result`의 `%param`), 그리고 버퍼에 남은 변화(다시 읽기). 결과만 보면 "결과는 맞게 만들었지만 실제로는 바꾸지 않은" 버그를 놓칩니다.
- 핸들러 안의 `MODIFY ENTITIES ... IN LOCAL MODE`는 진짜 트랜잭션 버퍼를 바꿉니다. 그래서 바꾼 필드에 걸린 결정(`calculateTotalPrice`)도 실제로 연쇄 실행됩니다. 참조 시나리오의 `deductdiscount_success`도 할인 뒤 총액까지 기대값에 넣습니다. 이런 연쇄를 막고 메서드 하나만 보고 싶으면 5단계의 EML 스텁을 씁니다.
- `acceptTravel`은 성공 메시지를 남기므로 `reported`가 비어 있지 않습니다. "오류가 없다"는 것은 심각도로 세어 검사합니다.
- 금액 비교는 `CONV /dmo/total_price( '310.00' )`처럼 같은 타입으로 맞춥니다. 문자 리터럴 `'310'`과 바로 비교하면 타입 변환 규칙 때문에 의도와 다른 결과가 나올 수 있습니다.
- 통화가 섞인 경우(`USD` Booking)는 `/DMO/CL_FLIGHT_AMDP=>convert_currency`가 환율 테이블을 읽으므로 그 테이블까지 더블로 바꿔야 합니다. 여기서는 통화 하나만 검사합니다.

**자주 나는 오류와 해결**
- `deductdiscount_invalid_param`에서 `%param-discount_percent = 150` 대입 오류: `ZRAP_A_DISCOUNT_###`의 `discount_percent`가 `abap.int1`(0~255)이어야 합니다.
- `result[ 1 ]`에서 `CX_SY_ITAB_LINE_NOT_FOUND`: 액션이 `failed`를 채우고 결과를 만들지 않았습니다. 먼저 `failed`를 디버거로 보세요(대개 `%fail-cause = not_found`, 테스트 데이터 삽입 누락).

**클래스 구조 해설**
- `ACTION IMPORT`/`ACTION RESULT` 타입은 BDEF의 `action ... result [1] $self` 한 줄에서, `%param`의 구조는 `parameter ZRAP_A_DISCOUNT_###`(입력)와 `$self`(결과)에서 생깁니다. `internal action reCalcTotalPrice;`처럼 결과가 없으면 `result` 파라미터도 없습니다.
- 기본값 함수 `GetDefaultsFordeductDiscount`는 `FOR READ ... FOR FUNCTION`이라 `mapped`가 없습니다. Fiori가 액션 대화 상자를 열 때 프레임워크가 부릅니다.

</details>


#### 4단계. 기능 제어와 권한 테스트: 인스턴스·전역, 권한 검사 통제

요구사항
1. `ltc_travel_handler`에 테스트 메서드를 추가하세요.
   - `instance_features_by_status`: 상태 `O`, `A`, `X`인 Travel 3건. R-03 `get_instance_features`의 규칙대로 `%field-BookingFee`, `%features-%update`, `%features-%delete`, `%action-Edit`, `%action-acceptTravel`, `%action-rejectTravel`, `%action-deductDiscount`, `%assoc-_Booking` 값을 경우마다 비교합니다. 기대값은 상태·항목·기대값을 담은 표로 만듭니다.
   - `global_features_create_closed`: `ZRAP_CTRL_###` 더블에 `ctrl_id = 'TRAVEL'`, `create_closed = abap_true`인 줄을 넣으면 `%create`와 `%action-createTravel`이 `fc-o-disabled`. 줄이 없으면 둘 다 `fc-o-enabled`.
   - `global_authorizations_allowed`: `c_use_real_auth = abap_false`(시뮬레이션)일 때 `%create`, `%update`, `%delete`, `%action-Edit`, `%action-createTravel`이 모두 `auth-allowed`이고 `reported`가 비어 있음.
   - `instance_auth_deny_country`: 스위치 테이블의 `deny_country = 'US'`. 여행사 `070001`(DE)의 Travel 1은 허용, 여행사 `070002`(US)의 Travel 2는 `%update`, `%delete`, `%action-Edit`, `%action-copyTravel`이 모두 `auth-unauthorized`이고 메시지 `not_authorized_country` 1개.
   - `update_auth_restricted`: ABAP Unit의 권한 검사 제어기(`cl_aunit_authority_check`)로 이 사용자의 `/DMO/TRVL` 권한을 "국가 DE, 활동 03(조회)만"으로 **제한**한 뒤 `is_update_granted( 'DE' )`가 `abap_false`인지 확인합니다. `c_use_real_auth = abap_false`이면(시뮬레이션) 아무것도 검사하지 않고 끝냅니다.
2. 테스트가 끝나면 권한 제어기를 `reset( )`해 다른 테스트에 영향을 주지 않게 하세요.

**확인** 5개 테스트가 초록색입니다. R-03 스위치 클래스로 실제 `ZRAP_CTRL_###`에 `create_closed = 'X'`를 넣어 둔 상태에서도 `global_features_create_closed`의 "줄 없음" 부분이 통과해야 합니다(더블을 쓰므로 실제 테이블 값과 무관).

<details><summary>정답·해설</summary>

정의부 테스트 목록에 추가:

```abap
    METHODS instance_features_by_status   FOR TESTING.
    METHODS global_features_create_closed FOR TESTING.
    METHODS global_authorizations_allowed FOR TESTING.
    METHODS instance_auth_deny_country    FOR TESTING.
    METHODS update_auth_restricted        FOR TESTING RAISING cx_static_check.
```

구현부에 추가:

```abap
  METHOD instance_features_by_status.
    TYPES: BEGIN OF ty_expected,
             travel_id      TYPE /dmo/travel_id,
             status         TYPE /dmo/overall_status,
             booking_fee    TYPE if_abap_behv=>t_xflag,
             update         TYPE if_abap_behv=>t_xflag,
             delete         TYPE if_abap_behv=>t_xflag,
             edit           TYPE if_abap_behv=>t_xflag,
             accept         TYPE if_abap_behv=>t_xflag,
             reject         TYPE if_abap_behv=>t_xflag,
             discount       TYPE if_abap_behv=>t_xflag,
             create_booking TYPE if_abap_behv=>t_xflag,
           END OF ty_expected.
    DATA expected           TYPE STANDARD TABLE OF ty_expected WITH EMPTY KEY.
    DATA travel_mock_data   TYPE tt_travel_db.
    DATA travels_to_test    TYPE TABLE FOR INSTANCE FEATURES KEY zrap_r_travel_###\\Travel.
    DATA requested_features TYPE STRUCTURE FOR INSTANCE FEATURES REQUEST zrap_r_travel_###\\Travel.
    DATA result             TYPE TABLE FOR INSTANCE FEATURES RESULT zrap_r_travel_###\\Travel.
    DATA failed             TYPE RESPONSE FOR FAILED EARLY zrap_r_travel_###.
    DATA reported           TYPE RESPONSE FOR REPORTED EARLY zrap_r_travel_###.

    CONSTANTS:
      on  TYPE if_abap_behv=>t_xflag VALUE if_abap_behv=>fc-o-enabled,
      off TYPE if_abap_behv=>t_xflag VALUE if_abap_behv=>fc-o-disabled,
      rw  TYPE if_abap_behv=>t_xflag VALUE if_abap_behv=>fc-f-unrestricted,
      ro  TYPE if_abap_behv=>t_xflag VALUE if_abap_behv=>fc-f-read_only.

    expected = VALUE #(
      "              BookingFee update delete Edit accept reject discount _Booking
      ( travel_id = c_travel_1 status = 'O'
        booking_fee = rw update = on  delete = on  edit = on  accept = on  reject = on  discount = on  create_booking = on )
      ( travel_id = c_travel_2 status = 'A'
        booking_fee = ro update = off delete = off edit = off accept = off reject = on  discount = off create_booking = on )
      ( travel_id = c_travel_3 status = 'X'
        booking_fee = ro update = on  delete = on  edit = on  accept = on  reject = off discount = off create_booking = off ) ).

    travel_mock_data = VALUE #( FOR e IN expected ( travel_id = e-travel_id overall_status = e-status ) ).
    cds_test_environment->insert_test_data( travel_mock_data ).
    travels_to_test = CORRESPONDING #( travel_mock_data MAPPING TravelID = travel_id EXCEPT * ).

    "the implementation always fills everything - an empty request is enough
    class_under_test->get_instance_features(
      EXPORTING keys               = travels_to_test
                requested_features = requested_features
      CHANGING  result             = result
                failed             = failed
                reported           = reported ).

    cl_abap_unit_assert=>assert_initial( act = failed ).
    cl_abap_unit_assert=>assert_equals( exp = lines( expected ) act = lines( result ) ).

    "compare item by item: other components (added later) do not break the test
    LOOP AT expected INTO DATA(exp).
      DATA(act) = result[ TravelID = exp-travel_id ].
      DATA(case) = |status { exp-status }|.
      cl_abap_unit_assert=>assert_equals( exp = exp-booking_fee act = act-%field-BookingFee
                                          quit = if_abap_unit_constant=>quit-no msg = |{ case }: BookingFee| ).
      cl_abap_unit_assert=>assert_equals( exp = exp-update act = act-%features-%update
                                          quit = if_abap_unit_constant=>quit-no msg = |{ case }: update| ).
      cl_abap_unit_assert=>assert_equals( exp = exp-delete act = act-%features-%delete
                                          quit = if_abap_unit_constant=>quit-no msg = |{ case }: delete| ).
      cl_abap_unit_assert=>assert_equals( exp = exp-edit act = act-%action-Edit
                                          quit = if_abap_unit_constant=>quit-no msg = |{ case }: Edit| ).
      cl_abap_unit_assert=>assert_equals( exp = exp-accept act = act-%action-acceptTravel
                                          quit = if_abap_unit_constant=>quit-no msg = |{ case }: acceptTravel| ).
      cl_abap_unit_assert=>assert_equals( exp = exp-reject act = act-%action-rejectTravel
                                          quit = if_abap_unit_constant=>quit-no msg = |{ case }: rejectTravel| ).
      cl_abap_unit_assert=>assert_equals( exp = exp-discount act = act-%action-deductDiscount
                                          quit = if_abap_unit_constant=>quit-no msg = |{ case }: deductDiscount| ).
      cl_abap_unit_assert=>assert_equals( exp = exp-create_booking act = act-%assoc-_Booking
                                          quit = if_abap_unit_constant=>quit-no msg = |{ case }: _Booking| ).
    ENDLOOP.
  ENDMETHOD.

  METHOD global_features_create_closed.
    "Types of the global feature control (no keys -> structures, not tables)
    DATA requested_features TYPE STRUCTURE FOR GLOBAL FEATURES REQUEST zrap_r_travel_###\\Travel.
    DATA result             TYPE STRUCTURE FOR GLOBAL FEATURES RESULT zrap_r_travel_###\\Travel.
    DATA reported           TYPE RESPONSE FOR REPORTED EARLY zrap_r_travel_###.
    DATA ctrl_mock_data     TYPE STANDARD TABLE OF zrap_ctrl_### WITH EMPTY KEY.

    requested_features = VALUE #( %create              = if_abap_behv=>mk-on
                                  %action-createTravel = if_abap_behv=>mk-on ).

    "1) no switch row -> open
    class_under_test->get_global_features(
      EXPORTING requested_features = requested_features
      CHANGING  result             = result
                reported           = reported ).
    cl_abap_unit_assert=>assert_equals( exp = if_abap_behv=>fc-o-enabled act = result-%create ).
    cl_abap_unit_assert=>assert_equals( exp = if_abap_behv=>fc-o-enabled act = result-%action-createTravel ).

    "2) switch row 'closed' -> create and createTravel disabled
    ctrl_mock_data = VALUE #( ( ctrl_id = class_under_test->c_ctrl_id create_closed = abap_true ) ).
    sql_test_environment->insert_test_data( ctrl_mock_data ).
    CLEAR result.

    class_under_test->get_global_features(
      EXPORTING requested_features = requested_features
      CHANGING  result             = result
                reported           = reported ).
    cl_abap_unit_assert=>assert_equals( exp = if_abap_behv=>fc-o-disabled act = result-%create ).
    cl_abap_unit_assert=>assert_equals( exp = if_abap_behv=>fc-o-disabled act = result-%action-createTravel ).
  ENDMETHOD.

  METHOD global_authorizations_allowed.
    DATA requested_authorizations TYPE STRUCTURE FOR GLOBAL AUTHORIZATION REQUEST zrap_r_travel_###\\Travel.
    DATA result                   TYPE STRUCTURE FOR GLOBAL AUTHORIZATION RESULT zrap_r_travel_###\\Travel.
    DATA reported                 TYPE RESPONSE FOR REPORTED EARLY zrap_r_travel_###.

    "with real AUTHORITY-CHECKs the outcome depends on the user running the test
    IF class_under_test->c_use_real_auth = abap_true.
      RETURN.
    ENDIF.

    requested_authorizations = VALUE #( %create              = if_abap_behv=>mk-on
                                        %update              = if_abap_behv=>mk-on
                                        %delete              = if_abap_behv=>mk-on
                                        %action-Edit         = if_abap_behv=>mk-on
                                        %action-createTravel = if_abap_behv=>mk-on ).

    class_under_test->get_global_authorizations(
      EXPORTING requested_authorizations = requested_authorizations
      CHANGING  result                   = result
                reported                 = reported ).

    cl_abap_unit_assert=>assert_initial( act = reported ).
    cl_abap_unit_assert=>assert_equals(
      exp = VALUE #( BASE result
                     %create              = if_abap_behv=>auth-allowed
                     %update              = if_abap_behv=>auth-allowed
                     %delete              = if_abap_behv=>auth-allowed
                     %action-Edit         = if_abap_behv=>auth-allowed
                     %action-createTravel = if_abap_behv=>auth-allowed )
      act = result ).
  ENDMETHOD.

  METHOD instance_auth_deny_country.
    DATA ctrl_mock_data           TYPE STANDARD TABLE OF zrap_ctrl_### WITH EMPTY KEY.
    DATA agency_view_mock_data    TYPE STANDARD TABLE OF /dmo/i_agency WITH EMPTY KEY.
    DATA travel_mock_data         TYPE tt_travel_db.
    DATA travels_to_test          TYPE TABLE FOR AUTHORIZATION KEY zrap_r_travel_###\\Travel.
    DATA requested_authorizations TYPE STRUCTURE FOR AUTHORIZATION REQUEST zrap_r_travel_###\\Travel.
    DATA result                   TYPE TABLE FOR AUTHORIZATION RESULT zrap_r_travel_###\\Travel.
    DATA failed                   TYPE RESPONSE FOR FAILED EARLY zrap_r_travel_###.
    DATA reported                 TYPE RESPONSE FOR REPORTED EARLY zrap_r_travel_###.

    IF class_under_test->c_use_real_auth = abap_true.
      RETURN.                    "this test checks the trial simulation only
    ENDIF.

    ctrl_mock_data = VALUE #( ( ctrl_id = class_under_test->c_ctrl_id deny_country = 'US' ) ).
    sql_test_environment->insert_test_data( ctrl_mock_data ).

    agency_view_mock_data = VALUE #( ( AgencyID = '070001' CountryCode = 'DE' )
                                     ( AgencyID = '070002' CountryCode = 'US' ) ).
    sql_test_environment->insert_test_data( agency_view_mock_data ).

    travel_mock_data = VALUE #( ( travel_id = c_travel_1 agency_id = '070001' )
                                ( travel_id = c_travel_2 agency_id = '070002' ) ).
    cds_test_environment->insert_test_data( travel_mock_data ).
    travels_to_test = CORRESPONDING #( travel_mock_data MAPPING TravelID = travel_id EXCEPT * ).

    requested_authorizations = VALUE #( %update            = if_abap_behv=>mk-on
                                        %delete            = if_abap_behv=>mk-on
                                        %action-Edit       = if_abap_behv=>mk-on
                                        %action-copyTravel = if_abap_behv=>mk-on ).

    class_under_test->get_instance_authorizations(
      EXPORTING keys                     = travels_to_test
                requested_authorizations = requested_authorizations
      CHANGING  result                   = result
                failed                   = failed
                reported                 = reported ).

    cl_abap_unit_assert=>assert_initial( act = failed ).

    DATA(allowed) = result[ TravelID = c_travel_1 ].
    cl_abap_unit_assert=>assert_equals( exp = if_abap_behv=>auth-allowed act = allowed-%update ).
    cl_abap_unit_assert=>assert_equals( exp = if_abap_behv=>auth-allowed act = allowed-%delete ).

    DATA(denied) = result[ TravelID = c_travel_2 ].
    cl_abap_unit_assert=>assert_equals( exp = if_abap_behv=>auth-unauthorized act = denied-%update ).
    cl_abap_unit_assert=>assert_equals( exp = if_abap_behv=>auth-unauthorized act = denied-%delete ).
    cl_abap_unit_assert=>assert_equals( exp = if_abap_behv=>auth-unauthorized act = denied-%action-Edit ).
    cl_abap_unit_assert=>assert_equals( exp = if_abap_behv=>auth-unauthorized act = denied-%action-copyTravel ).

    cl_abap_unit_assert=>assert_equals( exp = 1 act = lines( reported-travel ) ).
    DATA(message) = CAST zcm_rap_###( reported-travel[ 1 ]-%msg ).
    cl_abap_unit_assert=>assert_equals( exp = zcm_rap_###=>not_authorized_country
                                        act = message->if_t100_message~t100key ).
  ENDMETHOD.

  METHOD update_auth_restricted.
    "only meaningful when R-03 really evaluates AUTHORITY-CHECK
    IF class_under_test->c_use_real_auth = abap_false.
      RETURN.
    ENDIF.

    DATA(auth_controller) = cl_aunit_authority_check=>get_controller( ).

    "the user may only DISPLAY (03) travels of country DE in this test
    DATA(display_de_only) = VALUE cl_aunit_auth_check_types_def=>role_auth_objects(
      ( object         = '/DMO/TRVL'
        authorizations = VALUE #( ( VALUE #(
                           ( fieldname   = 'ACTVT'
                             fieldvalues = VALUE #( ( lower_value = '03' ) ) )
                           ( fieldname   = '/DMO/CNTRY'
                             fieldvalues = VALUE #( ( lower_value = 'DE' ) ) ) ) ) ) ) ).

    DATA(auth_object_set) = cl_aunit_authority_check=>create_auth_object_set(
      VALUE cl_aunit_auth_check_types_def=>user_role_authorizations(
        ( role_authorizations = display_de_only ) ) ).

    auth_controller->restrict_authorizations_to( auth_object_set ).

    "change (02) is not in the restricted set -> not granted
    DATA(granted) = class_under_test->is_update_granted( 'DE' ).

    auth_controller->reset( ).     "never leave the restriction active

    cl_abap_unit_assert=>assert_false( act = granted msg = 'update must not be granted' ).
  ENDMETHOD.
```

**왜 이렇게 쓰나**
- 기능 제어 결과를 표 전체로 비교하면, 나중에 R-03에 새 기능 제어 항목(예: 다른 액션)이 생길 때마다 테스트가 깨집니다. 여기서는 관심 있는 항목만 하나씩 비교해 테스트가 "규칙"만 지키게 했습니다. `%features-%update`와 `%update`는 같은 값을 가리키는 두 경로이므로 R-03 구현과 같은 경로를 씁니다.
- 전역 기능 제어·전역 권한은 키가 없으므로 `STRUCTURE FOR GLOBAL ...` 타입(표가 아님)을 씁니다. 인스턴스 권한은 키별 결과가 표로 옵니다.
- R-03은 트라이얼에서 권한을 줄 수 없어 시뮬레이션(`c_use_real_auth = abap_false`)을 씁니다. 그래서 테스트도 두 갈래입니다. 시뮬레이션은 스위치 테이블(`deny_country`)을 **더블**로 통제해 거부 경로를 검사하고, 실제 권한 경로는 `cl_aunit_authority_check`로 검사합니다.
- `cl_aunit_authority_check`의 제어기는 사용자의 권한을 **줄이기만** 합니다. 새 권한을 주지는 못합니다(cheat sheet 14의 설명). 그래서 "제한했더니 거부된다"는 방향의 테스트만 확실하게 쓸 수 있습니다.
- 테스트 안에서 `reset( )`을 단언보다 먼저 부른 이유: 단언이 실패하면 메서드가 거기서 멈추므로, 뒤에 둔 `reset( )`이 실행되지 않을 수 있습니다.

**자주 나는 오류와 해결**
- `STRUCTURE FOR GLOBAL FEATURES REQUEST`/`RESULT` 타입 이름이나 `get_global_features`에 `reported` 파라미터가 있는지는 로컬 자료로 확인하지 못했습니다(실제 시스템에서 확인 필요). ADT에서 `get_global_features`의 정의에 커서를 두고 F2를 눌러 시그니처를 보고 맞추세요.
- `instance_auth_deny_country`에서 Travel 2도 허용되면 `/DMO/I_AGENCY` 더블이 동작하지 않은 것입니다(CDS 뷰를 SQL 더블에 넣을 수 없는 경우). 그때는 이 테스트를 7단계 통합 테스트로 옮기고 실제 `/DMO/AGENCY` 데이터를 쓰는 방법을 생각해 보세요.
- `if_abap_behv=>t_xflag` 타입을 못 찾으면 `TYPE abp_behv_flag`로 바꿔 보세요(실제 시스템에서 확인 필요). 상수 `fc-o-enabled` 등은 R-03에서 이미 쓰고 있으므로 값 자체는 문제없습니다.

**클래스 구조 해설**
- `INSTANCE FEATURES KEY/REQUEST/RESULT`는 BDEF에서 `features : instance`가 붙은 항목(`update`, `delete`, `field BookingFee`, 액션, `_Booking` 생성, `draft action Edit`)이 있을 때 생기며, 결과 구조에는 그 항목만 들어 있습니다.
- `authorization master ( global, instance )`가 `get_global_authorizations`와 `get_instance_authorizations` 두 메서드를 요구합니다. `authorization : update`로 위임한 액션(`acceptTravel` 등)은 결과에 따로 나오지 않습니다.

</details>

#### 5단계. EML 스텁으로 핸들러만 격리하기: if_abap_behavior_testdouble

요구사항
1. Test Classes 탭에 스텁 클래스 `ltd_travel_stub`(`FOR TESTING`)을 만들고 `if_abap_behavior_testdouble`을 구현하세요.
   - 상태: `instances`(`TABLE FOR READ RESULT zrap_r_travel_###\\Travel`, 스텁이 "가진" 데이터), `updates`(받은 UPDATE 기록), 호출 횟수 `modify_calls`, `read_calls`.
   - `modify`: 엔터티 이름이 `ZRAP_R_TRAVEL_###`이고 연산이 UPDATE인지 단언한 뒤 받은 줄을 `updates`에 쌓고, `%control`이 켜진 `OverallStatus`, `BookingFee`만 `instances`에 반영합니다.
   - `read`: 연산이 READ인지 단언하고 `instances`를 결과에 돌려줍니다.
2. 테스트 클래스 `ltc_travel_stub`(1단계에서 `FRIENDS`에 넣은 이름)을 만드세요. CDS·SQL 더블은 쓰지 않습니다.
   - `setup`에서 `cl_abap_behv_test_environment=>set_test_double( )`로 스텁을 켜고, `teardown`에서 `unset_test_double( )`과 `ROLLBACK ENTITIES`를 합니다.
   - `accept_two_travels`: Travel `42`, `43`을 스텁 데이터로 두고 `acceptTravel`. 기대: 결과 2줄 모두 `A`, 스텁의 `updates` 2줄 모두 `%control-OverallStatus` 켜짐, `modify_calls = 1`, `read_calls = 1`.
   - `discount_without_determination`: 스텁 데이터 Travel `42`(수수료 `100`, 총액 `100`). 10% 할인 뒤 결과의 `BookingFee = 90`이지만 스텁의 `TotalPrice`는 **그대로 100**인지 확인합니다(결정이 돌지 않음 = 메서드만 격리됨).

**확인** 두 테스트가 초록색이고, 3단계의 `deductdiscount_success`(총액 90)와 이 단계의 `discount_without_determination`(총액 100)의 차이를 설명할 수 있어야 합니다.

<details><summary>정답·해설</summary>

Test Classes 탭 아래쪽에 추가(스텁 → 테스트 클래스 순서):

```abap
"! Replaces the whole BO ZRAP_R_TRAVEL_### for READ and MODIFY.
"! Keeps a tiny in-memory 'database' and records what the code under test wrote.
CLASS ltd_travel_stub DEFINITION FOR TESTING.
  PUBLIC SECTION.
    INTERFACES if_abap_behavior_testdouble.

    DATA instances    TYPE TABLE FOR READ RESULT zrap_r_travel_###\\Travel.
    DATA updates      TYPE TABLE FOR UPDATE zrap_r_travel_###\\Travel.
    DATA modify_calls TYPE i.
    DATA read_calls   TYPE i.

    METHODS reset.
ENDCLASS.

CLASS ltd_travel_stub IMPLEMENTATION.

  METHOD reset.
    CLEAR: instances, updates, modify_calls, read_calls.
  ENDMETHOD.

  METHOD if_abap_behavior_testdouble~modify.
    DATA updates_now TYPE TABLE FOR UPDATE zrap_r_travel_###\\Travel.

    LOOP AT changes ASSIGNING FIELD-SYMBOL(<change>).
      modify_calls += 1.
      cl_abap_unit_assert=>assert_equals( exp = 'ZRAP_R_TRAVEL_###' act = <change>-entity_name
                                          msg = 'stub: unexpected entity' ).
      cl_abap_unit_assert=>assert_equals( exp = if_abap_behv=>op-m-update act = <change>-op
                                          msg = 'stub: only UPDATE is simulated' ).

      ASSIGN <change>-instances->* TO FIELD-SYMBOL(<instances>).
      updates_now = <instances>.
      APPEND LINES OF updates_now TO updates.

      "apply only the fields this stub cares about, honoring %control
      LOOP AT updates_now INTO DATA(update).
        ASSIGN instances[ TravelID = update-TravelID ] TO FIELD-SYMBOL(<instance>).
        IF sy-subrc <> 0.
          CONTINUE.
        ENDIF.
        IF update-%control-OverallStatus = if_abap_behv=>mk-on.
          <instance>-OverallStatus = update-OverallStatus.
        ENDIF.
        IF update-%control-BookingFee = if_abap_behv=>mk-on.
          <instance>-BookingFee = update-BookingFee.
        ENDIF.
      ENDLOOP.
    ENDLOOP.
  ENDMETHOD.

  METHOD if_abap_behavior_testdouble~read.
    LOOP AT retrievals ASSIGNING FIELD-SYMBOL(<retrieval>).
      read_calls += 1.
      cl_abap_unit_assert=>assert_equals( exp = if_abap_behv=>op-r-read act = <retrieval>-op
                                          msg = 'stub: only READ is simulated' ).
      "simplification: return everything the stub holds (the tests use matching keys)
      ASSIGN <retrieval>-results->* TO FIELD-SYMBOL(<results>).
      <results> = CORRESPONDING #( instances ).
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.


"! @testing BDEF:ZRAP_R_TRAVEL_###
CLASS ltc_travel_stub DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    CONSTANTS c_root TYPE abp_root_entity_name VALUE 'ZRAP_R_TRAVEL_###'.

    CLASS-DATA class_under_test TYPE REF TO lhc_travel.
    CLASS-DATA stub             TYPE REF TO ltd_travel_stub.

    CLASS-METHODS class_setup.
    METHODS setup.
    METHODS teardown.

    METHODS accept_two_travels             FOR TESTING.
    METHODS discount_without_determination FOR TESTING.
ENDCLASS.

CLASS ltc_travel_stub IMPLEMENTATION.

  METHOD class_setup.
    CREATE OBJECT class_under_test FOR TESTING.
    CREATE OBJECT stub.
    "which BO the stub replaces
    stub->if_abap_behavior_testdouble~root_name = c_root.
  ENDMETHOD.

  METHOD setup.
    stub->reset( ).
    "from now on every READ/MODIFY on ZRAP_R_TRAVEL_### goes to the stub
    cl_abap_behv_test_environment=>set_test_double( object = stub ).
  ENDMETHOD.

  METHOD teardown.
    cl_abap_behv_test_environment=>unset_test_double( root = c_root ).
    ROLLBACK ENTITIES.                                 "#EC CI_ROLLBACK
  ENDMETHOD.

  METHOD accept_two_travels.
    DATA result   TYPE TABLE FOR ACTION RESULT zrap_r_travel_###\\Travel~acceptTravel.
    DATA mapped   TYPE RESPONSE FOR MAPPED EARLY zrap_r_travel_###.
    DATA failed   TYPE RESPONSE FOR FAILED EARLY zrap_r_travel_###.
    DATA reported TYPE RESPONSE FOR REPORTED EARLY zrap_r_travel_###.

    stub->instances = VALUE #( OverallStatus = 'O'
                               ( TravelID = '00000042' )
                               ( TravelID = '00000043' ) ).

    class_under_test->accepttravel(
      EXPORTING keys     = VALUE #( ( TravelID = '00000042' ) ( TravelID = '00000043' ) )
      CHANGING  result   = result
                mapped   = mapped
                failed   = failed
                reported = reported ).

    cl_abap_unit_assert=>assert_initial( act = failed ).

    "1) the action result
    cl_abap_unit_assert=>assert_equals( exp = 2 act = lines( result ) ).
    LOOP AT result INTO DATA(result_line).
      cl_abap_unit_assert=>assert_equals( exp = 'A' act = result_line-%param-OverallStatus ).
    ENDLOOP.

    "2) what the handler wrote - exactly the status, nothing else
    cl_abap_unit_assert=>assert_equals( exp = 2 act = lines( stub->updates ) ).
    LOOP AT stub->updates INTO DATA(update).
      cl_abap_unit_assert=>assert_equals( exp = if_abap_behv=>mk-on act = update-%control-OverallStatus ).
      cl_abap_unit_assert=>assert_equals( exp = if_abap_behv=>mk-off act = update-%control-BookingFee ).
    ENDLOOP.

    "3) one MODIFY for all keys, one READ for all keys (no EML inside a loop)
    cl_abap_unit_assert=>assert_equals( exp = 1 act = stub->modify_calls msg = 'modify calls' ).
    cl_abap_unit_assert=>assert_equals( exp = 1 act = stub->read_calls   msg = 'read calls' ).
  ENDMETHOD.

  METHOD discount_without_determination.
    DATA result   TYPE TABLE FOR ACTION RESULT zrap_r_travel_###\\Travel~deductDiscount.
    DATA mapped   TYPE RESPONSE FOR MAPPED EARLY zrap_r_travel_###.
    DATA failed   TYPE RESPONSE FOR FAILED EARLY zrap_r_travel_###.
    DATA reported TYPE RESPONSE FOR REPORTED EARLY zrap_r_travel_###.

    stub->instances = VALUE #( ( TravelID = '00000042' BookingFee = '100.00'
                                 TotalPrice = '100.00' CurrencyCode = 'EUR' ) ).

    class_under_test->deductdiscount(
      EXPORTING keys     = VALUE #( ( TravelID = '00000042' %param-discount_percent = 10 ) )
      CHANGING  result   = result
                mapped   = mapped
                failed   = failed
                reported = reported ).

    cl_abap_unit_assert=>assert_initial( act = failed ).
    cl_abap_unit_assert=>assert_equals( exp = CONV /dmo/booking_fee( '90.00' )
                                        act = result[ 1 ]-%param-BookingFee ).
    "no transactional buffer -> no determination -> total price untouched
    cl_abap_unit_assert=>assert_equals( exp = CONV /dmo/total_price( '100.00' )
                                        act = stub->instances[ 1 ]-TotalPrice ).
  ENDMETHOD.

ENDCLASS.
```

**왜 이렇게 쓰나**
- 3단계 테스트는 진짜 트랜잭션 버퍼를 쓰므로 결정·기능 제어 같은 BO의 다른 부분도 함께 돕니다. 스텁을 켜면 `lhc_travel` 안의 `READ/MODIFY ENTITIES ... IN LOCAL MODE`가 버퍼 대신 스텁으로 갑니다. 그래서 "이 메서드가 무엇을 읽고 무엇을 썼는가"만 정확히 볼 수 있습니다. 참조 시나리오 `/DMO/BP_TRAVEL_M`의 `test_using_entity_stub`과 같은 방식입니다.
- `modify_calls = 1`, `read_calls = 1` 검사는 "EML을 루프 안에서 부르지 말라"는 품질 기준을 테스트로 지키는 방법입니다.
- 스텁은 BO 전체를 대신하므로 직접 흉내 낸 것만 동작합니다. 여기서는 UPDATE와 READ, 두 필드만 흉내 냈습니다. 흉내 범위가 커지면 8~9단계의 RAP BO 테스트 더블 프레임워크가 낫습니다(그쪽은 소비자 코드용입니다).
- `discount_without_determination`은 같은 액션의 결과가 격리 방식에 따라 달라짐을 보여 줍니다. 단위 테스트에서 무엇을 함께 돌릴지(버퍼) 또는 끊을지(스텁) 의식적으로 고르세요.

**자주 나는 오류와 해결**
- `abp_root_entity_name` 타입을 못 찾으면 `TYPE string`으로 바꾸세요(`unset_test_double`의 파라미터 타입은 실제 시스템에서 확인 필요).
- 스텁의 단언이 "unexpected entity"로 실패하면 `<change>-entity_name`이 별칭(`TRAVEL`)이 아니라 엔터티 이름인지 디버거로 보세요. 참조 시나리오는 엔터티 이름(`/DMO/I_TRAVEL_M`)을 기대합니다.
- `set_test_double`을 `class_setup`에서만 부르면 첫 테스트 뒤 `teardown`의 `unset`으로 꺼져 두 번째 테스트부터 진짜 버퍼를 씁니다. 그래서 `setup`에서 매번 켭니다.

**클래스 구조 해설**
- `if_abap_behavior_testdouble`의 `modify`/`read`는 동적 EML(R-12 9단계)과 같은 `changes`/`retrievals` 표를 받습니다(줄마다 `entity_name`, `op`, `instances`/`results` 데이터 참조).
- 테스트 대상 메서드의 시그니처는 3단계와 같습니다. 바뀐 것은 메서드 안의 EML이 어디로 가는가뿐입니다.

</details>

#### 6단계. 세이버 테스트: adjust_numbers와 save_modified

요구사항
1. Test Classes 탭에 `ltc_saver`(`RISK LEVEL HARMLESS`)를 만드세요.
   - `class_setup`: `CREATE OBJECT saver FOR TESTING`, SQL 테스트 환경(`ZRAP_ATRAV_###`, `ZRAP_ABOOK_###`, `ZRAP_TLOG_###`).
   - `adjust_numbers_bookings`: 이미 저장된 Travel `00000001`에 Booking `0010`, `0020`이 있음(더블). 이번 저장에서 Travel 1에 새 Booking 2건, 이미 있던 Travel `00000002`(Booking 없음)에 새 Booking 1건. `mapped-booking`에는 `%pid`(임시 ID)와 `%tmp-TravelID`만 들어 있습니다. 기대: Travel 1의 새 Booking은 `0030`, `0040`, Travel 2는 `0010`. `mapped-travel`이 비어 있으므로 번호 범위는 쓰지 않습니다.
   - `save_modified_writes_log`: `update-travel` 1줄(`Description` 변경, `%control-Description` 켜짐)과 `delete-travel` 2줄을 넘깁니다. 기대: 로그 3줄 – `U`/`DESCRIPTION`/새 값 1줄, `D`/`*` 2줄. `reported`는 비어 있음.
2. `ltc_saver_numbers`(`RISK LEVEL DANGEROUS`)를 따로 만드세요.
   - `adjust_numbers_travels`: `mapped-travel` 2줄(각각 다른 `%pid`). 기대: 두 `TravelID`가 비어 있지 않고, 두 번째가 첫 번째 + 1.
   - 이 클래스가 왜 `DANGEROUS`인지 해설에 적으세요.

**확인** `ltc_saver`는 초록색입니다. `ltc_saver_numbers`는 시스템의 허용 위험 수준 설정에 따라 실행되지 않고 "risk level" 관련 경고로 건너뛸 수 있습니다. 그것도 정상입니다.

<details><summary>정답·해설</summary>

Test Classes 탭에 추가:

```abap
"! @testing BDEF:ZRAP_R_TRAVEL_###
CLASS ltc_saver DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    CLASS-DATA saver                TYPE REF TO lsc_zrap_r_travel_###.
    CLASS-DATA sql_test_environment TYPE REF TO if_osql_test_environment.

    CLASS-METHODS class_setup.
    CLASS-METHODS class_teardown.
    METHODS setup.
    METHODS teardown.

    METHODS adjust_numbers_bookings  FOR TESTING RAISING cx_static_check.
    METHODS save_modified_writes_log FOR TESTING RAISING cx_static_check.
ENDCLASS.

CLASS ltc_saver IMPLEMENTATION.

  METHOD class_setup.
    CREATE OBJECT saver FOR TESTING.
    "the saver works directly with ABAP SQL on these tables
    sql_test_environment = cl_osql_test_environment=>create(
                             i_dependency_list = VALUE #( ( 'ZRAP_ATRAV_###' )
                                                          ( 'ZRAP_ABOOK_###' )
                                                          ( 'ZRAP_TLOG_###' ) ) ).
  ENDMETHOD.

  METHOD setup.
    sql_test_environment->clear_doubles( ).
  ENDMETHOD.

  METHOD teardown.
    ROLLBACK ENTITIES.                                 "#EC CI_ROLLBACK
  ENDMETHOD.

  METHOD class_teardown.
    sql_test_environment->destroy( ).
  ENDMETHOD.

  METHOD adjust_numbers_bookings.
    DATA booking_db TYPE STANDARD TABLE OF zrap_abook_### WITH EMPTY KEY.
    DATA mapped     TYPE RESPONSE FOR MAPPED LATE zrap_r_travel_###.
    DATA reported   TYPE RESPONSE FOR REPORTED LATE zrap_r_travel_###.

    "given: travel 1 already has bookings 10 and 20 on the database
    booking_db = VALUE #( travel_id = '00000001'
                          ( booking_id = '0010' )
                          ( booking_id = '0020' ) ).
    sql_test_environment->insert_test_data( booking_db ).

    "three new bookings; their parents already exist (%tmp-TravelID filled)
    DATA(pid_1) = cl_system_uuid=>create_uuid_x16_static( ).
    DATA(pid_2) = cl_system_uuid=>create_uuid_x16_static( ).
    DATA(pid_3) = cl_system_uuid=>create_uuid_x16_static( ).
    mapped-booking = VALUE #( ( %pid = pid_1  %tmp-TravelID = '00000001' )
                              ( %pid = pid_2  %tmp-TravelID = '00000001' )
                              ( %pid = pid_3  %tmp-TravelID = '00000002' ) ).

    "when
    saver->adjust_numbers( CHANGING mapped   = mapped
                                    reported = reported ).

    "then: numbering continues per travel in steps of 10
    cl_abap_unit_assert=>assert_initial( act = reported ).
    cl_abap_unit_assert=>assert_equals( exp = '00000001' act = mapped-booking[ %pid = pid_1 ]-TravelID ).
    cl_abap_unit_assert=>assert_equals( exp = '0030'     act = mapped-booking[ %pid = pid_1 ]-BookingID ).
    cl_abap_unit_assert=>assert_equals( exp = '0040'     act = mapped-booking[ %pid = pid_2 ]-BookingID ).
    cl_abap_unit_assert=>assert_equals( exp = '00000002' act = mapped-booking[ %pid = pid_3 ]-TravelID ).
    cl_abap_unit_assert=>assert_equals( exp = '0010'     act = mapped-booking[ %pid = pid_3 ]-BookingID ).
  ENDMETHOD.

  METHOD save_modified_writes_log.
    DATA create   TYPE REQUEST FOR CHANGE zrap_r_travel_###.
    DATA update   TYPE REQUEST FOR CHANGE zrap_r_travel_###.
    DATA delete   TYPE REQUEST FOR DELETE zrap_r_travel_###.
    DATA reported TYPE RESPONSE FOR REPORTED LATE zrap_r_travel_###.

    "with full data: all fields are filled, %control tells what changed
    update-travel = VALUE #( ( TravelID    = '00000011'
                               Description = 'Changed by unit test'
                               CustomerID  = '000001'
                               %control-Description = if_abap_behv=>mk-on ) ).
    delete-travel = VALUE #( ( TravelID = '00000021' )
                             ( TravelID = '00000022' ) ).

    saver->save_modified( EXPORTING create   = create
                                    update   = update
                                    delete   = delete
                          CHANGING  reported = reported ).

    cl_abap_unit_assert=>assert_initial( act = reported ).

    "the INSERT went into the double, not into the real table
    SELECT FROM zrap_tlog_###
      FIELDS travel_id, entity_name, operation, field_name, new_value
      ORDER BY travel_id
      INTO TABLE @DATA(log).                            "#EC CI_NOWHERE

    cl_abap_unit_assert=>assert_equals( exp = 3 act = lines( log ) ).

    "only the field marked in %control is logged (CustomerID is not)
    cl_abap_unit_assert=>assert_equals( exp = '00000011'    act = log[ 1 ]-travel_id ).
    cl_abap_unit_assert=>assert_equals( exp = 'U'           act = log[ 1 ]-operation ).
    cl_abap_unit_assert=>assert_equals( exp = 'DESCRIPTION' act = log[ 1 ]-field_name ).
    cl_abap_unit_assert=>assert_equals( exp = 'Changed by unit test' act = log[ 1 ]-new_value ).

    LOOP AT log INTO DATA(delete_log) FROM 2.
      cl_abap_unit_assert=>assert_equals( exp = 'TRAVEL' act = delete_log-entity_name ).
      cl_abap_unit_assert=>assert_equals( exp = 'D'      act = delete_log-operation ).
      cl_abap_unit_assert=>assert_equals( exp = '*'      act = delete_log-field_name ).
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.


"! Draws real numbers from number range object ZRAP_NR_### -> changes persistent data
CLASS ltc_saver_numbers DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL DANGEROUS.

  PRIVATE SECTION.
    CLASS-DATA saver                TYPE REF TO lsc_zrap_r_travel_###.
    CLASS-DATA sql_test_environment TYPE REF TO if_osql_test_environment.

    CLASS-METHODS class_setup.
    CLASS-METHODS class_teardown.

    METHODS adjust_numbers_travels FOR TESTING RAISING cx_static_check.
ENDCLASS.

CLASS ltc_saver_numbers IMPLEMENTATION.

  METHOD class_setup.
    CREATE OBJECT saver FOR TESTING.
    "fallback path (SELECT MAX) must not read the real table
    sql_test_environment = cl_osql_test_environment=>create(
                             i_dependency_list = VALUE #( ( 'ZRAP_ATRAV_###' ) ) ).
  ENDMETHOD.

  METHOD class_teardown.
    sql_test_environment->destroy( ).
  ENDMETHOD.

  METHOD adjust_numbers_travels.
    DATA mapped   TYPE RESPONSE FOR MAPPED LATE zrap_r_travel_###.
    DATA reported TYPE RESPONSE FOR REPORTED LATE zrap_r_travel_###.

    DATA(pid_1) = cl_system_uuid=>create_uuid_x16_static( ).
    DATA(pid_2) = cl_system_uuid=>create_uuid_x16_static( ).
    mapped-travel = VALUE #( ( %pid = pid_1 ) ( %pid = pid_2 ) ).

    saver->adjust_numbers( CHANGING mapped   = mapped
                                    reported = reported ).

    DATA(id_1) = mapped-travel[ %pid = pid_1 ]-TravelID.
    DATA(id_2) = mapped-travel[ %pid = pid_2 ]-TravelID.

    "the exact numbers depend on the number range status - check the rule only
    cl_abap_unit_assert=>assert_not_initial( act = id_1 ).
    cl_abap_unit_assert=>assert_equals( exp = CONV /dmo/travel_id( id_1 + 1 ) act = id_2 ).
  ENDMETHOD.

ENDCLASS.
```

**왜 이렇게 쓰나**
- 세이버 메서드는 프레임워크가 저장 단계에서만 부르므로, 통합 테스트로만 검사하면 실패 원인을 찾기 어렵습니다. 핸들러와 똑같이 `CREATE OBJECT ... FOR TESTING` + `FRIENDS`로 직접 부릅니다(참조 시나리오: 비관리형 `ltcl_saver`의 `adjust_numbers`, 관리형 `ltc_save_not_in_documentation`의 `save_modified`).
- `adjust_numbers`의 `mapped`는 `RESPONSE FOR MAPPED LATE` 타입이며, 프레임워크가 넘겨줄 때처럼 `%pid`와 `%tmp`(임시 키)만 채워 넣으면 됩니다. 메서드가 `%key`(`TravelID`, `BookingID`)를 채웠는지 `%pid`로 찾아 확인합니다.
- `adjust_numbers_bookings`에서는 `mapped-travel`을 비워 두어 번호 범위 코드를 아예 타지 않게 했습니다. 부모가 새 Travel인 경우(`%tmp-TravelID`가 빈 경우)는 `READ ... BY \_Travel ... LINK`가 트랜잭션 버퍼에 그 Booking이 실제로 있어야 동작하므로 단위 테스트가 아니라 7단계 통합 테스트로 검사합니다.
- `save_modified`는 `REQUEST FOR CHANGE`/`REQUEST FOR DELETE` 타입의 구조를 직접 만들어 넘깁니다. `INSERT zrap_tlog_###`가 SQL 더블로 들어가므로 실제 로그 테이블은 깨끗합니다. `log_uuid`, `changed_by`, `changed_at`은 실행할 때마다 달라 비교하지 않습니다.
- **`ltc_saver_numbers`가 DANGEROUS인 이유**: `cl_numberrange_runtime=>number_get`은 번호 범위 상태(영속 데이터)를 바꾸고, 그 변경은 테스트 뒤에도 되돌아가지 않습니다(번호 범위는 별도 커넥션으로 처리됨, R-04 해설 참조). "영속 데이터를 바꾸는 테스트"는 `RISK LEVEL DANGEROUS`로 표시해야 합니다. 시스템이 이 수준을 허용하지 않으면 ABAP Unit이 이 클래스를 실행하지 않습니다.
- 번호 범위까지 HARMLESS로 테스트하고 싶다면, R-04 `adjust_numbers`의 `number_get` 호출 부분을 `TEST-SEAM ... END-TEST-SEAM`으로 감싸고, 테스트에서 `TEST-INJECTION`으로 받은 번호를 정해 주는 방법이 있습니다(11단계 해설 참고). 행동 풀 로컬 클래스 안에서 TEST-SEAM을 쓸 수 있는지는 실제 시스템에서 확인 필요입니다.

**자주 나는 오류와 해결**
- `mapped-booking[ %pid = pid_1 ]`에서 줄을 못 찾는다는 덤프: `adjust_numbers`가 `mapped`를 새 표로 바꿔 넣었거나(`%pid` 유실), R-04 코드가 `mapped-booking`을 `LOOP ... INTO`(복사본)로 돌며 값을 넣고 있습니다. `ASSIGNING`이어야 합니다.
- `save_modified` 호출에서 파라미터 불일치 오류: 이 구현은 `create`/`update`/`delete`와 `reported`만 씁니다. ADT에서 F2로 `save_modified`의 정확한 시그니처를 보고(예: `failed`, `mapped`가 더 있는지) 맞추세요.
- 로그가 4줄 이상이면 R-04의 `add_log_lines`가 `%control`에서 켜지지 않은 필드도 기록하고 있는지 보세요.

**클래스 구조 해설**
- `adjust_numbers`는 BDEF의 `late numbering`, `save_modified`는 `with additional save`(또는 `with unmanaged save`)가 있어야 재정의할 수 있습니다. `with full data`가 있으면 `update`에 바뀌지 않은 필드 값도 들어옵니다.
- 실제 순서는 `finalize`(결정) → `check_before_save`(검증) → `adjust_numbers` → 관리형 저장 → `save_modified` → `cleanup`입니다. 단위 테스트는 이 중 한 칸만 떼어 내 검사합니다.

</details>


#### 7단계. BO 통합 테스트: EML부터 COMMIT ENTITIES까지

요구사항
1. 테스트 전용 전역 클래스 `ZTC_RAP_TRAVEL_EML_###`를 만드세요. 클래스 정의 자체에 `FOR TESTING RISK LEVEL HARMLESS DURATION SHORT`를 붙이고, `"! @testing BDEF:ZRAP_R_TRAVEL_###`로 BDEF와 연결합니다.
2. `class_setup`: CDS 테스트 환경(`ZRAP_R_TRAVEL_###`, `ZRAP_R_BOOKING_###`, 리디렉션 켬)과 SQL 테스트 환경(`/DMO/AGENCY`, `/DMO/CUSTOMER`, `/DMO/CARRIER`, `/DMO/FLIGHT`, `ZRAP_CTRL_###`, `ZRAP_TLOG_###`, `ZRAP_EVLOG_###`)을 만들고, 테스트 데이터를 준비합니다. 여행사 `070001`, 고객 `000001`, 항공사 `LH`, 항공편 `LH 0400`(오늘+10, 가격 `2000.00 EUR`).
3. `setup`: 더블을 비우고 테스트 데이터를 다시 넣습니다. `teardown`: `ROLLBACK ENTITIES`.
4. `deep_create_accept_commit`: 한 `MODIFY ENTITIES` 문장에서 Travel 생성(`%cid = 'T1'`, 수수료 `10.50 EUR`) + Booking 생성(`CREATE BY \_Booking`, 항공편 가격 `2000.00 EUR`) + `acceptTravel` 실행(`%cid_ref = 'T1'`). 그다음 `COMMIT ENTITIES RESPONSES`. 기대:
   - `MODIFY`와 `COMMIT`의 `failed`가 비어 있고, `reported`에 오류 심각도 메시지가 없음
   - 활성 데이터(`SELECT FROM zrap_r_travel_###`, 더블을 읽음)에 1건, `TravelID`가 채워짐(late numbering), 상태 `A`, 총액 `2010.50`, 설명이 비어 있지 않음(결정 `setDefaultDescription`)
   - Booking 1건, `BookingID = 0010`, 상태 `N`(결정 `setInitialBookingValues`)
   - 변경 로그 더블 `ZRAP_TLOG_###`에 줄이 생김(`save_modified`)
5. `commit_fails_on_validation`: 고객 `999999`로 Travel을 만들고 `COMMIT ENTITIES`. 기대: `sy-subrc = 4`, 커밋 응답 `failed-travel`에 1줄, 메시지 `customer_unknown`, 활성 데이터 0건. 마지막에 `ROLLBACK ENTITIES`.

**확인** 두 테스트가 초록색입니다. 실제 테이블 `ZRAP_ATRAV_###`의 Data Preview에서 설명이 `Trip of customer 1 ...`인 새 줄이 생기지 **않았는지** 꼭 확인하세요. 생겼다면 리디렉션이 동작하지 않은 것이므로 즉시 테스트 실행을 멈추고 원인을 찾으세요.

<details><summary>정답·해설</summary>

```abap
"! Integration test of the Travel BO: interaction phase + save sequence on test doubles
"! @testing BDEF:ZRAP_R_TRAVEL_###
CLASS ztc_rap_travel_eml_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC
  FOR TESTING
  RISK LEVEL HARMLESS
  DURATION SHORT.

  PRIVATE SECTION.
    CLASS-DATA cds_test_environment TYPE REF TO if_cds_test_environment.
    CLASS-DATA sql_test_environment TYPE REF TO if_osql_test_environment.

    CLASS-DATA agency_mock_data   TYPE STANDARD TABLE OF /dmo/agency   WITH EMPTY KEY.
    CLASS-DATA customer_mock_data TYPE STANDARD TABLE OF /dmo/customer WITH EMPTY KEY.
    CLASS-DATA carrier_mock_data  TYPE STANDARD TABLE OF /dmo/carrier  WITH EMPTY KEY.
    CLASS-DATA flight_mock_data   TYPE STANDARD TABLE OF /dmo/flight   WITH EMPTY KEY.
    CLASS-DATA begin_date         TYPE /dmo/begin_date.
    CLASS-DATA end_date           TYPE /dmo/end_date.

    CLASS-METHODS class_setup.
    CLASS-METHODS class_teardown.
    METHODS setup.
    METHODS teardown.

    METHODS count_errors
      IMPORTING reported_tab TYPE TABLE FOR REPORTED LATE zrap_r_travel_###\\Travel
      RETURNING VALUE(count) TYPE i.

    METHODS deep_create_accept_commit  FOR TESTING RAISING cx_static_check.
    METHODS commit_fails_on_validation FOR TESTING RAISING cx_static_check.
ENDCLASS.



CLASS ztc_rap_travel_eml_### IMPLEMENTATION.

  METHOD class_setup.
    cds_test_environment = cl_cds_test_environment=>create_for_multiple_cds(
                             i_for_entities = VALUE #(
                               ( i_for_entity = 'ZRAP_R_TRAVEL_###' )
                               ( i_for_entity = 'ZRAP_R_BOOKING_###' ) ) ).
    cds_test_environment->enable_double_redirection( ).

    sql_test_environment = cl_osql_test_environment=>create(
                             i_dependency_list = VALUE #( ( '/DMO/AGENCY' )
                                                          ( '/DMO/CUSTOMER' )
                                                          ( '/DMO/CARRIER' )
                                                          ( '/DMO/FLIGHT' )
                                                          ( 'ZRAP_CTRL_###' )
                                                          ( 'ZRAP_TLOG_###' )
                                                          ( 'ZRAP_EVLOG_###' ) ) ).

    begin_date = cl_abap_context_info=>get_system_date( ) + 10.
    end_date   = cl_abap_context_info=>get_system_date( ) + 20.

    agency_mock_data   = VALUE #( ( agency_id = '070001' name = 'Test Agency' country_code = 'DE' ) ).
    customer_mock_data = VALUE #( ( customer_id = '000001' first_name = 'Yurim' last_name = 'Lee' ) ).
    carrier_mock_data  = VALUE #( ( carrier_id = 'LH' name = 'Test Carrier' currency_code = 'EUR' ) ).
    flight_mock_data   = VALUE #( ( carrier_id = 'LH' connection_id = '0400' flight_date = begin_date
                                    price = '2000.00' currency_code = 'EUR' ) ).
  ENDMETHOD.

  METHOD setup.
    cds_test_environment->clear_doubles( ).
    sql_test_environment->clear_doubles( ).

    sql_test_environment->insert_test_data( agency_mock_data ).
    sql_test_environment->insert_test_data( customer_mock_data ).
    sql_test_environment->insert_test_data( carrier_mock_data ).
    sql_test_environment->insert_test_data( flight_mock_data ).
  ENDMETHOD.

  METHOD teardown.
    ROLLBACK ENTITIES.                                 "#EC CI_ROLLBACK
  ENDMETHOD.

  METHOD class_teardown.
    cds_test_environment->destroy( ).
    sql_test_environment->destroy( ).
  ENDMETHOD.

  METHOD count_errors.
    LOOP AT reported_tab INTO DATA(line) WHERE %msg IS BOUND.
      IF line-%msg->m_severity = if_abap_behv_message=>severity-error.
        count += 1.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.


  METHOD deep_create_accept_commit.
    "----- when: one EML request = create travel + booking + action -----
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        CREATE FIELDS ( AgencyID CustomerID BeginDate EndDate BookingFee CurrencyCode )
          WITH VALUE #( ( %cid         = 'T1'
                          AgencyID     = agency_mock_data[ 1 ]-agency_id
                          CustomerID   = customer_mock_data[ 1 ]-customer_id
                          BeginDate    = begin_date
                          EndDate      = end_date
                          BookingFee   = '10.50'
                          CurrencyCode = 'EUR' ) )
        CREATE BY \_Booking
          FIELDS ( CustomerID CarrierID ConnectionID FlightDate FlightPrice CurrencyCode )
          WITH VALUE #( ( %cid_ref = 'T1'
                          %target  = VALUE #( ( %cid         = 'B1'
                                                CustomerID   = customer_mock_data[ 1 ]-customer_id
                                                CarrierID    = flight_mock_data[ 1 ]-carrier_id
                                                ConnectionID = flight_mock_data[ 1 ]-connection_id
                                                FlightDate   = flight_mock_data[ 1 ]-flight_date
                                                FlightPrice  = flight_mock_data[ 1 ]-price
                                                CurrencyCode = flight_mock_data[ 1 ]-currency_code ) ) ) )
      ENTITY Travel
        EXECUTE acceptTravel FROM VALUE #( ( %cid_ref = 'T1' ) )
      MAPPED   DATA(mapped)
      FAILED   DATA(failed)
      REPORTED DATA(reported).

    cl_abap_unit_assert=>assert_initial( act = failed msg = 'modify failed' ).
    cl_abap_unit_assert=>assert_equals( exp = 1 act = lines( mapped-travel ) ).
    cl_abap_unit_assert=>assert_equals( exp = 1 act = lines( mapped-booking ) ).
    "late numbering: no final key yet, only the preliminary %pid
    cl_abap_unit_assert=>assert_not_initial( act = mapped-travel[ 1 ]-%pid ).

    "----- save sequence: determinations on save, validations, adjust_numbers, save, save_modified -----
    COMMIT ENTITIES RESPONSES
      FAILED   DATA(commit_failed)
      REPORTED DATA(commit_reported).

    cl_abap_unit_assert=>assert_equals( exp = 0 act = sy-subrc msg = 'commit sy-subrc' ).
    cl_abap_unit_assert=>assert_initial( act = commit_failed msg = 'commit failed' ).
    cl_abap_unit_assert=>assert_equals( exp = 0 act = count_errors( commit_reported-travel ) ).

    "----- then: read what was written (CDS entity on top of the doubled tables) -----
    SELECT FROM zrap_r_travel_###
      FIELDS TravelID, OverallStatus, TotalPrice, Description
      INTO TABLE @DATA(travels).                        "#EC CI_NOWHERE
    cl_abap_unit_assert=>assert_equals( exp = 1 act = lines( travels ) ).
    DATA(travel) = travels[ 1 ].
    cl_abap_unit_assert=>assert_not_initial( act = travel-TravelID msg = 'adjust_numbers assigned an ID' ).
    cl_abap_unit_assert=>assert_equals( exp = 'A' act = travel-OverallStatus ).
    cl_abap_unit_assert=>assert_equals( exp = CONV /dmo/total_price( '2010.50' ) act = travel-TotalPrice ).
    cl_abap_unit_assert=>assert_not_initial( act = travel-Description msg = 'setDefaultDescription' ).

    SELECT FROM zrap_r_booking_###
      FIELDS TravelID, BookingID, BookingStatus
      INTO TABLE @DATA(bookings).                       "#EC CI_NOWHERE
    cl_abap_unit_assert=>assert_equals( exp = 1 act = lines( bookings ) ).
    cl_abap_unit_assert=>assert_equals( exp = travel-TravelID act = bookings[ 1 ]-TravelID ).
    cl_abap_unit_assert=>assert_equals( exp = '0010' act = bookings[ 1 ]-BookingID ).
    cl_abap_unit_assert=>assert_equals( exp = 'N' act = bookings[ 1 ]-BookingStatus ).

    "save_modified wrote the change log into its double
    SELECT COUNT(*) FROM zrap_tlog_### INTO @DATA(log_count).
    cl_abap_unit_assert=>assert_differs( exp = 0 act = log_count msg = 'change log expected' ).
  ENDMETHOD.

  METHOD commit_fails_on_validation.
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        CREATE FIELDS ( AgencyID CustomerID BeginDate EndDate CurrencyCode )
          WITH VALUE #( ( %cid         = 'T1'
                          AgencyID     = agency_mock_data[ 1 ]-agency_id
                          CustomerID   = '999999'                "not in the double
                          BeginDate    = begin_date
                          EndDate      = end_date
                          CurrencyCode = 'EUR' ) )
      FAILED DATA(failed).
    cl_abap_unit_assert=>assert_initial( act = failed msg = 'validations run on save, not on modify' ).

    COMMIT ENTITIES RESPONSES
      FAILED   DATA(commit_failed)
      REPORTED DATA(commit_reported).

    cl_abap_unit_assert=>assert_equals( exp = 4 act = sy-subrc msg = 'commit must be rejected' ).
    cl_abap_unit_assert=>assert_equals( exp = 1 act = lines( commit_failed-travel ) ).

    DATA(found) = abap_false.
    LOOP AT commit_reported-travel INTO DATA(line) WHERE %msg IS BOUND.
      DATA(message) = CAST zcm_rap_###( line-%msg ).
      IF message->if_t100_message~t100key = zcm_rap_###=>customer_unknown.
        found = abap_true.
      ENDIF.
    ENDLOOP.
    cl_abap_unit_assert=>assert_true( act = found msg = 'customer_unknown expected' ).

    "nothing was written
    SELECT COUNT(*) FROM zrap_r_travel_### INTO @DATA(travel_count).
    cl_abap_unit_assert=>assert_equals( exp = 0 act = travel_count ).

    "the failed transaction is still in the buffer - throw it away
    ROLLBACK ENTITIES.                                 "#EC CI_ROLLBACK
  ENDMETHOD.

ENDCLASS.
```

**왜 이렇게 쓰나**
- 단위 테스트(2~6단계)는 메서드 하나씩 봤고, "언제 불리는가(트리거)"와 "순서"는 검사하지 못했습니다. 통합 테스트는 프레임워크가 결정·검증·`adjust_numbers`·저장·`save_modified`를 **실제 순서대로** 부르게 하고 최종 결과만 봅니다(RAP400 ex3의 `deep_create_with_action`과 같은 구조).
- `COMMIT ENTITIES`는 테스트 안에서도 진짜로 저장합니다. 그래서 BO가 쓰는 **모든** 테이블(활성 테이블, 로그, 이벤트 로그, 스위치 테이블)을 더블로 바꿔야 `RISK LEVEL HARMLESS`가 사실이 됩니다. 결과는 CDS 엔터티 `zrap_r_travel_###`를 SELECT해 확인합니다. 그 아래 테이블이 더블이므로 테스트가 쓴 데이터만 보입니다.
- 검증은 저장 때 돌기 때문에 `commit_fails_on_validation`의 `MODIFY`는 성공하고 `COMMIT`이 실패합니다. 이 차이를 테스트로 고정해 두면 나중에 누군가 검증을 `on modify`로 바꿀 때 바로 알 수 있습니다.
- 실패한 `COMMIT` 뒤에는 버퍼에 인스턴스가 남습니다. 같은 테스트 안에서 계속 EML을 쓰려면 `ROLLBACK ENTITIES`가 필요합니다.
- draft EML(`%is_draft = mk-on`, `Activate`)은 draft 테이블 `ZRAP_DTRAV_###`/`ZRAP_DBOOK_###`에 씁니다. 이 테이블은 CDS 엔터티의 의존성이 아니므로 위 환경에서는 더블이 되지 않습니다. 그래서 통합 테스트는 활성 인스턴스로만 했습니다. draft까지 테스트하려면 draft 테이블을 SQL 더블에 넣어 볼 수 있지만, draft 런타임이 그 더블을 쓰는지는 실제 시스템에서 확인 필요입니다.

**자주 나는 오류와 해결**
- `TravelID`의 번호는 R-04의 번호 범위(`ZRAP_NR_###`)에서 옵니다. 번호 범위가 있으면 **진짜 번호가 하나 소비됩니다**(되돌릴 수 없음). 엄격하게는 이 클래스도 `DANGEROUS`입니다. 번호 소비가 싫으면 6단계 해설의 TEST-SEAM 방식을 쓰거나 R-04 상수 `c_use_number_range`를 `abap_false`로 두고 실행하세요(그러면 더블에 대한 `SELECT MAX`로 1번이 붙습니다).
- `travel_accepted` 이벤트(R-04)는 커밋 뒤 이벤트 핸들러 `ZCL_RAP_TRAV_EVT_###`가 처리합니다. 핸들러가 비동기로 실행되면 테스트의 SQL 더블 밖(실제 `ZRAP_EVLOG_###`)에 쓸 수 있습니다. 실행 뒤 실제 이벤트 로그 테이블도 확인하세요(실제 시스템에서 확인 필요).
- `MODIFY`의 `failed`에 `%fail-cause = unauthorized`가 나오면 R-03 전역 기능 제어/권한이 `ZRAP_CTRL_###`를 읽는데 그 테이블이 더블에 없는 경우입니다. SQL 더블 목록을 확인하세요.
- `count_errors`의 파라미터 타입이 활성화되지 않으면 2단계 "자주 나는 오류"의 `TYPES ... TYPE RESPONSE FOR REPORTED LATE` 방식으로 바꾸세요.

**클래스 구조 해설**
- 전역 테스트 클래스는 정의에 `FOR TESTING`이 붙어 있어 운영 코드에서 쓸 수 없고 운영 시스템으로 이송되어도 실행되지 않습니다. 테스트 메서드는 행동 풀 밖에 있으므로 `FRIENDS`가 필요 없고, BO를 **소비자처럼** EML로만 다룹니다.
- `"! @testing BDEF:...` 덕분에 BDEF나 행동 풀에서 `Ctrl+Shift+F10`을 눌러도 이 클래스가 함께 실행됩니다.

</details>

#### 8단계. BO를 쓰는 코드 테스트 (1): 소비자 클래스와 트랜잭션 버퍼 더블

요구사항
1. 소비자 클래스 `ZCL_RAP_TRAV_APPROVER_###`를 만드세요. EML로 `ZRAP_R_TRAVEL_###`만 다루고, **COMMIT은 하지 않습니다**(호출자가 결정).
   - `approve_open_travels( travel_ids )`: 주어진 Travel들의 상태를 한 번에 읽고, 상태 `O`인 것만 `acceptTravel`을 한 번에 실행합니다. 결과 구조: `accepted`(승인된 ID), `skipped`(열린 상태가 아니라 건너뛴 ID), `failed`, `reported`.
   - `change_description( travel_id, description )`: `Description`만 UPDATE하고 `failed`, `reported`를 돌려줍니다.
   - `get_description( travel_id )`: `Description`을 읽어 돌려줍니다.
   - `can_accept( travel_id )`: `GET PERMISSIONS ONLY INSTANCE`로 `acceptTravel`이 허용되는지 확인합니다(기능 제어 + 권한).
2. 이 클래스의 **Test Classes** 탭에 트랜잭션 버퍼 더블 테스트 `ltc_with_buffer_double`을 만드세요.
   - `class_setup`: `cl_botd_txbufdbl_bo_test_env`로 `ZRAP_R_TRAVEL_###` 더블 환경을 만들고(draft BO이므로 `handle_draft`도 지정), `setup`: `clear_doubles`.
   - 번호 매기기 도우미 `ltd_fields_handler`(`if_botd_bufdbl_fields_handler`): Travel 생성 때 읽기 전용 키 `TravelID`를 1부터 차례로 채웁니다.
   - `change_and_read_description`: 테스트 안에서 EML CREATE로 버퍼 더블에 Travel 하나를 넣고(설명 `Old`), `change_description`으로 `New`로 바꾼 뒤 `get_description`이 `New`인지 확인합니다.
   - `change_unknown_travel_fails`: 없는 Travel `99`를 바꾸면 `failed-travel`이 채워지는지 확인합니다.
   - `change_locked_travel_fails`: `configure_additional_behavior( )->for_modify_update( )`로 "Travel 1의 이 UPDATE는 `%fail-cause = locked`로 실패"하도록 설정하고 결과를 확인합니다.

**확인** 세 테스트가 초록색입니다. 실제 테이블에는 아무 변화가 없습니다(더블은 메모리 버퍼만 씁니다).

<details><summary>정답·해설</summary>

소비자 클래스 `ZCL_RAP_TRAV_APPROVER_###`:

```abap
"! Consumer of the Travel BO - used as code under test for the RAP BO test double framework.
"! It never commits: the caller owns the transaction.
CLASS zcl_rap_trav_approver_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    TYPES tt_travel_ids TYPE STANDARD TABLE OF /dmo/travel_id WITH EMPTY KEY.
    TYPES ty_failed     TYPE RESPONSE FOR FAILED EARLY zrap_r_travel_###.
    TYPES ty_reported   TYPE RESPONSE FOR REPORTED EARLY zrap_r_travel_###.

    TYPES: BEGIN OF ty_approval,
             accepted TYPE tt_travel_ids,
             skipped  TYPE tt_travel_ids,
             failed   TYPE ty_failed,
             reported TYPE ty_reported,
           END OF ty_approval.

    CONSTANTS c_status_open TYPE /dmo/overall_status VALUE 'O'.

    METHODS approve_open_travels
      IMPORTING travel_ids      TYPE tt_travel_ids
      RETURNING VALUE(approval) TYPE ty_approval.

    METHODS change_description
      IMPORTING travel_id   TYPE /dmo/travel_id
                description TYPE /dmo/description
      EXPORTING failed      TYPE ty_failed
                reported    TYPE ty_reported.

    METHODS get_description
      IMPORTING travel_id          TYPE /dmo/travel_id
      RETURNING VALUE(description) TYPE /dmo/description.

    METHODS can_accept
      IMPORTING travel_id      TYPE /dmo/travel_id
      RETURNING VALUE(allowed) TYPE abap_bool.
ENDCLASS.



CLASS zcl_rap_trav_approver_### IMPLEMENTATION.

  METHOD approve_open_travels.
    DATA read_keys   TYPE TABLE FOR READ IMPORT zrap_r_travel_###\\Travel.
    DATA accept_keys TYPE TABLE FOR ACTION IMPORT zrap_r_travel_###\\Travel~acceptTravel.

    "1) one READ for all travels
    read_keys = VALUE #( FOR id IN travel_ids ( TravelID = id ) ).
    READ ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        FIELDS ( OverallStatus ) WITH read_keys
      RESULT DATA(travels)
      FAILED DATA(read_failed).
    APPEND LINES OF read_failed-travel TO approval-failed-travel.

    "2) decide in ABAP, not with one EML call per travel
    LOOP AT travels INTO DATA(travel).
      IF travel-OverallStatus = c_status_open.
        APPEND VALUE #( %tky = travel-%tky ) TO accept_keys.
      ELSE.
        APPEND travel-TravelID TO approval-skipped.
      ENDIF.
    ENDLOOP.

    IF accept_keys IS INITIAL.
      RETURN.
    ENDIF.

    "3) one EXECUTE for all open travels
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        EXECUTE acceptTravel FROM accept_keys
      RESULT   DATA(accept_result)
      FAILED   DATA(accept_failed)
      REPORTED DATA(accept_reported).

    approval-accepted = VALUE #( FOR r IN accept_result ( r-TravelID ) ).
    APPEND LINES OF accept_failed-travel TO approval-failed-travel.
    approval-reported = accept_reported.
  ENDMETHOD.

  METHOD change_description.
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        UPDATE FIELDS ( Description )
        WITH VALUE #( ( TravelID = travel_id Description = description ) )
      FAILED   failed
      REPORTED reported.
  ENDMETHOD.

  METHOD get_description.
    READ ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        FIELDS ( Description ) WITH VALUE #( ( TravelID = travel_id ) )
      RESULT DATA(travels).
    description = VALUE #( travels[ 1 ]-Description OPTIONAL ).
  ENDMETHOD.

  METHOD can_accept.
    DATA keys    TYPE TABLE FOR PERMISSIONS KEY zrap_r_travel_###.
    DATA request TYPE STRUCTURE FOR PERMISSIONS REQUEST zrap_r_travel_###.
    DATA result  TYPE STRUCTURE FOR PERMISSIONS RESULT zrap_r_travel_###.

    keys = VALUE #( ( %key-TravelID = travel_id ) ).
    request-%action-acceptTravel = if_abap_behv=>mk-on.

    "instance permissions = instance feature control + instance authorization
    GET PERMISSIONS ONLY INSTANCE OF zrap_r_travel_###
      ENTITY Travel
      FROM keys
      REQUEST request
      RESULT result
      FAILED DATA(failed)
      REPORTED DATA(reported).

    allowed = xsdbool( failed IS INITIAL
                       AND line_exists( result-instances[ %action-acceptTravel = if_abap_behv=>perm-o-enabled ] ) ).
  ENDMETHOD.

ENDCLASS.
```

같은 클래스의 **Test Classes** 탭(번호 매기기 도우미 + 테스트 클래스):

```abap
"! Gives created travels a key, because TravelID is read-only for the consumer
CLASS ltd_fields_handler DEFINITION FINAL FOR TESTING.
  PUBLIC SECTION.
    INTERFACES if_botd_bufdbl_fields_handler.
    DATA max_travel_id TYPE i VALUE 0.
ENDCLASS.

CLASS ltd_fields_handler IMPLEMENTATION.
  METHOD if_botd_bufdbl_fields_handler~set_readonly_fields.
    DATA create_instances TYPE TABLE FOR CREATE zrap_r_travel_###\\Travel.

    IF entity_name = 'ZRAP_R_TRAVEL_###' AND operation = if_abap_behv=>op-m-create.
      create_instances = instances.
      LOOP AT create_instances ASSIGNING FIELD-SYMBOL(<instance>).
        max_travel_id += 1.
        <instance>-TravelID = max_travel_id.
      ENDLOOP.
      instances = create_instances.
    ENDIF.
  ENDMETHOD.
ENDCLASS.


"! @testing BDEF:ZRAP_R_TRAVEL_###
CLASS ltc_with_buffer_double DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    CLASS-DATA environment TYPE REF TO if_botd_txbufdbl_bo_test_env.
    CLASS-DATA cut         TYPE REF TO zcl_rap_trav_approver_###.

    CLASS-METHODS class_setup.
    CLASS-METHODS class_teardown.
    METHODS setup.

    METHODS create_travel_in_double
      IMPORTING description      TYPE /dmo/description
      RETURNING VALUE(travel_id) TYPE /dmo/travel_id.

    METHODS change_and_read_description FOR TESTING RAISING cx_static_check.
    METHODS change_unknown_travel_fails FOR TESTING RAISING cx_static_check.
    METHODS change_locked_travel_fails  FOR TESTING RAISING cx_static_check.
ENDCLASS.

CLASS ltc_with_buffer_double IMPLEMENTATION.

  METHOD class_setup.
    "a) which BDEFs get a double; b) the BO is draft-enabled
    DATA(env_config) = cl_botd_txbufdbl_bo_test_env=>prepare_environment_config(
                         )->set_bdef_dependencies( bdef_dependencies = VALUE #( ( 'ZRAP_R_TRAVEL_###' ) )
                         )->handle_draft( bdef_dependencies = VALUE #( ( 'ZRAP_R_TRAVEL_###' ) ) ).
    environment = cl_botd_txbufdbl_bo_test_env=>create( environment_config = env_config ).
    cut = NEW #( ).
  ENDMETHOD.

  METHOD class_teardown.
    environment->destroy( ).
  ENDMETHOD.

  METHOD setup.
    "empty buffer double + no configurations for every test
    environment->clear_doubles( ).
    DATA(double) = environment->get_test_double( 'ZRAP_R_TRAVEL_###' ).
    double->configure_additional_behavior( )->set_fields_handler( fields_handler = NEW ltd_fields_handler( ) ).
  ENDMETHOD.

  METHOD create_travel_in_double.
    "test data goes into the buffer double with ordinary EML
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        CREATE FIELDS ( Description CustomerID AgencyID )
        WITH VALUE #( ( %cid = 'T1' Description = description CustomerID = '000001' AgencyID = '070001' ) )
      MAPPED DATA(mapped)
      FAILED DATA(failed).
    cl_abap_unit_assert=>assert_initial( act = failed msg = 'test data could not be created' ).
    travel_id = mapped-travel[ 1 ]-TravelID.
  ENDMETHOD.

  METHOD change_and_read_description.
    DATA(travel_id) = create_travel_in_double( 'Old' ).
    cl_abap_unit_assert=>assert_equals( exp = '00000001' act = travel_id msg = 'fields handler' ).

    "code under test
    cut->change_description( EXPORTING travel_id   = travel_id
                                       description = 'New'
                             IMPORTING failed      = DATA(failed)
                                       reported    = DATA(reported) ).

    cl_abap_unit_assert=>assert_initial( act = failed ).
    cl_abap_unit_assert=>assert_initial( act = reported ).
    cl_abap_unit_assert=>assert_equals( exp = 'New' act = cut->get_description( travel_id ) ).
  ENDMETHOD.

  METHOD change_unknown_travel_fails.
    cut->change_description( EXPORTING travel_id   = '00000099'
                                       description = 'New'
                             IMPORTING failed      = DATA(failed) ).

    cl_abap_unit_assert=>assert_equals( exp = 1 act = lines( failed-travel ) ).
    cl_abap_unit_assert=>assert_equals( exp = if_abap_behv=>cause-not_found
                                        act = failed-travel[ 1 ]-%fail-cause ).
  ENDMETHOD.

  METHOD change_locked_travel_fails.
    DATA update_instances TYPE TABLE FOR UPDATE zrap_r_travel_###\\Travel.
    DATA failed_config    TYPE RESPONSE FOR FAILED EARLY zrap_r_travel_###.

    DATA(travel_id) = create_travel_in_double( 'Old' ).

    "exactly the instance the code under test will send (incl. %control)
    update_instances = VALUE #( ( TravelID = travel_id Description = 'New'
                                  %control-Description = if_abap_behv=>mk-on ) ).
    failed_config-travel = VALUE #( ( TravelID = travel_id
                                      %update = if_abap_behv=>mk-on
                                      %fail-cause = if_abap_behv=>cause-locked ) ).

    DATA(double) = environment->get_test_double( 'ZRAP_R_TRAVEL_###' ).
    DATA(input)  = double->create_modify_input_config( )->set_instance( update_instances[ 1 ] ).
    DATA(output) = double->create_modify_output_config( )->set_failed( failed_config ).
    double->configure_additional_behavior( )->for_modify_update( )->when_input( input )->then_set_output( output ).

    cut->change_description( EXPORTING travel_id   = travel_id
                                       description = 'New'
                             IMPORTING failed      = DATA(failed) ).

    cl_abap_unit_assert=>assert_equals( exp = if_abap_behv=>cause-locked
                                        act = failed-travel[ 1 ]-%fail-cause ).
    "the forced failure means nothing was changed
    cl_abap_unit_assert=>assert_equals( exp = 'Old' act = cut->get_description( travel_id ) ).
  ENDMETHOD.

ENDCLASS.
```

**왜 이렇게 쓰나**
- `ZCL_RAP_TRAV_APPROVER_###`는 Travel BO의 **소비자**입니다. 이 클래스를 테스트할 때 BO 자체(결정·검증·권한)는 관심 밖입니다. 트랜잭션 버퍼 더블은 BO 구현을 전혀 실행하지 않고, 프레임워크가 제공하는 "기억하는 가짜 버퍼"에 대해 CREATE/UPDATE/DELETE/READ가 동작하게 합니다(참조 시나리오 `/DMO/TC_BOTD_TRAVEL_M_DEMOS`의 `ltcl_txbufdbl_variant_demos`).
- `TravelID`는 소비자에게 읽기 전용이라 테스트에서 CREATE로 넣을 수 없습니다. 그래서 필드 핸들러가 "생성 때 프레임워크 대신 키를 매기는" 역할을 합니다.
- 버퍼 더블은 액션·함수·권한을 흉내 내지 못합니다. 그래서 `approve_open_travels`(액션)와 `can_accept`(권한)는 9단계에서 EML API 목으로 테스트합니다.
- `configure_additional_behavior( )->for_modify_update( )`는 "평소처럼 동작하되 **이 입력**에만 정해진 실패를 돌려준다"는 설정입니다. 잠금 충돌처럼 실제로 만들기 어려운 상황을 재현할 때 씁니다. 입력은 소비자 코드가 보내는 것과 `%control`까지 똑같아야 맞아떨어집니다.
- 소비자가 COMMIT하지 않게 설계했기 때문에 테스트가 쉬워졌습니다. 커밋 여부는 호출자의 결정이고, 이렇게 해야 여러 소비자 호출을 한 트랜잭션으로 묶을 수도 있습니다.

**자주 나는 오류와 해결**
- 이 BO는 **late numbering**입니다. 버퍼 더블이 late numbering BO에서 `TravelID`를 필드 핸들러로 채우게 하는지, `mapped-travel[ 1 ]-TravelID`에 그 값이 돌아오는지는 로컬 자료(early numbering 예제)로 확인하지 못했습니다(실제 시스템에서 확인 필요). `mapped`에 `%pid`만 돌아오면 `create_travel_in_double`에서 `travel_id`를 상수 `'00000001'`로 돌려주세요(필드 핸들러가 첫 번째 Travel에 1을 매기므로).
- `set_instance`에 넘기는 인스턴스는 한 줄이어야 합니다(참조 예제 주석: "input instance should contain only one instance").
- 소비자가 `ZRAP_I_TRAVEL_###`(인터페이스 BDEF)를 쓰도록 바꿨다면 `set_bdef_dependencies`에도 그 이름을 넣어야 합니다. 인터페이스 BDEF를 더블 대상으로 쓸 수 있는지는 실제 시스템에서 확인 필요입니다.

**클래스 구조 해설**
- `if_botd_bufdbl_fields_handler~set_readonly_fields`는 `entity_name`, `operation`, `association_name`, `instances`(CHANGING)를 받습니다. `instances`는 일반 타입이라 파생 타입 변수에 옮겨 고친 뒤 다시 넣습니다.
- 환경 객체는 `class_setup`에서 한 번 만들고 `class_teardown`에서 `destroy`합니다. `clear_doubles`는 버퍼 내용과 설정을 지우므로 필드 핸들러는 `setup`에서 다시 설정합니다.

</details>

#### 9단계. BO를 쓰는 코드 테스트 (2): EML API 목

요구사항
1. `ZCL_RAP_TRAV_APPROVER_###`의 Test Classes 탭에 `ltc_with_eml_mock`을 추가하세요. 환경은 `cl_botd_mockemlapi_bo_test_env`(`handle_draft` 포함)입니다.
2. 테스트 3개를 만드세요.
   - `approve_only_open`: Travel 1(상태 `O`), 2(상태 `A`), 3(없음)을 요청. READ 목 설정: 입력 1·2·3 → 결과 1·2, `failed`에 3(`not_found`). 액션 목 설정: 입력 1 → 결과 1(`%param-OverallStatus = 'A'`). 기대: `accepted = [1]`, `skipped = [2]`, `failed-travel`에 3. 끝으로 `verify( )`로 READ와 MODIFY가 정확히 1번씩 불렸는지 확인합니다.
   - `approve_twice_second_locked`: 입력을 따지지 않는(`ignore_input`) 설정으로 READ는 항상 "1은 열림", 액션은 첫 번째 호출만 성공하고(`for_times( 1 )`) 두 번째 호출은 `cause-locked`로 실패하게 합니다. `approve_open_travels`를 두 번 불러 결과가 각각 성공·실패인지 확인합니다.
   - `can_accept_uses_permissions`: GET PERMISSIONS 목 설정(입력 Travel 1, 요청 `%action-acceptTravel`; 결과 `perm-o-enabled`)으로 `can_accept( 1 )`이 `abap_true`인지, 결과를 `perm-o-disabled`로 바꾸면 `abap_false`인지 확인합니다.

**확인** 세 테스트가 초록색입니다. `approve_only_open`에서 소비자 코드를 "Travel마다 EXECUTE" 하도록 일부러 바꾸면 `verify`가 실패하는지 보세요.

<details><summary>정답·해설</summary>

Test Classes 탭에 추가:

```abap
"! @testing BDEF:ZRAP_R_TRAVEL_###
CLASS ltc_with_eml_mock DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    CLASS-DATA environment TYPE REF TO if_botd_mockemlapi_bo_test_env.
    CLASS-DATA double      TYPE REF TO if_botd_mockemlapi_test_double.
    CLASS-DATA cut         TYPE REF TO zcl_rap_trav_approver_###.

    CLASS-METHODS class_setup.
    CLASS-METHODS class_teardown.
    METHODS setup.

    METHODS approve_only_open           FOR TESTING RAISING cx_static_check.
    METHODS approve_twice_second_locked FOR TESTING RAISING cx_static_check.
    METHODS can_accept_uses_permissions FOR TESTING RAISING cx_static_check.
ENDCLASS.

CLASS ltc_with_eml_mock IMPLEMENTATION.

  METHOD class_setup.
    DATA(env_config) = cl_botd_mockemlapi_bo_test_env=>prepare_environment_config(
                         )->set_bdef_dependencies( bdef_dependencies = VALUE #( ( 'ZRAP_R_TRAVEL_###' ) )
                         )->handle_draft( bdef_dependencies = VALUE #( ( 'ZRAP_R_TRAVEL_###' ) ) ).
    environment = cl_botd_mockemlapi_bo_test_env=>create( environment_config = env_config ).
    double = environment->get_test_double( 'ZRAP_R_TRAVEL_###' ).
    cut = NEW #( ).
  ENDMETHOD.

  METHOD class_teardown.
    environment->destroy( ).
  ENDMETHOD.

  METHOD setup.
    environment->clear_doubles( ).
  ENDMETHOD.

  METHOD approve_only_open.
    DATA read_instances   TYPE TABLE FOR READ IMPORT zrap_r_travel_###\\Travel.
    DATA read_result      TYPE TABLE FOR READ RESULT zrap_r_travel_###\\Travel.
    DATA read_failed      TYPE RESPONSE FOR FAILED EARLY zrap_r_travel_###.
    DATA action_instances TYPE TABLE FOR ACTION IMPORT zrap_r_travel_###\\Travel~acceptTravel.
    DATA action_result    TYPE TABLE FOR ACTION RESULT zrap_r_travel_###\\Travel~acceptTravel.

    "----- 1) READ: input = exactly what the code under test will read (%control is ignored)
    read_instances = VALUE #( ( TravelID = '00000001' )
                              ( TravelID = '00000002' )
                              ( TravelID = '00000003' ) ).
    read_result = VALUE #( ( TravelID = '00000001' OverallStatus = 'O' )
                           ( TravelID = '00000002' OverallStatus = 'A' ) ).
    read_failed-travel = VALUE #( ( TravelID = '00000003' %fail-cause = if_abap_behv=>cause-not_found ) ).

    DATA(read_input_builder) = cl_botd_mockemlapi_bldrfactory=>get_input_config_builder( )->for_read( ).
    DATA(read_input) = read_input_builder->build_input_for_eml(
                         )->add_entity_part( read_input_builder->build_entity_part( 'ZRAP_R_TRAVEL_###'
                                               )->set_instances_for_read( read_instances ) ).
    DATA(read_output) = cl_botd_mockemlapi_bldrfactory=>get_output_config_builder( )->for_read(
                          )->build_output_for_eml( )->set_result_for_read( read_result
                          )->set_failed( read_failed ).
    double->configure_call( )->for_read( )->when_input( read_input )->then_set_output( read_output ).

    "----- 2) EXECUTE acceptTravel only for travel 1
    action_instances = VALUE #( ( TravelID = '00000001' ) ).
    action_result    = VALUE #( ( TravelID = '00000001'
                                  %param-TravelID = '00000001' %param-OverallStatus = 'A' ) ).

    DATA(modify_input_builder) = cl_botd_mockemlapi_bldrfactory=>get_input_config_builder( )->for_modify( ).
    DATA(modify_input) = modify_input_builder->build_input_for_eml(
                           )->add_entity_part( modify_input_builder->build_entity_part( 'ZRAP_R_TRAVEL_###'
                                                 )->set_instances_for_action( instances = action_instances ) ).
    DATA(modify_output) = cl_botd_mockemlapi_bldrfactory=>get_output_config_builder( )->for_modify(
                            )->build_output_for_eml( )->set_result_for_action( result = action_result ).
    double->configure_call( )->for_modify( )->when_input( modify_input )->then_set_output( modify_output ).

    "----- code under test
    DATA(approval) = cut->approve_open_travels( VALUE #( ( '00000001' ) ( '00000002' ) ( '00000003' ) ) ).

    "----- state verification
    cl_abap_unit_assert=>assert_equals( exp = VALUE zcl_rap_trav_approver_###=>tt_travel_ids( ( '00000001' ) )
                                        act = approval-accepted ).
    cl_abap_unit_assert=>assert_equals( exp = VALUE zcl_rap_trav_approver_###=>tt_travel_ids( ( '00000002' ) )
                                        act = approval-skipped ).
    cl_abap_unit_assert=>assert_equals( exp = 1 act = lines( approval-failed-travel ) ).
    cl_abap_unit_assert=>assert_equals( exp = '00000003' act = approval-failed-travel[ 1 ]-TravelID ).

    "----- behavior verification: one READ and one MODIFY - no EML inside a loop
    double->verify( )->read( read_input )->is_called_times( times = 1 ).
    double->verify( )->modify( modify_input )->is_called_times( times = 1 ).
  ENDMETHOD.

  METHOD approve_twice_second_locked.
    DATA read_result   TYPE TABLE FOR READ RESULT zrap_r_travel_###\\Travel.
    DATA action_result TYPE TABLE FOR ACTION RESULT zrap_r_travel_###\\Travel~acceptTravel.
    DATA failed_locked TYPE RESPONSE FOR FAILED EARLY zrap_r_travel_###.

    "READ: whatever is asked, travel 1 is open
    read_result = VALUE #( ( TravelID = '00000001' OverallStatus = 'O' ) ).
    DATA(read_output) = cl_botd_mockemlapi_bldrfactory=>get_output_config_builder( )->for_read(
                          )->build_output_for_eml( )->set_result_for_read( read_result ).
    double->configure_call( )->for_read( )->ignore_input( )->then_set_output( read_output ).

    "MODIFY: 1st call succeeds, 2nd call fails with 'locked'
    action_result = VALUE #( ( TravelID = '00000001' %param-OverallStatus = 'A' ) ).
    failed_locked-travel = VALUE #( ( TravelID = '00000001'
                                      %action-acceptTravel = if_abap_behv=>mk-on
                                      %fail-cause = if_abap_behv=>cause-locked ) ).

    DATA(output_builder) = cl_botd_mockemlapi_bldrfactory=>get_output_config_builder( )->for_modify( ).
    DATA(success_output) = output_builder->build_output_for_eml( )->set_result_for_action( result = action_result ).
    DATA(locked_output)  = output_builder->build_output_for_eml( )->set_failed( failed_locked ).

    double->configure_call(
      )->for_modify(
      )->ignore_input(
      )->then_set_output( success_output )->for_times( 1
      )->then_set_output( locked_output )->for_times( 1 ).

    DATA(first)  = cut->approve_open_travels( VALUE #( ( '00000001' ) ) ).
    DATA(second) = cut->approve_open_travels( VALUE #( ( '00000001' ) ) ).

    cl_abap_unit_assert=>assert_equals( exp = 1 act = lines( first-accepted ) ).
    cl_abap_unit_assert=>assert_initial( act = first-failed ).

    cl_abap_unit_assert=>assert_initial( act = second-accepted ).
    cl_abap_unit_assert=>assert_equals( exp = if_abap_behv=>cause-locked
                                        act = second-failed-travel[ 1 ]-%fail-cause ).
  ENDMETHOD.

  METHOD can_accept_uses_permissions.
    DATA instances TYPE TABLE FOR PERMISSIONS KEY zrap_r_travel_###.
    DATA request   TYPE STRUCTURE FOR PERMISSIONS REQUEST zrap_r_travel_###.
    DATA enabled   TYPE STRUCTURE FOR PERMISSIONS RESULT zrap_r_travel_###.
    DATA disabled  TYPE STRUCTURE FOR PERMISSIONS RESULT zrap_r_travel_###.

    "input = exactly what can_accept sends
    instances = VALUE #( ( %key-TravelID = '00000001' ) ).
    request-%action-acceptTravel = if_abap_behv=>mk-on.

    enabled  = VALUE #( instances = VALUE #( ( %key-TravelID = '00000001'
                                               %action-acceptTravel = if_abap_behv=>perm-o-enabled ) ) ).
    disabled = VALUE #( instances = VALUE #( ( %key-TravelID = '00000001'
                                               %action-acceptTravel = if_abap_behv=>perm-o-disabled ) ) ).

    DATA(input_builder) = cl_botd_mockemlapi_bldrfactory=>get_input_config_builder( )->for_get_permissions( ).
    "ONLY INSTANCE in the code under test <-> permissions_only-instance here
    DATA(input) = input_builder->build_input_for_eml( if_abap_behv=>permissions_only-instance
                    )->add_entity_part( input_builder->build_entity_part( 'ZRAP_R_TRAVEL_###'
                                          )->set_instances( instances
                                          )->set_request( request ) ).

    DATA(output_builder) = cl_botd_mockemlapi_bldrfactory=>get_output_config_builder( )->for_get_permissions( ).

    "1) enabled
    double->configure_call( )->for_get_permissions( )->when_input( input
          )->then_set_output( output_builder->build_output_for_eml( )->set_result( enabled ) ).
    cl_abap_unit_assert=>assert_true( act = cut->can_accept( '00000001' ) ).

    "2) disabled
    environment->clear_doubles( ).
    double->configure_call( )->for_get_permissions( )->when_input( input
          )->then_set_output( output_builder->build_output_for_eml( )->set_result( disabled ) ).
    cl_abap_unit_assert=>assert_false( act = cut->can_accept( '00000001' ) ).
  ENDMETHOD.

ENDCLASS.
```

**왜 이렇게 쓰나**
- EML API 목은 "이 EML 입력이 오면 이 응답을 돌려줘"라고 **설정**하는 방식입니다. 액션 결과, 권한, 잠금 실패처럼 버퍼 더블이 만들 수 없는 응답을 자유롭게 줄 수 있습니다. 대신 입력이 정확히 맞아야 합니다(`%control`은 비교하지 않음). 그래서 입력 표는 소비자 코드가 만드는 것과 같은 방식으로 만듭니다.
- **상태 검증**(결과 값 비교)과 **행동 검증**(`verify( )->...->is_called_times( )`)을 함께 씁니다. 행동 검증은 "한 번의 READ, 한 번의 EXECUTE"라는 성능 규칙을 지키게 합니다.
- `ignore_input`은 입력을 몰라도 되거나 관심 없을 때, `then_set_output( ... )->for_times( n )`을 이어 붙이면 호출 순서에 따라 다른 응답을 줍니다(참조 예제의 `for_times_configuration`).
- GET PERMISSIONS 목은 `build_input_for_eml( if_abap_behv=>permissions_only-instance )`처럼 소비자 코드의 `ONLY INSTANCE`와 같은 범위를 지정해야 맞아떨어집니다.

**버퍼 더블과 목, 언제 무엇을?**

| 상황 | 고르는 것 |
|---|---|
| CRUD + 읽기만 하는 소비자, 실제와 비슷한 데이터 흐름을 보고 싶음 | 트랜잭션 버퍼 더블 |
| 액션·함수·권한·잠금·특정 실패 응답이 필요 | EML API 목 |
| 몇 번 불렀는지까지 검사 | EML API 목(`verify`) |
| 소비자 안에 EML 문장이 많고 입력을 일일이 맞추기 어려움 | 버퍼 더블(+ 필요한 곳만 `configure_additional_behavior`) |

**자주 나는 오류와 해결**
- 설정과 맞지 않는 입력이 오면 목은 빈 응답을 돌려줍니다. 결과가 비어 있으면 먼저 입력 표(키 값, `%is_draft`, 줄 순서)를 소비자 코드와 비교하세요.
- 같은 `double`에 대해 설정을 바꿀 때는 `environment->clear_doubles( )`로 앞 설정을 지운 뒤 다시 설정합니다(`can_accept_uses_permissions` 2번).
- `is_called_times( times = 0 )`처럼 "불리지 않았음"을 검사하는 방법이 지원되는지는 로컬 자료로 확인하지 못했습니다(실제 시스템에서 확인 필요).
- `if_botd_mockemlapi_test_double`, `if_botd_mockemlapi_bo_test_env` 등 인터페이스 이름은 참조 시나리오의 선언을 따랐습니다. 이름을 못 찾으면 `DATA(...)` 인라인 선언으로 바꾸세요.

**클래스 구조 해설**
- 입력 빌더(`get_input_config_builder( )->for_read( )/for_modify( )/for_get_permissions( )`)는 "EML 문장 한 개"를, `build_entity_part( '엔터티' )`는 그 문장의 `ENTITY` 한 부분을, `set_instances_for_...`는 연산 하나를 나타냅니다. 소비자 EML 문장의 구조를 그대로 옮겨 적는다고 생각하면 됩니다.
- 출력 빌더는 응답 파라미터(`MAPPED`, `FAILED`, `REPORTED`, `RESULT`)를 하나씩 채웁니다.

</details>


#### 10단계. CDS 뷰 테스트: 계산 필드, CASE, 연관

요구사항
1. 조회용 CDS 뷰 엔터티 `ZRAP_I_TRAVEL_KPI_###`를 만드세요. 원본은 `ZRAP_ATRAV_###`(별칭 `Travel`)입니다.
   - 연관 `_Customer`: `/DMO/I_Customer`로, 카디널리티 `[0..1]`, 조건은 고객 번호
   - 요소: `TravelID`(키), `CustomerID`, `CustomerName`(연관 경로로 `_Customer`의 `LastName`), `BeginDate`, `EndDate`, `TravelDays`(시작일·종료일 중 하나라도 비어 있으면 0, 아니면 두 날짜 사이 일수 + 1, `dats_days_between` 사용), `TotalPrice`, `CurrencyCode`, `StatusText`(`O`→`Open`, `A`→`Accepted`, `X`→`Rejected`, 그 밖→`Unknown`, 길이 10 문자로 `cast`), 연관 `_Customer` 노출
2. 테스트 전용 전역 클래스 `ZTC_RAP_TRAVEL_KPI_###`를 만드세요.
   - `class_setup`: `cl_cds_test_environment=>create( )`로 이 뷰의 의존성(`ZRAP_ATRAV_###`, `/DMO/I_Customer`)을 더블로 바꿉니다. 노출된 연관을 ABAP SQL 경로로 읽는 테스트도 하므로 `test_associations = 'X'`를 줍니다.
   - `travel_days`: 하루 여행(시작 = 종료) → 1, 10일 여행 → 10, 날짜 없음 → 0
   - `status_text`: `O`, `A`, `X`, 빈 값 → 각각의 텍스트
   - `customer_name_optional`: 더블에 없는 고객의 Travel도 결과에 나오고 `CustomerName`만 비어 있음(`[0..1]` 연관 경로 = left outer join)
   - `path_via_association`: `SELECT ... \_Customer-FirstName`으로 노출된 연관을 따라 이름을 읽음

**직접 추가할 어노테이션**
- `@AccessControl.authorizationCheck` — 이 뷰에 접근 제어(DCL)를 검사할지 정함(조회 테스트용이라 검사 불필요)
- `@EndUserText.label` — 뷰의 설명 텍스트
- `@Metadata.ignorePropagatedAnnotations` — 원본 뷰·테이블에서 넘어오는 요소 어노테이션을 무시해 이 뷰의 어노테이션만 쓰게 함
- `@Semantics.amount.currencyCode` — 금액 요소가 어느 통화 요소를 따르는지 알려 줌

**확인** 뷰가 활성화되고 Data Preview에 실제 데이터의 `TravelDays`, `StatusText`가 보입니다. 테스트 클래스를 실행하면 4개 테스트가 초록색입니다.

<details><summary>정답·해설</summary>

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED      // no DCL check for this read-only KPI view
@EndUserText.label: 'Travel KPI (unit test demo)'     // description shown in ADT
@Metadata.ignorePropagatedAnnotations: true           // use only the annotations written here
define view entity ZRAP_I_TRAVEL_KPI_###
  as select from zrap_atrav_### as Travel

  association [0..1] to /DMO/I_Customer as _Customer
    on $projection.CustomerID = _Customer.CustomerID
{
  key Travel.travel_id                                   as TravelID,
      Travel.customer_id                                 as CustomerID,

      // path expression = left outer join to the customer view
      _Customer.LastName                                 as CustomerName,

      Travel.begin_date                                  as BeginDate,
      Travel.end_date                                    as EndDate,

      // calculated field: number of travel days, 0 if a date is missing
      case
        when Travel.begin_date = '00000000' or Travel.end_date = '00000000'
          then 0
        else dats_days_between( Travel.begin_date, Travel.end_date ) + 1
      end                                                as TravelDays,

      @Semantics.amount.currencyCode: 'CurrencyCode'     // amount follows CurrencyCode
      Travel.total_price                                 as TotalPrice,
      Travel.currency_code                               as CurrencyCode,

      // simple CASE with a fixed result type
      cast( case Travel.overall_status
              when 'O' then 'Open'
              when 'A' then 'Accepted'
              when 'X' then 'Rejected'
              else 'Unknown'
            end as abap.char( 10 ) )                     as StatusText,

      // exposed association (can be followed by consumers)
      _Customer
}
```

(→ 어노테이션 탭: @AccessControl.authorizationCheck, @EndUserText.label, @Metadata.ignorePropagatedAnnotations, @Semantics.amount.currencyCode)

```abap
"! Unit tests for the CDS view entity ZRAP_I_TRAVEL_KPI_###
"! @testing DDLS:ZRAP_I_TRAVEL_KPI_###
CLASS ztc_rap_travel_kpi_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC
  FOR TESTING
  RISK LEVEL HARMLESS
  DURATION SHORT.

  PRIVATE SECTION.
    TYPES tt_travel_db TYPE STANDARD TABLE OF zrap_atrav_### WITH EMPTY KEY.
    TYPES tt_customer  TYPE STANDARD TABLE OF /dmo/i_customer WITH EMPTY KEY.

    CLASS-DATA cds_test_environment TYPE REF TO if_cds_test_environment.

    CLASS-METHODS class_setup.
    CLASS-METHODS class_teardown.
    METHODS setup.

    METHODS travel_days            FOR TESTING.
    METHODS status_text            FOR TESTING.
    METHODS customer_name_optional FOR TESTING.
    METHODS path_via_association   FOR TESTING.
ENDCLASS.



CLASS ztc_rap_travel_kpi_### IMPLEMENTATION.

  METHOD class_setup.
    "doubles for the first-level dependencies: zrap_atrav_### and /DMO/I_Customer;
    "test_associations: exposed associations can be followed in ABAP SQL in the test
    cds_test_environment = cl_cds_test_environment=>create( i_for_entity      = 'ZRAP_I_TRAVEL_KPI_###'
                                                            test_associations = 'X' ).
  ENDMETHOD.

  METHOD setup.
    cds_test_environment->clear_doubles( ).
  ENDMETHOD.

  METHOD class_teardown.
    cds_test_environment->destroy( ).
  ENDMETHOD.

  METHOD travel_days.
    DATA(today) = cl_abap_context_info=>get_system_date( ).

    DATA(travels) = VALUE tt_travel_db(
      ( travel_id = '00000001'  begin_date = today      end_date = today )
      ( travel_id = '00000002'  begin_date = today      end_date = today + 9 )
      ( travel_id = '00000003' ) ).
    cds_test_environment->insert_test_data( i_data = travels ).

    SELECT FROM zrap_i_travel_kpi_###
      FIELDS TravelID, TravelDays
      ORDER BY TravelID
      INTO TABLE @DATA(result).                         "#EC CI_NOWHERE

    cl_abap_unit_assert=>assert_equals( exp = 3  act = lines( result ) ).
    cl_abap_unit_assert=>assert_equals( exp = 1  act = result[ 1 ]-TravelDays msg = 'one-day trip' ).
    cl_abap_unit_assert=>assert_equals( exp = 10 act = result[ 2 ]-TravelDays msg = 'ten-day trip' ).
    cl_abap_unit_assert=>assert_equals( exp = 0  act = result[ 3 ]-TravelDays msg = 'no dates' ).
  ENDMETHOD.

  METHOD status_text.
    DATA(travels) = VALUE tt_travel_db( ( travel_id = '00000001' overall_status = 'O' )
                                        ( travel_id = '00000002' overall_status = 'A' )
                                        ( travel_id = '00000003' overall_status = 'X' )
                                        ( travel_id = '00000004' ) ).
    cds_test_environment->insert_test_data( i_data = travels ).

    SELECT FROM zrap_i_travel_kpi_###
      FIELDS TravelID, StatusText
      ORDER BY TravelID
      INTO TABLE @DATA(result).                         "#EC CI_NOWHERE

    cl_abap_unit_assert=>assert_equals( exp = 'Open'     act = result[ 1 ]-StatusText ).
    cl_abap_unit_assert=>assert_equals( exp = 'Accepted' act = result[ 2 ]-StatusText ).
    cl_abap_unit_assert=>assert_equals( exp = 'Rejected' act = result[ 3 ]-StatusText ).
    cl_abap_unit_assert=>assert_equals( exp = 'Unknown'  act = result[ 4 ]-StatusText ).
  ENDMETHOD.

  METHOD customer_name_optional.
    DATA(customers) = VALUE tt_customer( ( CustomerID = '000001' FirstName = 'Yurim' LastName = 'Lee' ) ).
    cds_test_environment->insert_test_data( i_data = customers ).

    DATA(travels) = VALUE tt_travel_db( ( travel_id = '00000001' customer_id = '000001' )
                                        ( travel_id = '00000002' customer_id = '000999' ) ).
    cds_test_environment->insert_test_data( i_data = travels ).

    SELECT FROM zrap_i_travel_kpi_###
      FIELDS TravelID, CustomerName
      ORDER BY TravelID
      INTO TABLE @DATA(result).                         "#EC CI_NOWHERE

    "[0..1] path = left outer join: the travel without customer is NOT lost
    cl_abap_unit_assert=>assert_equals( exp = 2 act = lines( result ) ).
    cl_abap_unit_assert=>assert_equals( exp = 'Lee' act = result[ 1 ]-CustomerName ).
    cl_abap_unit_assert=>assert_initial( act = result[ 2 ]-CustomerName ).
  ENDMETHOD.

  METHOD path_via_association.
    DATA(customers) = VALUE tt_customer( ( CustomerID = '000001' FirstName = 'Yurim' LastName = 'Lee' ) ).
    cds_test_environment->insert_test_data( i_data = customers ).
    DATA(travels) = VALUE tt_travel_db( ( travel_id = '00000001' customer_id = '000001' ) ).
    cds_test_environment->insert_test_data( i_data = travels ).

    "follow the exposed association in ABAP SQL
    SELECT FROM zrap_i_travel_kpi_###
      FIELDS TravelID, \_Customer-FirstName AS FirstName
      INTO TABLE @DATA(result).                         "#EC CI_NOWHERE

    cl_abap_unit_assert=>assert_equals( exp = 'Yurim' act = result[ 1 ]-FirstName ).
  ENDMETHOD.

ENDCLASS.
```

**왜 이렇게 쓰나**
- CDS 뷰의 계산(CASE, 날짜 함수, 조인)은 DB에서 실행되므로 ABAP 코드처럼 디버깅할 수 없습니다. 테스트 더블로 **경계값**(같은 날, 빈 날짜, 없는 고객, 알 수 없는 상태)을 넣고 결과를 확인하는 것이 가장 확실한 검증 방법입니다.
- `create( i_for_entity = ... )`는 테스트 대상 뷰는 그대로 두고 그 뷰가 읽는 것(`ZRAP_ATRAV_###`, `/DMO/I_Customer`)만 더블로 바꿉니다. 그래서 `insert_test_data`에는 테이블 타입과 `/DMO/I_Customer` 타입의 데이터를 넣고, SELECT는 테스트 대상 뷰에서 합니다.
- `test_associations = 'X'`는 노출된 연관을 따라가는 ABAP SQL 경로(`\_Customer-FirstName`)도 더블을 읽게 합니다(cheat sheet 예제 `ztcl_demo_abap_unit_tdf_testcl`에서 이 파라미터를 사용). 정확한 의미와 기본값은 실제 시스템의 클래스 설명에서 확인하세요(실제 시스템에서 확인 필요).
- `customer_name_optional`은 "경로 표현식은 left outer join"이라는 CDS 규칙을 테스트로 남깁니다. 누군가 나중에 이 경로를 `inner join`으로 바꾸면 Travel이 사라지는 버그를 바로 잡아냅니다.
- `"! @testing DDLS:...` 표기는 로컬 자료에서 `BDEF:`와 `SRVB:`만 확인했습니다. `DDLS:`가 받아들여지는지는 실제 시스템에서 확인 필요입니다. 받아들여지지 않으면 이 줄을 지워도 테스트 실행에는 지장이 없습니다.

**자주 나는 오류와 해결**
- `dats_days_between`에 빈 날짜(`00000000`)를 넣으면 DB에 따라 오류가 날 수 있어 CASE로 먼저 걸렀습니다.
- `$projection.CustomerID`에서 오류가 나면 `Travel.customer_id = _Customer.CustomerID`로 바꿔도 됩니다.
- `insert_test_data`에서 "not a dependency" 계열 오류: 넣으려는 데이터의 타입이 이 뷰의 직접 의존성이 아닙니다(예: `/dmo/customer` 테이블 타입). `/DMO/I_Customer` 타입으로 넣으세요.

</details>

#### 11단계. OData 수준 테스트와 마무리: 로컬 클라이언트 프록시, 커버리지

요구사항
1. 서비스 바인딩 `ZRAP_API_TRAVEL_O2_###`를 만드세요. 서비스 정의 `ZRAP_UI_TRAVEL_###`, 바인딩 유형 **OData V2 - Web API**. 활성화 후 **Publish**합니다.
2. 테스트 전용 전역 클래스 `ZTC_RAP_TRAVEL_ODATA_###`를 만드세요(`"! @testing SRVB:ZRAP_API_TRAVEL_O2_###`).
   - `class_setup`: `cl_web_odata_client_factory=>create_v2_local_proxy( )`로 이 바인딩의 로컬 클라이언트 프록시를 만들고, CDS 테스트 환경(`ZRAP_C_TRAVEL_###`, `ZRAP_C_BOOKING_###`, 기본 의존성까지 더블)과 SQL 테스트 환경(`/DMO/AGENCY`, `/DMO/CUSTOMER`, `/DMO/CARRIER`, `/DMO/FLIGHT`, `ZRAP_CTRL_###`, `ZRAP_TLOG_###`, `ZRAP_EVLOG_###`)을 만듭니다.
   - `setup`: 더블을 비우고 여행사 `070001`·`070002`, 고객 `000001`, 활성 Travel `00000101`(여행사 `070001`, 상태 `O`, 설명 `Mock Travel`)과 `00000102`(여행사 `070002`)를 넣습니다.
   - `create_via_odata`: 엔터티 집합 `Travel`에 POST. 응답의 `OverallStatus = 'O'`, `TravelID`가 비어 있지 않음, 그리고 EML로 다시 읽어 설명이 같은지 확인합니다.
   - `read_list_with_filter`: `AgencyID eq '070001'` 필터 + `$top=50`으로 GET. 결과 1건(`00000101`).
   - `update_with_etag`: `00000101`을 키로 읽어 ETag를 얻고, `If-Match`로 PATCH(설명 `Updated via OData`). EML로 읽어 바뀐 설명을 확인합니다.
3. 마무리로 패키지 `ZRAP_###` 전체의 테스트를 실행하고 커버리지를 측정하세요.

**확인** 세 테스트가 초록색입니다. 패키지에서 커버리지를 측정하면 ABAP Coverage 뷰에 `ZBP_RAP_R_TRAVEL_###`의 문장 커버리지가 나옵니다. `lhc_travel`에서 테스트되지 않은 메서드(예: `copyTravel`, `addServiceFee`)가 빨간색으로 보이면 정상입니다. 그 메서드의 테스트를 직접 추가해 보세요.

<details><summary>정답·해설</summary>

```abap
"! OData-level tests through the local client proxy (no HTTP)
"! @testing SRVB:ZRAP_API_TRAVEL_O2_###
CLASS ztc_rap_travel_odata_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC
  FOR TESTING
  RISK LEVEL HARMLESS
  DURATION SHORT.

  PRIVATE SECTION.
    TYPES: BEGIN OF ty_entity_key,
             TravelID TYPE /dmo/travel_id,
           END OF ty_entity_key.

    CLASS-DATA client_proxy         TYPE REF TO /iwbep/if_cp_client_proxy.
    CLASS-DATA cds_test_environment TYPE REF TO if_cds_test_environment.
    CLASS-DATA sql_test_environment TYPE REF TO if_osql_test_environment.

    CLASS-METHODS class_setup RAISING cx_static_check.
    CLASS-METHODS class_teardown.
    METHODS setup.
    METHODS teardown.

    METHODS create_via_odata      FOR TESTING RAISING cx_static_check.
    METHODS read_list_with_filter FOR TESTING RAISING cx_static_check.
    METHODS update_with_etag      FOR TESTING RAISING cx_static_check.
ENDCLASS.



CLASS ztc_rap_travel_odata_### IMPLEMENTATION.

  METHOD class_setup.
    "local proxy: runs the OData service in this session, no HTTP call
    client_proxy = cl_web_odata_client_factory=>create_v2_local_proxy(
                     VALUE #( service_id      = 'ZRAP_API_TRAVEL_O2_###'
                              service_version = '0001' ) ).

    "the service reads the projections -> double their base tables as well
    cds_test_environment = cl_cds_test_environment=>create_for_multiple_cds(
                             i_for_entities = VALUE #(
                               ( i_for_entity = 'ZRAP_C_TRAVEL_###'  i_select_base_dependencies = abap_true )
                               ( i_for_entity = 'ZRAP_C_BOOKING_###' i_select_base_dependencies = abap_true ) ) ).

    sql_test_environment = cl_osql_test_environment=>create(
                             i_dependency_list = VALUE #( ( '/DMO/AGENCY' )
                                                          ( '/DMO/CUSTOMER' )
                                                          ( '/DMO/CARRIER' )
                                                          ( '/DMO/FLIGHT' )
                                                          ( 'ZRAP_CTRL_###' )
                                                          ( 'ZRAP_TLOG_###' )
                                                          ( 'ZRAP_EVLOG_###' ) ) ).
  ENDMETHOD.

  METHOD setup.
    DATA agencies  TYPE STANDARD TABLE OF /dmo/agency    WITH EMPTY KEY.
    DATA customers TYPE STANDARD TABLE OF /dmo/customer  WITH EMPTY KEY.
    DATA travels   TYPE STANDARD TABLE OF zrap_atrav_### WITH EMPTY KEY.

    cds_test_environment->clear_doubles( ).
    sql_test_environment->clear_doubles( ).

    agencies  = VALUE #( ( agency_id = '070001' name = 'Agency 1' country_code = 'DE' )
                         ( agency_id = '070002' name = 'Agency 2' country_code = 'DE' ) ).
    customers = VALUE #( ( customer_id = '000001' last_name = 'Lee' ) ).
    sql_test_environment->insert_test_data( agencies ).
    sql_test_environment->insert_test_data( customers ).

    DATA(begin_date) = cl_abap_context_info=>get_system_date( ) + 10.
    travels = VALUE #( customer_id = '000001' begin_date = begin_date end_date = begin_date + 5
                       currency_code = 'EUR' overall_status = 'O'
                       ( travel_id = '00000101' agency_id = '070001' description = 'Mock Travel' )
                       ( travel_id = '00000102' agency_id = '070002' description = 'Other Travel' ) ).
    cds_test_environment->insert_test_data( travels ).
  ENDMETHOD.

  METHOD teardown.
    ROLLBACK ENTITIES.                                 "#EC CI_ROLLBACK
  ENDMETHOD.

  METHOD class_teardown.
    cds_test_environment->destroy( ).
    sql_test_environment->destroy( ).
  ENDMETHOD.


  METHOD create_via_odata.
    DATA response_data TYPE zrap_c_travel_###.

    "business data typed with the projection = the OData entity type
    DATA(business_data) = VALUE zrap_c_travel_###(
                            AgencyID     = '070001'
                            CustomerID   = '000001'
                            BeginDate    = cl_abap_context_info=>get_system_date( ) + 10
                            EndDate      = cl_abap_context_info=>get_system_date( ) + 15
                            BookingFee   = '15.00'
                            CurrencyCode = 'EUR'
                            Description  = 'Created via OData' ).

    DATA(request) = client_proxy->create_resource_for_entity_set( 'Travel' )->create_request_for_create( ).
    request->set_business_data( business_data ).
    DATA(response) = request->execute( ).
    cl_abap_unit_assert=>assert_bound( act = response ).

    response->get_business_data( IMPORTING es_business_data = response_data ).
    cl_abap_unit_assert=>assert_equals( exp = 'O' act = response_data-OverallStatus msg = 'setInitialValues' ).
    cl_abap_unit_assert=>assert_not_initial( act = response_data-TravelID msg = 'late numbering key' ).

    "same data visible through EML on the projection
    READ ENTITIES OF zrap_c_travel_###
      ENTITY Travel
        FIELDS ( Description ) WITH VALUE #( ( TravelID = response_data-TravelID ) )
      RESULT DATA(read_result)
      FAILED DATA(failed).
    cl_abap_unit_assert=>assert_initial( act = failed ).
    cl_abap_unit_assert=>assert_equals( exp = business_data-Description act = read_result[ 1 ]-Description ).
  ENDMETHOD.

  METHOD read_list_with_filter.
    DATA agency_range  TYPE RANGE OF /dmo/agency_id.
    DATA business_data TYPE STANDARD TABLE OF zrap_c_travel_### WITH EMPTY KEY.

    agency_range = VALUE #( ( sign = 'I' option = 'EQ' low = '070001' ) ).

    DATA(request) = client_proxy->create_resource_for_entity_set( 'Travel' )->create_request_for_read( ).

    "$filter=AgencyID eq '070001' - property names in upper case
    DATA(filter_factory) = request->create_filter_factory( ).
    DATA(filter) = filter_factory->create_by_range( iv_property_path = 'AGENCYID'
                                                    it_range         = agency_range ).
    request->set_filter( filter ).
    request->set_top( 50 )->set_skip( 0 ).

    DATA(response) = request->execute( ).
    response->get_business_data( IMPORTING et_business_data = business_data ).

    cl_abap_unit_assert=>assert_equals( exp = 1 act = lines( business_data ) ).
    cl_abap_unit_assert=>assert_equals( exp = '00000101' act = business_data[ 1 ]-TravelID ).
  ENDMETHOD.

  METHOD update_with_etag.
    DATA business_data TYPE zrap_c_travel_###.

    DATA(entity_key) = VALUE ty_entity_key( TravelID = '00000101' ).
    DATA(resource) = client_proxy->create_resource_for_entity_set( 'Travel' )->navigate_with_key( entity_key ).

    "1) GET the entity to obtain its ETag (etag master LocalLastChangedAt)
    DATA(read_response) = resource->create_request_for_read( )->execute( ).

    "2) PATCH only the description, with If-Match
    business_data-Description = 'Updated via OData'.
    DATA(update_request) = resource->create_request_for_update( /iwbep/if_cp_request_update=>gcs_update_semantic-patch ).
    update_request->set_business_data( is_business_data    = business_data
                                       it_provided_property = VALUE #( ( `DESCRIPTION` ) ) ).
    update_request->set_if_match( read_response->get_etag( ) ).
    update_request->execute( ).

    "3) check through EML
    READ ENTITIES OF zrap_c_travel_###
      ENTITY Travel
        FIELDS ( Description ) WITH VALUE #( ( TravelID = '00000101' ) )
      RESULT DATA(read_result).
    cl_abap_unit_assert=>assert_equals( exp = 'Updated via OData' act = read_result[ 1 ]-Description ).
  ENDMETHOD.

ENDCLASS.
```

**TEST-SEAM으로 번호 범위를 HARMLESS하게 테스트하기(6단계 연결)**

R-04 `adjust_numbers`의 번호 범위 블록을 시임으로 감쌉니다(행동 풀 Local Types 탭, 세이버 구현).

```abap
      TEST-SEAM number_range.
        IF c_use_number_range = abap_true.
          TRY.
              cl_numberrange_runtime=>number_get(
                EXPORTING
                  nr_range_nr       = '01'
                  object            = 'ZRAP_NR_###'
                  quantity          = CONV #( lines( mapped-travel ) )
                IMPORTING
                  number            = DATA(number_range_key)
                  returncode        = DATA(number_range_return_code)
                  returned_quantity = DATA(number_range_returned_quantity) ).
              IF number_range_returned_quantity = lines( mapped-travel ).
                travel_id_max = number_range_key - number_range_returned_quantity.
                number_ok = abap_true.
              ENDIF.
            CATCH cx_number_ranges.
              number_ok = abap_false.
          ENDTRY.
        ENDIF.
      END-TEST-SEAM.
```

6단계 `ltc_saver_numbers`의 `RISK LEVEL`을 `HARMLESS`로 바꾸고, 테스트 메서드 맨 앞(`adjust_numbers` 호출 전)에 넣습니다.

```abap
    "replace the number range call: behave as if no number range were available
    TEST-INJECTION number_range.
      number_ok = abap_false.
    END-TEST-INJECTION.
```

이제 `adjust_numbers`는 더블(빈 `ZRAP_ATRAV_###`)에 대한 `SELECT MAX` 경로를 타므로 결과가 항상 `00000001`, `00000002`입니다. 단언을 `exp = '00000001'`처럼 정확한 값으로 바꿀 수 있습니다. 시임 안의 인라인 선언(`DATA(number_range_key)`)이 문제가 되면 선언을 시임 앞으로 옮기세요. 행동 풀의 로컬 클래스에서 TEST-SEAM을 쓸 수 있는지는 실제 시스템에서 확인 필요입니다.

**왜 이렇게 쓰나**
- 로컬 클라이언트 프록시는 HTTP 없이 같은 세션에서 OData 요청을 처리합니다. 서비스 바인딩 → 서비스 정의 → 프로젝션 → BO → 저장까지 **전체 스택**을 한 번에 검사하므로, 프로젝션의 노출 이름(`Travel`), 프로젝션 BDEF에서 `use`하지 않은 연산, ETag 처리 같은 "BO 단위 테스트로는 안 보이는" 오류를 잡습니다(RAP400 ex4와 같은 구조).
- V2 로컬 프록시 API(`create_v2_local_proxy`, `service_id`, `service_version`)는 RAP400 예제로 확인한 이름입니다. OData V4 바인딩(`ZRAP_API_TRAVEL_O4_###`)용 로컬 프록시 메서드와 그 파라미터는 로컬 자료에서 확인하지 못했습니다(실제 시스템에서 확인 필요). 그래서 이 단계는 테스트용 V2 Web API 바인딩을 따로 만들었습니다.
- `i_select_base_dependencies = abap_true`는 프로젝션 → R 뷰 → 테이블까지 내려가 맨 아래 테이블을 더블로 바꿉니다. OData 요청이 어느 층을 거치든 테스트 데이터만 보게 됩니다.
- Web API 바인딩은 UI가 아닌 시스템 간 연동용입니다. draft BO를 Web API로 노출하면 draft를 거치지 않고 활성 인스턴스를 바로 만들고 바꾸는 것으로 알고 있으나, 이 BO에서 실제로 그렇게 동작하는지는 실제 시스템에서 확인 필요입니다. UI(V2/V4 UI) 바인딩으로 테스트하면 생성이 draft로 처리되어 `Activate`까지 요청해야 합니다.
- PATCH에는 `If-Match`가 필요합니다. BDEF의 `etag master LocalLastChangedAt` 때문입니다. `set_if_match`를 빼고 실행해 오류가 나는지 보는 것도 좋은 연습입니다.

**마무리: 테스트 실행과 커버리지**
- 클래스 하나: 편집기에서 `Ctrl+Shift+F10`. 패키지 전체: Project Explorer에서 `ZRAP_###` 오른쪽 클릭 → Run As → ABAP Unit Test.
- 커버리지: `Ctrl+Shift+F11`(Coverage As → ABAP Unit Test). ABAP Coverage 뷰에서 문장·분기 커버리지를 보고, 편집기의 초록/빨강 표시로 실행되지 않은 줄을 찾습니다.
- `"! @testing BDEF:`/`SRVB:` 연결 덕분에 BDEF나 서비스 바인딩에서 테스트를 실행해도 행동 풀 밖의 테스트 클래스(7, 11단계)가 함께 실행됩니다.
- RAP와 무관한 일반 클래스 의존성은 `cl_abap_testdouble=>create( '인터페이스 또는 클래스' )` + `cl_abap_testdouble=>configure_call( double )->returning( 값 )`으로 바꿉니다(ABAP OO 테스트 더블 프레임워크). `FINAL` 클래스는 더블로 만들 수 없으므로, 바꿔 끼울 의존성은 인터페이스로 받도록 설계하세요.

**이 문제에서 쓴 테스트 도구 정리**

| 단계 | 테스트 대상 | 더블 |
|---|---|---|
| 1~4 | 핸들러 메서드 | CDS + SQL 테스트 더블, `cl_aunit_authority_check` |
| 5 | 핸들러 메서드(EML 격리) | `if_abap_behavior_testdouble` |
| 6 | 세이버 메서드 | SQL 테스트 더블(+ TEST-SEAM) |
| 7 | BO 전체 + 저장 | CDS + SQL 테스트 더블 |
| 8~9 | BO 소비자 | 트랜잭션 버퍼 더블, EML API 목 |
| 10 | CDS 뷰 | CDS 테스트 더블 |
| 11 | OData 서비스 | 로컬 클라이언트 프록시 + CDS/SQL 테스트 더블 |

**자주 나는 오류와 해결**
- `create_v2_local_proxy`에서 예외: 바인딩이 Publish되지 않았거나 `service_id`가 바인딩의 서비스 이름과 다릅니다. 서비스 바인딩 편집기의 Service 이름과 버전(`0001`)을 확인하세요.
- `create_resource_for_entity_set( 'Travel' )`에서 오류: 서비스 정의의 `expose ... as Travel` 이름과 대소문자까지 같아야 합니다.
- 같은 테이블이 CDS 환경(`i_select_base_dependencies`로 자동 포함)과 SQL 환경 양쪽에 들어가면 환경 생성 때 오류가 날 수 있습니다. 그 테이블을 SQL 환경 목록에서 빼고 `cds_test_environment->insert_test_data`로 넣으세요.

</details>

## 출처

- SAP-samples/abap-cheat-sheets
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/08_EML_ABAP_for_RAP.md
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/14_ABAP_Unit_Tests.md
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/17_SAP_LUW.md
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/22_Released_ABAP_Classes.md
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/25_Authorization_Checks.md
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/33_ABAP_Release_News.md
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/src/zcl_demo_abap_rap_draft_ln_m.clas.abap
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/src/zdemo_abap_rap_draft_m.bdef.asbdef
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/src/zcl_demo_abap_rap_ext_num_u.clas.abap
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/src/ztcl_demo_abap_unit_tdf_testcl.clas.testclasses.abap
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/src/zcl_demo_abap_unit_test.clas.abap
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/src/zcl_demo_abap_unit_test.clas.testclasses.abap
- SAP-samples/abap-platform-rap110
  - https://github.com/SAP-samples/abap-platform-rap110/tree/main/src (zrap110_eml_playground_sol, zrap110_r_traveltp_sol BDEF, zrap110_bp_traveltp_sol)
- SAP-samples/abap-platform-rap-workshops (RAP400: 테스트)
  - https://github.com/SAP-samples/abap-platform-rap-workshops/blob/main/rap4xx/rap400/README.md
  - https://github.com/SAP-samples/abap-platform-rap-workshops/blob/main/rap4xx/rap400/exercises/ex2/README.md
  - https://github.com/SAP-samples/abap-platform-rap-workshops/blob/main/rap4xx/rap400/exercises/ex3/README.md
  - https://github.com/SAP-samples/abap-platform-rap-workshops/tree/main/rap4xx/rap400/exercises/ex4/sources
  - https://github.com/SAP-samples/abap-platform-rap-workshops/blob/main/rap4xx/rap400/exercises/ex5/README.md
- SAP-samples/abap-platform-refscen-flight (ABAP-platform-cloud 브랜치)
  - https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/managed (`/DMO/TC_BOTD_TRAVEL_M_DEMOS`, `/DMO/TC_TRAVEL_M_BO_CONSUMER`, `/DMO/BP_TRAVEL_M` 테스트 클래스, `/DMO/TC_TRAVEL_PROC_M_O2_ODATA`)
  - https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/draft (`/DMO/BP_TRAVEL_D` 테스트 클래스·로컬 타입, `/DMO/TC_BOTD_TRAVEL_D_DEMOS`, `/DMO/R_TRAVEL_D`, `/DMO/I_TRAVEL_D` BDEF)
  - https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/unmanaged (`/DMO/BP_TRAVEL_U` 테스트 클래스)
  - https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/reuse (`/DMO/I_Customer`)
